# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Veo model methods"""

import time

import google.auth
import google.auth.transport.requests
import requests
from dotenv import load_dotenv

from models.model_setup import VeoModelSetup

from config.default import Default


config = Default()


load_dotenv(override=True)

#video_model, prediction_endpoint, fetch_endpoint = VeoModelSetup.init()
t2v_video_model = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{config.VEO_PROJECT_ID}/locations/us-central1/publishers/google/models/{config.VEO_MODEL_ID}"
t2v_prediction_endpoint = f"{t2v_video_model}:predictLongRunning"
fetch_endpoint = f"{t2v_video_model}:fetchPredictOperation"

i2v_video_model = f"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{config.VEO_PROJECT_ID}/locations/us-central1/publishers/google/models/{config.VEO_EXP_MODEL_ID}"
i2v_prediction_endpoint = f"{i2v_video_model}:predictLongRunning"


def send_request_to_google_api(api_endpoint, data=None):
    """
    Sends an HTTP request to a Google API endpoint.

    Args:
        api_endpoint: The URL of the Google API endpoint.
        data: (Optional) Dictionary of data to send in the request body (for POST, PUT, etc.).

    Returns:
        The response from the Google API.
    """

    # Get access token calling API
    creds, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    access_token = creds.token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(api_endpoint, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def compose_videogen_request(
    prompt,
    image_uri,
    gcs_uri,
    seed,
    aspect_ratio,
    sample_count,
    enable_prompt_rewriting,
    duration_seconds,
):
    """ Create a JSON Request for Veo """
    instance = {"prompt": prompt}
    if image_uri:
        instance["image"] = {"gcsUri": image_uri, "mimeType": "png"}
    request = {
        "instances": [instance],
        "parameters": {
            "storageUri": gcs_uri,
            "sampleCount": sample_count,
            "seed": seed,
            "aspectRatio": aspect_ratio,
            "enablePromptRewriting": enable_prompt_rewriting,
            "durationSeconds": duration_seconds,
        },
    }
    return request


def text_to_video(prompt, seed, aspect_ratio, sample_count, output_gcs, enable_pr, duration_seconds):
    """Text to video"""
    req = compose_videogen_request(
        prompt, None, output_gcs, seed, aspect_ratio, sample_count, enable_pr, duration_seconds
    )
    resp = send_request_to_google_api(t2v_prediction_endpoint, req)
    print(resp)
    return fetch_operation(resp["name"])


def image_to_video(
    prompt, image_gcs, seed, aspect_ratio, sample_count, output_gcs, enable_pr, duration_seconds
):
    """Image to video"""
    req = compose_videogen_request(
        prompt, image_gcs, output_gcs, seed, aspect_ratio, sample_count, enable_pr, duration_seconds
    )
    resp = send_request_to_google_api(t2v_prediction_endpoint, req)
    print(resp)
    return fetch_operation(resp["name"])


def fetch_operation(lro_name):
    """ Long Running Operation fetch """
    request = {"operationName": lro_name}
    # The generation usually takes 2 minutes. Loop 30 times, around 5 minutes.
    for i in range(30):
        resp = send_request_to_google_api(fetch_endpoint, request)
        if "done" in resp and resp["done"]:
            return resp
        time.sleep(10)


def show_video(op):
    """ show video """
    print(op)
    if op["response"]:
        print(f"Done: {op['response']['done']}")
        if op["response"]["generatedSamples"]:
            # veo-2.0-generate-exp
            for video in op["response"]["generatedSamples"]:
                print(video)
                gcs_uri = video["video"]["uri"]
                file_name = gcs_uri.split("/")[-1]
                print("Video generated - use the following to copy locally")
                print(f"gsutil cp {gcs_uri} {file_name}")
                return gcs_uri
        elif op["response"]["videos"]:
            # veo-2.0-generate-001
            print(f"Videos: {op['response']['videos']}")
            for video in op["response"]["videos"]:
                print(f"> {video}")
                gcs_uri = video["gcsUri"]
                file_name = gcs_uri.split("/")[-1]
                print("Video generated - use the following to copy locally")
                print(f"gsutil cp {gcs_uri} {file_name}")
                return gcs_uri
