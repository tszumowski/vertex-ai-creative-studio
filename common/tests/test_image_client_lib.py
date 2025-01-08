"""Tests for the ImagenClient."""

import os
import unittest
from unittest import mock

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from google.cloud import aiplatform
from common import imagen_client_lib, storage_client_lib


class ImagenClientTest(unittest.TestCase):
    """Test class for the ImagenClient."""

    def setUp(self) -> None:
        """Sets up the test environment."""
        super().setUp()
        self.enterContext(
            mock.patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}),
        )
        self.enterContext(
            mock.patch.dict(os.environ, {"GCP_REGION": "test-region"}),
        )
        self.enterContext(
            mock.patch.dict(os.environ, {"IMAGE_CREATION_BUCKET": "test-bucket"}),
        )

        self.enterContext(mock.patch.object(vertexai, "init", autospec=True))
        self.mock_image_generation_model = self.enterClassContext(
            mock.patch.object(ImageGenerationModel, "from_pretrained"),
        )
        self.mock_storage_client = self.enterClassContext(
            mock.patch.object(storage_client_lib, "StorageClient")
        )
        self.mock_ai_platform_client = self.enterClassContext(
            mock.patch.object(aiplatform.gapic, "PredictionServiceClient"),
        )
        self.mock_image = mock.MagicMock()
        self.mock_image._as_base64_string.return_value = b"mock_image_data"
        self.mock_image._gcs_uri = "gs://test-bucket/path/to/image.jpg"

    def test_generate_images_success(self) -> None:
        """Tests generating images successfully."""
        self.mock_image_generation_model.return_value.generate_images.return_value = (
            mock.MagicMock(images=[self.mock_image])
        )
        imagen_client = imagen_client_lib.ImagenClient()

        generated_images_uris = imagen_client.generate_images(
            generation_model="imagen-base",
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
        imagen_client = imagen_client_lib.ImagenClient()

        with self.assertRaisesRegex(
            imagen_client_lib.ImageClientError,
            "ImagenClient: Could not generate images Test exception",
        ):
            imagen_client.generate_images(
                generation_model="imagen-base",
                prompt="test prompt",
                add_watermark=False,
                aspect_ratio="1:1",
                num_images=1,
                language="en",
                negative_prompt=None,
            )

    def test_edit_image(self) -> None:
        imagen_client = imagen_client_lib.ImagenClient()
        imagen_client.edit_image(
            image_uri="gs://fake/path/to/image.jpg",
            prompt="fake prompt",
        )
        self.mock_storage_client.return_value.upload.assert_called_once_with(
            bucket_name="fake",
            contents=mock.ANY,
            mime_type=mock.ANY,
            file_name="path/to/image-mask.jpg",
            decode=True,
        )
        self.mock_ai_platform_client.return_value.predict.assert_has_calls(
            [
                mock.call(
                    endpoint="projects/test-project/locations/test-region/publishers/google/models/image-segmentation-001",
                    instances=[
                        {
                            "image": {"gcsUri": "gs://fake/path/to/image.jpg"},
                            "prompt": "",
                        },
                    ],
                    parameters={"mode": "foreground"},
                ),
                mock.call(
                    endpoint="projects/test-project/locations/test-region/publishers/google/models/imagen-3.0-capability-preview-0930",
                    instances=[
                        {
                            "referenceImages": [
                                {
                                    "referenceType": "REFERENCE_TYPE_RAW",
                                    "referenceId": 1,
                                    "referenceImage": {"bytesBase64Encoded": mock.ANY},
                                },
                                {
                                    "referenceType": "REFERENCE_TYPE_MASK",
                                    "referenceId": 1,
                                    "referenceImage": {"bytesBase64Encoded": mock.ANY},
                                    "maskImageConfig": {
                                        "maskMode": "MASK_MODE_USER_PROVIDED",
                                        "dilation": 0.01,
                                    },
                                },
                            ],
                            "prompt": "fake prompt",
                        },
                    ],
                    parameters={
                        "sampleCount": 1,
                        "editMode": "",
                        "aspectRatio": "1:1",
                        "output_gcs_uri": "gs://fake/path/to/image-edited.jpg",
                    },
                ),
            ],
            any_order=True,
        )


if __name__ == "__main__":
    unittest.main()
