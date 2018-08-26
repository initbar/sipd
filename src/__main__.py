# MIT License
#
# Copyright (c) 2018 Herbert Shin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://github.com/initbar/sipd

"""
__main__.py
-----------
"""

from __future__ import absolute_import

import argparse
import os
import sys
import yaml

from debug.logger import initialize_logger
from version import BRANCH
from version import VERSION

__all__ = ()


def main(args: argparse) -> int:
    """
    """
    with open(args.config) as config_file:
        settings = yaml.safe_load(config_file.read())

    # logger = initialize_logger(settings)
    return


if __name__ == "__main__":

    # enforce minimum Python 3 version.
    if not ((3, 0) <= sys.version_info):
        raise RuntimeError("minimum Python version 3.0 required")

    argsparser = argparse.ArgumentParser()
    n_exec = argsparser.add_argument_group("execution arguments")

    # version: show program's version number and exit.
    argsparser.add_argument("-v", "--version",
                            action="version",
                            version="%s/%s" % (BRANCH, VERSION))

    # config: configuration file path.
    default_configuration = os.path.abspath(os.path.curdir) + "/settings.yaml"
    n_exec.add_argument("-c", "--config",
                        nargs="?",
                        metavar="str",
                        default=default_configuration,
                        help="configuration path (default: %s)" % default_configuration)

    args = argsparser.parse_args()
    try: sys.exit(main(args))
    except KeyboardInterrupt:
        pass
