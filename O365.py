import uuid
import requests
import json
from ipReg import isIPv4, isIPv6

url = "https://endpoints.office.com/endpoints/worldwide?clientrequestid={}".format(uuid.uuid4())

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
                        if isIPv4(ip):
                            if ip not in ipv4:
                                ipv4.append(ip)
                        elif isIPv6(ip):
                            if ip not in ipv6:
                                ipv6.append(ip)
                elif serviceArea == '':
                    for ip in entry["ips"]:
                        if isIPv4(ip):
                            if ip not in ipv4:
                                ipv4.append(ip)
                        elif isIPv6(ip):
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