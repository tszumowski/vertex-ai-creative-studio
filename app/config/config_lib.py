import dataclasses
import os

from dotenv import load_dotenv

load_dotenv(override=True)


@dataclasses.dataclass
class GeminiModelConfig:
    """Configuration specific to Gemini models"""


@dataclasses.dataclass
class AppConfig:
    """All configuration variables for this application are managed here."""

    PROJECT_ID: str = dataclasses.field(
        default_factory=lambda: os.environ.get("PROJECT_ID"),
    )
    PROJECT_NUMBER: str = dataclasses.field(
        default_factory=lambda: os.environ.get("PROJECT_NUMBER"),
    )
    REGION: str = dataclasses.field(
        default_factory=lambda: os.environ.get("REGION", "us-central1"),
    )
    MODEL_GEMINI: str = dataclasses.field(
        default_factory=lambda: os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp"),
    )
    IMAGE_CREATION_BUCKET: str = dataclasses.field(
        default_factory=lambda: os.environ.get("IMAGE_CREATION_BUCKET"),
    )
    MODEL_IMAGEN2: str = "imagegeneration@006"
    MODEL_IMAGEN3_FAST: str = "imagen-3.0-fast-generate-001"
    MODEL_IMAGEN3: str = "imagen-3.0-generate-001"

    API_GATEWAY_URL: str = f"https://api-gateway-{PROJECT_NUMBER}.{REGION}.run.app"
