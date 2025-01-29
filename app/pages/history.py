from __future__ import annotations

from dataclasses import field

import mesop as me
from config import config_lib
from state import state

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

TEST_IMAGE_URIS = [
    "https://interactive-examples.mdn.mozilla.net/media/cc0-images/grapefruit-slice-332-332.jpg",
    "https://interactive-examples.mdn.mozilla.net/media/cc0-images/grapefruit-slice-332-332.jpg",
]


@me.stateclass
class HistoryPageState:
    """Local Page State"""

    show_advanced: bool = False
    temp_name: str = ""
    is_loading: bool = False
    image_uris: list[str] = field(default_factory=list)

    input: str = ""


def content(app_state=me.state) -> None:
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
            gap="10px",
        ),
    ):
        if page_state.image_uris:
            render_images()


def render_images(image_uris: list[str] | None = TEST_IMAGE_URIS):
    elements = []
    for image_uri in image_uris:
        elements.append(
            me.image(
                src=image_uri,
                alt="Grapefruit",
                style=me.Style(width="100%"),
            ),
        )


def get_logo(state: state.AppState) -> str:
    if state.theme_mode == "dark":
        return "https://images.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png"
    return "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"


def on_blur(e: me.InputBlurEvent) -> None:
    state = me.state(HistoryPageState)
    state.input = e.value


def on_enter(e: me.InputEnterEvent) -> None:
    state = me.state(HistoryPageState)

    # Make request to search images.
