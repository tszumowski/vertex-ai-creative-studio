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
"""Interpolation"""
import mesop as me

from components.header import header
from components.page_scaffold import (
    page_scaffold,
    page_frame,
)

from common.metadata import get_latest_videos

@me.stateclass
class PageState:
    """Local Page State"""

    is_loading: bool = False

    music_prompt_input: str = ""
    music_prompt_placeholder: str = ""
    music_prompt_textarea_key: int = 0
    music_upload_uri: str = ""


def library_content(app_state: me.state):
    """Library Mesop Page"""

    pagestate = me.state(PageState)

    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():  # pylint: disable=not-context-manager
            header("Library", "perm_media")

            media = get_latest_videos()

            with me.box(
                style=me.Style(
                    display="flex",
                    flex_direction="column",
                    align_items="center",
                    width="90hv",
                )
            ):
                for m in media:
                    aspect = m.get("aspect")
                    gcsuri = m.get("gcsuri")
                    video_url = gcsuri.replace(
                        "gs://",
                        "https://storage.mtls.cloud.google.com/",
                    )
                    prompt = m.get("prompt")
                    generation_time = m.get("generation_time")
                    timestamp = m.get("timestamp").strftime("%Y-%m-%d %H:%M")
                    with me.box(
                        style=me.Style(
                            padding=me.Padding.all(10),
                            display="flex",
                            flex_direction="column",
                            #align_items="center",
                            width="50%",
                            gap=10,
                        )
                    ):
                        me.text(f"Generated Video: {timestamp}", style=me.Style(font_weight="bold"))
                        me.text(f"Aspect ratio: {aspect}")
                        me.text(f"\"{prompt}\"")
                        me.html(f"<a href='{video_url}' target='_blank'>video</a>")
                        me.text(f"Generated in {round(generation_time)} seconds.")





_BOX_STYLE = me.Style(
    flex_basis="max(480px, calc(50% - 48px))",
    # background="#fff",
    background=me.theme_var("background"),
    border_radius=12,
    box_shadow=("0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"),
    padding=me.Padding(top=16, left=16, right=16, bottom=16),
    display="flex",
    flex_direction="column",
)
