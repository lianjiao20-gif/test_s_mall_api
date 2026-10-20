import os
import yaml


def write_yaml(data):
    with open(os.getcwd() + "/extract.yaml", "w", encoding="utf-8") as f:
        yaml.dump(data, stream=f, allow_unicode=True)

def read_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

def clear_yaml():
    with open(os.getcwd()+"/extract.yaml",encoding="utf-8",mode="w")as f:
        f.truncate()
