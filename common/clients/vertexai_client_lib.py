"""Module to interact with Imagen via VertexAI."""

from __future__ import annotations

import dataclasses
import enum
import mimetypes
import os
from typing import Literal, cast

import vertexai
from absl import logging
from vertexai.generative_models import (
    GenerationConfig,
    GenerationResponse,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)
from vertexai.preview.vision_models import (
    Image,
    ImageGenerationModel,
    MaskReferenceImage,
    MultiModalEmbeddingModel,
    RawReferenceImage,
)

from common import image_utils
from common.clients import storage_client_lib
from common.segmentation_utils import SemanticType

IMAGE_SEGMENTATION_MODEL = "image-segmentation-001"
IMAGEN_EDIT_MODEL = "imagen-3.0-capability-001"
IMAGEN_GENERATION_MODEL = "imagen-3.0-generate-001"
MULTIMODAL_EMBEDDING_MODEL = "multimodalembedding@001"
EMBEDDING_DIMENSIONS = 128
SEGMENTATION_ENDPOINT = (
    "projects/{project_id}/locations/{region}/"
    f"publishers/google/models/{IMAGE_SEGMENTATION_MODEL}"
)
AI_PLATFORM_REGIONAL_ENDPOINT = "{region}-aiplatform.googleapis.com"
EDIT_ENDPOINT = (
    "projects/{project_id}/locations/{region}/"
    f"publishers/google/models/{IMAGEN_EDIT_MODEL}"
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
    ],
)
_GENERATIVE_MODEL = "gemini-1.5-flash-001"
_GENERATION_CONFIG = GenerationConfig(
    temperature=0.8,
    top_p=0.95,
    top_k=20,
    candidate_count=1,
    stop_sequences=["STOP!"],
)
_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}


class EditMode(enum.Enum):
    EDIT_MODE_INPAINT_INSERTION = "inpainting-insert"
    EDIT_MODE_OUTPAINT = "outpainting"
    EDIT_MODE_INPAINT_REMOVAL = "inpainting-remove"
    EDIT_MODE_PRODUCT_IMAGE = "product-image"
    EDIT_MODE_BGSWAP = "background-swap"


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
        self._text_generation_client = GenerativeModel(
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
        media_content = Part.from_uri(media_uri, mime_type)
        response = self._text_generation_client.generate_content(
            contents=[media_content, getattr(Prompt, file_type.upper())],
            stream=False,
            generation_config=_GENERATION_CONFIG,
            safety_settings=_SAFETY_SETTINGS,
        )
        generation_response = cast(GenerationResponse, response)
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
        raise VertexAIClientError(f"Unsupported file type: {file_extension}")

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
                output_gcs_uri=f"{self.bucket_uri}/generated",
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

    def generate_text(self, prompt: str, media_uris: list[str] | None = None) -> str:
        """Generates text from a prompt and optional media.

        Args:
            prompt: The generation prompt.
            media_uris: Optional list of media to include in the prompt.

        Raises:
            VertexAIClientError: If text could not be generated.

        Returns:
            The generated text string.
        """
        try:
            contents = []
            if media_uris:
                for media_uri in media_uris:
                    mime_type = mimetypes.guess_type(media_uri)[0]
                    media_content = Part.from_uri(media_uri, mime_type)
                    contents.append(media_content)
            contents.append(prompt)
            response = self._text_generation_client.generate_content(
                contents=contents,
                stream=False,
                generation_config=_GENERATION_CONFIG,
                safety_settings=_SAFETY_SETTINGS,
            )
            generation_response = cast(GenerationResponse, response)
        except Exception as ex:
            raise VertexAIClientError(
                f"VertexAIClient: Could not generate text {ex}",
            ) from ex
        return generation_response.text.strip()

    def edit_image(
        self,
        image_uri: str,
        prompt: str,
        number_of_images: int = 1,
        edit_mode: str = "",
        mask_mode: str = "foreground",
        segmentation_classes: list[str] | None = None,
        target_size: tuple[str, str] | None = None,
    ) -> str:
        """Edits and image.

        Args:
            image_uri: The URI of the image to edit. E.g. "gs://dir/my_image.jpg"
            prompt: The edit prompt.
            number_of_images: Number of images to create after edits. Defaults to 1.
            edit_mode: The edit mode for editing. Defaults to "".
            mask_mode: The area to edit. Defaults to "foreground".
            segmentation_classes: (Optional) The objects to identify during masking.
            target_size: (Optional) The height and width of the target image.

        Returns:
            The edited image URI.

        Raises:
            VertexAIClientError: If the image could not be edited.
        """
        try:
            edit_model = ImageGenerationModel.from_pretrained(IMAGEN_EDIT_MODEL)
            image_uri_parts = image_uri.split("/")
            bucket_name = image_uri_parts[2]
            file_name = os.path.basename(image_uri)
            file, extension = os.path.splitext(file_name)
            edited_file_name = f"{file}-edited{extension}"

            image = Image(gcs_uri=image_uri)
            seed = None
            if edit_mode == EditMode.EDIT_MODE_OUTPAINT.name:
                # To use the outpainting feature, we must create an image mask and
                # prepare the original image by padding some empty space around it.
                image_pil_outpaint, mask_pil_outpaint = image_utils.pad_image_and_mask(
                    image,
                    target_size,
                    0,
                    0,
                )
                raw_ref_image = RawReferenceImage(
                    image=image_utils.get_bytes_from_pil(image_pil_outpaint),
                    reference_id=0,
                )
                mask_ref_image = MaskReferenceImage(
                    reference_id=1,
                    image=image_utils.get_bytes_from_pil(mask_pil_outpaint),
                    mask_mode="user_provided",
                    dilation=0.03,
                )
            if edit_mode == EditMode.EDIT_MODE_BGSWAP.name:
                raw_ref_image = RawReferenceImage(image=image, reference_id=0)
                mask_ref_image = MaskReferenceImage(
                    reference_id=1,
                    image=None,
                    mask_mode="background",
                )
                seed = 1
            if edit_mode in (
                EditMode.EDIT_MODE_INPAINT_INSERTION.name,
                EditMode.EDIT_MODE_INPAINT_REMOVAL.name,
            ):
                raw_ref_image = RawReferenceImage(image=image, reference_id=0)
                segmentation_ids = None
                if segmentation_classes:
                    segmentation_ids = [
                        SemanticType[name].value for name in segmentation_classes
                    ]
                mask_ref_image = MaskReferenceImage(
                    reference_id=1,
                    image=None,
                    mask_mode=mask_mode,
                    dilation=0.1,
                    segmentation_classes=segmentation_ids,
                )
            edited_image = edit_model.edit_image(
                prompt=prompt,
                edit_mode=EditMode[edit_mode].value,
                reference_images=[raw_ref_image, mask_ref_image],
                number_of_images=number_of_images,
                safety_filter_level="block_few",
                person_generation="allow_adult",
                seed=seed,
            )
            edited_file_uri = self.storage_client.upload(
                bucket_name=bucket_name,
                contents=edited_image[0]._as_base64_string(),
                mime_type=edited_image[0]._mime_type,
                file_name=edited_file_name,
                sub_dir="edited",
            )
        except Exception as ex:
            logging.exception(ex)
            raise VertexAIClientError(
                f"VertexAIClient: Could not edit image {ex}",
            ) from ex
        return edited_file_uri

    def upscale_image(
        self,
        image_uri: str,
        new_size: int | None = 2048,
        upscale_factor: Literal["x2", "x4"] | None = None,
        output_mime_type: Literal["image/png", "image/jpeg"] | None = "image/png",
        output_compression_quality: int | None = None,
    ) -> str:
        """Upscales an image.

        Args:
            image_uri: The URI of the image to upscale. E.g. "gs://dir/my_image.jpg"
            new_size: The size of the biggest dimension of the upscaled.
            upscale_factor: The upscaling factor. Supported values are "x2" and
                "x4". Defaults to None.
            output_mime_type: The mime type of the output image. Supported values
                are "image/png" and "image/jpeg". Defaults to "image/png".
            output_compression_quality: The compression quality of the output
                image
                as an int (0-100). Only applicable if the output mime type is
                "image/jpeg". Defaults to None.

        Returns:
            The GCS URI of the upscaled file.

        Raises:
            VertexAIClientError: If the image could not be upscaled.
        """
        try:
            gen_model = ImageGenerationModel.from_pretrained(IMAGEN_GENERATION_MODEL)
            image = Image(gcs_uri=image_uri)
            upscaled_image = gen_model.upscale_image(
                image=image,
                new_size=new_size,
                upscale_factor=upscale_factor,
                output_mime_type=output_mime_type,
                output_compression_quality=output_compression_quality,
            )
            image_uri_parts = image_uri.split("/")
            bucket_name = image_uri_parts[2]
            file_name = os.path.basename(image_uri)
            file, _ = os.path.splitext(file_name)
            extension = mimetypes.guess_all_extensions(output_mime_type)[0]
            upscaled_file_name = f"{file}-upscaled{extension}"
            upscaled_file_uri = self.storage_client.upload(
                bucket_name=bucket_name,
                contents=upscaled_image._as_base64_string(),
                mime_type=upscaled_image._mime_type,
                file_name=upscaled_file_name,
                sub_dir="upscaled",
            )
        except Exception as ex:
            logging.exception(ex)
            raise VertexAIClientError(
                f"VertexAIClient: Could not upscale image {ex}",
            ) from ex
        return upscaled_file_uri

    def get_embeddings_for_image(
        self,
        image_uri: str,
        prompt: str | None = None,
    ) -> tuple[float, float]:
        embedding_model = MultiModalEmbeddingModel.from_pretrained(
            MULTIMODAL_EMBEDDING_MODEL,
        )
        image = Image.load_from_file(image_uri)

        embeddings = embedding_model.get_embeddings(
            image=image,
            contextual_text=prompt,
            dimension=EMBEDDING_DIMENSIONS,
        )
        return embeddings.image_embedding, embeddings.text_embedding
