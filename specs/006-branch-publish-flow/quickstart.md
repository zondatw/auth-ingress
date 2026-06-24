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

## Validation Evidence

Recorded on 2026-06-24 from branch `006-branch-publish-flow`.

### Branch policy simulations

Commands:

```bash
uv run python -m scripts.release.validate_release --action published --tag v0.1.0 --prerelease false --target-commitish beta
uv run python -m scripts.release.validate_release --action published --tag v0.1.0 --prerelease false --target-commitish release
uv run python -m scripts.release.validate_release --action published --tag v0.1.0 --prerelease false --target-commitish main
```

Results:

- `beta` validated as `branch=beta index=testpypi`.
- `release` validated as `branch=release index=pypi`.
- `main` was rejected with safe reason `release-target-unsupported` and no
  traceback.

### Focused release validation

Command:

```bash
uv run pytest tests/unit/test_release_validation.py tests/unit/test_index_verification.py tests/contract/test_branch_publish_policy.py tests/contract/test_github_workflows.py tests/security/test_release_workflow_security.py tests/contract/test_release_operations_contract.py -q
```

Result: `34 passed, 1 warning`.

### Full regression

Command:

```bash
uv run pytest -q
```

Result: `181 passed, 15 warnings`.

### Release build/check

Command:

```bash
uv run python -m scripts.release.build_and_check
```

Result:

- Built `dist/auth_ingress-0.1.0.tar.gz`.
- Built `dist/auth_ingress-0.1.0-py3-none-any.whl`.
- Installed artifact smoke checks passed.

Artifact hashes from `dist/SHA256SUMS`:

- `45e8cf8173db3bd86d4df7e9ed31075897e8295b0f2f12d45698a498e156c812  auth_ingress-0.1.0-py3-none-any.whl`
- `a54a0850652d849099d8ed5d90a31e85722d168d7f23c617a5f1c1a53fc7d823  auth_ingress-0.1.0.tar.gz`

### Requirement and contract mapping

- FR-001–FR-005 and SC-001–SC-003: covered by branch policy unit/contract
  tests and branch-conditioned workflow tests.
- FR-006–FR-008: covered by release validation and duplicate-version preflight
  tests.
- FR-009, SPR-003–SPR-005, and SC-005: covered by release evidence contracts,
  safe summary output, redaction checks, and runbook updates.
- FR-010 and SC-004: covered by updated release, recovery, setup, and historical
  publish documentation.
- SPR-001–SPR-002: covered by workflow security tests proving job-scoped OIDC,
  no static package-index credentials, no checkout/run steps in publish jobs,
  and separate branch-conditioned TestPyPI/PyPI publish paths.
