from __future__ import annotations

import base64
import io
import json
import re
from typing import Any

from absl import logging
from PIL import Image


def extract_username(email_string: str | None) -> str:
    """Extracts the username from an email-like string.

    Args:
        email_string: The string containing the username and domain.

    Returns:
        The extracted username, or None if no valid username is found.
    """
    if email_string:
        match = re.search(
            r":([^@]+)@", email_string
        )  # Matches anything between ":" and "@"
        if match:
            return match.group(1)
    return ""


def get_image_dimensions_from_base64(base64_string: str) -> tuple[int, int]:
    """Retrieves the width and height of an image from a base64 encoded string.

    Args:
        base64_string: The base64 encoded image data.

    Returns:
        A tuple (width, height) if successful, or None if an error occurs.
    """
    try:
        # Remove the data URL prefix if it exists.
        if base64_string.startswith("data:image"):
            parts = base64_string.split(",")
            if len(parts) > 1:
                base64_string = parts[1]

        image_data = base64.b64decode(base64_string)
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)
        width, height = img.size
        return width, height
    except Exception as e:
        logging.info(f"App: Error getting image dimensions: {e}")
        return None


def make_local_request(endpoint: str) -> dict[str, Any]:
    filepath = (
        f"mocks/{endpoint}.json"  # Assuming mock files are in a 'mocks' directory
    )
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        logging.info(f"Mock file not found: {filepath}")
        return None  # Or raise an exception
