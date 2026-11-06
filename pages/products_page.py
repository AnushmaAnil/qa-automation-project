from selenium.webdriver.common.by import By

from .base_page import BasePage


class ProductsPage(BasePage):
    PATH = "/products"
    TITLE = (By.ID, "page-title")
    SEARCH_INPUT = (By.ID, "search-input")
    SEARCH_BTN = (By.ID, "search-btn")
    NO_RESULTS = (By.ID, "no-results")
    CART_COUNT = (By.ID, "cart-count")
    CART_LINK = (By.ID, "nav-cart")
    LOGOUT = (By.ID, "logout-link")
    PRODUCT_NAMES = (By.CSS_SELECTOR, ".product-name")

    def title(self):
        return self.text_of(self.TITLE)

    def product_names(self):
        self.find(self.TITLE)
        return [e.text for e in self.driver.find_elements(*self.PRODUCT_NAMES)]

    def add_to_cart(self, product_id):
        before = self.cart_count()
        self.click((By.ID, f"add-{product_id}"))
        self.wait.until(lambda d: int(d.find_element(*self.CART_COUNT).text) == before + 1)
        return self

    def cart_count(self):
        return int(self.text_of(self.CART_COUNT))

    def search(self, term):
        self.type(self.SEARCH_INPUT, term)
        self.click(self.SEARCH_BTN)
        self.wait_for_url_contains("q=")
        return self

    def go_to_cart(self):
        self.click(self.CART_LINK)

    def logout(self):
        self.click(self.LOGOUT)
