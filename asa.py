import requests
import sys
#import o365
import ipReg
import json
from config import Config

def getAuthToken(c):
    r = requests.post("https://{}/api/tokenservices".format(c['ftd_address']), data='', auth=(c['ftd_user'], c['ftd_password']), verify=c['ssl_verify'], headers={'content-type':"application/json"})
    if "X-Auth-Token" in r.headers.keys():
        return r.headers['X-Auth-Token']
    else:
        print("Error: {} - {}".format(r.status_code, r.content.splitlines()[0]))
        return False
    
def main(**kwargs):
    c = Config()
    if c.checkConfig() == False:
        c.rebuildConfig()
        exit("Check config and try again")
    config = c.config
    if config["ssl_verify"] == False:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    config["ftd_user"] = 'admin'
    config["ftd_password"] = 'secret'
    config["ftd_address"] = '192.168.100.221'

    key = getAuthToken(config)
    if key == False:
        print("Unable to retrieve auth token.")
        return
    
    headers= {
        'content-type':"application/json",
        'accept':'application/json',
        'X-Auth-Token':key
    }

    """
    #this section not used unless we want the full list... which wont work due to size limitations in ASA
    urls = o365.getUrls()
    if type(urls) == str:
        print(urls)
        exit(-1)
    fqdns = []
    for url in urls:
        if ipReg.isFQDN(url):
            fqdns.append(url)
    for url in config["ftd_user_defined_entries"]:
        if ipReg.isFQDN(url):
            print(url)
            for u in fqdns:
                if url in u:
                    fqdns = [x for x in fqdns if x != u]
    
    for url in fqdns:
        print(url)
    del urls
    """
    urls = []
    for url in config["ftd_user_defined_entries"]:
        if ipReg.isFQDN(url):
            urls.append(url)

    data = {
        "commands": [
            "no anyconnect-custom-data dynamic-split-exclude-domains {}".format(config["ftd_prefix_list"]),
            "anyconnect-custom-data dynamic-split-exclude-domains {} {}".format(config["ftd_prefix_list"],",".join(urls)),
            "show running-config | include anyconnect-custom-data dynamic-split-exclude-domains"
            ]
        }
    r = requests.post("https://{}/api/cli".format(config['ftd_address']), verify=config['ssl_verify'], headers=headers, data=json.dumps(data))
    print(json.dumps(r.json()["response"], indent=2))

    requests.post("https://{}/commands/writemem".format(config['ftd_address']), verify=config['ssl_verify'], headers=headers)

if __name__ == '__main__':
    main(**dict(arg.split("=",1) for arg in sys.argv[1:]))