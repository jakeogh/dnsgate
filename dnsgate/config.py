#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

from typing import Optional

from .global_vars import DNSMASQ_CONFIG_INCLUDE_DIRECTORY


class DnsgateConfig():
    def __init__(self, *,
                 mode: Optional[str] = None,
                 dnsmasq_config_file: Optional[str] = None,
                 backup: bool = False,
                 no_restart_dnsmasq: bool = False,
                 block_at_psl: bool = False,
                 dest_ip: Optional[str] = None,
                 sources=None,
                 output=None,
                 ):
        self.mode = mode
        self.no_restart_dnsmasq = no_restart_dnsmasq
        self.backup = backup
        self.dnsmasq_config_file = dnsmasq_config_file
        self.block_at_psl = block_at_psl
        self.dest_ip = dest_ip
        self.sources = sources
        self.output = output


def dnsmasq_config_file_line():
    return 'conf-dir=' + DNSMASQ_CONFIG_INCLUDE_DIRECTORY.as_posix()
