"""Dialog mesop component"""

from typing import Callable

import mesop as me


@me.content_component
def dialog(*, is_open: bool, on_click_background: Callable | None = None):  # pylint: disable=not-context-manager
    """renders a dialog component"""
    with me.box(
        style=me.Style(
            background=(
                "rgba(0, 0, 0, 0.4)"
                if me.theme_brightness() == "light"
                else "rgba(255, 255, 255, 0.4)"
            ),
            display="block" if is_open else "none",
            height="100%",
            width="100%",
            overflow_x="auto",
            overflow_y="auto",
            position="fixed",
            z_index=1000,
        ),
    ):
        with me.box(
            on_click=on_click_background,
            style=me.Style(
                place_items="center",
                display="grid",
                height="50vh",
            ),
        ):
            with me.box(
                style=me.Style(
                    background=me.theme_var("surface-container-lowest"),
                    border_radius=20,
                    box_sizing="content-box",
                    box_shadow=(
                        "0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"
                    ),
                    margin=me.Margin.symmetric(vertical="0", horizontal="auto"),
                    padding=me.Padding.all(20),
                )
            ):
                me.slot()
