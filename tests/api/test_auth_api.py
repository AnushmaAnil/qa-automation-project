import pytest

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_login_returns_token(api):
    r = api.post("/api/login", json={"username": "standard_user", "password": "secret123"})
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "standard_user"
    assert isinstance(body["token"], str) and len(body["token"]) >= 16


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.parametrize("payload, status", [
    ({"username": "standard_user", "password": "bad"}, 401),
    ({"username": "ghost", "password": "secret123"}, 401),
    ({"username": "locked_user", "password": "secret123"}, 403),
    ({"username": "standard_user"}, 400),
    ({}, 400),
], ids=["wrong-password", "unknown-user", "locked-user", "missing-password", "empty-body"])
def test_login_error_codes(api, payload, status):
    r = api.post("/api/login", json=payload)
    assert r.status_code == status
    assert "error" in r.json()


@pytest.mark.negative
@pytest.mark.regression
def test_order_requires_authentication(api):
    r = api.post("/api/orders", json={"items": [{"product_id": 1, "quantity": 1}],
                                      "pin_code": "682030"})
    assert r.status_code == 401


@pytest.mark.negative
@pytest.mark.regression
def test_invalid_token_is_rejected(api):
    r = api.get("/api/orders/ORD-1", token="not-a-real-token")
    assert r.status_code == 401
