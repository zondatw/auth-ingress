# Quickstart: Full Web-App Proxy Support

This guide validates the planned feature end to end after implementation. It
uses the representative downstream fixture defined by the test suite rather than
a production application.

## Prerequisites

- Python 3.12+ and `uv`.
- Chromium installed for Playwright.
- A local portal hostname and wildcard service hostname resolving to loopback
  (for example, `portal.localhost` and `*.apps.localhost`).
- TLS/wildcard certificate configuration for deployment validation; local tests
  may use the documented development-cookie mode.
- Existing demo users, groups, sessions, and service access rules.

## Setup

```bash
uv sync --extra test
uv run playwright install chromium
uv run auth-portal init-db
uv run auth-portal seed-demo
```

Configure the portal host, proxy base domain, secret, secure-cookie mode,
trusted proxy addresses, connection timeouts, transfer limits, and WebSocket
maximum lifetime using the settings documented during implementation.

## Start the Compatibility Fixture and Portal

Run the test downstream fixture on a trusted loopback/private address, then run
the portal on its configured portal host. The fixture must provide:

- Relative and root-relative CSS, JavaScript, image, and font resources.
- Nested routes and refresh-safe navigation.
- Background JSON actions, a form, query echo, upload, download, and range
  response.
- Application cookies and internal/external redirects.
- A text/binary WebSocket echo endpoint.

Expected outcome: neither process prints credentials, launch tickets, session or
cookie values, request/response bodies, private destinations, or uploaded data.

## Validate Complete Application Rendering

1. Open the protected fixture from the portal as an authorized user.
2. Confirm the portal performs a one-time redirect to the fixture's service host
   and removes the ticket from the final URL.
3. Confirm styles, scripts, image, font, and nested route content load.
4. Refresh the nested page and open it in a new tab.

Expected outcome: every request remains on the service host, the page renders
correctly, and the private destination never appears in page content, URLs, or
browser-visible response headers.

## Validate Interaction and State

1. Submit the fixture form and background data action with repeated query values.
2. Upload a file up to 50 MB and verify the fixture's checksum result.
3. Download a file up to 100 MB and verify its filename and checksum.
4. Request a valid byte range and verify partial content behavior.
5. Set fixture state, then open a second protected service using the same cookie
   name and verify the states do not collide.
6. Follow an internal redirect and attempt an external redirect.

Expected outcome: safe interactions work, transfers stream without corruption,
state remains service-specific, internal redirects stay on the service host, and
external redirects fail safely and are audited without target details.

## Validate Authorization and Abuse Boundaries

1. Request the service host without a proxy cookie.
2. Reuse an already consumed launch ticket and try it on another service host.
3. Sign out, disable the service, remove group access, and disable the user in
   separate runs, retrying a page, asset, form, upload, and reconnect each time.
4. Attempt malformed hosts, encoded path traversal, destination-selection input,
   reserved cookie replacement, public/metadata address resolution, and an
   internal-origin redirect to a different destination.

Expected outcome: every attempt is denied before protected content is returned;
no browser input changes the upstream origin; all audit events contain only
allowlisted context and reason codes.

## Validate WebSockets and Failures

1. Open the fixture WebSocket, exchange text and binary frames, and close cleanly.
2. Repeat while signed out, after permission removal, and after session expiry.
3. Interrupt the downstream connection, trigger connect/read timeouts, cancel a
   download, and stop an upload midway.

Expected outcome: authorized frames preserve type and content, denied handshakes
never connect downstream, reconnects reauthorize, both relay directions close on
failure, and partial failures expose no internal detail.

## Run Automated Checks

```bash
uv run pytest tests/contract
uv run pytest tests/security
uv run pytest tests/integration
uv run pytest tests/e2e/test_full_web_app_proxy.py
uv run pytest --cov=auth_portal
```

Expected outcome: the contract, security, integration, real-browser compatibility,
and existing auth portal regression suites pass, including the measurable
criteria in [spec.md](./spec.md).

