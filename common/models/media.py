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

"""Defines the GenMedia data model."""

from __future__ import annotations

import datetime
from typing import Any

from google.cloud.firestore_v1.vector import Vector
from vertexai.preview.vision_models import Image

from common.clients import vertexai_client_lib
from common.utils import image_utils


class GenMedia:
    """A class to hold information about generated media."""

    def __init__(
        self,
        media_uri: str,
        worker: str,
        username: str,
        **kwargs: dict[str, Any],
    ) -> None:
        """Instantiates the GenMedia class.

        Args:
            media_uri: The URI of the generated media.
            worker: The name of the worker that generated the media.
            username: The username of the user that generated the media.
            **kwargs: Additional keyword arguments.
        """
        self.media_uri = media_uri
        self.worker = worker
        self.username = username
        self.prompt = kwargs.get("prompt")
        self.model = kwargs.get("model")
        self.aspect_ratio = image_utils.get_aspect_ratio_string(
            Image(gcs_uri=media_uri),
        )
        self.image_embeddings = None
        self.prompt_embeddings = None
        self.timestamp = datetime.datetime.now(
            datetime.timezone.utc,
        )
        self.format = Image(gcs_uri=media_uri)._mime_type
        self.width, self.height = Image(gcs_uri=media_uri)._size
        self._generate_vectors()

    def _generate_vectors(self) -> None:
        """Generates the image and prompt embeddings."""
        vertexai_client = vertexai_client_lib.VertexAIClient()
        image_embeddings, prompt_embeddings = vertexai_client.get_embeddings(
            self.media_uri,
            self.prompt,
        )
        if image_embeddings:
            self.image_embeddings = Vector(image_embeddings)
        if prompt_embeddings:
            self.prompt_embeddings = Vector(prompt_embeddings)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__
