"""Module to interact with Imagen via VertexAI."""

from __future__ import annotations

import dataclasses
import mimetypes
import os
from typing import cast

import vertexai
from absl import logging
from vertexai import generative_models
from vertexai.preview.vision_models import ImageGenerationModel

from common.clients import storage_client_lib

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
_GENERATIVE_MODEL = "gemini-1.5-flash-001"

_GENERATION_CONFIG = generative_models.GenerationConfig(
    temperature=0.8,
    top_p=0.95,
    top_k=20,
    candidate_count=1,
    stop_sequences=["STOP!"],
)
SUPPORTED_IMAGE_TYPES = frozenset(["jpeg", "jpg", "png"])
SUPPORTED_VIDEO_TYPES = frozenset(
    [
        "x-flv",
        "mov",
        "mpeg",
        "mpegps",
        "mpg",
        "mp4",
        "webm",
        "wmv",
        "3gpp",
    ]
)


@dataclasses.dataclass(frozen=True)
class Prompt:
    IMAGE = (
        "You have a great eye for visual descriptions. Provide two sentences "
        "that describe this image:"
    )
    VIDEO = (
        "You have a great eye for visual descriptions. Provide two sentences "
        "that describe this video:"
    )


class VertexAIClientError(Exception):
    """Base ImageClientError class"""


class VertexAIClient:
    """Class to interact with the Imagen models."""

    def __init__(
        self,
    ) -> None:
        """Instantiates the VertexAIClient."""
        self.project_id = os.environ.get("PROJECT_ID")
        self.region = os.environ.get("REGION")
        vertexai.init(project=self.project_id, location=self.region)

        self.storage_client = storage_client_lib.StorageClient()
        self.bucket_name = os.environ.get("IMAGE_CREATION_BUCKET")
        self.bucket_uri = f"gs://{self.bucket_name}"
        self._text_generation_client = generative_models.GenerativeModel(
            model_name=_GENERATIVE_MODEL,
        )
        logging.info("VertexAIClient: Instantiated.")

    def generate_description_from_image(self, media_uri: str) -> str:
        """Generates text from medias.

        Args:
            media_uri: URI to a media file on Google Cloud Storage.

        Returns:
            The generated text.
        """
        file_extension = os.path.splitext(media_uri)[1].replace(".", "")
        file_type = self._get_file_type_from_extension(file_extension)
        mime_type = mimetypes.guess_type(media_uri)[0]
        media_content = generative_models.Part.from_uri(media_uri, mime_type)
        response = self._text_generation_client.generate_content(
            contents=[media_content, getattr(Prompt, file_type.upper())],
            stream=False,
            generation_config=_GENERATION_CONFIG,
        )
        generation_response = cast(generative_models.GenerationResponse, response)
        return generation_response.text.strip()

    def _get_file_type_from_extension(self, file_extension: str) -> str:
        """Gets the file type from the file extension.

        Args:
            file_extension: The file extension.

        Returns:
            The file type.

        Raises:
            ValueError: If the file extension is not supported.
        """
        if file_extension in SUPPORTED_IMAGE_TYPES:
            return "image"
        if file_extension in SUPPORTED_VIDEO_TYPES:
            return "video"
        raise ValueError(f"Unsupported file type: {file_extension}")

    def generate_images(
        self,
        model: str,
        prompt: str,
        add_watermark: bool,
        aspect_ratio: str,
        num_images: int,
        language: str,
        negative_prompt: str,
    ) -> list[str]:
        """Generates a set of images.

        Args:
            model: The model to use.
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
        image_generation_model = ImageGenerationModel.from_pretrained(
            model,
        )
        try:
            generated_images_uris = []
            response = image_generation_model.generate_images(
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
                    "VertexAIClient: Generated image: %s size: %s at %s",
                    index,
                    image_size,
                    image._gcs_uri,
                )
                generated_images_uris.append(image._gcs_uri)
        except Exception as ex:
            raise VertexAIClientError(
                f"VertexAIClient: Could not generate images {ex}",
            ) from ex
        return generated_images_uris
