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

from __future__ import annotations

from typing import Any, Callable

import mesop.labs as mel


@mel.web_component(
    path="./image_masker_component.js",
)  # Path to your image_masker_component.js file
def image_masker_component(
    *,
    img_src: str,
    on_mask_change: Callable[[mel.WebEvent], Any]
    | None = None,  # Callback for mask changes
    key: str | None = None,
):
    """
    A Mesop component for an image masker.

    Args:
        img_src: The URL of the image.
        on_mask_change: A callback function that will be called when the mask is changed.
                            The event detail will contain the mask data URL.
        key: A unique key for the component.
    """

    events = {}
    if on_mask_change:
        events["maskChangeEvent"] = on_mask_change

    return mel.insert_web_component(
        name="image-masker-component",  # Must match the custom element name
        key=key,
        properties={
            "img_src": img_src,
        },
        events=events,
    )
