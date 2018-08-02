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

# -------------------------------------------------------------------------------
# debug.py -- debugging and helper function module.
# -------------------------------------------------------------------------------

from datetime import datetime
from uuid import uuid4 as UUID

import hashlib

# namespace
# -------------------------------------------------------------------------------
# https://tools.ietf.org/html/rfc4122.html

# generate a random UUID string.
create_random_uuid = lambda: UUID().__str__()

# hash
# -------------------------------------------------------------------------------
# https://tools.ietf.org/html/rfc4634

md5sum = lambda plaintext: hashlib.md5(plaintext).hexdigest()
sha1sum = lambda plaintext: hashlib.sha1(plaintext).hexdigest()
sha256sum = lambda plaintext: hashlib.sha256(plaintext).hexdigest()
sha512sum = lambda plaintext: hashlib.sha512(plaintext).hexdigest()

# timestamps
# -------------------------------------------------------------------------------
# https://tools.ietf.org/html/rfc1305


def time_in_ntp():
    now = datetime.utcnow() - datetime(1900, 1, 1, 0, 0, 0)
    ntp = now.seconds + (now.days * 0x15180)  # 24 * 60 ** 2
    return str(ntp)
