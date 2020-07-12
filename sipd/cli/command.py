# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import Text

from ..version import BRANCH
from ..version import VERSION
from .config import Config


class Application(object, metaclass=ABCMeta):
    """Abstract contract for application classes.

    Design note:
      This ABC class is simply a placeholder for inheritance and type
      checks/validations.  Sipd should inherit from this parent class.
    """

    @abstractproperty
    def version(self) -> Text:
        """Application version."""
        return NotImplemented

    @abstractmethod
    def run(self):
        """Run application logic."""
        raise NotImplementedError


def _run(self):
    """Run application logic."""
    return


class Sipd(Application):
    """Sipd application."""

    __slots__ = "_config",

    def __init__(self, config: Config = None):
        """
        Args:
          config: Config -- Sipd configurations.
        """
        # use default configuration settings if empty.
        self._config: Config = (Config() if config is None else config)

    run = _run

    @property
    @lru_cache(maxsize=1)
    def version(self) -> Text:
        """Application version."""
        v: Text = f"{BRANCH}-v{VERSION}"
        return v

    @property
    def args(self) -> Dict:
        """CLI arguments."""
        return vars(self._config)
