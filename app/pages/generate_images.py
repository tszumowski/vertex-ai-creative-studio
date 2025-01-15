from __future__ import annotations

import dataclasses
import json
import secrets
from typing import TYPE_CHECKING, Any

import mesop as me
from absl import logging
from components.header import header
from config import config_lib
from state.state import AppState

from common import api_utils
from pages import constants

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
class PageState:
    """Local Page State"""

    show_advanced: bool = False
    temp_name: str = ""
    is_loading: bool = False

    model: str = config.default_image_model
    image_uris: list[str] = dataclasses.field(default_factory=list)

    # Image prompt and related settings
    prompt_input: str = ""
    prompt_placeholder: str = ""
    textarea_key: int = 0

    negative_prompt_input: str = ""
    negative_prompt_placeholder: str = ""
    negative_prompt_key: int = 0  # Or handle None later

    # Image generation parameters
    add_watermark: bool = True
    seed: int = 0
    num_images: int = 3
    aspect_ratio: str = "1:1"

    # Image style modifiers
    content_type: str = "Photo"
    color_tone: str = "Cool tone"
    lighting: str = "Golden hour"
    composition: str = "Wide angle"


def content(app_state: me.state) -> None:
    """Generate Images Page"""

    page_state = me.state(PageState)
    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="column",
            height="100%",
        ),
    ):
        with me.box(
            style=me.Style(
                background=me.theme_var("background"),
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
                ),
            ):
                header("Generate Images", "stadium")
                # welcome message
                with me.box(
                    style=me.Style(
                        flex_grow=1,
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    on_click=reload_welcome,
                ):
                    me.text(
                        app_state.welcome_message,
                        style=me.Style(
                            width="80vw",
                            font_size="10pt",
                            font_style="italic",
                            color="gray",
                        ),
                    )
                    with me.box(
                        style=me.Style(
                            display="flex",
                            justify_content="space-between",
                        ),
                    ):
                        me.select(
                            label="Imagen version",
                            options=constants.IMAGE_MODEL_OPTIONS,
                            key="model",
                            on_selection_change=modify_state,
                            value=config.default_image_model,
                        )
                    # Prompt
                with me.box(
                    style=me.Style(
                        margin=me.Margin(left="auto", right="auto"),
                        width="min(1024px, 100%)",
                        gap="24px",
                        flex_grow=1,
                        display="flex",
                        flex_wrap="wrap",
                        flex_direction="column",
                    ),
                ):
                    with me.box(style=_BOX_STYLE):
                        me.text(
                            "Prompt for image generation",
                            style=me.Style(font_weight=500),
                        )
                        me.box(style=me.Style(height=16))
                        me.textarea(
                            key=str(page_state.textarea_key),
                            on_blur=on_blur_image_prompt,
                            rows=3,
                            autosize=True,
                            max_rows=10,
                            style=me.Style(width="100%"),
                            value=page_state.prompt_placeholder,
                        )
                        # Prompt buttons
                        me.box(style=me.Style(height=12))
                        with me.box(
                            style=me.Style(
                                display="flex",
                                justify_content="space-between",
                            ),
                        ):
                            me.button(
                                "Clear",
                                color="primary",
                                type="stroked",
                                on_click=on_click_clear_images,
                            )

                            me.button(
                                "Random",
                                color="primary",
                                type="stroked",
                                on_click=get_random_prompt,
                                style=me.Style(color="#1A73E8"),
                            )
                            # prompt rewriter
                            with me.content_button(
                                on_click=print,
                                type="stroked",
                            ):
                                with me.tooltip(message="rewrite prompt with Gemini"):
                                    with me.box(
                                        style=me.Style(
                                            display="flex",
                                            gap=3,
                                            align_items="center",
                                        ),
                                    ):
                                        me.icon("auto_awesome")
                                        me.text("Rewriter")
                            # generate
                            me.button(
                                "Generate",
                                color="primary",
                                type="flat",
                                on_click=generate_images,
                            )

                    # Modifiers
                    with me.box(style=_BOX_STYLE):
                        with me.box(
                            style=me.Style(
                                display="flex",
                                justify_content="space-between",
                                gap=2,
                                width="100%",
                            ),
                        ):
                            if page_state.show_advanced:
                                with me.content_button(
                                    on_click=on_click_advanced_controls,
                                ):
                                    with me.tooltip(message="hide advanced controls"):
                                        with me.box(style=me.Style(display="flex")):
                                            me.icon("expand_less")
                            else:
                                with me.content_button(
                                    on_click=on_click_advanced_controls,
                                ):
                                    with me.tooltip(message="show advanced controls"):
                                        with me.box(style=me.Style(display="flex")):
                                            me.icon("expand_more")

                            # Default Modifiers
                            me.select(
                                label="Aspect Ratio",
                                options=constants.ASPECT_RATIO_OPTIONS,
                                key="aspect_ratio",
                                on_selection_change=modify_state,
                                style=me.Style(width="160px"),
                                value=page_state.aspect_ratio,
                            )
                            me.select(
                                label="Content Type",
                                options=constants.CONTENT_TYPE_OPTIONS,
                                key="content_type",
                                on_selection_change=modify_state,
                                style=me.Style(width="160px"),
                                value=page_state.content_type,
                            )
                            me.select(
                                label="Color & Tone",
                                options=constants.COLOR_AND_TONE_OPTIONS,
                                key="color_tone",
                                on_selection_change=modify_state,
                                style=me.Style(width="160px"),
                                value=page_state.color_tone,
                            )
                            me.select(
                                label="Lighting",
                                options=constants.LIGHTING_OPTIONS,
                                key="lighting",
                                on_selection_change=modify_state,
                                value=page_state.lighting,
                            )
                            me.select(
                                label="Composition",
                                options=constants.COMPOSITION_OPTIONS,
                                key="composition",
                                on_selection_change=modify_state,
                                value=page_state.composition,
                            )
                        # Advanced controls
                        # negative prompt
                        with me.box(
                            style=me.Style(
                                display="flex",
                                flex_direction="row",
                                gap=5,
                            ),
                        ):
                            if page_state.show_advanced:
                                me.box(style=me.Style(width=67))
                                me.input(
                                    label="negative phrases",
                                    on_blur=modify_state,
                                    value=page_state.negative_prompt_placeholder,
                                    key=str(page_state.negative_prompt_key),
                                    style=me.Style(
                                        width="350px",
                                    ),
                                )
                                me.select(
                                    label="number of images",
                                    value="3",
                                    options=constants.NUMBER_OF_IMAGES_OPTIONS,
                                    on_selection_change=modify_state,
                                    key="num_images",
                                    style=me.Style(width="155px"),
                                )
                                me.checkbox(
                                    label="add_watermark",
                                    checked=True,
                                    disabled=True,
                                    key="add_watermark",
                                )
                                me.input(
                                    label="seed",
                                    disabled=True,
                                    key="seed",
                                )

                    # Image output
                    with me.box(style=_BOX_STYLE):
                        me.text("Output", style=me.Style(font_weight=500))
                        if page_state.is_loading:
                            with me.box(
                                style=me.Style(
                                    display="grid",
                                    justify_content="center",
                                    justify_items="center",
                                )
                            ):
                                me.progress_spinner()
                        if len(page_state.image_uris) != 0:
                            with me.box(
                                style=me.Style(
                                    display="grid",
                                    justify_content="center",
                                    justify_items="center",
                                ),
                            ):
                                # Generated images row
                                with me.box(
                                    style=me.Style(
                                        flex_wrap="wrap",
                                        display="flex",
                                        gap="15px",
                                    ),
                                ):
                                    for img in page_state.image_uris:
                                        img_url = img.replace(
                                            "gs://",
                                            "https://storage.mtls.cloud.google.com/",
                                        )
                                        me.image(
                                            src=f"{img_url}",
                                            style=me.Style(
                                                width="300px",
                                                margin=me.Margin(top=10),
                                                border_radius="35px",
                                            ),
                                        )
                                # SynthID notice
                                with me.box(
                                    style=me.Style(
                                        display="flex",
                                        flex_direction="row",
                                        align_items="center",
                                    ),
                                ):
                                    me.text(
                                        text="images watermarked by SynthID",
                                        style=me.Style(
                                            padding=me.Padding.all(10),
                                            font_size="0.95em",
                                        ),
                                    )
                        else:
                            if page_state.is_loading:
                                me.text(
                                    text="generating images!",
                                    style=me.Style(
                                        display="grid",
                                        justify_content="center",
                                        padding=me.Padding.all(20),
                                    ),
                                )
                            else:
                                me.text(
                                    text="generate some images!",
                                    style=me.Style(
                                        display="grid",
                                        justify_content="center",
                                        padding=me.Padding.all(20),
                                    ),
                                )


def on_click_clear_images(event: me.ClickEvent) -> None:
    """Click Event to clear images."""
    del event
    state = me.state(PageState)
    state.prompt_input = ""
    state.prompt_placeholder = ""
    state.image_uris.clear()
    state.negative_prompt_input = ""
    state.textarea_key += 1
    state.negative_prompt_key += 1


# advanced controls
def on_click_advanced_controls(event: me.ClickEvent) -> None:
    """Click Event to toggle advanced controls."""
    del event  # Unused.
    me.state(PageState).show_advanced = not me.state(PageState).show_advanced


def modify_state(
    event: me.SelectSelectionChangeEvent | me.InputBlurEvent,
) -> None:
    state = me.state(PageState)
    setattr(state, event.key, event.value)


def on_blur_image_negative_prompt(event: me.InputBlurEvent) -> None:
    """Image Blur Event"""
    me.state(PageState).negative_prompt_input = event.value


def on_blur_image_prompt(event: me.InputBlurEvent) -> None:
    """Image Blur Event"""
    me.state(PageState).prompt_input = event.value


def reload_welcome(event: me.ClickEvent) -> Generator[Any, Any, Any]:
    """Handle regeneration of welcome message event"""
    del event  # Unused.
    app_state = me.state(AppState)
    app_state.welcome_message = "Hello"
    yield


async def generate_images(event: me.ClickEvent) -> AsyncGenerator[Any, Any, Any]:
    """Creates images from Imagen and returns a list of gcs uris.

    Args:
        model: tbd.
        prompt: tbd.
        num_images: tbd.
        negative_prompt: tbd.
        aspect_ratio: tbd.
        add_watermark: tbd.
        language: tbd.

    Returns:
        A list of strings (gcs uris of image output)
    """
    del event  # Unused.
    state = me.state(PageState)
    state.is_loading = True
    state.image_uris.clear()
    yield
    payload = {
        "model": state.model,
        "prompt": state.prompt_input,
        "num_images": state.num_images,
        "negative_prompt": state.negative_prompt_input,
        "aspect_ratio": state.aspect_ratio,
        "add_watermark": state.add_watermark,
    }
    logging.info("Making request with payload %s", payload)
    response = await api_utils.make_authenticated_request_with_handled_exception(
        method="POST",
        url=f"{config.api_gateway_url}/image_generation/generate_images",
        json_data=payload,
        service_url=config.api_gateway_url,
    )
    try:
        image_uris = await response.json()
        logging.info(image_uris)
        state.image_uris = image_uris
    except Exception as e:
        logging.exception("Something went wrong generating images: %s", e)
    state.is_loading = False
    yield


def on_image_input(event: me.InputEvent) -> None:
    """Image Input Event"""
    state = me.state(PageState)
    state.image_prompt_input = event.value


def get_random_prompt(event: me.ClickEvent) -> Generator[Any, Any, Any]:
    """Gets a random image generation prompt."""
    del event
    state = me.state(PageState)
    # with open("imagen_prompts.json") as file:
    #    data = file.read()
    # prompts = json.loads(data)
    prompt = secrets.choice(["Test1", "Test2"])
    state.prompt_placeholder = prompt
    on_image_input(me.InputEvent(key=str(state.textarea_key), value=prompt))
    yield
