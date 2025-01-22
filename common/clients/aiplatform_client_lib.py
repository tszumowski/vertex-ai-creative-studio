from __future__ import annotations

import base64
import os
from typing import Any

from absl import logging
from google.cloud import aiplatform

from common.clients import storage_client_lib, vertexai_client_lib

IMAGE_SEGMENTATION_MODEL = "image-segmentation-001"
SEGMENTATION_ENDPOINT = (
    "projects/{project_id}/locations/{region}/"
    f"publishers/google/models/{IMAGE_SEGMENTATION_MODEL}"
)
AIPLATFORM_REGIONAL_ENDPOINT = "{region}-aiplatform.googleapis.com"
IMAGEN_EDIT_MODEL = "imagen-3.0-capability-001"
EDIT_ENDPOINT = (
    "projects/{project_id}/locations/{region}/"
    f"publishers/google/models/{IMAGEN_EDIT_MODEL}"
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
        self.vertexai_client = vertexai_client_lib.VertexAIClient()

    def edit_image(
        self,
        image_uri: str,
        prompt: str,
        aspect_ratio: str = "1:1",
        number_of_images: int = 1,
        edit_mode: str = "",
        foreground_background: str = "foreground",
    ) -> str:
        """_summary_

        Args:
            image_uri: The URI of the image to edit. E.g. "gs://dir/my_image.jpg"
            prompt: The edit prompt.
            aspect_ratio: The aspect ratio. Defaults to "1:1".
            number_of_images: Number of images to create after edits. Defaults to 1.
            edit_mode: The edit mode for editing. Defaults to "".
            foreground_background: The area to edit. Defaults to "foreground".

        Returns:
            An AI Platform prediction response object.
        """
        try:
            image_uri_parts = image_uri.split("/")
            bucket_name = image_uri_parts[2]
            file_path = "/".join(image_uri_parts[3:])
            image_string = self.storage_client.download_as_string(
                bucket_name=bucket_name,
                file_path=file_path,
            )
            image_bytes = base64.b64decode(image_string)

            file, extension = file_path.split(".")
            edited_file_uri = f"gs://{bucket_name}/{file}-edited.{extension}"

            mask = self._get_image_segmentation_mask(image_uri, foreground_background)
            mask_bytes = mask["bytesBase64Encoded"]
            mask_file_path = f"{file}-mask.{extension}"

            gcs_output = self.storage_client.upload(
                bucket_name=bucket_name,
                contents=base64.b64encode(mask["bytesBase64Encoded"]).decode("utf-8"),
                mime_type=mask["mimeType"],
                file_name=mask_file_path,
            )
            logging.info("ImagenClient: Wrote mask to %s", gcs_output)
            instances = self._build_edit_prediction_instances(
                image_bytes,
                mask_bytes,
                prompt,
            )
            parameters = {
                "sampleCount": number_of_images,
                "editMode": edit_mode,
                "aspectRatio": aspect_ratio,
                "output_gcs_uri": edited_file_uri,
            }
            response = self.aiplatform_client.predict(
                endpoint=EDIT_ENDPOINT.format(
                    project_id=self.project_id,
                    region=self.region,
                ),
                instances=instances,
                parameters=parameters,
            )
            logging.info(
                "ImagenClient: Got response %s from endpoint %s. Params: %s, Instances %s.",
                response,
                EDIT_ENDPOINT.format(project_id=self.project_id, region=self.region),
                parameters,
                instances,
            )
        except Exception as ex:
            logging.exception(ex)
            raise AIPlatformClientError(
                f"AIPlatformClient: Could not generate images {ex}",
            ) from ex
        return response

    def _get_image_segmentation_mask(self, image_uri: str, mode: str) -> dict[str, Any]:
        description = self.vertexai_client.generate_description_from_image(image_uri)

        instances = []
        instances.append({"image": {"gcsUri": image_uri}})
        instances[0]["prompt"] = description

        response = self.aiplatform_client.predict(
            endpoint=SEGMENTATION_ENDPOINT.format(
                project_id=self.project_id,
                region=self.region,
            ),
            instances=instances,
            parameters={"mode": mode},
        )
        prediction = response.predictions[0]
        label = prediction["labels"][0]["label"]
        score = prediction["labels"][0]["score"]
        logging.info(
            "ImagenClient: Image segmentation: %s - %s bytes, %s %s",
            prediction["mimeType"],
            len(prediction["bytesBase64Encoded"]),
            label,
            score,
        )
        return prediction

    def _build_edit_prediction_instances(
        self,
        image_bytes: bytes,
        mask_bytes: str | bytes,
        prompt: str,
    ) -> list[dict[str, Any]]:
        reference_images = []
        reference_images.append(
            {
                "referenceType": "REFERENCE_TYPE_RAW",
                "referenceId": 1,
                "referenceImage": {"bytesBase64Encoded": image_bytes},
            },
        )
        reference_images.append(
            {
                "referenceType": "REFERENCE_TYPE_MASK",
                "referenceId": 1,
                "referenceImage": {"bytesBase64Encoded": mask_bytes},
                "maskImageConfig": {
                    "maskMode": "MASK_MODE_USER_PROVIDED",
                    "dilation": 0.01,
                },
            },
        )
        return [{"referenceImages": reference_images, "prompt": prompt}]
