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
passwords in `src/auth_entry_portal/cli.py`. Change or remove all demo accounts before
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

## Full web-app proxy deployment

Full proxy mode gives every service an isolated browser origin. Production
deployments require:

- A dedicated portal host configured with `AUTH_PORTAL_HOST`.
- Wildcard DNS and TLS for `*.AUTH_PORTAL_PROXY_BASE_DOMAIN`.
- `AUTH_PORTAL_PROXY_SCHEME=https` and secure cookies.
- Private network routing from the portal to every downstream destination;
  downstream services must remain unreachable from user networks.
- A narrow comma-separated `AUTH_PORTAL_TRUSTED_DOWNSTREAM_NETWORKS` value.
- Explicit request/response byte limits, launch-ticket lifetime, upstream
  timeout, and WebSocket maximum lifetime appropriate to the deployment.

Relevant settings are `AUTH_PORTAL_PROXY_BASE_DOMAIN`,
`AUTH_PORTAL_PROXY_SCHEME`, `AUTH_PORTAL_PROXY_COOKIE`,
`AUTH_PORTAL_PROXY_LAUNCH_TTL`, `AUTH_PORTAL_PROXY_MAX_REQUEST_BYTES`,
`AUTH_PORTAL_PROXY_MAX_RESPONSE_BYTES`,
`AUTH_PORTAL_PROXY_WEBSOCKET_LIFETIME`, and
`AUTH_PORTAL_TRUSTED_DOWNSTREAM_NETWORKS`.

Enable proxy mode per service only after its compatibility check succeeds.
Applications should use relative or root-relative URLs, or be configured with
their public service origin. Fixed private origins embedded in JavaScript are not
rewritten. Roll back by disabling proxy mode for the service; the legacy simple
entry flow remains available for non-proxy service entries.

## Validation

```bash
uv run pytest
```

The full manual journey is documented in
`specs/002-full-web-app-proxy/quickstart.md`.
