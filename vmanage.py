import requests
import json
import O365

url = "https://10.96.19.140"
uid = "admin"
pwd = "admin"
listName = "O365_DIA"




def getSession(url, uid, pwd, verify=True):  
    s = requests.session()
    #s.headers = headers
    r = s.post("https://{}/j_security_check".format(url),data={"j_username":uid,"j_password":pwd}, verify=verify)
    t = s.get("https://{}/dataservice/client/token".format(url))
    t = t.text
    if b"<html>" in  r.content:
        exit("vManage login failed")
    return s, t

def getDataPrefixList(s, url, verify=True):
    r = s.get("https://{}/dataservice/template/policy/list/dataprefix".format(url), verify=verify)
    js = r.json()
    listId = ""
    values = []
    entries = js['data']
    for entry in entries:
        if entry['name'] == listName:
            listId = entry["listId"]
    return listId

def updateDataPrefixList(s, url, verify, ipv4, ipv6, retries, wait)
    data = {
        "name" :listName,
        "entries": [
        ]
    }
    

    for ip in ipv4:
        data["entries"].append({"ipPrefix":ip})

    r = s.put("{}/dataservice/template/policy/list/dataprefix/{}".format(url, listId), headers=headers, verify=verify, data=json.dumps(data))

    if "error" in r.json().keys():
        print("\nError:\n ", r.json()["error"]["message"], "\n ", r.json()["error"]["details"], "\n")
        exit()

    r = s.get("{}/dataservice/template/policy/list/dataprefix/{}".format(url, listId), headers=headers, verify=verify)
    #print(json.dumps(r.json(), indent=4))
    js = r.json()
    polId = js["activatedId"]
    return polId

def activatePolicies(s, url, verify, polId, retries, wait)
    if len(polId) == 1:
        polId = polId[0]
        r = s.post("{}/dataservice/template/policy/vsmart/activate/{}".format(url, polId), headers=headers, data="{}",verify=verify)
        if r.status_code == 200:
            print("VSmart Activate Triggered")
        else:
            print(r.status_code, r.text)
    elif len(polId) > 1:
        for id in polId:
            r = s.post("{}/dataservice/template/policy/vsmart/activate/{}".format(url, polId), headers=headers, data="{}",verify=verify)
            if r.status_code == 200:
                print("VSmart Activate Triggered")
            else:
                print(r.status_code, r.text)

def main():
    headers = {
        "Content-Type":"application/json",
        "Accept":"application/json"
    }
    s, headers['X-XSRF-TOKEN'] = getSession(config["vmanage_address"], config["vmanage_user"], config["vmanage_password"])
    dataPrefixList = getDataPrefixList(s, config["vmanage_address"], config["ssl_verify"])
    if dataPrefixList == "":
        print("")
        return
    
    ipv4, ipv6 = O365.getIps()
    if type(ipv4) == bool:
        print(ipv6)
        exit()
    poldId = updateDataPrefixList(s, config["vmanage_address"], config["verify"], ipv4, ipv6, config["retries"], config["timeout"])
    if len(polId) < 1:
        exit("Referenced Policies not found")


if __name__ == "__main__":
    config = json.load("dia-config.json")
    if config["vmanage_address"][0:8] == "https://":
        config["vmanage_address"] = config["vmanage_address"].replace("https://","")
    if config["ssl_verify"] == False:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()