from __future__ import annotations

from typing import Any

from google.cloud.firestore_v1.vector import Vector

from common.clients import vertexai_client_lib


class GenMedia:
    def __init__(
        self,
        media_uri: str,
        worker: str,
        **kwargs: dict[str, Any],
    ) -> None:
        self.media_uri = media_uri
        self.worker = worker
        self.generation_params = {}
        for key, value in kwargs.items():
            if key not in [
                "media_uri",
            ]:
                self.generation_params[key] = value
        self.image_embeddings = None
        self.prompt_embeddings = None

        self._generate_metadata()

    def _generate_metadata(self) -> None:
        vertexai_client = vertexai_client_lib.VertexAIClient()
        image_embeddings, prompt_embeddings = vertexai_client.get_embeddings(
            self.media_uri,
            self.generation_params.get("prompt"),
        )
        if image_embeddings:
            self.image_embeddings = Vector(image_embeddings)
        if prompt_embeddings:
            self.prompt_embeddings = Vector(prompt_embeddings)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__
