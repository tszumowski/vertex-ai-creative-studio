from __future__ import annotations

import dataclasses
import secrets
from typing import TYPE_CHECKING, Any

import mesop as me
from absl import logging
from components.header import header
from config import config_lib
from icons.svg_icon_component import svg_icon_component
from pages import constants
from state.state import AppState
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
class GenerateImagesPageState:
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

    commentary: str = ""


def content(app_state: me.state) -> None:
    """Generate Images Page"""

    page_state = me.state(GenerateImagesPageState)
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
                            on_selection_change=on_event_modify_state,
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
                                on_click=on_click_generate_random_prompt,
                            )
                            # prompt rewriter
                            with me.content_button(
                                on_click=on_click_rewrite_prompt,
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
                                on_click=on_click_generate_images,
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
                                on_selection_change=on_event_modify_state,
                                style=me.Style(width="160px"),
                                value=page_state.aspect_ratio,
                            )
                            me.select(
                                label="Content Type",
                                options=constants.CONTENT_TYPE_OPTIONS,
                                key="content_type",
                                on_selection_change=on_event_modify_state,
                                style=me.Style(width="160px"),
                                value=page_state.content_type,
                            )
                            me.select(
                                label="Color & Tone",
                                options=constants.COLOR_AND_TONE_OPTIONS,
                                key="color_tone",
                                on_selection_change=on_event_modify_state,
                                style=me.Style(width="160px"),
                                value=page_state.color_tone,
                            )
                            me.select(
                                label="Lighting",
                                options=constants.LIGHTING_OPTIONS,
                                key="lighting",
                                on_selection_change=on_event_modify_state,
                                value=page_state.lighting,
                            )
                            me.select(
                                label="Composition",
                                options=constants.COMPOSITION_OPTIONS,
                                key="composition",
                                on_selection_change=on_event_modify_state,
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
                                    on_blur=on_event_modify_state,
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
                                    on_selection_change=on_event_modify_state,
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
                                ),
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
                                        flex_wrap="wrap", display="flex", gap="15px"
                                    ),
                                ):
                                    for _, img in enumerate(page_state.image_uris):
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
                                svg_icon_component(
                                    svg="""<svg data-icon-name="digitalWatermarkIcon" viewBox="0 0 24 24" width="24" height="24" fill="none" aria-hidden="true" sandboxuid="2"><path fill="#3367D6" d="M12 22c-.117 0-.233-.008-.35-.025-.1-.033-.2-.075-.3-.125-2.467-1.267-4.308-2.833-5.525-4.7C4.608 15.267 4 12.983 4 10.3V6.2c0-.433.117-.825.35-1.175.25-.35.575-.592.975-.725l6-2.15a7.7 7.7 0 00.325-.1c.117-.033.233-.05.35-.05.15 0 .375.05.675.15l6 2.15c.4.133.717.375.95.725.25.333.375.717.375 1.15V10.3c0 2.683-.625 4.967-1.875 6.85-1.233 1.883-3.067 3.45-5.5 4.7-.1.05-.2.092-.3.125-.1.017-.208.025-.325.025zm0-2.075c2.017-1.1 3.517-2.417 4.5-3.95 1-1.55 1.5-3.442 1.5-5.675V6.175l-6-2.15-6 2.15V10.3c0 2.233.492 4.125 1.475 5.675 1 1.55 2.508 2.867 4.525 3.95z" sandboxuid="2"></path><path fill="#3367D6" d="M12 16.275c0-.68-.127-1.314-.383-1.901a4.815 4.815 0 00-1.059-1.557 4.813 4.813 0 00-1.557-1.06 4.716 4.716 0 00-1.9-.382c.68 0 1.313-.128 1.9-.383a4.916 4.916 0 002.616-2.616A4.776 4.776 0 0012 6.475c0 .672.128 1.306.383 1.901a5.07 5.07 0 001.046 1.57 5.07 5.07 0 001.57 1.046 4.776 4.776 0 001.901.383c-.672 0-1.306.128-1.901.383a4.916 4.916 0 00-2.616 2.616A4.716 4.716 0 0012 16.275z" sandboxuid="2"></path></svg>"""
                                )

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

                    # Image commentary
                    if len(page_state.image_uris) != 0:
                        with me.box(style=_BOX_STYLE):
                            with me.box(
                                style=me.Style(
                                    display="flex",
                                    justify_content="space-between",
                                    gap=2,
                                    width="100%",
                                )
                            ):
                                with me.box(
                                    style=me.Style(
                                        flex_wrap="wrap",
                                        display="flex",
                                        flex_direction="row",
                                        # width="85%",
                                        padding=me.Padding.all(10),
                                    )
                                ):
                                    me.icon("assistant")
                                    me.text(
                                        "magazine editor",
                                        style=me.Style(font_weight=500),
                                    )
                                    me.markdown(
                                        text=page_state.commentary,
                                        style=me.Style(padding=me.Padding.all(15)),
                                    )


# Event Handlers
def on_click_clear_images(event: me.ClickEvent) -> None:
    """Click Event to clear images."""
    del event
    state = me.state(GenerateImagesPageState)
    state.prompt_input = ""
    state.prompt_placeholder = ""
    state.image_uris.clear()
    state.negative_prompt_input = ""
    state.textarea_key += 1
    state.negative_prompt_key += 1


def on_click_advanced_controls(event: me.ClickEvent) -> None:
    """Click Event to toggle advanced controls."""
    del event  # Unused.
    me.state(GenerateImagesPageState).show_advanced = not me.state(
        GenerateImagesPageState,
    ).show_advanced


def on_event_modify_state(
    event: me.SelectSelectionChangeEvent | me.InputBlurEvent,
) -> None:
    state = me.state(GenerateImagesPageState)
    setattr(state, event.key, event.value)


def on_blur_image_negative_prompt(event: me.InputBlurEvent) -> None:
    """Image Blur Event"""
    me.state(GenerateImagesPageState).negative_prompt_input = event.value


def on_blur_image_prompt(event: me.InputBlurEvent) -> None:
    """Image Blur Event"""
    me.state(GenerateImagesPageState).prompt_input = event.value


def reload_welcome(event: me.ClickEvent) -> Generator[Any, Any, Any]:
    """Handle regeneration of welcome message event"""
    del event  # Unused.
    app_state = me.state(AppState)
    app_state.welcome_message = "Hello"
    yield


async def on_click_rewrite_prompt(
    event: me.ClickEvent,
) -> None:
    del event  # Unused.
    state = me.state(GenerateImagesPageState)
    if state.prompt_input:
        payload = {
            "prompt": constants.REWRITER_PROMPT.format(prompt=state.prompt_input),
        }
        logging.info("Making request with payload %s", payload)
        response = await auth_request.make_authenticated_request(
            method="POST",
            url=f"{config.api_gateway_url}/generation/generate_text",
            json_data=payload,
            service_url=config.api_gateway_url,
        )
        try:
            rewritten_prompt = await response.json()
            state.prompt_input = rewritten_prompt
            state.prompt_placeholder = rewritten_prompt
        except Exception as e:
            logging.exception("Something went wrong generating text: %s", e)


async def send_image_generation_request(state: GenerateImagesPageState) -> list[str]:
    payload = {
        "model": state.model,
        "prompt": state.prompt_input,
        "num_images": state.num_images,
        "negative_prompt": state.negative_prompt_input,
        "aspect_ratio": state.aspect_ratio,
        "add_watermark": state.add_watermark,
    }
    logging.info("Making request with payload %s", payload)
    response = await auth_request.make_authenticated_request(
        method="POST",
        url=f"{config.api_gateway_url}/generation/generate_images",
        json_data=payload,
        service_url=config.api_gateway_url,
    )
    try:
        image_uris = await response.json()
        logging.info(image_uris)
        return image_uris
    except Exception as e:
        logging.exception("Something went wrong generating images: %s", e)


async def send_image_critic_request(state: GenerateImagesPageState) -> str:
    payload = {
        "prompt": constants.CRITIC_PROMPT.format(prompt=state.prompt_input),
        "media_uris": state.image_uris,
    }
    logging.info("Making request with payload %s", payload)
    response = await auth_request.make_authenticated_request(
        method="POST",
        url=f"{config.api_gateway_url}/generation/generate_text",
        json_data=payload,
        service_url=config.api_gateway_url,
    )
    try:
        text = await response.json()
        logging.info(text)
        return text
    except Exception as e:
        logging.exception("Something went wrong generating images: %s", e)


async def on_click_generate_images(
    event: me.ClickEvent,
) -> AsyncGenerator[Any, Any, Any]:
    """Creates images from Imagen and returns a list of gcs uris."""
    del event  # Unused.
    state = me.state(GenerateImagesPageState)
    state.is_loading = True
    state.image_uris.clear()
    yield
    state.image_uris = await send_image_generation_request(state)
    state.commentary = await send_image_critic_request(state)
    state.is_loading = False
    logging.info(state)
    logging.info(state.is_loading)
    yield


def on_image_input(event: me.InputEvent) -> None:
    """Image Input Event"""
    state = me.state(GenerateImagesPageState)
    state.prompt_input = event.value


def on_click_generate_random_prompt(event: me.ClickEvent) -> Generator[Any, Any, Any]:
    """Gets a random image generation prompt."""
    del event
    state = me.state(GenerateImagesPageState)
    prompt = secrets.choice(constants.RANDOM_PROMPTS)
    state.prompt_placeholder = prompt
    on_image_input(me.InputEvent(key=str(state.textarea_key), value=prompt))
    yield
