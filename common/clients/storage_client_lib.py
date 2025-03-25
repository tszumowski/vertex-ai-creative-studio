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

"""Module to interact with Google Cloud Storage."""

import base64
import mimetypes
import os
from urllib.parse import urlparse

import google.auth
from absl import logging
from google.auth import compute_engine
from google.auth.transport import requests
from google.cloud import exceptions, storage

_DEFAULT_URL_EXPIRATION_SECONDS = 3600


class StorageClientError(Exception):
    """Base StorageClientError class"""


class StorageClient:
    """Class to interact with the Google Cloud Storage."""

    def __init__(self) -> None:
        """Instantiates the StorageClient."""
        credentials, project = google.auth.default()
        self._client = storage.Client(project=project, credentials=credentials)
        auth_request = requests.Request()
        credentials.refresh(request=auth_request)
        self._signing_credentials = compute_engine.IDTokenCredentials(
            auth_request,
            "",
            service_account_email=credentials.service_account_email,
        )
        logging.info("StorageClient: Instantiated.")

    def upload(
        self,
        bucket_name: str,
        contents: str,
        mime_type: str,
        file_name: str,
        sub_dir: str = "",
    ) -> str:
        """Stores contents on GCS.

        Args:
            bucket: A GCS bucket.
            contents: base64 encoded bytes.
            mime_type: The mime type of the contents.
            file_name: The name for the file to be generated.
            sub_dir: The subdirectory to store the file in.

        Returns:
            The GCS uri of the stored image.
        """
        try:
            bucket = self._client.bucket(bucket_name)
            destination_blob_name = os.path.join(sub_dir, file_name)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_string(
                base64.b64decode(contents),
                content_type=mime_type,
            )
            uri = f"gs://{bucket_name}/{destination_blob_name}"
            logging.info("StorageClient: Uploaded image to %s.", uri)
            return uri
        except Exception as ex:
            raise StorageClientError(
                f"StorageClient: Could not upload file {ex}",
            ) from ex

    def download_as_string(self, gcs_uri: str) -> tuple[str, str, str]:
        """Downloads a file as string.

        Args:
            gcs_uri: The GCS URI of the blob (e.g., gs://bucket-name/path/to/file.txt).

        Returns:
            The b64 encodeded string and it's mimetype and file name.
        """
        try:
            parsed_uri = urlparse(gcs_uri)
        except Exception as e:
            raise StorageClientError("Invalid URI: %s. Error: %s", gcs_uri, e) from e

        if parsed_uri.scheme != "gs":
            raise StorageClientError(
                "Invalid GCS URI: %s. Must start with 'gs://'",
                gcs_uri,
            )

        bucket_name = parsed_uri.netloc
        blob_name = parsed_uri.path.lstrip("/")  # Remove leading slash
        mimetype = mimetypes.guess_type(gcs_uri)[0]
        file_name = os.path.basename(gcs_uri)
        try:
            parsed_uri = urlparse(gcs_uri)
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            content = blob.download_as_bytes()
            return (base64.b64encode(content).decode("utf-8"), mimetype, file_name)
        except Exception as ex:
            raise StorageClientError(
                f"StorageClient: Could not download file {ex}",
            ) from ex

    def get_signed_download_url_from_gcs_uri(self, gcs_uri: str) -> str:
        """Retrieves a GCS blob from a gs:// URI.

        Args:
            gcs_uri: The GCS URI of the blob (e.g., gs://bucket-name/path/to/file.txt).

        Returns:
            A google.cloud.storage.blob.Blob object, or None if the blob is not found.
        Raises:
            StorageClientError: If the URI is invalid or not a GCS URI.
            StorageClientError: If the client could not generate a signed url.
        """

        try:
            parsed_uri = urlparse(gcs_uri)
        except Exception as e:
            raise StorageClientError("Invalid URI: %s. Error: %s", gcs_uri, e) from e

        if parsed_uri.scheme != "gs":
            raise StorageClientError(
                "Invalid GCS URI: %s. Must start with 'gs://'",
                gcs_uri,
            )
        bucket_name = parsed_uri.netloc
        blob_name = parsed_uri.path.lstrip("/")  # Remove leading slash
        try:
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            return blob.generate_signed_url(
                expiration=_DEFAULT_URL_EXPIRATION_SECONDS,
                credentials=self._signing_credentials,
                version="v4",
            )
        except exceptions.ClientError as ce:
            logging.error(
                "Could not generate signed url from uri %s",
                gcs_uri,
            )
            raise StorageClientError(
                "Could not generated signed url. Error: %s",
                ce,
            ) from ce

    def get_storage_object_metadata(self, file_uri: str) -> tuple[str, str, str]:
        """Gets the bucket name, file name and extension from a file URI."""
        image_uri_parts = file_uri.split("/")
        bucket_name = image_uri_parts[2]
        base_name = os.path.basename(file_uri)
        file_name, extension = os.path.splitext(base_name)
        return bucket_name, file_name, extension
