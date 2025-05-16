import os
import json
import re

# Default configurations
DEFAULT_CONFIG = {
    "BRACKET2WEIGHT": True,
    "COLLAPSE_LINEBREAKS": True,
    "CONV_SPACE_UNDERSCORE": "None",
    "BLACKLIST_FILE": "blacklisted_tags.txt"
}
DEFAULT_BLACKLIST = "tagme .*text .*_bubble onomatopoeia dialogue\n.*_(artwork) watermark signature 20\d\d"

# Paths
base_dir = os.path.dirname(__file__)
config_path = os.path.join(base_dir, "settings.json")

# Load or create config file
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    updated = False
    for key, default_value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = default_value
            updated = True
    if updated:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
else:
    config = DEFAULT_CONFIG.copy()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

# Blacklist file handling
blacklist_path = os.path.join(base_dir, config["BLACKLIST_FILE"])
if not os.path.exists(blacklist_path):
    with open(blacklist_path, "w") as f:
        f.write(DEFAULT_BLACKLIST)

# Load blacklist patterns
with open(blacklist_path, "r") as f:
    blacklist_content = f.read()

# Load configurations globally
BRACKET2WEIGHT = config["BRACKET2WEIGHT"]
COLLAPSE_LINEBREAKS = config["COLLAPSE_LINEBREAKS"]
CONV_SPACE_UNDERSCORE = config["CONV_SPACE_UNDERSCORE"]

BLACKLISTED_TAGS = [
    re.compile(pattern.strip())
    for line in blacklist_content.splitlines()
    for pattern in line.split()
    if pattern.strip()
]
