# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

from argparse import ArgumentParser
from argparse import HelpFormatter
from argparse import Namespace
from multiprocessing import cpu_count
from pathlib import Path
from typing import Dict
from typing import Generic
from typing import Text

import json
import os


def parse_arguments() -> Dict:
    """Parse and return CLI arguments."""

    parser: ArgumentParser = ArgumentParser(
        formatter_class=lambda prog: HelpFormatter(
            prog, max_help_position=30,  # characters
        )
    )

    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        default=False,
        help="print program version and exit",
    )

    server: ArgumentParser = parser.add_argument_group("SIP server arguments")
    server.add_argument(
        "--address",
        metavar="host",
        type=Text,
        default="127.0.0.1",
        help="server listening address (default: '127.0.0.1')",
    )
    server.add_argument(
        "--port",
        metavar="port",
        type=int,
        default=5060,
        help="server listening port (default: 5060)",
    )
    server.add_argument(
        "--worker-count",
        metavar="n",
        type=int,
        default=1,
        help=f"number of worker threads  (default: 1)",
    )

    config: ArgumentParser = parser.add_argument_group("config arguments")
    default_conf_path: Text = os.path.join(os.path.curdir, "config.json")
    config.add_argument(
        "--config",
        metavar="path",
        type=Text,
        default=default_conf_path,
        help=f"configuration file path (default: '{default_conf_path}')",
    )

    args: Namespace = parser.parse_args()
    return vars(args)


class ConfigEntry(object):
    """Configuration entry."""

    def __repr__(self) -> Text:
        # Slotted classes must be repr'd based on the slot entries.
        if hasattr(self, "__slots__"):
            return f"{self.__class__.__name__}(%s)" % (
                ", ".join([
                    f"{k}={repr(getattr(self, k))}"
                    for k in iter(self.__slots__)
                ])
            )
        # Non-slotted classes can be repr'd based on the __dict__.
        return f"{self.__class__.__name__}(%s)" % (
            ", ".join([
                f"{k}={repr(v)}"
                for k, v in iter(self.__dict__.items())
            ])
        )


class Config(ConfigEntry):
    """Configurations."""

    def __init__(self, **kw: Dict):
        """
        Args:
          kw: Dict -- configuration kwargs.
        """
        # CLI configuration values have higher priority than a configuration
        # file's values (if it has been provided through the CLI argument).
        self._cli: Dict = kw
        self._file: Dict = {}

        path: Text = Path(kw.get("config", ""))  # `--config`
        if path.is_file():
            with path.open() as f:
                self._file = json.loads(f.read())

        # Design note: each configurations have been wrapped into a class
        # since a configuration file's key names are susceptible to changes.
        # Although heavy, this will help prevent breaking changes by making
        # backwards-compatibility logic to be handled by each ConfigEntry.
        self.version: bool = self._cli.get("version", False)
        self.logging = Logging(self)
        self.server = Server(self)
        self.sip = Sip(self)
        self.sdp = Sdp(self)


class Logging(ConfigEntry):
    """Logging configuration entries."""

    __slots__ = ("disk", "level")

    def __init__(self, cls):
        logging = cls._file.get("logging", {})
        self.level: Text = logging.get("level", "INFO")
        self.disk: Dict = logging.get(
            "disk",
            {
                "enabled": False,
                "path": os.path.join(os.path.curdir, "sipd.log"),  # ./sipd.log
                "total_days_preserved": 7,
            },
        )


class Server(ConfigEntry):
    """SIP server configuration entries."""

    __slots__ = ("host", "port", "workers")

    def __init__(self, cls):
        server = cls._file.get("server", {})
        self.host: Text = server.get("host", "127.0.0.1")
        self.port: Text = server.get("port", 5060)
        self.workers: Text = server.get("workers", 1)


class Sip(ConfigEntry):
    """SIP configuration entries."""

    __slots__ = ("headers", "version")

    def __init__(self, cls):
        sip = cls._file.get("sip", {})
        self.version: Text = sip.get("version", "2.0")
        self.headers: Dict = sip.get("headers", {})


class Sdp(ConfigEntry):
    """SDP configuration entries."""

    __slots__ = ("headers",)

    def __init__(self, cls):
        sdp = cls._file.get("sdp", {})
        self.headers: Dict = sdp.get("headers", {})
