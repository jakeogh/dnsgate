# dnsmasq-blacklist

[dnsmasq](https://wiki.gentoo.org/wiki/Dnsmasq) allows wildcard blocking of domains, for example, to block *.google.com:

```
echo 'address=/.google.com/127.0.0.1' >> /etc/dnsmasq.conf
```

dnsmasq-blacklist reads two popular /etc/hosts blocking lists and converts to dnsmasq.conf format

