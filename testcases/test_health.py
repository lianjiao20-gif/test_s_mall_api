import pytest
from commons.assert_util import execute_validate
from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml


class TestHealth:
    @pytest.mark.smoke
    @pytest.mark.parametrize("health_case", read_yaml("data/test_health.yaml"))
    def test_health_check(self, health_case):
        request_data = health_case["request"]
        res = RequestUtil().get_request_url(
            method = request_data["methods"],
            url = request_data["url"],
        )
        execute_validate(res, health_case["validate"])