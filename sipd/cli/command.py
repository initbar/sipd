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
      checks/validations. Sipd should inherit from this parent class.
    """

    @abstractproperty
    def version(self) -> Text:
        """Application version."""
        return NotImplemented

    @abstractmethod
    def run(self) -> Any:
        """Run application logic."""
        raise NotImplementedError


def _run(self):
    """Run application logic."""
    # -v, --version
    if self.config.version:
        print(self.version)
        return

    print(self.config)


class Sipd(Application):
    """Sipd application."""

    __slots__ = ("config",)

    def __init__(self, config: Config = None):
        """
        Args:
          config: Config -- Sipd configurations.
        """
        # Use default configuration values if file is not provided.
        self.config: Config = (Config() if config is None else config)

    def __repr__(self) -> Text:
        return f"{self.__class__.__name__}(version={repr(self.version)})"

    def __eq__(self, cls) -> bool:
        return self.version == cls.version and self.config == cls.config

    @property
    @lru_cache(maxsize=1)
    def version(self) -> Text:
        """Application version."""
        v: Text = f"{BRANCH}-v{VERSION}"
        return v

    # Core application logic has been separated into a function in order
    # to make Sipd variant implementations not be a child of Sipd class.
    run = _run
