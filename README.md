
# dnsgate

**dnsgate** merges 3rd party [1] DNS blocking lists into `/etc/dnsmasq.conf` or `/etc/hosts` format.

While not required, [dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq) improves on conventional [/etc/hosts domain blocking](http://winhelp2002.mvps.org/hosts.htm) by enabling * blocking of domains.

For example *.google.com:

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```
Has the effect of returning 127.0.0.1 for all google.com domains. Rather than return 127.0.0.1, dnsmasq can return NXDOMAIN:

```
echo 'server=/.google.com/' >> /etc/dnsmasq.conf
```
This instead returns NXDOMAIN on *.google.com. Returning NXDOMAIN is dnsgate's default behavior in dnsmasq mode.

Said another way, conventional `/etc/hosts` blocking can't use wildcards (*) and therefore requires the user to keep track of each subdomain / domain combination they want to block. This is not necessarily a problem. Even if you don't use dnsmasq, other people [1] keep track of the subdomains for you. If you want to block a specific domain completely, use dnsmasq.

With `--mode dnsmasq` (default if not specified) the `--block-at-psl` option strips domains to their "Public Second Level Domain" which is the domain with any subdomain stripped, removing the need to manually specify/track specific subdomains. `--block-at-psl` may block domain's you want to use, so use it with `--whitelist`.

**Features:**
* **Wildcard Blocking** --block-at-psl will block TLD's instead of individual subdomains (dnsmasq mode only).
* **System-wide.** All programs that use the local DNS resolver benefit.
* **Blacklist Caching.** Optionally cache and re-use remote blacklists (see --cache and --cache-timeout).
* **Non-interactive.** Can be run as a periodic cron job.
* **Fully Configurable.** See ./dnsgate --help (TODO, add /etc/dnsgate/config file support)
* **Custom Lists.** See /etc/dnsgate/blacklist and /etc/dnsgate/whitelist.
* **Return NXDOMAIN.** Rather than redirect the request to 127.0.0.1, NXDOMAIN is returned. (dnsmasq mode only).
* **Return Custom IP.** --dest-ip allows redirection to specified IP (disables returning NXDOMAIN in dnsmasq mode)
* **Installation Support.** see --install-help
* **Extensive Debugging Support.** see --verbose and --debug
* **IDN Support.** What to block snowman? ./dnsgate --blacklist-append ☃.net

**TODO:**
* **Full Test Coverage.**

**Dependencies:**
 - [dnsmasq](http://www.thekelleys.org.uk/dnsmasq/doc.html) (optional)
 - python3 (tested on 3.4)
 - [click](https://github.com/mitsuhiko/click)
 - [tldextract](https://github.com/john-kurkowski/tldextract)
 - [colorama](https://github.com/tartley/colorama)

```
Usage: dnsgate [OPTIONS]

Options:
  --mode [dnsmasq|hosts]
  --block-at-psl          
                           strips subdomains, for example:
                               analytics.google.com -> google.com
                               Useful for dnsmasq if you are willing to maintain a --whitelist file
                               for inadvertently blocked domains.
  --restart-dnsmasq        Restart dnsmasq service (defaults to True, ignored if --mode hosts)
  --output-file TEXT       output file defaults to /etc/dnsgate/generated_blacklist
  --backup                 backup output file before overwriting
  --noclobber              do not overwrite existing output file
  --blacklist-append TEXT  Add domain to /etc/dnsgate/blacklist
  --whitelist-append TEXT  Add domain to /etc/dnsgate/whitelist
  --blacklist TEXT        
                           blacklist(s) defaults to:
                               http://winhelp2002.mvps.org/hosts.txt
                               http://someonewhocares.org/hosts/hosts
  --cache                  cache --url files as dnsgate_cache_domain_hosts.(timestamp) to ~/.dnsgate/cache
  --cache-expire INTEGER   seconds until a cached remote file is re-downloaded
  --dest-ip TEXT           IP to redirect blocked connections to (defaults to 127.0.0.1)
  --show-config            print config information to stderr
  --install-help           show commands to configure dnsmasq or /etc/hosts (note: this does nothing else)
  --debug                  print debugging information to stderr
  --verbose                print more information to stderr
  --help                   Show this message and exit.
```
 
**three dnsmasq examples that do the same thing:**
 
```  
$ ./dnsgate
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
  
$ ./dnsgate --show-config
mode: dnsmasq
block_at_psl: False
restart_dnsmasq: True
output_file: /etc/dnsgate/generated_blacklist
backup: False
noclobber: False
blacklist_append: None
whitelist_append: None
blacklist: ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts']
cache: False
dest_ip: None
debug: False
show_config: True
install_help: False
debug: False
verbose: False
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
  
$ ./dnsgate --verbose
using output_file: /etc/dnsgate/generated_blacklist
reading whitelist: /etc/dnsgate/whitelist
76 unique domains from the whitelist
validating 76 domains
76 validated whitelist domains
reading remote blacklist(s): ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts']
23685 unique domains from the remote blacklist(s)
validating 23685 domains
23685 validated remote blacklisted domains
23684 unique blacklisted domains after subtracting the 76 whitelisted domains
re-adding 19 domains in the local blacklist /etc/dnsgate/blacklist to override the whitelist
23698 unique blacklisted domains after re-adding the custom blacklist
validating final domain block list
validating 23698 domains
23698 validated blacklisted domains
sorting domains by their subdomain and grouping by TLD
final blacklisted domain count: 23698
writing output file: /etc/dnsgate/generated_blacklist in dnsmasq format
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
``` 
**dnsmasq example with --block-at-psl:**
 
```  
$ ./dnsgate --verbose --block-at-psl
using output_file: /etc/dnsgate/generated_blacklist
reading whitelist: /etc/dnsgate/whitelist
76 unique domains from the whitelist
validating 76 domains
76 validated whitelist domains
reading remote blacklist(s): ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts']
23685 unique domains from the remote blacklist(s)
validating 23685 domains
23685 validated remote blacklisted domains
removing subdomains on 23685 domains
10559 blacklisted unique domains left after stripping to PSL domains
subtracting 76 explicitely whitelisted domains so not explicitely whitelisted subdomains that existed (and were blocked) before the subdomain stripping can be re-added
10496 unique blacklisted domains left after subtracting the whitelist
iterating through the original 76 whitelisted domains and making sure none are blocked by * rules
iterating through the original 23685 blacklisted domains and re-adding subdomains that are not whitelisted
10765 unique blacklisted domains after re-adding non-explicitely blacklisted subdomains
10765 unique blacklisted domains after subtracting the 76 whitelisted domains
re-adding 19 domains in the local blacklist /etc/dnsgate/blacklist to override the whitelist
10771 unique blacklisted domains after re-adding the custom blacklist
validating final domain block list
validating 10771 domains
10771 validated blacklisted domains
sorting domains by their subdomain and grouping by TLD
final blacklisted domain count: 10771
writing output file: /etc/dnsgate/generated_blacklist in dnsmasq format
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
``` 
**dnsmasq install help:**
 
```  
$ ./dnsgate --install-help
    $ cp -vi /etc/dnsmasq.conf /etc/dnsmasq.conf.bak.1451538845.6310759
    $ grep "conf-file=/etc/dnsgate/generated_blacklist" /etc/dnsmasq.conf || { echo "conf-file=/etc/dnsgate/generated_blacklist" >> /etc/dnsmasq.conf ; }
    $ /etc/init.d/dnsmasq restart
``` 
**three hosts examples that do the same thing:**
 
```  
$ ./dnsgate --mode hosts
  
$ ./dnsgate --mode hosts --show-config
mode: hosts
block_at_psl: False
restart_dnsmasq: True
output_file: /etc/dnsgate/generated_blacklist
backup: False
noclobber: False
blacklist_append: None
whitelist_append: None
blacklist: ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts']
cache: False
dest_ip: None
debug: False
show_config: True
install_help: False
debug: False
verbose: False
  
$ ./dnsgate --mode hosts --verbose
using output_file: /etc/dnsgate/generated_blacklist
reading whitelist: /etc/dnsgate/whitelist
76 unique domains from the whitelist
validating 76 domains
76 validated whitelist domains
reading remote blacklist(s): ['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts']
23685 unique domains from the remote blacklist(s)
validating 23685 domains
23685 validated remote blacklisted domains
23684 unique blacklisted domains after subtracting the 76 whitelisted domains
re-adding 19 domains in the local blacklist /etc/dnsgate/blacklist to override the whitelist
23698 unique blacklisted domains after re-adding the custom blacklist
validating final domain block list
validating 23698 domains
23698 validated blacklisted domains
sorting domains by their subdomain and grouping by TLD
final blacklisted domain count: 23698
writing output file: /etc/dnsgate/generated_blacklist in hosts format
``` 
**/etc/hosts install help:**
 
```  
$ ./dnsgate --mode hosts --install-help
    $ mv -vi /etc/hosts /etc/hosts.default
    $ cat /etc/hosts.default /etc/dnsgate/generated_blacklist > /etc/hosts
``` 



**More Information:**
 - https://news.ycombinator.com/item?id=10572700
 - https://news.ycombinator.com/item?id=10369516

**Related Software:**
 - https://github.com/gaenserich/hostsblock (bash)
 - http://pgl.yoyo.org/as/#unbound
 - https://github.com/longsleep/adblockrouter
 - https://github.com/StevenBlack/hosts (TODO, use this)
 - https://github.com/Mechazawa/FuckFuckAdblock

**Simple Software:**
If you find this useful you may appreciate:

 - Disabling JS and making a keybinding to enable it ([surf](http://surf.suckless.org/)+[tabbed](http://tools.suckless.org/tabbed/) makes this easy)
 - [musl](http://wiki.musl-libc.org/wiki/Functional_differences_from_glibc#Name_Resolver_.2F_DNS)

[1]: http://winhelp2002.mvps.org/hosts.txt http://someonewhocares.org/hosts/hosts


