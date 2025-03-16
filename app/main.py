from __future__ import annotations

import os

import google.cloud.logging
import mesop as me
import requests
from absl import logging
from components.scaffold import page_scaffold
from config import config_lib
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import FileResponse
from pages import edit_images, generate_images, history, settings
from state.state import AppState
from utils import auth_request

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()
logging.info("Logging client instantiated.")

app = FastAPI()
config = config_lib.AppConfig()


@app.get("/userinfo")
def userinfo(request: Request) -> str | None:
    return request.headers.get("X-Goog-Authenticated-User-ID")


@app.get("/download")
async def download(gcs_uri: str):
    payload = {
        "gcs_uri": gcs_uri,
    }
    logging.info("Making request with payload %s", payload)
    response = await auth_request.make_authenticated_request(
        method="POST",
        url=f"{config.api_gateway_url}/files/download",
        json_data=payload,
        service_url=config.api_gateway_url,
    )
    download_url = await response.json()
    return FileResponse(path=download_url)


def on_load(event: me.LoadEvent) -> None:  # pylint: disable=unused-argument
    """On load event"""
    del event
    state = me.state(AppState)
    if state.theme_mode:
        me.set_theme_mode(state.theme_mode)
    else:
        me.set_theme_mode("system")
    try:
        id_token = auth_request.get_id_token(config.app_url)
        headers = {"Authorization": f"Bearer {id_token}"}
        response = requests.get(
            f"{config.app_url}/userinfo",
            headers=headers,
            timeout=10,
        )
        user_info = response.text
        logging.info("User: %s", user_info)
        state.user = user_info
    except Exception as ex:
        logging.exception(ex)


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
        allowed_iframe_parents=["https://google.github.io"],
        allowed_script_srcs=["https://cdn.jsdelivr.net"],
    ),
)
def edit_images_page() -> None:
    """Main Page"""
    with page_scaffold():  # pylint: disable=not-context-manager
        edit_images.content()


@me.page(
    path="/history",
    title="History",
    on_load=on_load,
    security_policy=me.SecurityPolicy(
        dangerously_disable_trusted_types=True,
        allowed_connect_srcs="https://apis.google.com",
        allowed_iframe_parents=["https://google.github.io"],
        allowed_script_srcs=["https://cdn.jsdelivr.net"],
    ),
)
def history_page() -> None:
    """Main Page"""
    app_state = me.state(AppState)
    with page_scaffold():  # pylint: disable=not-context-manager
        history.content(app_state=app_state)


@me.page(
    path="/settings",
    title="Settings",
    on_load=on_load,
    security_policy=me.SecurityPolicy(
        dangerously_disable_trusted_types=True,
        allowed_connect_srcs="https://apis.google.com",
    ),
)
def settings_page() -> None:
    """Main Page"""
    app_state = me.state(AppState)
    with page_scaffold():  # pylint: disable=not-context-manager
        settings.content(app_state=app_state)


app.mount(
    "/",
    WSGIMiddleware(
        me.create_wsgi_app(debug_mode=os.environ.get("DEBUG_MODE", "") == "true"),
    ),
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        reload_includes=["*.py", "*.js"],
        timeout_graceful_shutdown=0,
    )
