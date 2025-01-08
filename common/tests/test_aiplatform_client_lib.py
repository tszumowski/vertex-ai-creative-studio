"""Tests for the AIPlatformClient."""

import os
import unittest
from unittest import mock

from google.cloud import aiplatform

from common import aiplatform_client_lib, storage_client_lib, vertexai_client_lib


class AIPlatformClientTest(unittest.TestCase):
    """Test class for the AIPlatformClient."""

    def setUp(self) -> None:
        """Sets up the test environment."""
        super().setUp()
        self.enterContext(
            mock.patch.dict(os.environ, {"GCP_PROJECT_NAME": "test-project"}),
        )
        self.enterContext(
            mock.patch.dict(os.environ, {"GCP_REGION": "test-region"}),
        )
        self.enterContext(
            mock.patch.dict(os.environ, {"IMAGE_CREATION_BUCKET": "test-bucket"}),
        )

        self.enterContext(mock.patch.object(aiplatform, "init", autospec=True))

        self.mock_storage_client = self.enterClassContext(
            mock.patch.object(storage_client_lib, "StorageClient")
        )
        self.mock_vertexai_client = self.enterClassContext(
            mock.patch.object(vertexai_client_lib, "VertexAIClient")
        )
        self.mock_vertexai_client.return_value.generate_description_from_image.return_value = "Fake description"  # noqa: E501
        self.mock_ai_platform_client = self.enterClassContext(
            mock.patch.object(aiplatform.gapic, "PredictionServiceClient"),
        )

    def test_edit_image(self) -> None:
        client = aiplatform_client_lib.AIPlatformClient()
        client.edit_image(
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
        self.mock_storage_client.return_value.download_as_string.assert_called_once_with(
            bucket_name="fake",
            file_name="path/to/image.jpg",
        )
        self.mock_ai_platform_client.return_value.predict.assert_has_calls(
            [
                mock.call(
                    endpoint="projects/test-project/locations/test-region/publishers/google/models/image-segmentation-001",
                    instances=[
                        {
                            "image": {"gcsUri": "gs://fake/path/to/image.jpg"},
                            "prompt": "Fake description",
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
