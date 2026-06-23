# Release Infrastructure Setup

This file records the required non-sensitive configuration for publishing
`auth-ingress`. Never record OIDC tokens, API tokens, passwords, environment
secrets, or application credentials here.

## Canonical Identity

| Setting | Required value | Current evidence |
|---------|----------------|------------------|
| GitHub owner | `zondatw` | Repository remote |
| GitHub repository | `auth-ingress` | `git@github.com:zondatw/auth-ingress.git` |
| Default branch | `main` | Verified with GitHub repository metadata |
| Visibility | Public | Verified with GitHub repository metadata |
| Distribution | `auth-ingress` | `pyproject.toml` |
| Import namespace | `auth_entry_portal` | `src/auth_entry_portal/` |
| Release workflow | `.github/workflows/release.yml` | Implemented and contract-tested locally |

## Required CI Checks

Configure branch protection on `main` after `.github/workflows/ci.yml` has run at
least once. Require the multi-version tests, browser/coverage, and package jobs.
Do not allow a GitHub Release from a revision that lacks those successful checks.

## GitHub Environments

### `testpypi`

- Restrict deployments to tags matching `v*`.
- Do not store TestPyPI API credentials.
- Bind only the TestPyPI Trusted Publisher described below.

### `pypi`

- Restrict deployments to tags matching `v*`.
- Require a maintainer reviewer.
- Prevent self-review and administrator bypass where the repository plan allows.
- Do not store PyPI API credentials.
- Bind only the PyPI Trusted Publisher described below.

## Trusted Publisher Claims

Create separate pending publishers at PyPI and TestPyPI with these exact claims:

| Claim | PyPI | TestPyPI |
|-------|------|----------|
| Project | `auth-ingress` | `auth-ingress` |
| Owner | `zondatw` | `zondatw` |
| Repository | `auth-ingress` | `auth-ingress` |
| Workflow | `release.yml` | `release.yml` |
| Environment | `pypi` | `testpypi` |

The workflow must use job-scoped `id-token: write`; workflow-level OIDC
permission is prohibited. A claim mismatch is corrected in configuration and is
never bypassed with a long-lived token.

## Configuration Evidence

Record only URLs, configuration timestamps, GitHub environment names, package
project names, policy links, and coarse verification outcomes.

| Item | Status | Evidence |
|------|--------|----------|
| Canonical repository and remote | Verified | `git remote -v` |
| Required CI checks | Pending | Workflow must run first |
| `testpypi` environment | Blocked | GitHub CLI authentication must be renewed |
| `pypi` protected environment | Blocked | GitHub CLI authentication must be renewed |
| TestPyPI Trusted Publisher | Blocked | An authenticated TestPyPI owner session is required |
| PyPI Trusted Publisher | Blocked | An authenticated PyPI owner session is required |
| No package-index token secrets | Pending verification | Repository/environment settings |
| Evidence retention >= 90 days | Workflow-enforced; repository setting must remain 90 days | Release artifact `retention-days: 90` and policy links below |

## Retention Policy Evidence

- GitHub documents a default 90-day retention period for Actions logs and
  artifacts and permits public repositories to configure up to 90 days:
  https://docs.github.com/actions/managing-workflow-runs/removing-workflow-artifacts
- The release workflow sets the immutable artifact handoff to 90 days. Repository
  administrators must keep Actions log retention at 90 days and must not manually
  delete release workflow runs during an investigation.
- GitHub Releases, environment deployments/approvals, and Security Advisories
  provide durable source-side evidence unless an administrator deletes them.
- PyPI release files, SHA-256 hashes, provenance, and yank reasons provide public
  index-side evidence. Yanking is preferred to deletion:
  https://docs.pypi.org/project-management/yanking/
- Pending Trusted Publisher setup and its repository/workflow/environment claim
  are documented by PyPI here:
  https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/

If any service changes its retention policy below 90 days, export only the
allowlisted version, revision, filename, hash, approval outcome, and reason-code
evidence to an organization-controlled audit store before expiry.

## Immutable Action and Tool Inventory

Dependabot proposes GitHub Action updates weekly. A maintainer reviews upstream
release notes and commit identity, runs workflow contract/security tests, and
updates both the full SHA and human-readable version comment together.

| Dependency | Reviewed version | Immutable reference |
|------------|------------------|---------------------|
| `actions/checkout` | v6 | `df4cb1c069e1874edd31b4311f1884172cec0e10` |
| `astral-sh/setup-uv` | v8.1.0 | `08807647e7069bb48b6ef5acd8ec9567f424441b` |
| `actions/upload-artifact` | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |
| `actions/download-artifact` | v8.0.1 | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` |
| `pypa/gh-action-pypi-publish` | release/v1 | `cef221092ed1bacb1cc03d23a2d87d1d172e277b` |
| uv | 0.11.23 | Explicit workflow input |
| Hatchling | 1.30.1 | Exact build-system requirement |

Inventory reviewed on 2026-06-22. Floating action tags and unpinned build tools
are prohibited in release workflows.

## External Setup Status — 2026-06-22

Local workflow, package, permission, and redaction contracts pass. Live setup is
not complete: `gh auth status --hostname github.com` reports that the active
`zondatw` token is invalid, the in-app browser is unavailable, and no
authenticated PyPI or TestPyPI owner session is available. Consequently, the
GitHub environments, reviewer protection, Trusted Publisher claims, staging
rehearsal, and public release have not been represented as complete.
