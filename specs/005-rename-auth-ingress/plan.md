# Implementation Plan: Rename Auth Ingress

**Branch**: `005-rename-auth-ingress` | **Date**: 2026-06-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-rename-auth-ingress/spec.md`

## Summary

Rename the project/product identity to `auth-ingress` across operator-facing
installation guidance, release metadata, CLI entry points, web UI labels, package
validation, and release documentation while preserving current authentication,
authorization, session, proxy, user-management, and audit behavior. The approach
is a compatibility-aware rename: `auth-ingress` becomes the preferred public
distribution, command, repository, and UI identity; old command and configuration
names remain accepted or clearly documented for migration where needed.

## Technical Context

**Language/Version**: Python 3.12 minimum; validation also covers Python 3.13 and
3.14 as already required by the project metadata and CI.

**Primary Dependencies**: Existing FastAPI/Starlette server-rendered web
application, SQLAlchemy persistence, Hatchling packaging, uv-based local
validation, pytest, Playwright browser tests, GitHub Actions release workflows,
and PyPI/TestPyPI Trusted Publisher release tooling.

**Storage**: Existing SQLite-backed application data remains unchanged. No data
migration is planned for users, services, access rules, sessions, reset
requests, or audit events.

**Testing**: pytest contract/integration/security/smoke tests, Playwright browser
journeys for visible UI identity, artifact build/smoke validation, and targeted
text scans that classify remaining old-name references.

**Target Platform**: Server-side Python web application installed as a Python
distribution and operated through CLI commands on supported deployment hosts.

**Project Type**: Single server-rendered web application with CLI, package
metadata, release automation, and documentation surfaces.

**Performance Goals**: Rename must not regress existing portal performance;
release identity scans and artifact checks should complete as part of the
existing validation workflow without adding more than 2 minutes to local release
checks.

**Constraints**: Authentication, authorization, session, proxy, password,
password-reset, user-management, and audit semantics must not change. Secrets,
session IDs, reset factors, and credentials must not be introduced into logs,
docs, validation output, or release artifacts. Existing operators need a clear
migration path for old command, package, repository, and configuration names.

**Scale/Scope**: Rename all current primary references in source, docs,
templates, package metadata, tests, release scripts, CI/CD, and release setup
guidance. Preserve existing database content and historical audit/log meaning.
Classify old-name references that remain as compatibility aliases, historical
records, or intentional security-stable identifiers.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Secure Identity Boundaries**: PASS. The plan explicitly preserves all
  authentication, authorization, session, token, reset, and access-control
  behavior. Rename work only changes identity surfaces and compatibility aliases.
- **User-Centered Authentication Flows**: PASS. User-visible pages retain the
  same success, denial, recovery, first-install, and user-management flows while
  changing product labels to `auth-ingress`.
- **Testable Security Behavior**: PASS. Planned tests include regression checks
  proving old compatibility commands/configuration do not bypass existing auth
  safeguards, plus full existing auth/security test coverage.
- **Observable and Auditable Operations**: PASS. Audit event semantics and
  historical evidence are preserved; old names in historical records are
  documented rather than rewritten blindly.
- **Simple, Explicit Architecture**: PASS. No new external identity provider,
  cryptographic primitive, storage mechanism, background job, or service
  dependency is introduced. Current release tooling is updated in place.

## Project Structure

### Documentation (this feature)

```text
specs/005-rename-auth-ingress/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── naming-matrix.md
│   ├── cli-compatibility.md
│   └── release-identity.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml
.github/
├── RELEASE_SETUP.md
└── workflows/
    ├── ci.yml
    └── release.yml
docs/
├── releasing.md
├── release-recovery.md
└── user-management.md
scripts/release/
├── build_and_check.py
├── check_artifacts.py
├── package_metadata.py
├── validate_release.py
├── verify_index.py
└── verify_staged_release.py
src/auth_entry_portal/
├── cli.py
├── config.py
├── main.py
└── web/
    ├── templates/
    └── static/
tests/
├── contract/
├── integration/
├── security/
├── smoke/
└── unit/
```

**Structure Decision**: Extend the existing single application and release
tooling in place. The runtime import namespace remains under
`src/auth_entry_portal/` for compatibility unless implementation tasks prove a
safe alias-only migration is necessary; the public distribution, command, docs,
repository metadata, and UI identity become `auth-ingress`.

## Complexity Tracking

No constitution violations are accepted for this plan.

## Phase 0: Research Summary

Research is captured in [research.md](./research.md). Key decisions:

1. Use `auth-ingress` as the preferred public distribution, command, repository,
   and UI identity.
2. Keep the existing import namespace stable for this rename phase and expose
   compatibility only where it prevents operator breakage.
3. Preserve historical records and security salts instead of rewriting sensitive
   identity-bound material.
4. Add explicit old-name scanning and classification to release validation.

## Phase 1: Design Summary

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/naming-matrix.md](./contracts/naming-matrix.md)
- [contracts/cli-compatibility.md](./contracts/cli-compatibility.md)
- [contracts/release-identity.md](./contracts/release-identity.md)
- [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- **Secure Identity Boundaries**: PASS. Contracts preserve existing security
  behavior and explicitly reject weakening aliases.
- **User-Centered Authentication Flows**: PASS. UI and CLI contracts specify
  operator-visible rename behavior without changing auth flows.
- **Testable Security Behavior**: PASS. Quickstart includes unchanged full auth
  suite, alias checks, artifact smoke checks, and classified old-name scans.
- **Observable and Auditable Operations**: PASS. Historical audit/log references
  are preserved and documented; no sensitive payload expansion is planned.
- **Simple, Explicit Architecture**: PASS. The plan uses existing project
  packaging, release scripts, tests, and docs without adding new subsystems.
