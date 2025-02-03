"""Worker for generating images."""

from typing import Any

from common import base_worker
from common.clients import aiplatform_client_lib, vertexai_client_lib
from common.models.media import GenMedia


class ImageGenerationServiceWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> list[str]:
        """Execute the Image generation process."""
        client = vertexai_client_lib.VertexAIClient()
        image_uris = client.generate_images(**kwargs)
        # Add other tasks e.g. persiting to database here.
        for image_uri in image_uris:
            genmedia = GenMedia(image_uri, worker=self.name, **kwargs)
            self.firestore_client.create(data=genmedia.to_dict())
        return image_uris


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
        client = vertexai_client_lib.VertexAIClient()
        edited_image_uri = client.edit_image(**kwargs)
        # Add other tasks e.g. persiting to database here.
        genmedia = GenMedia(edited_image_uri, worker=self.name, **kwargs)
        self.firestore_client.create(data=genmedia.to_dict())
        return edited_image_uri


class ImageUpscalingServiceWorker(base_worker.BaseWorker):
    """Processes an image upscaling request."""

    def execute(self, **kwargs: dict[str, Any]) -> str:
        """Execute the Image editing process."""
        client = vertexai_client_lib.VertexAIClient()
        upscaled_image_uri = client.upscale_image(**kwargs)
        # Add other tasks e.g. persiting to database here.
        genmedia = GenMedia(upscaled_image_uri, worker=self.name, **kwargs)
        self.firestore_client.create(data=genmedia.to_dict())
        return upscaled_image_uri


class VideoGenerationServiceWorker(base_worker.BaseWorker):
    """Processes a video generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> str:
        """Execute the Video generation process."""
        client = aiplatform_client_lib.AIPlatformClient()
        video_uri = client.generate_video(**kwargs)
        # Add other tasks e.g. persiting to database here.
        genmedia = GenMedia(video_uri, worker=self.name, **kwargs)
        self.firestore_client.create(data=genmedia.to_dict())
        return video_uri
