import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.products_page import ProductsPage

pytestmark = pytest.mark.ui


def _cart_with_backpack(driver):
    products = ProductsPage(driver)
    products.add_to_cart(1)
    products.go_to_cart()
    CartPage(driver).proceed_to_checkout()
    return CheckoutPage(driver)


@pytest.mark.smoke
def test_end_to_end_purchase(logged_in_driver):
    checkout = _cart_with_backpack(logged_in_driver)
    checkout.place_order("Asha Nair", "Kakkanad, Kochi", "682030")
    assert checkout.find(CheckoutPage.CONFIRMATION)
    assert checkout.order_id().startswith("ORD-")
    assert "1999" in checkout.text_of(CheckoutPage.ORDER_TOTAL)
    # cart must be empty after a successful order
    assert ProductsPage(logged_in_driver).open().cart_count() == 0


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize("name, address, pin, expected_error", [
    ("", "Kochi", "682030", "Full name is required"),
    ("Asha", "", "682030", "Address is required"),
    ("Asha", "Kochi", "", "PIN code must be exactly 6 digits"),
    ("Asha", "Kochi", "68203", "PIN code must be exactly 6 digits"),
    ("Asha", "Kochi", "68203A", "PIN code must be exactly 6 digits"),
], ids=["no-name", "no-address", "empty-pin", "short-pin", "alpha-pin"])
def test_checkout_validation_errors(logged_in_driver, name, address, pin, expected_error):
    checkout = _cart_with_backpack(logged_in_driver)
    checkout.place_order(name, address, pin)
    assert expected_error in checkout.error_message()


@pytest.mark.regression
@pytest.mark.negative
def test_checkout_with_empty_cart_redirects_to_cart(logged_in_driver):
    logged_in_driver.get(logged_in_driver.base_url + "/checkout")
    assert CartPage(logged_in_driver).is_empty()
