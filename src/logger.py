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

LOGGING_FORMATTER = logging.Formatter(LOGGING_FORMAT)

__all__ = ["initialize_logger"]


def initialize_logger(configuration: dict) -> logging:
    """ return root logger configured to user definitions.
    @configuration<dict> -- `settings.yaml`
    """
    config = configuration["log"]

    # console logging configuration.
    logging.basicConfig(level=config["level"], format=LOGGING_FORMAT)
    logger = logging.getLogger()

    # disk logging configuration.
    if config["disk"].get("enabled"):
        log_filename = config["disk"]["name"]
        log_preserve_days = config["disk"]["total_days_preserved"]
        log_filepath = config["disk"]["path"]
        if not log_filepath.endswith("/"):
            log_filepath += "/"

        # if the target log file does not exist, safely create one.
        if not os.path.exists(log_filepath):
            os.makedirs(log_filepath)

        # register `TimedRotatingFileHandler` in order to properly rotate old
        # log files and preserve them. All rotations are done at midnight.
        handler = TimedRotatingFileHandler(
            backupCount=log_preserve_days,
            filename=log_filepath + log_filename,
            interval=1,
            when="midnight")
        handler.setFormatter(LOGGING_FORMATTER)
        handler.suffix = "%Y%m%d"
        logger.addHandler(handler)

    return logger
