import re

from selenium.webdriver.common.by import By

from .base_page import BasePage


class CartPage(BasePage):
    PATH = "/cart"
    EMPTY = (By.ID, "cart-empty")
    TOTAL = (By.ID, "cart-total")
    CHECKOUT_BTN = (By.ID, "checkout-btn")

    def is_empty(self):
        return self.is_visible(self.EMPTY)

    def total(self):
        return int(re.sub(r"\D", "", self.text_of(self.TOTAL)))

    def quantity_of(self, product_id):
        return int(self.text_of((By.CSS_SELECTOR, f"#cart-row-{product_id} .item-qty")))

    def has_item(self, product_id):
        return self.is_visible((By.ID, f"cart-row-{product_id}"))

    def remove(self, product_id):
        self.click((By.ID, f"remove-{product_id}"))
        return self

    def proceed_to_checkout(self):
        self.click(self.CHECKOUT_BTN)
