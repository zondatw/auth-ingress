# Implementation Plan: Full Web-App Proxy Support

**Branch**: `002-full-web-app-proxy` | **Date**: 2026-06-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-full-web-app-proxy/spec.md`

## Summary

Extend the authenticated portal from single-response service entry to a
full-browser reverse proxy. Each service receives an isolated public origin under
a configured wildcard proxy domain. The existing portal entry route authorizes
the user, issues a one-time launch ticket, and redirects to that service origin,
where a host-only proxy session is established. Catch-all HTTP and WebSocket
handlers revalidate the central portal session and service access rules before
streaming traffic to the fixed internal destination.

The design deliberately avoids rewriting arbitrary HTML, CSS, and JavaScript.
Separate service origins preserve root-relative URLs, nested navigation, browser
cookie behavior, and same-origin application requests. Internal absolute URLs
remain a compatibility failure unless the downstream application can be
configured with its public service origin.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: FastAPI/Starlette for host-aware HTTP and WebSocket
routing; HTTPX `AsyncClient` for pooled streaming HTTP forwarding; `websockets`
for downstream WebSocket connections; SQLAlchemy for launch-ticket and session
persistence; existing Jinja2, itsdangerous, and Argon2 security utilities

**Storage**: Existing SQLite store for initial deployment, adding one-time proxy
launch tickets and per-service proxy policy fields; schema remains portable to
PostgreSQL

**Testing**: pytest contract/integration/security tests; Playwright with a local
representative downstream application covering assets, nested navigation, data
requests, forms, uploads, downloads, cookies, redirects, range responses, and
WebSockets

**Target Platform**: Linux/macOS server process behind TLS termination with a
portal hostname plus wildcard DNS/TLS for service subdomains; desktop and mobile
standards-based browsers

**Project Type**: Single server-rendered web application acting as an
authentication portal and application reverse proxy

**Performance Goals**: No more than 500 ms p95 added latency for normal
local-network interactions; stream 50 MB uploads and 100 MB downloads without
buffering entire bodies; sustain the existing small-deployment target of tens of
services and hundreds of users

**Constraints**: Every new HTTP request and WebSocket handshake must revalidate
session, user, service, and group authorization; direct downstream access remains
network-restricted; arbitrary destinations, DNS rebinding to public addresses,
unsafe redirects, reserved-cookie replacement, and cross-service routing are
denied; payloads, cookies, tickets, sessions, destinations, and secrets are never
logged; wildcard DNS and TLS are deployment prerequisites

**Scale/Scope**: Version 1 supports one fixed internal HTTP(S) destination per
service, all standard HTTP methods, streaming request/response bodies, safe
headers/cookies/redirects, byte-range passthrough, and bidirectional WebSockets.
Raw TCP tunnels, native protocols, automatic rewriting of arbitrary JavaScript,
and authentication of third-party origins are out of scope.

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

- **Secure Identity Boundaries**: PASS. Portal and per-service browser origins,
  one-time launch tickets, host-only proxy cookies, central session validation,
  fixed internal destinations, DNS/IP validation, and state isolation define the
  trust boundaries. Credentials, tickets, cookies, sessions, destinations, and
  payloads are classified as sensitive and excluded from logs/audits.
- **User-Centered Authentication Flows**: PASS. Design artifacts cover authorized
  launch, direct service-host access, nested navigation, denied/expired access,
  unsafe redirects, incompatible apps, downstream timeout/disconnect, interrupted
  transfer, and WebSocket reconnect behavior.
- **Testable Security Behavior**: PASS. Planned tests cover allowed traffic,
  signed-out and revoked sessions, permission/service changes, malformed paths,
  arbitrary hosts/destinations, DNS rebinding, cookie collision, redirect escape,
  payload redaction, transfer failure, and WebSocket denial/reconnect.
- **Observable and Auditable Operations**: PASS. Launch, allowed entry, denied
  request/handshake, unsafe redirect, upstream failure, and compatibility-check
  events use non-sensitive reason codes and correlation identifiers. Successful
  static-resource requests remain diagnostic metrics rather than per-resource
  audit rows to prevent excessive audit volume.
- **Simple, Explicit Architecture**: PASS. The existing application process,
  database, session model, and authorization service are retained. One new
  `websockets` dependency is required because HTTPX does not proxy WebSocket
  frames. One-time launch tickets are the smallest mechanism that can establish
  host-only service authentication without sharing the portal cookie across all
  subdomains.

## Project Structure

### Documentation (this feature)

```text
specs/002-full-web-app-proxy/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── host-routing.md
│   ├── http-forwarding.md
│   ├── websocket-forwarding.md
│   └── compatibility.md
└── tasks.md
```

### Source Code (repository root)

```text
src/auth_portal/
├── config.py
├── main.py
├── models/
│   ├── service_entry.py
│   └── proxy_launch_ticket.py
├── repositories/
├── security/
│   ├── cookies.py
│   └── proxy_destination.py
├── services/
│   ├── access_service.py
│   ├── proxy_authorization_service.py
│   ├── proxy_header_policy.py
│   ├── proxy_http_service.py
│   ├── proxy_websocket_service.py
│   └── service_compatibility_service.py
└── web/
    ├── routes/
    │   ├── services.py
    │   ├── proxy.py
    │   └── admin_services.py
    └── templates/admin/services.html

tests/
├── contract/
│   ├── test_proxy_host_contract.py
│   ├── test_proxy_http_contract.py
│   └── test_proxy_websocket_contract.py
├── integration/
│   ├── test_proxy_assets.py
│   ├── test_proxy_interactions.py
│   └── test_proxy_websocket.py
├── security/
│   ├── test_proxy_authorization.py
│   ├── test_proxy_destination.py
│   ├── test_proxy_headers.py
│   └── test_proxy_state_isolation.py
├── e2e/test_full_web_app_proxy.py
└── fixtures/downstream_app.py
```

**Structure Decision**: Extend the existing single application and risk-grouped
test structure. Host routing, authorization, HTTP transport, WebSocket transport,
and header policy are separate modules because they have different trust inputs
and failure modes, but remain within the existing process and deployment unit.

## Complexity Tracking

No constitution violations require justification.

