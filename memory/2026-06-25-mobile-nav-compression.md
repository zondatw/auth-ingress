# Debug Report: Mobile Navigation Compression

- Symptom: At phone widths, the admin navigation bar was too crowded and wrapped into a tall header.
- Root cause: The mobile CSS kept full navigation pills, allowed wrapping, and displayed the signed-in user chip alongside admin links.
- Fix: Changed the mobile header to a compact one-column grid, reduced brand/nav pill sizing, forced the nav rail to a single non-wrapping horizontal row, hid the user chip on phone widths, and allowed horizontal overflow as a fallback.
- Regression test: Added CSS contract assertions and a Playwright check that the phone-width header stays at or below 96px while admin nav links remain visible.
- Evidence: `uv run pytest tests/contract/test_ui_style_contract.py tests/e2e/test_tech_style_ui.py -q` → 8 passed.
- Status: DONE.
