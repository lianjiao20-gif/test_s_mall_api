import pytest
from commons.assert_util import execute_validate
from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml


class TestProducts:
    @pytest.mark.parametrize("getProducts_case", read_yaml("data/products/test_products.yaml"))
    def test_products_list(self, getProducts_case):
        request_data = getProducts_case["request"]
        res = RequestUtil().get_request_url(
            method = request_data["methods"],
            url = request_data["url"],
        )
        execute_validate(res, getProducts_case["validate"])
    
    @pytest.mark.parametrize("getProductsInfo_case", read_yaml("data/products/test_products_information.yaml"))
    def test_get_products_information(self, getProductsInfo_case):
        request_data = getProductsInfo_case["request"]
        path_params = request_data["url"].format(**request_data["params"])
        res = RequestUtil().get_request_url(
            method = request_data["methods"],
            url = path_params,
        )
        execute_validate(res, getProductsInfo_case["validate"])
