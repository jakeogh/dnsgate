
# dnsgate

**dnsgate** merges 3rd party dns blocking lists```[1]```into /etc/dnsmasq.conf or /etc/hosts format.

While not required, [dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq) improves on conventional [/etc/hosts domain blocking](http://winhelp2002.mvps.org/hosts.htm) by enabling * blocking of domains.

For example *.google.com:

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```

Said another way, conventional `/etc/hosts` blocking can't use wildcards * and therefore requires the user to keep track of each subdomain/tld combination they want to block.

With `--format=dnsmasq` the `--trim-subdomains` option can be used to block domain's at their top level, removing the need to manually specify specific subdomains. `--trim-subdomains` may block TLD's you want to use, so use it with `--whitelist`.

As a bonus, using dnsmasq can significantly lower DNS latency and therefore make your net connection more responsive.

```
usage: dnsgate [-h] [--format {dnsmasq,hosts}] [--output OUTPUT]
               [--url [URL [URL ...]]] [--remove-subdomains] [--verbose]
               [--install-help] [--whitelist WHITELIST]
               [--url-cache-dir URL_CACHE_DIR] [--dest-ip DEST_IP]

optional arguments:
  -h, --help            show this help message and exit
  --format {dnsmasq,hosts}
                        generate /etc/dnsmasq.conf (default) or /etc/hosts format file
  --output OUTPUT       output file (default stdout)
  --url [URL [URL ...]]
                        hosts file url(s)
                        defaults to:
                            http://winhelp2002.mvps.org/hosts.txt
                            http://someonewhocares.org/hosts/hosts
                        local files can be specified:
                            file://some_file
                         
  --remove-subdomains   remove subdomains (see --whitelist)
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
                        
  --whitelist WHITELIST
                        file of DNS names to whitelist
                        example:
                            stackexchange.com
                            stackoverflow.com
                        
  --url-cache-dir URL_CACHE_DIR
                        cache --url files as
                        dnsgate_cache_domain_hosts.(timestamp)
                        optionally in a specified directory
                        
  --dest-ip DEST_IP     IP to redirect blocked connections to. Defaults to 127.0.0.1
                        

```
 
**dnsmasq example:**
```

    $ ./dnsgate --format=dnsmasq --output=blacklist.txt --install-help
    $ cp -vi blacklist.txt /etc/
    $ cp -vi /etc/dnsmasq.conf /etc/dnsmasq.conf.bak
    $ echo "conf-file=/etc/blacklist.txt" >> /etc/dnsmasq.conf
    $ /etc/init.d/dnsmasq restart

See --help and --verbose for more information.

```
 
**hosts example:**
```

    $ ./dnsgate --format=hosts --output=blacklist.txt --install-help
    $ cp -vi /etc/hosts /etc/hosts.bak
    $ cat blacklist.txt >> /etc/hosts
    NOTE: "cp /etc/hosts.bak /etc/hosts" before doing this a second time.

See --help and --verbose for more information.

```
 

`[1]:`
 `http://winhelp2002.mvps.org/hosts.txt`
 `http://someonewhocares.org/hosts/hosts`


**Similar Software**

https://gaenserich.github.io/hostsblock/


**Why?**

Individuals should decide who they execute code for. Providers will either adapt and not use sub or alternate domains; explicitly linking the requirement to execute their code to get their content, or will find a better way.

If you find this useful, you may appreciate the effects of disabling JS and making a hotkey for when you want to use it.

