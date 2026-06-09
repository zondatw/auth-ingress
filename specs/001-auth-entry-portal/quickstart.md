# Quickstart: Auth Entry Portal

This guide validates the planned feature end to end after implementation.

## Prerequisites

- Python 3.12 available locally.
- `uv` available for environment and command execution.
- Browser runtime available for Playwright tests.
- Downstream demo services are reachable only through the portal path or a
  trusted internal network path.

## Setup

```bash
uv sync
uv run auth-portal init-db
uv run auth-portal seed-demo
```

Expected outcome:

- Database schema exists.
- Demo administrator, demo users, demo groups, and demo service entries exist.
- No seeded credentials or session identifiers appear in logs.

## Run the Portal

```bash
uv run auth-portal serve --host 127.0.0.1 --port 8000
```

Expected outcome:

- Portal home is reachable at `http://127.0.0.1:8000/`.
- Signed-out users are directed to sign in.

## Validate User Entry

1. Open a protected service route as a signed-out user.
2. Sign in as a user who is allowed for that service.
3. Confirm the user reaches the originally requested service.
4. Sign out.
5. Use browser history to try to return to the service.

Expected outcome:

- Requested service path is preserved through sign-in.
- Authorized entry succeeds.
- Sign-out prevents future access through browser history.
- Audit events exist for sign-in, service entry, and sign-out.

## Validate Unauthorized Access

1. Sign in as a user without access to a selected service.
2. Attempt to enter that service.
3. Attempt an unknown or disabled service route.

Expected outcome:

- The protected service is not opened.
- The user receives a clear unauthorized or unavailable message.
- Denied attempts create non-sensitive audit events.

## Validate Admin Service Management

1. Sign in as an administrator.
2. Add a service entry with a display name, destination, enabled state, and group
   access rule.
3. Sign in as a user in the allowed group and confirm the service appears.
4. Disable the service entry and confirm new access attempts are blocked.

Expected outcome:

- Admin changes are saved in under 3 minutes.
- Service visibility follows the configured access rule.
- Create, update, and disable actions create audit events.

## Run Automated Checks

```bash
uv run pytest
uv run pytest tests/security
uv run pytest tests/integration
uv run playwright test
```

Expected outcome:

- Positive and denied access paths pass.
- Expired or revoked sessions cannot authorize service entry.
- Repeated failed sign-in attempts are throttled.
- Audit-event tests confirm sensitive values are excluded.
