import os
import re
from pathlib import Path

import yaml


ENV_REFERENCE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _env_values():
    values = {}
    env_file = Path.cwd() / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if value.startswith(("'", '"')) and value.endswith(value[0]):
                value = value[1:-1]
            values[key] = value
    values.update(os.environ)
    return values


def _replace_env_references(data, values):
    if isinstance(data, str):
        def replace(match):
            name = match.group(1)
            return match.group(0) if name == "token" else values.get(name, match.group(0))

        return ENV_REFERENCE.sub(replace, data)
    if isinstance(data, list):
        return [_replace_env_references(item, values) for item in data]
    if isinstance(data, dict):
        return {key: _replace_env_references(value, values) for key, value in data.items()}
    return data


def write_yaml(data):
    with open(os.getcwd() + "/extract.yaml", "w", encoding="utf-8") as f:
        yaml.dump(data, stream=f, allow_unicode=True)

def read_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return _replace_env_references(data, _env_values())

def clear_yaml():
    with open(os.getcwd()+"/extract.yaml",encoding="utf-8",mode="w")as f:
        f.truncate()
