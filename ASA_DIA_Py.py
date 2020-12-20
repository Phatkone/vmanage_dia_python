import requests
import sys
import json
import uuid
import base64

configFile = 'dia-config.json'

class Config:
    apiKey = ''
    usr = ''
    pwd = ''
    fwl = ''
    srcUrl = ''
    usrDefinedEntries = []

    def __init__(self):
        pass


def checkConfig():
    c = Config()
    try:
        configValid = True
        missingValues = []
        with open(configFile) as f:
            config = json.load(f)
        if 'api_key' in config.keys():
            c.apiKey = config['api_key']
        else:
            missingValues.append('api_key')
        if 'user' in config.keys():
            c.usr = config['user']
        else:
            missingValues.append('user')
        if 'password' in config.keys():
            c.pwd = config['password']
        else:
            missingValues.append('password')
        if 'firewall' in config.keys():
            c.fwl = config['firewall']
        else:
            missingValues.append('firewall')
        if 'source_url' in config.keys():
            c.srcUrl = config['source_url']
        else:
            missingValues.append('source_url')
        if 'user_defined_entries' in config.keys():
            c.usrDefinedEntries = config['user_defined_entries']
        else:
            missingValues.append('user_defined_entries')

        if c.apiKey == '' and (c.usr == '' or c.pwd == ''):
            print("Missing Auth Parameters. Please check config file and try again")
            configValid = False
        if c.fwl == '':
            print("Missing firewall host/address. Please check config file and try again")
            configValid = False
        if c.srcUrl == '':
            print("Missing source url. Please check config file and try again")
            configValid = False

        if configValid == False:
            return c, False

        return c, 'success'
    except IOError as e:
        print(e)
        return c, e

def makeConfigFile(config):
    try:
        data = {
            'api_key':config.apiKey,
            'user':config.usr,
            'password':config.pwd,
            'firewall':config.fwl,
            'source_url':config.srcUrl,
            'user_defined_entries':config.usrDefinedEntries
            }
        msg = """
            
        """
        with open(configFile,'w') as f:
            json.dump(data,f)
        return True, 'success'
    except IOError as e:
        print(e)
        return False, e

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
    print(getAuthToken)
    """
    urls = requests.get("{}?clientrequestid={}".format(c.srcUrl, uuid.uuid4()))
    if urls.status_code == 200:
        print(urls.json())
    else:
        print(urls.status_code, urls.text)
    return
    """
    r = requests.get("https://{}/api/access/global/rules".format(c.fwl), auth=(c.usr, c.pwd), verify=False, headers={"Accept":'application/json','Content-Type':'application/json'})
    print(r, r.text)

if __name__ == '__main__':
    main(**dict(arg.split("=",1) for arg in sys.argv[1:]))


