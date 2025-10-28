import json
import os

DEFAULT_CONFIG = {
    "search_paths": ["~/"],
    "max_results": 20
}

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    config_path = os.path.abspath(config_path)

    if not os.path.exists(config_path):
        return DEFAULT_CONFIG

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return {**DEFAULT_CONFIG, **config}
    except Exception:
        return DEFAULT_CONFIG
