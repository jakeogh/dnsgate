#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# "psl domain" is "Public Second Level domain"
# extracted using https://publicsuffix.org/
# essentially this is the first level at which
# the public could register domains for a given TLD.
__version__ = "0.0.1"

from .global_vars import DNSMASQ_CONFIG_INCLUDE_DIRECTORY

class Dnsgate_Config():
    def __init__(self, mode=False, dnsmasq_config_file=None, backup=False,
            no_restart_dnsmasq=False, block_at_psl=False, dest_ip=None,
            sources=None, output=None):
        self.mode = mode
        self.no_restart_dnsmasq = no_restart_dnsmasq
        self.backup = backup
        self.dnsmasq_config_file = dnsmasq_config_file
        self.block_at_psl = block_at_psl
        self.dest_ip = dest_ip
        self.sources = sources
        self.output = output

def generate_dnsmasq_config_file_line():
    return 'conf-dir=' + DNSMASQ_CONFIG_INCLUDE_DIRECTORY

