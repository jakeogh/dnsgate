#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

from pathlib import Path

from urltool import TLD_EXTRACT

CACHE_DIRECTORY          = Path('/var/cache/dnsgate')
OUTPUT_FILE_PATH_NAME    = Path('generated_blacklist')
CONFIG_DIRECTORY         = Path('/etc/dnsgate')
CONFIG_FILE              = CONFIG_DIRECTORY / Path('config')
CUSTOM_BLACKLIST         = CONFIG_DIRECTORY / Path('blacklist')
CUSTOM_WHITELIST         = CONFIG_DIRECTORY / Path('whitelist')
OUTPUT_FILE_PATH         = CONFIG_DIRECTORY / OUTPUT_FILE_PATH_NAME

DNSMASQ_CONFIG_INCLUDE_DIRECTORY = Path('/etc/dnsmasq.d')
DNSMASQ_CONFIG_FILE              = Path('/etc/dnsmasq.conf')
DNSMASQ_CONFIG_SYMLINK           = DNSMASQ_CONFIG_INCLUDE_DIRECTORY / OUTPUT_FILE_PATH_NAME

DEFAULT_REMOTE_BLACKLISTS = [
    'http://winhelp2002.mvps.org/hosts.txt',
    'http://someonewhocares.org/hosts/hosts',
    'https://raw.githubusercontent.com/jmdugan/blocklists/master/corporations/facebook/all',]

ALL_REMOTE_BLACKLISTS = [
    'http://winhelp2002.mvps.org/hosts.txt',
    'http://someonewhocares.org/hosts/hosts',
    'https://adaway.org/hosts.txt',
    'https://raw.githubusercontent.com/StevenBlack/hosts/master/data/StevenBlack/hosts',
    'http://www.malwaredomainlist.com/hostslist/hosts.txt',
    'http://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts;showintro=0',]
    # http://hosts-file.net/?s=Download

CACHE_EXPIRE = 3600 * 24 * 2 # 48 hours
