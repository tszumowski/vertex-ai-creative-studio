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

"""Helper method to make authenticated requests."""

from __future__ import annotations

import json
from typing import Any

import aiohttp
import google.auth.transport.requests
import google.oauth2.id_token
import requests
from absl import logging
from fastapi import HTTPException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
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
            detail=f"Service error: {e.message}",
        ) from e
    if isinstance(e, aiohttp.ClientConnectionError):
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to the service: {e}",
        ) from e
    if isinstance(e, aiohttp.ClientError):
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with the service: {e}",
        ) from e
    # Handle other unexpected exceptions
    logging.exception("Error when making authenticated request: %s", e)
    raise HTTPException(
        status_code=500,
        detail=f"An unexpected error occurred: {e}",
    ) from e


async def handle_async_exceptions(e: Exception) -> HTTPException:
    """Handles exceptions that may occur during image generation."""
    if isinstance(e, aiohttp.ClientResponseError):
        raise HTTPException(
            status_code=e.status,
            detail=f"Service error: {e.message}",
        ) from e
    if isinstance(e, aiohttp.ClientConnectionError):
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to the service: {e}",
        ) from e
    if isinstance(e, aiohttp.ClientError):
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with the service: {e}",
        ) from e
    # Handle other unexpected exceptions
    logging.exception("Error when making authenticated request: %s", e)
    raise HTTPException(
        status_code=500,
        detail=f"An unexpected error occurred: {e}",
    ) from e


async def make_async_request(
    method: str,
    url: str,
    json_data: dict[str, Any] | None = None,
    service_url: str | None = None,
) -> aiohttp.ClientResponse:
    """Makes an authenticated request to the specified URL with exception handling.

    Args:
        method: The HTTP method to use for the request.
        url: The URL to make the request to.
        json_data: The JSON data to send in the request (optional).
        service_url: The URL of the service to use for authentication (optional).

    Returns:
        The response from the server.

    Raises:
        HTTPException: If an error occurs during the request.
    """
    try:
        headers = None
        if service_url:
            id_token = get_id_token(service_url)
            headers = {"Authorization": f"Bearer {id_token}"}
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.request(
                method,
                url,
                json=json_data,
                headers=headers,
                timeout=30,
            ) as response:
                await response.read()
                return response
    except Exception as e:
        raise await handle_async_exceptions(e) from e


def stringify_values(data: dict[str, Any]) -> dict[str, str]:
    """Converts all values in the dictionary to strings."""
    new_dict = {}
    for key, value in data.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            new_dict[key] = str(value)
        elif isinstance(value, (dict, list, tuple)):
            new_dict[key] = json.dumps(value)
    return new_dict


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=3, min=1, max=30),
)
def make_request(
    api_endpoint: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Sends an HTTP request to a Google API endpoint.

    Args:
        api_endpoint: The URL of the Google API endpoint.
        data: (Optional) Dictionary of data to send in the request body.

    Returns:
        The response from the Google API.
    """
    # Get access token calling API
    try:
        creds, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        access_token = creds.token

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            url=api_endpoint,
            headers=headers,
            json=data,
            timeout=30,
        )
        response.raise_for_status()
    except Exception as ex:
        raise handle_exceptions(ex) from ex
    return response.json()
