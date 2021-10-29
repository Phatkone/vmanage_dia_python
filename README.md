# Cisco SD-WAN vManage DIA Dynamic Updater

## Purpose
This tool dynamically updates a Data Prefix List in vManage with Microsoft o365 IPv4 addresses.
Additional DIA addresses and subnets can be added through the configuration file as IPv4 addresses or FQDNs (no wildcards).


dynamic updating of split tunneling destinations for vManage

dia-config.json contains all required configurables.

Requires dnspython and requests python modules.
Built for Python 3

utilises dnspython, json, re, urllib3 and requests

-- vmanage.py --
updates the data prefix list with all ipv4 entries, any user defined entries will have their respective a-records pulled and updated accordingly
Will only run if theres a change to the latest version listed in the rss feed.