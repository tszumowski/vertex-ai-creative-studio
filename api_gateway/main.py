"""Entry point for the api gateway."""

from __future__ import annotations

import os
from typing import Any

import google.cloud.logging
from absl import logging
from fastapi import FastAPI, Request

from common import api_utils

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()
logging.info("Logging client instantiated.")

app = FastAPI()

PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
REGION = os.environ.get("REGION")

_GENERATION_SERVICE_URL = (
    f"https://genmedia-generation-service-{PROJECT_NUMBER}.{REGION}.run.app"
)

_FILE_SERVICE_URL = f"https://genmedia-file-service-{PROJECT_NUMBER}.{REGION}.run.app"


@app.post("/generation/generate_images")
async def generate_images_gateway(request: Request) -> list[str]:
    """Exposes the image generation endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_GENERATION_SERVICE_URL}/generate_images",
        json_data=data,
        service_url=_GENERATION_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("image_uris")


@app.post("/generation/generate_video")
async def generate_video_gateway(request: Request) -> list[str]:
    """Exposes the video generation endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_GENERATION_SERVICE_URL}/generate_video",
        json_data=data,
        service_url=_GENERATION_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("video_uri")


@app.post("/generation/generate_text")
async def generate_text(request: Request) -> str:
    """Exposes the image generation endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_GENERATION_SERVICE_URL}/generate_text",
        json_data=data,
        service_url=_GENERATION_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("text")


@app.post("/editing/edit_image")
async def edit_image(request: Request) -> str:
    """Exposes the image editing endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_GENERATION_SERVICE_URL}/edit_image",
        json_data=data,
        service_url=_GENERATION_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("edited_image_uri")


@app.post("/editing/segment_image")
async def segment_image(request: Request) -> dict[str, str]:
    """Exposes the image editing endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_GENERATION_SERVICE_URL}/segment_image",
        json_data=data,
        service_url=_GENERATION_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("mask")


@app.post("/editing/upscale_image")
async def upscale_image(request: Request) -> str:
    """Exposes the image upscaling endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_GENERATION_SERVICE_URL}/upscale_image",
        json_data=data,
        service_url=_GENERATION_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("upscaled_image_uri")


@app.post("/files/download")
async def download(request: Request) -> str:
    """Exposes the file download endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_FILE_SERVICE_URL}/download",
        json_data=data,
        service_url=_FILE_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("file_string")


@app.post("/files/upload")
async def upload(request: Request) -> str:
    """Exposes the file download endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_FILE_SERVICE_URL}/upload",
        json_data=data,
        service_url=_FILE_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("file_uri")


@app.post("/files/search")
async def search(request: Request) -> list[dict[str, Any]]:
    """Exposes the file search endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_FILE_SERVICE_URL}/search",
        json_data=data,
        service_url=_FILE_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("results")
