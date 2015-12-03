
# dnsgate

**dnsgate** merges 3rd party [1] dns blocking lists into `/etc/dnsmasq.conf` or `/etc/hosts` format.

While not required, [dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq) improves on conventional [/etc/hosts domain blocking](http://winhelp2002.mvps.org/hosts.htm) by enabling * blocking of domains.

For example *.google.com:

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```

Said another way, conventional `/etc/hosts` blocking can't use wildcards (*) and therefore requires the user to keep track of each subdomain / domain combination they want to block. This is not necessarily a problem. Even if you don't use dnsmasq, other people [1] keep track of the subdomains for you. If you want to block a specific domain completely, use dnsmasq.

With `--format=dnsmasq` (default if not specified) the `--block-at-tld` option blocks domains at their TLD, removing the need to manually specify/track specific subdomains. `--block-at-tld` may block TLD's you want to use, so use it with `--whitelist`.

```
Usage: dnsgate [OPTIONS]

Options:
  --mode [dnsmasq|hosts]
  --block-at-tld
                           strips subdomains, for example:
                               analytics.google.com -> google.com
                               Useful for dnsmasq if you are willing to maintain a --whitelist file for inadvertently blocked domains.
  --restart-dnsmasq        Restart dnsmasq service (defaults to True, ignored if --mode hosts)
  --output-file TEXT       output file (defaults to /etc/dnsgate/generated_blacklist with --mode dnsmasq and stdout with --mode hosts)
  --backup                 backup output file before overwriting
  --noclobber              do not overwrite existing output file
  --blacklist-append TEXT  Add domain to /etc/dnsgate/blacklist
  --whitelist-append TEXT  Add domain to /etc/dnsgate/whitelist
  --blacklist TEXT
                           blacklist(s) defaults to:
                               http://winhelp2002.mvps.org/hosts.txt
                               http://someonewhocares.org/hosts/hosts
                               /etc/dnsgate/blacklist
  --whitelist TEXT
                           whitelists(s) defaults to:/etc/dnsgate/whitelist
  --cache                  cache --url files as dnsgate_cache_domain_hosts.(timestamp) to ~/.dnsgate/cache
  --dest-ip TEXT           IP to redirect blocked connections to (defaults to 127.0.0.1)
  --show-config            print config information to stderr
  --install-help           show commands to configure dnsmasq or /etc/hosts
  --debug                  print debugging information to stderr
  --help                   Show this message and exit.
```

**dnsmasq example:**

```
$ ./dnsgate
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
```
**is equivalent to:**

```
$ ./dnsgate --show-config
mode: dnsmasq
block_at_tld: False
restart_dnsmasq: True
output_file: /etc/dnsgate/generated_blacklist
backup: False
noclobber: False
blacklist_append: None
whitelist_append: None
blacklist: ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts', '/etc/dnsgate/blacklist']
whitelist: ['/etc/dnsgate/whitelist']
cache: False
dest_ip: None
debug: False
show_config: True
install_help: False
debug: False
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
```
**hosts example:**

```
$ ./dnsgate --mode hosts
```
**is equivalent to:**

```
$ ./dnsgate --mode hosts --show-config
mode: hosts
block_at_tld: False
restart_dnsmasq: True
output_file: /etc/dnsgate/generated_blacklist
backup: False
noclobber: False
blacklist_append: None
whitelist_append: None
blacklist: ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts', '/etc/dnsgate/blacklist']
whitelist: ['/etc/dnsgate/whitelist']
cache: False
dest_ip: None
debug: False
show_config: True
install_help: False
debug: False
```

`[1]:`
 `http://winhelp2002.mvps.org/hosts.txt`
 `http://someonewhocares.org/hosts/hosts`


**Similar Software**

https://gaenserich.github.io/hostsblock/

**Simple Software**

If you find this useful you may appreciate:

 - Disabling JS and making a keybinding to enable it ([surf](http://surf.suckless.org/)+[tabbed](http://tools.suckless.org/tabbed/) makes this easy)
 - [musl](http://wiki.musl-libc.org/wiki/Functional_differences_from_glibc#Name_Resolver_.2F_DNS)


