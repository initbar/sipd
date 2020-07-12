# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

from argparse import ArgumentParser
from argparse import HelpFormatter
from multiprocessing import cpu_count
from typing import Dict
from typing import Text

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

    default_conf_path = os.path.join(os.path.curdir, "config.toml")
    config.add_argument(
        "--config",
        metavar="path",
        type=Text,
        default=default_conf_path,
        help=f"configuration file path (default: '{default_conf_path}')",
    )

    args = parser.parse_args()
    return vars(args)


class Config(object):
    """
    """

    def __init__(self, **kw):
        self._kw = kw
