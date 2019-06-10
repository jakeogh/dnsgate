
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

Said another way, conventional `/etc/hosts` blocking can not use wildcards * and therefore someone must keep track of each subdomain / domain combination that should be blocked. This is not necessarily a problem. Even if you don't use dnsmasq, other people [1] keep track of the subdomains for you and dnsgate automatically pulls from them. If you want to block a specific domain completely, you must use dnsmasq.

With `--mode dnsmasq` (which is default) `--block-at-psl` strips domains to their "Public Second Level Domain" which is the top public domain with any subdomain stripped, removing the need to manually specify/track specific subdomains. `--block-at-psl` may block domain's you want to use, so use it with `whitelist`.

**Features:**
* **Persistent Configuration.** see `dnsgate configure --help`.
* **Wildcard Blocking.** `--block-at-psl` will block TLD's instead of individual subdomains (dnsmasq mode only).
* **System-wide.** All programs that use the local DNS resolver benefit.
* **Blacklist Caching.** Optionally cache and re-use remote blacklists (see `--no-cache` and `--cache-expire`).
* **Non-interactive.** Can be run as a periodic cron job.
* **Quickly modify your custom Lists.** Like `dnsgate whitelist projectwonderful.com` or `dnsgate blacklist cnn.com`.
* **Return NXDOMAIN.** Rather than redirect the request to 127.0.0.1, NXDOMAIN is returned. (dnsmasq mode only).
* **Return Custom IP.** `--dest-ip` allows redirection to specified IP (disables returning NXDOMAIN in dnsmasq mode).
* **Installation Support.** see install-help
* **Verbose Output.** see `dnsgate --verbose generate`
* **IDN Support.** What to block snowman? `dnsgate blacklist ☃.net`
* **TLD Blocking.** Want to block Saudi Arabia? `dnsgate blacklist sa`
* **Enable/Disable Support.** `dnsgate enable` and `dnsgate disable` (dnsmasq mode only)

**TODO:**
* **Test on distros other than gentoo w/ [OpenRC](https://wiki.gentoo.org/wiki/Comparison_of_init_systems) && dnsmasq**
* **Pip install support**
* **Add tox tests**
* **Add optional DNS filtering proxy to allow hierarchical rules.**
* **Add optional bind rpz output.**
* **Make enable/disable work in `--mode hosts`**

**Dependencies:**
 - [dnsmasq](http://www.thekelleys.org.uk/dnsmasq/doc.html) (optional)
 - python3 (tested on 3.4)
 - [click](https://github.com/mitsuhiko/click)
 - [tldextract](https://github.com/john-kurkowski/tldextract)
 - [kcl](https://github.com/jakeogh/kcl)

**Install:**
```
$ git clone https://github.com/jakeogh/dnsgate.git
$ cd dnsgate
# python3 setup.py install
$ dnsgate configure --help
```

```
  
$ ./dnsgate --help
Usage: dnsgate [OPTIONS] COMMAND [ARGS]...

  dnsgate combines, deduplicates, and optionally modifies local and remote DNS blacklists. Use "dnsgate
  (command) --help" for more information.

Options:
  --no-restart-dnsmasq  do not restart the dnsmasq service
  --backup              backup output file before overwriting
  --verbose             print debug information to stderr
  --help                Show this message and exit.

Commands:
  blacklist     Add domain(s) to /etc/dnsgate/blacklist
  blockall      return NXDOMAIN on _ALL_ domains
  configure     write /etc/dnsgate/config
  disable       Disable /etc/dnsgate/generated_blacklist
  enable        Enable /etc/dnsgate/generated_blacklist
  generate      Create /etc/dnsgate/generated_blacklist
  install_help  Help configure dnsmasq or /etc/hosts
  whitelist     Add domain(s) to /etc/dnsgate/whitelist
```
```
  
$ ./dnsgate configure --help
Usage: dnsgate configure [OPTIONS] [SOURCES]...

  Write /etc/dnsgate/config

  [SOURCES] are the remote blacklist(s) to get rules from. Defaults to:

  http://winhelp2002.mvps.org/hosts.txt http://someonewhocares.org/hosts/hosts
  https://adaway.org/hosts.txt

Options:
  --mode [dnsmasq|hosts]          [required]
  --block-at-psl                  strips subdomains, for example: analytics.google.com -> google.com (must
                                  manually whitelist inadvertently blocked domains)
  --dest-ip TEXT                  IP to redirect blocked connections to (defaults to 127.0.0.1 in hosts
                                  mode, specifying this in dnsmasq mode causes lookups to resolve rather
                                  than return NXDOMAIN)
  --dnsmasq-config-file FILENAME  dnsmasq config file (defaults to /etc/dnsmasq.conf)
  --output TEXT                   (for testing) output file (defaults to /etc/dnsgate/generated_blacklist)
  --help                          Show this message and exit.
```
 
**create dnsgate configuration file for --mode dnsmasq:**
 
```  
$ ./dnsgate configure --mode dnsmasq
``` 
**dnsmasq examples that do the same thing:**
 
```  
$ ./dnsgate generate
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
  
$ ./dnsgate --verbose generate
Using output file: /etc/dnsgate/generated_blacklist
132 validated whitelist domains.
Reading remote blacklist(s):
['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts', 'https://adaway.org/hosts.txt']
24077 domains from remote blacklist(s).
24077 validated remote blacklisted domains.
24075 blacklisted domains after subtracting the 132 whitelisted domains
Re-adding 69 domains in the local blacklist /etc/dnsgate/blacklist to override the whitelist.
24137 blacklisted domains after re-adding the custom blacklist.
23526 blacklisted domains after removing redundant rules.
Sorting domains by their subdomain and grouping by TLD.
Final blacklisted domain count: 23526
Writing output file: /etc/dnsgate/generated_blacklist in dnsmasq format
 * Stopping dnsmasq ... [ ok ]
 * Starting dnsmasq ... [ ok ]
``` 
**create dnsgate configuration file for --mode hosts:**
 
```  
$ ./dnsgate configure --mode hosts
``` 
**hosts examples that do the same thing:**
 
```  
$ ./dnsgate generate
  
$ ./dnsgate --verbose generate
Using output file: /etc/dnsgate/generated_blacklist
132 validated whitelist domains.
Reading remote blacklist(s):
['http://winhelp2002.mvps.org/hosts.txt', 'http://someonewhocares.org/hosts/hosts', 'https://adaway.org/hosts.txt']
24077 domains from remote blacklist(s).
24077 validated remote blacklisted domains.
24075 blacklisted domains after subtracting the 132 whitelisted domains
Re-adding 69 domains in the local blacklist /etc/dnsgate/blacklist to override the whitelist.
24137 blacklisted domains after re-adding the custom blacklist.
23526 blacklisted domains after removing redundant rules.
Sorting domains by their subdomain and grouping by TLD.
Final blacklisted domain count: 23526
Writing output file: /etc/dnsgate/generated_blacklist in hosts format
``` 
**/etc/hosts install help:**
 
```  
$ ./dnsgate install_help
    $ mv -vi /etc/hosts /etc/hosts.default
    $ cat /etc/hosts.default /etc/dnsgate/generated_blacklist > /etc/hosts
``` 



**More Information:**
 - https://news.ycombinator.com/item?id=10572700
 - https://news.ycombinator.com/item?id=10369516
 - https://news.ycombinator.com/item?id=11084968

**Related Stuff:**
 - https://github.com/dhowe/AdNauseam
 - https://github.com/gaenserich/hostsblock (bash)
 - https://github.com/jdoss/dockerhole (bash)
 - http://pgl.yoyo.org/as/#unbound
 - https://github.com/longsleep/adblockrouter
 - https://github.com/StevenBlack/hosts (python)
 - https://github.com/Mechazawa/FuckFuckAdblock
 - http://surf.suckless.org/files/adblock-hosts
 - http://git.r-36.net/hosts-gen
 - https://github.com/vain/lariza
 - https://github.com/fivefilters/block-ads/wiki/There-are-no-acceptable-ads
 - https://github.com/entaopy/peerblock
 - https://surf.suckless.org/files/adblock-hosts/
 - https://github.com/anned20/begoneads

**Simple Software:**

If you find this useful you may appreciate:

 - Disabling JS and making a keybinding to enable it ([surf](http://git.suckless.org/surf/log/?h=surf-webkit2)+[tabbed](http://tools.suckless.org/tabbed/) makes this easy)
 - [musl](http://wiki.musl-libc.org/wiki/Functional_differences_from_glibc#Name_Resolver_.2F_DNS)
 - https://wiki.gentoo.org/wiki/Project:Hardened_musl/Bluedragon
 - https://github.com/andmarti1424/sc-im
 - https://news.ycombinator.com/item?id=17770972
 - https://git.2f30.org/

[1]: http://winhelp2002.mvps.org/hosts.txt http://someonewhocares.org/hosts/hosts

