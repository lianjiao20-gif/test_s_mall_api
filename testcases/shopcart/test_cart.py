import pytest

from commons.assert_util import execute_validate
from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml


def build_headers(request_data, request):
    headers = request_data.get("headers")
    if not headers:
        return None

    token = request.getfixturevalue("auth_token")
    return {
        name: value.replace("${token}", token)
        for name, value in headers.items()
    }


class TestCart:
    @pytest.mark.parametrize("cart_case", read_yaml("data/shopcart/test_cart.yaml"))
    def test_get_cart(self, cart_case, request):
        request_data = cart_case["request"]
        res = RequestUtil().get_request_url(
            method=request_data["methods"],
            url=request_data["url"],
            headers=build_headers(request_data, request),
        )
        execute_validate(res, cart_case["validate"])

    @pytest.mark.parametrize("add_cart_case", read_yaml("data/shopcart/test_add_cart.yaml"))
    def test_add_cart(self, add_cart_case, request):
        request_data = add_cart_case["request"]
        res = RequestUtil().get_request_url(
            method = request_data["methods"],
            url = request_data["url"],
            headers = build_headers(request_data, request),
            json = request_data["json"],
        )
        execute_validate(res, add_cart_case["validate"])

    @pytest.mark.parametrize("modify_cart_case", read_yaml("data/shopcart/test_modify_cart.yaml"))
    def test_modify_cart(self, modify_cart_case, request):
        request_data = modify_cart_case["request"]
        validate = modify_cart_case["validate"]
        headers = build_headers(request_data, request)
        item_url = request_data["url"].format(**request_data["path_params"])
        items_url = item_url.rsplit("/", 1)[0]
        cart_url = items_url.rsplit("/", 1)[0]
        product_id = request_data["path_params"]["productId"]

        expected_status = None
        for rule in validate:
            if "eq" in rule and rule["eq"][0] == "status_code":
                expected_status = rule["eq"][1]
                break
        if expected_status is None:
            raise ValueError("修改购物车用例缺少 status_code 断言")

        # YAML 只写最终响应；根据预期状态准备购物车前置条件。
        needs_cart_state = (
            headers is not None
            and isinstance(product_id, int)
            and expected_status in (200, 404, 409)
        )
        if not needs_cart_state:
            res = RequestUtil().get_request_url(
                method=request_data["methods"],
                url=item_url,
                headers=headers,
                json=request_data["json"],
            )
            execute_validate(res, validate)
            return

        cart_res = RequestUtil().get_request_url(
            method="get", url=cart_url, headers=headers
        )
        assert cart_res.status_code == 200, cart_res.text
        original_quantity = next(
            (item["quantity"] for item in cart_res.json()["items"]
             if item["productId"] == product_id),
            None,
        )

        created = False
        removed = False
        needs_present = expected_status in (200, 409)
        try:
            if needs_present and original_quantity is None:
                add_res = RequestUtil().get_request_url(
                    method="post", url=items_url, headers=headers,
                    json={"productId": product_id, "quantity": 1},
                )
                created = add_res.status_code == 201
                assert add_res.status_code == 201, add_res.text
            elif not needs_present and original_quantity is not None:
                remove_res = RequestUtil().get_request_url(
                    method="delete", url=item_url, headers=headers
                )
                removed = remove_res.status_code == 204
                assert remove_res.status_code == 204, remove_res.text

            res = RequestUtil().get_request_url(
                method=request_data["methods"],
                url=item_url,
                headers=headers,
                json=request_data["json"],
            )
            execute_validate(res, validate)
        finally:
            if created:
                restore_res = RequestUtil().get_request_url(
                    method="delete", url=item_url, headers=headers
                )
                assert restore_res.status_code == 204, restore_res.text
            elif needs_present and original_quantity is not None:
                restore_res = RequestUtil().get_request_url(
                    method="patch", url=item_url, headers=headers,
                    json={"quantity": original_quantity},
                )
                assert restore_res.status_code == 200, restore_res.text
            elif removed:
                restore_res = RequestUtil().get_request_url(
                    method="post", url=items_url, headers=headers,
                    json={"productId": product_id, "quantity": original_quantity},
                )
                assert restore_res.status_code == 201, restore_res.text

    @pytest.mark.parametrize("delete_cart_case", read_yaml("data/shopcart/test_delete_cart.yaml"))
    def test_delete_cart(self, delete_cart_case, request):
        request_data = delete_cart_case["request"]
        item_url = request_data["url"].format(**request_data["path_params"])
        res = RequestUtil().get_request_url(
            method = request_data["methods"],
            url = item_url,
            headers = build_headers(request_data, request),
        )
        execute_validate(res, delete_cart_case["validate"])
