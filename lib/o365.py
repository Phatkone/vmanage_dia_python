import uuid
import requests
import json
import xml.etree.ElementTree as ET
from lib.ipReg import isIPv4, isIPv6

rss_url = "https://endpoints.office.com/version/<instance>?allversions=true&format=rss&clientrequestid={}".format(uuid.uuid4())
url = "https://endpoints.office.com/endpoints/<instance>?clientrequestid={}".format(uuid.uuid4())

def getIPs(instance: str = "WorldWide", optimized: bool = False, tenant: str = '', service_area: str = '', proxies: dict = {}, verbose: bool = False, *args, **kwargs) -> tuple:
    global url
    url = url.replace('<instance>', instance)
    if tenant != '' and tenant is not None:
        url = "{}&TenantName={}".format(url, tenant)
        if verbose:
            print("Setting TenantName: {}".format(tenant))
    if service_area != '' and service_area is not None:
        url = "{}&ServiceAreas={}".format(url, service_area)
        if verbose:
            print("Setting ServiceArea: {}".format(service_area))

    if verbose:
        print("Getting IP list from: {}".format(url))
        if len(proxies) > 0:
            print("Proxies configured: {}".format(proxies))
    r = requests.get(url, proxies = proxies)
    ipv4 = []
    ipv6 = []
    if verbose:
        print("Response: {}".format(r.text))
    if r.status_code == 200:
        js = r.json()
        for entry in js:
            if "ips" in entry.keys():
                if optimized and ('category' in entry.keys() and entry['category'] != 'Optimize'):
                    continue
                if service_area != "" and service_area is not None and entry['serviceArea'].lower() == service_area.lower():
                    for ip in entry["ips"]:
                        if isIPv4(ip):
                            if ip not in ipv4:
                                ipv4.append(ip)
                        elif isIPv6(ip):
                            if ip not in ipv6:
                                ipv6.append(ip)
                elif service_area == '' or service_area is None:
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

def getUrls(instance: str = "WorldWide", optimized: bool = False, tenant: str = '', service_area: str = '', proxies: dict = {}, verbose: bool = False, *args: list, **kwargs: dict):
    global url
    url = url.replace('<instance>', instance)
    if tenant != '':
        url = "{}&TenantName={}".format(url, tenant)
        if verbose:
            print("Setting TenantName")
    if service_area != '' and service_area is not None:
        url = "{}&ServiceAreas={}".format(url, service_area)
        if verbose:
            print("Setting ServiceArea: {}".format(service_area))
    if verbose:
        print("Getting IP list from: {}".format(url))
        if len(proxies) > 0:
            print("Proxies configured: {}".format(proxies))
    r = requests.get(url, proxies = proxies)
    urls = []
    if verbose:
        print("Response: {}".format(r.text))
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

def getRSSVersion(proxies: dict = {}, verbose: bool = False):
    global rss_url
    if verbose:
        print("Getting RSS Feed from: {}".format(rss_url))
        if len(proxies) > 0:
            print("Proxies configured: {}".format(proxies))
    r = requests.get(rss_url, proxies = proxies)
    if verbose:
        print("Response: {}".format(r.text))
    if r.status_code != 200:
        return False
    try:
        xml = ET.fromstring(r.text)
        version = xml.find('channel').find('item').find('guid').text
        if verbose:
            print("Retrieving GUID from RSS XML: {}".format(version))
    except ET.ParseError as e:
        print("Error retrieving O365 Version:\n> {}".format(e))
        return False
    except AttributeError as e:
        print("Error retrieving O365 Version:\n> {}".format(e))
        return False
    return version