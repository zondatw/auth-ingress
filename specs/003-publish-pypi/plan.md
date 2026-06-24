# Implementation Plan: Publish Auth Entry Portal to PyPI

**Branch**: `003-publish-pypi` | **Date**: 2026-06-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-publish-pypi/spec.md`, including
GitHub Actions CI/CD and confirmation that the existing `auth-entry-portal`
distribution name is retained.

## Summary

Publish the existing `auth-entry-portal` distribution as one source archive and
one universal wheel through a least-privilege GitHub Actions pipeline. Pull
requests and main receive locked multi-version tests. A published GitHub Release
builds and validates artifacts once, stages them on TestPyPI, verifies an exact
clean install, and promotes the unchanged artifacts to PyPI through a protected
environment using OIDC Trusted Publishing. The Python import namespace is renamed
to `auth_ingress`; the `auth-portal` CLI and configuration names remain
stable. The canonical GitHub repository is `zondatw/auth-entry-portal` before
release integration is registered.

## Technical Context

**Language/Version**: Python 3.12, 3.13, and 3.14; package metadata requires
Python >=3.12

**Primary Dependencies**: Existing FastAPI application dependencies; Hatchling
build backend; uv for locked environments and builds; GitHub Actions; PyPI and
TestPyPI; `pypa/gh-action-pypi-publish` for Trusted Publishing

**Storage**: No application storage changes; immutable wheel/source archives in
GitHub workflow artifacts, TestPyPI, and PyPI

**Testing**: pytest, pytest-cov, Playwright Chromium journeys, metadata/archive
validation, isolated wheel and source-install smoke tests, TestPyPI exact-version
installation

**Target Platform**: Universal Python wheel for Python >=3.12; CI and release on
GitHub-hosted Ubuntu runners; runtime remains platform-independent where current
dependencies support it

**Project Type**: Installable Python web application and CLI distribution

**Performance Goals**: Clean package install and smoke validation within 5
minutes; complete staging-to-public approval workflow within 15 minutes excluding
external index delays

**Constraints**: Build once and promote identical artifacts; no stored PyPI
credentials; production environment approval required; action dependencies
pinned to reviewed commit SHAs; version must match release tag; no overwrite or
silent duplicate skipping; public release blocked until license approval and
package-name registration succeed

**Scale/Scope**: One pure-Python distribution, one source archive, one universal
wheel, three Python versions, two workflows, two package indexes, two protected
environments, package metadata/documentation, release/recovery runbooks,
artifact-focused tests, and one canonical GitHub repository rename

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

- **Secure Identity Boundaries**: **PASS** — the only new authority is release
  publication authority, issued as a short-lived project/workflow/environment-
  bound token. Application credentials and sessions remain outside the release
  system.
- **User-Centered Authentication Flows**: **PASS** — install, publish, denial,
  duplicate, timeout, staging failure, approval, retry verification, yank, and
  credential-revocation journeys are specified.
- **Testable Security Behavior**: **PASS** — CI/release contract tests cover
  authorized and unauthorized triggers, version mismatch, malformed artifacts,
  missing resources, duplicates, and failed smoke checks before publication.
- **Observable and Auditable Operations**: **PASS** — GitHub deployment history,
  release records, index upload/yank records, artifact hashes, and job conclusions
  provide diagnostics; log review rejects tokens, application secrets, and
  personal data.
- **Simple, Explicit Architecture**: **PASS** — GitHub Actions owns orchestration,
  PyPI/TestPyPI own immutable distribution storage and OIDC exchange, Hatchling
  builds, and uv installs/tests. Build and publish remain separate jobs; no new
  application service or storage abstraction is introduced.

**Pre-design gate result**: PASS. No constitution exceptions are required.

**Post-design re-check**: PASS. The contracts preserve job-scoped OIDC, immutable
artifacts, explicit approval and recovery, test-first security gates, and
non-sensitive audit evidence. No complexity exception was introduced.

## Project Structure

### Documentation (this feature)

```text
specs/003-publish-pypi/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── ci-workflow.md
│   ├── package-distribution.md
│   └── release-operations.md
└── tasks.md                    # generated later by /speckit-tasks
```

### Source Code (repository root)

```text
.github/
├── dependabot.yml
└── workflows/
    ├── ci.yml
    └── release.yml

src/auth_ingress/                 # renamed runtime/import namespace
├── cli.py
├── main.py
└── web/
    ├── static/
    └── templates/

tests/
├── contract/
│   └── test_package_contract.py
├── integration/
│   └── test_distribution_artifacts.py
└── smoke/
    └── test_installed_package.py

CHANGELOG.md
LICENSE                           # owner-approved content required before release
README.md
pyproject.toml
uv.lock
```

**Structure Decision**: Preserve the current single-package `src/` layout and
runtime namespace. Add repository-root release metadata, package-focused tests,
and two top-level workflows. Build and release behavior stays outside application
modules; no runtime code layer or database migration is needed.

## Phase 0: Research Decisions

Research is recorded in [research.md](./research.md). The resolved decisions are:

1. Retain `auth-entry-portal`; recheck availability immediately before Trusted
   Publisher registration.
2. Use the renamed canonical GitHub repository `zondatw/auth-entry-portal` and
   rename the Python import namespace to `auth_ingress`.
3. Use pull-request/main CI and a separate GitHub Release-driven workflow.
4. Use TestPyPI and PyPI Trusted Publishers with separate protected environments.
5. Build once, validate both artifacts, and promote the identical artifact set.
6. Keep static versions synchronized with `v<version>` GitHub Release tags.
7. Pin actions and uv, keep OIDC permission publish-job-only, and use default PyPI
   attestations.
8. Block release until an owner-approved license and security contact exist.

## Phase 1: Design

### Package Boundary

- Distribution: `auth-entry-portal`.
- Import namespace: `auth_ingress`.
- CLI: `auth-portal`.
- Build output: exactly one `py3-none-any` wheel and one source archive.
- Runtime assets: all templates and static files under `src/auth_ingress/web/`.
- Version source: static `[project].version`, exactly matching the release tag.

### Continuous Integration

- `ci.yml` runs for pull requests and pushes to `main` with default
  `contents: read` permissions.
- A Python 3.12/3.13/3.14 matrix performs locked installation and the non-browser
  suite; the newest version also runs Chromium end-to-end tests and coverage.
- A package job builds the wheel/source archive, validates metadata and content,
  installs each independently, and invokes CLI help and disposable database
  initialization.
- CI is a required branch check before a GitHub Release can be published.
- Third-party action updates are proposed weekly through Dependabot and reviewed
  before changing full-SHA pins.

### Release Pipeline

1. Trigger only when a GitHub Release is published for a `v<version>` tag.
2. Validate tag/version equality, release type, checked-in lock state, package
   name, required public metadata, license/security prerequisites, and CI success.
3. Build once without OIDC authority; validate and smoke-test both artifacts;
   calculate hashes; upload one immutable workflow artifact.
4. In a separate `testpypi` environment job with job-scoped OIDC, download and
   publish the artifact set to TestPyPI.
5. In a non-OIDC verification job, wait with bounded retries for index
   propagation, install the exact TestPyPI version in isolation, and repeat CLI,
   database, template, and static-resource smoke checks.
6. In a separate protected `pypi` environment job with job-scoped OIDC, require
   maintainer approval, download the same artifact set, verify recorded hashes,
   and publish once to PyPI.
7. Verify the public version, hashes, metadata, and provenance without attempting
   another upload; write a non-sensitive workflow summary.

### External Configuration

- Verify the renamed `zondatw/auth-entry-portal` repository's default branch,
  protection, release, issue, and documentation links. The local `origin` already
  uses the new repository URL.
- Create pending Trusted Publishers for `auth-entry-portal` on PyPI and TestPyPI,
  bound to GitHub owner `zondatw`, repository `auth-entry-portal`, `release.yml`,
  and the matching `pypi` or `testpypi` environment.
- Protect `pypi` with required reviewers, prevent self-review and administrator
  bypass where supported, and restrict deployment to version tags.
- Protect `testpypi` with version-tag restrictions; approval is optional because
  it is a staging gate and has no PyPI authority.
- Do not configure `PYPI_API_TOKEN`, maintainer passwords, or long-lived upload
  secrets.

### Failure and Recovery

- A failed check or TestPyPI validation stops before public approval.
- A duplicate or ambiguous upload stops; maintainers compare published hashes to
  expected hashes before deciding whether the release completed.
- Index propagation uses bounded read-only retry, never repeated uploads.
- A defective release is yanked with a public reason and replaced by a new
  version. Published files and versions are never overwritten.
- A suspected release compromise revokes the Trusted Publisher association,
  cancels active workflows, records affected versions/hashes, and follows the
  documented notification/replacement procedure.

### Design Artifacts

- [data-model.md](./data-model.md) defines release, artifact, approval, and event
  states.
- [package-distribution.md](./contracts/package-distribution.md) defines names,
  metadata, contents, and smoke-test behavior.
- [ci-workflow.md](./contracts/ci-workflow.md) defines workflow triggers, jobs,
  permissions, artifacts, and gates.
- [release-operations.md](./contracts/release-operations.md) defines setup,
  normal release, failure verification, yank, and revocation procedures.
- [quickstart.md](./quickstart.md) provides runnable end-to-end validation.

## Complexity Tracking

No constitution violations or justified complexity exceptions.
