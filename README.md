# dnsmasq-blacklist

[dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq)'s configuration syntax provides an alternative to /etc/hosts domain blocking.

Unlike /etc/hosts dnsmasq allows wildcard blocking of domains, for example, to block *.google.com (and google.com):

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```

**dnsmasq-blacklist** merges two /etc/hosts blocking lists```[1]``` into /etc/dnsmasq.conf or /etc/hosts format.

Unlike conventional [hosts file blocking](http://winhelp2002.mvps.org/hosts.htm), dnsmasq does not require the listing of each subdomain. If the `--trim-subdomains` option is enabled subdomain changes wont subvert blocking (unless --hosts is also enabled).

Using dnsmasq often significantly lowers DNS latency.

```
$./dnsmasq-blacklist -h
usage: dnsmasq-blacklist [-h] [--url [URL [URL ...]]] [--trim-subdomains]
                         [--whitelist WHITELIST] [--keep]
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
                         
  --trim-subdomains     strip subdomains (see --whitelist)
                        example:
                            analytics.google.com -> google.com
                        not enabled by default. Useful for dnsmasq if you are willing to maintain a
                        --whitelist file for inadvertently blocked domains. This causes ad-serving
                        domains to be blocked at their TLD's. Wihout this option, the domain owner
                        can change until the --url lists are updated. It does not make sense to use
                        this flag if you are generateing a /etc/hosts format file since the effect
                        would be to block google.com and not *.google.com
                         
  --whitelist WHITELIST
                        file containing DNS names to whitelist
                        example:
                            stackexchange.com
                            stackoverflow.com
                         
  --keep                save retrieved hosts files as hosts.(timestamp) in the current folder
                         


$./dnsmasq-blacklist --dnsmasq /etc/dnsmasq.blacklist.conf

To add to dnsmasq.conf:
cp -vi /etc/dnsmasq.conf /etc/dnsmasq.conf.1428126020.6137238 && \
echo "conf-file=/etc/dnsmasq.blacklist.conf" >> /etc/dnsmasq.conf

Then restart the dnsmasq service:
"/etc/init.d/dnsmasq restart" or "service dnsmasq restart"

$ head /etc/dnsmasq.blacklist.conf
address=/.s28.sitemeter.com/127.0.0.1
address=/.ameritradeogilvy.112.2o7.net/127.0.0.1
address=/.xtds.info/127.0.0.1
address=/.ad.netcommunities.com/127.0.0.1
address=/.banners.affilimatch.de/127.0.0.1
address=/.www.synovite-scripts.com/127.0.0.1
address=/.win-spy.com/127.0.0.1
address=/.www.hitscreamer.com/127.0.0.1
address=/.www.ivwbox.de/127.0.0.1
address=/.images.bmnq.com/127.0.0.1
```

`[1]:`
 `http://winhelp2002.mvps.org/hosts.txt`
 `http://someonewhocares.org/hosts/hosts`
