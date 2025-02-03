"""Entry point for the image generation service."""

import fastapi
import google.cloud.logging
from absl import logging
from models import (
    EditImageRequest,
    EditImageResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageUpscalingRequest,
    ImageUpscalingResponse,
    TextGenerationRequest,
    TextGenerationResponse,
    VideoGenerationRequest,
    VideoGenerationResponse,
)
from worker import (
    ImageEditingServiceWorker,
    ImageGenerationServiceWorker,
    ImageUpscalingServiceWorker,
    TextGenerationServiceWorker,
    VideoGenerationServiceWorker,
)

from common.clients import aiplatform_client_lib, vertexai_client_lib

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

app = fastapi.FastAPI()


@app.post("/generate_images")
def generate_images(request: ImageGenerationRequest) -> ImageGenerationResponse:
    try:
        kwargs = request.dict()
        worker = ImageGenerationServiceWorker(settings=None)
        image_uris = worker.execute(**kwargs)
        return {"image_uris": image_uris}
    except vertexai_client_lib.VertexAIClientError as err:
        logging.error(
            "ImageGenerationService: An error occured trying to generate images %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", err),
        ) from err


@app.post("/generate_text")
def generate_text(request: TextGenerationRequest) -> TextGenerationResponse:
    try:
        kwargs = request.dict()
        worker = TextGenerationServiceWorker(settings=None)
        prompt = worker.execute(**kwargs)
        return {"text": prompt}
    except vertexai_client_lib.VertexAIClientError as err:
        logging.error(
            "TextGenerationServiceWorker: An error occured trying to generate text %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err


@app.post("/edit_image")
def edit_image(request: EditImageRequest) -> EditImageResponse:
    try:
        kwargs = request.dict()
        worker = ImageEditingServiceWorker(settings=None)
        edited_image_uri = worker.execute(**kwargs)
        return {"edited_image_uri": edited_image_uri}
    except vertexai_client_lib.VertexAIClientError as err:
        logging.error(
            "ImageEditingServiceWorker: An error occured trying to edit image: %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err


@app.post("/upscale_image")
def upscale_image(request: ImageUpscalingRequest) -> ImageUpscalingResponse:
    try:
        kwargs = request.dict()
        worker = ImageUpscalingServiceWorker(settings=None)
        upscaled_image_uri = worker.execute(**kwargs)
        return {"upscaled_image_uri": upscaled_image_uri}
    except vertexai_client_lib.VertexAIClientError as err:
        logging.error(
            "ImageUpscalingServiceWorker: An error occured trying to upscale image: %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err


@app.post("/generate_video")
def generate_video(request: VideoGenerationRequest) -> VideoGenerationResponse:
    try:
        kwargs = request.dict()
        worker = VideoGenerationServiceWorker(settings=None)
        video_uri = worker.execute(**kwargs)
        return {"video_uri": video_uri}
    except aiplatform_client_lib.AIPlatformClientError as err:
        logging.error(
            "VideoGenerationServiceWorker: An error occured trying to generate video: %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err
