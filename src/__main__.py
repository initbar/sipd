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

import sys

from loader import Application
from loader import parse_arguments
from logger import initialize_logger
from version import BRANCH, VERSION


if __name__ == "__main__":

    # enforce minimum Python 3 version.
    if not ((3, 0) <= sys.version_info):
        raise RuntimeError("minimum Python version 3.0 required")

    # parse `-h` and `-v`.
    args = parse_arguments()
    if args.version:
        sys.stderr.write(Application.version)
        sys.exit()

    # TODO: parse configuration.

    logger = initialize_logger(level=("DEBUG" if args.print_debug_logs else "INFO"))
    logger.debug("successfully initialized logger.")

    try:
        if args.print_environment:
            logger.info("app environment: %s", vars(args))
        app = Application(param=args)
        result, benchmark = app.run()
    except KeyboardInterrupt:
        pass
    finally:
        if args.print_benchmark:
            # TODO: benchmark is not always accurate since it also adds
            # `sys.stdout.write` time. I need to either change the start
            # and end or subtract print time from the overall benchmark.
            logger.info("app performance: %s seconds.", benchmark)
