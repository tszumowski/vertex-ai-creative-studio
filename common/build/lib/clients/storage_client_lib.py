"""Module to interact with Google Cloud Storage."""

import base64
import os

import google.auth
from absl import logging
from google.cloud import storage


class StorageClient:
    """Class to interact with the Google Cloud Storage."""

    def __init__(self) -> None:
        credentials, project = google.auth.default()
        self._client = storage.Client(project=project, credentials=credentials)
        logging.info("StorageClient: Instantiated.")

    def upload(
        self,
        bucket_name: str,
        contents: bytes,
        mime_type: str,
        file_name: str,
        sub_dir: str = "",
        decode: bool = False,
    ) -> str:
        """Stores contents on GCS.

        Args:
            bucket: A GCS bucket.
            contents: base64 encoded bytes.
            mime_type: The mime type of the contents.
            file_name: The name for the file to be generated.
            sub_dir: The subdirectory to store the file in.
            decode: Whether or not the contents need decoding.

        Returns:
            The GCS uri of the stored image.
        """
        bucket = self._client.bucket(bucket_name)
        destination_blob_name = os.path.join(sub_dir, file_name)
        blob = bucket.blob(destination_blob_name)
        if decode:
            logging.info("StorageClient: Decoding contents.")
            contents_bytes = base64.b64decode(contents)
            blob.upload_from_string(contents_bytes, content_type=mime_type)
        else:
            blob.upload_from_string(contents, content_type=mime_type)
        uri = f"gs://{bucket_name}/{destination_blob_name}"
        logging.info("StorageClient: Uploaded image to %s.", uri)
        return uri

    def download_as_string(self, bucket_name: str, file_path: str) -> str:
        """Downloads a file as string.

        Args:
            bucket_name: A GCS bucket.
            file_path: The path to the file within the bucket.

        Returns:
            The b64 encodeded string.
        """
        bucket = self._client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        content = blob.download_as_bytes()
        return base64.b64encode(content).decode("utf-8")
