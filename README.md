# dnsmasq-blacklist

[dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq) allows wildcard blocking of domains, for example, to block *.google.com:

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```

**dnsmasq-blacklist** reads two popular /etc/hosts blocking lists```[1]``` and converts them to dnsmasq.conf format.

Unlike conventional [hosts file blocking](http://winhelp2002.mvps.org/hosts.htm), dnsmasq does not require the listing of each subdomain. If the --trim-subdomains option is enabled subdomain changes wont subvert blocking.

Using dnsmasq has another benefit; caching repeated DNS queries decreases the time it takes to load web pages.

```
$./dnsmasq-blacklist -h
usage: dnsmasq-blacklist [-h] [--output OUTPUT] [--trim-subdomains] [--hosts]
                         [--whitelist WHITELIST] [--keep]
                         [urls [urls ...]]

positional arguments:
  urls                  optional hosts file url(s)
                        defaults to:
                        http://winhelp2002.mvps.org/hosts.txt
                        http://someonewhocares.org/hosts/hosts
                        
                        local files can also be specified:
                        file://some_file

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       write to file (default is stdout)
  --trim-subdomains     do not include subdomains (see --whitelist)
                        example:
                            analytics.google.com will block google.com and all
						subdomains. This option is not enabled by default, you
						may want to enable it if you are using dnsmasq and are
						willing to maintain a `--whitelist` file for domains
						that are inadvertently blocked, the effect is the vast
						majority of ad-serving domains are blocked at their top
						domain name, otherwise the subdomain can be changed and
						ads served until the lists are updated with the new 
						subdomains.
  --hosts               generate /etc/hosts format file
                        (not useful with --trim-subdomains since hosts files can't
						block subdomains unless explicitly specified)
  --whitelist WHITELIST
                        file containing DNS names to whitelist
                        example:
                            stackexchange.com
                            stackoverflow.com
  --keep                save remote hosts files as hosts.timestamp in the current
						folder


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

`[1]:`
 `http://winhelp2002.mvps.org/hosts.txt`
 `http://someonewhocares.org/hosts/hosts`
