"""Worker for generating images."""

from typing import Any

from common import base_worker
from common.clients import aiplatform_client_lib, vertexai_client_lib


class ImageGenerationServiceWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> list[str]:
        """Execute the Image generation process."""
        client = vertexai_client_lib.VertexAIClient()
        images = client.generate_images(**kwargs)
        # Add other tasks e.g. persiting to database here.
        return images


class TextGenerationServiceWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> str:
        """Execute the Image generation process."""
        client = vertexai_client_lib.VertexAIClient()
        text = client.generate_text(**kwargs)
        # Add other tasks e.g. persiting to database here.
        return text


class ImageEditingServiceWorker(base_worker.BaseWorker):
    """Processes an image editing request."""

    def execute(self, **kwargs: dict[str, Any]) -> str:
        """Execute the Image editing process."""
        client = aiplatform_client_lib.AIPlatformClient()
        edited_image_uri = client.edit_image(**kwargs)
        # Add other tasks e.g. persiting to database here.
        return edited_image_uri
