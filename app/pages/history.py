from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import mesop as me
from absl import logging
from components.dialog import dialog, dialog_actions
from config import config_lib
from state import state
from utils import auth_request, helpers

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

config = config_lib.AppConfig()

RESULT_ATTRIBUTES = [
    "worker",
    "prompt",
    "model",
    "aspect_ratio",
    "format",
    "width",
    "height",
    "timestamp",
    "username",
]


@me.stateclass
class HistoryPageState:
    """Local Page State"""

    is_loading: bool = False
    is_open: bool = False
    dialog_data: str = ""
    dialog_index: int = 0
    download_content: str = ""
    download_mimetype: str = ""
    download_filename: str = ""
    image_results: str = ""

    input: str = ""


def content(app_state: me.state) -> None:
    app_state = me.state(state.AppState)
    page_state = me.state(HistoryPageState)

    with dialog(
        is_open=page_state.is_open,
        on_click_background=on_click_close_background,
    ):
        with me.box(
            style=me.Style(
                position="fixed",  # Fixed positioning to overlay content
                top="50%",  # Center vertically
                left="50%",  # Center horizontally
                transform="translate(-50%, -50%)",  # Adjust for centering
                width="40%",  # 20% of the viewport width
                min_width="200px",  # Minimum width to prevent it from becoming too small.
                background="white",
                border_radius="8px",
                padding=me.Padding.all(15),
                box_shadow="0 4px 8px rgba(0, 0, 0, 0.2)",  # Subtle shadow
            ),
        ):
            if page_state.dialog_data:
                me.text("Explore Metadata", type="headline-4")
                for element in RESULT_ATTRIBUTES:
                    for key, value in json.loads(page_state.dialog_data).items():
                        if key == element:
                            me.markdown(f"<b>{snake_to_normal(key)}:</b> {value}")
                with dialog_actions():
                    me.button(
                        label="Edit",
                        key=f"edit_{page_state.dialog_index}",
                        on_click=on_click_edit,
                    )
                    with me.content_button():
                        me.html(
                            html=(
                                f'<a href="data:{page_state.download_mimetype};'
                                f'base64,{page_state.download_content}" '
                                f'download="{page_state.download_filename}">Download</a>'
                            ),
                        )
                    me.button("Close", on_click=on_click_close_dialog, type="flat")

    with me.box(
        style=me.Style(
            background=me.theme_var("background"),
            margin=me.Margin.all(75),
            text_align="center",
            display="flex",
            flex_direction="column",
            overflow="auto",
            gap="10px",
        ),
    ):
        me.image(
            src=get_logo(app_state),
            alt="Google",
            style=me.Style(width="200px"),
        )
        me.input(
            label="Search images...",
            value=page_state.input,
            on_blur=on_blur,
            on_enter=on_enter,
            appearance="outline",
            style=me.Style(width="625px"),
        )
    with me.box(
        style=me.Style(
            background=me.theme_var("background"),
            margin=me.Margin.all(15),
            text_align="center",
            display="flex",
            flex_wrap="wrap",
            flex_direction="row",
            gap=15,
        ),
    ):
        if page_state.image_results:
            for idx, result in enumerate(json.loads(page_state.image_results)):
                media_uri = result.get("media_uri")
                media_url = media_uri.replace(
                    "gs://",
                    "https://storage.mtls.cloud.google.com/",
                )
                with me.box(
                    style=me.Style(position="relative", display="inline-block"),
                ):  # the box that contains the image and icon.
                    me.image(
                        src=f"{media_url}",
                        style=me.Style(
                            height="200px",
                            border_radius="10px",
                        ),
                    )
                    with me.content_button(
                        on_click=on_click_dialog_open,
                        type="icon",
                        style=me.Style(
                            position="absolute",
                            top="5px",
                            right="5px",
                            z_index=1,
                            min_width="0px",
                        ),
                        key=f"info_{idx}",
                    ):
                        me.icon(
                            icon="info",
                            style=me.Style(
                                color="primary",
                                background="white",
                                border_radius="100%",
                            ),
                        )


def clear_dialog_data(state: HistoryPageState) -> None:
    state.is_open = False
    state.dialog_data = ""
    state.dialog_index = 0
    state.download_content = ""
    state.download_mimetype = ""
    state.download_filename = ""


def on_click_close_background(e: me.ClickEvent) -> None:
    state = me.state(HistoryPageState)
    if e.is_target:
        clear_dialog_data(state)


def on_click_edit(event: me.ClickEvent) -> Generator[Any, Any, Any]:
    state = me.state(HistoryPageState)
    img_idx = int(event.key.split("_")[1])
    result = json.loads(state.image_results)[img_idx]
    media_uri = result.get("media_uri")
    clear_dialog_data(state)
    yield
    me.navigate("/edit", query_params={"upload_uri": media_uri})
    yield


def get_logo(state: state.AppState) -> str:
    if state.theme_mode == "dark":
        return "https://images.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png"
    return "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"


def on_blur(event: me.InputBlurEvent) -> None:
    state = me.state(HistoryPageState)
    state.input = ""
    state.input = event.value


def on_click_close_dialog(event: me.ClickEvent) -> None:
    del event  # Unused.
    state = me.state(HistoryPageState)
    clear_dialog_data(state)


async def on_click_dialog_open(e: me.ClickEvent) -> None:
    state = me.state(HistoryPageState)
    state.is_open = True
    idx = int(e.key.split("_")[1])
    info = json.loads(state.image_results)[idx]
    state.dialog_data = json.dumps(info)
    state.dialog_index = idx

    image = json.loads(state.image_results)[idx]
    media_uri = image.get("media_uri")
    payload = {
        "gcs_uri": media_uri,
    }
    logging.info("Making request with payload %s", payload)
    if config.local_dev:
        data = helpers.make_local_request("download")
        state.download_content = data["content"]
        state.download_mimetype = data["mimetype"]
        state.download_filename = data["filename"]
        return
    try:
        response = await auth_request.make_authenticated_request(
            method="POST",
            url=f"{config.api_gateway_url}/files/download",
            json_data=payload,
            service_url=config.api_gateway_url,
        )
        data = await response.json()
        state.download_content = data["content"]
        state.download_mimetype = data["mimetype"]
        state.download_filename = data["filename"]
    except Exception as e:
        logging.exception("Something went wrong generating download URL: %s", e)


async def send_image_search_request(state: HistoryPageState) -> list[str]:
    payload = {
        "search_text": state.input,
    }
    logging.info("Making request with payload %s", payload)
    if config.local_dev:
        return helpers.make_local_request("search").get("results")
    try:
        response = await auth_request.make_authenticated_request(
            method="POST",
            url=f"{config.api_gateway_url}/files/search",
            json_data=payload,
            service_url=config.api_gateway_url,
        )
        data = await response.json()
        logging.info("Got response: %s", data)
        return data.get("results")
    except Exception as e:
        logging.exception("Something went wrong generating images: %s", e)


async def on_enter(event: me.InputEnterEvent) -> AsyncGenerator[Any, Any, Any]:
    state = me.state(HistoryPageState)
    state.input = event.value
    state.is_loading = True
    state.image_results = ""
    yield
    results = await send_image_search_request(state)
    state.image_results = json.dumps(results)
    state.is_loading = False
    yield


def snake_to_normal(snake_case_string: str) -> str:
    """Converts a lower_snake_case string to Normal Case.

    Args:
        snake_case_string: The input string in lower_snake_case.

    Returns:
        The string in Normal Case.
    """
    words = snake_case_string.split("_")
    normal_case_words = [word.capitalize() for word in words]
    return " ".join(normal_case_words)
