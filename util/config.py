import json

config = json.load(open('./config.json', 'r'))

def get_config_field(key):
    global config
    if key in config:
        # print('using config field ' + key + ': ' + config[key])
        return config[key]
    else:
        return None