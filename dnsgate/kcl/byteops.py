#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common symlink functions
__version__ = "0.0.1"

import requests
from kcl.printops import eprint
from kcl.printops import LOG

def remove_comments_from_bytes(line): #todo check for (assert <=1 line break) multiple linebreaks?
    assert isinstance(line, bytes)
    uncommented_line = b''
    for char in line:
        char = bytes([char])
        if char != b'#':
            uncommented_line += char
        else:
            break
    return uncommented_line

def read_url_bytes(url, no_cache=False):
    eprint("GET: %s", url, level=LOG['DEBUG'])
    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0'
    try:
        raw_url_bytes = requests.get(url, headers={'User-Agent': user_agent},
            allow_redirects=True, stream=False, timeout=15.500).content
    except Exception as e:
        eprint(e, level=LOG['WARNING'])
        return False
    if not no_cache:
        cache_index_file = CACHE_DIRECTORY + '/sha1_index'
        cache_file = generate_cache_file_name(url)
        with open(cache_file, 'xb') as fh:
            fh.write(raw_url_bytes)
        line_to_write = cache_file + ' ' + url + '\n'
        write_unique_line(line_to_write, cache_index_file)

    eprint("Returning %d bytes from %s", len(raw_url_bytes), url, level=LOG['DEBUG'])
    return raw_url_bytes


if __name__ == '__main__':
    quit(0)
