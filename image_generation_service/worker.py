"""Worker for generating images."""

from common import vertexai_client_lib
from common import base_worker


class ImageGenerationServiceWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs):
        """Execute the Image generation process."""
        model = kwargs.pop("model")
        client = vertexai_client_lib.ImagenClient(model)
        images = client.generate_images(**kwargs)
        # Add other tasks e.g. persiting to database here.
        return images
