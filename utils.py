import datetime
import json
import os
import re
from urllib.parse import urlparse


def is_float(n):
    try:
        float(n)
        return '.' in str(n)
    except ValueError:
        return False


def log(content):
    now = datetime.datetime.now()
    dmy = now.strftime("%d/%m/%Y")
    hms = now.strftime("%H:%M:%S")
    try:
        print(f"[ {dmy} | {hms} ] {content}")
    except UnicodeEncodeError:
        safe_content = str(content).encode('ascii', errors='replace').decode('ascii')
        print(f"[ {dmy} | {hms} ] {safe_content}")


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def _parse_env_value(value):
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return ""
    if value and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def get_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    env_path = os.path.join(base_dir, ".env")

    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as fh:
                config = json.load(fh) or {}
        except (json.JSONDecodeError, ValueError):
            config = {}

    env_values = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                env_values[key.strip().lower()] = _parse_env_value(value)

    for key, value in os.environ.items():
        env_values[key.strip().lower()] = _parse_env_value(value)

    config.update(env_values)
    return config
