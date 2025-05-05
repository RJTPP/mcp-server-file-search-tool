import json

with open("config.json", "r") as f:
    config = json.load(f)

BASE_DIR = config["BASE_DIR"]
DEFAULT_TIME_LIMIT = config.get("DEFAULT_TIME_LIMIT", 10)
HIDE_HIDDEN_FILES = config.get("HIDE_HIDDEN_FILES", True)
EXCLUDE_PATHS = config.get("EXCLUDE_PATHS", [])
