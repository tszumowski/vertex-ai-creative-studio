"""Worker for generating images."""

from typing import Any

from common import base_worker, vertexai_client_lib


class ImageGenerationServiceWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> list[str]:
        """Execute the Image generation process."""
        client = vertexai_client_lib.ImagenClient()
        images = client.generate_images(**kwargs)
        # Add other tasks e.g. persiting to database here.
        return images
