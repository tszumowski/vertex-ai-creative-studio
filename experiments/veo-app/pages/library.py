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

from common.metadata import get_latest_videos
from components.header import header
from components.page_scaffold import (
    page_frame,
    page_scaffold,
)


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
                    reference_image = m.get("reference_image")
                    auto_enhanced_prompt = m.get("enhanced_prompt")
                    duration = m.get("duration")
                    error_message = m.get("error_message")
                    if duration:
                        video_length = f"{duration} sec"
                    else:
                        video_length = "Unknown"
                    with me.box(
                        style=me.Style(
                            padding=me.Padding.all(10),
                            display="flex",
                            flex_direction="column",
                            # align_items="center",
                            width="50%",
                            gap=10,
                        )
                    ):
                        me.text(
                            f"Generated Video: {timestamp}",
                            style=me.Style(font_weight="bold"),
                        )

                        with me.box(
                            style=me.Style(
                                display="flex",
                                flex_direction="row",
                                gap=3,
                            )
                        ):
                            if reference_image:
                                pill("i2v", "gen")
                            else:
                                pill("t2v", "gen")
                            pill(aspect, "aspect")
                            pill(video_length, "duration")
                            pill("24 fps", "fps")
                            if auto_enhanced_prompt:
                                me.icon("auto_fix_normal")

                        me.text(f'"{prompt}"')
                        with me.box(
                            style=me.Style(gap=3, display="flex", flex_basis="row")
                        ):
                            if error_message:
                                me.text(
                                    f"Error: {error_message}",
                                    style=me.Style(
                                        width=300,
                                        font_style="italic",
                                        font_size="10pt",
                                        margin=me.Margin.all(3),
                                        padding=me.Padding.all(6),
                                        border=me.Border.all(
                                            me.BorderSide(
                                                style="solid",
                                                width=1,
                                                color=me.theme_var("error")
                                            )
                                        ),
                                        border_radius=5,
                                    ),
                                )
                            else:
                                me.video(
                                    src=video_url,
                                    style=me.Style(height=150, border_radius=6),
                                )
                            if reference_image:
                                reference_image = reference_image.replace(
                                    "gs://",
                                    "https://storage.mtls.cloud.google.com/",
                                )
                                me.image(
                                    src=reference_image,
                                    style=me.Style(height=75, border_radius=6),
                                )
                        # me.html(f"<a href='{video_url}' target='_blank'>video</a>")

                        me.text(f"Generated in {round(generation_time)} seconds.")
                        me.divider()


@me.component
def pill(label: str, pill_type: str):
    """Pill display"""

    background = me.theme_var("on-secondary-fixed-variant")
    match pill_type:
        case "aspect":
            background = me.theme_var("on-secondary-fixed-variant")
        case "gen":
            if pill_type == "i2v":
                background = me.theme_var("on-primary-fixed")
            else:
                background = me.theme_var("on-primary-fixed-variant")

    me.text(
        label,
        style=me.Style(
            background=background,
            color="white",
            border_radius="5px",
            text_align="center",
            font_size="8pt",
            font_weight="bold",
            display="inline-flex",
            padding=me.Padding.all(5),
        ),
    )


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
