# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipping
#
# This source code is licensed under the MIT license.

"""
setup.py
--------
"""

from __future__ import absolute_import
from setuptools import find_packages
from setuptools import setup

from sipping.version import VERSION

setup(
    name="sipping",
    packages=find_packages(),
    description="active-recording Session Initiation Protocol daemon",
    url="https://github.com/initbar/sipping",
    version=VERSION,
    license="MIT",
    author="Herbert Shin",
    author_email="h@init.bar",
    keywords = [
        "active-record",
        "genesys",
        "rtp",
        "rtp-proxy",
        "sip",
        "sip-client",
        "sip-server",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
