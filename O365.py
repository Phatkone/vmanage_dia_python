import uuid
import requests
import json
import re

url = "https://endpoints.office.com/endpoints/worldwide?clientrequestid={}".format(uuid.uuid4())
regexv4 = "^(\d{1,2}\.|[0-1][0-9][0-9]\.|2[0-4][0-9]\.|25[0-5]\.){3}(\d{1,2}|[0-1][0-9][0-9]|2[0-4][0-9]|25[0-5])\/\d{1,2}$"
regexv6 = "^[0-9a-f]{1,4}:[0-9a-f:]+\/\d{1,3}$p/i"

def getIps(serviceArea = ''):
    r = requests.get(url)
    ipv4 = []
    ipv6 = []
    if r.status_code == 200:
        js = r.json()
        for entry in js:
            if "ips" in entry.keys():
                if serviceArea != "" and entry['serviceArea'].lower() == serviceArea.lower():
                    for ip in entry["ips"]:
                        if re.match(regexv4, ip):
                            if ip not in ipv4:
                                ipv4.append(ip)
                        elif re.match(regexv6, ip):
                            if ip not in ipv6:
                                ipv6.append(ip)
                elif serviceArea == '':
                    for ip in entry["ips"]:
                        if re.match(regexv4, ip):
                            if ip not in ipv4:
                                ipv4.append(ip)
                        elif re.match(regexv6, ip):
                            if ip not in ipv6:
                                ipv6.append(ip)
        return ipv4, ipv6
    else:
        return False, r.text

def getUrls(serviceArea = ''):
    r = requests.get(url)
    urls = []
    if r.status_code == 200:
        js = r.json()
        for entry in js:
            if "urls" in entry.keys():
                if serviceArea != "" and entry['serviceArea'].lower() == serviceArea.lower():
                    for ur in entry["urls"]:
                        if ur not in urls:
                            urls.append(ur)
                elif serviceArea == '':
                    for ur in entry["urls"]:
                        if ur not in urls:
                            urls.append(ur)
        return urls
    else:
        return r.text