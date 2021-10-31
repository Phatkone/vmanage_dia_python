import uuid
import requests
import json
import xml.etree.ElementTree as ET
from lib.ipReg import isIPv4, isIPv6
from lib.cprint import cprint


def getIPs(instance: str = "WorldWide", optimized: bool = False, tenant: str = '', service_area: str = '', proxies: dict = {}, verbose: bool = False, *args, **kwargs) -> tuple:
    url = "https://endpoints.office.com/endpoints/{}?clientrequestid={}".format(instance, uuid.uuid4())
    if tenant != '' and tenant is not None:
        url = "{}&TenantName={}".format(url, tenant)
        if verbose:
            cprint("Setting TenantName: {}".format(tenant), "purple")
    if service_area != '' and service_area is not None:
        url = "{}&ServiceAreas={}".format(url, service_area)
        if verbose:
            cprint("Setting ServiceArea: {}".format(service_area), "purple")

    if verbose:
        cprint("Getting IP list from: {}".format(url), "purple")
        if len(proxies) > 0:
            cprint("Proxies configured: {}".format(proxies), "yellow")
    r = requests.get(url, proxies = proxies)
    ipv4 = []
    ipv6 = []
    if verbose:
        cprint("Response: {}".format(r.text), "green")
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
    url = "https://endpoints.office.com/endpoints/{}?clientrequestid={}".format(instance, uuid.uuid4())
    if tenant != '':
        url = "{}&TenantName={}".format(url, tenant)
        if verbose:
            cprint("Setting TenantName", "purple")
    if service_area != '' and service_area is not None:
        url = "{}&ServiceAreas={}".format(url, service_area)
        if verbose:
            cprint("Setting ServiceArea: {}".format(service_area), "purple")
    if verbose:
        cprint("Getting IP list from: {}".format(url), "purple")
        if len(proxies) > 0:
            cprint("Proxies configured: {}".format(proxies), "yellow")
    r = requests.get(url, proxies = proxies)
    urls = []
    if verbose:
        cprint("Response: {}".format(r.text), "purple")
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

def getRSSVersion(instance: str = "WorldWide", proxies: dict = {}, verbose: bool = False):
    rss_url = "https://endpoints.office.com/version/{}?allversions=true&format=rss&clientrequestid={}".format(instance, uuid.uuid4())
    if verbose:
        cprint("Getting RSS Feed from: {}".format(rss_url), "purple")
        if len(proxies) > 0:
            cprint("Proxies configured: {}".format(proxies), "purple")
    r = requests.get(rss_url, proxies = proxies)
    if verbose:
        cprint("Response: {}".format(r.text), "green")
    if r.status_code != 200:
        return False
    try:
        xml = ET.fromstring(r.text)
        version = xml.find('channel').find('item').find('guid').text
        if verbose:
            cprint("Retrieving GUID from RSS XML: {}".format(version), "green")
    except ET.ParseError as e:
        cprint("Error retrieving O365 Version:\n> {}".format(e), "red")
        return False
    except AttributeError as e:
        cprint("Error retrieving O365 Version:\n> {}".format(e), "red")
        return False
    return version