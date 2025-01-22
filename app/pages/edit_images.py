from __future__ import annotations

from typing import TYPE_CHECKING, Any

import mesop as me
from absl import logging
from components.header import header
from config import config_lib
from utils import auth_request
import base64

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

config = config_lib.AppConfig()

_BOX_STYLE = me.Style(
    flex_basis="max(480px, calc(50% - 48px))",
    background=me.theme_var("background"),
    border_radius=12,
    box_shadow=("0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"),
    padding=me.Padding(top=16, left=16, right=16, bottom=16),
    display="flex",
    flex_direction="column",
    width="100%",
)


@me.stateclass
class EditImagesPageState:
    """Local Page State"""

    show_advanced: bool = False
    temp_name: str = ""
    is_loading: bool = False

    prompt_input: str = ""
    prompt_placeholder: str = ""
    textarea_key: int = 0

    upload_file: me.UploadedFile = None
    upload_file_key: int = 0
    upload_uri: str = ""
    edit_mode: str = "EDIT_MODE_INPAINT_INSERTION"
    edit_prompt_placeholder: str = ""
    edit_output_key: int = 0
    edit_uri: str = ""
    foreground_background: str = "foreground"


def content() -> None:
    page_state = me.state(EditImagesPageState)
    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="column",
            height="100%",
        ),
    ):
        with me.box(
            style=me.Style(
                background=me.theme_var("background"),  # "#f0f4f8",
                height="100%",
                overflow_y="scroll",
                margin=me.Margin(bottom=20),
            ),
        ):
            with me.box(
                style=me.Style(
                    background=me.theme_var("background"),
                    padding=me.Padding(top=24, left=24, right=24, bottom=24),
                    display="flex",
                    flex_direction="column",
                    height="100%",
                ),
            ):
                # Page Header
                header("Edit Images", "edit")

                # Page Contents
                with me.box(
                    style=me.Style(
                        margin=me.Margin(left="auto", right="auto"),
                        width="min(1024px, 100%)",
                        gap="24px",
                        display="flex",
                        flex_direction="column",
                    ),
                ):
                    # Edit input & output
                    with me.box(
                        style=me.Style(
                            display="flex",
                            flex_direction="row",
                            gap=20,
                        ),
                    ):
                        with me.box(style=_BOX_STYLE):
                            me.text("Upload Image", style=me.Style(font_weight="bold"))
                            me.box(style=me.Style(height="12px"))

                            if page_state.upload_uri:
                                me.image(
                                    src=page_state.upload_uri.replace(
                                        "gs://",
                                        "https://storage.mtls.cloud.google.com/",
                                    ),
                                    style=me.Style(
                                        height="400px",
                                        border_radius=12,
                                    ),
                                    key=str(page_state.upload_file_key),
                                )
                            else:
                                me.box(style=me.Style(height="400px", width="400px"))
                            me.box(style=me.Style(height="12px"))
                            me.uploader(
                                label="Upload Image",
                                accepted_file_types=["image/jpeg", "image/png"],
                                on_upload=on_upload,
                                type="flat",
                                color="primary",
                                style=me.Style(font_weight="bold"),
                            )
                        with me.box(style=_BOX_STYLE):
                            me.text("Output Image", style=me.Style(font_weight="bold"))
                            me.box(style=me.Style(height="12px"))

                            if page_state.edit_uri:
                                me.image(
                                    src=page_state.edit_uri.replace(
                                        "gs://",
                                        "https://storage.mtls.cloud.google.com/",
                                    ),
                                    style=me.Style(
                                        height="400px",
                                        border_radius=12,
                                    ),
                                    key=str(page_state.edit_output_key),
                                )
                            else:
                                me.box(style=me.Style(height="400px", width="400px"))
                            me.box(style=me.Style(height="12px"))

                            me.box(style=me.Style(height="20px"))

                    # Edit controls
                    with me.box(style=_BOX_STYLE):
                        me.textarea(
                            label="prompt for image editing",
                            key=str(page_state.textarea_key),
                            on_blur=on_blur_image_edit_prompt,
                            rows=2,
                            autosize=True,
                            max_rows=5,
                            style=me.Style(width="100%"),
                            value=page_state.edit_prompt_placeholder,
                        )
                        with me.box(
                            style=me.Style(
                                display="flex",
                                justify_content="space-between",
                            ),
                        ):
                            # Clear
                            me.button(
                                "Clear",
                                color="primary",
                                type="stroked",
                                on_click=on_click_clear_images,
                            )
                            # Foreground / Background
                            me.select(
                                label="Foreground / Background",
                                options=[
                                    me.SelectOption(
                                        label="Foreground", value="foreground"
                                    ),
                                    me.SelectOption(
                                        label="Background", value="background"
                                    ),
                                ],
                                key="foreground_background",
                                on_selection_change=on_selection_change_image,
                                value=page_state.foreground_background,
                            )
                            # Editing mode
                            me.select(
                                label="Edit mode",
                                options=[
                                    me.SelectOption(
                                        label="Outpainting",
                                        value="EDIT_MODE_OUTPAINT",
                                    ),
                                    me.SelectOption(
                                        label="Inpainting insert",
                                        value="EDIT_MODE_INPAINT_INSERTION",
                                    ),
                                    me.SelectOption(
                                        label="Inpainting removal",
                                        value="EDIT_MODE_INPAINT_REMOVAL",
                                    ),
                                ],
                                key="edit_mode",
                                on_selection_change=on_selection_change_image_edit_mode,
                                value=page_state.edit_mode,
                            )
                            # Generate
                            me.button(
                                "Generate",
                                color="primary",
                                type="flat",
                                on_click=on_click_image_edit,
                            )


# Event Handlers
def on_click_clear_images(event: me.ClickEvent) -> None:
    """Click Event to clear images."""
    del event
    state = me.state(EditImagesPageState)
    state.prompt_input = ""
    state.prompt_placeholder = ""
    state.upload_file = None
    state.upload_file_key += 1
    state.upload_uri = ""
    state.textarea_key += 1


def on_blur_image_edit_prompt(event: me.InputBlurEvent) -> None:
    """handle image editing prompt"""
    state = me.state(EditImagesPageState)
    state.edit_prompt_placeholder = event.value


async def on_upload(event: me.UploadEvent) -> None:
    """Upload image to GCS.

    Args:
        event: An Upload event.
    """
    state = me.state(EditImagesPageState)
    state.upload_file = None
    state.upload_file = event.file
    contents = event.file.getvalue()
    payload = {
        "bucket_name": config.image_creation_bucket,
        "contents": base64.b64encode(contents).decode("utf-8"),
        "mime_type": event.file.mime_type,
        "file_name": event.file.name,
        "sub_dir": "uploaded",
    }
    try:
        logging.info("Making request with payload %s", payload)
        response = await auth_request.make_authenticated_request(
            method="POST",
            url=f"{config.api_gateway_url}/files/upload",
            json_data=payload,
            service_url=config.api_gateway_url,
        )
        state.upload_uri = await response.json()
        logging.info(
            "Contents len %s of type %s uploaded to %s as %s.",
            len(contents),
            event.file.mime_type,
            config.image_creation_bucket,
            state.upload_uri,
        )
    except Exception as e:
        logging.exception("Something went wrong uploading image: %s", e)


def on_selection_change_image(event: me.SelectSelectionChangeEvent) -> None:
    """Change Event For Selecting an Image Model."""
    state = me.state(EditImagesPageState)
    setattr(state, event.key, event.value)


def on_selection_change_image_edit_mode(event: me.SelectSelectionChangeEvent) -> None:
    """change image edit mode
    Args:
        e (me.SelectSelectionChangeEvent): event
    """
    state = me.state(EditImagesPageState)
    state.edit_mode = event.value


async def send_image_editing_request(state: EditImagesPageState) -> str:
    """event for image editing"""
    payload = {
        "image_uri": state.upload_uri,
        "prompt": state.edit_prompt_placeholder,
        "aspect_ratio": "1:1",
        "number_of_images": 1,
        "edit_mode": state.edit_mode,
        "foreground_background": state.foreground_background,
    }
    logging.info("Making request with payload %s", payload)
    response = await auth_request.make_authenticated_request(
        method="POST",
        url=f"{config.api_gateway_url}/editing/edit_image",
        json_data=payload,
        service_url=config.api_gateway_url,
    )
    try:
        edited_image_uri = await response.json()
        logging.info(edited_image_uri)
        return edited_image_uri
    except Exception as e:
        logging.exception("Something went wrong generating images: %s", e)


async def on_click_image_edit(event: me.ClickEvent) -> AsyncGenerator[Any, Any, Any]:
    """Creates images from Imagen and returns a list of gcs uris."""
    del event  # Unused.
    state = me.state(EditImagesPageState)
    state.edit_uri = ""
    state.edit_output_key += 1
    state.is_loading = True
    yield
    state.edit_uri = await send_image_editing_request(state)
    state.is_loading = False
    yield
