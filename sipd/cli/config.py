# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

from argparse import ArgumentParser
from argparse import HelpFormatter
from multiprocessing import cpu_count
from typing import Dict
from typing import Generic
from typing import Text

import inspect
import json
import os


def parse_arguments() -> Dict:
    """Parse and return CLI arguments."""

    parser = ArgumentParser(
        formatter_class=lambda prog: HelpFormatter(
            prog,
            max_help_position=30,
        )
    )

    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="print program version and exit",
    )

    #
    # server
    #

    server = parser.add_argument_group("server arguments")

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

    #
    # configuration
    #

    config = parser.add_argument_group("config arguments")

    default_conf_path = os.path.join(os.path.curdir, "config.json")
    config.add_argument(
        "--config",
        metavar="path",
        type=Text,
        default=default_conf_path,
        help=f"configuration file path (default: '{default_conf_path}')",
    )

    args = parser.parse_args()
    return vars(args)


class Entry(object):
    """Configuration entry."""

    @classmethod
    def __init__(self, cls):
        ...

    def __repr__(self):
        return f"{self.__class__.__name__}(%s)" % (
            ", ".join([
                f"{k}={repr(v)}" for k, v
                in self.__dict__.items()
            ])
        )


class Config(Entry):
    """
    """

    def __init__(self, **kw):
        self._cli = kw

        conf = kw.get("config")
        if not os.path.isfile(conf):
            self._conf = {}
        else:
            f = open(conf)
            self._conf = json.loads(f.read())
            f.close()

        self.version: bool = self._cli.get("version", False)
        self.project = Project(self)
        self.server = Server(self)
        self.sip = Sip(self)
        self.sdp = Sdp(self)
        self.logging = Logging(self)


class Project(Entry):

    def __init__(self, cls):
        project = cls._conf.get("project", {})
        self.name: Text = project.get("name", "")
        self.description: Text = project.get("description", "")
        self.repository: Text = project.get("repository", "")
        self.MIT: Text = project.get("MIT", "")


class Server(Entry):

    def __init__(self, cls):
        server = cls._conf.get("server", {})
        self.host: Text = server.get("host", "127.0.0.1")
        self.port: Text = server.get("port", 5060)
        self.workers: Text = server.get("workers", 1)


class Sip(Entry):

    def __init__(self, cls):
        sip = cls._conf.get("sip", {})
        self.version: Text = sip.get("version", "2.0")
        self.headers: Dict = sip.get("headers", {})


class Sdp(Entry):

    def __init__(self, cls):
        sdp = cls._conf.get("sdp", {})
        self.headers: Dict = sdp.get("headers", {})


class Logging(Entry):

    def __init__(self, cls):
        logging = cls._conf.get("logging", {})
        self.level: Text = logging.get("level", "INFO")
        self.disk: Dict = logging.get("disk", {})
