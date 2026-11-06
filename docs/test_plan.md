# Test Plan - ShopEasy

| Item | Detail |
|---|---|
| Application under test | ShopEasy demo app (web UI + REST API), bundled in `demo_app/` |
| Objective | Verify login, product browsing/search, cart, checkout and order APIs |
| In scope | Functional UI tests, API tests (status codes, schema, validation, auth), negative and boundary tests |
| Out of scope | Performance, security penetration, cross-device/mobile testing |
| Tools | Python, Pytest, Selenium WebDriver, Requests, pytest-html, GitHub Actions |
| Design patterns | Page Object Model, explicit waits, parametrised data-driven tests, fixtures |
| Environments | Local (Chrome/Firefox/Edge), CI (headless Chrome) |

## Test types and markers
- `smoke` - 1 critical test per feature, runs first (`pytest -m smoke`)
- `regression` - full coverage (`pytest -m regression`)
- `negative` - invalid input / error handling
- `ui` and `api` - layer selectors

## Techniques used
- Equivalence partitioning and boundary value analysis (quantity 0/1/10/11, PIN length 5/6)
- Negative testing (empty fields, wrong credentials, locked user, unauthorised access)
- Authorisation testing (user cannot read another user's order)

## Entry / exit criteria
- Entry: build deployed and reachable
- Exit: 100% smoke pass, 95%+ regression pass, no open Critical/High defects

## Known defects
- BUG-001 - search is case-sensitive (tracked as `xfail(strict=True)`; the build fails if the bug is fixed without removing the marker)

## Risks
- UI locator changes break tests (mitigated by Page Objects: one fix location)
