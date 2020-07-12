# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

from logging.handlers import TimedRotatingFileHandler
from functools import wraps

import logging
import os


LOGGING_FORMAT = " ".join(
    [
        "[%(asctime)-15s]",
        "<<%(threadName)s>>",
        "%(levelname)s",
        "<%(pathname)s:%(funcName)s:%(lineno)s>",
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
def Logger(level, log_to_disk, log_path, log_name, log_days) -> logging:
    """ return customized root logger instance """
    logging.basicConfig(level=level, format=LOGGING_FORMAT)
    logger = logging.getLogger()
    return logger
