# Auth Entry Portal

A small server-rendered FastAPI portal that authenticates internal users before
allowing them to enter downstream services that do not implement their own login
flow.

## Install from PyPI

Auth Entry Portal requires Python 3.12 or newer. Install a stable release in a
virtual environment and pin the version in managed deployments:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "auth-entry-portal==0.1.0"
auth-portal --help
```

The distribution name is `auth-entry-portal`, the Python import namespace is
`auth_entry_portal`, and the command remains `auth-portal`:

```python
from auth_entry_portal.main import create_app
```

Before first use, configure a high-entropy secret and an explicit database URL,
then initialize the schema:

```bash
export AUTH_PORTAL_SECRET_KEY="replace-with-a-high-entropy-secret"
export AUTH_PORTAL_DATABASE_URL="sqlite:////absolute/path/auth_portal.db"
auth-portal init-db
auth-portal serve --host 127.0.0.1 --port 8000
```

Upgrade only after reviewing [CHANGELOG.md](CHANGELOG.md), then install the exact
new version and rerun application smoke checks:

```bash
python -m pip install --upgrade "auth-entry-portal==<new-version>"
auth-portal --help
```

Verify the installed version with
`python -m pip show auth-entry-portal`. Remove the package with
`python -m pip uninstall auth-entry-portal`; database files and external
configuration are intentionally retained and must be removed separately if no
longer needed.

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

For a production-style first installation, create the first administrator with
the one-time local bootstrap command. It prompts twice without echoing or
accepting the password as an argument:

```bash
uv run auth-portal bootstrap-admin \
  --email admin@example.com \
  --display-name "Administrator"
uv run auth-portal serve --host 127.0.0.1 --port 8000
```

Before bootstrap, sign-in displays local setup guidance and never exposes a
registration form. Repeating the command after any identity exists makes no
change. If setup fails before completion, correct the reported non-secret input
or storage problem and safely retry the same command.

For disposable development data only:

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
- `AUTH_PORTAL_PASSWORD_RESET_TTL` (minimum: 300 seconds; default: 1800)
- `AUTH_PORTAL_SMTP_HOST`, `AUTH_PORTAL_SMTP_PORT`, `AUTH_PORTAL_SMTP_SENDER`
- `AUTH_PORTAL_SMTP_USERNAME`, `AUTH_PORTAL_SMTP_PASSWORD`, `AUTH_PORTAL_SMTP_STARTTLS`
- `AUTH_PORTAL_SMTP_TIMEOUT`
- `AUTH_PORTAL_USER_PAGE_SIZE` (10–100; default: 50)
- `AUTH_PORTAL_MANAGEMENT_RATE_LIMIT_ATTEMPTS`, `AUTH_PORTAL_MANAGEMENT_RATE_LIMIT_WINDOW`
- `AUTH_PORTAL_DOWNSTREAM_TIMEOUT`

Demo accounts use the addresses shown by the seed implementation. `seed-demo`
prompts for each password, or reads the local-only
`AUTH_PORTAL_DEMO_ADMIN_PASSWORD`, `AUTH_PORTAL_DEMO_MEMBER_PASSWORD`, and
`AUTH_PORTAL_DEMO_OUTSIDER_PASSWORD` values. Each must contain at least 12
characters. The CLI deliberately does not print credentials. Remove all demo
accounts and unset these variables before deployment.

Administrators manage users at `/admin/users` or with `auth-portal users`.
Memberships remain the only per-user access-list input; user detail explains all
groups granting each service. Page and CLI mutations preview first and reject a
stale user revision. Creating a user generates a one-time temporary password
that is shown only in the create response; the user must change it immediately
after first sign-in. Later password resets can still use configured SMTP links;
reset secrets are stored only as digests and never shown to an operator. See
[docs/user-management.md](docs/user-management.md) for commands, exit codes,
conflict recovery, lifecycle controls, and delivery troubleshooting.

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
