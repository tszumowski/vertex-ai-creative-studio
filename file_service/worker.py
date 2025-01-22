"""Worker for interacting with the file storage client."""

from typing import Any

from common import base_worker
from common.clients import storage_client_lib


class DownloadWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> list[str]:
        """Execute the Image generation process."""
        client = storage_client_lib.StorageClient()
        file_string = client.download_as_string(**kwargs)
        # Add other tasks e.g. persiting to database here.
        return file_string


class UploadWorker(base_worker.BaseWorker):
    """Processes an image generation request."""

    def execute(self, **kwargs: dict[str, Any]) -> list[str]:
        """Execute the Image generation process."""
        client = storage_client_lib.StorageClient()
        file_uri = client.upload(**kwargs)
        # Add other tasks e.g. persiting to database here.
        return file_uri
