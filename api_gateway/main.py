"""Entry point for the api gateway."""

from __future__ import annotations

import os
from typing import Any

import aiohttp
import google.auth.transport.requests
import google.oauth2.id_token
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
REGION = os.environ.get("REGION")

_IMAGE_GENERATION_SERVICE_URL = (
    f"https://image-generation-service-{PROJECT_NUMBER}.{REGION}.run.app"
)


def get_id_token(audience: str) -> str:
    """Fetches an ID token for the specified audience."""
    req = google.auth.transport.requests.Request()
    return google.oauth2.id_token.fetch_id_token(req, audience)


async def handle_exceptions(e: Exception) -> HTTPException:
    """Handles exceptions that may occur during image generation."""
    if isinstance(e, aiohttp.ClientResponseError):
        raise HTTPException(
            status_code=e.status,
            detail=f"Image generation service error: {e.message}",
        ) from e
    if isinstance(e, aiohttp.ClientConnectionError):
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to image generation service: {e}",
        ) from e
    if isinstance(e, aiohttp.ClientError):
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with image generation service: {e}",
        ) from e
    # Handle other unexpected exceptions
    raise HTTPException(
        status_code=500,
        detail=f"An unexpected error occurred: {e}",
    ) from e


async def make_authenticated_request_with_handled_exception(
    method: str,
    url: str,
    json_data: dict[str, Any] | None = None,
) -> JSONResponse:
    """
    Makes an authenticated request to the specified URL with exception handling.
    """
    try:
        id_token = get_id_token(_IMAGE_GENERATION_SERVICE_URL)
        headers = {"Authorization": f"Bearer {id_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                json=json_data,
                headers=headers,
            ) as response:
                response.raise_for_status()
                return JSONResponse(
                    content=await response.json(),
                    status_code=response.status,
                )
    except Exception as e:
        raise await handle_exceptions(e) from e


@app.post("/image-generation/generate_images")
async def generate_image_api(request: Request) -> JSONResponse:
    """Exposes the image generation endpoint through the API Gateway."""
    data = await request.json()
    return await make_authenticated_request_with_handled_exception(
        "POST",
        f"{_IMAGE_GENERATION_SERVICE_URL}/generate_images",
        data,
    )
