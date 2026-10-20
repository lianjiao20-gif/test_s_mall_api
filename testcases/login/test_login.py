import pytest
from commons.assert_util import execute_validate
from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml, write_yaml


class TestLogin:
    @pytest.mark.parametrize("login_case", read_yaml("data/login/test_login.yaml"))
    def test_login(self, login_case):
        request_data = login_case["request"]            
        res = RequestUtil().get_request_url(
            method = request_data["methods"],
            url = request_data["url"],
            json = request_data["params"],
        )
        execute_validate(res, login_case["validate"])
        if res.status_code == 200:
            write_yaml({"token": res.json()["token"]})
