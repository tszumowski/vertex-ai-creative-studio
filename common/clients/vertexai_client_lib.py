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

"""Module to interact with Imagen via VertexAI."""

from __future__ import annotations

import dataclasses
import mimetypes
import os
import time
from typing import Literal, cast

import cv2
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
    ControlReferenceImage,
    Image,
    ImageGenerationModel,
    ImageSegmentationModel,
    MaskReferenceImage,
    MultiModalEmbeddingModel,
    RawReferenceImage,
    Scribble,
    StyleReferenceImage,
    SubjectReferenceImage,
)

from common.clients import storage_client_lib
from common.models.edit_mode import EditMode
from common.utils import image_utils

IMAGE_SEGMENTATION_MODEL = "image-segmentation-001"
IMAGEN_EDIT_MODEL = "imagen-3.0-capability-001"
IMAGEN_GENERATION_MODEL = "imagen-3.0-generate-001"
MULTIMODAL_EMBEDDING_MODEL = "multimodalembedding@001"
EMBEDDING_DIMENSIONS = 256
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

SUBJECT_TYPE_MATCHING = {
    "person": {
        "reference_type": "REFERENCE_TYPE_SUBJECT",
        "subject_type": "SUBJECT_TYPE_PERSON",
    },
    "anmial": {
        "reference_type": "REFERENCE_TYPE_SUBJECT",
        "subject_type": "SUBJECT_TYPE_ANIMAL",
    },
    "product": {
        "reference_type": "REFERENCE_TYPE_SUBJECT",
        "subject_type": "SUBJECT_TYPE_PRODUCT",
    },
    "style": {
        "reference_type": "REFERENCE_TYPE_STYLE",
        "subject_type": "",
    },
    "default": {
        "reference_type": "REFERENCE_TYPE_SUBJECT",
        "subject_type": "SUBJECT_TYPE_DEFAULT",
    },
}


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
        try:
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
            generation_response = cast("GenerationResponse", response)
        except Exception as ex:
            logging.exception("VertexAIClient: Something went wrong: %s", ex)
            raise VertexAIClientError(
                f"Could not generate description from image {ex}",
            ) from ex
        return generation_response.text.strip()

    def _get_file_type_from_extension(self, file_extension: str) -> str:
        """Gets the file type from the file extension.

        Args:
            file_extension: The file extension.

        Returns:
            The file type.

        Raises:
            VertexAIClientError: If the file extension is not supported.
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
        reference_images: list[dict[str, str]],
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
            reference_images: A list of reference images including type.

        Returns:
            A list of GCS uris.

        Raises:
            VertexAIClientError: When the images could not be generated.
        """

        _reference_images = []
        if reference_images:
            for idx, ref in enumerate(reference_images):
                if not ref["reference_image_uri"]:
                    continue
                ref_img = None
                if ref["reference_type"] in ("default", "person", "animal", "product"):
                    ref_img = SubjectReferenceImage(
                        reference_id=idx,
                        image=Image(
                            gcs_uri=ref["reference_image_uri"],
                        ),
                        subject_type=ref["reference_type"],
                    )
                if ref["reference_type"] == "style":
                    ref_img = StyleReferenceImage(
                        reference_id=idx,
                        image=Image(
                            gcs_uri=ref["reference_image_uri"],
                        ),
                    )
                _reference_images.append(ref_img)
        try:
            generated_images_uris = []
            if _reference_images:
                # Reference images are currently only supported in the capability model.
                # We would expect reference images to be supported in the base imagen3
                # models in the future.
                image_generation_model = ImageGenerationModel.from_pretrained(
                    IMAGEN_EDIT_MODEL,
                )
                response = image_generation_model._generate_images(
                    prompt=prompt,
                    # Cannot add watermark in imagen capability model.
                    aspect_ratio=aspect_ratio,
                    number_of_images=num_images,
                    output_gcs_uri=f"{self.bucket_uri}/generated",
                    language=language,
                    negative_prompt=negative_prompt,
                    reference_images=_reference_images,
                )
            else:
                image_generation_model = ImageGenerationModel.from_pretrained(
                    model,
                )
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
            logging.exception("VertexAIClient: Something went wrong: %s", ex)
            raise VertexAIClientError(
                f"Could not generate images {ex}",
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
            generation_response = cast("GenerationResponse", response)
        except Exception as ex:
            logging.exception("VertexAIClient: Something went wrong: %s", ex)
            raise VertexAIClientError(
                f"Could not generate text {ex}",
            ) from ex
        return generation_response.text.strip()

    def edit_image(
        self,
        model: str,
        image_uri: str,
        prompt: str,
        number_of_images: int,
        edit_mode: str,
        mask_uri: str,
    ) -> str:
        """Edits and image.

        Args:
            model: The imagen edit model used.
            image_uri: The URI of the image to edit. E.g. "gs://dir/my_image.jpg"
            prompt: The edit prompt.
            number_of_images: Number of images to create after edits.
            edit_mode: The edit mode for editing.
            mask_mode: The area to edit.
            mask_uri: The URI of the image mask.

        Returns:
            The edited image URI.

        Raises:
            VertexAIClientError: If the image could not be edited.
        """
        try:
            edit_model = ImageGenerationModel.from_pretrained(model)
            bucket_name, file_name, extension = (
                self.storage_client.get_storage_object_metadata(image_uri)
            )
            timestamp_int = int(time.time())
            edited_file_name = f"{file_name}-edited-{timestamp_int}{extension}"

            image = Image(gcs_uri=image_uri)
            mask = Image(gcs_uri=mask_uri) if mask_uri else None
            seed = 1
            dilation = 0.01
            if edit_mode == EditMode.EDIT_MODE_BGSWAP.name:
                dilation = 0.0
            if edit_mode == EditMode.EDIT_MODE_OUTPAINT.name:
                dilation = 0.03
            if edit_mode in (
                EditMode.EDIT_MODE_INPAINT_INSERTION.name,
                EditMode.EDIT_MODE_INPAINT_REMOVAL.name,
                EditMode.EDIT_MODE_OUTPAINT.name,
                EditMode.EDIT_MODE_BGSWAP.name,
            ):
                raw_ref_image = RawReferenceImage(image=image, reference_id=0)
                mask_ref_image = MaskReferenceImage(
                    reference_id=1,
                    image=mask,
                    mask_mode="user_provided",
                    dilation=dilation,
                )
                reference_images = [raw_ref_image, mask_ref_image]

            if edit_mode == EditMode.EDIT_MODE_CONTROLLED_EDITING.name:
                ext = mimetypes.guess_all_extensions(image._mime_type)
                tmp_image_file = f"/tmp/canny{ext}"
                image.save(tmp_image_file)
                img = cv2.imread(tmp_image_file)
                threshold_lower = 100
                threshold_upper = 150
                tmp_edge_file = f"/tmp/canny_edge{ext}"
                edge = cv2.Canny(img, threshold_lower, threshold_upper)
                cv2.imwrite(tmp_edge_file, edge)
                control_image = ControlReferenceImage(
                    reference_id=1,
                    image=Image.load_from_file(location=tmp_edge_file),
                    control_type="canny",
                )
                reference_images = [control_image]

            if edit_mode == EditMode.EDIT_MODE_PRODUCT_IMAGE.name:
                raw_ref_image = RawReferenceImage(image=image, reference_id=0)
                reference_images = [raw_ref_image]

            edited_image = edit_model.edit_image(
                prompt=prompt,
                edit_mode=EditMode[edit_mode].value,
                reference_images=reference_images,
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
            logging.exception("VertexAIClient: Something went wrong: %s", ex)
            raise VertexAIClientError(
                f"Could not edit image {ex}",
            ) from ex
        return edited_file_uri

    def upscale_image(
        self,
        model: str,
        image_uri: str,
        new_size: int,
        upscale_factor: Literal["x2", "x4"],
        output_mime_type: Literal["image/png", "image/jpeg"],
        output_compression_quality: int,
    ) -> str:
        """Upscales an image.

        Args:
            model: The imagen model used.
            image_uri: The URI of the image to upscale. E.g. "gs://dir/my_image.jpg"
            new_size: The size of the biggest dimension of the upscaled.
            upscale_factor: The upscaling factor. Supported values are "x2" and
                "x4".
            output_mime_type: The mime type of the output image. Supported values
                are "image/png" and "image/jpeg".
            output_compression_quality: The compression quality of the output
                image
                as an int (0-100). Only applicable if the output mime type is
                "image/jpeg".

        Returns:
            The GCS URI of the upscaled file.

        Raises:
            VertexAIClientError: If the image could not be upscaled.
        """
        try:
            gen_model = ImageGenerationModel.from_pretrained(model)
            image = Image(gcs_uri=image_uri)
            upscaled_image = gen_model.upscale_image(
                image=image,
                new_size=new_size,
                upscale_factor=upscale_factor,
                output_mime_type=output_mime_type,
                output_compression_quality=output_compression_quality,
            )
            bucket_name, file_name, extension = (
                self.storage_client.get_storage_object_metadata(image_uri)
            )
            timestamp_int = int(time.time())
            upscaled_file_name = f"{file_name}-upscaled-{timestamp_int}{extension}"
            upscaled_file_uri = self.storage_client.upload(
                bucket_name=bucket_name,
                contents=upscaled_image._as_base64_string(),
                mime_type=upscaled_image._mime_type,
                file_name=upscaled_file_name,
                sub_dir="upscaled",
            )
        except Exception as ex:
            logging.exception("VertexAIClient: Something went wrong: %s", ex)
            raise VertexAIClientError(
                f"Could not upscale image {ex}",
            ) from ex
        return upscaled_file_uri

    def get_embeddings(
        self,
        image_uri: str | None = None,
        text: str | None = None,
    ) -> tuple[float, float]:
        """Gets the embeddings for an image and/or text.

        Args:
            image_uri: The URI of the image to get embeddings for.
            text: The text to get embeddings for.

        Returns:
            The embeddings for the image and/or text.

        Raises:
            VertexAIClientError: If the embeddings could not be generated.
        """
        try:
            embedding_model = MultiModalEmbeddingModel.from_pretrained(
                MULTIMODAL_EMBEDDING_MODEL,
            )
            text = text if text else None  # Ensure text is not "".
            image = None
            if image_uri:
                image = Image.load_from_file(image_uri)

            embeddings = embedding_model.get_embeddings(
                image=image,
                contextual_text=text,
                dimension=EMBEDDING_DIMENSIONS,
            )
        except Exception as ex:
            logging.exception("VertexAIClient: Something went wrong: %s", ex)
            raise VertexAIClientError(
                f"Could not get embeddings for image or text: {ex}",
            ) from ex
        return embeddings.image_embedding, embeddings.text_embedding

    def outpaint_image(
        self,
        image_uri: str,
        target_size: tuple[int, int] = (1024, 1024),
        horizontal_alignment: str = "center",
        vertical_alignment: str = "center",
    ) -> dict[str, str]:
        """Outpaints an image.

        Args:
            image_uri: The URI of the image to outpaint.
            target_size: The target size of the outpainted image.
            horizontal_alignment: The horizontal alignment of the outpainted
                image.
            vertical_alignment: The vertical alignment of the outpainted image

        Returns:
            The URIs of the outpainted image, mask and overlay.

        Raises:
            VertexAIClientError: If the image could not be outpainted.
        """
        try:
            image = Image(gcs_uri=image_uri)
            new_w, new_h = target_size
            if vertical_alignment == "top":
                vertical_offset_ratio = -1
            elif vertical_alignment == "center":
                vertical_offset_ratio = 0
            elif vertical_alignment == "bottom":
                vertical_offset_ratio = 1

            if horizontal_alignment == "left":
                horizontal_offset_ratio = -1
            elif horizontal_alignment == "center":
                horizontal_offset_ratio = 0
            elif horizontal_alignment == "right":
                horizontal_offset_ratio = 1
            image_pil, mask_pil = image_utils.pad_image_and_mask(
                image,
                target_size=(new_w, new_h),
                vertical_offset_ratio=vertical_offset_ratio,
                horizontal_offset_ratio=horizontal_offset_ratio,
            )
            new_image = Image(image_utils.get_bytes_from_pil(image_pil))
            bucket_name, file_name, _ = self.storage_client.get_storage_object_metadata(
                image_uri,
            )
            new_image_ext = mimetypes.guess_all_extensions(new_image._mime_type)[0]
            timestamp_int = int(time.time())
            new_image_file_name = f"{file_name}-outpaint-{timestamp_int}{new_image_ext}"
            new_image_uri = self.storage_client.upload(
                bucket_name=bucket_name,
                contents=new_image._as_base64_string(),
                mime_type=new_image._mime_type,
                file_name=new_image_file_name,
                sub_dir="outpainted",
            )

            new_mask = Image(image_utils.get_bytes_from_pil(mask_pil))
            bucket_name, file_name, _ = self.storage_client.get_storage_object_metadata(
                image_uri,
            )
            new_mask_ext = mimetypes.guess_all_extensions(new_mask._mime_type)[0]
            new_mask_file_name = f"{file_name}-mask{new_mask_ext}"
            new_mask_uri = self.storage_client.upload(
                bucket_name=bucket_name,
                contents=new_mask._as_base64_string(),
                mime_type=new_mask._mime_type,
                file_name=new_mask_file_name,
                sub_dir="masks",
            )
            overlay = image_utils.overlay_mask(
                new_image,
                new_mask,
            )
            overlay_ext = mimetypes.guess_all_extensions(overlay._mime_type)[0]
            overlay_file_name = f"{file_name}-overlay{overlay_ext}"
            overlay_file_uri = self.storage_client.upload(
                bucket_name=bucket_name,
                contents=overlay._as_base64_string(),
                mime_type=overlay._mime_type,
                file_name=overlay_file_name,
                sub_dir="overlays",
            )
        except Exception as ex:
            logging.exception("VertexAIClient: Something went wrong: %s", ex)
            raise VertexAIClientError(
                f"Could not outpaint image {ex}",
            ) from ex
        return {
            "image_uri": new_image_uri,
            "mask_uri": new_mask_uri,
            "overlay_uri": overlay_file_uri,
        }

    def segment_image(
        self,
        image_uri: str,
        mode: str = "foreground",
        prompt: str | None = None,
        scribble: Scribble | None = None,
        target_size: tuple[int, int] | None = None,
        horizontal_alignment: str | None = None,
        vertical_alignment: str | None = None,
    ) -> dict[str, str]:
        """Segments an image.

        Args:
            image_uri: The URI of the image to segment.
            mode: The segmentation mode.
            prompt: The prompt to use for segmentation.
            scribble: The scribble to use for segmentation.
            target_size: The target size of the segmented image.
            horizontal_alignment: The horizontal alignment of the image.
            vertical_alignment: The vertical alignment of the image

        Returns:
            The URI of the segmented image, mask and overlay.

        Raises:
            VertexAIClientError: If the image could not be segmented.
        """
        if mode == "user_provided":
            return self.outpaint_image(
                image_uri,
                target_size=target_size,
                horizontal_alignment=horizontal_alignment,
                vertical_alignment=vertical_alignment,
            )
        try:
            segmentation_model = ImageSegmentationModel.from_pretrained(
                IMAGE_SEGMENTATION_MODEL,
            )
            base_image = Image.load_from_file(image_uri)
            segmented_image = segmentation_model.segment_image(
                base_image=base_image,
                prompt=prompt if prompt else None,
                scribble=scribble,
                mode=mode,
            )
            segmented_image_mime_type = segmented_image.masks[0]._mime_type
            bucket_name, file_name, extension = (
                self.storage_client.get_storage_object_metadata(image_uri)
            )
            extension = mimetypes.guess_all_extensions(segmented_image_mime_type)[0]
            timestamp_int = int(time.time())
            mask_file_name = f"{file_name}-mask-{timestamp_int}{extension}"

            mask_file_uri = self.storage_client.upload(
                bucket_name=bucket_name,
                contents=segmented_image.masks[0]._as_base64_string(),
                mime_type=segmented_image.masks[0]._mime_type,
                file_name=mask_file_name,
                sub_dir="masks",
            )
            overlay = image_utils.overlay_mask(
                base_image,
                segmented_image.masks[0],
            )
            overlay_file_name = f"{file_name}-overlay{extension}"
            overlay_file_uri = self.storage_client.upload(
                bucket_name=bucket_name,
                contents=overlay._as_base64_string(),
                mime_type=overlay._mime_type,
                file_name=overlay_file_name,
                sub_dir="overlays",
            )
        except Exception as ex:
            logging.exception("VertexAIClient: Something went wrong: %s", ex)
            raise VertexAIClientError(
                f"Could not segment image {ex}",
            ) from ex
        return {
            "mask_uri": mask_file_uri,
            "overlay_uri": overlay_file_uri,
            "image_uri": image_uri,
        }
