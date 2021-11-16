#!/usr/bin/env python3
# tab-width:4

# flake8: noqa           # flake8 has no per file settings :(
# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=C0114  # Missing module docstring (missing-module-docstring)
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement
# pylint: disable=C0305  # Trailing newlines editor should fix automatically, pointless warning
# pylint: disable=C0413  # TEMP isort issue [wrong-import-position] Import "from pathlib import Path" should be placed at the top of the module [C0413]


import glob
import os
import time
from pathlib import Path
from logtool import leprint
from logtool import LOG
from hashtool import hash_str
from pathtool import read_file_bytes
from urltool import extract_domain_set_from_hosts_format_bytes
from urltool import extract_domain_set_from_hosts_format_url
from .global_vars import CACHE_EXPIRE, CACHE_DIRECTORY


class CachedCopyNotFoundError(FileNotFoundError):
    pass


def get_domains_from_url(*,
                         url: str,
                         no_cache: bool = False,
                         cache_expire: int = CACHE_EXPIRE,
                         ) -> set:

    unexpired_copy = get_cached_url_copy(url=url, cache_expire=cache_expire)
    if unexpired_copy:
        leprint("Using cached copy: %s", unexpired_copy, level=LOG['INFO'])
        unexpired_copy_bytes = read_file_bytes(unexpired_copy)
        assert isinstance(unexpired_copy_bytes, bytes)
        return extract_domain_set_from_hosts_format_bytes(unexpired_copy_bytes)

    return extract_domain_set_from_hosts_format_url(url, no_cache)


def generate_cache_file_name(url):
    url_hash = hash_str(url)
    file_name = CACHE_DIRECTORY / Path(url_hash + '_hosts')
    return file_name


def get_cached_url_copy(url: str, *,
                        cache_expire: int = CACHE_EXPIRE,
                        ) -> str:

    newest_copy = get_matching_cached_file(url)
    if newest_copy:
        newest_copy_timestamp = os.stat(newest_copy).st_mtime
        expiration_timestamp = int(newest_copy_timestamp) + int(cache_expire)
        if expiration_timestamp > time.time():
            return newest_copy

        os.rename(newest_copy, newest_copy + '.expired')

    raise CachedCopyNotFoundError(url)


def get_matching_cached_file(url):
    name = generate_cache_file_name(url)
    matching_cached_file = glob.glob(name)
    if matching_cached_file:
        return matching_cached_file[0]
    return False
