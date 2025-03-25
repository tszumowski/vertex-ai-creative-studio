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

import dataclasses
import os

from absl import logging
from dotenv import load_dotenv

load_dotenv(override=True)


@dataclasses.dataclass
class GeminiModelConfig:
    """Configuration specific to Gemini models"""


class AppConfig:
    """All configuration variables for this application are managed here."""

    def __init__(self) -> None:
        self.local_dev = os.environ.get("LOCAL_DEV", "false").lower() == "true"
        self.project_id = os.environ.get("PROJECT_ID")
        self.project_number = os.environ.get("PROJECT_NUMBER")
        self.region = os.environ.get("REGION", "us-central1")
        self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.image_creation_bucket = os.environ.get("IMAGE_CREATION_BUCKET")
        self.api_gateway_url = (
            f"https://genmedia-api-gateway-{self.project_number}.{self.region}.run.app"
        )
        self.app_url = (
            f"https://genmedia-app-{self.project_number}.{self.region}.run.app"
        )
        self.default_image_model = "imagen-3.0-fast-generate-001"
        self.default_editing_model = "imagen-3.0-capability-001"
        if self.local_dev:
            logging.debug("Config: Running in local development mode.")
