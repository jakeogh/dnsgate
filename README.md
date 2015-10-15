# dnsmasq-blacklist

**dnsmasq-blacklist** merges two /etc/hosts blocking lists```[1]``` into /etc/dnsmasq.conf or /etc/hosts format.

[dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq) improves on conventional [/etc/hosts domain blocking](http://winhelp2002.mvps.org/hosts.htm) by enabling * blocking of domains.

For example *.google.com:

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```

Conventional [hosts file blocking](http://winhelp2002.mvps.org/hosts.htm) requires the user to keep track of each subdomain/tld combination they want to block.

In dnsmasq mode the `--trim-subdomains` option can be used to block ad-serving domain's at their top level, removing the need to manually specify specific subdomains.

As a bonus, using dnsmasq can significantly lower DNS latency and therefore make your net connection more responsive.

```
$./dnsmasq-blacklist -h
usage: dnsmasq-blacklist [-h] [--url [URL [URL ...]]] [--remove-subdomains]
                         [--verbose] [--whitelist WHITELIST]
                         [--url-cache-dir URL_CACHE_DIR]
                         {dnsmasq,hosts} output_file

positional arguments:
  {dnsmasq,hosts}       (required) generate /etc/dnsmasq.conf or /etc/hosts file
  output_file           (required) output file (- for stdout)

optional arguments:
  -h, --help            show this help message and exit
  --url [URL [URL ...]]
                        optional hosts file url(s)
                        defaults to:
                            http://winhelp2002.mvps.org/hosts.txt
                            http://someonewhocares.org/hosts/hosts
                        local files can be specified:
                            file://some_file
                         
  --remove-subdomains   remove subdomains (see --whitelist)
                        example:
                            analytics.google.com -> google.com
                        not enabled by default. Useful for dnsmasq if you are willing
                        to maintain a --whitelist file for inadvertently blocked domains.
                        This causes ad-serving domains to be blocked at their TLD.
                        Without this option, the domain owner can change the subdomain
                        until the --url lists are updated. It does not make sense to
                        use this flag if you are generating a /etc/hosts format file
                        since the effect would be to block google.com and not
                        *.google.com
  --verbose             print additional debugging information to stderr
  --whitelist WHITELIST
                        file of DNS names to whitelist
                        example:
                            stackexchange.com
                            stackoverflow.com
  --url-cache-dir URL_CACHE_DIR
                        cache --url files as
                        dnsmasq-blacklist_cache_domain_hosts.(timestamp)
                        optionally in a specified directory
                         
```

`[1]:`
 `http://winhelp2002.mvps.org/hosts.txt`
 `http://someonewhocares.org/hosts/hosts`


**Why?**

To force the issue. Individuals should decide who they execute code for. Providers will either adapt and not use subdomains; explicitly linking the requirement to execute their code to get their content, or will find a better way.

If you find this useful, you may appreciate the effects of disabling JS and making a hotkey for when you want to use it.
