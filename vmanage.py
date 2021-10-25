import requests
import json
import lib.o365 as o365
import time
import lib.ipReg as ipReg
import sys
from lib.config import Config
from lib.dig import getARecords

def getSession(url: str, uid: str, pwd: str, verify: bool = True, verbose: bool = False, *args, **kwargs) -> tuple:  
    s = requests.session()
    if verbose:
        print("Initialising Session")
        print("Logging in to https://{}/j_security_check".format(url))
    r = s.post("https://{}/j_security_check".format(url),data={"j_username":uid,"j_password":pwd}, verify=verify)
    if verbose:
        print("Response: {}".format(r.text))
        print("Retrieving client XSRF token")
    t = s.get("https://{}/dataservice/client/token".format(url))
    if verbose:
        print("Response: {}".format(t.text))
    t = t.text
    if b"<html>" in  r.content:
        exit("vManage login failed")
    return s, t


def getDataPrefixList(s: requests.sessions.Session, url: str, port: int, list_name: str, verify: bool = True, verbose: bool = False, *args, **kwargs) -> str:
    if verbose:
        print("Retrieving data prefix list from: https://{}:{}/dataservice/template/policy/list/dataprefix".format(url, port))
    r = s.get("https://{}:{}/dataservice/template/policy/list/dataprefix".format(url, port), verify = verify)
    if verbose:
        print("Response: {}".format(r.text))
    js = r.json()
    list_id = ""
    entries = js['data']
    if verbose:
        print("data response: {} ".format(entries))
    for entry in entries:
        if entry['name'] == list_name:
            list_id = entry["listId"]
            if verbose:
                print("list name matches configuration. listId: {}".format(list_id))
    return list_id


def updateDataPrefixList(s: requests.sessions.Session, url: str, port: int, list_id: str, list_name: str, verify: bool, headers: dict, ipv4: list, ipv6: list, retries: int, timeout: int, user_defined_entries: list = [], verbose: bool = False, *args, **kwargs) -> str:
    data = {
        "name" :list_name,
        "entries": [
        ]
    }
    if verbose:
        print("Creating data prefix list structure. ")
    for ip in ipv4:
        if verbose:
            print("Adding entry: {}".format(ip))
        data["entries"].append({"ipPrefix":ip})
    
    
    if verbose:
        print("Processing user defined entries")
    for entry in user_defined_entries:
        if ipReg.isFQDN(entry):
            if verbose:
                print("FQDN Record: {}".format(entry))
            records = getARecords(entry)
            if verbose:
                print("A Record(s): {}".format(records))
            for record in records:
                if ipReg.isIPv4(record) and (record[-2] == "/" or record[-3] == "/"):
                    data["entries"].append({"ipPrefix":"{}".format(record)})
                    if verbose:
                        print("Adding CIDR Entry: {}".format(record))
                elif ipReg.isIPv4(record):
                    if verbose:
                        print("Adding /32 entry: {}/32".format(record))
                    data["entries"].append({"ipPrefix":"{}/32".format(record)})
            del records
        elif ipReg.isIPv4(entry):
            if verbose:
                print("Adding entry: {}".format(entry))
            data["entries"].append({"ipPrefix":"{}/32".format(entry) if '/' not in entry else entry})

    success = False
    attempts = 1

    if verbose:
        print("Putting new data prefix list data into vManage")
    while success == False and attempts <= retries:
        if verbose:
            print("Put request to: https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id))
        r = s.put("https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id), headers=headers, verify=verify, data=json.dumps(data))
        if verbose:
            print("Response: {}".format(r.text))
        if "error" in r.json().keys():
            print("\nError:\n ", r.json()["error"]["message"], "\n ", r.json()["error"]["details"], "\n")
            if attempts == retries:
                print("Exceeded attempts {} of {}".format(attempts, retries))
                exit(-1)
            else:
                print("Trying again in {} seconds, attempt {} of {}".format(timeout, attempts, retries))
            attempts += 1
            time.sleep(timeout)
        else:
            if verbose:
                print("Successfully loaded new data prefix list entries")
            success = True
            continue

    if verbose:
        print("Fetching activated ID from: https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id))
    r = s.get("https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id), headers=headers, verify=verify)
    if verbose:
        print("Response: {}".format(r.text))
    js = r.json()
    pol_id = js["activatedId"] if 'activatedId' in js.keys() else ""
    return pol_id


def activatePolicies(s: requests.sessions.Session, url: str, port: int, verify: bool, headers: dict, pol_id: str, retries: int, timeout: int, verbose: bool = False, *args, **kwargs) -> None:
    attempts = 1
    success = False
    while success == False and attempts <= retries:
        r = s.post("https://{}:{}/dataservice/template/policy/vsmart/activate/{}".format(url, port, pol_id), headers=headers, data="{}",verify=verify)
        if r.status_code == 200:
            print("vSmart Activate Triggered")
            success = True
        else:
            print(r.status_code, r.text)
            if attempts == retries:
                print("Exceeded attempts {} of {}".format(attempts, retries))
                exit(-1)
            else:
                print("Trying again in {} seconds, attempt {} of {}".format(timeout, attempts, retries))
            attempts += 1
            time.sleep(timeout)


def main() -> None:
    if verbose:
        print("Retrieving latest O365 list version")
    o365_version = o365.getRSSVersion(proxies, verbose)

    if verbose:
        print("Version received: {}".format(o365_version))

    if config["o365_version"] == o365_version:
        print("No updates from o365. Skipping")
        return
    print("Last saved o365 list version: {} new version: {}. Continuing.".format(config["o365_version"], o365_version))

    headers = {
        "Content-Type":"application/json",
        "Accept":"application/json"
    }
    if verbose:
        print("Setting content headers: {}".format(headers))

    if verbose:
        print("Retrieving Session Token")
    s, headers['X-XSRF-TOKEN'] = getSession(config["vmanage_address"], 
        config["vmanage_user"], 
        config["vmanage_password"], 
        config["ssl_verify"]
    )
    if verbose:
        print("Session Token: {}".format(headers['X-XSRF-TOKEN']))
        print("Retrieving Data Prefix List")
    
    data_prefix_list = getDataPrefixList(s, 
        config["vmanage_address"], 
        config["vmanage_port"], 
        config["vmanage_data_prefix_list"], 
        config["ssl_verify"],
        verbose
    )
    if verbose:
        print("Data Prefix List ID: {}".format(data_prefix_list))

    if data_prefix_list == "":
        print("Data Prefix List Not Found {}".format(data_prefix_list))
        return
    
    if verbose:
        print("Retrieving O365 IP Addresses")
    ipv4, ipv6 = o365.getIPs(proxies = proxies, verbose = verbose)
    if type(ipv4) == bool:
        #if ipv4 is type bool then getIPs returned false, ipv6 is the error message
        print(ipv6)
        exit(-1)
    if verbose:
        print(ipv4)


    if verbose:
        print("Updating data prefix list")
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
        config["vmanage_user_defined_entries"]
    )
    if verbose:
        print(pol_id)

    if len(pol_id) < 1:
        exit("Referenced Policies not found")


    if verbose:
        print("Activating Policies")
    for id in pol_id:
        activatePolicies(s, 
            config["vmanage_address"], 
            config["vmanage_port"], 
            config["ssl_verify"], 
            headers, 
            id, 
            config["retries"], 
            config["timeout"]
        )
    if verbose:
        print("Successfully updated poicies.")
    
    config["o365_version"] = o365_version   
    if verbose:
        print("Saving new O365 list version")
    c.rebuildConfig()


if __name__ == "__main__":
    args = sys.argv
    verbose = True if ('-v' in args or '--verbose' in args) else False    

    if verbose:
        print("Retrieving and verifying configuration file")
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
            print("Disabling SSL Verification")
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by keyboard")