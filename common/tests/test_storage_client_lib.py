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

"""Tests for the StorageClient."""

import base64
import unittest
from unittest import mock

import google.auth
from google.cloud import storage

from common.clients import storage_client_lib

_FAKE_BUCKET_NAME = "fake_bucket_name"


class StorageClientTest(unittest.TestCase):
    """Test class for the StorageClient."""

    def setUp(self) -> None:
        super().setUp()
        self.mock_credentials = mock.create_autospec(
            google.auth.credentials.Credentials,
        )
        self.mock_credentials.service_account_email = "fake_service_account_email"
        self.mock_auth = self.enterContext(
            mock.patch.object(
                google.auth,
                "default",
                autospec=True,
                return_value=(self.mock_credentials, ""),
            ),
        )
        self.patcher = mock.patch.object(storage, "Client", autospec=True)
        self.storage_client_mock = self.patcher.start()
        self.mock_bucket = mock.create_autospec(storage.Bucket)
        self.mock_blob = mock.create_autospec(storage.Blob)
        self.mock_bucket.return_value = self.mock_blob
        self.mock_bucket.blob.return_value = self.mock_blob
        self.mock_bucket.name = _FAKE_BUCKET_NAME
        self.storage_client_mock.return_value.bucket.return_value = self.mock_bucket

    def tearDown(self) -> None:
        self.patcher.stop()
        super().tearDown()

    def test_upload_decode(self) -> None:
        storage_client_lib.StorageClient().upload(
            _FAKE_BUCKET_NAME,
            b"fakebyte",
            "fake_mime_type",
            "fake_file_name",
            "",
        )
        self.mock_blob.upload_from_string.assert_called_once_with(
            b"}\xa9\x1eo+^",
            "fake_mime_type",
        )

    def test_download_as_string(self) -> None:
        self.mock_blob.download_as_bytes.return_value = b"}\xa9\x1eo+^"
        storage_client_lib.StorageClient().download_as_string(
            _FAKE_BUCKET_NAME,
            "fake_file_path",
        )
        self.mock_blob.download_as_bytes.assert_has_calls([mock.call()])
