from selenium.webdriver.common.by import By

from .base_page import BasePage


class CheckoutPage(BasePage):
    PATH = "/checkout"
    FULL_NAME = (By.ID, "full-name")
    ADDRESS = (By.ID, "address")
    PIN_CODE = (By.ID, "pin-code")
    PLACE_ORDER = (By.ID, "place-order-btn")
    ERROR = (By.ID, "checkout-error")
    CONFIRMATION = (By.ID, "order-confirmation")
    ORDER_ID = (By.ID, "order-id")
    ORDER_TOTAL = (By.ID, "order-total")

    def place_order(self, name, address, pin):
        self.type(self.FULL_NAME, name)
        self.type(self.ADDRESS, address)
        self.type(self.PIN_CODE, pin)
        self.click(self.PLACE_ORDER)
        return self

    def error_message(self):
        return self.text_of(self.ERROR)

    def order_id(self):
        return self.text_of(self.ORDER_ID)
