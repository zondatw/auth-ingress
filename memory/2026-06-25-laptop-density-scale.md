# Debug Report: Laptop UI Density

- Symptom: In laptop browser mode, portal objects appeared too small.
- Root cause: The refreshed UI used one compact density across desktop and mobile: 16px base text, 24px panels, 170px metric columns, and 240px service card columns. This made laptop views feel underscaled.
- Fix: Added a desktop/laptop breakpoint at `min-width: 900px` to increase base font size, container width, panel padding, metric columns, service-card columns, service-card height, and control padding. Phone layout explicitly stays at 16px.
- Regression test: Added CSS contract checks and a Playwright laptop viewport test that verifies body font size and minimum portal card/metric dimensions.
- Evidence: `uv run pytest tests/contract/test_ui_style_contract.py tests/e2e/test_tech_style_ui.py -q` → 10 passed.
- Status: DONE.
