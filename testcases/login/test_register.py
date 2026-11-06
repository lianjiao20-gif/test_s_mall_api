import pytest
from commons.assert_util import execute_validate
from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml, resolve_env_data


class TestRegister:
    @pytest.mark.parametrize("register_case", read_yaml("data/login/test_register.yaml", resolve_env=False))
    def test_register(self, register_case):
        case = resolve_env_data(register_case)
        request_data = case["request"]
        res = RequestUtil().sendRequest(
            method = request_data["methods"],
            url = request_data["url"],
            json = request_data["params"]
        )
        execute_validate(res, case["validate"])
