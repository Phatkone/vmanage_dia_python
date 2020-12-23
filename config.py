import json
configFile = 'dia-config.json'

class Config:
    
    config = {}
    defaults = {
        "ftd_user": '',
        "ftd_password": '',
        "ftd_address": '',
        "ftd_port": 443,
        "ftd_prefix_list": '',
        "vmanage_user": '',
        "vmanage_password": '',
        "vmanage_address": '',
        "vmanage_port": 443,
        "vmanage_data_prefix_list": '',
        "retries": 5,
        "timeout": 300,
        "user_defined_entries": [],
        "ssl_verify": True
    }

    def __init__(self):
        try:
            with open(configFile) as f:
                self.config = json.load(f)
        except IOError as e:
            print(e)
    
    def checkConfig(self):
        for k,v in self.defaults.items():
            if k not in self.config.keys():
                print("Missing '{}' key from config file".format(k))
                return False
            if self.config[k] == '':
                print("'{}' is not set in config file.")
                return False
        return True
    
    def rebuildConfig(self):
        newvals = {}
        for k,v in self.defaults.items():
            if k in self.config.keys():
                newvals[k] = self.config[k]
            else:
                newvals[k] = self.defaults[k]
        try:
            with open(configFile,'w') as f:
                f.write(json.dumps(newvals,indent=4))
            return True
        except IOError as e:
            return e
