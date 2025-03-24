"""Entry point for the image generation service."""

import fastapi
import google.cloud.logging
from absl import logging
from models import (
    EditImageRequest,
    EditImageResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageSegmentationRequest,
    ImageSegmentationResponse,
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
    ImageSegmentationServiceWorker,
    ImageUpscalingServiceWorker,
    TextGenerationServiceWorker,
    VideoGenerationServiceWorker,
)

from common.clients import aiplatform_client_lib, vertexai_client_lib
from common.models import settings as settings_lib

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

app = fastapi.FastAPI()


@app.post("/generate_images")
def generate_images(request: ImageGenerationRequest) -> ImageGenerationResponse:
    try:
        kwargs = request.dict()
        username = kwargs.pop("username")
        settings = settings_lib.Settings(username=username)
        worker = ImageGenerationServiceWorker(settings=settings)
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
        settings = settings_lib.Settings()
        worker = TextGenerationServiceWorker(settings=settings)
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
        username = kwargs.pop("username")
        settings = settings_lib.Settings(username=username)
        worker = ImageEditingServiceWorker(settings=settings)
        edited_image_uris = worker.execute(**kwargs)
        return {"edited_image_uris": edited_image_uris}
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
        username = kwargs.pop("username")
        settings = settings_lib.Settings(username=username)
        worker = ImageUpscalingServiceWorker(settings=settings)
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
        username = kwargs.pop("username")
        settings = settings_lib.Settings(username=username)
        worker = VideoGenerationServiceWorker(settings=settings)
        video_uris = worker.execute(**kwargs)
        return {"video_uris": video_uris}
    except aiplatform_client_lib.AIPlatformClientError as err:
        logging.error(
            "VideoGenerationServiceWorker: An error occured trying to generate video: %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err


@app.post("/segment_image")
def segment_image(request: ImageSegmentationRequest) -> ImageSegmentationResponse:
    try:
        kwargs = request.dict()
        settings = settings_lib.Settings()
        worker = ImageSegmentationServiceWorker(settings=settings)
        mask = worker.execute(**kwargs)
        return {"mask": mask}
    except vertexai_client_lib.VertexAIClientError as err:
        logging.error(
            "ImageSegmentationServiceWorker: An error occured trying to segment image: %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err
