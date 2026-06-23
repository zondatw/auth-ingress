# Implementation Plan: Manage User Access

**Branch**: `004-manage-user-access` | **Date**: 2026-06-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-manage-user-access/spec.md`

## Summary

Add a secure first-install administrator bootstrap, an authenticated user
management page, and an operator CLI for user lifecycle and group-membership
changes. Keep group membership as the only per-user input to service access and
derive effective access from existing group rules.

The implementation extends the single server-rendered Python application with a
shared user-management service used by both web routes and CLI commands. A
singleton installation-state row serializes one-time bootstrap; per-user revision
numbers prevent stale access-list writes; account disable, privilege removal, and
credential reset revoke active sessions; reset secrets are stored only as digests
and delivered through an explicitly configured recovery channel. All mutations
are transactional and write redacted audit evidence.

## Technical Context

**Language/Version**: Python 3.12, 3.13, and 3.14

**Primary Dependencies**: FastAPI/Starlette, Jinja2, SQLAlchemy 2.x,
Argon2 password hashing, itsdangerous signed session/CSRF utilities, argparse,
and the Python standard email/SMTP libraries for the initial recovery delivery
adapter

**Storage**: SQLite for the packaged single-instance deployment, using explicit
transaction serialization for bootstrap and optimistic user revisions for
operator conflicts; schema remains compatible with a later PostgreSQL migration

**Testing**: pytest unit, contract, integration, and security tests; FastAPI test
client for route behavior; Playwright for first-run and administrator browser
journeys; subprocess-based CLI tests against disposable databases

**Target Platform**: Packaged Linux/macOS server application with desktop web
browsers and a local operator CLI

**Project Type**: Single server-rendered web application plus packaged CLI

**Performance Goals**: First bounded user-search result within 2 seconds for 95%
of requests over 10,000 users; confirmed changes visible within 5 seconds; a page
membership change under 60 seconds and CLI change under 30 seconds for an
operator; first bootstrap and verified sign-in under 5 minutes

**Constraints**: No default credentials, public bootstrap route, password/reset
secret in arguments or logs, direct per-user service grant, hard user deletion,
or partial mutation; authorization is rechecked at execution; the last active
administrator cannot be disabled or demoted; audit evidence is retained at least
90 days

**Scale/Scope**: Up to 10,000 managed identities, hundreds of groups, and tens to
hundreds of protected services in a single portal deployment; group/service-rule
administration, directory synchronization, bulk import, public registration,
and unattended bootstrap are outside this feature

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

- **Secure Identity Boundaries**: PASS before and after design. The plan names
  user identity, privilege, membership, effective access, session, password,
  reset secret, installation state, and audit boundaries. Secrets enter through
  hidden input or a protected recovery channel, are hashed/digested at rest, and
  never enter page, CLI, or audit output.
- **User-Centered Authentication Flows**: PASS before and after design. Contracts
  cover clean bootstrap, already-initialized and failed bootstrap, sign-in before
  setup, search and empty state, preview/confirm, conflicts, denied operations,
  account disable/reactivation, reset delivery failure, and safe retry.
- **Testable Security Behavior**: PASS before and after design. Planned contract,
  integration, security, CLI, and browser validation covers successful and
  denied access, malformed input, stale revisions, concurrent bootstrap,
  disabled/expired authorization, last-admin protection, secret redaction, and
  session revocation.
- **Observable and Auditable Operations**: PASS before and after design. The data
  model and operation contract define actor, target, action, outcome, reason,
  changed-field names, timestamp, and client category while prohibiting values
  that contain credentials, reset secrets, sessions, or excess personal data.
- **Simple, Explicit Architecture**: PASS before and after design. One shared
  application service owns web/CLI behavior. SQLite, SMTP recovery delivery, and
  the existing session/password libraries have named ownership and failure
  behavior; no background job, separate frontend, or new identity provider is
  introduced.

## Project Structure

### Documentation (this feature)

```text
specs/004-manage-user-access/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   ├── management-operations.md
│   └── ui-flows.md
└── tasks.md
```

### Source Code (repository root)

```text
src/auth_entry_portal/
├── cli.py
├── config.py
├── main.py
├── models/
│   ├── audit_event.py
│   ├── identity.py
│   ├── installation.py
│   └── password_reset.py
├── repositories/
│   └── schema.py
├── security/
│   └── dependencies.py
├── services/
│   ├── audit_service.py
│   ├── bootstrap_service.py
│   ├── password_reset_service.py
│   └── user_admin_service.py
└── web/
    ├── routes/
    │   ├── admin_users.py
    │   └── password_reset.py
    └── templates/
        ├── admin/users.html
        ├── admin/user_detail.html
        ├── auth/setup_required.html
        └── auth/reset_password.html

tests/
├── contract/
├── e2e/
├── integration/
├── security/
└── unit/
```

**Structure Decision**: Extend the existing `src/auth_entry_portal/` single
application. Routes and CLI remain thin adapters; shared services own validation,
authorization, transactions, preview calculation, lockout safeguards, and audit
creation. This preserves the current architecture and guarantees interface
parity without a new API tier or frontend project.

## Complexity Tracking

No constitution violations are accepted for this plan.
