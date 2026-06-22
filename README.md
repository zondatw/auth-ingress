# Auth Entry Portal

A small server-rendered FastAPI portal that authenticates internal users before
allowing them to enter downstream services that do not implement their own login
flow.

## Trust boundary

The portal is an access-control boundary only when downstream services are
reachable exclusively from the portal or a trusted internal network. Never
configure a publicly reachable downstream URL: users who know it could bypass
the portal. Destinations are restricted to loopback, private IP addresses,
`.internal` hosts, and local `mock://` demo targets. Embedded credentials, query
parameters, and fragments are rejected.

Credentials are Argon2-hashed. Browser cookies contain only a signed opaque
reference to a server-side session and use HttpOnly and SameSite protections.
Production deployments must set `AUTH_PORTAL_SECRET_KEY` to a high-entropy value,
enable `AUTH_PORTAL_SECURE_COOKIES=true`, terminate TLS, and protect the SQLite
file at the operating-system level.

## Setup and operation

```bash
uv sync --extra test
uv run auth-portal init-db
uv run auth-portal seed-demo
uv run auth-portal serve --host 127.0.0.1 --port 8000
```

Configuration uses these environment variables:

- `AUTH_PORTAL_DATABASE_URL`
- `AUTH_PORTAL_SECRET_KEY`
- `AUTH_PORTAL_SESSION_COOKIE`
- `AUTH_PORTAL_SESSION_TTL`
- `AUTH_PORTAL_SECURE_COOKIES`
- `AUTH_PORTAL_RATE_LIMIT_ATTEMPTS`
- `AUTH_PORTAL_RATE_LIMIT_WINDOW`
- `AUTH_PORTAL_AUDIT_RETENTION_DAYS` (minimum/default: 90)
- `AUTH_PORTAL_DOWNSTREAM_TIMEOUT`

Demo accounts use the addresses shown by the seed implementation with local-only
passwords in `src/auth_portal/cli.py`. Change or remove all demo accounts before
deployment. The CLI deliberately does not print credentials.

## Audit and recovery

Sign-in attempts, sign-out, allowed and denied service entry, and administrative
changes create structured database audit events. Context is allowlisted to a
correlation ID and coarse client category; passwords, cookies, session IDs,
secrets, request bodies, and unnecessary personal data are excluded. Retain
events for at least 90 days and back up the database according to organizational
policy.

If a downstream service fails, the portal returns a generic unavailable response
without retrying unsafe requests or exposing internal details. Operators should
use the response correlation ID and audit events to investigate. Revoke access by
disabling a user, removing group membership, disabling a service, or revoking its
active sessions; authorization is re-evaluated on every protected request.

## Validation

```bash
uv run pytest
```

The full manual journey is documented in
`specs/001-auth-entry-portal/quickstart.md`.
