"""Tests for the ImagenClient."""

import os
import unittest
from unittest import mock

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

from common import imagen_client_lib


class ImagenClientTest(unittest.TestCase):
    """Test class for the ImagenClient."""

    def setUp(self) -> None:
        """Sets up the test environment."""
        super().setUp()
        os.environ["GCP_PROJECT_ID"] = "test-project"
        os.environ["GCP_REGION"] = "test-region"
        os.environ["IMAGE_CREATION_BUCKET"] = "test-bucket"

        self.enterContext(mock.patch.object(vertexai, "init", autospec=True))
        self.mock_image_generation_model = self.enterClassContext(
            mock.patch.object(ImageGenerationModel, "from_pretrained"),
        )

        self.mock_image = mock.MagicMock()
        self.mock_image._as_base64_string.return_value = b"mock_image_data"
        self.mock_image._gcs_uri = "gs://test-bucket/path/to/image.jpg"

    def test_generate_images_success(self) -> None:
        """Tests generating images successfully."""
        self.mock_image_generation_model.return_value.generate_images.return_value = (
            mock.MagicMock(images=[self.mock_image])
        )
        imagen_client = imagen_client_lib.ImagenClient(model="imagen-base")

        generated_images_uris = imagen_client.generate_images(
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
        imagen_client = imagen_client_lib.ImagenClient(model="imagen-base")

        with self.assertRaisesRegex(
            imagen_client_lib.ImageClientError,
            "ImagenClient: Could not generate images Test exception",
        ):
            imagen_client.generate_images(
                prompt="test prompt",
                add_watermark=False,
                aspect_ratio="1:1",
                num_images=1,
                language="en",
                negative_prompt=None,
            )


if __name__ == "__main__":
    unittest.main()
