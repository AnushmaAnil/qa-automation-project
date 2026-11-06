import pytest

from pages.cart_page import CartPage
from pages.products_page import ProductsPage

pytestmark = pytest.mark.ui
BACKPACK, BIKE_LIGHT = 1, 2          # product ids (prices 1999 and 499)


@pytest.mark.smoke
def test_add_item_updates_cart_badge(logged_in_driver):
    products = ProductsPage(logged_in_driver)
    assert products.cart_count() == 0
    products.add_to_cart(BACKPACK)
    assert products.cart_count() == 1


@pytest.mark.regression
def test_cart_total_for_multiple_items(logged_in_driver):
    products = ProductsPage(logged_in_driver)
    products.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)
    products.go_to_cart()
    cart = CartPage(logged_in_driver)
    assert cart.has_item(BACKPACK) and cart.has_item(BIKE_LIGHT)
    assert cart.total() == 1999 + 499


@pytest.mark.regression
def test_adding_same_item_twice_increases_quantity(logged_in_driver):
    products = ProductsPage(logged_in_driver)
    products.add_to_cart(BIKE_LIGHT).add_to_cart(BIKE_LIGHT)
    products.go_to_cart()
    cart = CartPage(logged_in_driver)
    assert cart.quantity_of(BIKE_LIGHT) == 2
    assert cart.total() == 499 * 2


@pytest.mark.regression
def test_remove_item_updates_total(logged_in_driver):
    products = ProductsPage(logged_in_driver)
    products.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)
    products.go_to_cart()
    cart = CartPage(logged_in_driver).remove(BACKPACK)
    assert not cart.has_item(BACKPACK)
    assert cart.total() == 499


@pytest.mark.regression
@pytest.mark.negative
def test_empty_cart_message(logged_in_driver):
    cart = CartPage(logged_in_driver).open()
    assert cart.is_empty()
