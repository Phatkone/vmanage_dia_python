import requests
import sys
import json
import uuid
import base64


def getAuthToken(c):
    token = ''
    r = requests.post("https://{}:{}@{}/api/mgmtaccess".format(c.usr,c.pwd,c.fwl), data='', verify=False, header={'content-type':"application/json"})
    print(r.text)
    c.apiKey = token
    return c

def main(**kwargs):
    c, msg = checkConfig()
    if msg == 'success':
        print("yes")
    else:
        print('no!', msg)
        if type(msg) is FileNotFoundError or msg == False:
            print("nop")
            mkcfg = makeConfigFile(c)
            if type(mkcfg) == bool and mkcfg == True:
                print("made it")
            else:
                print(mkcfg)
        else:
            print("here")
    #print(getAuthToken)
    urls = requests.get("{}?clientrequestid={}".format(c.srcUrl, uuid.uuid4()))
    if urls.status_code == 200:
        print(json.dumps(urls.json(),indent=2))
    else:
        print(urls.status_code, urls.text)
    return
    r = requests.get("https://{}/api/access/global/rules".format(c.fwl), auth=(c.usr, c.pwd), verify=False, headers={"Accept":'application/json','Content-Type':'application/json'})
    print(r, r.text)

if __name__ == '__main__':
    main(**dict(arg.split("=",1) for arg in sys.argv[1:]))


