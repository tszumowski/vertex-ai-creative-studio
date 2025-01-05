"""Module to interact with Imagen via VertexAI."""

import os

import vertexai
from absl import logging
from vertexai.preview.vision_models import ImageGenerationModel

vertexai.init(
    project=os.environ.get("GCP_PROJECT_ID"), location=os.environ.get("GCP_REGION")
)


class ImageClientError(Exception):
    """Base ImageClientError class"""


class ImagenClient:
    """Class to interact with the Imagen models."""

    def __init__(self, model: str) -> None:
        """Instantiates the ImagenClient."""
        self.model = ImageGenerationModel.from_pretrained(model)
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
