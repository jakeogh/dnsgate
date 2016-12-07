#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

import tldextract

CACHE_DIRECTORY          = '/var/cache/dnsgate'
OUTPUT_FILE_PATH_NAME    = 'generated_blacklist'
CONFIG_DIRECTORY         = '/etc/dnsgate'
CONFIG_FILE              = CONFIG_DIRECTORY + '/config'
CUSTOM_BLACKLIST         = CONFIG_DIRECTORY + '/blacklist'
CUSTOM_WHITELIST         = CONFIG_DIRECTORY + '/whitelist'
OUTPUT_FILE_PATH         = CONFIG_DIRECTORY + '/' + OUTPUT_FILE_PATH_NAME
TLDEXTRACT_CACHE         = CACHE_DIRECTORY + '/tldextract_cache'

DNSMASQ_CONFIG_INCLUDE_DIRECTORY = '/etc/dnsmasq.d'
DNSMASQ_CONFIG_FILE      = '/etc/dnsmasq.conf'
DNSMASQ_CONFIG_SYMLINK   = DNSMASQ_CONFIG_INCLUDE_DIRECTORY + '/' + \
    OUTPUT_FILE_PATH_NAME
DEFAULT_REMOTE_BLACKLISTS = [
    'http://winhelp2002.mvps.org/hosts.txt',
    'http://someonewhocares.org/hosts/hosts']
ALL_REMOTE_BLACKLISTS = [
    'http://winhelp2002.mvps.org/hosts.txt',
    'http://someonewhocares.org/hosts/hosts',
    'https://adaway.org/hosts.txt',
    'https://raw.githubusercontent.com/StevenBlack/hosts/master/data/StevenBlack/hosts',
    'http://www.malwaredomainlist.com/hostslist/hosts.txt',
    'http://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts;showintro=0']
    # http://hosts-file.net/?s=Download

CACHE_EXPIRE = 3600 * 24 * 2 # 48 hours
TLD_EXTRACT = tldextract.TLDExtract(cache_file=TLDEXTRACT_CACHE)

