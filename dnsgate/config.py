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

#import click
#import copy
#import time
#import glob
#import hashlib
#import sys
#import os
#import ast
#import shutil
#import requests
#import pprint
#import configparser
#from shutil import copyfileobj
#import logging
#import string
#from kcl.printops import eprint
#from kcl.printops import LOG
#from kcl.printops import logger_quiet
#from kcl.printops import set_verbose
#from file_headers import *
#from global_vars import *
#from cache import *
#from kcl.stringops import contains_whitespace
#from kcl.stringops import hash_str
#from kcl.byteops import remove_comments_from_bytes
#from kcl.byteops import read_url_bytes
#from kcl.fileops import comment_out_line_in_file
#from kcl.fileops import uncomment_line_in_file
#from kcl.fileops import write_unique_line_to_file
#from kcl.fileops import backup_file_if_exists
#from kcl.fileops import read_file_bytes
#from kcl.fileops import path_exists
#from kcl.symlink import is_broken_symlink
#from kcl.symlink import is_unbroken_symlink
#from kcl.symlink import get_symlink_abs_target
#from kcl.symlink import is_unbroken_symlink_to_target
#from kcl.symlink import create_relative_symlink
#from kcl.domain import *

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

