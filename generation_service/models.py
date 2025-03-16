"""Data model for the generation service."""

from __future__ import annotations

from pydantic import BaseModel


class ImageGenerationRequest(BaseModel):
    model: str
    prompt: str
    num_images: int | None = 1
    negative_prompt: str | None = None
    aspect_ratio: str | None = "1:1"
    add_watermark: bool | None = True
    language: str | None = "auto"
    reference_images: list[dict[str, str]] | None = None


class ImageGenerationResponse(BaseModel):
    image_uris: list[str]


class TextGenerationRequest(BaseModel):
    prompt: str
    media_uris: list[str] | None = None


class TextGenerationResponse(BaseModel):
    text: str


class EditImageRequest(BaseModel):
    image_uri: str
    prompt: str
    number_of_images: int = 1
    edit_mode: str = ""
    mask_uri: str = ""


class EditImageResponse(BaseModel):
    edited_image_uri: str


class VideoGenerationRequest(BaseModel):
    prompt: str
    image_uri: str
    aspect_ratio: str = "16:9"


class VideoGenerationResponse(BaseModel):
    video_uri: str


class ImageUpscalingRequest(BaseModel):
    image_uri: str
    new_size: int | None = 2048
    upscale_factor: str | None = None
    output_mime_type: str | None = "image/png"
    output_compression_quality: int | None = None


class ImageUpscalingResponse(BaseModel):
    upscaled_image_uri: str


class ImageSegmentationRequest(BaseModel):
    image_uri: str
    mode: str = "foreground"
    prompt: str | None = None
    target_size: tuple[int, int] | None = None
    horizontal_alignment: str | None = None
    vertical_alignment: str | None = None


class ImageSegmentationResponse(BaseModel):
    mask: dict[str, str]
