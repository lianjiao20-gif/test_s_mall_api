import requests
import pytest

from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml
import testcases.order.test_order as order_module


def json_response(status_code, body):
    response = requests.Response()
    response.status_code = status_code
    response._content = body.encode()
    return response


def test_order_detail_formats_path_before_request(monkeypatch):
    case = read_yaml("data/order/test_userinfo_order.yaml")[1]
    actual_request = {}

    def local_response(**kwargs):
        actual_request.update(kwargs)
        if kwargs["headers"] == {"Authorization": "Bearer local-token"}:
            return json_response(400, '{"error":{"code":"INVALID_ID","message":"无效的 ID"}}')
        return json_response(401, '{"error":{"code":"UNAUTHORIZED","message":"请先登录"}}')

    class LocalRequest:
        def getfixturevalue(self, name):
            assert name == "auth_token"
            return "local-token"

    monkeypatch.setattr(RequestUtil.session, "request", local_response)
    order_module.TestOrder().test_userinfo_order(case, LocalRequest())

    assert actual_request == {
        "method": "get",
        "url": "http://134.175.134.64:8080/api/orders/aaa",
        "headers": {"Authorization": "Bearer local-token"},
    }


def test_create_order_prepares_a_cart_item(monkeypatch):
    case = read_yaml("data/order/test_create_order.yaml")[1]
    calls = []

    class LocalRequest:
        def getfixturevalue(self, name):
            assert name == "auth_token"
            return "local-token"

    def local_response(**kwargs):
        calls.append(kwargs)
        if kwargs["url"] == "http://134.175.134.64:8080/api/cart" and kwargs["method"] == "get":
            return json_response(200, '{"items":[{"productId":1,"quantity":60}]}')
        if kwargs["url"] == "http://134.175.134.64:8080/api/cart/items/1" and kwargs["method"] == "delete":
            return json_response(204, "")
        if kwargs["url"].endswith("/cart/items"):
            return json_response(201, "{}")
        if len(calls) < 4:
            return json_response(400, '{"error":{"code":"EMPTY_CART"}}')
        return json_response(201, "{}")

    monkeypatch.setattr(RequestUtil.session, "request", local_response)
    order_module.TestOrder().test_create_order(case, LocalRequest())

    assert [call["url"] for call in calls] == [
        "http://134.175.134.64:8080/api/cart",
        "http://134.175.134.64:8080/api/cart/items/1",
        "http://134.175.134.64:8080/api/cart/items",
        "http://134.175.134.64:8080/api/orders",
    ]
    assert all(call["headers"] == {"Authorization": "Bearer local-token"} for call in calls)
    assert calls[2]["json"] == {"productId": 2, "quantity": 1}


def test_out_of_stock_order_uses_authentication(monkeypatch):
    case = read_yaml("data/order/test_create_order.yaml")[0]
    calls = []

    class LocalRequest:
        def getfixturevalue(self, name):
            assert name == "auth_token"
            return "local-token"

    def local_response(**kwargs):
        calls.append(kwargs)
        if kwargs["url"].endswith("/api/cart"):
            return json_response(200, '{"items":[{"productId":1,"quantity":60}]}')
        if kwargs["url"].endswith("/api/products/1"):
            return json_response(200, '{"id":1,"stock":20}')
        if kwargs["headers"] == {"Authorization": "Bearer local-token"}:
            return json_response(409, '{"error":{"code":"OUT_OF_STOCK","message":"库存不足"}}')
        return json_response(401, '{"error":{"code":"UNAUTHORIZED","message":"请先登录"}}')

    monkeypatch.setattr(RequestUtil.session, "request", local_response)
    order_module.TestOrder().test_create_order(case, LocalRequest())
    assert [call["url"].rsplit("/", 1)[-1] for call in calls] == ["cart", "1", "orders"]


@pytest.mark.parametrize("cart_body", [
    '{"items":[]}',
    '{"items":[{"productId":1,"quantity":1}]}',
])
def test_out_of_stock_order_does_not_submit_without_precondition(monkeypatch, cart_body):
    case = read_yaml("data/order/test_create_order.yaml")[0]
    calls = []

    class LocalRequest:
        def getfixturevalue(self, name):
            return "local-token"

    def local_response(**kwargs):
        calls.append(kwargs)
        if kwargs["url"].endswith("/api/cart"):
            return json_response(200, cart_body)
        if kwargs["url"].endswith("/api/products/1"):
            return json_response(200, '{"id":1,"stock":20}')
        return json_response(201, "{}")

    monkeypatch.setattr(RequestUtil.session, "request", local_response)
    with pytest.raises(pytest.skip.Exception, match="库存不足前置条件未满足"):
        order_module.TestOrder().test_create_order(case, LocalRequest())
    assert not any(call["url"].endswith("/api/orders") for call in calls)
