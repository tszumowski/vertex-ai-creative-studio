from __future__ import annotations

import base64
import io
from dataclasses import field
from typing import TYPE_CHECKING, Any

import mesop as me
from absl import logging
from components.header import header
from config import config_lib
from pages import constants
from PIL import Image
from utils import auth_request

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

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
    is_loading_segmentation: bool = False
    show_overlay: bool = False

    prompt_input: str = ""
    prompt_placeholder: str = ""
    textarea_key: int = 0

    upload_file: me.UploadedFile = None
    upload_file_key: int = 0
    upload_uri: str = ""
    outpainted_uri: str = ""
    edit_mode: str = "EDIT_MODE_INPAINT_INSERTION"
    edit_mode_placeholder: str = ""

    mask_mode: str = "foreground"
    mask_mode_placeholder = ""
    mask_mode_disabled: bool = False

    edit_uri: str = ""
    mask_uri: str = ""
    overlay_uri: str = ""
    overlay_file_key: int = 0
    mask_prompt: str = ""

    segmentation_classes: list[str] = field(default_factory=list)
    segmentation_classes_disabled: bool = True
    initial_edit_target_height: str = "1024"
    initial_edit_target_width: str = "1024"
    edit_target_height: str = "1024"
    edit_target_width: str = "1024"
    target_aspect_ratio: str = ""
    horizontal_alignment: str = "center"
    vertical_alignment: str = "center"


def content() -> None:
    page_state = me.state(EditImagesPageState)
    if me.query_params.get("upload_uri"):
        page_state.upload_uri = me.query_params.get("upload_uri")
    logging.info("Page loaded with state: %s", page_state)
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
                            gap=35,
                            border_radius=20,
                        ),
                    ):
                        with me.box(style=_BOX_STYLE):
                            me.text("Upload Image", style=me.Style(font_weight="bold"))
                            me.box(style=me.Style(height="12px"))
                            if page_state.is_loading_segmentation:
                                with me.box(
                                    style=me.Style(
                                        align_items="center",
                                        display="flex",
                                        justify_content="center",
                                        position="relative",
                                        top="25%",
                                    ),
                                ):
                                    me.progress_spinner()
                            else:
                                if (
                                    page_state.upload_uri
                                    and not page_state.show_overlay
                                ):
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
                                elif page_state.overlay_uri and page_state.show_overlay:
                                    me.image(
                                        src=page_state.overlay_uri.replace(
                                            "gs://",
                                            "https://storage.mtls.cloud.google.com/",
                                        ),
                                        style=me.Style(
                                            height="400px",
                                            border_radius=12,
                                        ),
                                        key=str(page_state.overlay_file_key),
                                    )
                                else:
                                    me.box(
                                        style=me.Style(height="400px", width="460px"),
                                    )
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
                            if page_state.is_loading:
                                with me.box(
                                    style=me.Style(
                                        align_items="center",
                                        display="flex",
                                        justify_content="center",
                                        position="relative",
                                        top="25%",
                                    ),
                                ):
                                    me.progress_spinner()
                            else:
                                if page_state.edit_uri:
                                    me.image(
                                        src=page_state.edit_uri.replace(
                                            "gs://",
                                            "https://storage.mtls.cloud.google.com/",
                                        ),
                                        style=me.Style(
                                            height="400px",
                                            border_radius=12,
                                            justify_content="center",
                                            display="flex",
                                        ),
                                    )
                                    with me.card_actions(align="end"):
                                        me.button(
                                            label="Download",
                                            on_click=on_click_download,
                                        )
                                        me.button(
                                            label="Edit",
                                            on_click=on_click_edit,
                                        )
                                else:
                                    me.box(
                                        style=me.Style(
                                            height="400px",
                                            width="460px",
                                        ),
                                    )
                                me.box(style=me.Style(height="12px"))
                                me.box(style=me.Style(height="20px"))

                    # Edit controls
                    with me.box(style=_BOX_STYLE):
                        me.text("What do you want to do with this image?")
                        me.select(
                            label="Edit mode",
                            options=constants.EDIT_MODE_OPTIONS,
                            key="edit_mode",
                            on_selection_change=on_selection_change_edit_mode,
                            value=page_state.edit_mode,
                            placeholder=page_state.edit_mode_placeholder,
                        )
                        if page_state.edit_mode == "EDIT_MODE_INPAINT_INSERTION":
                            me.text("Select a zone where to insert.")
                        if page_state.edit_mode == "EDIT_MODE_INPAINT_REMOVAL":
                            me.text("Select object(s) to be removed")
                        with me.box(
                            style=me.Style(
                                background=me.theme_var("background"),
                                border_radius=12,
                                display="inline-flex",
                                flex_direction="row",
                                width="100%",
                                gap="25px",
                                align_content="center",
                                align_self="center",
                            ),
                        ):
                            me.select(
                                label="Mask Mode",
                                options=constants.MASK_MODE_OPTIONS,
                                key="mask_mode",
                                disabled=page_state.mask_mode_disabled,
                                on_selection_change=on_selection_change_mask_mode,
                                value=page_state.mask_mode,
                                placeholder=page_state.mask_mode_placeholder,
                            )
                            if page_state.mask_mode == "prompt":
                                me.textarea(
                                    label="Describe what you want to mask.",
                                    key="mask_prompt",
                                    on_blur=on_blur,
                                    rows=1,
                                    autosize=True,
                                    max_rows=4,
                                    style=me.Style(width="600px"),
                                    value=page_state.prompt_placeholder,
                                )
                            if page_state.mask_mode == "semantic":
                                me.select(
                                    label="Semantic Types",
                                    disabled=page_state.segmentation_classes_disabled,
                                    options=constants.SEMANTIC_TYPES,
                                    key="segmentation_classes",
                                    on_selection_change=on_selection_change_segmentation_classes,
                                    value=page_state.segmentation_classes,
                                    multiple=True,
                                )
                            if (
                                page_state.edit_mode == "EDIT_MODE_OUTPAINT"
                                and page_state.mask_mode != "semantic"
                            ):
                                with me.box(
                                    style=me.Style(
                                        display="flex",
                                        flex_direction="column",
                                    ),
                                ):
                                    me.input(
                                        label="Target Height",
                                        appearance="outline",
                                        value=page_state.edit_target_height,
                                        on_input=on_input,
                                        on_blur=on_blur,
                                        key="edit_target_height",
                                    )
                                    me.input(
                                        label="Target Width",
                                        appearance="outline",
                                        value=page_state.edit_target_width,
                                        on_input=on_input,
                                        on_blur=on_blur,
                                        key="edit_target_width",
                                    )
                                with me.box(
                                    style=me.Style(
                                        display="flex",
                                        flex_direction="column",
                                    ),
                                ):
                                    me.text(
                                        "Or select a new target ratio:",
                                        type="subtitle-2",
                                    )
                                    me.box(style=me.Style(height=5))
                                    me.radio(
                                        on_change=on_change_aspect_ratio,
                                        options=constants.ASPECT_RATIO_RADIO_OPTIONS,
                                        value=page_state.target_aspect_ratio,
                                        color="primary",
                                    )
                                    me.box(style=me.Style(height=15))
                                    me.text(
                                        "Position the original image:",
                                        type="subtitle-2",
                                    )
                                    with me.box(
                                        style=me.Style(
                                            display="flex",
                                            flex_direction="row",
                                            gap=65,
                                            padding=me.Padding(
                                                top=10,
                                                left=10,
                                                right=10,
                                                bottom=10,
                                            ),
                                        ),
                                    ):
                                        me.icon(icon="align_horizontal_left")
                                        me.icon(icon="align_horizontal_center")
                                        me.icon(icon="align_horizontal_right")
                                    me.radio(
                                        on_change=on_change_alignment,
                                        options=constants.HORIZONTAL_ALIGNMENT_RADIO_OPTIONS,
                                        value=page_state.horizontal_alignment,
                                        color="primary",
                                        key="horizontal_alignment",
                                    )
                                    with me.box(
                                        style=me.Style(
                                            display="flex",
                                            flex_direction="row",
                                            gap=65,
                                            padding=me.Padding(
                                                top=10,
                                                left=10,
                                                right=10,
                                                bottom=10,
                                            ),
                                        ),
                                    ):
                                        me.icon(icon="align_vertical_bottom")
                                        me.icon(icon="align_vertical_center")
                                        me.icon(icon="align_vertical_top")
                                    me.radio(
                                        on_change=on_change_alignment,
                                        options=constants.VERTICAL_ALIGNMENT_RADIO_OPTIONS,
                                        value=page_state.vertical_alignment,
                                        color="primary",
                                        key="vertical_alignment",
                                    )
                        with me.box(
                            style=me.Style(
                                display="flex",
                                flex_direction="row",
                                gap=15,
                            ),
                        ):
                            me.button(
                                "Set Zone",
                                color="primary",
                                type="flat",
                                on_click=on_click_image_segmentation,
                            )
                            me.button(
                                "Unset Zone",
                                color="primary",
                                type="raised",
                                on_click=on_click_unset_zone,
                            )
                        me.box(style=me.Style(height="20px"))
                        if page_state.edit_mode in (
                            "EDIT_MODE_INPAINT_INSERTION",
                            "EDIT_MODE_BGSWAP",
                            "EDIT_MODE_OUTPAINT",
                        ):
                            me.textarea(
                                label="Describe what you want to insert in the selected zone.",
                                key="prompt_input",
                                on_blur=on_blur,
                                rows=2,
                                autosize=True,
                                max_rows=5,
                                style=me.Style(width="100%"),
                                value=page_state.prompt_placeholder,
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
                            # Generate
                            me.button(
                                "Generate",
                                color="primary",
                                type="flat",
                                disabled=not page_state.show_overlay,
                                on_click=on_click_image_edit,
                            )


def on_click_edit(event: me.ClickEvent) -> None:
    del event  # Unused.
    page_state = me.state(EditImagesPageState)
    me.navigate("/edit", query_params={"upload_uri": page_state.edit_uri})


def on_click_download(event: me.ClickEvent) -> None:
    del event  # Unused
    page_state = me.state(EditImagesPageState)
    target = page_state.edit_uri.replace(
        "gs://",
        "https://storage.mtls.cloud.google.com/",
    )
    me.navigate(target)


def on_change_alignment(event: me.RadioChangeEvent) -> None:
    state = me.state(EditImagesPageState)
    setattr(state, event.key, event.value)


def on_click_unset_zone(event: me.ClickEvent) -> None:
    del event  # Unused.
    state = me.state(EditImagesPageState)
    state.mask_uri = ""
    state.overlay_uri = ""
    state.overlay_file_key += 1
    state.outpainted_uri = ""
    state.show_overlay = False


async def on_click_image_segmentation(
    event: me.ClickEvent,
) -> AsyncGenerator[Any, Any, Any]:
    """Creates images from Imagen and returns a list of gcs uris."""
    del event  # Unused.
    state = me.state(EditImagesPageState)
    state.is_loading_segmentation = True
    state.show_overlay = False
    state.outpainted_uri = ""
    state.mask_uri = ""
    state.overlay_uri = ""
    state.overlay_file_key += 1
    yield
    mask = await send_image_segmentation_request(state)
    state.mask_uri = mask["mask_uri"]
    state.overlay_uri = mask["overlay_uri"]
    state.outpainted_uri = mask.get("image_uri")
    state.is_loading_segmentation = False
    state.show_overlay = True
    yield


async def send_image_segmentation_request(state: EditImagesPageState) -> str:
    """Event for image segmentation."""
    if not state.upload_uri:
        return None
    payload = {
        "image_uri": state.upload_uri,
        "mode": state.mask_mode,
        "prompt": state.mask_prompt,
        "target_size": _get_target_image_size(state),
        "horizontal_alignment": state.horizontal_alignment,
        "vertical_alignment": state.vertical_alignment,
    }
    logging.info("Making request with payload %s", payload)
    response = await auth_request.make_authenticated_request(
        method="POST",
        url=f"{config.api_gateway_url}/editing/segment_image",
        json_data=payload,
        service_url=config.api_gateway_url,
    )
    try:
        return await response.json()
    except Exception as e:
        logging.exception("Something went wrong segmenting image: %s", e)


def on_change_aspect_ratio(event: me.RadioChangeEvent) -> None:
    state = me.state(EditImagesPageState)
    state.target_aspect_ratio = event.value
    new_aspect_ratio = tuple(int(x) for x in event.value.split(":"))
    new_w = max(
        int(state.initial_edit_target_width),
        round(
            int(state.initial_edit_target_height)
            * (new_aspect_ratio[0] / new_aspect_ratio[1]),
        ),
    )
    new_h = max(
        int(state.initial_edit_target_height),
        round(
            int(state.initial_edit_target_width)
            * (new_aspect_ratio[1] / new_aspect_ratio[0]),
        ),
    )
    state.edit_target_height = str(new_h)
    state.edit_target_width = str(new_w)


def on_input(event: me.InputEvent) -> None:
    state = me.state(EditImagesPageState)
    setattr(state, event.key, event.value)
    state.target_aspect_ratio = ""


def on_blur(event: me.InputBlurEvent) -> None:
    state = me.state(EditImagesPageState)
    setattr(state, event.key, event.value)


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
    state.edit_uri = ""
    state.edit_target_height = ""
    state.edit_target_width = ""
    state.mask_uri = ""
    state.overlay_file_key += 1
    state.overlay_uri = ""


async def on_upload(event: me.UploadEvent) -> None:
    """Upload image to GCS.

    Args:
        event: An Upload event.
    """
    state = me.state(EditImagesPageState)
    state.upload_file = None
    state.upload_file = event.file
    contents = base64.b64encode(event.file.getvalue()).decode("utf-8")
    width, length = get_image_dimensions_from_base64(contents)
    state.initial_edit_target_width, state.initial_edit_target_height = (
        str(width),
        str(length),
    )
    state.edit_target_width, state.edit_target_height = (
        str(width),
        str(length),
    )
    payload = {
        "bucket_name": config.image_creation_bucket,
        "contents": contents,
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


def on_selection_change_edit_mode(
    event: me.SelectSelectionChangeEvent,
) -> Generator[Any, Any, Any]:
    """Change Event For Selecting an Image Model."""
    state = me.state(EditImagesPageState)
    setattr(state, event.key, event.value)
    if state.edit_mode in ("EDIT_MODE_OUTPAINT", "EDIT_MODE_CONTROLLED_EDITING"):
        state.mask_mode = "user_provided"
        state.mask_mode_disabled = True
    elif state.edit_mode == "EDIT_MODE_BGSWAP":
        state.mask_mode = "background"
        state.mask_mode_disabled = True
    elif state.edit_mode == "EDIT_MODE_INPAINT_REMOVAL":
        state.mask_mode_disabled = False
        state.prompt_input = ""
    else:
        state.mask_mode_disabled = False
        state.mask_mode = "foreground"
    state.show_overlay = False
    yield


def on_selection_change_segmentation_classes(
    event: me.SelectSelectionChangeEvent,
) -> Generator[Any, Any, Any]:
    """Change Event For Selecting an Image Model."""
    state = me.state(EditImagesPageState)

    state.segmentation_classes = event.values
    yield
    if len(state.segmentation_classes) > 3:
        state.segmentation_classes.pop()
    yield
    state.mask_prompt = ",".join(state.segmentation_classes)
    yield


def on_selection_change_mask_mode(
    event: me.SelectSelectionChangeEvent,
) -> Generator[Any, Any, Any]:
    state = me.state(EditImagesPageState)
    state.mask_mode = event.value
    state.show_overlay = False

    if event.value == "semantic":
        state.segmentation_classes_disabled = False
    else:
        state.segmentation_classes_disabled = True
        state.segmentation_classes.clear()
    yield


def _get_target_image_size(state: EditImagesPageState) -> tuple[int, int]:
    if state.edit_mode == "EDIT_MODE_OUTPAINT":
        return (int(state.edit_target_width), int(state.edit_target_height))
    return None


async def send_image_editing_request(state: EditImagesPageState) -> str:
    """Event for image editing."""
    image_uri = state.upload_uri
    if state.outpainted_uri and state.edit_mode == "EDIT_MODE_OUTPAINT":
        image_uri = state.outpainted_uri
    payload = {
        "image_uri": image_uri,
        "prompt": state.prompt_input,
        "number_of_images": 1,
        "edit_mode": state.edit_mode,
        "mask_mode": state.mask_mode,
        "mask_uri": state.mask_uri,
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
    state.is_loading = True
    yield
    state.edit_uri = await send_image_editing_request(state)
    state.is_loading = False
    yield


def get_image_dimensions_from_base64(base64_string: str) -> tuple[int, int]:
    """Retrieves the width and height of an image from a base64 encoded string.

    Args:
        base64_string: The base64 encoded image data.

    Returns:
        A tuple (width, height) if successful, or None if an error occurs.
    """
    try:
        # Remove the data URL prefix if it exists.
        if base64_string.startswith("data:image"):
            parts = base64_string.split(",")
            if len(parts) > 1:
                base64_string = parts[1]

        image_data = base64.b64decode(base64_string)
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)
        width, height = img.size
        return width, height
    except Exception as e:
        logging.info(f"App: Error getting image dimensions: {e}")
        return None
