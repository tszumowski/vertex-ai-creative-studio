"""Tests for the AIPlatformClient."""

import base64
import dataclasses
import os
import unittest
from unittest import mock

from google.cloud import aiplatform

from common.clients import (
    aiplatform_client_lib,
    storage_client_lib,
    vertexai_client_lib,
)


class FakePredictResponse:
    def __init__(self) -> None:
        self.predictions = [
            {
                "mimeType": "image/jpg",
                "bytesBase64Encoded": "encoded_value",
                "labels": [{"label": "fake_label", "score": 1}],
            },
        ]


class AIPlatformClientTest(unittest.TestCase):
    """Test class for the AIPlatformClient."""

    def setUp(self) -> None:
        """Sets up the test environment."""
        super().setUp()
        self.enterContext(
            mock.patch.dict(os.environ, {"PROJECT_ID": "test-project"}),
        )
        self.enterContext(
            mock.patch.dict(os.environ, {"REGION": "test-region"}),
        )
        self.enterContext(
            mock.patch.dict(os.environ, {"IMAGE_CREATION_BUCKET": "test-bucket"}),
        )

        self.enterContext(mock.patch.object(aiplatform, "init", autospec=True))
        self.enterContext(
            mock.patch.object(
                base64,
                "b64decode",
                autospec=True,
            ),
        )
        self.enterContext(
            mock.patch.object(
                base64,
                "b64encode",
                autospec=True,
            )
        )
        self.mock_storage_client = self.enterClassContext(
            mock.patch.object(storage_client_lib, "StorageClient"),
        )
        self.mock_storage_client.return_value.download_as_string.return_value = (
            "fake_image_strin"
        )
        self.mock_vertexai_client = self.enterClassContext(
            mock.patch.object(vertexai_client_lib, "VertexAIClient"),
        )
        self.mock_vertexai_client.return_value.generate_description_from_image.return_value = "Fake description"  # noqa: E501
        self.mock_ai_platform_client = self.enterClassContext(
            mock.patch.object(aiplatform.gapic, "PredictionServiceClient"),
        )
        self.mock_ai_platform_client.return_value.predict.return_value = (
            FakePredictResponse()
        )


if __name__ == "__main__":
    unittest.main()
