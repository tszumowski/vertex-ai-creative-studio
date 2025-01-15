"""Entry point for the api gateway."""

from __future__ import annotations

import os

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

_IMAGE_GENERATION_SERVICE_URL = (
    f"https://image-generation-service-{PROJECT_NUMBER}.{REGION}.run.app"
)


@app.post("/image_generation/generate_images")
async def generate_images_gateway(request: Request) -> list[str]:
    """Exposes the image generation endpoint through the API Gateway."""
    logging.info("API Gateway: Received request: %s", request)
    data = await request.json()
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{_IMAGE_GENERATION_SERVICE_URL}/generate_images",
        json_data=data,
        service_url=_IMAGE_GENERATION_SERVICE_URL,
    )
    logging.info("API Gateway: Received response: %s", await response.json())
    data = await response.json()
    return data.get("image_uris")
