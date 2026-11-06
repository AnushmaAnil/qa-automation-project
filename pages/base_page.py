"""BasePage: common helpers wrapping Selenium with explicit waits."""
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    TIMEOUT = 10
    PATH = "/"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver, self.TIMEOUT,
            ignored_exceptions=(NoSuchElementException, StaleElementReferenceException))

    def open(self):
        self.driver.get(self.driver.base_url + self.PATH)
        return self

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def text_of(self, locator):
        return self.find(locator).text

    def is_visible(self, locator, timeout=2):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def wait_for_url_contains(self, fragment):
        self.wait.until(EC.url_contains(fragment))

    @property
    def current_path(self):
        from urllib.parse import urlparse
        return urlparse(self.driver.current_url).path
