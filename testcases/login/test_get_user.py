import pytest
from commons.assert_util import execute_validate
from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml


class TestGetUser:
    @pytest.mark.parametrize("getUser_case", read_yaml("data/login/test_get_user.yaml"))
    def test_get_user(self, getUser_case, request):
        request_data = getUser_case["request"]
        headers = request_data.get("headers")
        if headers:
            auth_token = request.getfixturevalue("auth_token")
            new_headers = {}
            for name, value in headers.items():
                new_headers[name] = value.replace("${token}", auth_token)
            headers = new_headers
            
        res = RequestUtil().get_request_url(
            method = request_data["methods"],
            url = request_data["url"],
            headers = headers,
        )
        execute_validate(res, getUser_case["validate"])
