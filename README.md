# o365 Dynamic Updater for vManage Data Prefix List

## Purpose
This tool dynamically updates a Data Prefix List in vManage with Microsoft o365 IPv4 addresses.  
Additional direct internet addresses and subnets can be added through the configuration file as IPv4 addresses or FQDNs (no wildcards).  
The o365 list can be manipulated to only populate the optimize tagged addresses or even specific tenancies.  
Note. Any existing entries in the data prefix list will be removed when the script runs, include these in the user defined entries within the configuration file.

## Requirements
This script has been built for python3. No testing has been performed on python2 and as such is not supported.  
The following pip packages are required for operation:
 - requests
 - dnspythong
 - json

## Configuration File
All configuration is in the dia-config.json file.

The script will generate any missing properties.

The format is as follows:
```
{
    # Username/Password for vManage session - strings
    "vmanage_user": "admin",
    "vmanage_password": "admin",
    # IP or FQDN and port for vManage API access - string and integer
    "vmanage_address": "10.1.1.254",
    "vmanage_port": 443,
    # Data Prefix List to update. - string
    "vmanage_data_prefix_list": "O365_DIA",
    # User defined entries to include in the data prefix list beyond the o365 addresses. - List of strings.
    "vmanage_user_defined_entries": [
        "cisco.com",
        "8.8.8.8",
        "1.1.1.1/32"
    ],
    # Policy activation retry attempts and timeout between attempts - integers
    "retries": 5,
    "timeout": 1,
    # SSL verification. May need to set to false if the certificate for vManage isn't trusted or if a web proxy with SSL decryption is utilised - boolean
    "ssl_verify": false,
    # http/https proxy if used by the environment. false if unused, string if used. Pass credentials if necessary as http basic auth syntax.
    # These proxies are only applied for the O365 list requests, calls to vManage do not use the proxies.
    "http_proxy": false,
    "https_proxy": "username:password@10.1.1.1:8080",
    # Microsoft Instance - string: Worldwide, USGovDoD, USGovGCCHigh, China, Germany
    "instance": "WorldWide",
    # Microsoft Optimized list only. - boolean
    "optimized": false,
    # Tenant if retrieving specific addresses only. - string
    "tenant": null,
    # Microsoft o365 service area. - string: Common, Exchange, SharePoint, Skype or null
    "service_area": null,
    # DNS server address (single) - string
    "dns_server": "1.1.1.1",
    # Version pulled from o365 RSS feed. This is automatically updated by the script, do not set this field.
    "o365_version": "0"
}
```

## Usage
Call vManage.py to execute.
main.py will call vManage.py every 86,400 seconds (24 hours) if you wish to have it run by itself.
*This is not advised. Recommend using a cron job to schedule the script for recurring use.*

This script can run with --verbose or -v for verbose run and --dry or -d for a dry run.

## License
[GNU GPL 3.0](LICENSE) License applies.

## Author
Craig B. [Phatkone](https://github.com/Phatkone)
```
           ,,,
          (. .)
-------ooO-(_)-Ooo-------
```