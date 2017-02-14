#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

import sys
import os
from .global_vars import *
from .config import dnsmasq_config_file_line

def dnsmasq_install_help(dnsmasq_config_file, output_file=OUTPUT_FILE_PATH):
    config_file_line = dnsmasq_config_file_line()
    print('    $ cp -vi ' + dnsmasq_config_file + ' ' + dnsmasq_config_file +
        '.bak.' + str(time.time()), file=sys.stderr)
    print('    $ grep ' + config_file_line + ' ' + dnsmasq_config_file +
        '|| { echo ' + config_file_line + ' >> dnsmasq_config_file ; }',
        file=sys.stderr)
    print('    $ /etc/init.d/dnsmasq restart', file=sys.stderr)

def hosts_install_help(output_file=OUTPUT_FILE_PATH):
    print('    $ mv -vi /etc/hosts /etc/hosts.default', file=sys.stderr)
    print('    $ cat /etc/hosts.default ' + output_file + ' > /etc/hosts',
        file=sys.stderr)

OUTPUT_FILE_HELP = '(for testing) output file (defaults to ' + OUTPUT_FILE_PATH + ')'
DNSMASQ_CONFIG_HELP = 'dnsmasq config file (defaults to ' + DNSMASQ_CONFIG_FILE + ')'
BACKUP_HELP = 'backup output file before overwriting'
INSTALL_HELP_HELP = 'Help configure dnsmasq or /etc/hosts'
SOURCES_HELP = '''remote blacklist(s) to get rules from. Defaults to:
\b

''' + ' '.join(DEFAULT_REMOTE_BLACKLISTS)
WHITELIST_HELP = '''\b
whitelists(s) defaults to:''' + CUSTOM_WHITELIST.replace(os.path.expanduser('~'), '~')
BLOCK_AT_PSL_HELP = 'strips subdomains, for example: analytics.google.com -> google.com' + \
    ' (must manually whitelist inadvertently blocked domains)'
VERBOSE_HELP = 'print debug information to stderr'
NO_CACHE_HELP = 'do not cache --source files as sha1(url) to ~/.dnsgate/cache/'
CACHE_EXPIRE_HELP = 'seconds until cached remote sources are re-downloaded ' + \
    '(defaults to ' + str(CACHE_EXPIRE / 3600) + ' hours)'
DEST_IP_HELP = 'IP to redirect blocked connections to (defaults to ' + \
    '127.0.0.1 in hosts mode, specifying this in dnsmasq mode causes ' + \
    'lookups to resolve rather than return NXDOMAIN)'
NO_RESTART_DNSMASQ_HELP = 'do not restart the dnsmasq service'
BLACKLIST_HELP = 'Add domain(s) to ' + CUSTOM_BLACKLIST
WHITELIST_HELP = 'Add domain(s) to ' + CUSTOM_WHITELIST
DISABLE_HELP = 'Disable ' + OUTPUT_FILE_PATH
ENABLE_HELP = 'Enable ' + OUTPUT_FILE_PATH
CONFIGURE_HELP = '''Write ''' + CONFIG_FILE + '''
\b

[SOURCES] are the ''' + SOURCES_HELP
GENERATE_HELP = 'Create ' + OUTPUT_FILE_PATH
BLOCKALL_HELP = 'return NXDOMAIN on _ALL_ domains'

