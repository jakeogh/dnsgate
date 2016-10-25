#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

import os
import copy
from kcl.fileops import read_file_bytes
from kcl.byteops import remove_comments_from_bytes
from kcl.printops import eprint
from kcl.printops import LOG
from kcl.byteops import read_url_bytes
from global_vars import TLD_EXTRACT

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

def valid_name(domain):
    # RFC 952: https://tools.ietf.org/html/rfc952
    # A "name" (Net, Host, Gateway, or Domain name) is a text string up
    # to 24 characters drawn from the alphabet (A-Z), digits (0-9), minus
    # sign (-), and period (.). Note that periods are only allowed when
    # they serve to delimit components of "domain style names". (See
    # RFC-921, "Domain Name System Implementation Schedule", for
    # background). No blank or space characters are permitted as part of a
    # name. No distinction is made between upper and lower case. The first
    # character must be an alpha character. The last character must not be
    # a minus sign or period.

    # RFC 1123: https://tools.ietf.org/html/rfc1123#page-13
    # The syntax of a legal Internet host name was specified in RFC-952
    # [DNS:4]. One aspect of host name syntax is hereby changed: the
    # restriction on the first character is relaxed to allow either a
    # letter or a digit. Host software MUST support this more liberal
    # syntax.

    # Host software MUST handle host names of up to 63 characters and
    # SHOULD handle host names of up to 255 characters.
    pass

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

def extract_domain_set_from_dnsgate_format_file(dnsgate_file):
    domains = set([])
    dnsgate_file = os.path.abspath(dnsgate_file)
    dnsgate_file_bytes = read_file_bytes(dnsgate_file)
    lines = dnsgate_file_bytes.splitlines()
    for line in lines:
        line = line.strip()
        line = remove_comments_from_bytes(line)
        # ignore leading/trailing .
        line = b'.'.join(list(filter(None, line.split(b'.'))))
        if len(line) > 0:
            domains.add(line)
    return set(domains)


def extract_domain_set_from_hosts_format_bytes(hosts_format_bytes):
    assert isinstance(hosts_format_bytes, bytes)
    domains = set()
    hosts_format_bytes_lines = hosts_format_bytes.split(b'\n')
    for line in hosts_format_bytes_lines:
        line = line.replace(b'\t', b' ')         # expand tabs
        line = b' '.join(line.split())           # collapse whitespace
        line = line.strip()
        line = remove_comments_from_bytes(line)
        if b' ' in line:                         # hosts format
            # get DNS name (the url's are in hosts 0.0.0.0 dom.com format
            line = line.split(b' ')[1]
            # pylint: disable=bad-builtin
            # ignore leading/trailing .
            line = b'.'.join(list(filter(None, line.split(b'.'))))
            # pylint: enable=bad-builtin
            domains.add(line)
    return domains

def extract_domain_set_from_hosts_format_url(url, no_cache=False):
    url_bytes = read_url_bytes(url, no_cache)
    domains = extract_domain_set_from_hosts_format_bytes(url_bytes)
    eprint("Domains in %s:%s", url, len(domains), level=LOG['DEBUG'])
    return domains

def prune_redundant_rules(domains):
    domains_orig = copy.deepcopy(domains) # need to iterate through _orig later
    for domain in domains_orig:
        domain_parts_msb = list(reversed(domain.split(b'.'))) # start with the TLD
        for index in range(len(domain_parts_msb)):
            domain_to_check = b'.'.join(domain_parts_msb[0:index])
            if domain_to_check in domains_orig:
                eprint("removing: %s because it's parent domain: %s is already blocked",
                    domain, domain_to_check, level=LOG['DEBUG'])
                domains.remove(domain)


