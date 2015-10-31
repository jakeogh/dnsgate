
# dnsgate

**dnsgate** merges 3rd party dns blocking lists`[1]`into `/etc/dnsmasq.conf` or `/etc/hosts` format.

While not required, [dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq) improves on conventional [/etc/hosts domain blocking](http://winhelp2002.mvps.org/hosts.htm) by enabling * blocking of domains.

For example *.google.com:

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```

Said another way, conventional `/etc/hosts` blocking can't use wildcards * and therefore requires the user to keep track of each subdomain/tld combination they want to block. This is not necessarily a problem. Even if you don't use dnsmasq, other people `[1]` keep track of the subdomains for you. If you decide you want to block a specific domain completely, you must use dnsmasq.

With `--format=dnsmasq` the `--trim-subdomains` option can be used to block domain's at their top level, removing the need to manually specify specific subdomains. `--trim-subdomains` may block TLD's you want to use, so use it with `--whitelist`.

Since dnsmasq caches dns queries, it often lowers DNS latency.

```
usage: dnsgate [-h] [--format {dnsmasq,hosts}]
               [--blacklist [BLACKLIST [BLACKLIST ...]]]
               [--whitelist [WHITELIST [WHITELIST ...]]] [--output OUTPUT]
               [--dest-ip DEST_IP] [--block-tld] [--verbose] [--install-help]
               [--url-cache]

optional arguments:
  -h, --help            show this help message and exit
  --format {dnsmasq,hosts}
                        generate /etc/dnsmasq.conf (default) or /etc/hosts format file
                        
  --blacklist [BLACKLIST [BLACKLIST ...]]
                        blacklist(s) defaults to:
                            http://winhelp2002.mvps.org/hosts.txt
                            http://someonewhocares.org/hosts/hosts
                            /home/user/.dnsgate/blacklist
                        
  --whitelist [WHITELIST [WHITELIST ...]]
                        whitelists(s) defaults to:
                            /home/user/.dnsgate/whitelist
                        
  --output OUTPUT       output file (default stdout)
                        
  --dest-ip DEST_IP     IP to redirect blocked connections to. Defaults to 127.0.0.1
                        
  --block-tld           remove subdomains (see --whitelist)
                        example:
                            analytics.google.com -> google.com
                        not enabled by default. Useful for dnsmasq if you are willing
                        to maintain a --whitelist file for inadvertently blocked
                        domains. This causes ad-serving domains to be blocked at their
                        TLD. Without this option, the domain owner can change the
                        subdomain until the --url lists are updated. It does not make
                        sense to use this flag if you are generating a /etc/hosts
                        format file since the effect would be to block google.com and
                        not *.google.com
                        
  --verbose             print additional debugging information to stderr
                        
  --install-help        print example install and configure information
                        (requires format)
                        
  --url-cache           cache --url files as dnsgate_cache_domain_hosts.(timestamp)
                        to ~/.dnsgate/cache
                        

```
 
**dnsmasq example:**
```
    $ dnsgate --format=dnsmasq --output=dnsgate_output
    $ cp -vi dnsgate_output /etc/
    $ cp -vi /etc/dnsmasq.conf /etc/dnsmasq.conf.bak
    $ echo "conf-file=/etc/dnsgate_output" >> /etc/dnsmasq.conf
    $ /etc/init.d/dnsmasq restart

See --help and --verbose for more information.

``` 
**hosts example:**
```
    $ dnsgate --format=hosts --output=dnsgate_output
    $ cp -vi /etc/hosts /etc/hosts.bak
    $ cat dnsgate_output >> /etc/hosts
    NOTE: "cp /etc/hosts.bak /etc/hosts" before doing this a second time.

See --help and --verbose for more information.

``` 

`[1]:`
 `http://winhelp2002.mvps.org/hosts.txt`
 `http://someonewhocares.org/hosts/hosts`


**Similar Software**

https://gaenserich.github.io/hostsblock/


If you find this useful, you may appreciate the effects of disabling JS and making a key shortcut to enable it.

