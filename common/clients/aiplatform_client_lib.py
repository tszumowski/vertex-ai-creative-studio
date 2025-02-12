from __future__ import annotations

import os
import time
from typing import Any

import google.auth
import requests
from absl import logging
from google.cloud import aiplatform

from common.clients import storage_client_lib, vertexai_client_lib

VIDEO_GENERATION_MODEL = "veo-001-preview-0815"
AIPLATFORM_REGIONAL_ENDPOINT = "{region}-aiplatform.googleapis.com"
VIDEO_GENERATION_ENDPOINT = (
    "https://{region}-aiplatform.googleapis.com/v1beta1/"
    "projects/{project_id}/locations/{region}/"
    f"publishers/google/models/{VIDEO_GENERATION_MODEL}"
)
IMAGE_SEGMENTATION_MODEL = "image-segmentation-001"
SEGMENTATION_ENDPOINT = (
    "projects/{project_id}/locations/{region}/"
    f"publishers/google/models/{IMAGE_SEGMENTATION_MODEL}"
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
        self.video_prediction_endpoint = (
            f"{VIDEO_GENERATION_ENDPOINT}:predictLongRunning".format(
                region=self.region,
                project_id=self.project_id,
            )
        )
        self.video_fetch_endpoint = (
            f"{VIDEO_GENERATION_ENDPOINT}:fetchPredictOperation".format(
                region=self.region,
                project_id=self.project_id,
            )
        )
        logging.info(
            "ImagenClient: Prediction client initiated on project %s in %s: %s.",
            self.project_id,
            self.region,
            AIPLATFORM_REGIONAL_ENDPOINT.format(region=self.region),
        )
        self.storage_client = storage_client_lib.StorageClient()
        self.vertexai_client = vertexai_client_lib.VertexAIClient()

    def generate_video(
        self,
        prompt: str,
        image_uri: str | None = "",
        aspect_ratio: str | None = "16:9",
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
        instance = {"prompt": prompt}
        if image_uri:
            instance["image"] = {"gcsUri": image_uri, "mimeType": "png"}
        req = {
            "instances": [instance],
            "parameters": {
                "sampleCount": 1,
                "seed": 1,
                "aspectRatio": aspect_ratio,
            },
        }
        operation = self._send_request_to_google_api(
            self.video_prediction_endpoint, req
        )
        result = self._fetch_operation(operation["name"])
        if result["response"]:
            video = result["response"]["generatedSamples"][0]
            return video["video"]["uri"]
        raise AIPlatformClientError(
            "VertexAIClient: Could not generate video.",
        )

    def _send_request_to_google_api(
        self,
        api_endpoint: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Sends an HTTP request to a Google API endpoint.

        Args:
            api_endpoint: The URL of the Google API endpoint.
            data: (Optional) Dictionary of data to send in the request body.

        Returns:
            The response from the Google API.
        """

        # Get access token calling API
        creds, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        access_token = creds.token

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(api_endpoint, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()

    def _fetch_operation(self, lro_name: str) -> dict[str, Any] | None:
        request = {"operationName": lro_name}
        # The generation usually takes 2 minutes. Loop 30 times, around 5 minutes.
        for _ in range(30):
            resp = self._send_request_to_google_api(self.video_fetch_endpoint, request)
            if resp.get("done"):
                return resp
            time.sleep(10)
        return None
