import json

from ted_sws.resources import PREFIXES_PATH

PREFIXES_DEFINITIONS_KEY = "prefix_definitions"
PREFIXES_FILE = "prefixes.json"

PREFIXES: dict = json.loads((PREFIXES_PATH / PREFIXES_FILE).read_text())
PREFIXES_DEFINITIONS: dict = PREFIXES[PREFIXES_DEFINITIONS_KEY]