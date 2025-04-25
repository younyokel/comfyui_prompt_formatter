import os
import json
import re

# Default configurations
DEFAULT_CONFIG = {
    "BRACKET2WEIGHT": True,
    "CONV_SPACE_UNDERSCORE": "None",
    "BLACKLIST_FILE": "blacklisted_tags.txt"
}
DEFAULT_BLACKLIST = "tagme .*text .*_bubble onomatopoeia dialogue\n.*_(artwork) watermark signature 20\d\d"

config_path = os.path.join(os.path.dirname(__file__), "config.json")
blacklist_path = os.path.join(os.path.dirname(__file__), DEFAULT_CONFIG["BLACKLIST_FILE"])

# Load or create config file
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
else:
    config = DEFAULT_CONFIG
    with open(config_path, "w") as f:
        json.dump(config, indent=4, fp=f)

# Load or create blacklist file
if not os.path.exists(blacklist_path):
    with open(blacklist_path, "w") as f:
        f.write(DEFAULT_BLACKLIST)

# Load blacklist patterns
with open(blacklist_path, "r") as f:
    blacklist_content = f.read()

# Load configurations globally
BRACKET2WEIGHT = config.get("BRACKET2WEIGHT", DEFAULT_CONFIG["BRACKET2WEIGHT"])
CONV_SPACE_UNDERSCORE = config.get("CONV_SPACE_UNDERSCORE", DEFAULT_CONFIG["CONV_SPACE_UNDERSCORE"])

BLACKLISTED_TAGS = [
    re.compile(pattern.strip())
    for line in blacklist_content.splitlines()
    for pattern in line.split()
    if pattern.strip()
]