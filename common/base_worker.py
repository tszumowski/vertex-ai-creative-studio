"""Base Service Worker."""

from __future__ import annotations

import abc
from typing import Any

from absl import logging


class BaseWorker(abc.ABC):
    def __init__(
        self,
        settings: Any | None = None,  # Needs to be defined.
    ) -> None:
        """Initializes the Google Ads worker.

        Args:
          feed_config: An instance of FeedConfig.
        """
        self.settings = settings
        self._error_msg = ""
        self._warning_msg = ""
        logging.info("Initialized worker: %s.", self.name)

    @abc.abstractmethod
    def execute(
        self,
    ) -> Any:  # Needs to be defined, should return a worker result.
        """Executes the logic.

        Args:
          settings: The user settings, passed in via the UI.

        Returns:
          A summary of results based on the work done by this worker.
        """

    @property
    def name(self) -> str:
        """The name of this worker class."""
        return self.__class__.__name__
