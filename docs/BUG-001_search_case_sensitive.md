# BUG-001 - Product search is case-sensitive

| Field | Value |
|---|---|
| Severity | Medium |
| Priority | Medium |
| Status | Open |
| Module | Products / Search (UI and `GET /api/products?search=`) |
| Environment | ShopEasy demo build, any browser |

## Steps to reproduce
1. Log in as `standard_user` / `secret123`.
2. On the Products page type `backpack` and press Search - Backpack is shown.
3. Search again with `BACKPACK`.

## Expected result
Search ignores letter case; Backpack is returned for `BACKPACK`, `backpack` and `Backpack`.

## Actual result
"No products found" for `BACKPACK`. The API returns an empty list for `?search=BACKPACK`.

## Impact
Customers typing in different cases (mobile auto-capitalisation) do not find products, which can lose sales.

## Suggested fix
Compare lowercased values: `term.lower() in p["name"].lower()` in `search_products()`.

## Automated evidence
`tests/ui/test_products.py::test_search_is_case_insensitive` and
`tests/api/test_products_api.py::test_search_is_case_insensitive` (both `xfail(strict=True)`).
