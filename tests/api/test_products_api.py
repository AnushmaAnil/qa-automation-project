import pytest

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_list_products_schema(api):
    r = api.get("/api/products")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/json")
    products = r.json()
    assert len(products) == 4
    for p in products:
        assert set(p) == {"id", "name", "price", "category"}
        assert isinstance(p["id"], int) and isinstance(p["price"], int) and p["price"] > 0


@pytest.mark.regression
def test_get_single_product(api):
    r = api.get("/api/products/1")
    assert r.status_code == 200
    assert r.json()["name"] == "Backpack"


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize("pid", [0, 999, 5])
def test_unknown_product_returns_404(api, pid):
    assert api.get(f"/api/products/{pid}").status_code == 404


@pytest.mark.regression
def test_search_filters_products(api):
    names = [p["name"] for p in api.get("/api/products", params={"search": "Jacket"}).json()]
    assert names == ["Fleece Jacket"]


@pytest.mark.regression
@pytest.mark.xfail(reason="BUG-001: product search is case-sensitive", strict=True)
def test_search_is_case_insensitive(api):
    names = [p["name"] for p in api.get("/api/products", params={"search": "BACKPACK"}).json()]
    assert names == ["Backpack"]
