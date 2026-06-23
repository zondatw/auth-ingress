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
uv run pytest --cov=auth_entry_portal --cov-report=term-missing
```

Expected:

- Existing security, contract, integration, smoke, and browser tests pass.
- Auth, sessions, password reset, first install, service proxy, and user
  management behavior remain unchanged except for visible product naming.
