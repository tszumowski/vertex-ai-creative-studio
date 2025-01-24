"""Data model for the image generation service."""

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
    mask_mode: str = "foreground"
    segmentation_classes: list[str] = []


class EditImageResponse(BaseModel):
    edited_image_uri: str


class VideoGenerationRequest(BaseModel):
    prompt: str
    image_uri: str
    aspect_ratio: str = "16:9"


class VideoGenerationResponse(BaseModel):
    video_uri: str
