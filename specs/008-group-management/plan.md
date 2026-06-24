# Implementation Plan: Group Management Page

**Branch**: `008-group-management` | **Date**: 2026-06-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-group-management/spec.md`

## Summary

Add an authenticated group management page for SRE/Admin operators to view access groups, understand user and service dependencies, create and edit safe group metadata, deactivate/reactivate groups, and permanently remove only unused groups. The implementation will extend the existing server-rendered admin UI, group/access models, management form-state behavior, audit evidence, and authorization checks so group lifecycle operations are visible, reversible where appropriate, and guarded against accidental access loss or administrator lockout.

## Technical Context

**Language/Version**: Python 3.12 project runtime, with current validation also covering Python 3.14-compatible behavior

**Primary Dependencies**: FastAPI/Starlette for routing and forms; Jinja2 for server-rendered admin pages; SQLAlchemy for persisted users, groups, service entries, access rules, and audit events; existing auth-ingress security helpers for CSRF, sessions, admin authorization, and rate limiting

**Storage**: Existing SQLite-backed SQLAlchemy persistence. Group records already exist; this feature requires lifecycle/status and revision metadata for groups, plus schema upgrade behavior for existing installations.

**Testing**: pytest for unit, contract, integration, and security tests; Playwright for browser/e2e validation of admin group journeys

**Target Platform**: Server-rendered web application for SRE/Admin operators in desktop and standard browser workflows

**Project Type**: Single Python web application with server-rendered admin UI

**Performance Goals**: Group list and detail pages render the first bounded result set within 2 seconds for normal operator requests; group create/edit flows complete in under 60 seconds for valid input; lifecycle changes appear in related management and access views within 5 seconds on fresh read

**Constraints**: Group names, membership counts, service associations, operator identity, and audit evidence are access-control data; authorization must be checked on every read and mutation; denied/stale/dependency-blocked operations must make no state change; group deactivation must stop future access grants promptly; permanent removal is limited to unused groups

**Scale/Scope**: Initial scope targets small internal deployments with tens to hundreds of groups, hundreds to thousands of users, and tens of services. Bulk group import, external directory sync, delegated group ownership, and bulk dependency cleanup are outside this feature.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Secure Identity Boundaries**: PASS. The feature touches group names, memberships, service associations, authorization decisions, operator identity, and audit records; all are classified as confidential access-control data, and no credentials or tokens are displayed or logged.
- **User-Centered Authentication Flows**: PASS. The plan covers success, denial, invalid input, stale edits, dependency-blocked removal, empty results, deactivation/reactivation, and retry/refresh outcomes.
- **Testable Security Behavior**: PASS. Planned artifacts require positive, denied, malformed, stale, dependency-blocked, last-admin-risk, and sensitive-output regression tests.
- **Observable and Auditable Operations**: PASS. Group create, update, deactivate, reactivate, removal, denied, stale, and dependency-blocked outcomes will emit structured non-sensitive audit evidence.
- **Simple, Explicit Architecture**: PASS. The feature stays in the existing server-rendered application and database model, extending current group and admin-management patterns without adding external providers, background jobs, or a separate frontend.

## Project Structure

### Documentation (this feature)

```text
specs/008-group-management/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── group-management-ui.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── auth_ingress/
    ├── models/
    │   └── identity.py
    ├── repositories/
    │   └── schema.py
    ├── services/
    │   ├── group_admin_service.py
    │   ├── access_service.py
    │   ├── audit_service.py
    │   └── user_management_types.py
    └── web/
        ├── routes/
        │   └── admin_groups.py
        └── templates/
            └── admin/
                ├── groups.html
                └── group_detail.html

tests/
├── contract/
│   └── test_admin_groups_contract.py
├── integration/
│   └── test_admin_groups.py
├── security/
│   └── test_group_management_security.py
├── e2e/
│   └── test_admin_groups.py
└── unit/
    └── test_group_admin_service.py
```

**Structure Decision**: Use the existing `src/auth_ingress/` single-application layout. Group lifecycle rules belong in a dedicated service module; routes assemble request-scoped form state and authorization context; templates render list/detail workflows; schema upgrades extend the existing group table for status/revision metadata.

## Complexity Tracking

No constitution violations are accepted for this plan.
