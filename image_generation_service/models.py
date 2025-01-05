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
    images: list[str]
