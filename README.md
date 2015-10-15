# dnsmasq-blacklist

**dnsmasq-blacklist** merges two /etc/hosts blocking lists```[1]``` into /etc/dnsmasq.conf or /etc/hosts format.

[dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq)'s configuration syntax provides an alternative to /etc/hosts domain blocking.

Unlike /etc/hosts dnsmasq allows wildcard blocking of domains, for example, to block *.google.com (and google.com):

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```

Unlike conventional [hosts file blocking](http://winhelp2002.mvps.org/hosts.htm), dnsmasq does not require the listing of each subdomain. If the `--trim-subdomains` option is enabled subdomain changes wont subvert blocking (unless --hosts is also enabled).

Using dnsmasq often significantly lowers DNS latency.

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
                        local files can also be specified:
                            file://some_file
                         
  --remove-subdomains   remove subdomains (see --whitelist)
                        example:
                            analytics.google.com -> google.com
                        not enabled by default. Useful for dnsmasq if you are willing to maintain a
                        --whitelist file for inadvertently blocked domains. This causes ad-serving
                        domains to be blocked at their TLD's. Without this option, the domain owner
                        can change until the --url lists are updated. It does not make sense to use
                        this flag if you are generating a /etc/hosts format file since the effect
                        would be to block google.com and not *.google.com
                         
  --verbose             print additional debugging information to stderr
                         
  --whitelist WHITELIST
                        file of DNS names to whitelist
                        example:
                            stackexchange.com
                            stackoverflow.com
                         
  --url-cache-dir URL_CACHE_DIR
                        cache --url files as dnsmasq-blacklist_cache_domain_hosts.(timestamp) optionally in a specified directory
                         
```

`[1]:`
 `http://winhelp2002.mvps.org/hosts.txt`
 `http://someonewhocares.org/hosts/hosts`


**Why?**

To force the issue. Individuals should decide who they execute code for. Providers will either adapt and not use subdomains; explicitly linking the requirement to execute their code to get their content, or will find a better way.
