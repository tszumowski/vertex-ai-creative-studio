import dataclasses
import os

from pages import constants

from dotenv import load_dotenv

load_dotenv(override=True)


@dataclasses.dataclass
class GeminiModelConfig:
    """Configuration specific to Gemini models"""


class AppConfig:
    """All configuration variables for this application are managed here."""

    def __init__(self) -> None:
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
