# Implementation Plan: Auth Entry Portal

**Branch**: `001-auth-entry-portal` | **Date**: 2026-06-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-auth-entry-portal/spec.md`

## Summary

Build a mini auth portal that sits in front of downstream services that do not
have their own user-facing authentication flow. Users authenticate through the
portal, see only the services they may access, and enter protected services
through portal-controlled service routes. Administrators manage service entries,
access rules, enabled state, and audit visibility.

The technical approach is a single Python web application that serves the user
portal and admin UI, persists users/service entries/access rules/audit events,
and enforces authorization before forwarding or launching downstream service
requests. Downstream services must be reachable only through the portal or a
trusted internal network path; otherwise the portal cannot be the access boundary.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI/Starlette for web routing and middleware;
Jinja2 for server-rendered pages; SQLAlchemy or SQLModel for persistence; HTTPX
for downstream service forwarding; password hashing and signed-session utilities
from maintained Python security libraries

**Storage**: SQLite for the initial mini portal deployment and local validation,
with schema boundaries that can move to PostgreSQL without changing feature
behavior

**Testing**: pytest for unit/integration/security tests; Playwright for browser
journey tests covering sign-in, service entry, admin flows, and browser history
edge cases

**Target Platform**: Web application for desktop and mobile browsers, deployed as
one server-side application process

**Project Type**: Single server-rendered web application

**Performance Goals**: 95% of authorized users reach the intended service from a
signed-out start in under 60 seconds; portal pages feel interactive within 1
second in normal local-network conditions; admin service-entry changes complete
in under 3 minutes

**Constraints**: Credentials, session identifiers, secrets, and unnecessary
personal data must never appear in logs or audit payloads; downstream services
must not be directly reachable by users outside the portal path; failed sign-in
attempts must be rate-limited; audit records must be retained for at least 90
days

**Scale/Scope**: Initial scope targets a small internal portal with tens of
services, hundreds of users, and administrator-managed access rules. Self-service
registration and password recovery remain out of scope for this feature.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Secure Identity Boundaries**: PASS. The portal is the trust boundary for
  credentials, sessions, service destinations, access rules, and audit records.
  Downstream services must be isolated from direct user access so service entry
  decisions cannot be bypassed.
- **User-Centered Authentication Flows**: PASS. The plan covers direct portal
  sign-in, requested-service sign-in, successful entry, denial, expired sessions,
  unavailable services, empty service lists, and sign-out/browser-history
  behavior.
- **Testable Security Behavior**: PASS. Planned tests cover successful entry,
  signed-out denial, unauthorized denial, expired sessions, malformed service
  links, repeated failed sign-in attempts, disabled services, and sign-out
  history behavior.
- **Observable and Auditable Operations**: PASS. The data model and contracts
  require non-sensitive audit events for sign-in attempts, sign-out, service
  entry, denied access, and service-entry changes.
- **Simple, Explicit Architecture**: PASS. A single server-rendered application
  avoids a split frontend/backend for the first version. SQLite is selected for
  the mini portal scope, while keeping persistence boundaries portable.

## Project Structure

### Documentation (this feature)

```text
specs/001-auth-entry-portal/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── openapi.yaml
│   └── ui-flows.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── auth_portal/
    ├── main.py
    ├── config.py
    ├── models/
    ├── repositories/
    ├── services/
    ├── web/
    │   ├── routes/
    │   ├── templates/
    │   └── static/
    └── security/

tests/
├── contract/
├── integration/
├── security/
├── e2e/
└── unit/
```

**Structure Decision**: Use a single application under `src/auth_portal/` with
feature-oriented subpackages for models, repositories, services, web routes, and
security helpers. Tests are grouped by risk and validation type so security
coverage is easy to locate.

## Complexity Tracking

No constitution violations are accepted for this plan.
