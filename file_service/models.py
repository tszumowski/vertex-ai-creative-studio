"""Data model for the image generation service."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class DownloadFileRequest(BaseModel):
    gcs_uri: str


class DownloadFileResponse(BaseModel):
    content: str
    mimetype: str
    filename: str


class UploadFileRequest(BaseModel):
    bucket_name: str
    contents: str
    mime_type: str
    file_name: str
    sub_dir: str | None = ""


class UploadFileResponse(BaseModel):
    file_uri: str


class SearchFileRequest(BaseModel):
    search_text: str


class SearchFileResponse(BaseModel):
    results: list[dict[str, Any]] = []
