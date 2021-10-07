#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

import glob
import os
import time
from kcl.logops import leprint
from kcl.logops import LOG
from kcl.stringops import hash_str
from pathtool import read_file_bytes
from kcl.domainops import extract_domain_set_from_hosts_format_bytes
from kcl.domainops import extract_domain_set_from_hosts_format_url
from .global_vars import CACHE_EXPIRE, CACHE_DIRECTORY

def get_domains_from_url(url, no_cache=False, cache_expire=CACHE_EXPIRE):
    unexpired_copy = get_cached_url_copy(url=url, cache_expire=cache_expire)
    if unexpired_copy:
        leprint("Using cached copy: %s", unexpired_copy, level=LOG['INFO'])
        unexpired_copy_bytes = read_file_bytes(unexpired_copy)
        assert isinstance(unexpired_copy_bytes, bytes)
        return extract_domain_set_from_hosts_format_bytes(unexpired_copy_bytes)
    else:
        return extract_domain_set_from_hosts_format_url(url, no_cache)

def generate_cache_file_name(url):
    url_hash = hash_str(url)
    file_name = CACHE_DIRECTORY + '/' + url_hash + '_hosts'
    return file_name

def get_cached_url_copy(url, cache_expire=CACHE_EXPIRE):
    newest_copy = get_matching_cached_file(url)
    if newest_copy:
        newest_copy_timestamp = os.stat(newest_copy).st_mtime
        expiration_timestamp = int(newest_copy_timestamp) + int(cache_expire)
        if expiration_timestamp > time.time():
            return newest_copy
        else:
            os.rename(newest_copy, newest_copy + '.expired')
            return False
    return False

def get_matching_cached_file(url):
    name = generate_cache_file_name(url)
    matching_cached_file = glob.glob(name)
    if matching_cached_file:
        return matching_cached_file[0]
    else:
        return False
