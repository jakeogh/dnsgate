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

# flake8: noqa           # flake8 has no per file settings :(
# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=C0114  # Missing module docstring (missing-module-docstring)
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement
# pylint: disable=C0305  # Trailing newlines editor should fix automatically, pointless warning
# pylint: disable=C0413  # TEMP isort issue [wrong-import-position] Import "from pathlib import Path" should be placed at the top of the module [C0413]


__version__ = "0.0.1"

import ast
import configparser
import copy
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional

import click
from logtool import LOG
from logtool import leprint
from logtool import set_verbose
from pathtool import backup_file_if_exists
from pathtool import comment_out_line_in_file
from pathtool import create_relative_symlink
from pathtool import file_exists_nonzero
from pathtool import is_broken_symlink
from pathtool import is_unbroken_symlink
from pathtool import uncomment_line_in_file
from pathtool import write_line_to_file
from stringtool import contains_whitespace
from urltool import extract_domain_set_from_dnsgate_format_file
from urltool import extract_psl_domain
from urltool import group_by_tld
from urltool import prune_redundant_rules
from urltool import strip_to_psl
from urltool import validate_domain_list

from .cache import get_domains_from_url
from .config import DnsgateConfig
from .config import dnsmasq_config_file_line
from .file_headers import make_custom_blacklist_header
from .file_headers import make_custom_whitelist_header
from .file_headers import make_output_file_header
from .global_vars import CACHE_DIRECTORY
from .global_vars import CACHE_EXPIRE
from .global_vars import CONFIG_DIRECTORY
from .global_vars import CONFIG_FILE
from .global_vars import CUSTOM_BLACKLIST
from .global_vars import CUSTOM_WHITELIST
from .global_vars import DEFAULT_REMOTE_BLACKLISTS
from .global_vars import DNSMASQ_CONFIG_FILE
from .global_vars import DNSMASQ_CONFIG_INCLUDE_DIRECTORY
from .global_vars import DNSMASQ_CONFIG_SYMLINK
from .global_vars import OUTPUT_FILE_PATH
from .help import BACKUP_HELP
from .help import BLACKLIST_HELP
from .help import BLOCK_AT_PSL_HELP
from .help import BLOCKALL_HELP
from .help import CACHE_EXPIRE_HELP
from .help import CONFIGURE_HELP
from .help import DEST_IP_HELP
from .help import DISABLE_HELP
from .help import DNSMASQ_CONFIG_HELP
from .help import ENABLE_HELP
from .help import GENERATE_HELP
from .help import INSTALL_HELP_HELP
from .help import NO_CACHE_HELP
from .help import NO_RESTART_DNSMASQ_HELP
from .help import OUTPUT_FILE_HELP
from .help import VERBOSE_HELP
from .help import WHITELIST_HELP
from .help import dnsmasq_install_help
from .help import hosts_install_help


#  todo, check return code, run disable() and try again if the service fails
def restart_dnsmasq_service():
    if os.path.lexists('/etc/init.d/dnsmasq'):
        os.system('/etc/init.d/dnsmasq restart 1>&2')
    else:
        os.system('systemctl restart dnsmasq 1>&2')  # untested
    return True


def append_to_local_rule_file(*,
                              path: Path,
                              idn: str,
                              verbose: bool,
                              debug: bool,
                              ) -> None:

    leprint("attempting to append %s to %s", idn, path, level=LOG['INFO'])
    hostname = idn.encode('idna').decode('ascii')
    leprint("appending hostname: %s to %s", hostname, path, level=LOG['DEBUG'])
    line = hostname + '\n'
    write_line_to_file(line=line, path=path, verbose=verbose, debug=debug)


# https://github.com/mitsuhiko/click/issues/441
CONTEXT_SETTINGS = \
    dict(help_option_names=['--help'],
         terminal_width=shutil.get_terminal_size((80, 20)).columns)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--no-restart-dnsmasq',
              is_flag=True,
              help=NO_RESTART_DNSMASQ_HELP,)
@click.option('--backup',
              is_flag=True,
              help=BACKUP_HELP,)
@click.option('--verbose',
              is_flag=True,
              help=VERBOSE_HELP,
              callback=set_verbose,
              expose_value=False,)
@click.pass_context
def dnsgate(ctx, no_restart_dnsmasq, backup):
    """
    dnsgate combines, deduplicates, and optionally modifies local and
    remote DNS blacklists. Use \"dnsgate (command) --help\"
    for more information.
    """
    config = configparser.ConfigParser()
    if 'dnsgate configure' not in ' '.join(sys.argv):
        if 'dnsgate.py configure' not in ' '.join(sys.argv):
            try:
                with open(CONFIG_FILE, 'r') as cf:
                    config.read_file(cf)
            except FileNotFoundError:
                leprint("No configuration file found, run " + "\"dnsgate configure --help\". Exiting.", level=LOG['ERROR'])
                sys.exit(1)

            mode = config['DEFAULT']['mode']

            try:
                output_path = config['DEFAULT']['output']
            except KeyError:
                leprint('ERROR: ' + CONFIG_FILE.as_posix() + ' has no "output" defined. ' + "run 'dnsgate configure --help' to fix. Exiting.", level=LOG['ERROR'])
                sys.exit(1)
            assert isinstance(output_path, str)
            if not os.path.exists(os.path.dirname(output_path)):
                leprint("ERROR: dnsgate is configured for 'mode = dnsmasq' in " + CONFIG_FILE.as_posix() + " but dnsmasq_config_file is not set. " + "run 'dnsgate configure --help' to fix. Exiting.", level=LOG['ERROR'])
                sys.exit(1)

            block_at_psl = config['DEFAULT'].getboolean('block_at_psl')
            dest_ip = config['DEFAULT']['dest_ip']  #  todo validate ip or False/None
            if dest_ip == 'False':
                dest_ip = None
            sources = ast.literal_eval(config['DEFAULT']['sources'])  # configparser has no .getlist()?
            if mode == 'dnsmasq':
                try:
                    dnsmasq_config_file = \
                        click.open_file(config['DEFAULT']['dnsmasq_config_file'],
                        'w', atomic=True, lazy=True)
                    dnsmasq_config_file.close()  # it exists and is writeable
                except KeyError:
                    leprint("ERROR: dnsgate is configured for 'mode = dnsmasq' in " + CONFIG_FILE.as_posix() + " but dnsmasq_config_file is not set. run 'dnsgate configure --help' to fix. Exiting.", level=LOG['ERROR'])
                    sys.exit(1)

                ctx.obj = DnsgateConfig(mode=mode,
                                        block_at_psl=block_at_psl,
                                        dest_ip=dest_ip,
                                        no_restart_dnsmasq=no_restart_dnsmasq,
                                        dnsmasq_config_file=dnsmasq_config_file,
                                        backup=backup,
                                        sources=sources,
                                        output=output_path,)
            else:
                if not dest_ip:
                    dest_ip = '0.0.0.0'
                ctx.obj = DnsgateConfig(mode=mode,
                                        block_at_psl=block_at_psl,
                                        dest_ip=dest_ip,
                                        no_restart_dnsmasq=no_restart_dnsmasq,
                                        backup=backup,
                                        sources=sources,
                                        output=output_path,)

            os.makedirs(CACHE_DIRECTORY, exist_ok=True)


@dnsgate.command(help=WHITELIST_HELP)
@click.argument('domains', required=True, nargs=-1)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
def whitelist(domains: Optional[tuple],
              verbose: bool,
              debug: bool,
              ) -> None:
    if domains:
        for domain in domains:
            append_to_local_rule_file(path=CUSTOM_WHITELIST, idn=domain, verbose=verbose, debug=debug,)
        context = click.get_current_context()
        context.invoke(generate)


@dnsgate.command(help=BLACKLIST_HELP)
@click.argument('domains', required=True, nargs=-1)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
def blacklist(domains: Optional[tuple],
              verbose: bool,
              debug: bool,
              ) -> None:
    if domains:
        for domain in domains:
            append_to_local_rule_file(path=CUSTOM_BLACKLIST, idn=domain, verbose=verbose, debug=debug,)
        context = click.get_current_context()
        context.invoke(generate)


@dnsgate.command(help=INSTALL_HELP_HELP)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_obj
def install_help(config,
                 verbose: bool,
                 debug: bool,
                 ) -> None:
    if config.mode == 'dnsmasq':
        dnsmasq_install_help(dnsmasq_config_file=DNSMASQ_CONFIG_FILE, output_file=OUTPUT_FILE_PATH)
    elif config.mode == 'hosts':
        hosts_install_help()


@dnsgate.command(help=ENABLE_HELP)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_obj
def enable(config,
           verbose: bool,
           debug: bool,
           ) -> None:
    if config.mode == 'dnsmasq':
        if not file_exists_nonzero(OUTPUT_FILE_PATH):
            leprint('ERROR: %s does not exist, run "dnsgate generate" to fix. Exiting.', OUTPUT_FILE_PATH, level=LOG['ERROR'])
            sys.exit(1)
        # verify generate() was last run in dnsmasq mode so dnsmasq does not
        # fail when the service is restarted
        with open(OUTPUT_FILE_PATH, 'r') as fh:
            file_content = fh.read(550) #just check the header
            if 'mode: dnsmasq' not in file_content:
                leprint('ERROR: %s was not generated in dnsmasq mode, run "dnsgate generate --help" to fix. Exiting.', OUTPUT_FILE_PATH, level=LOG['ERROR'])
                sys.exit(1)

        dnsmasq_config_line = dnsmasq_config_file_line()
        if not uncomment_line_in_file(path=config.dnsmasq_config_file, line=dnsmasq_config_line, verbose=verbose, debug=debug,):
            write_line_to_file(line=dnsmasq_config_line, path=config.dnsmasq_config_file.name, unique=True, verbose=verbose, debug=debug,)

        config.dnsmasq_config_file.close()
        symlink = DNSMASQ_CONFIG_SYMLINK
        if not os.path.islink(symlink): # not a symlink
            if os.path.exists(symlink): # but exists
                leprint("ERROR: " + symlink.as_posix() + " exists and is not a symlink. You need to manually delete it. Exiting.", level=LOG['ERROR'])
                sys.exit(1)
        if is_broken_symlink(symlink): #hm, a broken symlink, ok, remove it
            leprint("WARNING: removing broken symlink: %s", symlink, level=LOG['WARNING'])
            os.remove(symlink)
        if not is_unbroken_symlink(symlink):
            try:
                os.remove(symlink) # maybe it was symlink to somewhere else
            except FileNotFoundError:
                pass    # that's ok
            create_relative_symlink(target=OUTPUT_FILE_PATH, link_name=symlink, verbose=verbose, debug=debug,)
        restart_dnsmasq_service()
    else:
        leprint("ERROR: enable is only available with --mode dnsmasq. Exiting.", level=LOG['ERROR'])
        sys.exit(1)


@dnsgate.command(help=DISABLE_HELP)
@click.argument('timeout', required=False, type=int)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_context
def disable(ctx,
            timeout: int,
            verbose: bool,
            debug: bool,
            ) -> None:

    '''TIMEOUT: re-enable after n seconds'''

    config = ctx.obj
    if config.mode == 'dnsmasq':
        comment_out_line_in_file(path=config.dnsmasq_config_file, line=dnsmasq_config_file_line(), verbose=verbose, debug=debug,)
        config.dnsmasq_config_file.close()
        symlink = DNSMASQ_CONFIG_SYMLINK
        if os.path.islink(symlink):
            os.remove(symlink)
        if not os.path.islink(symlink): # not a symlink
            if os.path.exists(symlink): # but exists
                leprint("ERROR: " + symlink.as_posix() + " exists and is not a symlink. You need to manually delete it. Exiting.", level=LOG['ERROR'])
                sys.exit(1)
        restart_dnsmasq_service()
        leprint("Sleepin %ss:", timeout)
        time.sleep(timeout)
        ctx.invoke(enable)
    else:
        leprint("ERROR: disable is only available with --mode dnsmasq. Exiting.",
               level=LOG['ERROR'])
        sys.exit(1)


@dnsgate.command(help=BLOCKALL_HELP)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_obj
def blockall(config,
             verbose: bool,
             debug: bool,
             ) -> None:

    if config.mode == 'dnsmasq':
        domains_combined = set(['.'])
        write_output_file(config=config, domains_combined=domains_combined, verbose=verbose, debug=debug,)
    else:
        leprint("ERROR: blockall is only available with --mode dnsmasq. Exiting.",
               level=LOG['ERROR'])
        sys.exit(1)


@click.pass_obj
def write_output_file(*,
                      config,
                      domains_combined: set,
                      verbose: bool,
                      debug: bool,
                      ):
    config_dict = make_config_dict(config)

    leprint("Writing output file: %s in %s format", config.output, config.mode, level=LOG['INFO'])
    with click.open_file(config.output, 'wb', atomic=True, lazy=True) as fh:
        fh.write(make_output_file_header(config_dict))
        for domain in domains_combined:
            if config.mode == 'dnsmasq':
                if config.dest_ip:
                    dnsmasq_line = 'address=/.' + domain.decode('utf8') + '/' + config.dest_ip + '\n'
                else:
                    dnsmasq_line = 'server=/.' + domain.decode('utf8') + '/' '\n'  # return NXDOMAIN
                fh.write(dnsmasq_line.encode('utf8'))
            elif config.mode == 'hosts':
                if config.dest_ip:
                    hosts_line = config.dest_ip + ' ' + domain.decode('utf8') + '\n'
                else:
                    hosts_line = '127.0.0.1' + ' ' + domain.decode('utf8') + '\n'
                fh.write(hosts_line.encode('utf8'))


@dnsgate.command(help=CONFIGURE_HELP, short_help='write /etc/dnsgate/config')
@click.argument('sources', nargs=-1)
@click.option('--mode', is_flag=False,
              type=click.Choice(['dnsmasq', 'hosts']),
              required=True,)
@click.option('--block-at-psl',
              is_flag=True,
              help=BLOCK_AT_PSL_HELP,)
@click.option('--dest-ip',
              is_flag=False,
              help=DEST_IP_HELP,
              default=None,)
@click.option('--dnsmasq-config-file',
              is_flag=False,
              help=DNSMASQ_CONFIG_HELP,
              type=click.File(mode='w', atomic=True, lazy=True),
              default=DNSMASQ_CONFIG_FILE,)
@click.option('--output',
              is_flag=False,
              help=OUTPUT_FILE_HELP,
              default=OUTPUT_FILE_PATH,)
def configure(sources: Optional[tuple[str]],
              mode: str,
              block_at_psl: bool,
              dest_ip: str,
              dnsmasq_config_file: Path,
              output: Path,
              ):
    if contains_whitespace(dnsmasq_config_file.name):
        leprint("ERROR: --dnsmasq-config-file can not contain whitespace. Exiting.",
               level=LOG['ERROR'])
        sys.exit(1)

    if not sources:
        sources = DEFAULT_REMOTE_BLACKLISTS

    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)
    config = configparser.ConfigParser()
    config['DEFAULT'] = \
        {
            'mode': mode,
            'block_at_psl': block_at_psl,
            'dest_ip': dest_ip,
            'sources': sources,
            'output': output
        }

    if mode == 'dnsmasq':
        os.makedirs(DNSMASQ_CONFIG_INCLUDE_DIRECTORY, exist_ok=True)
        config['DEFAULT']['dnsmasq_config_file'] = dnsmasq_config_file.name

    with open(CONFIG_FILE, 'w') as cf:
        config.write(cf)

    if not os.path.exists(CUSTOM_BLACKLIST):
        with open(CUSTOM_BLACKLIST, 'w') as fh: # not 'wb', utf8 is ok
            fh.write(make_custom_blacklist_header(CUSTOM_BLACKLIST))

    if not os.path.exists(CUSTOM_WHITELIST):
        with open(CUSTOM_WHITELIST, 'w') as fh: # not 'wb', utf8 is ok
            fh.write(make_custom_whitelist_header(CUSTOM_WHITELIST))

@click.pass_obj
def make_config_dict(config): #todo, just cat the config file
    config_dict = {
        'mode': config.mode,
        'sources': config.sources,
        'block_at_psl': config.block_at_psl,
        'dest_ip': config.dest_ip,
        'output': config.output
        }
    return config_dict

@dnsgate.command(help=GENERATE_HELP)
@click.option('--no-cache', is_flag=True, help=NO_CACHE_HELP)
@click.option('--cache-expire',
              is_flag=False,
              help=CACHE_EXPIRE_HELP,
              type=int,
              default=CACHE_EXPIRE,)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_obj
def generate(config,
             no_cache: bool,
             cache_expire: int,
             verbose: bool,
             debug: bool,
             ):

    leprint('Using output file: %s', config.output, level=LOG['INFO'])
    whitelist_file = os.path.abspath(CUSTOM_WHITELIST)
    try:
        domains_whitelist = extract_domain_set_from_dnsgate_format_file(whitelist_file)
    except FileNotFoundError:
        domains_whitelist = set()
        leprint('WARNING: %s is missing, only the default remote sources will be used.' +
               'Run "dnsgate configure --help" to fix.', CUSTOM_WHITELIST, level=LOG['WARNING'])
    else:
        if domains_whitelist:
            leprint("%d domains from %s", len(domains_whitelist),
                   CUSTOM_WHITELIST, level=LOG['DEBUG'])
            domains_whitelist = validate_domain_list(domains_whitelist)
            leprint('%d validated whitelist domains.', len(domains_whitelist),
                   level=LOG['INFO'])

    if not domains_whitelist:
        if config.block_at_psl:
            leprint('WARNING: block_at_psl is enabled in ' + CONFIG_FILE.as_posix() + ' and 0 domains were obtained from %s. If you get "Domain Not Found" errors, use "dnsgate whitelist --help"', CUSTOM_WHITELIST, level=LOG['WARNING'])

    domains_combined_orig = set()   # domains from all sources, combined
    leprint("Reading remote blacklist(s):\n%s", str(config.sources), level=LOG['INFO'])
    for item in config.sources:
        if item.startswith('http'):
            leprint("Trying http:// blacklist location: %s", item, level=LOG['DEBUG'])
            domains = get_domains_from_url(url=item, no_cache=no_cache, cache_expire=cache_expire)
            if domains:
                domains_combined_orig = domains_combined_orig | domains # union
                leprint("len(domains_combined_orig): %s",
                       len(domains_combined_orig), level=LOG['DEBUG'])
            else:
                leprint('ERROR: Failed to get ' + item + ', skipping.', level=LOG['ERROR'])
                continue
        else:
            leprint('ERROR: ' + item +
                   ' must start with http:// or https://, skipping.', level=LOG['ERROR'])

    leprint("%d domains from remote blacklist(s).",
           len(domains_combined_orig), level=LOG['INFO'])

    if len(domains_combined_orig) == 0:
        leprint("WARNING: 0 domains were retrieved from " +
               "remote sources, only the local " + CUSTOM_BLACKLIST +
               " will be used.", level=LOG['WARNING'])

    domains_combined_orig = validate_domain_list(domains_combined_orig)
    leprint('%d validated remote blacklisted domains.',
           len(domains_combined_orig), level=LOG['INFO'])

    domains_combined = copy.deepcopy(domains_combined_orig) # need to iterate through _orig later

    if config.block_at_psl and config.mode != 'hosts':
        domains_combined = strip_to_psl(domains_combined)
        leprint("%d blacklisted domains left after stripping to PSL domains.",
               len(domains_combined), level=LOG['INFO'])

        if domains_whitelist:
            leprint("Subtracting %d whitelisted domains.",
                   len(domains_whitelist), level=LOG['INFO'])
            domains_combined = domains_combined - domains_whitelist
            leprint("%d blacklisted domains left after subtracting the whitelist.",
                   len(domains_combined), level=LOG['INFO'])
            leprint('Iterating through the original %d whitelisted domains and ' +
                   'making sure none are blocked by * rules.',
                   len(domains_whitelist), level=LOG['INFO'])
            for domain in domains_whitelist:
                domain_psl = extract_psl_domain(domain)
                if domain_psl in domains_combined:
                    domains_combined.remove(domain_psl)
                    print("TODO: removed domain_psl:", domain_psl)

        # this needs to happen even if len(whitelisted_domains) == 0
        leprint('Iterating through original %d blacklisted domains to re-add subdomains' +
               ' that are not whitelisted', len(domains_combined_orig), level=LOG['INFO'])
        # re-add subdomains that are not explicitly whitelisted or already blocked
        for orig_domain in domains_combined_orig: # check every original full hostname
            if orig_domain not in domains_whitelist: # if it's not in the whitelist
                if orig_domain not in domains_combined: # and it's not in the current blacklist
                                                        # (almost none will be if --block-at-psl)
                    # get it's psl to see if it's already blocked
                    orig_domain_psl = extract_psl_domain(orig_domain)

                    if orig_domain_psl not in domains_combined: # if the psl is not already blocked
                        leprint("Re-adding: %s", orig_domain, level=LOG['DEBUG'])
                        domains_combined.add(orig_domain) # add the full hostname to the blacklist

        leprint('%d blacklisted domains after re-adding non-explicitly blacklisted subdomains',
               len(domains_combined), level=LOG['INFO'])

    elif config.block_at_psl and config.mode == 'hosts':
        leprint("ERROR: --block-at-psl is not possible in hosts mode. Exiting.",
               level=-LOG['ERROR'])
        sys.exit(1)

    # apply whitelist before applying local blacklist
    domains_combined = domains_combined - domains_whitelist  # remove exact whitelist matches
    leprint("%d blacklisted domains after subtracting the %d whitelisted domains",
           len(domains_combined), len(domains_whitelist), level=LOG['INFO'])

    # must happen after subdomain stripping and after whitelist subtraction
    blacklist_file = os.path.abspath(CUSTOM_BLACKLIST)
    try:
        domains_blacklist = extract_domain_set_from_dnsgate_format_file(blacklist_file)
    except FileNotFoundError:
        domains_blacklist = set()
        leprint('WARNING: %s is missing, only the default remote sources ' +
               'will be used. Run "dnsgate configure --help" to fix.',
               CUSTOM_BLACKLIST, level=LOG['WARNING'])
    else:
        if domains_blacklist: # ignore empty blacklist
            leprint("Got %s domains from the CUSTOM_BLACKLIST: %s",
                   len(domains_blacklist), blacklist_file, level=LOG['DEBUG'])
            leprint("Re-adding %d domains in the local blacklist %s to override the whitelist.",
                   len(domains_blacklist), CUSTOM_BLACKLIST, level=LOG['INFO'])
            domains_combined = domains_combined | domains_blacklist # union
            leprint("%d blacklisted domains after re-adding the custom blacklist.",
                   len(domains_combined), level=LOG['INFO'])

    leprint("Validating final domain blacklist.", level=LOG['DEBUG'])
    domains_combined = validate_domain_list(domains_combined)
    leprint('%d validated blacklisted domains.', len(domains_combined), level=LOG['DEBUG'])

    prune_redundant_rules(domains_combined)
    leprint('%d blacklisted domains after removing redundant rules.', len(domains_combined),
           level=LOG['INFO'])

    domains_combined = group_by_tld(domains_combined) # do last, returns sorted list
    leprint('Final blacklisted domain count: %d', len(domains_combined), level=LOG['INFO'])

    if config.backup: # todo: unit test
        backup_file_if_exists(config.output)

    if not domains_combined:
        leprint("The list of domains to block is empty, nothing to do, exiting.",
               level=LOG['INFO'])
        sys.exit(1)

    for domain in domains_whitelist:
        domain_tld = extract_psl_domain(domain)
        if domain_tld in domains_combined:
            leprint('WARNING: %s is listed in both %s and %s, the local blacklist always takes precedence.', domain.decode('UTF8'), CUSTOM_BLACKLIST, CUSTOM_WHITELIST, level=LOG['WARNING'])

    write_output_file(config=config, domains_combined=domains_combined, verbose=verbose, debug=debug,)

    if not config.no_restart_dnsmasq:
        if config.mode != 'hosts':
            restart_dnsmasq_service()


if __name__ == '__main__':

    # pylint: disable=no-value-for-parameter
    dnsgate()
    # pylint: enable=no-value-for-parameter
    leprint("Exiting without error.", level=LOG['DEBUG'])
    sys.exit(0)
