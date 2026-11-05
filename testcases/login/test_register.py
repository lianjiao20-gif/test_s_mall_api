import pytest
from commons.assert_util import execute_validate
from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml


class TestRegister:
    @pytest.mark.parametrize("register_case", read_yaml("data/login/test_register.yaml"))
    def test_register(self, register_case, request):
        request_data = register_case["request"]
        res = RequestUtil().sendRequest(
            method = request_data["methods"],
            url = request_data["url"],
            json = request_data["params"]
        )
        execute_validate(res, register_case["validate"])
        