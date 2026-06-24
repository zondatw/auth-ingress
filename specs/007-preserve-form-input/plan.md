# Implementation Plan: Preserve Management Form Input

**Branch**: `007-preserve-form-input` | **Date**: 2026-06-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-preserve-form-input/spec.md`

## Summary

Fix management-form validation UX so invalid submissions do not clear the user's safe entered values. The implementation will standardize form-state recovery for administrative create/edit flows, return field-level validation messages, preserve selection controls, and explicitly avoid redisplaying sensitive values such as temporary passwords, credentials, tokens, and recovery secrets.

The technical approach is to extend the existing server-rendered FastAPI/Jinja management UI with reusable form-state data structures, update service/user management routes to pass submitted safe values back to templates after validation failures, and add contract/integration/e2e regression coverage for the previously reported cleared-field behavior.

## Technical Context

**Language/Version**: Python 3.12 project runtime, with current CI also validating Python 3.14-compatible behavior

**Primary Dependencies**: FastAPI/Starlette for routing and form handling; Jinja2 for server-rendered management pages; SQLAlchemy for persisted users, groups, service entries, access rules, and audit events; existing auth-ingress security helpers for CSRF, sessions, admin authorization, and rate limiting

**Storage**: Existing SQLite-backed SQLAlchemy persistence. No new durable tables are required; failed form state is request-scoped and must not be persisted except for non-sensitive audit outcomes.

**Testing**: pytest for contract, integration, unit, and security regression tests; existing browser/e2e tests for admin service and user management journeys

**Target Platform**: Server-rendered web application for SRE/Admin users in desktop and mobile browsers

**Project Type**: Single Python web application with server-rendered admin UI

**Performance Goals**: Failed validation responses should return in the same user-perceived time as existing management form responses; administrators should be able to correct one invalid field and resubmit in under 30 seconds; no management form should require re-entering safe unchanged values after validation failure

**Constraints**: Sensitive values must never be repopulated, logged, or audited; authorization failures must remain distinct from validation failures; CSRF failures must not preserve stale submissions as if they were valid recoverable data; duplicate resubmission protection and existing confirmation flows must remain intact

**Scale/Scope**: Covers current administrative management forms: service management, user creation, user profile edits, user memberships, user status, user deletion/confirmation, and password reset confirmation where applicable. Does not change the business validation rules or introduce client-side-only validation as the source of truth.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Secure Identity Boundaries**: PASS. The feature explicitly classifies sensitive fields and requires that credentials, temporary passwords, recovery values, session data, and tokens are never redisplayed, logged, or audited from failed submissions.
- **User-Centered Authentication Flows**: PASS. Invalid input, denied authorization, missing referenced records, expired forms, retry, and successful correction flows are specified as distinct user-visible outcomes.
- **Testable Security Behavior**: PASS. Planned tests cover successful correction, invalid input, malformed values, denied management attempts, stale records, sensitive-field non-repopulation, and regression cases for cleared management forms.
- **Observable and Auditable Operations**: PASS. Denied submissions, stale referenced records, malformed input, and suspicious repeated invalid submissions will continue to emit non-sensitive audit/diagnostic events.
- **Simple, Explicit Architecture**: PASS. The design stays within the existing server-rendered application and does not add new storage, client-only validation authority, background jobs, or external dependencies.

## Project Structure

### Documentation (this feature)

```text
specs/007-preserve-form-input/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── management-form-state.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── auth_ingress/
    ├── services/
    │   ├── service_admin_service.py
    │   ├── user_admin_service.py
    │   └── user_management_types.py
    └── web/
        ├── routes/
        │   ├── admin_services.py
        │   └── admin_users.py
        └── templates/
            └── admin/
                ├── services.html
                ├── users.html
                └── user_detail.html

tests/
├── contract/
│   ├── test_admin_contract.py
│   └── test_admin_users_contract.py
├── integration/
│   ├── test_admin_services.py
│   └── test_user_lifecycle.py
├── security/
└── e2e/
    ├── test_admin_services.py
    └── test_admin_users.py
```

**Structure Decision**: Use the existing single application under `src/auth_ingress/`. Route handlers will own request recovery and template context assembly, service modules will continue to own business validation, and templates will render preserved safe values and field-specific errors. Tests stay in the existing contract/integration/security/e2e groups.

## Complexity Tracking

No constitution violations are accepted for this plan.
