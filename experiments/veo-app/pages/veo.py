# Copyright 2024 Google LLC
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

import time

import mesop as me
import requests

from common.metadata import add_video_metadata
from components.header import header
from components.page_scaffold import (
    page_frame,
    page_scaffold,
)
from config.default import Default
from models.model_setup import VeoModelSetup
from models.veo import text_to_video, image_to_video
from common.storage import store_to_gcs
from pages.styles import _BOX_STYLE_CENTER_DISTRIBUTED


config = Default()

veo_model = VeoModelSetup.init()


@me.stateclass
class PageState:
    """Mesop Page State"""

    veo_prompt_input: str = ""
    veo_prompt_placeholder: str = ""
    veo_prompt_textarea_key: int = 0

    is_loading: bool = False

    prompt: str
    original_prompt: str

    aspect_ratio: str = "16:9"
    video_length: int = 5

    # I2V reference Image
    reference_image_file: me.UploadedFile = None
    reference_image_file_key: int = 0
    reference_image_gcs: str
    reference_image_uri: str

    rewriter_name: str

    result_video: str

    timing: str


def veo_content(app_state: me.state):
    """Veo Mesop Page"""
    state = me.state(PageState)

    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():  # pylint: disable=not-context-manager
            header("Veo", "movie")

            # tricolumn
            with me.box(
                style=me.Style(
                    display="flex",
                    flex_direction="row",
                    gap=10,
                    height=250,
                )
            ):
                # Controls
                with me.box(
                    style=me.Style(
                        # flex_basis="450px",
                        flex_basis="max(480px, calc(60% - 48px))",
                        display="flex",
                        flex_direction="column",
                        align_items="stretch",
                        justify_content="space-between",
                        gap=10,
                    )
                ):
                    subtle_veo_input()
                    # me.box(style=me.Style(height=12))
                    # me.text("no video generated")

                    with me.box(
                        style=me.Style(display="flex", flex_basis="row", gap=5)
                    ):
                        me.select(
                            label="aspect",
                            appearance="outline",
                            options=[
                                me.SelectOption(label="16:9 widescreen", value="16:9"),
                                me.SelectOption(label="9:16 portrait", value="9:16"),
                            ],
                            value=state.aspect_ratio,
                            on_selection_change=on_selection_change_aspect,
                        )
                        me.select(
                            label="length",
                            options=[
                                me.SelectOption(label="5 seconds", value="5"),
                                me.SelectOption(label="6 seconds", value="6"),
                                me.SelectOption(label="7 seconds", value="7"),
                                me.SelectOption(label="8 seconds", value="8"),
                            ],
                            appearance="outline",
                            style=me.Style(),
                            value=f"{state.video_length}",
                            on_selection_change=on_selection_change_length,
                        )

                # Uploaded image
                with me.box(style=_BOX_STYLE_CENTER_DISTRIBUTED):
                    me.text("Reference Image (optional)")

                    if state.reference_image_uri:
                        output_url = state.reference_image_uri
                        # output_url = f"https://storage.mtls.cloud.google.com/{state.reference_image_uri}"
                        # output_url = "https://storage.mtls.cloud.google.com/ghchinoy-genai-sa-assets-flat/edits/image (30).png"
                        print(f"displaying {output_url}")
                        me.image(
                            src=output_url,
                            style=me.Style(
                                height=150,
                                border_radius=12,
                            ),
                            key=str(state.reference_image_file_key),
                        )
                    else:
                        me.image(src=None, style=me.Style(height=200))

                    with me.box(
                        style=me.Style(display="flex", flex_direction="row", gap=5)
                    ):
                        # me.button(label="Upload", type="flat", disabled=True)
                        me.uploader(
                            label="Upload",
                            accepted_file_types=["image/jpeg", "image/png"],
                            on_upload=on_click_upload,
                            type="flat",
                            color="primary",
                            style=me.Style(font_weight="bold"),
                        )
                        me.button(
                            label="Clear", on_click=on_click_clear_reference_image
                        )

            me.box(style=me.Style(height=30))

            # Generated video
            with me.box(style=_BOX_STYLE_CENTER_DISTRIBUTED):
                me.text("Generated Video")
                me.box(style=me.Style(height=8))
                with me.box(style=me.Style(height="100%")):
                    if state.is_loading:
                        me.progress_spinner()
                    elif state.result_video:
                        video_url = state.result_video.replace(
                            "gs://",
                            "https://storage.mtls.cloud.google.com/",
                        )
                        print(f"video_url: {video_url}")
                        me.video(src=video_url)
                        me.text(state.timing)


def on_click_upload(e: me.UploadEvent):
    """Upload image to GCS"""
    state = me.state(PageState)
    state.reference_image_file = e.file
    contents = e.file.getvalue()
    destination_blob_name = store_to_gcs(
        "uploads", e.file.name, e.file.mime_type, contents
    )
    # gcs
    state.reference_image_gcs = f"gs://{destination_blob_name}"
    # url
    state.reference_image_uri = (
        f"https://storage.mtls.cloud.google.com/{destination_blob_name}"
    )
    # log
    print(
        f"{destination_blob_name} with contents len {len(contents)} of type {e.file.mime_type} uploaded to {config.GENMEDIA_BUCKET}."
    )


def on_click_clear_reference_image(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Clear reference image"""
    state = me.state(PageState)
    state.reference_image_file = None
    state.reference_image_file_key += 1
    state.reference_image_uri = None
    state.reference_image_gcs = None
    state.is_loading = False


def on_selection_change_length(e: me.SelectSelectionChangeEvent):
    """Adjust the video duration length in seconds based on user event"""
    state = me.state(PageState)
    state.video_length = int(e.value)


def on_selection_change_aspect(e: me.SelectSelectionChangeEvent):
    """Adjust aspect ratio based on user event."""
    state = me.state(PageState)
    state.aspect_ratio = e.value


def on_click_clear(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Clear prompt and video"""
    state = me.state(PageState)
    state.result_video = None
    state.prompt = None
    state.original_prompt = None
    state.video_length = 5
    state.aspect_ratio = "16:9"
    state.is_loading = False
    yield


def on_click_veo(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Veo generate request handler"""
    state = me.state(PageState)
    state.is_loading = True
    yield

    print(f"Lights, camera, action!:\n{state.veo_prompt_input}")

    aspect_ratio = state.aspect_ratio  # @param ["16:9", "9:16"]
    seed = 120
    sample_count = 1
    rewrite_prompt = False
    duration_seconds = state.video_length

    start_time = time.time()  # Record the starting time

    try:
        if state.reference_image_gcs:
            print(f"I2V invoked. I see you have an image! {state.reference_image_gcs} ")
            op = image_to_video(
                state.veo_prompt_input,
                state.reference_image_gcs,
                seed,
                aspect_ratio,
                sample_count,
                f"gs://{config.VIDEO_BUCKET}",
                rewrite_prompt,
                duration_seconds,
            )
        else:
            print("T2V invoked.")
            op = text_to_video(
                state.veo_prompt_input,
                seed,
                aspect_ratio,
                sample_count,
                f"gs://{config.VIDEO_BUCKET}",
                rewrite_prompt,
                duration_seconds,
            )
        print(f"Ok {op}")
        gcs_uri = ""
        if op["response"]:
            print(f"Response: {op['response']}")
            print_keys(op["response"])
            if (
                "generatedSamples" in op["response"]
                and op["response"]["generatedSamples"]
            ):
                # if op["response"]["generatedSamples"]:
                print(f"Generated Samples: {op['response']['generatedSamples']}")
                for video in op["response"]["generatedSamples"]:
                    # veo-2.0-generate-exp
                    gcs_uri = video["video"]["uri"]
                    # file_name = gcs_uri.split("/")[-1]
                    # print("Video generated - use the following to copy locally")
                    # print(f"gsutil cp {gcs_uri} {file_name}")
                    # state.result_video = gcs_uri
            elif "videos" in op["response"] and op["response"]["videos"]:
                # elif op["response"]["videos"]:
                # veo-2.0-generate-001
                videos = op["response"]["videos"]
                print(f"Videos: {len(videos)}")
                for video in videos:
                    print(f"> {video}")
                    gcs_uri = video["gcsUri"]
            else:
                print(f"something else has happened: {op['response']}")
            file_name = gcs_uri.split("/")[-1]
            print("Video generated - use the following to copy locally")
            print(f"gsutil cp {gcs_uri} {file_name}")
            state.result_video = gcs_uri
    except ValueError as err:
        print(f"error {err}")
    except requests.exceptions.HTTPError as err:
        print(f"error {err}")
    except Exception as err:
        print(f"error {err}")

    end_time = time.time()  # Record the ending time
    execution_time = end_time - start_time  # Calculate the elapsed time
    print(f"Execution time: {execution_time} seconds")  # Print the execution time
    state.timing = f"Generation time: {round(execution_time)} seconds"

    add_video_metadata(
        gcs_uri,
        state.veo_prompt_input,
        aspect_ratio,
        veo_model,
        execution_time,
        state.video_length,
        state.reference_image_gcs,
    )

    state.is_loading = False
    yield
    print("Cut! That's a wrap!")


def on_blur_veo_prompt(e: me.InputBlurEvent):
    """Veo prompt blur event"""
    me.state(PageState).veo_prompt_input = e.value


@me.component
def subtle_veo_input():
    """veo input"""

    pagestate = me.state(PageState)

    icon_style = me.Style(
        display="flex",
        flex_direction="column",
        gap=3,
        font_size=10,
        align_items="center",
    )
    with me.box(
        style=me.Style(
            border_radius=16,
            padding=me.Padding.all(8),
            background=me.theme_var("secondary-container"),
            display="flex",
            width="100%",
        )
    ):
        with me.box(
            style=me.Style(
                flex_grow=1,
            )
        ):
            me.native_textarea(
                autosize=True,
                min_rows=10,
                max_rows=13,
                placeholder="video creation instructions",
                style=me.Style(
                    padding=me.Padding(top=16, left=16),
                    background=me.theme_var("secondary-container"),
                    outline="none",
                    width="100%",
                    overflow_y="auto",
                    border=me.Border.all(
                        me.BorderSide(style="none"),
                    ),
                    color=me.theme_var("foreground"),
                    flex_grow=1,
                ),
                on_blur=on_blur_veo_prompt,
                key=str(pagestate.veo_prompt_textarea_key),
                value=pagestate.veo_prompt_placeholder,
            )
        with me.box(
            style=me.Style(
                display="flex",
                flex_direction="column",
                gap=15,
            )
        ):
            # do the veo
            with me.content_button(
                type="icon",
                on_click=on_click_veo,
            ):
                with me.box(style=icon_style):
                    me.icon("play_arrow")
                    me.text("Create")
            # invoke gemini
            with me.content_button(
                type="icon",
                disabled=True,
            ):
                with me.box(style=icon_style):
                    me.icon("auto_awesome")
                    me.text("Rewriter")
            # clear all of this
            with me.content_button(
                type="icon",
                on_click=on_click_clear,
            ):
                with me.box(style=icon_style):
                    me.icon("clear")
                    me.text("Clear")


def print_keys(obj, prefix=""):
    """Recursively prints keys of a JSON object."""
    if isinstance(obj, dict):
        for key in obj:
            print(prefix + key)
            print_keys(obj[key], prefix + "  ")  # Recurse with increased indentation
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            print_keys(item, prefix + f"  [{i}] ")  # indicate list index in prefix
