import requests

response = requests.Session().request(
    method="GET", 
    url="https://www.baidu.com",
    params={"wd": "python"},
)
assert False, "1236666"

