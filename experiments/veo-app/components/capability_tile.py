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
"""Welcome page"""

from typing import Optional

import mesop as me


def on_tile_click(e: me.ClickEvent):
    """Handles clicks on any tile, internal or external."""
    if e.key.startswith("http"):
        me.navigate(e.key, new_tab=True)
    else:
        me.navigate(e.key)


@me.component
def media_tile(label: str, icon: str, route: Optional[str], external_url: Optional[str] = None):
    """Media component that can handle internal routes and external URLs."""
    
    is_clickable = bool(route) or bool(external_url)
    nav_key = route or external_url

    box_style = me.Style(
        display="flex",
        flex_direction="column",
        gap=5,
        align_items="center",
        border=me.Border().all(
            me.BorderSide(style="solid", color=me.theme_var("tertiary-fixed-variant"))
        ),
        border_radius=12,
        height=160,
        width=160,
        justify_content="center",
        background=me.theme_var("secondary-container"),
        position="relative",
    )

    if is_clickable:
        box_style.cursor = "pointer"
    else:
        box_style.opacity = 0.6
        box_style.cursor = "default"

    with me.box(
        style=box_style,
        key=nav_key if is_clickable else f"tile_{label}_{icon}",
        on_click=on_tile_click if is_clickable else None,
    ):
        # This inner box is for the main content (icon and text)
        with me.box(
            style=me.Style(
                display="flex",
                flex_direction="column",
                align_items="center",
                font_size="18px",
                gap=5,
            )
        ):
            me.icon(
                icon,
                style=me.Style(
                    font_size="38pt",
                    width="50px",
                    height="60px",
                    color=me.theme_var("on-surface"),
                ),
            )
            me.text(label, style=me.Style(font_weight="medium", text_align="center"))

        # "Open in new" icon is placed in a separate box for absolute positioning
        if external_url:
            with me.box(
                style=me.Style(
                    position="absolute",
                    top=8,
                    right=8,
                ),
            ):
                me.icon("open_in_new", style=me.Style(font_size="18px", color=me.theme_var("on-surface-variant")))
