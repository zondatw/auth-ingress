# Implementation Plan: Tech Style UI Refresh

**Branch**: `009-tech-style-ui` | **Date**: 2026-06-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/009-tech-style-ui/spec.md`

## Summary

Refresh the existing auth-ingress server-rendered UI into a cohesive dark,
technical control surface inspired by `zondatw/agent-interlude`'s monitoring
console feel: dense but readable operational context, scan-friendly cards,
timeline/detail patterns, and high-contrast diagnostic states. The technical
approach is to evolve the existing Jinja templates and local static stylesheet,
reuse current route data wherever possible, and add only small safe summary
view-models where required for admin context.

## Technical Context

**Language/Version**: Python 3.12+ application; package currently supports
Python 3.12, 3.13, and 3.14.

**Primary Dependencies**: Existing FastAPI/Starlette routing, Jinja2
server-rendered templates, local static CSS, pytest, and Playwright browser
tests. No third-party hosted design assets or client-side frameworks.

**Storage**: No persistence schema changes planned. Any operational summaries
must be derived from existing users, groups, services, and audit records.

**Testing**: pytest contract/integration/security tests for rendered UI
contracts, preserved security behavior, and redaction; Playwright e2e/browser
tests for layout, navigation, keyboard focus, responsive behavior, and core
journeys.

**Target Platform**: Desktop and mobile browsers served by the existing
server-rendered auth-ingress web application.

**Project Type**: Single Python server-rendered web application.

**Performance Goals**: Refreshed pages remain visually usable within the
existing local-network expectations; admin summary queries must not add
noticeable delay for the small internal-portal scope.

**Constraints**: Preserve existing authentication, authorization, CSRF,
password, service-entry, management-form, and audit behavior; do not expose
secrets; no external font/script/CDN dependency; mobile layouts must avoid page
overflow except intentional scroll containers for dense tables.

**Scale/Scope**: All visible auth-ingress pages under auth, portal, admin,
audit, errors, and password flows. Initial scope targets a small internal portal
with hundreds of users and tens of services.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Secure Identity Boundaries**: PASS. The refresh affects templates, styles,
  and safe summaries only. Credentials, sessions, CSRF tokens, reset secrets,
  temporary passwords, authorization decisions, and audit-sensitive fields are
  explicitly protected from unnecessary display.
- **User-Centered Authentication Flows**: PASS. Sign-in, first setup, password
  change/reset, denial, validation failure, unavailable/empty states,
  destructive confirmations, and retry guidance remain specified and testable.
- **Testable Security Behavior**: PASS. Planned tests cover positive rendering,
  denied/non-admin access, invalid/stale/destructive flows, preserved form
  values, secret redaction, keyboard focus, and responsive behavior.
- **Observable and Auditable Operations**: PASS. Existing audit behavior is
  preserved. New operational summaries are aggregate/read-only and must avoid
  secrets or unnecessary personal data.
- **Simple, Explicit Architecture**: PASS. Reuse current Jinja templates,
  route data, and local CSS rather than adding a separate frontend stack.

## Project Structure

### Documentation (this feature)

```text
specs/009-tech-style-ui/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── visual-system.md
│   ├── page-state-contract.md
│   └── accessibility-security.md
└── tasks.md
```

### Source Code (repository root)

```text
src/auth_ingress/
├── web/
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── portal/
│   │   ├── admin/
│   │   └── errors/
│   ├── static/
│   │   └── portal.css
│   └── routes/
│       ├── portal.py
│       ├── admin_users.py
│       ├── admin_groups.py
│       ├── admin_services.py
│       ├── admin_audit.py
│       └── auth.py
└── services/
    ├── audit_service.py
    ├── access_service.py
    ├── user_admin_service.py
    ├── group_admin_service.py
    └── service_admin_service.py

tests/
├── contract/
├── integration/
├── security/
└── e2e/
```

**Structure Decision**: Keep the feature inside the existing server-rendered web
surface. Most work belongs in `portal.css` and existing templates. Route/service
changes are limited to safe aggregate summaries needed by admin/portal context
cards and must not change authorization or persistence behavior.

## Complexity Tracking

No constitution violations are accepted for this plan.

## Post-Design Constitution Check

- **Secure Identity Boundaries**: PASS. Contracts define forbidden visible
  fields and required redaction behavior.
- **User-Centered Authentication Flows**: PASS. Quickstart covers sign-in,
  setup, password, portal, admin, validation-error, denial, and destructive
  confirmation journeys.
- **Testable Security Behavior**: PASS. Contracts map UI states to contract,
  security, and browser test expectations.
- **Observable and Auditable Operations**: PASS. Operational summaries are
  aggregate and read-only; existing audit retention remains unchanged.
- **Simple, Explicit Architecture**: PASS. No new frontend runtime, external
  hosted asset, storage layer, or analytics dependency is introduced.
