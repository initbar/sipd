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
logger.py
---------
"""

from __future__ import absolute_import
from logging.handlers import TimedRotatingFileHandler

import logging
import os

LOGGING_FORMAT = " ".join(
    [
        u"\u001b[0m[%(asctime)-15s]",
        u"<<\u001b[32;1m%(threadName)s\u001b[0m>>",
        "%(levelname)s",
        u"<\u001b[36m%(pathname)s\u001b[0m:%(funcName)s:\u001b[31;1m%(lineno)s\u001b[0m>",
        "%(message)s",
    ]
)

__all__ = ["initialize_logger"]


def initialize_logger(configuration: dict) -> logging:
    """
    """
    logger = logging.getLogger()

    config = configuration["log"]
    if log_filesystem.get("enabled"):
        log_days = log_filesystem["total_days"]
        log_file = log_filesystem["name"]
        log_path = log_filesystem["path"]
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        if not log_path.endswith("/"):
            log_path += "/"
        log_path += log_file
        fs_handler = TimedRotatingFileHandler(
            log_path,  # log path
            "midnight",  # log rotation time
            1,  # interval
            log_days,
        )
        fs_handler.setFormatter(logging_formatter)
        fs_handler.suffix = "%Y%m%d"
        logger.addHandler(fs_handler)
    else:
        fs_handler = None

    # console
    if log_console.get("enabled"):
        logging.basicConfig(level=log["level"], format=logging_format)

    logger.debug("<main>:successfully initialized logger.")
    return logger
