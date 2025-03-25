# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import os

import google.cloud.logging
import mesop as me
from absl import logging
from components.scaffold import page_scaffold
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse
from pages import edit_images, generate_images, history, settings
from pydantic import BaseModel
from state.state import AppState

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()
logging.info("Logging client instantiated.")

app = FastAPI()


class UserInfo(BaseModel):
    email: str | None
    agent: str | None


@app.get("/__/auth/")
def auth_proxy(request: Request) -> RedirectResponse:
    user_agent = request.headers.get("user-agent")
    user_email = request.headers.get("X-Goog-Authenticated-User-Email")
    app.state.user_info = UserInfo(email=user_email, agent=user_agent)
    return RedirectResponse(url="/generate")


@app.get("/")
def home() -> RedirectResponse:
    return RedirectResponse(url="/__/auth/")


def on_load(event: me.LoadEvent) -> None:  # pylint: disable=unused-argument
    """On load event"""
    del event
    state = me.state(AppState)
    state.user_email = app.state.user_info.email if not None else ""
    state.user_agent = app.state.user_info.agent if not None else ""
    if state.theme_mode:
        me.set_theme_mode(state.theme_mode)
    else:
        me.set_theme_mode("system")
    logging.info("AppState on Page Load: %s", state)


@me.page(
    path="/generate",
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
    app_state = me.state(AppState)
    with page_scaffold():  # pylint: disable=not-context-manager
        edit_images.content(app_state=app_state)


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
