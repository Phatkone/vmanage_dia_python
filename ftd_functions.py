import json
import requests



def grantToken(url, usr, pwd):
    data = {
        "grant_type":"password",
        "username":usr,
        "password":pwd
    }
    js = json.dumps(data)
    headers = {"content-Type":"application/json","Accept":"application/json"}
    r = requests.post("{}/api/fdm/latest/fdm/token".format(url),data=js,headers=headers,verify=False)
    if r.status_code == 200:
        return r.json()
    else:
        print(r.status_code, r.text)
        return False 
