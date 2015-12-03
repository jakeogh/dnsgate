
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
  --output-format [dnsmasq|hosts]
  --show-config                   print config information to stderr
  --debug                         print debugging information to stderr
  --cache                         cache --url files as dnsgate_cache_domain_hosts.(timestamp) to ~/.dnsgate/cache
  --noclobber                     do not overwrite existing output file
  --block-at-tld
                                  strips subdomains, for example:
                                      analytics.google.com -> google.com
                                      Useful for dnsmasq if you are willing to maintain a --whitelist file for inadvertently blocked domains.
  --backup                        backup output file before overwriting
  --restart-dnsmasq               Restart dnsmasq service (defaults to True, ignored if --format=hosts)
  --output-file TEXT              output file (defaults to /etc/dnsgate/generated_blacklist with --format=dnsmasq and stdout with --format=hosts)
  --blacklist-append TEXT         Add domain to /etc/dnsgate/blacklist
  --whitelist-append TEXT         Add domain to /etc/dnsgate/whitelist
  --blacklist TEXT
                                  blacklist(s) defaults to:
                                      http://winhelp2002.mvps.org/hosts.txt
                                      http://someonewhocares.org/hosts/hosts
                                      /etc/dnsgate/blacklist
  --whitelist TEXT
                                  whitelists(s) defaults to:/etc/dnsgate/whitelist
  --dest-ip TEXT                  IP to redirect blocked connections to (defaults to 127.0.0.1)
  --help                          Show this message and exit.
```

**dnsmasq example:**

```
$ ./dnsgate
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
```
***is equivalent to:***

```
$ ./dnsgate --show-config
output_file: /etc/dnsgate/generated_blacklist
output_format: dnsmasq
debug: False
show_config: True
cache: False
noclobber: False
block_at_tld: False
backup: False
whitelist_append: None
blacklist_append: None
blacklist: ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts', '/etc/dnsgate/blacklist']
whitelist: ['/etc/dnsgate/whitelist']
restart_dnsmasq: True
dest_ip: 127.0.0.1
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
```
**hosts example:**

```
$ ./dnsgate --output-format hosts --output-file hosts.blacklist
```
**is equivalent to:**

```
$ ./dnsgate --output-format hosts --output-file hosts.blacklist --show-config
output_file: hosts.blacklist
output_format: hosts
debug: False
show_config: True
cache: False
noclobber: False
block_at_tld: False
backup: False
whitelist_append: None
blacklist_append: None
blacklist: ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts', '/etc/dnsgate/blacklist']
whitelist: ['/etc/dnsgate/whitelist']
restart_dnsmasq: True
dest_ip: 127.0.0.1
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


