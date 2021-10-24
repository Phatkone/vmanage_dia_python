import uuid
import requests
import json
import xml.etree.ElementTree as ET
from lib.ipReg import isIPv4, isIPv6

rss_url = "https://endpoints.office.com/version/worldwide?allversions=true&format=rss&clientrequestid={}".format(uuid.uuid4())
url = "https://endpoints.office.com/endpoints/worldwide?clientrequestid={}".format(uuid.uuid4())

def getIPs(optimized: bool = False, tenant: str = '', service_area: str = '', *args, **kwargs) -> tuple:
    global url
    if tenant != '':
        url = "{}&TenantName={}".format(url,tenant)
    r = requests.get(url)
    ipv4 = []
    ipv6 = []
    if r.status_code == 200:
        js = r.json()
        for entry in js:
            if "ips" in entry.keys():
                if optimized and ('category' in entry.keys() and entry['category'] != 'Optimize'):
                    continue
                if service_area != "" and entry['serviceArea'].lower() == service_area.lower():
                    for ip in entry["ips"]:
                        if isIPv4(ip):
                            if ip not in ipv4:
                                ipv4.append(ip)
                        elif isIPv6(ip):
                            if ip not in ipv6:
                                ipv6.append(ip)
                elif service_area == '':
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

def getUrls(optimized: bool = False, tenant: str = '', service_area: str = '', *args: list, **kwargs: dict):
    global url
    if tenant != '':
        url = "{}&TenantName={}".format(url,tenant)
    print(url)
    r = requests.get(url)
    urls = []
    if r.status_code == 200:
        js = r.json()
        for entry in js:
            if "urls" in entry.keys():
                if optimized and ('category' in entry.keys() and entry['category'] != 'Optimize'):
                    continue
                if service_area != "" and entry['serviceArea'].lower() == service_area.lower():
                    for ur in entry["urls"]:
                        if ur not in urls:
                            urls.append(ur)
                elif service_area == '':
                    for ur in entry["urls"]:
                        if ur not in urls:
                            urls.append(ur)
        return urls
    else:
        return r.text

def getRSSVersion():
    global rss_url
    r = requests.get(rss_url)
    if r.status_code != 200:
        return False
    try:
        xml = ET.fromstring(r.text)
        version = xml.find('channel').find('item').find('guid').text
    except ET.ParseError as e:
        print("Error retrieving O365 Version:\n> {}".format(e))
        return False
    except AttributeError as e:
        print("Error retrieving O365 Version:\n> {}".format(e))
        return False
    return version