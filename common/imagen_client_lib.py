"""Module to interact with Imagen via VertexAI."""

from __future__ import annotations

import os
from typing import Any

import vertexai
from absl import logging
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

from common import storage_client_lib


IMAGE_SEGMENTATION_MODEL = "image-segmentation-001"
SEGMENTATION_ENDPOINT = (
    "projects/{project_id}/locations/{region}/"
    f"publishers/google/models/{IMAGE_SEGMENTATION_MODEL}"
)
AI_PLATFORM_REGIONAL_ENDPOINT = "{region}-aiplatform.googleapis.com"
IMAGEN_EDIT_MODEL = "imagen-3.0-capability-preview-0930"
EDIT_ENDPOINT = (
    "projects/{project_id}/locations/{region}/"
    f"publishers/google/models/{IMAGEN_EDIT_MODEL}"
)


class ImageClientError(Exception):
    """Base ImageClientError class"""


class ImagenClient:
    """Class to interact with the Imagen models."""

    def __init__(
        self,
    ) -> None:
        """Instantiates the ImagenClient."""
        self.project_id = os.environ.get("GCP_PROJECT_ID")
        self.region = os.environ.get("GCP_REGION")
        vertexai.init(project=self.project_id, location=self.region)
        self.ai_platform_client = aiplatform.gapic.PredictionServiceClient(
            client_options={
                "api_endpoint": AI_PLATFORM_REGIONAL_ENDPOINT.format(region=self.region)
            },
        )
        logging.info(
            "ImagenClient: Prediction client initiated on project %s in %s: %s.",
            self.project_id,
            self.region,
            AI_PLATFORM_REGIONAL_ENDPOINT.format(region=self.region),
        )
        self.storage_client = storage_client_lib.StorageClient()
        self.bucket_name = os.environ.get("IMAGE_CREATION_BUCKET")
        self.bucket_uri = f"gs://{self.bucket_name}"
        logging.info("ImagenClient: Instantiated.")

    def generate_images(
        self,
        generation_model: str,
        prompt: str,
        add_watermark: bool,
        aspect_ratio: str,
        num_images: int,
        language: str,
        negative_prompt: str,
    ) -> list[str]:
        """Generates a set of images.

        Args:
            generation_model: The model to use.
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
        generation_model = ImageGenerationModel.from_pretrained(generation_model)
        try:
            generated_images_uris = []
            response = generation_model.generate_images(
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
        image_uri_parts = image_uri.split("/")
        bucket_name = image_uri_parts[2]
        file_path = "/".join(image_uri_parts[3:])
        image_string = self.storage_client.download_as_string(bucket_name, file_path)

        file, extension = file_path.split(".")
        edited_file_uri = f"gs://{bucket_name}/{file}-edited.{extension}"

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
            "output_gcs_uri": edited_file_uri,
        }
        response = self.ai_platform_client.predict(
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
        return response

    def _get_image_segmentation_mask(self, image_uri: str, mode: str) -> dict[str, Any]:
        description = ""

        instances = []
        instances.append({"image": {"gcsUri": image_uri}})
        instances[0]["prompt"] = description

        response = self.ai_platform_client.predict(
            endpoint=SEGMENTATION_ENDPOINT.format(
                project_id=self.project_id, region=self.region
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
