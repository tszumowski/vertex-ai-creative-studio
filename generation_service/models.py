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

"""Data model for the generation service."""

from __future__ import annotations

from pydantic import BaseModel


class ImageGenerationRequest(BaseModel):
    model: str
    prompt: str
    num_images: int
    negative_prompt: str
    aspect_ratio: str
    add_watermark: bool
    language: str | None = "auto"
    reference_images: list[dict[str, str]] | None = None
    username: str | None = None


class ImageGenerationResponse(BaseModel):
    image_uris: list[str]


class TextGenerationRequest(BaseModel):
    prompt: str
    media_uris: list[str] | None = None


class TextGenerationResponse(BaseModel):
    text: str


class EditImageRequest(BaseModel):
    model: str
    image_uri: str
    prompt: str
    number_of_images: int = 1
    edit_mode: str
    mask_uri: str | None = None
    username: str | None = None


class EditImageResponse(BaseModel):
    edited_image_uris: list[str]


class VideoGenerationRequest(BaseModel):
    prompt: str
    image_uri: str
    aspect_ratio: str
    username: str | None = None


class VideoGenerationResponse(BaseModel):
    video_uris: list[str]


class ImageUpscalingRequest(BaseModel):
    image_uri: str
    new_size: int | None = 2048
    upscale_factor: str | None = None
    output_mime_type: str | None = "image/png"
    output_compression_quality: int | None = None
    username: str | None = None


class ImageUpscalingResponse(BaseModel):
    upscaled_image_uri: str


class ImageSegmentationRequest(BaseModel):
    image_uri: str
    mode: str
    prompt: str
    target_size: tuple[int, int] | None = None
    horizontal_alignment: str | None = None
    vertical_alignment: str | None = None


class ImageSegmentationResponse(BaseModel):
    mask: dict[str, str]
