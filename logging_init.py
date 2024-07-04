from logging import config
import json

# Load logging configuration from JSON file
with open('log_config.json', 'r') as fh:
    log_config = json.load(fh)

# Apply the logging configuration
config.dictConfig(log_config)
