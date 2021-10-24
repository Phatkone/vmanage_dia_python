import json
configFile = 'dia-config.json'

class Config:
    
    config = {}
    defaults = {
        "vmanage_user": '',
        "vmanage_password": '',
        "vmanage_address": '',
        "vmanage_port": 443,
        "vmanage_data_prefix_list": '',
        "vmanage_user_defined_entries": [],
        "retries": 5,
        "timeout": 300,
        "ssl_verify": True,
        "sharepoint_tenant":"",
        "o365_version":""
    }

    def __init__(self):
        try:
            with open(configFile) as f:
                self.config = json.load(f)
        except IOError as e:
            print(e)
    
    def checkConfig(self):
        for k in self.defaults.keys():
            if k not in self.config.keys():
                print("Missing '{}' key from config file".format(k))
                return False
            if self.config[k] == '':
                print("'{}' is not set in config file.")
                return False
        return True
    
    def rebuildConfig(self):
        newvals = {}
        for k in self.defaults.keys():
            if k in self.config.keys():
                newvals[k] = self.config[k]
            else:
                newvals[k] = self.defaults[k]
        try:
            with open(configFile, 'w') as f:
                f.write(json.dumps(newvals, indent=4))
            return True
        except IOError as e:
            return e
