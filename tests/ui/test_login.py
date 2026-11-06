import pytest

from pages.login_page import LoginPage
from pages.products_page import ProductsPage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_valid_login_opens_products_page(driver):
    LoginPage(driver).open().login("standard_user", "secret123")
    products = ProductsPage(driver)
    assert products.title() == "Products"
    assert products.current_path == "/products"


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.parametrize("username, password, expected_error", [
    ("", "secret123", "Username is required"),
    ("standard_user", "", "Password is required"),
    ("standard_user", "wrong-pass", "Invalid username or password"),
    ("no_such_user", "secret123", "Invalid username or password"),
    ("locked_user", "secret123", "locked"),
], ids=["empty-username", "empty-password", "wrong-password", "unknown-user", "locked-user"])
def test_invalid_login_shows_error(driver, username, password, expected_error):
    page = LoginPage(driver).open().login(username, password)
    assert expected_error in page.error_message()
    assert page.current_path == "/login"


@pytest.mark.regression
def test_logout_returns_to_login(logged_in_driver):
    ProductsPage(logged_in_driver).logout()
    assert LoginPage(logged_in_driver).find(LoginPage.LOGIN_BTN)


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize("path", ["/products", "/cart", "/checkout"])
def test_protected_pages_redirect_to_login(driver, path):
    driver.get(driver.base_url + path)
    assert LoginPage(driver).find(LoginPage.LOGIN_BTN)
    assert "/login" in driver.current_url
