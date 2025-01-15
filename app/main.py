from absl import logging
import google.cloud.logging
import mesop as me
from components.scaffold import page_scaffold
from pages import generate_images
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
    security_policy=me.SecurityPolicy(dangerously_disable_trusted_types=True),
)
def generate_images_page() -> None:
    """Main Page"""
    app_state = me.state(AppState)
    with page_scaffold():  # pylint: disable=not-context-manager
        generate_images.content(app_state=app_state)
