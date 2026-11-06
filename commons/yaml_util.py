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
            # 如果变量名是 token，不替换，原样返回 ${token}
            if name == "token":
                return match.group(0)
            # 其他变量：优先从values字典取，取不到保留原字符串
            return values.get(name, match.group(0))
        return ENV_REFERENCE.sub(replace, data)
    if isinstance(data, list):
        return [_replace_env_references(item, values) for item in data]
    if isinstance(data, dict):
        return {key: _replace_env_references(value, values) for key, value in data.items()}
    return data


def write_yaml(data):
    with open(os.getcwd() + "/extract.yaml", "w", encoding="utf-8") as f:
        yaml.dump(data, stream=f, allow_unicode=True)

def resolve_env_data(data):
    """解析为新对象，保留原始参数中的环境变量占位符。"""
    return _replace_env_references(data, _env_values())


def read_yaml(file_path, resolve_env=True):
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if resolve_env:
        return resolve_env_data(data)
    else:
        return data

def clear_yaml():
    with open(os.getcwd()+"/extract.yaml",encoding="utf-8",mode="w")as f:
        f.truncate()
