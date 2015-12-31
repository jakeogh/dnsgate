#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# PUBLIC DOMAIN
# http://github.com/jkeogh/dnsgate
__version__ = "0.0.1"

import click
import copy
import time
import glob
import hashlib
import sys
import os
import shutil
import requests
import tldextract
from urllib.parse import urlparse
from shutil import copyfileobj
from logdecorator import logdecorator as ld

if '--debug' not in sys.argv:
    ld.logger.setLevel(ld.LOG_LEVELS['DEBUG'] + 1)  #prevent @ld.log_prefix() on main() from printing when debug is off

# psl_domain is a "Public Second Level Domain" extracted by using https://publicsuffix.org/

NO_CACHE_EXTRACT = tldextract.TLDExtract(cache_file=False)

CONFIG_DIRECTORY = '/etc/dnsgate'
CACHE_DIRECTORY = CONFIG_DIRECTORY + '/cache'
CUSTOM_BLACKLIST = CONFIG_DIRECTORY + '/blacklist'
CUSTOM_WHITELIST = CONFIG_DIRECTORY + '/whitelist'
DEFAULT_OUTPUT_FILE = CONFIG_DIRECTORY + '/generated_blacklist'
DEFAULT_REMOTE_BLACKLIST_SOURCES = ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts']
DEFAULT_CACHE_EXPIRE = 3600*12  #12 hours

def eprint(*args, log_level, **kwargs):
    if click_debug:
        ld.logger.debug(*args, **kwargs)
    else:
        if log_level == ld.LOG_LEVELS['INFO']:
            ld.logger_quiet.info(*args, **kwargs)
        elif log_level >= ld.LOG_LEVELS['WARNING']:
            ld.logger_quiet.warning(*args, **kwargs)

@ld.log_prefix()
def restart_dnsmasq_service():
    if os.path.lexists('/etc/init.d/dnsmasq'):
        ret = os.system('/etc/init.d/dnsmasq restart')
    else:
        ret = os.system('systemctl restart dnsmasq')    # untested
    return True

@ld.log_prefix()
def hash_str(string):
    assert(isinstance(string, str))
    assert len(string) > 0
    return hashlib.sha1(string.encode('utf-8')).hexdigest()

def remove_comments_from_bytes(line):
    assert isinstance(line, bytes)
    uncommented_line = b''
    for char in line:
        char = bytes([char])
        if char != b'#':
            uncommented_line += char
        else:
            break
    return uncommented_line

@ld.log_prefix(show_args=False)
def group_by_tld(domains):
    eprint('sorting domains by their subdomain and grouping by TLD', log_level=ld.LOG_LEVELS['INFO'])
    sorted_output = []
    reversed_domains = []
    for domain in domains:
        rev_domain = domain.split(b'.')
        rev_domain.reverse()
        reversed_domains.append(rev_domain)
    reversed_domains.sort() #sorting a list of lists by the tld
    for rev_domain in reversed_domains:
        rev_domain.reverse()
        sorted_output.append(b'.'.join(rev_domain))
    return sorted_output

def extract_psl_domain(domain):
    dom = NO_CACHE_EXTRACT(domain.decode('utf-8'))  #prevent tldextract cache update error when run as a normal user
    dom = dom.domain + '.' + dom.suffix
    return dom.encode('utf-8')

@ld.log_prefix(show_args=False)
def strip_to_psl(domains):
    '''This causes ad-serving domains to be blocked at their TLD.
    Otherwise the subdomain can be changed until the --url lists are updated.
    It does not make sense to use this flag if you are generating a /etc/hosts
    format file since the effect would be to block google.com and not
    *.google.com.'''
    eprint('removing subdomains on %d domains', len(domains), log_level=ld.LOG_LEVELS['INFO'])
    domains_stripped = set()
    for line in domains:
        line = extract_psl_domain(line)             # get tld
        domains_stripped.add(line)
    return domains_stripped

@ld.log_prefix()
def write_unique_line(line, file):
    with open(file, 'r+') as fh:
        if line not in fh:
            fh.write(line)

@ld.log_prefix()
def backup_file_if_exists(file):
    timestamp = str(time.time())
    dest_file = file + '.bak.' + timestamp
    try:
        with open(file, 'r') as sf:
            with open(dest_file, 'x') as df:
                copyfileobj(sf, df)
    except FileNotFoundError:
        pass    # skip backup is file does not exist

@ld.log_prefix(show_args=False)
def validate_domain_list(domains):
    eprint('validating %d domains', len(domains), log_level=ld.LOG_LEVELS['INFO'])
    valid_domains = set([])
    for hostname in domains:
        try:
            hostname = hostname.decode('utf-8')
            hostname = hostname.encode('idna').decode('ascii')
            valid_domains.add(hostname.encode('utf-8'))
        except Exception as e:
            ld.logger.exception(e)
    return valid_domains

def dnsmasq_install_help(output_file):
    dnsmasq_config_line = '\"conf-file=' + output_file + '\"'
    print('    $ cp -vi /etc/dnsmasq.conf /etc/dnsmasq.conf.bak.' + str(time.time()), file=sys.stderr)
    print('    $ grep ' + dnsmasq_config_line + ' /etc/dnsmasq.conf || { echo '
    + dnsmasq_config_line + ' >> /etc/dnsmasq.conf ; }', file=sys.stderr)
    print('    $ /etc/init.d/dnsmasq restart', file=sys.stderr)
    quit(0)

def hosts_install_help(output_file):
    print('    $ mv -vi /etc/hosts /etc/hosts.default', file=sys.stderr)
    print('    $ cat /etc/hosts.default ' + output_file + ' > /etc/hosts', file=sys.stderr)
    quit(0)

# idn='☃.net'
@ld.log_prefix()
def custom_list_append(domain_file, domain):
    eprint("attempting to append %s to %s", domain, domain_file, log_level=ld.LOG_LEVELS['INFO'])
    idn = domain
    eprint("idn: %s", idn, log_level=ld.LOG_LEVELS['DEBUG'])
    hostname = idn.encode('idna').decode('ascii')
    eprint("appending hostname: %s to %s", hostname, domain_file, log_level=ld.LOG_LEVELS['DEBUG'])
    line = hostname + '\n'
    write_unique_line(line, domain_file)

#todo add check for tld domain blocks

@ld.log_prefix()
def extract_domain_set_from_dnsgate_format_file(dnsgate_file):
    domains = set([])
    dnsgate_file = os.path.abspath(dnsgate_file)
    try:
        dnsgate_file_bytes = read_file_bytes(dnsgate_file)
    except Exception as e:
        ld.logger.exception(e)
    else:
        lines = dnsgate_file_bytes.splitlines()
        for line in lines:
            line = line.strip()
            line = remove_comments_from_bytes(line)
            line = b'.'.join(list(filter(None, line.split(b'.')))) # ignore leading/trailing .
            if len(line) > 0:
                domains.add(line)
    return set(domains)

@ld.log_prefix()
def read_file_bytes(file):
    if os.path.isfile(file):
        with open(file, 'rb') as fh:
            file_bytes = fh.read()
        return file_bytes
    else:
        raise FileNotFoundError(file + ' does not exist.')

@ld.log_prefix()
def extract_domain_set_from_hosts_format_url_or_cached_copy(url, cache=False):
    unexpired_copy = get_newest_unexpired_cached_url_copy(url)
    if unexpired_copy:
        eprint("using cached copy: %s", unexpired_copy, log_level=ld.LOG_LEVELS['INFO'])
        unexpired_copy_bytes = read_file_bytes(unexpired_copy)
        assert isinstance(unexpired_copy_bytes, bytes)
        return extract_domain_set_from_hosts_format_bytes(unexpired_copy_bytes)
    else:
        return extract_domain_set_from_hosts_format_url(url, cache)

@ld.log_prefix()
def extract_domain_set_from_hosts_format_url(url, cache=False):
    url_bytes = read_url_bytes(url, cache)
    domains = extract_domain_set_from_hosts_format_bytes(url_bytes)
    eprint("domains in %s:%s", url, len(domains), log_level=ld.LOG_LEVELS['DEBUG'])
    return domains

@ld.log_prefix()
def generate_cache_file_name(url):
    url_hash = hash_str(url)
    file_name = CACHE_DIRECTORY + '/' + url_hash + '_hosts.' + str(time.time())
    return file_name

@ld.log_prefix()
def get_newest_cached_url_copy(url):
    matches = get_matching_cached_files(url)
    try:
        return sorted(matches, key = lambda x: int(x.split(".")[1]))[-1]
    except IndexError:
        return False

@ld.log_prefix()
def get_newest_unexpired_cached_url_copy(url):
    newest_copy = get_newest_cached_url_copy(url)
    if newest_copy:
        newest_copy_timestamp = newest_copy.split('.')[-2:-1][0]
        expiration_timestamp = int(newest_copy_timestamp) + int(click_cache_expire)
        if expiration_timestamp > time.time():
            return newest_copy
        else:
            return False
    return False

@ld.log_prefix()
def get_matching_cached_files(url):
    to_glob = generate_cache_file_name(url).split('.')[0]
    to_glob = to_glob + '*'
    #print(to_glob)
    return glob.glob(to_glob)

@ld.log_prefix()
def read_url_bytes(url, cache=False):
    eprint("GET: %s", url, log_level=ld.LOG_LEVELS['DEBUG'])
    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0'
    try:
        raw_url_bytes = requests.get(url, headers={'User-Agent': user_agent}, allow_redirects=True,
                        stream=False, timeout=15.500).content
    except Exception as e:
        ld.logger.exception(e)
        return False
    if cache:
        output_file = generate_cache_file_name(url)
        if not os.path.isdir(CACHE_DIRECTORY):
            os.makedirs(CACHE_DIRECTORY)
        with open(output_file, 'xb') as fh:
            fh.write(raw_url_bytes)

    eprint("returning %d bytes from %s", len(raw_url_bytes), url, log_level=ld.LOG_LEVELS['DEBUG'])
    return raw_url_bytes

@ld.log_prefix(show_args=False)
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
            line = line.split(b' ')[1]           # get DNS name (the url's are in hosts 0.0.0.0 dom.com format)
            # pylint: disable=bad-builtin
            line = b'.'.join(list(filter(None, line.split(b'.'))))    # ignore leading/trailing .
            # pylint: enable=bad-builtin
            domains.add(line)
    return domains

OUTPUT_FILE_HELP = '''output file defaults to ''' + DEFAULT_OUTPUT_FILE
NOCLOBBER_HELP = '''do not overwrite existing output file'''
BACKUP_HELP = '''backup output file before overwriting'''
INSTALL_HELP_HELP = '''show commands to configure dnsmasq or /etc/hosts (note: this does nothing else)'''
BLACKLIST_HELP = '''\b
blacklist(s) defaults to:
''' + '\n'.join(['    {0}'.format(i) for i in DEFAULT_REMOTE_BLACKLIST_SOURCES])

WHITELIST_HELP = '''\b
whitelists(s) defaults to:''' + CUSTOM_WHITELIST.replace(os.path.expanduser('~'), '~')
BLOCK_AT_PSL_HELP = '''
\b
strips subdomains, for example:
    analytics.google.com -> google.com
    Useful for dnsmasq if you are willing to maintain a --whitelist file
    for inadvertently blocked domains.'''
DEBUG_HELP = '''print debugging information to stderr'''
VERBOSE_HELP = '''print more information to stderr'''
SHOW_CONFIG_HELP = '''print config information to stderr'''
CACHE_HELP = '''cache --url files as dnsgate_cache_domain_hosts.(timestamp) to ~/.dnsgate/cache'''
CACHE_EXPIRE_HELP = '''seconds until a cached remote file is re-downloaded'''
DEST_IP_HELP = '''IP to redirect blocked connections to (defaults to 127.0.0.1)'''
RESTART_DNSMASQ_HELP = '''Restart dnsmasq service (defaults to True, ignored if --mode hosts)'''
BLACKLIST_APPEND_HELP = '''Add domain to ''' + CUSTOM_BLACKLIST
WHITELIST_APPEND_HELP = '''Add domain to ''' + CUSTOM_WHITELIST

#https://github.com/mitsuhiko/click/issues/441
CONTEXT_SETTINGS = dict(help_option_names=['--help'], terminal_width=shutil.get_terminal_size((80, 20)).columns)
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--mode',             is_flag=False, type=click.Choice(['dnsmasq', 'hosts']), default='dnsmasq')
@click.option('--block-at-psl',     is_flag=True,  help=BLOCK_AT_PSL_HELP)
@click.option('--restart-dnsmasq',  is_flag=True,  help=RESTART_DNSMASQ_HELP, default=True)
@click.option('--output-file',      is_flag=False, help=OUTPUT_FILE_HELP,     default=DEFAULT_OUTPUT_FILE)
@click.option('--backup',           is_flag=True,  help=BACKUP_HELP)
@click.option('--noclobber',        is_flag=True,  help=NOCLOBBER_HELP)
@click.option('--blacklist-append', is_flag=False, help=BLACKLIST_APPEND_HELP, type=str)
@click.option('--whitelist-append', is_flag=False, help=WHITELIST_APPEND_HELP, type=str)
@click.option('--blacklist',        is_flag=False, help=BLACKLIST_HELP, default=DEFAULT_REMOTE_BLACKLIST_SOURCES)
@click.option('--cache',            is_flag=True,  help=CACHE_HELP)
@click.option('--cache-expire',     is_flag=False, help=CACHE_EXPIRE_HELP, type=int, default=DEFAULT_CACHE_EXPIRE)
@click.option('--dest-ip',          is_flag=False, help=DEST_IP_HELP)
@click.option('--show-config',      is_flag=True,  help=SHOW_CONFIG_HELP)
@click.option('--install-help',     is_flag=True,  help=INSTALL_HELP_HELP)
@click.option('--debug',            is_flag=True,  help=DEBUG_HELP)
@click.option('--verbose',          is_flag=True,  help=VERBOSE_HELP)
@ld.log_prefix()
def dnsgate(mode, block_at_psl, restart_dnsmasq, output_file, backup, noclobber,
            blacklist_append, whitelist_append, blacklist, cache, cache_expire,
            dest_ip, show_config, install_help, debug, verbose):

    if show_config:
        print("mode:", mode)
        print("block_at_psl:", block_at_psl)
        print("restart_dnsmasq:", restart_dnsmasq)
        print("output_file:", output_file)
        print("backup:", backup)
        print("noclobber:", noclobber)
        print("blacklist_append:", blacklist_append)
        print("whitelist_append:", whitelist_append)
        print("blacklist:", blacklist)
        print("cache:", cache)
        print("dest_ip:", dest_ip)
        print("debug:", debug)
        print("show_config:", show_config)
        print("install_help:", install_help)
        print("debug:", debug)
        print("verbose:", verbose)

    global click_cache_expire
    click_cache_expire = cache_expire

    global click_debug
    click_debug = debug

    if not verbose and not debug:
        ld.logger.setLevel(ld.LOG_LEVELS['DEBUG'] + 1)
        ld.logger_quiet.setLevel(ld.LOG_LEVELS['INFO'] + 1)

    if verbose and not debug:
        ld.logger_quiet.setLevel(ld.LOG_LEVELS['INFO'])

    if debug:
        ld.logger.setLevel(ld.LOG_LEVELS['DEBUG'])
    else:
        ld.logger.setLevel(ld.LOG_LEVELS['INFO'])

    if output_file == '-' or output_file == '/dev/stdout':
        output_file = '/dev/stdout'
    else:
        eprint("using non standard output_file", log_level=ld.LOG_LEVELS['DEBUG'])
        output_file = os.path.abspath(output_file)

    if os.path.isfile(output_file) and output_file != '/dev/stdout':
        if noclobber:
            ld.logger.error("File '%s' exists. Refusing to overwrite because --noclobber was used. Exiting.",
                output_file)
            quit(1)

    eprint('using output_file: %s', output_file, log_level=ld.LOG_LEVELS['INFO'])

    if install_help:
        if mode == 'dnsmasq':
            dnsmasq_install_help(output_file)
        elif mode == 'hosts':
            hosts_install_help(output_file)

    if whitelist_append:
        custom_list_append(CUSTOM_WHITELIST, whitelist_append)

    if blacklist_append:
        custom_list_append(CUSTOM_BLACKLIST, blacklist_append)

    domains_whitelist = set()
    eprint("reading whitelist: %s", str(CUSTOM_WHITELIST), log_level=ld.LOG_LEVELS['INFO'])
    whitelist_file = os.path.abspath(CUSTOM_WHITELIST)
    domains_whitelist = domains_whitelist | extract_domain_set_from_dnsgate_format_file(whitelist_file)
    if domains_whitelist:
        eprint("%d unique domains from the whitelist", len(domains_whitelist), log_level=ld.LOG_LEVELS['INFO'])
        domains_whitelist = validate_domain_list(domains_whitelist)
        eprint('%d validated whitelist domains', len(domains_whitelist), log_level=ld.LOG_LEVELS['INFO'])

    domains_combined_orig = set()   # domains from all sources, combined
    eprint("reading remote blacklist(s): %s", str(blacklist), log_level=ld.LOG_LEVELS['INFO'])
    for item in blacklist:
        if item.startswith('http'):
            try:
                eprint("trying http:// blacklist location: %s", item, log_level=ld.LOG_LEVELS['DEBUG'])
                domains = extract_domain_set_from_hosts_format_url_or_cached_copy(item, cache)
                if domains:
                    domains_combined_orig = domains_combined_orig | domains # union
                    eprint("len(domains_combined_orig): %s",
                        len(domains_combined_orig), log_level=ld.LOG_LEVELS['DEBUG'])
                else:
                    ld.logger.error('failed to get %s, skipping.', item)
                    continue
            except Exception as e:
                ld.logger.error("Exception on blacklist url: %s", item)
                ld.logger.exception(e)
        else:
            ld.logger.error("%s must start with http:// or https://, skipping.", item)
            pass

    eprint("%d unique domains from the remote blacklist(s)",
        len(domains_combined_orig), log_level=ld.LOG_LEVELS['INFO'])

    domains_combined_orig = validate_domain_list(domains_combined_orig)
    eprint('%d validated remote blacklisted domains', len(domains_combined_orig), log_level=ld.LOG_LEVELS['INFO'])

    domains_combined = copy.deepcopy(domains_combined_orig) # need to iterate through _orig later

    if block_at_psl:
        domains_combined = strip_to_psl(domains_combined)
        eprint("%d blacklisted unique domains left after stripping to PSL domains",
                len(domains_combined), log_level=ld.LOG_LEVELS['INFO'])

        eprint("subtracting %d explicitely whitelisted domains so not explicitely whitelisted subdomains" +
                " that existed (and were blocked) before the subdomain stripping can be re-added",
                len(domains_whitelist), log_level=ld.LOG_LEVELS['INFO'])
        domains_combined = domains_combined - domains_whitelist
        eprint("%d unique blacklisted domains left after subtracting the whitelist",
                len(domains_combined), log_level=ld.LOG_LEVELS['INFO'])

        eprint('iterating through the original %d whitelisted domains and making sure none are blocked by' +
                ' * rules', len(domains_whitelist), log_level=ld.LOG_LEVELS['INFO'])

        for domain in domains_whitelist:
            domain_psl = extract_psl_domain(domain)
            if domain_psl in domains_combined:
                domains_combined.remove(domain_psl)

        eprint('iterating through the original %d blacklisted domains and re-adding subdomains' +
                ' that are not whitelisted', len(domains_combined_orig), log_level=ld.LOG_LEVELS['INFO'])
        # re-add subdomains that are not explicitly whitelisted or already blocked
        for orig_domain in domains_combined_orig: # check every original full hostname
            if orig_domain not in domains_whitelist: # if it's not in the whitelist
                if orig_domain not in domains_combined: # and it's not in the current blacklist
                                                        # (almost none will be if --block-at-psl)
                    orig_domain_psl = extract_psl_domain(orig_domain) # get it's psl to see if it's
                                                                      # already blocked by a dnsmasq * rule

                    if orig_domain_psl not in domains_combined: # if the psl is not already blocked
                        eprint("re-adding: %s", orig_domain, log_level=ld.LOG_LEVELS['DEBUG'])
                        domains_combined.add(orig_domain) # add the full hostname to the blacklist

        eprint("%d unique blacklisted domains after re-adding non-explicitely blacklisted subdomains",
                len(domains_combined), log_level=ld.LOG_LEVELS['INFO'])

    # apply whitelist before applying local blacklist
    domains_combined = domains_combined - domains_whitelist  # remove exact whitelist matches
    eprint("%d unique blacklisted domains after subtracting the %d whitelisted domains",
            len(domains_combined), len(domains_whitelist), log_level=ld.LOG_LEVELS['INFO'])

    # must happen after subdomain stripping and after whitelist subtraction
    blacklist_file = os.path.abspath(CUSTOM_BLACKLIST)
    domains = extract_domain_set_from_dnsgate_format_file(blacklist_file)
    if domains:
        eprint("got %s domains from the CUSTOM_BLACKLIST: %s",
            domains, blacklist_file, log_level=ld.LOG_LEVELS['DEBUG'])
        eprint("re-adding %d domains in the local blacklist %s to override the whitelist",
            len(domains), CUSTOM_BLACKLIST, log_level=ld.LOG_LEVELS['INFO'])
        domains_combined = domains_combined | domains # union
    eprint("%d unique blacklisted domains after re-adding the custom blacklist",
        len(domains_combined), log_level=ld.LOG_LEVELS['INFO'])

    eprint("validating final domain block list", log_level=ld.LOG_LEVELS['INFO'])
    domains_combined = validate_domain_list(domains_combined)
    eprint('%d validated blacklisted domains', len(domains_combined), log_level=ld.LOG_LEVELS['INFO'])

    domains_combined = group_by_tld(domains_combined) # do last, returns sorted list
    eprint('final blacklisted domain count: %d', len(domains_combined), log_level=ld.LOG_LEVELS['INFO'])

    if backup:
        backup_file_if_exists(output_file)

    try:
        os.mkdir(CONFIG_DIRECTORY)
    except FileExistsError:
        pass

    if not domains_combined:
        logger.error("the list of domains to block is empty, nothing further to do, exiting.")
        quit(1)

    for domain in domains_whitelist:
        domain_tld = extract_psl_domain(domain)
        if domain_tld in domains_combined:
            eprint('%s is listed in both %s and %s, the local blacklist always takes precedence.',
                domain.decode('UTF8'), CUSTOM_BLACKLIST, CUSTOM_WHITELIST, log_level=ld.LOG_LEVELS['WARNING'])


    eprint("writing output file: %s in %s format", output_file, mode, log_level=ld.LOG_LEVELS['INFO'])
    try:
        with open(output_file, 'wb') as fh:
            for domain in domains_combined:
                if mode == 'dnsmasq':
                    if dest_ip:
                        dnsmasq_line = b'address=/.' + domain + b'/' + dest_ip + b'\n'
                    else:
                        dnsmasq_line = b'server=/.' + domain + b'/' b'\n'  #return NXDOMAIN
                    fh.write(dnsmasq_line)
                elif mode == 'hosts':
                    if dest_ip:
                        hosts_line = dest_ip + b' ' + domain + b'\n'
                    else:
                        hosts_line = b'127.0.0.1' + b' ' + domain + b'\n'
    except PermissionError as e:
        ld.logger.error(e)
        ld.logger.error("root permissions are reqired to write to %s", output_file)
        quit(1)

    if restart_dnsmasq:
        if mode != 'hosts':
            restart_dnsmasq_service()

if __name__ == '__main__':
    dnsgate()
    eprint("Exiting without error.", log_level=ld.LOG_LEVELS['DEBUG'])
    quit(0)
