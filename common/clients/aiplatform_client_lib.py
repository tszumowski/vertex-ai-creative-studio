# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module to interact with Google Cloud AI Platform."""

from __future__ import annotations

import os
import time
from typing import Any

import google.auth
import requests
from absl import logging
from google.cloud import aiplatform

from vertexai.preview.vision_models import Image

from common.clients import storage_client_lib
from common.models.edit_mode import EditMode
from common.models.edit_params import EditParams
from common.utils import api_utils

AIPLATFORM_REGIONAL_ENDPOINT = "{region}-aiplatform.googleapis.com"
VIDEO_GENERATION_ENDPOINT = (
    "https://{region}-aiplatform.googleapis.com/v1beta1/"
    "projects/{project_id}/locations/{region}/"
    "publishers/google/models/{model}"
)
IMAGE_SEGMENTATION_MODEL = "image-segmentation-001"
SEGMENTATION_ENDPOINT = (
    "projects/{project_id}/locations/{region}/"
    f"publishers/google/models/{IMAGE_SEGMENTATION_MODEL}"
)

EDIT_ENDPOINT = (
    "https://{region}-aiplatform.googleapis.com/v1/"
    "projects/{project_id}/locations/{region}/"
    "publishers/google/models/{model}"
)


class AIPlatformClientError(Exception):
    """Base ImageClientError class"""


class AIPlatformClient:
    """Class to interact with AIPlatform."""

    def __init__(self) -> None:
        """Instantiates the AIPlatform Client."""
        self.project_id = os.environ.get("PROJECT_ID")
        self.region = os.environ.get("REGION")
        aiplatform.init(project=self.project_id, location=self.region)
        self.aiplatform_client = aiplatform.gapic.PredictionServiceClient(
            client_options={
                "api_endpoint": AIPLATFORM_REGIONAL_ENDPOINT.format(
                    region=self.region,
                ),
            },
        )
        logging.info(
            "ImagenClient: Prediction client initiated on project %s in %s: %s.",
            self.project_id,
            self.region,
            AIPLATFORM_REGIONAL_ENDPOINT.format(region=self.region),
        )
        self.storage_client = storage_client_lib.StorageClient()

    def generate_video(
        self,
        model: str = "veo-2.0-generate-001",
        prompt: str = "",
        num_videos: int = 1,
        image_uri: str | None = "",
        aspect_ratio: str | None = "16:9",
        duration_seconds: int = 360,
    ) -> str:
        """Generates a video with prompt and image input.

        Args:
            prompt: The prompt.
            image_uri: (Optional) The image to use as reference for the video.
            aspect_ratio: (Optional) The aspect ratio of the video.

        Returns:
            The GCS URI of the generated video.

        Raises:
            AIPlatformClientError: If the video could not be generated.
        """
        video_prediction_endpoint = (
            f"{VIDEO_GENERATION_ENDPOINT}:predictLongRunning".format(
                region=self.region,
                project_id=self.project_id,
                model=model,
            )
        )
        video_fetch_endpoint = (
            f"{VIDEO_GENERATION_ENDPOINT}:fetchPredictOperation".format(
                region=self.region,
                project_id=self.project_id,
                model=model,
            )
        )
        instance = {"prompt": prompt}
        if image_uri:
            instance["image"] = {
                "gcsUri": image_uri,
                "mimeType": Image(gcs_uri=image_uri)._mime_type,
            }
        req = {
            "instances": [instance],
            "parameters": {
                "sampleCount": num_videos,
                "seed": 1,
                "aspectRatio": aspect_ratio,
                "durationSeconds": duration_seconds,
            },
        }
        operation = self._send_request_to_google_api(
            video_prediction_endpoint,
            req,
        )
        result = self._poll_video_operation(video_fetch_endpoint, operation["name"])
        if result["response"]:
            video = result["response"]["generatedSamples"][0]
            return video["video"]["uri"]
        raise AIPlatformClientError(
            "VertexAIClient: Could not generate video.",
        )

    def edit_image(
        self,
        model: str,
        image_uri: str,
        prompt: str,
        edit_mode: str,
        number_of_images: int,
        mask_uri: str,
    ) -> list[str]:
        """Edits and image.

        Args:
            model: The imagen edit model used.
            image_uri: The URI of the image to edit. E.g. "gs://dir/my_image.jpg"
            prompt: The edit prompt.
            number_of_images: Number of images to create after edits. Defaults to 1.
            edit_mode: The edit mode for editing. Defaults to "".
            mask_mode: The area to edit. Defaults to "foreground".
            mask_uri: The URI of the image mask.

        Returns:
            The edited image URIs.

        Raises:
            AIPlatformClientError: If the image could not be edited.
        """
        image_editing_endpoint = f"{EDIT_ENDPOINT}:predict".format(
            region=self.region,
            project_id=self.project_id,
            model=model,
        )
        edit_params = EditParams(
            edit_mode=EditMode.__getitem__(edit_mode),
        )
        image_base64_string = Image(gcs_uri=image_uri)._as_base64_string()
        mask_base64_string = Image(gcs_uri=mask_uri)._as_base64_string()
        try:
            instance = {"prompt": prompt}
            instance["referenceImages"] = [
                {
                    "referenceType": "REFERENCE_TYPE_RAW",
                    "referenceId": 1,
                    "referenceImage": {"bytesBase64Encoded": image_base64_string},
                },
                {
                    "referenceType": "REFERENCE_TYPE_MASK",
                    "referenceId": 2,
                    "referenceImage": {"bytesBase64Encoded": mask_base64_string},
                    "maskImageConfig": {
                        "maskMode": "MASK_MODE_USER_PROVIDED",
                        "dilation": edit_params.get_dilation(),
                    },
                },
            ]
            if edit_mode == "EDIT_MODE_BGSWAP":
                del instance["referenceImages"][1]["referenceImage"]
                instance["referenceImages"][1]["maskImageConfig"]["maskMode"] = (
                    "MASK_MODE_BACKGROUND"
                )
                del instance["referenceImages"][1]["maskImageConfig"]["dilation"]
            req = {
                "instances": [instance],
                "parameters": {
                    "editConfig": {"baseSteps": edit_params.get_base_steps()},
                    "editMode": edit_params.get_edit_mode(),
                    "seed": 1,
                    "sampleCount": number_of_images,
                    "includeRaiReason": "true",
                },
            }
            response = api_utils.make_request(
                image_editing_endpoint,
                req,
            )
            bucket_name, file_name, extension = (
                self.storage_client.get_storage_object_metadata(image_uri)
            )
            timestamp_int = int(time.time())
            edited_file_name = f"{file_name}-edited-{timestamp_int}{extension}"

            results = []
            for result in response["predictions"]:
                edited_file_uri = self.storage_client.upload(
                    bucket_name=bucket_name,
                    contents=result["bytesBase64Encoded"],
                    mime_type=result["mimeType"],
                    file_name=edited_file_name,
                    sub_dir="edited",
                )
                results.append(edited_file_uri)
        except Exception as ex:
            logging.exception("AIPlatformClient: Could not edit image: %s", ex)
            raise AIPlatformClientError("Could not edit image: %s", ex) from ex
        return results

    def _poll_video_operation(
        self,
        video_fetch_endpoint: str,
        lro_name: str,
    ) -> dict[str, Any] | None:
        """Polls the video generation operation.

        Args:
            video_fetch_endpoint: The URL of the video generation operation.
            lro_name: The name of the video generation operation.

        Returns:
            The response from the video generation operation once finished.
        """
        request = {"operationName": lro_name}
        # The generation usually takes 2 minutes. Loop 30 times, around 5 minutes.
        for _ in range(30):
            resp = api_utils.make_request(video_fetch_endpoint, request)
            if resp.get("done"):
                return resp
            time.sleep(10)
        return None
