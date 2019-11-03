# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipping
#
# This source code is licensed under the MIT license.

"""
sipping.logging
---------------
"""

from __future__ import absolute_import
from logging.handlers import TimedRotatingFileHandler
from six import wraps  # functools.wraps

import logging
import os

LOGGING_FORMAT = " ".join(
    [
        "\u001b[0m[%(asctime)-15s]",
        "<<\u001b[32;1m%(threadName)s\u001b[0m>>",
        "%(levelname)s",
        "<\u001b[36m%(pathname)s\u001b[0m:%(funcName)s:\u001b[31;1m%(lineno)s\u001b[0m>",
        "%(message)s",
    ]
)

LOGGING_FORMATTER = logging.Formatter(LOGGING_FORMAT)


def feature_log_to_disk(func):
    """ attach file logging capability to logger instance """
    @wraps(func)
    def feature(*a, **kw):
        logger = func(*a, **kw)
        log_disk = kw.get("log_to_disk")
        log_path = kw.get("log_path")
        log_name = kw.get("log_name")
        if not kw.get("log_to_disk"):
            return logger

        # resolve log path
        log_path = "".join(
            [os.path.abspath(log_path), ("/" if not log_path.endswith("/") else "")]
        )
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        # add rotating file log handler
        handler = TimedRotatingFileHandler(
            backupCount=kw.get("log_days"),
            filename=log_path + log_name,
            interval=1,
            when="midnight",
        )
        handler.setFormatter(LOGGING_FORMATTER)
        handler.suffix = "%Y%m%d"
        logger.addHandler(handler)
        return logger
    return feature


@feature_log_to_disk
def initialize_logger(level, log_to_disk, log_path, log_name, log_days) -> logging:
    """ return customized root logger instance """
    logging.basicConfig(level=level, format=LOGGING_FORMAT)
    logger = logging.getLogger()
    return logger


__all__ = ["initialize_logger"]
