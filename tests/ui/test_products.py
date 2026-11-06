import pytest

from pages.products_page import ProductsPage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_all_products_are_listed(logged_in_driver):
    names = ProductsPage(logged_in_driver).product_names()
    assert names == ["Backpack", "Bike Light", "Cotton T-Shirt", "Fleece Jacket"]


@pytest.mark.regression
def test_search_returns_matching_product(logged_in_driver):
    page = ProductsPage(logged_in_driver).search("Jacket")
    assert page.product_names() == ["Fleece Jacket"]


@pytest.mark.regression
@pytest.mark.negative
def test_search_with_no_match_shows_message(logged_in_driver):
    page = ProductsPage(logged_in_driver).search("Laptop")
    assert page.is_visible(ProductsPage.NO_RESULTS)


@pytest.mark.regression
@pytest.mark.xfail(reason="BUG-001: product search is case-sensitive", strict=True)
def test_search_is_case_insensitive(logged_in_driver):
    page = ProductsPage(logged_in_driver).search("BACKPACK")
    assert page.product_names() == ["Backpack"]
