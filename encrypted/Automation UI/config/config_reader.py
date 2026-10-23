import os
from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).parent / "config.yaml"


def get_config():
    with open(_CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    # Allow CLI/CI overrides without editing the file, e.g.:
    #   BROWSER=firefox HEADLESS=false behave
    config["browser"] = os.getenv("BROWSER", config["browser"])
    config["headless"] = os.getenv("HEADLESS", str(config["headless"])).lower() == "true"
    config["base_url"] = os.getenv("BASE_URL", config["base_url"])
    return config
