from __future__ import annotations

import datetime
from typing import Any

from google.cloud.firestore_v1.vector import Vector
from vertexai.preview.vision_models import Image

from common import image_utils
from common.clients import vertexai_client_lib


class GenMedia:
    def __init__(
        self,
        media_uri: str,
        worker: str,
        username: str,
        **kwargs: dict[str, Any],
    ) -> None:
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
