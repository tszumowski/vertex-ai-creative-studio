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

"""Entry point for the api gateway."""

from __future__ import annotations

import os
from typing import Any

import google.cloud.logging
from absl import logging
from fastapi import FastAPI, Request

from common.utils import api_utils

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


async def process_request(
    request: Request,
    service_url: str,
    endpoint: str,
    method: str = "POST",
) -> dict[str, Any]:
    """Processes a request to the API Gateway.

    Args:
        request: The request to process.
        service_url: The URL of the service to call.
        endpoint: The endpoint to call.
        method: The HTTP method to use.

    Returns:
        The response from the service.
    """
    request_body = await request.json()
    logging.info("API Gateway: Received request: %s", request_body)
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method=method,
        url=f"{service_url}/{endpoint}",
        json_data=request_body,
        service_url=service_url,
    )
    data = await response.json()
    logging.info("API Gateway: Received response: %s", data)
    return data


@app.post("/generation/generate_images")
async def generate_images_gateway(request: Request) -> dict[str, Any]:
    """Exposes the image generation endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_GENERATION_SERVICE_URL,
        endpoint="generate_images",
    )


@app.post("/generation/generate_video")
async def generate_video_gateway(request: Request) -> dict[str, Any]:
    """Exposes the video generation endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_GENERATION_SERVICE_URL,
        endpoint="generate_video",
    )


@app.post("/generation/generate_text")
async def generate_text(request: Request) -> dict[str, Any]:
    """Exposes the image generation endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_GENERATION_SERVICE_URL,
        endpoint="generate_text",
    )


@app.post("/editing/edit_image")
async def edit_image(request: Request) -> dict[str, Any]:
    """Exposes the image editing endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_GENERATION_SERVICE_URL,
        endpoint="edit_image",
    )


@app.post("/editing/segment_image")
async def segment_image(request: Request) -> dict[str, Any]:
    """Exposes the image editing endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_GENERATION_SERVICE_URL,
        endpoint="segment_image",
    )


@app.post("/editing/upscale_image")
async def upscale_image(request: Request) -> dict[str, Any]:
    """Exposes the image upscaling endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_GENERATION_SERVICE_URL,
        endpoint="upscale_image",
    )


@app.post("/files/download")
async def download(request: Request) -> dict[str, Any]:
    """Exposes the files download endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_FILE_SERVICE_URL,
        endpoint="download",
    )


@app.post("/files/upload")
async def upload(request: Request) -> dict[str, Any]:
    """Exposes the files upload endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_FILE_SERVICE_URL,
        endpoint="upload",
    )


@app.post("/files/search")
async def search(request: Request) -> dict[str, Any]:
    """Exposes the files search endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_FILE_SERVICE_URL,
        endpoint="search",
    )


@app.post("/files/list")
async def list_all(request: Request) -> dict[str, Any]:
    """Exposes the files list endpoint through the API Gateway."""
    return await process_request(
        request=request,
        service_url=_FILE_SERVICE_URL,
        endpoint="list",
    )
