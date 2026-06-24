# Implementation Plan: Branch Publish Flow

**Branch**: `006-branch-publish-flow` | **Date**: 2026-06-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-branch-publish-flow/spec.md`

## Summary

Change the release pipeline so package publication is controlled by exact branch
policy: `beta` publishes staging releases to TestPyPI only, and `release`
publishes production releases to PyPI only. The implementation will adapt the
existing GitHub Release workflow and release validation scripts to classify a
release target, reject wrong-branch or duplicate-version attempts before upload,
and preserve non-sensitive evidence for every publish attempt.

## Technical Context

**Language/Version**: Python 3.12+ project; release validation currently runs
with Python 3.14 in CI.

**Primary Dependencies**: Existing GitHub Actions workflow, uv, Hatchling,
PyPI Trusted Publisher OIDC, PyYAML-based workflow contract tests, packaging
version validation, and existing release helper scripts.

**Storage**: No application storage changes. Release evidence remains in GitHub
workflow logs/artifacts, release records, and package-index metadata.

**Testing**: pytest unit, contract, and security tests for release validators,
workflow structure, docs/runbooks, and package-index verification behavior.

**Target Platform**: GitHub-hosted CI/CD for publishing the `auth-ingress`
Python package to TestPyPI and PyPI.

**Project Type**: Python package with server-rendered web application runtime and
release automation scripts/workflows.

**Performance Goals**: Wrong-branch and duplicate-version release attempts fail
before any upload step starts; branch-policy validation completes during the
existing release validation job without materially increasing release duration.

**Constraints**: No long-lived package-index tokens; OIDC permission remains
job-scoped; publish jobs do not checkout repository code or execute arbitrary
repo scripts; never overwrite or skip existing package files; evidence must not
contain secrets or application data.

**Scale/Scope**: One package distribution (`auth-ingress`), two publish
branches (`beta`, `release`), two package indexes (TestPyPI, PyPI), one release
workflow, and existing release documentation/scripts/tests.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Secure Identity Boundaries**: PASS. The feature touches release identity and
  package-index OIDC trust boundaries, not runtime user identity. Package-index
  credentials and OIDC permissions are explicitly constrained and excluded from
  logs/docs.
- **User-Centered Authentication Flows**: PASS. Runtime authentication flows are
  unaffected. Maintainer release flows define success, wrong-branch denial,
  duplicate-version denial, ambiguous upload recovery, and retry behavior.
- **Testable Security Behavior**: PASS. Planned tests cover allowed branch/index
  combinations, denied wrong-branch attempts, duplicate-version prevention,
  publish-job permission boundaries, and no-secret workflow content.
- **Observable and Auditable Operations**: PASS. Release attempts must record
  branch, target index, version, artifact names, hashes, verification result,
  final outcome, and safe failure reason.
- **Simple, Explicit Architecture**: PASS. Reuse existing workflow and release
  scripts rather than introducing another release system. External dependencies
  remain GitHub Actions, TestPyPI, PyPI, and Trusted Publisher OIDC.

## Project Structure

### Documentation (this feature)

```text
specs/006-branch-publish-flow/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── branch-policy.md
│   ├── release-workflow.md
│   └── release-evidence.md
└── tasks.md
```

### Source Code (repository root)

```text
.github/
└── workflows/
    └── release.yml

scripts/
└── release/
    ├── validate_release.py
    ├── verify_index.py
    ├── verify_staged_release.py
    └── package_metadata.py

docs/
├── releasing.md
└── release-recovery.md

tests/
├── contract/
│   ├── test_release_operations_contract.py
│   └── test_github_workflows.py
├── security/
│   └── test_release_workflow_security.py
└── unit/
    ├── test_release_validation.py
    └── test_index_verification.py
```

**Structure Decision**: Keep release policy in the existing release workflow and
release validation scripts. Add or extend tests beside the current release
contract/security/unit coverage so branch publishing behavior is verified
without changing application runtime modules.

## Complexity Tracking

No constitution violations are accepted for this plan.

## Post-Design Constitution Check

- **Secure Identity Boundaries**: PASS. Contracts preserve package-index OIDC
  boundaries and prohibit static credentials.
- **User-Centered Authentication Flows**: PASS. Release maintainer success,
  denial, duplicate-version, and ambiguous-state flows are represented in
  quickstart validation.
- **Testable Security Behavior**: PASS. Contracts identify unit, contract, and
  security tests for allowed and denied publish paths.
- **Observable and Auditable Operations**: PASS. `release-evidence.md` defines
  required non-sensitive evidence and retention expectations.
- **Simple, Explicit Architecture**: PASS. Design reuses existing release
  workflow/scripts and does not introduce a second release system.
