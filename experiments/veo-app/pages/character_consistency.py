# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import field

import mesop as me

from common.metadata import get_media_item_by_id
from common.storage import store_to_gcs
from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from models.character_consistency import generate_character_video
from state.character_consistency_state import CharacterConsistencyState
from state.state import AppState


@me.stateclass
class PageState:
    """Character Consistency Page State"""

    uploaded_image_gcs_uris: list[str] = field(default_factory=list)  # pylint: disable=invalid-field-call
    scene_prompt: str = ""
    candidate_image_urls: list[str] = field(default_factory=list)  # pylint: disable=invalid-field-call
    best_image_url: str = ""
    outpainted_image_url: str = ""
    final_video_url: str = ""
    status_message: str = "Ready."
    is_generating: bool = False


def character_consistency_page_content():
    """UI for the Character Consistency page."""
    state = me.state(PageState)

    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():  # pylint: disable=not-context-manager
            header("Character Consistency", "person")

            with me.box(style=me.Style(margin=me.Margin.symmetric(vertical=20))):
                me.uploader(
                    label="Upload Reference Images",
                    on_upload=on_upload,
                    multiple=True,
                    style=me.Style(width="100%"),
                )

            if state.uploaded_image_gcs_uris:
                with me.box(style=me.Style(display="flex", flex_wrap="wrap", gap=10, justify_content="center")):
                    for uri in state.uploaded_image_gcs_uris:
                        me.image(
                            src=uri.replace(
                                "gs://", "https://storage.mtls.cloud.google.com/"
                            ),
                            style=me.Style(width=200, height=200, object_fit="contain", border_radius="12px",
                                box_shadow="0 2px 4px rgba(0,0,0,0.1)",),
                        )

            me.textarea(
                label="Scene Prompt",
                rows=3,
                on_input=on_prompt_input,
                style=me.Style(width="100%"),
            )

            me.button(
                "Generate",
                on_click=on_generate_click,
                disabled=state.is_generating,
                style=me.Style(margin=me.Margin.symmetric(vertical=20)),
            )

            me.text(
                state.status_message,
                style=me.Style(margin=me.Margin.symmetric(vertical=10)),
            )

            if state.candidate_image_urls:
                me.text("Candidate Images", type="headline-5")
                with me.box(
                    style=me.Style(
                        display="flex",
                        flex_wrap="wrap",
                        gap=10,
                        justify_content="center",
                    )
                ):
                    for url in state.candidate_image_urls:
                        me.image(
                            src=url,
                            style=me.Style(
                                width=200,
                                height=200,
                                border_radius="12px",
                                box_shadow="0 2px 4px rgba(0,0,0,0.1)",
                            ),
                        )

            if state.best_image_url:
                me.text("Best Image", type="headline-5")
                me.image(
                    src=state.best_image_url,
                    style=me.Style(width=400, height=400, object_fit="contain"),
                )

            if state.outpainted_image_url:
                me.text("Outpainted Image", type="headline-5")
                me.image(
                    src=state.outpainted_image_url,
                    style=me.Style(width=600, height=338, object_fit="contain"),
                )

            if state.final_video_url:
                me.text("Final Video", type="headline-5")
                me.video(
                    src=state.final_video_url, style=me.Style(width=600, height=338)
                )


def on_upload(e: me.UploadEvent):
    """Handle image uploads."""
    state = me.state(PageState)
    for file in e.files:
        gcs_url = store_to_gcs(
            "character_consistency_references",
            file.name,
            file.mime_type,
            file.getvalue(),
        )
        state.uploaded_image_gcs_uris.append(gcs_url)
    yield


def on_prompt_input(e: me.InputEvent):
    """Handle prompt input."""
    state = me.state(PageState)
    state.scene_prompt = e.value


def on_generate_click(e: me.ClickEvent):
    """Handle generate button click."""
    state = me.state(PageState)
    app_state = me.state(AppState)
    state.is_generating = True
    state.status_message = "Generating..."
    yield

    try:
        media_item_id = generate_character_video(
            user_email=app_state.user_email,
            reference_image_gcs_uris=state.uploaded_image_gcs_uris,
            scene_prompt=state.scene_prompt,
        )
        media_item = get_media_item_by_id(media_item_id)
        if media_item:
            state.candidate_image_urls = [
                f"https://storage.mtls.cloud.google.com/{gcs_uri.replace('gs://', '')}"
                for gcs_uri in media_item.candidate_images
            ]
            state.best_image_url = f"https://storage.mtls.cloud.google.com/{media_item.best_candidate_image.replace('gs://', '')}"
            state.outpainted_image_url = f"https://storage.mtls.cloud.google.com/{media_item.outpainted_image.replace('gs://', '')}"
            state.final_video_url = f"https://storage.mtls.cloud.google.com/{media_item.gcsuri.replace('gs://', '')}"
            state.status_message = "Successfully generated video!"
        else:
            state.status_message = (
                f"Error: Could not retrieve generated media with ID: {media_item_id}"
            )

    except Exception as e:
        state.status_message = f"Error: {e}"

    state.is_generating = False
    yield
