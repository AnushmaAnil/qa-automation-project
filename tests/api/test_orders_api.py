import pytest

pytestmark = pytest.mark.api


def _order(api, token, items, pin="682030"):
    return api.post("/api/orders", token=token, json={"items": items, "pin_code": pin})


@pytest.mark.smoke
def test_create_order_calculates_total(api, token):
    r = _order(api, token, [{"product_id": 1, "quantity": 2}, {"product_id": 2, "quantity": 1}])
    assert r.status_code == 201
    body = r.json()
    assert body["order_id"].startswith("ORD-")
    assert body["total"] == 1999 * 2 + 499


@pytest.mark.regression
def test_created_order_can_be_fetched(api, token):
    created = _order(api, token, [{"product_id": 3, "quantity": 1}]).json()
    r = api.get(f"/api/orders/{created['order_id']}", token=token)
    assert r.status_code == 200
    assert r.json()["total"] == 799
    assert r.json()["items"] == [{"product_id": 3, "quantity": 1}]


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize("items, pin, status", [
    ([], "682030", 400),
    ("not-a-list", "682030", 400),
    ([{"product_id": 1, "quantity": 0}], "682030", 400),
    ([{"product_id": 1, "quantity": 11}], "682030", 400),
    ([{"product_id": 1, "quantity": -1}], "682030", 400),
    ([{"product_id": 1, "quantity": "2"}], "682030", 400),
    ([{"product_id": 1, "quantity": 1}], "12345", 400),
    ([{"product_id": 1, "quantity": 1}], "abcdef", 400),
    ([{"product_id": 999, "quantity": 1}], "682030", 404),
], ids=["empty-items", "items-not-list", "qty-zero", "qty-too-high", "qty-negative",
        "qty-string", "short-pin", "alpha-pin", "unknown-product"])
def test_invalid_orders_are_rejected(api, token, items, pin, status):
    assert _order(api, token, items, pin).status_code == status


@pytest.mark.regression
@pytest.mark.parametrize("qty", [1, 10])
def test_quantity_boundaries_are_accepted(api, token, qty):
    assert _order(api, token, [{"product_id": 2, "quantity": qty}]).status_code == 201


@pytest.mark.regression
@pytest.mark.negative
def test_unknown_order_returns_404(api, token):
    assert api.get("/api/orders/ORD-0", token=token).status_code == 404


@pytest.mark.regression
@pytest.mark.negative
def test_user_cannot_read_another_users_order(api, token):
    from demo_app import app as app_module
    app_module.USERS["other_user"] = {"password": "pw12345", "locked": False}
    try:
        other = api.post("/api/login", json={"username": "other_user", "password": "pw12345"}).json()["token"]
        oid = _order(api, token, [{"product_id": 1, "quantity": 1}]).json()["order_id"]
        assert api.get(f"/api/orders/{oid}", token=other).status_code == 403
    finally:
        app_module.USERS.pop("other_user", None)
