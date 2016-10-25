#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common symlink functions
__version__ = "0.0.1"

import copy
import time
import glob
import hashlib
import sys
import os
import ast
import shutil
import requests
import tldextract
import pprint
import configparser
from shutil import copyfileobj
import logging
import string

def contains_whitespace(s):
    return True in [c in s for c in string.whitespace]


def hash_str(string):
    assert isinstance(string, str)
    assert len(string) > 0
    return hashlib.sha1(string.encode('utf-8')).hexdigest()

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


def group_by_tld(domains):
    eprint('Sorting domains by their subdomain and grouping by TLD.',
        level=LOG['INFO'])
    sorted_output = []
    reversed_domains = []
    for domain in domains:
        rev_domain = domain.split(b'.')
        rev_domain.reverse()
        reversed_domains.append(rev_domain)
    reversed_domains.sort() # sorting a list of lists by the tld
    for rev_domain in reversed_domains:
        rev_domain.reverse()
        sorted_output.append(b'.'.join(rev_domain))
    return sorted_output

def extract_psl_domain(domain):
    dom = TLD_EXTRACT(domain.decode('utf-8'))
    dom = dom.domain + '.' + dom.suffix
    return dom.encode('utf-8')

def strip_to_psl(domains):
    '''This causes ad-serving domains to be blocked at their root domain.
    Otherwise the subdomain can be changed until the --url lists are updated.
    It does not make sense to use this flag if you are generating a /etc/hosts
    format file since the effect would be to block google.com and not
    *.google.com.'''
    eprint('Removing subdomains on %d domains.', len(domains),
        level=LOG['INFO'])
    domains_stripped = set()
    for line in domains:
        line = extract_psl_domain(line)
        domains_stripped.add(line)
    return domains_stripped



def validate_domain_list(domains):
    eprint('Validating %d domains.', len(domains), level=LOG['DEBUG'])
    valid_domains = set([])
    for hostname in domains:
        try:
            hostname = hostname.lower()
            hostname = hostname.decode('utf-8')
            hostname = hostname.encode('idna').decode('ascii')
            valid_domains.add(hostname.encode('utf-8'))
        except Exception as e:
            eprint("WARNING: %s is not a valid domain. Skipping", hostname,
                level=LOG['WARNING'])
    return valid_domains

def extract_domain_from_iri(iri):
    iri_urlparsed  = requests.utils.urlparse(iri)   # https://hg.python.org/cpython/file/tip/Lib/urllib/parse.py
    return iri_urlparsed.netloc


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
