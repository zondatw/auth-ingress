# Debug Report: Form Button Spacing

- Symptom: Buttons in stacked management forms, for example the user detail `Account lifecycle` panel, appeared too close together.
- Root cause: The refreshed UI CSS defined spacing inside each `form`, but panels containing multiple sibling forms had no rule spacing `form + form`. The account lifecycle panel renders separate forms for status, password reset, and permanent removal.
- Fix: Added shared panel spacing rules in `src/auth_ingress/web/static/portal.css` for adjacent forms and paragraph-to-form transitions.
- Regression test: Added a contract assertion in `tests/contract/test_ui_style_contract.py` for `.panel>form+form`.
- Evidence: `uv run pytest tests/contract/test_ui_style_contract.py tests/e2e/test_tech_style_ui.py -q` → 8 passed.
- Status: DONE.
