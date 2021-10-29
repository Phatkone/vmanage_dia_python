import requests
import json
import lib.o365 as o365
import time
import lib.ipReg as ipReg
import sys
from lib.bcolours import cprint
from lib.config import Config
from lib.dig import getARecords


def getSession(url: str, uid: str, pwd: str, verify: bool = True, verbose: bool = False, *args, **kwargs) -> tuple:  
    s = requests.session()
    if verbose:
        cprint("Initialising Session", 'purple')
        cprint("Logging in to https://{}/j_security_check".format(url), 'purple')
    try:
        r = s.post("https://{}/j_security_check".format(url),data={"j_username":uid,"j_password":pwd}, verify=verify)
    except requests.exceptions.ConnectionError as e:
        cprint("Unable to establish session to vManage:\n{}".format(e), 'red')
        exit()
    
    if verbose:
        cprint("Response: {}".format(r.text), 'purple')
        cprint("Retrieving client XSRF token", 'purple')
    t = s.get("https://{}/dataservice/client/token".format(url))
    if verbose:
        cprint("Response: {}".format(t.text), 'purple')
    t = t.text
    if b"<html>" in  r.content:
        cprint("vManage login failed", 'red')
        exit(-1)
    return s, t


def getDataPrefixList(s: requests.sessions.Session, url: str, port: int, list_name: str, verify: bool = True, verbose: bool = False, *args, **kwargs) -> str:
    if verbose:
        cprint("Retrieving data prefix list from: https://{}:{}/dataservice/template/policy/list/dataprefix".format(url, port), 'purple')
    r = s.get("https://{}:{}/dataservice/template/policy/list/dataprefix".format(url, port), verify = verify)
    if verbose:
        cprint("Response: {}".format(r.text), 'purple')
    js = r.json()
    list_id = ""
    entries = js['data']
    if verbose:
        cprint("data response: {} ".format(entries), 'purple')
    for entry in entries:
        if entry['name'] == list_name:
            list_id = entry["listId"]
            if verbose:
                cprint("list name matches configuration. listId: {}".format(list_id), 'purple')
    return list_id


def updateDataPrefixList(s: requests.sessions.Session, url: str, port: int, list_id: str, list_name: str, verify: bool, headers: dict, ipv4: list, ipv6: list, retries: int, timeout: int, user_defined_entries: list = [], verbose: bool = False, dry: bool = False, *args, **kwargs) -> str:
    data = {
        "name" :list_name,
        "entries": [
        ]
    }
    if verbose:
        cprint("Creating data prefix list structure. ")
    for ip in ipv4:
        if verbose:
            cprint("Adding entry: {}".format(ip))
        data["entries"].append({"ipPrefix":ip})
    
    
    if verbose:
        cprint("Processing user defined entries")
    for entry in user_defined_entries:
        if ipReg.isFQDN(entry):
            if verbose:
                cprint("FQDN Record: {}".format(entry))
            records = getARecords(entry, config['dns_server'])
            if verbose:
                cprint("A Record(s): {}".format(records))
            for record in records:
                if ipReg.isIPv4(record) and (record[-2] == "/" or record[-3] == "/"):
                    data["entries"].append({"ipPrefix":"{}".format(record)})
                    if verbose:
                        cprint("Adding CIDR Entry: {}".format(record))
                elif ipReg.isIPv4(record):
                    if verbose:
                        cprint("Adding /32 entry: {}/32".format(record))
                    data["entries"].append({"ipPrefix":"{}/32".format(record)})
            del records
        elif ipReg.isIPv4(entry):
            if verbose:
                cprint("Adding entry: {}".format(entry))
            data["entries"].append({"ipPrefix":"{}/32".format(entry) if '/' not in entry else entry})

    success = False
    attempts = 1

    if verbose or dry:
        cprint("New Data Prefix List: {}".format(json.dumps(data, indent=2)))

    if verbose:
        cprint("Putting new data prefix list data into vManage")
    while success == False and attempts <= retries:
        if verbose or dry:
            cprint("Put request to: https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id))
        if dry:
            success = True
            continue
        r = s.put("https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id), headers=headers, verify=verify, data=json.dumps(data))
        if verbose:
            cprint("Response: {}".format(r.text))
        if "error" in r.json().keys():
            cprint("\nError:\n ", r.json()["error"]["message"], "\n ", r.json()["error"]["details"], "\n")
            if attempts == retries:
                cprint("Exceeded attempts {} of {}".format(attempts, retries))
                exit(-1)
            else:
                cprint("Trying again in {} seconds, attempt {} of {}".format(timeout, attempts, retries))
            attempts += 1
            time.sleep(timeout)
        else:
            if verbose:
                cprint("Successfully loaded new data prefix list entries")
            success = True
            continue

    if verbose or dry:
        cprint("Fetching activated ID from: https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id))
    r = s.get("https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id), headers=headers, verify=verify)
    if verbose:
        cprint("Response: {}".format(r.text))
    js = r.json()
    pol_id = js["activatedId"] if 'activatedId' in js.keys() else ""
    return pol_id


def activatePolicies(s: requests.sessions.Session, url: str, port: int, verify: bool, headers: dict, pol_id: str, retries: int, timeout: int, verbose: bool = False, dry: bool = False, *args, **kwargs) -> None:
    attempts = 1
    success = False
    while success == False and attempts <= retries:
        if verbose or dry:
            cprint("Posting to activate policy at: https://{}:{}/dataservice/template/policy/vsmart/activate/{}".format(url, port, pol_id))
        if dry:
            success = True
            return
        r = s.post("https://{}:{}/dataservice/template/policy/vsmart/activate/{}".format(url, port, pol_id), headers=headers, data="{}",verify=verify)
        if verbose:
            cprint("Response: {}".format(r.text))
        if r.status_code == 200:
            cprint("vSmart Activate Triggered")
            success = True
        else:
            cprint(r.status_code, r.text)
            if attempts == retries:
                cprint("Exceeded attempts {} of {}".format(attempts, retries))
                exit(-1)
            else:
                cprint("Trying again in {} seconds, attempt {} of {}".format(timeout, attempts, retries))
            attempts += 1
            time.sleep(timeout)


def main() -> None:
    instance = config['instance']
    if verbose:
        cprint("Retrieving latest O365 list version")
    o365_version = o365.getRSSVersion(instance, proxies, verbose)

    if verbose:
        cprint("Version received: {}".format(o365_version))

    if config["o365_version"] == o365_version:
        cprint("No updates from o365. Skipping")
        return
    cprint("Last saved o365 list version: {} new version: {}. Continuing.".format(config["o365_version"], o365_version))

    headers = {
        "Content-Type":"application/json",
        "Accept":"application/json"
    }
    if verbose:
        cprint("Setting content headers: {}".format(headers))

    if verbose:
        cprint("Retrieving Session Token")
    s, headers['X-XSRF-TOKEN'] = getSession(config["vmanage_address"], 
        config["vmanage_user"], 
        config["vmanage_password"], 
        config["ssl_verify"]
    )
    if verbose:
        cprint("Session Token: {}".format(headers['X-XSRF-TOKEN']))
        cprint("Retrieving Data Prefix List")
    
    data_prefix_list = getDataPrefixList(s, 
        config["vmanage_address"], 
        config["vmanage_port"], 
        config["vmanage_data_prefix_list"], 
        config["ssl_verify"],
        verbose
    )
    if verbose:
        cprint("Data Prefix List ID: {}".format(data_prefix_list))

    if data_prefix_list == "":
        cprint("Data Prefix List Not Found {}".format(data_prefix_list))
        return
    
    if verbose:
        cprint("Retrieving O365 IP Addresses")
    optimized = bool(config['optimized'])
    tenant = config['tenant']
    service_area = config['service_area']
    ipv4, ipv6 = o365.getIPs(instance, optimized,
        tenant, 
        service_area,
        proxies, 
        verbose
    )
    if type(ipv4) == bool:
        #if ipv4 is type bool then getIPs returned false, ipv6 is the error message
        cprint(ipv6)
        exit(-1)
    if verbose:
        cprint(ipv4)


    if verbose:
        cprint("Updating data prefix list")
    
    pol_id = updateDataPrefixList(s, 
        config["vmanage_address"], 
        config["vmanage_port"], 
        data_prefix_list, 
        config["vmanage_data_prefix_list"], 
        config["ssl_verify"], 
        headers, 
        ipv4, 
        ipv6, 
        config["retries"], 
        config["timeout"], 
        config["vmanage_user_defined_entries"],
        verbose,
        dry
    )
    if verbose:
        cprint(pol_id)

    if len(pol_id) < 1:
        exit("Referenced Policies not found")

    if verbose or dry:
        cprint("Activating Policies")
    for id in pol_id:
        activatePolicies(s, 
            config["vmanage_address"], 
            config["vmanage_port"], 
            config["ssl_verify"], 
            headers, 
            id, 
            config["retries"], 
            config["timeout"],
            verbose,
            dry
        )
    if verbose:
        cprint("Successfully updated poicies.")
    
    config["o365_version"] = o365_version   
    if verbose:
        cprint("Saving new O365 list version")
    c.rebuildConfig()


if __name__ == "__main__":
    args = sys.argv
    verbose = True if ('-v' in args or '--verbose' in args) else False
    dry = True if ('-d' in args or '--dry' in args) else False

    if verbose:
        cprint("Retrieving and verifying configuration file")
    c = Config()
    if c.checkConfig() == False:
        c.rebuildConfig()
        exit("Check config and try again")
    config = c.config
    if config["vmanage_address"][0:8] == "https://":
        config["vmanage_address"] = config["vmanage_address"].replace("https://","")
    proxies = {}
    if config['http_proxy'] is not None:
        proxies['http'] = config['http_proxy']
    if config['https_proxy'] is not None:
        proxies['https'] = config['https_proxy']
    if config["ssl_verify"] == False:
        if verbose:
            cprint("Disabling SSL Verification")
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        main()
    except KeyboardInterrupt:
        cprint("Interrupted by keyboard")