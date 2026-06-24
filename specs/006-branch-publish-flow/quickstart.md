# Quickstart: Branch Publish Flow

Use this guide to validate the branch-based release policy before enabling
publication.

## Prerequisites

- Clean working tree on branch `006-branch-publish-flow`.
- Existing package metadata identifies `auth-ingress`.
- TestPyPI and PyPI Trusted Publisher claims exist for the expected repository,
  workflow, and environments.
- No package-index API tokens or maintainer passwords are stored in repository
  or environment secrets.

## 1. Validate branch policy

Run release validation tests for these scenarios:

- `beta` authorizes TestPyPI only.
- `release` authorizes PyPI only.
- `main`, feature branches, `beta-fix`, `release-candidate`, and `releases` are
  rejected before upload.
- Duplicate versions on the target package index stop before upload.

Expected:

- Every wrong-branch attempt fails with a stable, non-sensitive reason code.
- No denied scenario reaches an upload step.

## 2. Validate workflow structure

Inspect the release workflow contract.

Expected:

- TestPyPI publish/verify jobs run only for `beta`.
- PyPI publish/verify jobs run only for `release`.
- Publish jobs retain job-scoped OIDC permission.
- Publish jobs do not checkout repository code or execute arbitrary repository
  commands.
- Static package-index credentials and `skip-existing` are absent.

## 3. Validate local package build

```bash
uv run python -m scripts.release.build_and_check
```

Expected:

- Wheel and source archive names use the `auth_ingress` normalized artifact
  prefix.
- Metadata identifies `auth-ingress`.
- Installed artifact smoke checks pass.
- `dist/SHA256SUMS` contains hashes for all release artifacts.

## 4. Validate staging release behavior

Create or simulate a release targeting `beta`.

Expected:

- TestPyPI receives the package version.
- PyPI does not receive the package version.
- Evidence records branch `beta`, target TestPyPI, version, artifact names,
  SHA-256 hashes, verification result, and final outcome.

## 5. Validate production release behavior

Create or simulate a release targeting `release`.

Expected:

- PyPI receives the package version only after validation passes.
- TestPyPI is not published as part of the same release request.
- Evidence records branch `release`, target PyPI, version, artifact names,
  SHA-256 hashes, verification result, provenance status when available, and
  final outcome.

## 6. Validate recovery and documentation

Review release and recovery runbooks.

Expected:

- Maintainers can identify the correct branch for staging and production in
  under two minutes.
- Duplicate, blocked, and ambiguous release attempts instruct maintainers to use
  read-only package-index verification and prepare a new version when needed.
- Evidence retention is at least 90 days.
- No docs, logs, or examples expose package-index secrets, application secrets,
  sessions, database content, or demo passwords.

## 7. Run regression suite

```bash
uv run pytest -q
uv run pytest tests/unit/test_release_validation.py tests/contract/test_github_workflows.py tests/security/test_release_workflow_security.py -q
```

Expected:

- Existing release, package, workflow, and security tests pass.
- New branch-policy tests pass for both allowed branches and denied branches.
