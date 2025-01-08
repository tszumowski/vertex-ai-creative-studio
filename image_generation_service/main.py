"""Entry point for the image generation service."""

import fastapi
import google.cloud.logging
from absl import logging

from common import vertexai_client_lib
from image_generation_service.models import (
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from image_generation_service.worker import ImageGenerationServiceWorker

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

app = fastapi.FastAPI()


@app.post("/generate_images")
async def generate_images(request: ImageGenerationRequest) -> ImageGenerationResponse:
    try:
        kwargs = request.dict()
        worker = ImageGenerationServiceWorker()
        return worker.execute(**kwargs)
    except vertexai_client_lib.VertexAIClientError as err:
        logging.error(
            "ImageGenerationService: An error occured trying to generate images %s", err
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", err),
        ) from err
