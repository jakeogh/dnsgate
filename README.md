
# dnsgate

**dnsgate** merges 3rd party [1] DNS blocking lists into `/etc/dnsmasq.conf` or `/etc/hosts` format.

While not required, [dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq) improves on conventional [/etc/hosts domain blocking](http://winhelp2002.mvps.org/hosts.htm) by enabling * blocking of domains.

For example *.google.com:

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```
Returnins 127.0.0.1 for all google.com domains. Rather than return 127.0.0.1 and make the application chack if port 80/443/whatever is open, dnsmasq has another advantage; it can return NXDOMAIN:

```
echo 'server=/.google.com/' >> /etc/dnsmasq.conf
```
This instead returns NXDOMAIN on *.google.com. Returning NXDOMAIN instead of localhost is default in dnsmasq output mode.

Said another way, conventional `/etc/hosts` blocking can not use wildcards * and therefore someone must keep track of each subdomain / domain combination that should be blocked. This is not necessarily a problem. Even if you don't use dnsmasq, other people [1] keep track of the subdomains for you. If you want to block a specific domain completely, you must use dnsmasq.

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
  --no-cache               do not cache --url files as sha1(url) to ~/.dnsgate/cache/
  --cache-expire INTEGER   seconds until a cached remote file is re-downloaded (defaults to 24 hours)
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
no_cache: False
dest_ip: None
debug: False
show_config: True
install_help: False
debug: False
verbose: False
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
  
$ ./dnsgate --verbose
Using output_file: /etc/dnsgate/generated_blacklist
Reading whitelist: /etc/dnsgate/whitelist
78 validated whitelist domains.
Reading remote blacklist(s):
['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts']
23634 domains from the remote blacklist(s).
23634 validated remote blacklisted domains.
23633 blacklisted domains after subtracting the 78 whitelisted domains
Re-adding 62 domains in the local blacklist /etc/dnsgate/blacklist to override the whitelist.
23690 blacklisted domains after re-adding the custom blacklist.
Sorting domains by their subdomain and grouping by TLD.
Final blacklisted domain count: 18326
Writing output file: /etc/dnsgate/generated_blacklist in dnsmasq format
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
``` 
**dnsmasq example with --block-at-psl:**
 
```  
$ ./dnsgate --verbose --block-at-psl
Using output_file: /etc/dnsgate/generated_blacklist
Reading whitelist: /etc/dnsgate/whitelist
78 validated whitelist domains.
Reading remote blacklist(s):
['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts']
23634 domains from the remote blacklist(s).
23634 validated remote blacklisted domains.
Removing subdomains on 23634 domains.
10536 blacklisted domains left after stripping to PSL domains.
Subtracting 78 whitelisted domains.
10471 blacklisted domains left after subtracting the whitelist.
Iterating through the original 78 whitelisted domains andmaking sure none are blocked by * rules.
Iterating through original 23634 blacklisted domains to re-add subdomains that are not whitelisted
10746 blacklisted domains after re-adding non-explicitely blacklisted subdomains
10746 blacklisted domains after subtracting the 78 whitelisted domains
Re-adding 62 domains in the local blacklist /etc/dnsgate/blacklist to override the whitelist.
10795 blacklisted domains after re-adding the custom blacklist.
Sorting domains by their subdomain and grouping by TLD.
Final blacklisted domain count: 10372
Writing output file: /etc/dnsgate/generated_blacklist in dnsmasq format
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
``` 
**dnsmasq install help:**
 
```  
$ ./dnsgate --install-help
    $ cp -vi /etc/dnsmasq.conf /etc/dnsmasq.conf.bak.1451865526.704349
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
no_cache: False
dest_ip: None
debug: False
show_config: True
install_help: False
debug: False
verbose: False
  
$ ./dnsgate --mode hosts --verbose
Using output_file: /etc/dnsgate/generated_blacklist
Reading whitelist: /etc/dnsgate/whitelist
78 validated whitelist domains.
Reading remote blacklist(s):
['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts']
23634 domains from the remote blacklist(s).
23634 validated remote blacklisted domains.
23633 blacklisted domains after subtracting the 78 whitelisted domains
Re-adding 62 domains in the local blacklist /etc/dnsgate/blacklist to override the whitelist.
23690 blacklisted domains after re-adding the custom blacklist.
Sorting domains by their subdomain and grouping by TLD.
Final blacklisted domain count: 18323
Writing output file: /etc/dnsgate/generated_blacklist in hosts format
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


