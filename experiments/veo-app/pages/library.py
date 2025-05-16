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
from common.metadata import (
    get_total_media_count, 
    db, 
    config, 
    get_media_item_by_id, 
    MediaItem
)
from google.cloud import firestore # Explicitly import for firestore.Query

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


@me.stateclass
@dataclass
class PageState:
    """Local Page State"""
    is_loading: bool = False
    current_page: int = 1
    media_per_page: int = 9
    total_media: int = 0
    media_items: List[MediaItem] = field(default_factory=list) 
    key: int = 0 
    show_details_dialog: bool = False
    selected_media_item_id: Optional[str] = None 
    dialog_instance_key: int = 0
    selected_values: list[str] = field(default_factory=lambda: ["videos", "images", "music"]) # Default to all types
    initial_url_param_processed: bool = False 
    url_item_not_found_message: Optional[str] = None


def get_media_for_page(page: int, media_per_page: int, filters: Optional[List[str]] = None) -> List[MediaItem]:
    """
    Helper function to get media for a specific page as MediaItem objects, 
    using Firestore doc.id. Includes basic filtering by mime_type.
    """
    fetch_limit = 1000 # Adjust as needed, or implement server-side cursors for true pagination

    try:
        query = db.collection(config.GENMEDIA_COLLECTION_NAME).order_by("timestamp", direction=firestore.Query.DESCENDING)
        
        # Basic client-side filtering based on selected_values (mime_type prefixes)
        # For production, filtering should ideally be done server-side if possible.
        # This example fetches a larger set and then filters.

        all_fetched_items: List[MediaItem] = []
        for doc in query.limit(fetch_limit).stream(): # Fetch a larger set for client-side filtering/pagination
            raw_item_data = doc.to_dict()
            if raw_item_data is None: 
                print(f"Warning: doc.to_dict() returned None for doc ID: {doc.id}")
                continue

            # Ensure mime_type is available for filtering
            mime_type = raw_item_data.get("mime_type", "") 
            
            # Client-side filter application
            passes_filter = True
            if filters:
                passes_filter = False
                if "videos" in filters and mime_type.startswith("video/"):
                    passes_filter = True
                elif "images" in filters and mime_type.startswith("image/"):
                    passes_filter = True
                elif "music" in filters and mime_type.startswith("audio/"):
                    passes_filter = True
            
            if not passes_filter:
                continue

            timestamp_iso_str: Optional[str] = None
            raw_timestamp = raw_item_data.get("timestamp")
            if isinstance(raw_timestamp, datetime): 
                timestamp_iso_str = raw_timestamp.isoformat()
            elif isinstance(raw_timestamp, str): 
                timestamp_iso_str = raw_timestamp
            elif hasattr(raw_timestamp, 'isoformat'): 
                 timestamp_iso_str = raw_timestamp.isoformat()

            try: gen_time = float(raw_item_data.get("generation_time")) if raw_item_data.get("generation_time") is not None else None
            except (ValueError, TypeError): gen_time = None
            
            try: item_duration = float(raw_item_data.get("duration")) if raw_item_data.get("duration") is not None else None
            except (ValueError, TypeError): item_duration = None

            media_item = MediaItem(
                id=doc.id, 
                aspect=str(raw_item_data.get("aspect")) if raw_item_data.get("aspect") is not None else None,
                gcsuri=str(raw_item_data.get("gcsuri")) if raw_item_data.get("gcsuri") is not None else None,
                prompt=str(raw_item_data.get("prompt")) if raw_item_data.get("prompt") is not None else None,
                generation_time=gen_time, 
                timestamp=timestamp_iso_str,
                reference_image=str(raw_item_data.get("reference_image")) if raw_item_data.get("reference_image") is not None else None,
                last_reference_image=str(raw_item_data.get("last_reference_image")) if raw_item_data.get("last_reference_image") is not None else None,
                enhanced_prompt=str(raw_item_data.get("enhanced_prompt")) if raw_item_data.get("enhanced_prompt") is not None else None,
                duration=item_duration,
                error_message=str(raw_item_data.get("error_message")) if raw_item_data.get("error_message") is not None else None,
                raw_data=raw_item_data 
            )
            all_fetched_items.append(media_item)
        
        # Update total_videos based on the count of items that passed the filter
        # This is not ideal as it means total_videos might change based on client-side filter of a limited fetch.
        # A better approach is to get the count from Firestore with filters.
        # For now, this will make pagination work with the client-filtered list.
        # pagestate = me.state(PageState) # Cannot get state here
        # pagestate.total_videos = len(all_fetched_items) # This needs to be handled carefully

        start_slice = (page - 1) * media_per_page
        end_slice = start_slice + media_per_page
        return all_fetched_items[start_slice:end_slice]

    except Exception as e:
        print(f"Error fetching media from Firestore: {e}")
        return []


def library_content(app_state: me.state):
    pagestate = me.state(PageState)

    # Initial data loading and URL parameter processing
    if not pagestate.initial_url_param_processed:
        # Fetch total count based on current filters (or all if no filters initially)
        # For simplicity, get_total_media_count might need to accept filters too.
        # Or, we fetch all and then filter, which is done in get_media_for_page now.
        
        # Load initial page of media
        # The get_media_for_page function now handles basic client-side filtering
        current_media = get_media_for_page(pagestate.current_page, pagestate.media_per_page, pagestate.selected_values)
        
        # To correctly set total_videos for pagination WITH client-side filtering,
        # ideally, get_total_media_count would also accept filters.
        # As a workaround for now, if filters are active, total_videos might be less accurate
        # unless get_media_for_page fetched ALL items and then filtered.
        # For this example, let's assume get_total_media_count gives total unfiltered,
        # and pagination might be slightly off if filters reduce the item count significantly.
        if not pagestate.media_items and pagestate.total_media == 0: # Only set total_videos once initially
            pagestate.total_media = get_total_media_count() 
        
        pagestate.media_items = current_media


        query_params = me.query_params
        media_id_from_url = query_params.get("media_id")
        
        if media_id_from_url:
            item_in_current_list = next((v for v in pagestate.media_items if v.id == media_id_from_url), None)

            if item_in_current_list:
                pagestate.selected_media_item_id = media_id_from_url
                pagestate.show_details_dialog = True
                pagestate.dialog_instance_key += 1
            else:
                fetched_item = get_media_item_by_id(media_id_from_url) 
                if fetched_item:
                    if not any(v.id == fetched_item.id for v in pagestate.media_items):
                        pagestate.media_items.insert(0, fetched_item) 
                    pagestate.selected_media_item_id = fetched_item.id
                    pagestate.show_details_dialog = True
                    pagestate.dialog_instance_key += 1
                else:
                    pagestate.url_item_not_found_message = f"Media item with ID '{media_id_from_url}' not found."
        
        pagestate.initial_url_param_processed = True


    total_pages = (
        pagestate.total_media + pagestate.media_per_page - 1
    ) // pagestate.media_per_page if pagestate.media_per_page > 0 else 0


    with page_scaffold():
        with page_frame():
            header("Library", "perm_media")

            if pagestate.url_item_not_found_message:
                with me.box(style=me.Style(padding=me.Padding.all(16), background=me.theme_var("error-container"), color=me.theme_var("on-error-container"), border_radius=8, margin=me.Margin(bottom=16))):
                    me.text(pagestate.url_item_not_found_message)

            with me.box(): 
                me.button_toggle(
                    value=pagestate.selected_values,
                    buttons=[
                        me.ButtonToggleButton(label="All", value="all"), # Added "All"
                        me.ButtonToggleButton(label="Images", value="images"),
                        me.ButtonToggleButton(label="Videos", value="videos"),
                        me.ButtonToggleButton(label="Music", value="music"),
                    ],
                    multiple=True, # Keep true if you want multiple selections, or false for single
                    on_change=on_change_selected_filters, 
                    style=me.Style(margin=me.Margin(bottom=20)),
                )

            with me.box(key=str(pagestate.key), style=me.Style(display="grid", grid_template_columns="repeat(auto-fill, minmax(300px, 1fr))", gap="16px", width="100%")):
                if pagestate.is_loading and not pagestate.show_details_dialog:
                    with me.box(style=me.Style(display="flex", justify_content="center", padding=me.Padding.all(20))):
                        me.progress_spinner()
                elif not pagestate.media_items:
                    with me.box(style=me.Style(padding=me.Padding.all(20), text_align="center")):
                        me.text("No media items found for the selected filters.")
                else:
                    for i, m_item in enumerate(pagestate.media_items):  
                        mime_type = m_item.raw_data.get("mime_type", "") if m_item.raw_data else ""
                        media_type_group = ""
                        if mime_type.startswith("video/"): media_type_group = "video"
                        elif mime_type.startswith("image/"): media_type_group = "image"
                        elif mime_type.startswith("audio/"): media_type_group = "audio"

                        item_url = m_item.gcsuri.replace("gs://", "https://storage.mtls.cloud.google.com/") if m_item.gcsuri else ""
                        
                        prompt_full = m_item.prompt or ""
                        prompt_display_grid = (prompt_full[:100] + "...") if len(prompt_full) > 100 else prompt_full
                        
                        timestamp_display_str = "N/A"
                        if m_item.timestamp:
                            try: timestamp_display_str = datetime.fromisoformat(m_item.timestamp).strftime("%Y-%m-%d %H:%M")
                            except (ValueError, TypeError): timestamp_display_str = m_item.timestamp
                        
                        item_duration_str = f"{m_item.duration} sec" if m_item.duration is not None else "N/A"

                        with me.box(key=str(i), on_click=on_media_item_click, style=me.Style(
                            padding=me.Padding.all(16), display="flex", flex_direction="column", width="100%", gap=10, cursor="pointer",
                            border=me.Border.all(me.BorderSide(width=1, color=me.theme_var("outline-variant"))), 
                            border_radius=12, background=me.theme_var("surface-container-low"),
                        )):
                            me.text(f"Generated: {timestamp_display_str}", style=me.Style(font_weight="bold", font_size="0.9em", color=me.theme_var("onsecondarycontainer")))
                            
                            # Pills section
                            with me.box(style=me.Style(display="flex", flex_wrap="wrap", gap=5, margin=me.Margin(bottom=8))):
                                if media_type_group == "video":
                                    pill("Video", "media_type_video") # General type pill
                                    pill("t2v" if not m_item.reference_image else "i2v", "gen_t2v" if not m_item.reference_image else "gen_i2v")
                                    if m_item.aspect: pill(m_item.aspect, "aspect")
                                    if m_item.duration is not None: pill(item_duration_str, "duration")
                                    pill("24 fps", "fps") # Assuming for video
                                elif media_type_group == "image":
                                    pill("Image", "media_type_image")
                                    if m_item.aspect: pill(m_item.aspect, "aspect")
                                elif media_type_group == "audio":
                                    pill("Audio", "media_type_audio")
                                    if m_item.duration is not None: pill(item_duration_str, "duration")
                                
                                if m_item.enhanced_prompt and media_type_group == "video": # Assuming enhanced prompt is video specific
                                    with me.tooltip(message="Prompt was auto-enhanced"):
                                        me.icon("auto_fix_normal", style=me.Style(color=me.theme_var("primary")))
                            
                            me.text(f'"{prompt_display_grid}"' if prompt_display_grid else "No prompt provided", style=me.Style(font_size="10pt", font_style="italic" if prompt_display_grid else "normal", min_height="40px"))
                            
                            # Media Preview Section
                            with me.box(style=me.Style(display="flex", flex_direction="row", gap=8, align_items="center", justify_content="center", margin=me.Margin(top=8, bottom=8), min_height="150px")):
                                if m_item.error_message:
                                    me.text(f"Error: {m_item.error_message}", style=me.Style(width="100%", font_style="italic", font_size="10pt", margin=me.Margin.all(3), padding=me.Padding.all(8), border=me.Border.all(me.BorderSide(style="solid", width=1, color=me.theme_var("error"))), border_radius=5, background=me.theme_var("errorcontainer"), color=me.theme_var("onerrorcontainer")))
                                else:
                                    if media_type_group == "video" and item_url:
                                        me.video(src=item_url, style=me.Style(width="100%", height="150px", border_radius=6, object_fit="cover"))
                                    elif media_type_group == "image" and item_url:
                                        me.image(src=item_url, alt_text=m_item.prompt or "Generated Image", style=me.Style(max_width="100%", max_height="150px", height="auto", border_radius=6, object_fit="contain"))
                                    elif media_type_group == "audio" and item_url:
                                        me.audio(src=item_url, 
                                                 #style=me.Style(width="100%"),
                                        )
                                    else:
                                        me.text(f"{media_type_group.capitalize() if media_type_group else 'Media'} not available.", style=me.Style(height="150px", display="flex", align_items="center", justify_content="center", color=me.theme_var("onsurfacevariant")))
                            
                                if media_type_group == "video": # Show reference images only for video
                                    with me.box(style=me.Style(display="flex", flex_direction="column", gap=5)):
                                        if m_item.reference_image:
                                            ref_img_url = m_item.reference_image.replace("gs://", "https://storage.mtls.cloud.google.com/")
                                            me.image(src=ref_img_url, style=me.Style(height="70px", width="auto", border_radius=4, object_fit="contain"))
                                        if m_item.last_reference_image:
                                            last_ref_img_url = m_item.last_reference_image.replace("gs://", "https://storage.mtls.cloud.google.com/")
                                            me.image(src=last_ref_img_url, style=me.Style(height="70px", width="auto", border_radius=4, object_fit="contain"))

                            if m_item.generation_time is not None:
                                me.text(f"Generated in {round(m_item.generation_time)} seconds.", style=me.Style(font_size="0.8em", color=me.theme_var("onsurfacevariant")))

            library_dialog_style = me.Style(max_width="80vw", width="80vw", min_width="600px")
            
            with dialog(key=str(pagestate.dialog_instance_key), is_open=pagestate.show_details_dialog, dialog_style=library_dialog_style):
                item_to_display: Optional[MediaItem] = None
                if pagestate.selected_media_item_id:
                    item_to_display = next((v for v in pagestate.media_items if v.id == pagestate.selected_media_item_id), None)
                
                if item_to_display:
                    item = item_to_display 
                    dialog_mime_type = item.raw_data.get("mime_type", "") if item.raw_data else ""
                    dialog_media_type_group = ""
                    if dialog_mime_type.startswith("video/"): dialog_media_type_group = "video"
                    elif dialog_mime_type.startswith("image/"): dialog_media_type_group = "image"
                    elif dialog_mime_type.startswith("audio/"): dialog_media_type_group = "audio"

                    with me.box(style=me.Style(display="flex", flex_direction="column", gap=12, width="100%", max_width="900px", height="auto", max_height="80vh", overflow_y="auto", padding=me.Padding.all(24))): # Increased padding
                        me.text("Media Details", style=me.Style(font_size="1.5rem", font_weight="bold", margin=me.Margin(bottom=16), color=me.theme_var("on-surface-variant"), flex_shrink=0)) # Adjusted title style
                        
                        # Media Preview in Dialog
                        item_display_url = item.gcsuri.replace("gs://", "https://storage.mtls.cloud.google.com/") if item.gcsuri else ""
                        if dialog_media_type_group == "video" and item_display_url:
                           me.video(src=item_display_url, style=me.Style(width="100%", max_height="40vh", border_radius=8, background="#000", display="block", margin=me.Margin(bottom=16)))
                        elif dialog_media_type_group == "image" and item_display_url:
                           me.image(src=item_display_url, alt_text=item.prompt or "Image", style=me.Style(width="100%", max_height="40vh", border_radius=8, object_fit="contain", margin=me.Margin(bottom=16)))
                        elif dialog_media_type_group == "audio" and item_display_url:
                           me.audio(src=item_display_url, 
                                    #style=me.Style(width="100%", margin=me.Margin(top=8, bottom=16))
                                    )

                        if item.error_message: me.text(f"Error: {item.error_message}", style=me.Style(color=me.theme_var("error"), font_style="italic"))
                        me.text(f"Prompt: \"{item.prompt or 'N/A'}\"")
                        if item.enhanced_prompt: me.text(f'Enhanced Prompt: "{item.enhanced_prompt}"')
                        
                        dialog_timestamp_str = "N/A"
                        if item.timestamp:
                            try: dialog_timestamp_str = datetime.fromisoformat(item.timestamp).strftime("%Y-%m-%d %H:%M")
                            except (ValueError, TypeError): dialog_timestamp_str = item.timestamp
                        me.text(f"Generated: {dialog_timestamp_str}")

                        if item.generation_time is not None: me.text(f"Generation Time: {round(item.generation_time)} seconds")
                        
                        if dialog_media_type_group == "video" or dialog_media_type_group == "image":
                            if item.aspect: me.text(f"Aspect Ratio: {item.aspect}")
                        if dialog_media_type_group == "video" or dialog_media_type_group == "audio":
                            if item.duration is not None: me.text(f"Duration: {item.duration} seconds")
                        
                        if dialog_media_type_group == "video": # Video specific details
                            if item.reference_image:
                                ref_url = item.reference_image.replace("gs://", "https://storage.mtls.cloud.google.com/")
                                me.text("Reference Image:", style=me.Style(font_weight="medium", margin=me.Margin(top=8)))
                                me.image(src=ref_url, style=me.Style(max_width="250px", height="auto", border_radius=6, margin=me.Margin(top=4)))
                            if item.last_reference_image:
                                last_ref_url = item.last_reference_image.replace("gs://", "https://storage.mtls.cloud.google.com/")
                                me.text("Last Reference Image:", style=me.Style(font_weight="medium", margin=me.Margin(top=8)))
                                me.image(src=last_ref_url, style=me.Style(max_width="250px", height="auto", border_radius=6, margin=me.Margin(top=4)))
                        
                        with me.content_button(
                            on_click=on_click_set_permalink,
                            key=item.id,
                        ):
                            with me.box(
                                style=me.Style(display="flex", flex_direction="row", align_items="center", gap=5)
                            ):
                                me.icon(icon="link")
                                me.text("permalink")

                        if item.raw_data:
                            with me.expansion_panel(key="raw_metadata_panel", title="Firestore Metadata", description=item.id, icon="dataset"):
                                try:
                                    json_string = json.dumps(item.raw_data, indent=2, default=str) 
                                    me.markdown(f"```json\n{json_string}\n```")
                                except Exception as e_json:
                                    print(f"Error serializing raw_data to JSON: {e_json}")
                                    me.text("Could not display raw data (serialization error).")
                        else:
                            me.text("Raw Firestore data not available.")
                else: 
                    with me.box(style=me.Style(padding=me.Padding.all(16))):
                         me.text("No media item selected or found for the given ID.")

                with dialog_actions():
                    me.button("Close", on_click=on_close_details_dialog, type="flat")

            if total_pages > 1: 
                with me.box(style=me.Style(display="flex", justify_content="center", align_items="center", gap=16, margin=me.Margin(top=24, bottom=24))):
                    me.button("Previous", key="-1", on_click=handle_page_change, disabled=pagestate.current_page == 1 or pagestate.is_loading, type="stroked")
                    me.text(f"Page {pagestate.current_page} of {total_pages}")
                    me.button("Next", key="1", on_click=handle_page_change, disabled=pagestate.current_page == total_pages or pagestate.is_loading, type="stroked")


def on_click_set_permalink(e: me.ClickEvent):
    """ set the permalink from dialog """
    me.query_params['media_id'] = e.key

def on_media_item_click(e: me.ClickEvent):
    pagestate = me.state(PageState)
    try:
        selected_index = int(e.key)
        if 0 <= selected_index < len(pagestate.media_items):
            clicked_item = pagestate.media_items[selected_index]
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
    if pagestate.is_loading: yield; return
    
    if pagestate.total_media == 0: 
        pagestate.total_media = get_total_media_count()

    pagestate.is_loading = True; yield
    direction = int(e.key)
    new_page = pagestate.current_page + direction
    
    current_total_pages = (pagestate.total_media + pagestate.media_per_page - 1) // pagestate.media_per_page if pagestate.media_per_page > 0 else 0

    if 1 <= new_page <= current_total_pages:
        pagestate.current_page = new_page
        pagestate.media_items = get_media_for_page(pagestate.current_page, pagestate.media_per_page, pagestate.selected_values) 
        pagestate.key += 1
        pagestate.url_item_not_found_message = None 
    pagestate.is_loading = False; yield

def on_change_selected_filters(e: me.ButtonToggleChangeEvent):
    pagestate = me.state(PageState)
    new_filters = e.values
    # Handle "All" filter: if "all" is selected, or if no specific type is selected, show all.
    # If specific types are selected, "all" should be ignored or deselected.
    if "all" in new_filters and len(new_filters) > 1:
        pagestate.selected_values = [val for val in new_filters if val != "all"]
    elif not new_filters: # If everything is deselected, default to "all"
        pagestate.selected_values = ["all"]
    else:
        pagestate.selected_values = new_filters
    
    pagestate.url_item_not_found_message = None 
    pagestate.current_page = 1 # Reset to first page on filter change
    pagestate.is_loading = True
    yield # Allow UI to update (e.g., show spinner)

    # Refetch data with new filters
    # The total count might change based on filters, so we need to be careful.
    # For a simple client-side filter as implemented in get_media_for_page,
    # get_total_media_count would ideally also take filters.
    # For now, we'll refetch the first page and the total count (unfiltered).
    # This might lead to pagination inaccuracies if filters drastically reduce item count.
    
    # pagestate.total_videos = get_total_media_count() # Or a filtered count if available
    
    # Fetching all items and then filtering for total_videos (if client-side filtering is primary)
    # This is inefficient for large datasets.
    all_items_for_filter_count = get_media_for_page(1, 9999, pagestate.selected_values) # Fetch all matching
    pagestate.total_media = len(all_items_for_filter_count)
    
    pagestate.media_items = get_media_for_page(pagestate.current_page, pagestate.media_per_page, pagestate.selected_values)
    pagestate.key += 1 
    pagestate.is_loading = False
    yield
