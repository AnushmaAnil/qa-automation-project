# QA Test Automation Framework - ShopEasy

An end-to-end test automation project in **Python + Pytest + Selenium**, covering
**UI testing** (Page Object Model) and **REST API testing**. The application under
test (a small e-commerce site) is bundled, so everything runs locally with no setup
beyond `pip install`.

## What this project demonstrates
- Page Object Model with a reusable BasePage and explicit waits (no `sleep`)
- Data-driven tests with `pytest.mark.parametrize`
- Fixtures for browser, logged-in session, API client and auto-started test server
- Smoke / regression / negative suites using markers
- API tests: status codes, response schema, validation, authentication, authorisation, boundary values
- Automatic screenshot on failure, embedded in a self-contained HTML report
- A documented defect (BUG-001) tracked with `xfail(strict=True)`
- Test plan, 26 documented test cases and a sample bug report in `docs/`
- CI pipeline (GitHub Actions) running tests headless

## Setup (Windows / macOS / Linux)
Requirements: Python 3.9+ and Google Chrome (Firefox/Edge also work).
Selenium 4 downloads the matching browser driver automatically.

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate        macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
pytest                       # everything (opens Chrome - great for a live demo)
pytest --headless            # no browser window
pytest -m smoke              # critical checks only
pytest -m api                # API tests only (no browser needed)
pytest -m "ui and negative"  # combine markers
pytest --browser firefox     # chrome | firefox | edge
pytest -k checkout           # tests matching a name
```
Open `reports/report.html` after a run. Failure screenshots are saved in `reports/screenshots/`.

Want to click around the app yourself? `python -m demo_app.app` then open http://127.0.0.1:5000
(login: `standard_user` / `secret123`).

## Expected result
All tests pass except two that show as **XFAIL**: they are the deliberately planted
BUG-001 (case-sensitive search). This is intentional and shows defect handling.

## Project structure
```
demo_app/        application under test (Flask): UI + REST API
pages/           Page Objects (login, products, cart, checkout)
tests/ui/        Selenium UI tests
tests/api/       API tests (requests)
conftest.py      fixtures, CLI options, screenshot-on-failure hook
docs/            test plan, test cases (CSV), bug report
.github/         CI workflow
```

## Demo script (2 minutes)
1. `pytest -m smoke` - browser opens and runs critical flows.
2. Show `pages/` - explain Page Object Model and why locators live in one place.
3. Show a parametrised test (`test_checkout_validation_errors`) - 5 cases from one function.
4. `pytest -m api` - fast API checks, show `test_orders_api.py`.
5. Open `reports/report.html` and `docs/BUG-001_search_case_sensitive.md`.
6. To show a failure screenshot: temporarily change an expected text in a test, run it, open the report.

## Ideas to extend (mention in interviews)
Allure reports, pytest-xdist parallel runs, Playwright version, JMeter performance test, Jira integration.
