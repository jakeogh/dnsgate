#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# PUBLIC DOMAIN
# http://github.com/jkeogh/dnsgate

import click
import copy
import time
import sys
import os
import shutil
import inspect
import requests
import tldextract
from urllib.parse import urlparse
from shutil import copyfileobj
from debug_logging import log_prefix, logger, logger_quiet, print_traceback, log_levels

CONFIG_DIRECTORY = '/etc/dnsgate'
CACHE_DIRECTORY = CONFIG_DIRECTORY + '/cache'
DEFAULT_BLACKLIST = CONFIG_DIRECTORY + '/blacklist'
DEFAULT_WHITELIST = CONFIG_DIRECTORY + '/whitelist'
DEFAULT_OUTPUT_FILE = CONFIG_DIRECTORY + '/generated_blacklist'
DEFAULT_BLACKLIST_SOURCES = ['http://winhelp2002.mvps.org/hosts.txt',
                             'http://someonewhocares.org/hosts/hosts', DEFAULT_BLACKLIST]
DEFAULT_WHITELIST_SOURCES = [DEFAULT_WHITELIST]

def eprint(*args, log_level, **kwargs):
    if click_debug:
        logger.debug(*args, **kwargs)
    else:
        if log_level >= log_levels['INFO']:
            logger_quiet.info(*args, **kwargs)

@log_prefix()
def restart_dnsmasq_service():
    if os.path.lexists('/etc/init.d/dnsmasq'):
        ret = os.system('/etc/init.d/dnsmasq restart')
    else:
        ret = os.system('systemctl restart dnsmasq')    # untested
    return True

def remove_comments(line):
    uncommented_line = ''
    for char in line:
        if char != '#':
            uncommented_line += char
        else:
            break
    return uncommented_line

#@log_prefix()
def extract_domains_from_bytes_list(domain_bytes):
    domains = set()
    for line in domain_bytes:
        line = line.decode('UTF-8')
        line = line.replace('\t', ' ')          # expand tabs
        line = ' '.join(line.split())           # collapse whitespace
        line = line.strip()
        line = remove_comments(line)
        if ' ' in line:                         # hosts format
            line = line.split(' ')[1]           # get DNS name (the url's are in hosts 0.0.0.0 dom.com format)
            # pylint: disable=bad-builtin
            line = '.'.join(list(filter(None, line.split('.'))))    # ignore leading/trailing .
            # pylint: enable=bad-builtin
            domains.add(line)
    return domains

@log_prefix()
def read_list_of_domains(file):
    domains = set([])
    file = os.path.abspath(file)
    try:
        lines = read_file(file).splitlines()
    except Exception as e:
        logger.exception(e)
    else:
        for line in lines:
            line = line.strip()
            line = remove_comments(line)
            line = '.'.join(list(filter(None, line.split('.')))) # ignore leading/trailing .
            if len(line) > 0:
                domains.add(line)
    return domains

@log_prefix()
def get_url(url, cache=False):
    if url.startswith('http://') or url.startswith('https://'):
        eprint("GET: %s", url, log_level=log_levels['DEBUG'])
        user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0'
        try:
            raw_hosts_file_lines = requests.get(url, headers={'User-Agent': user_agent}, allow_redirects=True,
                                   stream=False, timeout=15.500).content.split(b'\n')
        except Exception as e:
            logger.exception(e)
            return False
#           raise e
        if cache:
            domain = urlparse(url).netloc
            output_file = CACHE_DIRECTORY + '/' + 'dnsgate_cache_' + domain + '_hosts.' + str(time.time())
            if not os.path.isdir(CACHE_DIRECTORY):
                os.makedirs(CACHE_DIRECTORY)
            with open(output_file, 'wb') as fh:
                for line in raw_hosts_file_lines:
                    fh.write(line + b'\n')
        domains = extract_domains_from_bytes_list(raw_hosts_file_lines)
    else:
        logger.error("unknown url scheme: %s", url)
        os._exit(1)

    eprint("domains in %s:%s", url, len(domains), log_level=log_levels['DEBUG'])
    return domains

def group_by_tld(domains):
    eprint('sorting domains by their subdomain and grouping by TLD', log_level=log_levels['INFO'])
    sorted_output = []
    reversed_domains = []
    for domain in domains:
        rev_domain = domain.split('.')
        rev_domain.reverse()
        reversed_domains.append(rev_domain)
    reversed_domains.sort() #sorting a list of lists by the tld
    for rev_domain in reversed_domains:
        rev_domain.reverse()
        sorted_output.append('.'.join(rev_domain))
    return sorted_output

@log_prefix()
def read_file(file):
    if os.path.isfile(file):
        with open(file, 'r') as fh:
            file_bytes = fh.read()
        return file_bytes
    else:
        raise FileNotFoundError(file + ' does not exist.')

def domain_extract(domain):
    dom = no_cache_extract(domain)  #prevent tldextract cache update error when run as a normal user
    return dom

def strip_to_tld(domains):
    '''This causes ad-serving domains to be blocked at their TLD.
    Otherwise the subdomain can be changed until the --url lists are updated.
    It does not make sense to use this flag if you are generating a /etc/hosts
    format file since the effect would be to block google.com and not
    *.google.com.'''
    eprint('removing subdomains on %d domains', len(domains), log_level=log_levels['INFO'])
    domains_stripped = set()
    for line in domains:
        line = domain_extract(line)             # get tld
        line = line.domain + '.' + line.suffix
        domains_stripped.add(line)
    return domains_stripped

@log_prefix()
def write_unique_line(line, file):
    with open(file, 'r+') as fh:
        if line not in fh:
            fh.write(line)

@log_prefix()
def backup_file_if_exists(file):
    timestamp = str(time.time())
    dest_file = file + '.bak.' + timestamp
    try:
        with open(file, 'r') as sf:
            with open(dest_file, 'x') as df:
                copyfileobj(sf, df)
    except FileNotFoundError:
        pass    # skip backup is file does not exist

def validate_domain_list(domains):
    eprint('validating %d domains', len(domains), log_level=log_levels['INFO'])
    valid_domains = set([])
    for hostname in domains:
        try:
            hostname = hostname.encode('idna').decode('ascii')
            valid_domains.add(hostname)
        except Exception as e:
            logger.exception(e)
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

# pylint: disable=invalid-name
output_file_help = '''output file defaults to ''' + DEFAULT_OUTPUT_FILE
noclobber_help = '''do not overwrite existing output file'''
backup_help = '''backup output file before overwriting'''
install_help_help = '''show commands to configure dnsmasq or /etc/hosts (note: this does nothing else)'''
blacklist_help = '''\b
blacklist(s) defaults to:
''' + '\n'.join(['    {0}'.format(i) for i in DEFAULT_BLACKLIST_SOURCES])

whitelist_help = '''\b
whitelists(s) defaults to:''' + DEFAULT_WHITELIST.replace(os.path.expanduser('~'), '~')
block_at_tld_help = '''
\b
strips subdomains, for example:
    analytics.google.com -> google.com
    Useful for dnsmasq if you are willing to maintain a --whitelist file
    for inadvertently blocked domains.'''
debug_help = '''print debugging information to stderr'''
verbose_help = '''print more information to stderr'''
show_config_help = '''print config information to stderr'''
cache_help = '''cache --url files as dnsgate_cache_domain_hosts.(timestamp) to ~/.dnsgate/cache'''
dest_ip_help = '''IP to redirect blocked connections to (defaults to 127.0.0.1)'''
restart_dnsmasq_help = '''Restart dnsmasq service (defaults to True, ignored if --mode hosts)'''
blacklist_append_help = '''Add domain to ''' + DEFAULT_BLACKLIST
whitelist_append_help = '''Add domain to ''' + DEFAULT_WHITELIST
# pylint: enable=invalid-name

if '--debug' not in sys.argv:
    logger.setLevel(log_levels['DEBUG'] + 1)  #prevent @log_prefix() on main() from printing when debug if off


#https://github.com/mitsuhiko/click/issues/441
CONTEXT_SETTINGS = dict(help_option_names=['--help'], terminal_width=shutil.get_terminal_size((80, 20)).columns)
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--mode',             is_flag=False, type=click.Choice(['dnsmasq', 'hosts']), default='dnsmasq')
@click.option('--block-at-tld',     is_flag=True,  help=block_at_tld_help)
@click.option('--restart-dnsmasq',  is_flag=True,  help=restart_dnsmasq_help,  default=True)
@click.option('--output-file',      is_flag=False, help=output_file_help,      default=DEFAULT_OUTPUT_FILE)
@click.option('--backup',           is_flag=True,  help=backup_help)
@click.option('--noclobber',        is_flag=True,  help=noclobber_help)
@click.option('--blacklist-append', is_flag=False, help=blacklist_append_help, type=str)
@click.option('--whitelist-append', is_flag=False, help=whitelist_append_help, type=str)
@click.option('--blacklist',        is_flag=False, help=blacklist_help, default=DEFAULT_BLACKLIST_SOURCES)
@click.option('--whitelist',        is_flag=False, help=whitelist_help, default=DEFAULT_WHITELIST_SOURCES)
@click.option('--cache',            is_flag=True,  help=cache_help)
@click.option('--dest-ip',          is_flag=False, help=dest_ip_help)
@click.option('--show-config',      is_flag=True,  help=show_config_help)
@click.option('--install-help',     is_flag=True,  help=install_help_help)
@click.option('--debug',            is_flag=True,  help=debug_help)
@click.option('--verbose',          is_flag=True,  help=verbose_help)
@log_prefix()
def main(mode, block_at_tld, restart_dnsmasq, output_file, backup, noclobber,
            blacklist_append, whitelist_append, blacklist, whitelist,
            cache, dest_ip, show_config, install_help, debug, verbose):

    if show_config:
        print("mode:", mode)
        print("block_at_tld:", block_at_tld)
        print("restart_dnsmasq:", restart_dnsmasq)
        print("output_file:", output_file)
        print("backup:", backup)
        print("noclobber:", noclobber)
        print("blacklist_append:", blacklist_append)
        print("whitelist_append:", whitelist_append)
        print("blacklist:", blacklist)
        print("whitelist:", whitelist)
        print("cache:", cache)
        print("dest_ip:", dest_ip)
        print("debug:", debug)
        print("show_config:", show_config)
        print("install_help:", install_help)
        print("debug:", debug)
        print("verbose:", verbose)

    global click_debug
    click_debug = debug

    if not verbose and not debug:
        logger.setLevel(log_levels['DEBUG'] + 1)
        logger_quiet.setLevel(log_levels['INFO'] + 1)

    if verbose and not debug:
        logger_quiet.setLevel(log_levels['INFO'])

    if debug:
        logger.setLevel(log_levels['DEBUG'])
    else:
        logger.setLevel(log_levels['INFO'])

    if output_file == '-' or output_file == '/dev/stdout':
        output_file = '/dev/stdout'
    else:
        eprint("using non standard output_file", log_level=log_levels['DEBUG'])
        output_file = os.path.abspath(output_file)

    if os.path.isfile(output_file) and output_file != '/dev/stdout':
        if noclobber:
            logger.error("File '%s' exists. Refusing to overwrite because --noclobber was used. Exiting.", output_file)
            quit(1)

    eprint('using output_file: %s', output_file, log_level=log_levels['INFO'])

    if install_help:
        if mode == 'dnsmasq':
            dnsmasq_install_help(output_file)
        elif mode == 'hosts':
            hosts_install_help(output_file)

#   idn='☃.net'
    if whitelist_append:
        eprint("attempting to append %s to %s", whitelist_append, DEFAULT_WHITELIST, log_level=log_levels['INFO'])
        idn = whitelist_append
        eprint("idn: %s", idn, log_level=log_levels['DEBUG'])
        hostname = idn.encode('idna').decode('ascii')
        eprint("appending hostname: %s to %s", hostname, DEFAULT_WHITELIST, log_level=log_levels['DEBUG'])
        line = hostname + '\n'
        write_unique_line(line, DEFAULT_WHITELIST)

    if blacklist_append:
        eprint("attempting to append %s to %s", blacklist_append, DEFAULT_BLACKLIST, log_level=log_levels['INFO'])
        idn = blacklist_append
        hostname = idn.encode('idna').decode('ascii')
        eprint("appending hostname: %s to %s", hostname, DEFAULT_BLACKLIST, log_level=log_levels['DEBUG'])
        line = hostname + '\n'
        write_unique_line(line, DEFAULT_BLACKLIST)

    domains_whitelist = set()
    eprint("reading whitelist(s): %s", str(whitelist), log_level=log_levels['INFO'])
    for item in whitelist:
        whitelist_file = os.path.abspath(item)
        domains_whitelist = domains_whitelist|read_list_of_domains(whitelist_file)

    if domains_whitelist:
        eprint("%d unique domains from the whitelist(s)", len(domains_whitelist), log_level=log_levels['INFO'])

    domains_combined_orig = set()   # domains from all sources, combined
    eprint("reading blacklist(s): %s", str(blacklist), log_level=log_levels['INFO'])
    for item in blacklist:
        if item.startswith('http'):
            try:
                eprint("trying http:// blacklist location: %s", item, log_level=log_levels['DEBUG'])
                domains = get_url(item, cache)
                if domains:
                    domains_combined_orig = domains_combined_orig|domains # union
                    eprint("blacklist: %s", blacklist, log_level=log_levels['DEBUG'])
                    eprint("len(domains_combined_orig): %s", len(domains_combined_orig), log_level=log_levels['DEBUG'])
                else:
                    logger.error('failed to get %s, skipping.', item)
                    continue

            except Exception as e:
                logger.error("Exception on blacklist url: %s", item)
                logger.exception(e)

        else:
            eprint("trying local blacklist file: %s", item, log_level=log_levels['DEBUG'])
            blacklist_file = os.path.abspath(item)
            domains = read_list_of_domains(blacklist_file)
            eprint("got %s domains from %s", domains, blacklist_file, log_level=log_levels['DEBUG'])
            if domains:
                domains_combined_orig = domains_combined_orig|domains # union

    eprint("%d unique domains from the blacklist(s)", len(domains_combined_orig), log_level=log_levels['INFO'])

    domains_combined_orig = domains_combined_orig - domains_whitelist  # remove exact whitelist matches

    eprint("%d unique blacklisted domains after subtracting the %d whitelisted domains",
            len(domains_combined_orig), len(domains_whitelist), log_level=log_levels['INFO'])

    domains_combined_orig = validate_domain_list(domains_combined_orig)
    eprint('%d validated blacklisted domains', len(domains_combined_orig), log_level=log_levels['INFO'])

    domains_combined = copy.deepcopy(domains_combined_orig)

    if block_at_tld:
        domains_combined = strip_to_tld(domains_combined)
        eprint("%d blacliksted unique domains left after stripping to TLD's",
                len(domains_combined), log_level=log_levels['INFO'])
        eprint("subtracting %d explicitely whitelisted domains", len(domains_whitelist), log_level=log_levels['INFO'])
        domains_combined = domains_combined - domains_whitelist
        eprint("%d unique blacklisted domains left after subtracting the whitelist",
                len(domains_combined), log_level=log_levels['INFO'])

        eprint('iterating through the original %d blacklisted domains and re-adding subdomains' +
                ' that are not whitelisted', len(domains_combined_orig), log_level=log_levels['INFO'])
        #re-add subdomains that are not explicitly whitelisted or already blocked by another rule
        for orig_domain in domains_combined_orig: #check every original full hostname
            if orig_domain not in domains_whitelist: #if it's not in the whitelist
                if orig_domain not in domains_combined: #and it's not in the current blacklist
                                                        #(almost none will be if --block-at-tld)
                    orig_domain_tldextract = domain_extract(orig_domain) #get it's tld to see if it's
                                                                         #already blocked by a dnsmasq * rule
                    orig_domain_tld = orig_domain_tldextract.domain + '.' + orig_domain_tldextract.suffix
                    if orig_domain_tld not in domains_combined: #if the tld is not already blocked
                        eprint("re-adding: %s", orig_domain, log_level=log_levels['DEBUG'])
                        domains_combined.add(orig_domain) #add the full hostname to the blacklist

        eprint("%d unique blacklisted domains after re-adding non-explicitely blacklisted subdomains",
                len(domains_combined), log_level=log_levels['INFO'])

    #this must happen after tld stripping
    if DEFAULT_BLACKLIST in blacklist:
        eprint("re-adding domains in the local blacklist %s to override the whitelist",
                DEFAULT_BLACKLIST, log_level=log_levels['INFO'])
        blacklist_file = os.path.abspath(DEFAULT_BLACKLIST)
        domains = read_list_of_domains(blacklist_file)
        eprint("got %s domains from %s", domains, blacklist_file, log_level=log_levels['DEBUG'])
        if domains:
            domains_combined = domains_combined | domains # union

        eprint("%d unique blacklisted domains after re-adding the custom blacklist",
                len(domains_combined), log_level=log_levels['INFO'])

    domains_combined = group_by_tld(domains_combined)
    eprint('final blacklisted domain count: %d', len(domains_combined), log_level=log_levels['INFO'])

    if backup:
        backup_file_if_exists(output_file)

    try:
        os.mkdir(CONFIG_DIRECTORY)
    except FileExistsError:
        pass

    if mode == 'hosts':
        eprint("writing output file: %s in /etc/hosts format", output_file, log_level=log_levels['INFO'])
        with open(output_file, 'w') as fh:
            for domain in domains_combined:
                if dest_ip:
                    hosts_line = dest_ip + ' ' + domain + '\n'
                else:
                    hosts_line = '127.0.0.1' + ' ' + domain + '\n'
                fh.write(hosts_line)

    elif mode == 'dnsmasq':
        eprint("writing output file: %s in dnsmasq format", output_file, log_level=log_levels['INFO'])
        with open(output_file, 'w') as fh:
            for domain in domains_combined:
                if dest_ip:
                    dnsmasq_line = 'address=/.' + domain + '/' + dest_ip + '\n'
                else:
                    dnsmasq_line = 'server=/.' + domain + '/' '\n'  #return NXDOMAIN
                fh.write(dnsmasq_line)

    if restart_dnsmasq:
        if mode != 'hosts':
            restart_dnsmasq_service()


if __name__ == '__main__':
    no_cache_extract = tldextract.TLDExtract(cache_file=False)
    main()
    eprint("Exiting without error.", log_level=log_levels['DEBUG'])
    quit(0)
