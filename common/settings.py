"""Defines the Settings class."""

import dataclasses


@dataclasses.dataclass
class Settings:
    """A class for keeping track of the application settings."""

    username: str = ""
