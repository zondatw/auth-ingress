# Quickstart: Preserve Management Form Input

## Prerequisites

- Dependencies installed with `uv sync --locked --extra test`
- A local test database or test client fixture with an administrator user
- Existing service and user management pages available

## Validation Commands

Run focused tests for the management forms:

```bash
uv run pytest tests/contract/test_admin_contract.py tests/contract/test_admin_users_contract.py -q
uv run pytest tests/integration/test_admin_services.py tests/integration/test_user_lifecycle.py -q
uv run pytest tests/e2e/test_admin_services.py tests/e2e/test_admin_users.py -q
```

Run sensitive-output regression coverage:

```bash
uv run pytest tests/security -q
```

## Manual Validation Scenarios

### Service create validation preserves values

1. Sign in as an administrator.
2. Open the service management page.
3. Enter a valid display name, description, destination, status, groups, and proxy settings.
4. Enter an invalid service slug or a non-existent group.
5. Submit the form.
6. Expected outcome:
   - The page shows a validation error.
   - Display name, description, destination, status, groups, and proxy settings remain visible.
   - The invalid field is identified.
   - Correcting only the invalid value allows resubmission.

### Service edit validation preserves existing context

1. Open an existing service entry.
2. Change several fields.
3. Submit an invalid destination or group selection.
4. Expected outcome:
   - The service being edited is still clear.
   - Safe changed values remain visible.
   - Existing service list and available groups remain visible.

### User creation validation preserves values

1. Open the user management page.
2. Enter email, display name, status, admin flag, and group selections.
3. Submit an invalid email or conflicting email.
4. Expected outcome:
   - Safe values remain visible.
   - Selected groups remain selected.
   - No temporary password is displayed unless creation succeeds.

### User detail validation preserves active form state

1. Open an existing user's detail page.
2. Change profile fields or memberships.
3. Submit a stale revision, invalid value, or invalid group selection.
4. Expected outcome:
   - The active form shows the relevant error.
   - Safe changed values remain visible.
   - Denied, conflict, and not-found outcomes are distinguishable.

### Sensitive values are not echoed

1. Trigger a failed form response in a flow that can involve password reset, temporary password, token, or recovery values.
2. Inspect the returned page.
3. Expected outcome:
   - Sensitive values are blank or absent.
   - Audit and diagnostic output does not contain sensitive submitted values.

## Expected Completion Signal

The feature is ready when all focused automated tests pass and manual browser validation confirms that failed management forms preserve safe values while never redisplaying sensitive fields.
