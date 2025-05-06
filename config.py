import json

with open("config.json", "r") as f:
    config = json.load(f)

BASE_DIR = config["BASE_DIR"]
DEFAULT_TIME_LIMIT = config.get("DEFAULT_TIME_LIMIT", 10)
HIDE_HIDDEN_FILES = config.get("HIDE_HIDDEN_FILES", True)
EXCLUDE_PATHS = config.get("EXCLUDE_PATHS", [])

PATH_MASKER = config.get("PATH_MASKER", {})
PATH_MASKER_ENABLED = PATH_MASKER.get("ENABLED", False)
PATH_MASKER_MODE = PATH_MASKER.get("MODE", "prefix")
PATH_MASKER_MASK_TOKEN = PATH_MASKER.get("MASK_TOKEN", "MASK")
PATH_MASKER_LOOK_FOR = PATH_MASKER.get("LOOK_FOR", [])

HOST = config.get("HOST", "127.0.0.1")
PORT = config.get("PORT", 6277)