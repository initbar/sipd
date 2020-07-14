# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

from setuptools import find_packages
from setuptools import setup

from sipd.version import VERSION

setup(
    name="sipd",
    packages=find_packages(),
    description="active-recording Session Initiation Protocol daemon",
    url="https://github.com/initbar/sipd",
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
