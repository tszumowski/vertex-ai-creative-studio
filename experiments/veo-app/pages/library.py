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
"""Library"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict

import mesop as me

# Imports from your project structure
# Assuming MediaItem class is also defined in common.metadata for get_media_item_by_id
from common.metadata import (
    get_total_media_count,
    db,
    config,
    get_media_item_by_id,
    MediaItem,
)
from google.cloud import firestore  # Explicitly import for firestore.Query

from components.dialog import (
    dialog,
    dialog_actions,
)
from components.header import header
from components.page_scaffold import (
    page_frame,
    page_scaffold,
)
from components.pill import pill


# MediaItem class is imported from common.metadata, so local definition is not strictly needed here
# if it's identical. However, keeping it as per user's provided code structure.
# If MediaItem from common.metadata is the source of truth, ensure this definition matches
# or remove this local one and rely solely on the import.
# For this update, I am assuming the imported MediaItem from common.metadata is the one used.
# If there's a conflict, the imported one usually takes precedence depending on Python's import system.
# To be safe, it's best to have a single definition.
# The user's code has `from common.metadata import ... MediaItem`, so the local def below is effectively shadowed
# if `common.metadata` actually provides `MediaItem`. If not, this local def is used.
# Given the request, I'll assume the local definition is what the user wants this file to "see"
# and that get_media_item_by_id returns an object that duck-types correctly or is an instance of this.

# @me.stateclass # This local definition should be removed if MediaItem is correctly imported from common.metadata
# @dataclass
# class MediaItem:
#     """Represents a single media item in the library."""
#     id: Optional[str] = None
#     aspect: Optional[str] = None
#     gcsuri: Optional[str] = None
#     prompt: Optional[str] = None
#     generation_time: Optional[float] = None
#     timestamp: Optional[str] = None # ISO string format
#     reference_image: Optional[str] = None
#     last_reference_image: Optional[str] = None
#     enhanced_prompt: Optional[str] = None
#     duration: Optional[float] = None
#     error_message: Optional[str] = None
#     raw_data: Optional[Dict] = field(default_factory=dict)


@me.stateclass
@dataclass
class PageState:
    """Local Page State"""

    is_loading: bool = False
    current_page: int = 1
    videos_per_page: int = 9
    total_videos: int = 0
    videos: List[MediaItem] = field(default_factory=list)
    key: int = 0  # Key for media grid
    show_details_dialog: bool = False
    selected_media_item_id: Optional[str] = None
    dialog_instance_key: int = 0
    selected_values: list[str] = field(default_factory=lambda: ["videos"])
    initial_url_param_processed: bool = False
    url_item_not_found_message: Optional[str] = None


def get_videos_for_page(page: int, videos_per_page: int) -> List[MediaItem]:
    """Helper function to get videos for a specific page as MediaItem objects, using Firestore doc.id."""
    fetch_limit = 1000

    try:
        media_ref = (
            db.collection(config.GENMEDIA_COLLECTION_NAME)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(fetch_limit)
        )

        all_processed_media_items: List[MediaItem] = []
        for doc in media_ref.stream():
            raw_item_data = doc.to_dict()
            if raw_item_data is None:
                print(f"Warning: doc.to_dict() returned None for doc ID: {doc.id}")
                continue

            timestamp_iso_str: Optional[str] = None
            raw_timestamp = raw_item_data.get("timestamp")
            if isinstance(raw_timestamp, datetime):
                timestamp_iso_str = raw_timestamp.isoformat()
            elif isinstance(raw_timestamp, str):
                timestamp_iso_str = raw_timestamp
            elif hasattr(raw_timestamp, "isoformat"):
                timestamp_iso_str = raw_timestamp.isoformat()

            try:
                gen_time = (
                    float(raw_item_data.get("generation_time"))
                    if raw_item_data.get("generation_time") is not None
                    else None
                )
            except (ValueError, TypeError):
                gen_time = None

            try:
                item_duration = (
                    float(raw_item_data.get("duration"))
                    if raw_item_data.get("duration") is not None
                    else None
                )
            except (ValueError, TypeError):
                item_duration = None

            item_id_from_backend = doc.id

            # Assuming MediaItem is imported from common.metadata and is the correct class to instantiate
            media_item = MediaItem(
                id=item_id_from_backend,
                aspect=str(raw_item_data.get("aspect"))
                if raw_item_data.get("aspect") is not None
                else None,
                gcsuri=str(raw_item_data.get("gcsuri"))
                if raw_item_data.get("gcsuri") is not None
                else None,
                prompt=str(raw_item_data.get("prompt"))
                if raw_item_data.get("prompt") is not None
                else None,
                generation_time=gen_time,
                timestamp=timestamp_iso_str,
                reference_image=str(raw_item_data.get("reference_image"))
                if raw_item_data.get("reference_image") is not None
                else None,
                last_reference_image=str(raw_item_data.get("last_reference_image"))
                if raw_item_data.get("last_reference_image") is not None
                else None,
                enhanced_prompt=str(raw_item_data.get("enhanced_prompt"))
                if raw_item_data.get("enhanced_prompt") is not None
                else None,
                duration=item_duration,
                error_message=str(raw_item_data.get("error_message"))
                if raw_item_data.get("error_message") is not None
                else None,
                raw_data=raw_item_data,
            )
            all_processed_media_items.append(media_item)

        start_slice = (page - 1) * videos_per_page
        end_slice = start_slice + videos_per_page
        return all_processed_media_items[start_slice:end_slice]

    except Exception as e:
        print(f"Error fetching media from Firestore: {e}")
        return []


def library_content(app_state: me.state):
    pagestate = me.state(PageState)

    # Initial data loading and URL parameter processing
    if not pagestate.initial_url_param_processed:
        # Load initial page of videos if needed
        if not pagestate.videos and pagestate.total_videos == 0:
            pagestate.total_videos = get_total_media_count()
            if pagestate.total_videos > 0:
                pagestate.videos = get_videos_for_page(
                    pagestate.current_page, pagestate.videos_per_page
                )
        elif (
            not pagestate.videos and pagestate.total_videos > 0
        ):  # If total_videos is set but videos list is empty
            pagestate.videos = get_videos_for_page(
                pagestate.current_page, pagestate.videos_per_page
            )

        # Process URL parameter for media_id
        query_params = me.query_params
        media_id_from_url = query_params.get("media_id")

        if media_id_from_url:
            item_in_current_list = next(
                (v for v in pagestate.videos if v.id == media_id_from_url), None
            )

            if item_in_current_list:
                pagestate.selected_media_item_id = media_id_from_url
                pagestate.show_details_dialog = True
                pagestate.dialog_instance_key += 1
                print(
                    f"INFO: Dialog opened for media_id from URL (found in current page): {media_id_from_url}"
                )
            else:
                print(
                    f"INFO: Media ID {media_id_from_url} from URL not in current page. Attempting direct fetch..."
                )
                # Ensure get_media_item_by_id is imported from common.metadata
                fetched_item = get_media_item_by_id(media_id_from_url)
                if fetched_item:
                    # Add to list if not already there (could happen if list was empty)
                    if not any(v.id == fetched_item.id for v in pagestate.videos):
                        pagestate.videos.insert(0, fetched_item)  # Prepend
                    pagestate.selected_media_item_id = fetched_item.id
                    pagestate.show_details_dialog = True
                    pagestate.dialog_instance_key += 1
                    print(
                        f"INFO: Dialog opened for media_id from URL (fetched directly): {media_id_from_url}"
                    )
                else:
                    pagestate.url_item_not_found_message = (
                        f"Media item with ID '{media_id_from_url}' not found."
                    )
                    print(
                        f"ERROR: Media ID {media_id_from_url} from URL not found after direct fetch."
                    )

        pagestate.initial_url_param_processed = True

    total_pages = (
        (pagestate.total_videos + pagestate.videos_per_page - 1)
        // pagestate.videos_per_page
        if pagestate.videos_per_page > 0
        else 0
    )

    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():  # pylint: disable=not-context-manager
            header("Library", "perm_media")

            if pagestate.url_item_not_found_message:
                with me.box(
                    style=me.Style(
                        padding=me.Padding.all(16),
                        background=me.theme_var("error-container"),
                        color=me.theme_var("on-error-container"),
                        border_radius=8,
                        margin=me.Margin(bottom=16),
                    )
                ):
                    me.text(pagestate.url_item_not_found_message)

            with me.box():
                me.button_toggle(
                    value=pagestate.selected_values,
                    buttons=[
                        me.ButtonToggleButton(label="Images", value="images"),
                        me.ButtonToggleButton(label="Videos", value="videos"),
                        me.ButtonToggleButton(label="Music", value="music"),
                    ],
                    multiple=True,
                    hide_selection_indicator=False,
                    disabled=pagestate.is_loading,
                    on_change=on_change_selected_filters,
                    style=me.Style(margin=me.Margin(bottom=20)),
                )

            with me.box(
                key=str(pagestate.key),
                style=me.Style(
                    display="grid",
                    grid_template_columns="repeat(auto-fill, minmax(300px, 1fr))",
                    gap="16px",
                    width="100%",
                ),
            ):
                if pagestate.is_loading and not pagestate.show_details_dialog:
                    with me.box(
                        style=me.Style(
                            display="flex",
                            justify_content="center",
                            padding=me.Padding.all(20),
                        )
                    ):
                        me.progress_spinner()
                elif not pagestate.videos:
                    with me.box(
                        style=me.Style(padding=me.Padding.all(20), text_align="center")
                    ):
                        me.text("No media items found.")
                else:
                    for i, m_item in enumerate(pagestate.videos):
                        video_url = (
                            m_item.gcsuri.replace(
                                "gs://", "https://storage.mtls.cloud.google.com/"
                            )
                            if m_item.gcsuri
                            else ""
                        )
                        prompt_full = m_item.prompt or ""
                        prompt_display_grid = (
                            (prompt_full[:100] + "...")
                            if len(prompt_full) > 100
                            else prompt_full
                        )
                        timestamp_display_str = "N/A"
                        if m_item.timestamp:
                            try:
                                timestamp_display_str = datetime.fromisoformat(
                                    m_item.timestamp
                                ).strftime("%Y-%m-%d %H:%M")
                            except (ValueError, TypeError):
                                timestamp_display_str = m_item.timestamp
                        video_length = (
                            f"{m_item.duration} sec"
                            if m_item.duration is not None
                            else "Unknown"
                        )

                        with me.box(
                            key=str(i),
                            on_click=on_media_item_click,
                            style=me.Style(
                                padding=me.Padding.all(16),
                                display="flex",
                                flex_direction="column",
                                width="100%",
                                gap=10,
                                cursor="pointer",
                                border=me.Border.all(
                                    me.BorderSide(
                                        width=1, color=me.theme_var("outline-variant")
                                    )
                                ),
                                border_radius=12,
                                background=me.theme_var("surface-container-low"),
                            ),
                        ):
                            me.text(
                                f"Generated: {timestamp_display_str}",
                                style=me.Style(
                                    font_weight="bold",
                                    font_size="0.9em",
                                    color=me.theme_var("onsecondarycontainer"),
                                ),
                            )
                            with me.box(
                                style=me.Style(
                                    display="flex",
                                    flex_wrap="wrap",
                                    gap=5,
                                    margin=me.Margin(bottom=8),
                                )
                            ):
                                pill(
                                    "t2v" if not m_item.reference_image else "i2v",
                                    "gen_t2v"
                                    if not m_item.reference_image
                                    else "gen_i2v",
                                )
                                pill(m_item.aspect or "16:9", "aspect")
                                pill(video_length, "duration")
                                pill("24 fps", "fps")
                                if m_item.enhanced_prompt:
                                    with me.tooltip(message="Prompt was auto-enhanced"):
                                        me.icon(
                                            "auto_fix_normal",
                                            style=me.Style(
                                                color=me.theme_var("primary")
                                            ),
                                        )
                            me.text(
                                f'"{prompt_display_grid}"'
                                if prompt_display_grid
                                else "No prompt provided",
                                style=me.Style(
                                    font_size="10pt",
                                    font_style="italic"
                                    if prompt_display_grid
                                    else "normal",
                                    min_height="40px",
                                ),
                            )
                            with me.box(
                                style=me.Style(
                                    display="flex",
                                    flex_direction="row",
                                    gap=8,
                                    align_items="flex-start",
                                    margin=me.Margin(top=8, bottom=8),
                                )
                            ):
                                if m_item.error_message:
                                    me.text(
                                        f"Error: {m_item.error_message}",
                                        style=me.Style(
                                            width="100%",
                                            font_style="italic",
                                            font_size="10pt",
                                            margin=me.Margin.all(3),
                                            padding=me.Padding.all(8),
                                            border=me.Border.all(
                                                me.BorderSide(
                                                    style="solid",
                                                    width=1,
                                                    color=me.theme_var("error"),
                                                )
                                            ),
                                            border_radius=5,
                                            background=me.theme_var("errorcontainer"),
                                            color=me.theme_var("onerrorcontainer"),
                                        ),
                                    )
                                else:
                                    if video_url:
                                        me.video(
                                            src=video_url,
                                            style=me.Style(
                                                width="100%",
                                                height="150px",
                                                border_radius=6,
                                                object_fit="cover",
                                            ),
                                        )
                                    else:
                                        me.text(
                                            "Video not available.",
                                            style=me.Style(
                                                height="150px",
                                                display="flex",
                                                align_items="center",
                                                justify_content="center",
                                                color=me.theme_var("onsurfacevariant"),
                                            ),
                                        )

                                ref_images_box_style = me.Style(
                                    display="flex", flex_direction="column", gap=5
                                )
                                with me.box(style=ref_images_box_style):
                                    if m_item.reference_image:
                                        ref_img_url = m_item.reference_image.replace(
                                            "gs://",
                                            "https://storage.mtls.cloud.google.com/",
                                        )
                                        me.image(
                                            src=ref_img_url,
                                            style=me.Style(
                                                height="70px",
                                                width="auto",
                                                border_radius=4,
                                                object_fit="contain",
                                            ),
                                        )
                                    if m_item.last_reference_image:
                                        last_ref_img_url = m_item.last_reference_image.replace(
                                            "gs://",
                                            "https://storage.mtls.cloud.google.com/",
                                        )
                                        me.image(
                                            src=last_ref_img_url,
                                            style=me.Style(
                                                height="70px",
                                                width="auto",
                                                border_radius=4,
                                                object_fit="contain",
                                            ),
                                        )

                            if m_item.generation_time is not None:
                                me.text(
                                    f"Generated in {round(m_item.generation_time)} seconds.",
                                    style=me.Style(
                                        font_size="0.8em",
                                        color=me.theme_var("onsurfacevariant"),
                                    ),
                                )

            library_dialog_style = me.Style(
                max_width="80vw", width="80vw", min_width="600px"
            )

            # pylint: disable=not-context-manager
            with dialog(
                key=str(pagestate.dialog_instance_key),
                is_open=pagestate.show_details_dialog,
                dialog_style=library_dialog_style,
            ):
                item_to_display: Optional[MediaItem] = None
                if pagestate.selected_media_item_id:
                    item_to_display = next(
                        (
                            v
                            for v in pagestate.videos
                            if v.id == pagestate.selected_media_item_id
                        ),
                        None,
                    )

                if item_to_display:
                    item = item_to_display
                    with me.box(
                        style=me.Style(
                            display="flex",
                            flex_direction="column",
                            gap=12,
                            width="100%",
                            max_width="900px",
                            height="auto",
                            max_height="75vh",
                            overflow_y="auto",
                            padding=me.Padding.all(16),
                        )
                    ):
                        me.text(
                            "Media Details",
                            style=me.Style(
                                font_size="1.25rem",
                                font_weight="bold",
                                margin=me.Margin(bottom=8),
                                color=me.theme_var("on-secondary-container"),
                                flex_shrink=0,
                            ),
                        )

                        # Formatted details section
                        item_video_url_dialog = (
                            item.gcsuri.replace(
                                "gs://", "https://storage.mtls.cloud.google.com/"
                            )
                            if item.gcsuri
                            else ""
                        )
                        if item_video_url_dialog:
                            me.video(
                                src=item_video_url_dialog,
                                style=me.Style(
                                    width="100%",
                                    max_height="350px",
                                    border_radius=8,
                                    background="#000",
                                    display="block",
                                    margin=me.Margin(top=8, bottom=8),
                                ),
                            )
                        if item.error_message:
                            me.text(
                                f"Error: {item.error_message}",
                                style=me.Style(
                                    color=me.theme_var("error"), font_style="italic"
                                ),
                            )
                        me.text(f"Prompt: \"{item.prompt or 'N/A'}\"")
                        if item.enhanced_prompt:
                            me.text(f'Enhanced Prompt: "{item.enhanced_prompt}"')
                        item_timestamp_display_str_dialog = "N/A"
                        if item.timestamp:
                            try:
                                item_timestamp_display_str_dialog = (
                                    datetime.fromisoformat(item.timestamp).strftime(
                                        "%Y-%m-%d %H:%M"
                                    )
                                )
                            except (ValueError, TypeError):
                                item_timestamp_display_str_dialog = item.timestamp
                        me.text(f"Generated: {item_timestamp_display_str_dialog}")
                        if item.generation_time is not None:
                            me.text(
                                f"Generation Time: {round(item.generation_time)} seconds"
                            )
                        if item.aspect:
                            me.text(f"Aspect Ratio: {item.aspect}")
                        if item.duration is not None:
                            me.text(f"Duration: {item.duration} seconds")
                        if item.reference_image:
                            ref_url = item.reference_image.replace(
                                "gs://", "https://storage.mtls.cloud.google.com/"
                            )
                            me.text(
                                "Reference Image:",
                                style=me.Style(
                                    font_weight="medium", margin=me.Margin(top=8)
                                ),
                            )
                            me.image(
                                src=ref_url,
                                style=me.Style(
                                    max_width="250px",
                                    height="auto",
                                    border_radius=6,
                                    margin=me.Margin(top=4),
                                ),
                            )
                        if item.last_reference_image:
                            last_ref_url = item.last_reference_image.replace(
                                "gs://", "https://storage.mtls.cloud.google.com/"
                            )
                            me.text(
                                "Last Reference Image:",
                                style=me.Style(
                                    font_weight="medium", margin=me.Margin(top=8)
                                ),
                            )
                            me.image(
                                src=last_ref_url,
                                style=me.Style(
                                    max_width="250px",
                                    height="auto",
                                    border_radius=6,
                                    margin=me.Margin(top=4),
                                ),
                            )

                        # Raw Firestore Data Section
                        if item.raw_data:
                            with me.expansion_panel(
                                key="metadata",
                                title="Metadata",
                                description=pagestate.selected_media_item_id,
                                icon="local_fire_department",
                            ):
                                # me.text("Firestore Document Data:", style=me.Style(font_weight="bold", margin=me.Margin(top=16, bottom=4)))
                                try:
                                    json_string = json.dumps(
                                        item.raw_data, indent=2, default=str
                                    )
                                    me.markdown(f"```json\n{json_string}\n```")
                                except Exception as e_json:
                                    print(
                                        f"Error serializing raw_data to JSON: {e_json}"
                                    )
                                    me.text(
                                        "Could not display raw data (serialization error)."
                                    )
                        else:
                            me.text("Raw Firestore data not available.")
                else:
                    with me.box(style=me.Style(padding=me.Padding.all(16))):
                        me.text("No media item selected or found for the given ID.")

                # pylint: disable=not-context-manager

                with dialog_actions():
                    me.button("Close", on_click=on_close_details_dialog, type="flat")

            if total_pages > 1:
                with me.box(
                    style=me.Style(
                        display="flex",
                        justify_content="center",
                        align_items="center",
                        gap=16,
                        margin=me.Margin(top=24, bottom=24),
                    )
                ):
                    me.button(
                        "Previous",
                        key="-1",
                        on_click=handle_page_change,
                        disabled=pagestate.current_page == 1 or pagestate.is_loading,
                        type="stroked",
                    )
                    me.text(f"Page {pagestate.current_page} of {total_pages}")
                    me.button(
                        "Next",
                        key="1",
                        on_click=handle_page_change,
                        disabled=pagestate.current_page == total_pages
                        or pagestate.is_loading,
                        type="stroked",
                    )


def on_media_item_click(e: me.ClickEvent):
    pagestate = me.state(PageState)
    try:
        selected_index = int(e.key)
        if 0 <= selected_index < len(pagestate.videos):
            clicked_item = pagestate.videos[selected_index]
            if clicked_item.id is None:
                print(f"WARNING: Clicked item at index {selected_index} has a None ID.")
            pagestate.selected_media_item_id = clicked_item.id
            pagestate.show_details_dialog = True
            pagestate.dialog_instance_key += 1
            pagestate.url_item_not_found_message = None
        else:
            print(f"Error: Invalid index {selected_index} for media item click.")
    except ValueError:
        print(f"Error: Click event key '{e.key}' is not a valid integer index.")
    yield


def on_close_details_dialog(e: me.ClickEvent):
    pagestate = me.state(PageState)
    pagestate.show_details_dialog = False
    pagestate.selected_media_item_id = None
    pagestate.url_item_not_found_message = None
    yield


def handle_page_change(e: me.ClickEvent):
    pagestate = me.state(PageState)
    if pagestate.is_loading:
        yield
        return

    if pagestate.total_videos == 0:
        pagestate.total_videos = get_total_media_count()

    pagestate.is_loading = True
    yield
    direction = int(e.key)
    new_page = pagestate.current_page + direction

    current_total_pages = (
        (pagestate.total_videos + pagestate.videos_per_page - 1)
        // pagestate.videos_per_page
        if pagestate.videos_per_page > 0
        else 0
    )

    if 1 <= new_page <= current_total_pages:
        pagestate.current_page = new_page
        pagestate.videos = get_videos_for_page(
            pagestate.current_page, pagestate.videos_per_page
        )
        pagestate.key += 1
        pagestate.url_item_not_found_message = None
    pagestate.is_loading = False
    yield


def on_change_selected_filters(e: me.ButtonToggleChangeEvent):
    pagestate = me.state(PageState)
    pagestate.selected_values = e.values
    pagestate.url_item_not_found_message = None
    # This is where you would typically re-fetch data based on the new filters.
    # pagestate.current_page = 1
    # pagestate.is_loading = True; yield
    # pagestate.videos = get_videos_for_page(1, pagestate.videos_per_page, filters=pagestate.selected_values)
    # pagestate.total_videos = get_total_media_count(filters=pagestate.selected_values)
    # pagestate.key +=1
    # pagestate.is_loading = False; yield
    yield
