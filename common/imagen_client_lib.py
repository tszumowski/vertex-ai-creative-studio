"""Module to interact with Imagen via VertexAI."""

from __future__ import annotations

import os
from typing import Any

import vertexai
from absl import logging
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

from common import storage_client_lib

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
REGION = os.environ.get("GCP_REGION")
IMAGE_SEGMENTATION_MODEL = "image-segmentation-001"
SEGMENTATION_ENDPOINT = (
    f"projects/{PROJECT_ID}/locations/{REGION}/"
    f"publishers/google/models/{IMAGE_SEGMENTATION_MODEL}"
)
AI_PLATFORM_REGIONAL_ENDPOINT = f"{REGION}-aiplatform.googleapis.com"
IMAGEN_EDIT_MODEL = "imagen-3.0-capability-preview-0930"
EDIT_ENDPOINT = (
    f"projects/{PROJECT_ID}/locations/{REGION}/"
    f"publishers/google/models/{IMAGEN_EDIT_MODEL}"
)

vertexai.init(project=PROJECT_ID, location=REGION)


class ImageClientError(Exception):
    """Base ImageClientError class"""


class ImagenClient:
    """Class to interact with the Imagen models."""

    def __init__(self, model: str) -> None:
        """Instantiates the ImagenClient."""
        self.model = ImageGenerationModel.from_pretrained(model)
        self.ai_platform_client = aiplatform.gapic.PredictionServiceClient(
            client_options={"api_endpoint": AI_PLATFORM_REGIONAL_ENDPOINT},
        )
        self.storage_client = storage_client_lib.StorageClient()
        self.bucket_name = os.environ.get("IMAGE_CREATION_BUCKET")
        self.bucket_uri = f"gs://{self.bucket_name}"
        logging.info("ImagenClient: Instantiated.")

    def generate_images(
        self,
        prompt: str,
        add_watermark: bool,
        aspect_ratio: str,
        num_images: int,
        language: str,
        negative_prompt: str,
    ) -> list[str]:
        """Generates a set of images.

        Args:
            prompt: The prompt.
            add_watermark: Whether to add a watermark or not.
            aspect_ratio: The aspect ratio of the images.
            num_images: The number of images to generate.
            language: The language.
            negative_prompt: The negative prompt.

        Returns:
            A list of GCS uris.

        Raises:
            ImageClientError: When the images could not be generated.
        """
        try:
            generated_images_uris = []
            response = self.model.generate_images(
                prompt=prompt,
                add_watermark=add_watermark,
                aspect_ratio=aspect_ratio,
                number_of_images=num_images,
                output_gcs_uri=self.bucket_uri,
                language=language,
                negative_prompt=negative_prompt,
            )

            for index, image in enumerate(response.images):
                image_size = len(image._as_base64_string())
                logging.info(
                    "ImagenClient: Generated image: %s size: %s at %s",
                    index,
                    image_size,
                    image._gcs_uri,
                )
                generated_images_uris.append(image._gcs_uri)
        except Exception as ex:
            raise ImageClientError(
                f"ImagenClient: Could not generate images {ex}",
            ) from ex
        return generated_images_uris

    def edit_image(
        self,
        image_uri: str,
        prompt: str,
        aspect_ratio: str = "1:1",
        number_of_images: int = 1,
        edit_mode: str = "",
        foreground_background: str = "foreground",
    ) -> str:
        image_uri_parts = image_uri.split("/")
        bucket_name = image_uri_parts[3]
        file_path = "/".join(image_uri_parts[3:])

        image_string = self.storage_client.download_as_string(bucket_name, file_path)
        file, extension = file_path.split(".")
        edited_file_path = f"{file}-edited.{extension}"
        mask = self._get_image_segmentation_mask(image_uri, foreground_background)
        mask_bytes = mask["bytesBase64Encoded"]
        mask_file_path = f"{file}-mask.{extension}"

        gcs_output = self.storage_client.upload(
            bucket_name=bucket_name,
            contents=mask["bytesBase64Encoded"],
            mime_type=mask["mimeType"],
            file_name=mask_file_path,
            decode=True,
        )
        logging.info("ImagenClient: Wrote mask to %s", gcs_output)
        instances = self._build_edit_prediction_instances(
            image_string,
            mask_bytes,
            prompt,
        )
        parameters = {
            "sampleCount": number_of_images,
            "editMode": edit_mode,
            "aspectRatio": aspect_ratio,
            "output_gcs_uri": edited_file_path,
        }
        response = self.ai_platform_client.predict(
            endpoint=EDIT_ENDPOINT,
            instances=instances,
            parameters=parameters,
        )
        logging.info(
            "ImagenClient: Got response %s from endpoint %s. Params: %s, Instances %s.",
            response,
            EDIT_ENDPOINT,
            parameters,
            instances,
        )
        return response

    def _get_image_segmentation_mask(self, image_uri: str, mode: str) -> dict[str, Any]:
        description = "Gemini description of the image."

        instances = []
        instances.append({"image": {"gcsUri": image_uri}})
        instances[0]["prompt"] = description

        parameters = {"mode": mode}
        logging.info(
            "ImagenClient: Prediction client initiated on project %s in %s: %s.",
            PROJECT_ID,
            REGION,
            AI_PLATFORM_REGIONAL_ENDPOINT,
        )
        response = self.ai_platform_client.predict(
            endpoint=SEGMENTATION_ENDPOINT,
            instances=instances,
            parameters=parameters,
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
        image_string: str,
        mask_bytes: str | bytes,
        prompt: str,
    ) -> list[dict[str, Any]]:
        reference_images = []
        reference_images.append(
            {
                "referenceType": "REFERENCE_TYPE_RAW",
                "referenceId": 1,
                "referenceImage": {"bytesBase64Encoded": image_string},
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
