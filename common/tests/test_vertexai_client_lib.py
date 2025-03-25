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

"""Tests for the VertexAIClient."""

import os
import unittest
from unittest import mock

import vertexai
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

from common.clients import storage_client_lib, vertexai_client_lib


class VertexAIClientTest(unittest.TestCase):
    """Test class for the VertexAIClient."""

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

        self.enterContext(mock.patch.object(vertexai, "init", autospec=True))
        self.mock_image_generation_model = self.enterClassContext(
            mock.patch.object(ImageGenerationModel, "from_pretrained"),
        )
        self.mock_storage_client = self.enterClassContext(
            mock.patch.object(storage_client_lib, "StorageClient"),
        )
        self.mock_image = mock.MagicMock()
        self.mock_image._as_base64_string.return_value = b"mock_image_data"
        self.mock_image._gcs_uri = "gs://test-bucket/path/to/image.jpg"

    def test_generate_images_success(self) -> None:
        """Tests generating images successfully."""
        self.mock_image_generation_model.return_value.generate_images.return_value = (
            mock.MagicMock(images=[self.mock_image])
        )
        imagen_client = vertexai_client_lib.VertexAIClient()

        generated_images_uris = imagen_client.generate_images(
            model="imagen-base",
            prompt="test prompt",
            add_watermark=False,
            aspect_ratio="1:1",
            num_images=1,
            language="en",
            negative_prompt=None,
        )

        self.assertEqual(generated_images_uris, ["gs://test-bucket/path/to/image.jpg"])

    def test_generate_images_failure(self) -> None:
        """Tests handling failures when generating images."""
        self.mock_image_generation_model.return_value.generate_images.side_effect = (
            Exception("Test exception")
        )
        imagen_client = vertexai_client_lib.VertexAIClient()

        with self.assertRaisesRegex(
            vertexai_client_lib.VertexAIClientError,
            "VertexAIClient: Could not generate images Test exception",
        ):
            imagen_client.generate_images(
                model="imagen-base",
                prompt="test prompt",
                add_watermark=False,
                aspect_ratio="1:1",
                num_images=1,
                language="en",
                negative_prompt=None,
            )


if __name__ == "__main__":
    unittest.main()
