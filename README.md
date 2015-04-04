# dnsmasq-blacklist

[dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq) allows wildcard blocking of domains, for example, to block *.google.com:

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```

dnsmasq-blacklist reads two popular /etc/hosts blocking lists and converts to dnsmasq.conf format


```
$./dnsmasq-blacklist -h
usage: dnsmasq-blacklist [-h] [--no-subdomains] output_file

positional arguments:
  output_file      File to write dnsmasq rules to

optional arguments:
  -h, --help       show this help message and exit
  --no-subdomains  No not include subdomains (legitimate domains may be
                   blocked).

$./dnsmasq-blacklist /etc/dnsmasq.blacklist.conf
Done generating /etc/dnsmasq.blacklist.conf

To add to dnsmasq.conf:
cp -vi /etc/dnsmasq.conf /etc/dnsmasq.conf.1428126020.6137238 && \
echo "conf-file=/etc/dnsmasq.blacklist.conf" >> /etc/dnsmasq.conf

Then restart the dnsmasq service:
"/etc/init.d/dnsmasq restart" or "service dnsmasq restart"

$head /etc/dnsmasq.blacklist.conf
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
