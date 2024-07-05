from logging import config
import json

with open('../log_config.json', 'r') as fh:
    log_config = json.load(fh)

config.dictConfig(log_config)