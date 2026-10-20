import pytest
from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml, write_yaml


@pytest.fixture(scope="session")
def auth_token():
    login_case = None
    for case in read_yaml("data/login/test_login.yaml"):
        if case.get("extract"):
            login_case = case
            break
    request_data = login_case["request"]

    res = RequestUtil().get_request_url(
        method=request_data["methods"],
        url=request_data["url"],
        json=request_data["params"],
    )
    assert res.status_code == 200, res.text

    token = res.json().get("token")
    assert token, "登录成功，但响应中没有 token"
    write_yaml({"token": token})
    return token
