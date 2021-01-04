dynamic updating of split tunneling destinations for Cisco FTD/ASA and vManage

dia-config.json contains all required configurables.

Requires dnspython and requests python modules.
Built for Python 3

utilises dnspython, json, re, urllib3 and requests

-- asa.py --
requires API agent installed and running,
will update anyconnect custom data for the named prefix list to have the urls defined in user_defined_entries (no wildcards)

-- fdm.py --
still work in progress. creates flexobject for anyconnect, however, fdm currently rejects the commands as blacklisted

-- vmanage.py --
updates the data prefix list with all ipv4 entries, any user defined entries will have their respective a-records pulled and updated accordingly