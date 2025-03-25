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

"""Worker for generating images."""

from typing import Any

from common import base_worker
from common.clients import aiplatform_client_lib, vertexai_client_lib
from common.models.media import GenMedia
from common.utils import api_utils


class ImageGenerationServiceWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> list[str]:
        """Execute the Image generation process."""
        try:
            client = vertexai_client_lib.VertexAIClient()
            image_uris = client.generate_images(**kwargs)
            # Add other tasks e.g. persiting to database here.
            for image_uri in image_uris:
                genmedia = GenMedia(
                    image_uri,
                    worker=self.name,
                    username=self.settings.username,
                    **kwargs,
                )
                self.firestore_client.create(data=genmedia.to_dict())
            event = api_utils.stringify_values(kwargs)
            event["name"] = self.name
            self.tadau_client.send_events([event])
        except vertexai_client_lib.VertexAIClientError as err:
            self.tadau_client.send_error_event(
                error_message=str(err),
                error_code=type(err).__name__,
                error_location=self.name,
                error_location_id=self.name,
            )
            raise
        return image_uris


class TextGenerationServiceWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> str:
        """Execute the Image generation process."""
        try:
            client = vertexai_client_lib.VertexAIClient()
            text = client.generate_text(**kwargs)
            event = api_utils.stringify_values(kwargs)
            event["name"] = self.name
            self.tadau_client.send_events([event])
        except vertexai_client_lib.VertexAIClientError as err:
            self.tadau_client.send_error_event(
                error_message=str(err),
                error_code=type(err).__name__,
                error_location=self.name,
                error_location_id=self.name,
            )
            raise
        return text


class ImageEditingServiceWorker(base_worker.BaseWorker):
    """Processes an image editing request."""

    def execute(self, **kwargs: dict[str, Any]) -> list[str]:
        """Execute the Image editing process."""
        try:
            client = aiplatform_client_lib.AIPlatformClient()
            edited_image_uris = client.edit_image(**kwargs)
            for uri in edited_image_uris:
                genmedia = GenMedia(
                    uri,
                    worker=self.name,
                    username=self.settings.username,
                    **kwargs,
                )
                self.firestore_client.create(data=genmedia.to_dict())
            event = api_utils.stringify_values(kwargs)
            event["name"] = self.name
            self.tadau_client.send_events([event])
        except vertexai_client_lib.VertexAIClientError as err:
            self.tadau_client.send_error_event(
                error_message=str(err),
                error_code=type(err).__name__,
                error_location=self.name,
                error_location_id=self.name,
            )
            raise
        return edited_image_uris


class ImageUpscalingServiceWorker(base_worker.BaseWorker):
    """Processes an image upscaling request."""

    def execute(self, **kwargs: dict[str, Any]) -> str:
        """Execute the Image editing process."""
        try:
            client = vertexai_client_lib.VertexAIClient()
            upscaled_image_uri = client.upscale_image(**kwargs)
            genmedia = GenMedia(
                upscaled_image_uri,
                worker=self.name,
                username=self.settings.username,
                **kwargs,
            )
            self.firestore_client.create(data=genmedia.to_dict())
            event = api_utils.stringify_values(kwargs)
            event["name"] = self.name
            self.tadau_client.send_events([event])
        except vertexai_client_lib.VertexAIClientError as err:
            self.tadau_client.send_error_event(
                error_message=str(err),
                error_code=type(err).__name__,
                error_location=self.name,
                error_location_id=self.name,
            )
            raise
        return upscaled_image_uri


class VideoGenerationServiceWorker(base_worker.BaseWorker):
    """Processes a video generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> str:
        """Execute the Video generation process."""
        try:
            client = aiplatform_client_lib.AIPlatformClient()
            video_uris = client.generate_video(**kwargs)
            for uri in video_uris:
                genmedia = GenMedia(
                    uri,
                    worker=self.name,
                    username=self.settings.username,
                    **kwargs,
                )
            self.firestore_client.create(data=genmedia.to_dict())
            event = api_utils.stringify_values(kwargs)
            event["name"] = self.name
            self.tadau_client.send_events([event])
        except aiplatform_client_lib.AIPlatformClientError as err:
            self.tadau_client.send_error_event(
                error_message=str(err),
                error_code=type(err).__name__,
                error_location=self.name,
                error_location_id=self.name,
            )
            raise
        return video_uris


class ImageSegmentationServiceWorker(base_worker.BaseWorker):
    """Processes an image segmentation request."""

    def execute(self, **kwargs: dict[str, Any]) -> dict[str, str]:
        """Execute the Image segmentation process."""
        try:
            client = vertexai_client_lib.VertexAIClient()
            mask = client.segment_image(**kwargs)
            event = api_utils.stringify_values(kwargs)
            event["name"] = self.name
            self.tadau_client.send_events([event])
        except aiplatform_client_lib.AIPlatformClientError as err:
            self.tadau_client.send_error_event(
                error_message=str(err),
                error_code=type(err).__name__,
                error_location=self.name,
                error_location_id=self.name,
            )
            raise
        # Add other tasks e.g. persiting to database here.
        return mask
