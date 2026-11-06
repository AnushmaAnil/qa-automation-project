from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login-btn")
    ERROR = (By.ID, "login-error")

    def login(self, username, password):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BTN)
        return self

    def error_message(self):
        return self.text_of(self.ERROR)
