"""Data model for the image generation service."""

from __future__ import annotations

from pydantic import BaseModel


class DownloadFileRequest(BaseModel):
    bucket_name: str
    file_path: str


class DownloadFileResponse(BaseModel):
    file_string: str


class UploadFileRequest(BaseModel):
    bucket_name: str
    contents: str
    mime_type: str
    file_name: str
    sub_dir: str | None = ""


class UploadFileResponse(BaseModel):
    file_uri: str
