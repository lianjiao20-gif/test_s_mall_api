import pytest
from commons.assert_util import execute_validate
from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml


class TestOrder:
    @pytest.mark.parametrize("create_order_case", read_yaml("data/order/test_create_order.yaml"))
    def test_create_order(self, create_order_case, request):
        request_data = create_order_case["request"]
        headers = request_data.get("headers")
        if headers:
            auth_token = request.getfixturevalue("auth_token")
            new_headers = {}
            for name, value in headers.items():
                if name == "Authorization":
                    new_headers[name] = value.replace("${token}", auth_token)
                else:
                    new_headers[name] = value
            headers = new_headers

        preflight = create_order_case.get("preflight")
    
        if preflight:
            product_id = preflight["productId"]
            api_base = request_data["url"].rsplit("/", 1)[0]
            # 发送购物车查询请求，拿到购物车中商品的数量，判断是否满足前置条件
            cart_res = RequestUtil().sendRequest(
                method="get", url=f"{api_base}/cart", headers=headers
            )
            assert cart_res.status_code == 200, cart_res.text
            quantity = None
            for item in cart_res.json()["items"]:
                if item["productId"] == product_id:
                    quantity = item["quantity"]
                    break
            # 发送商品查询请求，拿到商品的库存，判断是否满足前置条件
            product_res = RequestUtil().sendRequest(
                method="get", url=f"{api_base}/products/{product_id}", headers=headers
            )
            assert product_res.status_code == 200, product_res.text
            product = product_res.json()
            stock = product.get("stock")
            # 如果商品信息中没有 stock库存 字段，则尝试从 product 字段中获取
            if stock is None and isinstance(product.get("product"), dict):
                stock = product["product"].get("stock")
            if quantity is None or stock is None or quantity <= stock:
                pytest.skip(
                    f"库存不足前置条件未满足：商品 {product_id} 购物车数量={quantity}，当前库存={stock}；未提交订单"
                )

        setup = create_order_case.get("setup")
        if setup:
            if setup.get("clear_cart"):
                cart_url = setup["url"].rsplit("/", 1)[0]
                cart_res = RequestUtil().sendRequest(
                    method="get", url=cart_url, headers=headers
                )
                assert cart_res.status_code == 200, cart_res.text
                for item in cart_res.json()["items"]:
                    delete_res = RequestUtil().sendRequest(
                        method="delete",
                        url=f'{setup["url"]}/{item["productId"]}',
                        headers=headers,
                    )
                    assert delete_res.status_code == 204, delete_res.text
            setup_res = RequestUtil().sendRequest(
                method=setup["methods"],
                url=setup["url"],
                headers=headers,
                json=setup["json"],
            )
            assert setup_res.status_code == 201, setup_res.text

        res = RequestUtil().sendRequest(
            method = request_data["methods"],
            url = request_data["url"],
            headers = headers,
        )
        execute_validate(res, create_order_case["validate"])

    @pytest.mark.parametrize("user_order_case", read_yaml("data/order/test_user_order.yaml"))
    def test_user_order(self, user_order_case, request):
        request_data = user_order_case["request"]
        headers = request_data.get("headers")
        if headers:
            auth_token = request.getfixturevalue("auth_token")
            new_headers = {}
            for name, value in headers.items():
                new_headers[name] = value.replace("${token}", auth_token)
            headers = new_headers
            
        res = RequestUtil().sendRequest(
            method = request_data["methods"],
            url = request_data["url"],
            headers = headers,
        )
        execute_validate(res, user_order_case["validate"])
    
    @pytest.mark.parametrize("userinfo_order_case", read_yaml("data/order/test_userinfo_order.yaml"))
    def test_userinfo_order(self, userinfo_order_case, request):
        request_data = userinfo_order_case["request"]
        headers = request_data.get("headers")
        if headers:
            auth_token = request.getfixturevalue("auth_token")
            new_headers = {}
            for name, value in headers.items():
                new_headers[name] = value.replace("${token}", auth_token)
            headers = new_headers
            
        res = RequestUtil().sendRequest(
            method = request_data["methods"],
            url = request_data["url"].format(**request_data.get("path_params", {})),
            headers = headers,
        )
        execute_validate(res, userinfo_order_case["validate"])
