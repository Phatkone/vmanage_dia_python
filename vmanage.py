import requests
import json
import o365
import time
import ipReg
from config import Config
from dig import getARecords

def getSession(url: str, uid: str, pwd: str, verify: bool = True) -> tuple:  
    s = requests.session()
    r = s.post("https://{}/j_security_check".format(url),data={"j_username":uid,"j_password":pwd}, verify=verify)
    t = s.get("https://{}/dataservice/client/token".format(url))
    t = t.text
    if b"<html>" in  r.content:
        exit("vManage login failed")
    return s, t


def getDataPrefixList(s: requests.sessions.Session, url: str, port: int, list_name: str, verify: bool = True) -> str:
    r = s.get("https://{}:{}/dataservice/template/policy/list/dataprefix".format(url, port), verify = verify)
    js = r.json()
    list_id = ""
    entries = js['data']
    for entry in entries:
        if entry['name'] == list_name:
            list_id = entry["listId"]
    return list_id


def updateDataPrefixList(s: requests.sessions.Session, url: str, port: int, list_id: str, list_name: str, verify: bool, headers: dict, ipv4: list, ipv6: list, retries: int, timeout: int, user_defined_entries: list = []) -> str:
    data = {
        "name" :list_name,
        "entries": [
        ]
    }
    
    for ip in ipv4:
        data["entries"].append({"ipPrefix":ip})
    for entry in user_defined_entries:
        if ipReg.isFQDN(entry):
            records = getARecords(entry)
            print(entry, records)
            for record in records:
                if ipReg.isIPv4(record) and (record[-2] == "/" or record[-3] == "/"):
                    data["entries"].append({"ipPrefix":"{}".format(record)})
                elif ipReg.isIPv4(record):
                    data["entries"].append({"ipPrefix":"{}/32".format(record)})
            del records
        elif ipReg.isIPv4(entry):
            print(entry)
            data["entries"].append({"ipPrefix":"{}/32".format(entry)})
    success = False
    attempts = 1

    while success == False and attempts <= retries:
        r = s.put("https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id), headers=headers, verify=verify, data=json.dumps(data))
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
            success = True
            continue

    r = s.get("https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, list_id), headers=headers, verify=verify)
    js = r.json()
    pol_id = js["activatedId"]
    return pol_id


def activatePolicies(s: requests.sessions.Session, url: str, port: int, verify: bool, headers: dict, pol_id: str, retries: int, timeout: int) -> None:
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
    o365_version = o365.getRSSVersion()
    if config["o365_version"] == o365_version:
        print("No updates from o365. Skipping")
        return
    print("Last saved o365 list version: {} new version: {}. Continuing.".format(config["o365_version"], o365_version))

    headers = {
        "Content-Type":"application/json",
        "Accept":"application/json"
    }
    s, headers['X-XSRF-TOKEN'] = getSession(config["vmanage_address"], 
        config["vmanage_user"], 
        config["vmanage_password"], 
        config["ssl_verify"]
    )
    data_prefix_list = getDataPrefixList(s, 
        config["vmanage_address"], 
        config["vmanage_port"], 
        config["vmanage_data_prefix_list"], 
        config["ssl_verify"]
    )
    if data_prefix_list == "":
        print("")
        return
    ipv4, ipv6 = o365.getIPs()
    if type(ipv4) == bool:
        #if ipv4 is type bool then getIPs returned false, ipv6 is the error message
        print(ipv6)
        exit(-1)

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

    if len(pol_id) < 1:
        exit("Referenced Policies not found")


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
    
    print("Successfully updated poicies.")
    config["o365_version"] = o365_version
    c.rebuildConfig()


if __name__ == "__main__":
    c = Config()
    if c.checkConfig() == False:
        c.rebuildConfig()
        exit("Check config and try again")
    config = c.config
    if config["vmanage_address"][0:8] == "https://":
        config["vmanage_address"] = config["vmanage_address"].replace("https://","")
    if config["ssl_verify"] == False:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()