from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import mesop as me
from absl import logging
from config import config_lib
from pydantic.dataclasses import dataclass
from state import state
from utils import auth_request

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

config = config_lib.AppConfig()


@dataclass
class SearchResults:
    vector_distance: float
    worker: str
    media_uri: str
    generation_params: dict[str, Any]


@me.stateclass
class HistoryPageState:
    """Local Page State"""

    is_loading: bool = False
    image_results: str = ""

    input: str = ""


def content(app_state: me.state) -> None:
    app_state = me.state(state.AppState)
    page_state = me.state(HistoryPageState)

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
                with me.card(
                    appearance="outlined",
                    style=me.Style(
                        width="330px",
                    ),
                ):
                    me.image(
                        src=f"{media_url}",
                        style=me.Style(
                            width="300px",
                            margin=me.Margin(top=10),
                            border_radius="35px",
                        ),
                    )
                    with me.card_content():
                        del result["media_uri"]
                        me.markdown(
                            text=format_dict_to_text_nested(result),
                            style=me.Style(text_align="left"),
                        )

                    with me.card_actions(align="end"):
                        me.button(
                            label="Download",
                            on_click=on_click_download,
                            key=f"download_{idx}",
                        )
                        me.button(
                            label="Edit", key=f"edit_{idx}", on_click=on_click_edit
                        )


def on_click_edit(event: me.ClickEvent):
    page_state = me.state(HistoryPageState)
    img_idx = int(event.key.split("_")[1])
    result = json.loads(page_state.image_results)[img_idx]
    media_uri = result.get("media_uri")
    me.navigate("/edit", query_params={"upload_uri": media_uri})


def on_click_download(event: me.ClickEvent):
    page_state = me.state(HistoryPageState)
    img_idx = int(event.key.split("_")[1])
    result = json.loads(page_state.image_results)[img_idx]
    target = result.get("media_uri").replace(
        "gs://",
        "https://storage.mtls.cloud.google.com/",
    )
    me.navigate(target)


def get_logo(state: state.AppState) -> str:
    if state.theme_mode == "dark":
        return "https://images.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png"
    return "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"


def on_blur(event: me.InputBlurEvent) -> None:
    state = me.state(HistoryPageState)
    state.input = ""
    state.input = event.value


async def send_image_search_request(state: HistoryPageState) -> list[str]:
    payload = {
        "search_text": state.input,
    }
    logging.info("Making request with payload %s", payload)
    response = await auth_request.make_authenticated_request(
        method="POST",
        url=f"{config.api_gateway_url}/files/search",
        json_data=payload,
        service_url=config.api_gateway_url,
    )
    try:
        results = await response.json()
        logging.info(results)
        return results
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


def format_nested_dict(input_dict):
    formatted_lines = []
    for key, value in input_dict.items():
        key_str = str(key)
        if isinstance(value, dict):
            formatted_lines.append(f"*{key_str}*\n")  # Indent nested keys
            formatted_lines.extend(
                format_nested_dict(value),
            )  # Recurse for nested dicts
        else:
            if key == "vector_distance":
                value = round(value, 3)
            formatted_lines.append(f"**{key_str}**: {str(value)} \n")
    return formatted_lines


def format_dict_to_text_nested(input_dict):
    return "\n".join(format_nested_dict(input_dict))
