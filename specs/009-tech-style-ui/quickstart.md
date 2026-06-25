# Quickstart: Tech Style UI Refresh

Use this guide to validate the refreshed technical UI before implementation is
considered complete.

## Prerequisites

- Clean working tree on branch `009-tech-style-ui`.
- Test dependencies installed with `uv sync --extra test`.
- Browser test dependencies installed when running Playwright scenarios.
- Demo or test data contains at least one admin, one normal user, groups,
  services, access rules, and audit events.

## 1. Validate visual-system coverage

Open each visible page:

- `/sign-in`
- `/setup-required` path or first-install equivalent state
- `/change-password`
- `/reset-password`
- `/`
- `/admin/users`
- `/admin/groups`
- `/admin/services`
- `/admin/audit`
- access-denied/error state

Expected:

- Every page uses the refreshed dark technical shell.
- Navigation, panels, forms, buttons, tables, status chips, alerts, notices,
  and empty states are visually consistent.
- No page remains in the old generic light-only presentation.

## 2. Validate operational context

Open portal and admin pages with populated data.

Expected:

- Portal/admin pages show safe scan-friendly summaries where data exists.
- User, group, and service detail pages expose relationship/dependency context.
- Audit and empty states provide useful guidance without exposing secrets.

## 3. Validate security-sensitive states

Exercise:

- failed sign-in;
- setup required;
- first sign-in password change;
- temporary password display and copy;
- validation errors in user/group/service forms;
- deactivate/remove confirmation;
- unauthorized admin access;
- access denied for unavailable or unauthorized service entry.

Expected:

- Messages are clear, prominent, and safe.
- Safe form values remain after validation failure where existing behavior
  supports it.
- Destructive actions emphasize risk, target, and confirmation.
- No credentials, sessions, reset secrets, database details, or unnecessary
  personal data are visible.

## 4. Validate keyboard and responsive behavior

Use keyboard-only navigation and narrow viewport widths.

Expected:

- Every link, input, select, checkbox, button, and copy control is reachable.
- Focus indicators are visible.
- Mobile navigation remains usable.
- Tables and dense regions do not cause unintended full-page overflow.

## 5. Run focused tests

```bash
uv run pytest tests/contract/test_ui_style_contract.py tests/security/test_ui_style_security.py -q
uv run pytest tests/e2e/test_tech_style_ui.py -q
```

Expected:

- Visual contract, redaction/security, and browser journey tests pass.

## 6. Run regression tests

```bash
uv run pytest tests/contract/test_admin_contract.py tests/contract/test_admin_users_contract.py tests/contract/test_admin_groups_contract.py tests/contract/test_user_entry_contract.py -q
uv run pytest tests/security/test_admin_boundary.py tests/security/test_group_management_security.py tests/security/test_management_form_state.py tests/security/test_management_form_outcomes.py -q
uv run pytest -q
```

Expected:

- Existing authentication, portal, admin, group, service, audit, and form-state
  behavior continues to pass.

## Validation Evidence

Record final focused and full-regression results here during implementation.

- 2026-06-25: `uv run pytest tests/contract/test_ui_style_contract.py tests/security/test_ui_style_security.py tests/integration/test_ui_style_routes.py -q` → 13 passed, 1 warning.
- 2026-06-25: `uv run pytest tests/e2e/test_tech_style_ui.py -q` → 2 passed, 3 warnings.
- 2026-06-25: `uv run pytest tests/contract/test_admin_contract.py tests/contract/test_admin_users_contract.py tests/contract/test_admin_groups_contract.py tests/contract/test_user_entry_contract.py tests/security/test_admin_boundary.py tests/security/test_group_management_security.py tests/security/test_management_form_state.py tests/security/test_management_form_outcomes.py -q` → 28 passed, 1 warning.
- 2026-06-25: `uv run pytest -q` → 232 passed, 15 warnings.
