import unittest
from unittest.mock import MagicMock, patch

from google.cloud.firestore import DocumentReference

from common.metadata import MediaItem, get_media_item_by_id
from models.veo import generate_video
from state.veo_state import PageState


class TestVeoExtendFlow(unittest.TestCase):
    @patch("models.veo.client")
    @patch("common.metadata.db")
    def test_extend_video_flow(self, mock_db, mock_client):
        # 1. Setup initial state and mock objects
        state = PageState()
        state.veo_prompt_input = "A cat playing a piano"
        state.video_length = 5
        state.aspect_ratio = "16:9"
        state.veo_model = "2.0"

        # Mock the API response for the initial video generation
        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.error = None
        mock_operation.result.generated_videos = [MagicMock()]
        mock_operation.result.generated_videos[0].video.uri = "gs://bucket/initial_video.mp4"
        mock_client.models.generate_videos.return_value = mock_operation
        mock_client.operations.get.return_value = mock_operation

        # Mock Firestore
        mock_doc_ref = MagicMock(spec=DocumentReference)
        mock_doc_ref.id = "initial_video_doc_id"
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        # 2. Generate the initial video
        initial_video_uri = generate_video(state)

        # 3. Simulate saving to Firestore and updating state
        initial_item = MediaItem(
            gcsuri=initial_video_uri, prompt=state.veo_prompt_input
        )
        # In a real scenario, add_media_item_to_firestore would be called here
        initial_item.id = mock_doc_ref.id
        state.result_video = initial_video_uri
        state.result_video_firestore_id = initial_item.id

        # 4. Setup for the extend call
        state.veo_prompt_input = "The cat starts singing"
        state.video_extend_length = 4

        # Mock the API response for the extended video generation
        mock_extend_operation = MagicMock()
        mock_extend_operation.done = True
        mock_extend_operation.error = None
        mock_extend_operation.result.generated_videos = [MagicMock()]
        mock_extend_operation.result.generated_videos[0].video.uri = "gs://bucket/extended_video.mp4"
        mock_client.models.generate_videos.return_value = mock_extend_operation

        # Mock Firestore for the extended video
        mock_extend_doc_ref = MagicMock(spec=DocumentReference)
        mock_extend_doc_ref.id = "extended_video_doc_id"
        mock_db.collection.return_value.document.return_value = mock_extend_doc_ref

        # 5. Generate the extended video
        extended_video_uri = generate_video(state, extend_video_uri=state.result_video)

        # 6. Simulate saving the extended video metadata
        extended_item = MediaItem(
            gcsuri=extended_video_uri,
            prompt=state.veo_prompt_input,
            original_video_id=state.result_video_firestore_id,
            original_video_gcsuri=state.result_video,
        )
        extended_item.id = mock_extend_doc_ref.id

        # 7. Assertions
        self.assertEqual(extended_video_uri, "gs://bucket/extended_video.mp4")
        self.assertEqual(extended_item.original_video_id, "initial_video_doc_id")
        self.assertEqual(extended_item.original_video_gcsuri, "gs://bucket/initial_video.mp4")


if __name__ == "__main__":
    unittest.main()
