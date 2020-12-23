import requests
import json
import O365
import time
from config import Config

def getSession(url, uid, pwd, verify=True):  
    s = requests.session()
    #s.headers = headers
    r = s.post("https://{}/j_security_check".format(url),data={"j_username":uid,"j_password":pwd}, verify=verify)
    t = s.get("https://{}/dataservice/client/token".format(url))
    t = t.text
    if b"<html>" in  r.content:
        exit("vManage login failed")
    return s, t

def getDataPrefixList(s, url, port, listName, verify=True):
    r = s.get("https://{}:{}/dataservice/template/policy/list/dataprefix".format(url, port), verify=verify)
    js = r.json()
    listId = ""
    values = []
    entries = js['data']
    for entry in entries:
        if entry['name'] == listName:
            listId = entry["listId"]
    return listId

def updateDataPrefixList(s, url, port, listId, listName, verify, headers, ipv4, ipv6, retries, timeout):
    data = {
        "name" :listName,
        "entries": [
        ]
    }
    
    for ip in ipv4:
        data["entries"].append({"ipPrefix":ip})
    success = False
    attempts = 1

    while success == False and attempts <= retries:
        r = s.put("https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, listId), headers=headers, verify=verify, data=json.dumps(data))
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

    r = s.get("https://{}:{}/dataservice/template/policy/list/dataprefix/{}".format(url, port, listId), headers=headers, verify=verify)
    js = r.json()
    polId = js["activatedId"]
    return polId

def activatePolicies(s, url, port, verify, headers, polId, retries, timeout):
    attempts = 1
    success = False
    while success == False and attempts <= retries:
        r = s.post("https://{}:{}/dataservice/template/policy/vsmart/activate/{}".format(url, port, polId), headers=headers, data="{}",verify=verify)
        if r.status_code == 200:
            print("VSmart Activate Triggered")
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

def main():
    headers = {
        "Content-Type":"application/json",
        "Accept":"application/json"
    }
    s, headers['X-XSRF-TOKEN'] = getSession(config["vmanage_address"], config["vmanage_user"], config["vmanage_password"], config["ssl_verify"])
    dataPrefixList = getDataPrefixList(s, config["vmanage_address"], config["vmanage_port"], config["vmanage_data_prefix_list"], config["ssl_verify"])
    if dataPrefixList == "":
        print("")
        return
    
    ipv4, ipv6 = O365.getIps()
    if type(ipv4) == bool:
        print(ipv6)
        exit(-1)
    polId = updateDataPrefixList(s, config["vmanage_address"], config["vmanage_port"], dataPrefixList, config["vmanage_data_prefix_list"], config["ssl_verify"], headers, ipv4, ipv6, config["retries"], config["timeout"])
    if len(polId) < 1:
        exit("Referenced Policies not found")
    for id in polId:
        activatePolicies(s,  config["vmanage_address"], config["vmanage_port"], config["ssl_verify"], headers, id, config["retries"], config["timeout"])


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