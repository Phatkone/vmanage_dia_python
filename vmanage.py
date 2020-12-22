import requests
import json
import O365

url = "https://10.96.19.140"
uid = "admin"
pwd = "admin"
listName = "O365_DIA"


headers = {
    "Content-Type":"application/json",
    "Accept":"application/json"
}

def getSession():  
    s = requests.session()
    #s.headers = headers
    r = s.post("{}/j_security_check".format(url),data={"j_username":uid,"j_password":pwd}, verify=False)
    t = s.get("{}/dataservice/client/token".format(url))
    t = t.text
    if b"<html>" in  r.content:
        exit("login failed")
    return s, t


s, headers['X-XSRF-TOKEN'] = getSession()
r = s.get("{}/dataservice/template/policy/list/dataprefix".format(url), verify=False)
js = r.json()
listId = ""
values = []
entries = js['data']
for entry in entries:
    if entry['name'] == listName:
        listId = entry["listId"]
        values = entry["entries"]

data = {
    "name" :listName,
    "entries": [
    ]
}
ipv4, ipv6 = O365.getIps()
if type(ipv4) == bool:
    print(ipv6)
    exit()

for ip in ipv4:
    data["entries"].append({"ipPrefix":ip})

r = s.put("{}/dataservice/template/policy/list/dataprefix/{}".format(url, listId), headers=headers, verify=False, data=json.dumps(data))
#print(json.dumps(r.json(), indent=4))
if "error" in r.json().keys():
    print("\nError:\n ", r.json()["error"]["message"], "\n ", r.json()["error"]["details"], "\n")
    exit()

r = s.get("{}/dataservice/template/policy/list/dataprefix/{}".format(url, listId), headers=headers, verify=False)
print(json.dumps(r.json(), indent=4))
js = r.json()
polId = js["activatedId"]


if len(polId) == 1:
    polId = polId[0]
    r = s.post("{}/dataservice/template/policy/vsmart/activate/{}".format(url, polId), headers=headers, data="{}",verify=False)
    if r.status_code == 200:
        print("VSmart Activate Triggered")
    else:
        print(r.status_code, r.text)
elif len(polId) > 1:
    for id in polId:
        r = s.post("{}:8443/dataservice/template/policy/vsmart/activate/{}".format(url, id),verify=False)
        if r.status_code == 200:
            print("VSmart Activate Triggered")
        else:
            print(r.status_code, r.text)


if __name__ == "__main__":
    config = json.load("dia-config.json")
    main()