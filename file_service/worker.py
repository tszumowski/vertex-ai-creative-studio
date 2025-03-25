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

"""Worker for interacting with the file storage client."""

from typing import Any

from google.cloud.firestore import Query

from common import base_worker
from common.clients import storage_client_lib, vertexai_client_lib


class DownloadWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> tuple[str, str, str]:
        """Execute the Image generation process."""
        client = storage_client_lib.StorageClient()
        media_data, mimetype, filename = client.download_as_string(**kwargs)
        # Add other tasks e.g. persiting to database here.
        return media_data, mimetype, filename


class UploadWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> list[str]:
        """Execute the Image generation process."""
        client = storage_client_lib.StorageClient()
        file_uri = client.upload(**kwargs)
        # Add other tasks e.g. persiting to database here.
        return file_uri


class SearchWorker(base_worker.BaseWorker):
    """Processes a search request."""

    def execute(self, **kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        """Execute the search process."""
        vertexai_client = vertexai_client_lib.VertexAIClient()
        _, text_embedding = vertexai_client.get_embeddings(
            text=kwargs.get("search_text"),
        )
        results = self.firestore_client.nn_search(embedding=text_embedding)
        # Add other tasks e.g. persiting to database here.
        return results

    def list_all(self) -> list[dict[str, Any]]:
        return self.firestore_client.query(
            query_fun=lambda q: q.order_by(
                "timestamp",
                direction=Query.DESCENDING,
            ),
        )
