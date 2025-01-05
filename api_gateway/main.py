"""Entry point for the api gateway."""

import os

import aiohttp
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

_IMAGE_GENERATION_SERVICE_URL = os.environ.get("IMAGE_GENERATION_SERVICE_URL")


@app.post("/image-generation/generate_images")
async def generate_image_api(request: Request) -> JSONResponse:
    """Exposes the image generation endpoint through the API Gateway."""
    try:
        data = await request.json()
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{_IMAGE_GENERATION_SERVICE_URL}/generate_images",
                json=data,
            ) as response,
        ):
            response.raise_for_status()
            return JSONResponse(
                content=await response.json(),
                status_code=response.status_code,
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error forwarding request: {e}",
        ) from e
