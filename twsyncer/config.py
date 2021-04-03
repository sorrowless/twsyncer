import json
import os


def load_config():
    home = os.path.expanduser("~")
    config = os.path.join(home, ".config", "twsyncer", "config.json")
    if not os.path.isfile(config):
        print("Config not found")
        return None
    with open(config, "rt") as fh:
        config = json.load(fh)
    return config
