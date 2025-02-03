import mesop as me
from pages import constants
from state.state import AppState

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


def content(app_state: me.state) -> None:
    """Generate Images Page"""
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
                            "Prompt used by Rewriter.",
                            style=me.Style(font_weight=500),
                        )
                        me.box(style=me.Style(height=16))
                        me.textarea(
                            key="rewriter_prompt",
                            on_blur=on_blur_prompt,
                            rows=3,
                            autosize=True,
                            max_rows=30,
                            style=me.Style(width="100%"),
                            value=app_state.rewriter_prompt_placeholder,
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
                                "Set Rewriter",
                                color="primary",
                                type="flat",
                                on_click=on_click_set_rewriter_prompt,
                            )
                            me.button(
                                "Restore Default",
                                type="stroked",
                                on_click=on_click_restore_rewriter_default,
                            )
                me.box(style=me.Style(height=16))
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
                            "Prompt used by Critic.",
                            style=me.Style(font_weight=500),
                        )
                        me.box(style=me.Style(height=16))
                        me.textarea(
                            key="critic_prompt",
                            on_blur=on_blur_prompt,
                            rows=3,
                            autosize=True,
                            max_rows=30,
                            style=me.Style(width="100%"),
                            value=app_state.critic_prompt_placeholder,
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
                                "Set Critic",
                                color="primary",
                                type="flat",
                                on_click=on_click_set_critic_prompt,
                            )
                            me.button(
                                "Restore Default",
                                type="stroked",
                                on_click=on_click_restore_critic_default,
                            )


def on_blur_prompt(event: me.InputBlurEvent) -> None:
    """Image Blur Event"""
    state = me.state(AppState)
    setattr(state, event.key, event.value)


def on_click_set_rewriter_prompt(event: me.ClickEvent) -> None:
    """Click Event to clear images."""
    del event
    state = me.state(AppState)
    state.rewriter_prompt_placeholder = state.rewriter_prompt
    state.textarea_key += 1


def on_click_set_critic_prompt(event: me.ClickEvent) -> None:
    """Click Event to clear images."""
    del event
    state = me.state(AppState)
    state.critic_prompt_placeholder = state.critic_prompt

    state.textarea_key += 1


def on_click_restore_rewriter_default(event: me.ClickEvent) -> None:
    del event
    state = me.state(AppState)
    state.rewriter_prompt_placeholder = constants.REWRITER_PROMPT.strip()
    state.rewriter_prompt = constants.REWRITER_PROMPT.strip()
    state.textarea_key += 1


def on_click_restore_critic_default(event: me.ClickEvent) -> None:
    del event
    state = me.state(AppState)
    state.critic_prompt_placeholder = constants.CRITIC_PROMPT.strip()
    state.critic_prompt = constants.CRITIC_PROMPT.strip()
    state.textarea_key += 1
