#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common string functions
__version__ = "0.0.1"

import hashlib
import string

def contains_whitespace(s):
    return True in [c in s for c in string.whitespace]


def hash_str(str_to_hash):
    assert isinstance(str_to_hash, str)
    assert len(str_to_hash) > 0
    return hashlib.sha1(str_to_hash.encode('utf-8')).hexdigest()

