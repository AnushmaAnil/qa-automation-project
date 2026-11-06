"""Shared fixtures: local app server, browser driver, API client, failure screenshots."""
import os
import threading
from pathlib import Path

import pytest
import requests
from selenium import webdriver
from werkzeug.serving import make_server

from demo_app.app import app

SCREENSHOT_DIR = Path("reports/screenshots")


# ------------------------------------------------------------ CLI options
def pytest_addoption(parser):
    parser.addoption("--browser", default="chrome",
                     choices=["chrome", "firefox", "edge"], help="Browser for UI tests")
    parser.addoption("--headless", action="store_true",
                     help="Run the browser without a visible window")


# --------------------------------------------------------- app under test
@pytest.fixture(scope="session")
def base_url():
    """Start the demo app on a free port for the whole test session."""
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


# ------------------------------------------------------------------- UI
def _build_driver(browser, headless):
    in_ci = bool(os.getenv("CI"))
    if browser == "chrome":
        opts = webdriver.ChromeOptions()
        if headless:
            opts.add_argument("--headless=new")
        if in_ci:
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1280,900")
        return webdriver.Chrome(options=opts)
    if browser == "firefox":
        opts = webdriver.FirefoxOptions()
        if headless:
            opts.add_argument("-headless")
        return webdriver.Firefox(options=opts)
    opts = webdriver.EdgeOptions()
    if headless:
        opts.add_argument("--headless=new")
    return webdriver.Edge(options=opts)


@pytest.fixture
def driver(request, base_url):
    drv = _build_driver(request.config.getoption("--browser"),
                        request.config.getoption("--headless"))
    drv.implicitly_wait(0)          # we use explicit waits only (best practice)
    drv.base_url = base_url
    yield drv
    drv.quit()


@pytest.fixture
def logged_in_driver(driver):
    """A browser that is already logged in as the standard user."""
    from pages.login_page import LoginPage
    LoginPage(driver).open().login("standard_user", "secret123").wait_for_url_contains("/products")
    return driver


# ------------------------------------------------------------------ API
class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def request(self, method, path, token=None, **kw):
        headers = kw.pop("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return self.session.request(method, self.base_url + path,
                                    headers=headers, timeout=10, **kw)

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)


@pytest.fixture(scope="session")
def api(base_url):
    return ApiClient(base_url)


@pytest.fixture(scope="session")
def token(api):
    r = api.post("/api/login", json={"username": "standard_user", "password": "secret123"})
    assert r.status_code == 200
    return r.json()["token"]


# ------------------------------------------- screenshot on UI test failure
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if drv:
            from pytest_html import extras
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            drv.save_screenshot(str(SCREENSHOT_DIR / f"{item.name}.png"))
            report.extras = getattr(report, "extras", []) + [
                extras.png(drv.get_screenshot_as_base64(), "Failure screenshot")]
