from config import Config
import requests
import json
import O365

expectedResponses = {
    "get" : 200,
    "post" : 200,
    "put" : 200,
    "delete" : 204
}

def getToken(url, port, usr, pwd, verify=True):
    data = {
        "grant_type":"password",
        "username":usr,
        "password":pwd
    }
    js = json.dumps(data)
    headers = {
        "Content-Type":"application/json",
        "Accept":"application/json"
    }
    r = requests.post("https://{}:{}/api/fdm/latest/fdm/token".format(url, port),data=js,headers=headers,verify=False)
    if r.status_code == 200:
        return r.json()
    else:
        print(r.status_code, r.text)
        return False 

def deployConfig(url, port, headers, verify):
    return requests.post("https://{}:{}/api/fdm/latest/operational/deploy".format(url,port), headers=headers,data={},verify=verify)


#def createFlexObject(url,port,headers,verify,data)

def main():
    tokenReq = getToken(config["ftd_address"], config["ftd_port"], config["ftd_user"], config["ftd_password"], config["ssl_verify"])
    if type(tokenReq) != bool:
        token = tokenReq["access_token"]
        print("Token = {} \r\n".format(token))
    else:
        token = ""
    headers = {
        "Authorization":"Bearer {}".format(token),
        "Accept":"application/json",
        "Content-Type":"application/json"
    }

    flexPolicy = {
        "flexConfigObjects":[
            {
                "type": "FlexConfigObject",
                "name": "testFlexConfigObject"
            }
        ],
        "name": "testFlexConfigPolicy",
        "type": "flexconfigpolicy"
    }

    flexObject = {
        "name": "testFlexConfigObject",
        "description": "Test flex config object",
        "lines": [
            "webvpn",
            "anyconnect-custom-attr dynamic-split-exclude-domains description exclude traffic for the following domains",
            "anyconnect-custom-data dynamic-split-exclude-domains excludeddomains $urls"
        ],
        "isBlacklisted": "false",
        "variables": [
            {
            "name": "urls",
            "variableType": "STRING",
            "value": "test.com, test2.com",
            "type": "flexvariable"
            }
        ],
        "type": "flexconfigobject"
    }
    r = requests.post("https://{}:{}/api/fdm/latest/object/flexconfigobjects".format(config["ftd_address"],config["ftd_port"]), verify=config["ssl_verify"], headers=headers, data=json.dumps(flexObject))
    print(r.text)
    r = requests.post("https://{}:{}/api/fdm/latest/object/flexconfigpolicies".format(config["ftd_address"],config["ftd_port"]), verify=config["ssl_verify"], headers=headers, data=json.dumps(flexPolicy))
    print(r.text)
    r = requests.get("https://{}:{}/api/fdm/latest/object/flexconfigobjects".format(config["ftd_address"],config["ftd_port"]), verify=config["ssl_verify"], headers=headers)
    print(r.text)
    r = requests.get("https://{}:{}/api/fdm/latest/object/flexconfigpolicies".format(config["ftd_address"],config["ftd_port"]), verify=config["ssl_verify"], headers=headers)
    print(r.text)

    dep = deployConfig(config["ftd_address"], config["ftd_port"],headers,config["ssl_verify"])
    if dep.status_code == 200:
        print(dep.json())


if __name__ == "__main__":
    c = Config()
    if c.checkConfig() == False:
        c.rebuildConfig()
        exit("Check config and try again")
    config = c.config
    if config["ftd_address"][0:8] == "https://":
        config["ftd_address"] = config["ftd_address"].replace("https://","")
    if config["ssl_verify"] == False:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()