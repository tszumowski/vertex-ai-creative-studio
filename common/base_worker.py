"""Base Service Worker."""

from __future__ import annotations

import abc
import os
from typing import TYPE_CHECKING, Any

import cloud_detect
import tadau as tadau_lib
from absl import logging

from common.clients import firestore_client_lib

if TYPE_CHECKING:
    from common.models import settings as settings_lib


class BaseWorker(abc.ABC):
    def __init__(
        self,
        settings: settings_lib.Settings,
    ) -> None:
        """Initializes the Google Ads worker.

        Args:
          feed_config: An instance of FeedConfig.
        """
        self.settings = settings
        self.firestore_client = firestore_client_lib.FirestoreClient()
        self.tadau_client = tadau_lib.Tadau(
            api_secret="DV9DIB-zThOVZBOMB0oFUg",
            measurement_id="G-M99NE04QRK",
            opt_in=True,
            fixed_dimensions={
                "deploy_id": f"genmedia_studio_{os.environ.get('PROJECT_ID')}",
                "deploy_infra": cloud_detect.provider(),
            },
        )
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
