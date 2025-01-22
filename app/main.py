import google.cloud.logging
import mesop as me
from absl import logging
from components.scaffold import page_scaffold
from pages import edit_images, generate_images
from state.state import AppState

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()
logging.info("Logging client instantiated.")


def on_load(event: me.LoadEvent) -> None:  # pylint: disable=unused-argument
    """On load event"""
    del event
    state = me.state(AppState)
    if state.theme_mode:
        me.set_theme_mode(state.theme_mode)
    else:
        me.set_theme_mode("system")


@me.page(
    path="/",
    title="Home",
    on_load=on_load,
    security_policy=me.SecurityPolicy(
        allowed_script_srcs=[
            "https://cdn.jsdelivr.net",
        ],
        dangerously_disable_trusted_types=True,
    ),
)
def generate_images_page() -> None:
    """Main Page"""
    app_state = me.state(AppState)
    with page_scaffold():  # pylint: disable=not-context-manager
        generate_images.content(app_state=app_state)


@me.page(
    path="/edit",
    title="Edit",
    on_load=on_load,
    security_policy=me.SecurityPolicy(
        dangerously_disable_trusted_types=True,
        allowed_connect_srcs="https://apis.google.com",
    ),
)
def edit_images_page() -> None:
    """Main Page"""
    with page_scaffold():  # pylint: disable=not-context-manager
        edit_images.content()
