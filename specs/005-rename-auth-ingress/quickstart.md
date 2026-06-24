# Quickstart: Rename Auth Ingress

Use this guide to validate the rename end to end after implementation.

## Prerequisites

- Clean working tree on branch `005-rename-auth-ingress`.
- Python versions supported by the project are available through the existing
  validation workflow.
- Network access for final PyPI/TestPyPI and GitHub name checks before release.
- No real production secrets in local environment variables.

## 1. Validate preferred CLI identity

```bash
uv run auth-ingress --help
uv run auth-ingress init-db
uv run auth-ingress bootstrap-admin --email admin@example.test --display-name "Admin"
```

Expected:

- Help and command examples show `auth-ingress` as preferred.
- Bootstrap still prompts for passwords through hidden input.
- No password, session, reset token, or secret appears in output.

## 2. Validate compatibility CLI identity

```bash
uv run auth-portal --help
```

Expected:

- The compatibility command still works.
- Help or migration docs make clear that `auth-ingress` is preferred.
- Behavior remains identical for security-sensitive subcommands.

## 3. Validate configuration prefix migration

Run a disposable startup or config-loading check with both old and new prefixes
for a non-secret setting.

Expected:

- `AUTH_INGRESS_*` is preferred when both prefixes are present.
- `AUTH_PORTAL_*` remains accepted when the new prefix is absent.
- Documentation lists migration mapping without exposing real secrets.

## 4. Validate web UI identity

Start the portal locally and inspect:

- sign-in page;
- setup-required page;
- portal home page;
- admin users/services/audit pages;
- reset and change-password pages;
- access-denied page.

Expected:

- Current UI labels and page titles use `auth-ingress`.
- Existing authentication, authorization, password reset, first-install, proxy,
  and user-management behavior remains unchanged.

## 5. Validate docs and release identity

```bash
uv run python -m scripts.release.build_and_check
```

Expected:

- Artifact metadata identifies `auth-ingress`.
- Wheel/source archive names use the normalized `auth_ingress` prefix.
- Installed artifact smoke checks pass for `auth-ingress`.
- Compatibility command is present if retained by the implementation.

## 6. Validate old-name reference classification

Run the implementation-provided old-name scan over source, tests, docs,
workflows, release scripts, and built artifacts.

Expected:

- No unclassified old-name references remain.
- Every old-name reference is classified as compatibility alias, historical
  reference, security-stable identifier, or intentional exception.
- Current operator-facing docs use `auth-ingress` as the primary name.

## 7. Validate name availability before release

Check exact package endpoints:

- `https://pypi.org/pypi/auth-ingress/json`
- `https://test.pypi.org/pypi/auth-ingress/json`

Expected:

- Both remain unavailable before first publication, or a fallback decision is
  recorded before release.
- Repository-facing docs point to the canonical `zondatw/auth-ingress` URL.

## 8. Run regression suite

```bash
uv run pytest -q
uv run pytest --cov=auth_ingress --cov-report=term-missing
```

Expected:

- Existing security, contract, integration, smoke, and browser tests pass.
- Auth, sessions, password reset, first install, service proxy, and user
  management behavior remain unchanged except for visible product naming.

## Validation Evidence

Recorded on 2026-06-24 from branch `005-rename-auth-ingress`.

### Preferred and compatibility identity

- `pyproject.toml` exposes `auth-ingress` as the preferred console command and
  keeps `auth-portal` as a compatibility command pointing to the same CLI entry.
- Runtime configuration prefers `AUTH_INGRESS_*` and falls back to
  `AUTH_PORTAL_*` when the new variable is absent.
- Python import namespace remains `auth_ingress`.
- Security-stable cookie, CSRF, password-reset, proxy-header, and historical
  labels that still contain old names are classified as intentional historical
  or compatibility references.

### Name availability

Checked exact package endpoints on 2026-06-24:

- `https://pypi.org/pypi/auth-ingress/json` returned `404`.
- `https://test.pypi.org/pypi/auth-ingress/json` returned `404`.

### Old-name classification

The implementation scan covered `README.md`, `docs/`, `.github/`, `src/`,
`tests/`, `scripts/`, `pyproject.toml`, and historical specs for publish,
user-management, and this rename feature.

Result:

- Zero unclassified old-name references.
- Remaining references are classified as compatibility aliases, historical
  references, or security-stable identifiers in
  `tests/fixtures/rename_inventory.py`.

### Regression and coverage

Commands:

```bash
uv run pytest -q
uv run pytest --cov=auth_ingress --cov-report=term-missing
```

Results:

- `uv run pytest -q`: `168 passed, 15 warnings`.
- Coverage run: `168 passed, 21 warnings`, total coverage `87%`.

### Python validation matrix

Commands:

```bash
uv run --python 3.12 --extra test pytest -q
uv run --python 3.13 --extra test pytest -q
uv run --python 3.14 --extra test pytest -q
```

Results:

- Python 3.12.10: `168 passed, 15 warnings`.
- Python 3.13.6: `168 passed, 15 warnings`.
- Python 3.14.5: `168 passed, 15 warnings`.

### Browser/UI identity evidence

The automated browser/UI identity checks passed through
`tests/e2e/test_rename_identity.py` as part of the full regression suite. The
covered pages include sign-in, setup-required, portal home, admin users,
admin services, admin audit, reset password, change password, and access denied.

### Release artifact evidence

Command:

```bash
uv run python -m scripts.release.build_and_check
```

Result:

- Built `dist/auth_ingress-0.1.0.tar.gz`.
- Built `dist/auth_ingress-0.1.0-py3-none-any.whl`.
- Installed artifact smoke checks passed for the renamed distribution.

Artifact hashes from `dist/SHA256SUMS`:

- `45e8cf8173db3bd86d4df7e9ed31075897e8295b0f2f12d45698a498e156c812  auth_ingress-0.1.0-py3-none-any.whl`
- `a54a0850652d849099d8ed5d90a31e85722d168d7f23c617a5f1c1a53fc7d823  auth_ingress-0.1.0.tar.gz`

### Requirement and contract mapping

- FR-001–FR-004, SC-001, SC-002, and SC-005: verified by docs, CLI, UI,
  package, installed artifact, and smoke tests.
- FR-005–FR-008 and SPR-001–SPR-005: verified by compatibility CLI/config
  tests, migration docs tests, admin-boundary tests, and old-name security
  classification tests.
- FR-009 and SC-004: verified by the comprehensive old-name scan with zero
  unclassified findings.
- FR-010: verified by the 2026-06-24 PyPI/TestPyPI exact endpoint checks.
- Release, migration, UI, CLI, package, and staged-index contracts all have
  passing automated coverage in the regression suite.
