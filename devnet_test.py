import requests
import json
import ftd_functions

fwl = "https://10.10.20.65"
uid = "admin"
pwd = "Cisco1234!"
getToken = ftd_functions.grantToken(fwl,uid,pwd)

if type(getToken) != bool:
    token = getToken["access_token"]
    print("Token = {} \r\n".format(token))
else:
    token = ""
print(getToken)
exit()
headers = {
    "Authorization":"Bearer {}".format(token),
    "Accept":"application/json",
    "Content-Type":"application/json"
}

if token != "":
    r = requests.get("{}/api/fdm/latest/devices/default/action/provision".format(fwl), headers = headers, verify=False)
    print(r.text)
else:
    exit()

j = r.json()
body = {
    'acceptEULA': True,
    'eulaText': j['items'][0]['eulaText'],
    'type': 'initialprovision'
}

r = requests.post("{}/api/fdm/latest/devices/default/action/provision".format(fwl), headers=headers, verify=False, data=json.dumps(body))
print(r.text)

body = {
    "type":"smartagentconnection",
    "connectionType":"EVALUATION"
}

r = requests.post("{}/api/fdm/latest/license/smartagentconnections".format(fwl), headers=headers, verify=False, data=json.dumps(body))
print(r.text)

