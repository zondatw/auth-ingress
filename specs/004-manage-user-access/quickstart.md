# Quickstart: Validate Manage User Access

This guide validates the feature end to end after implementation. Use a
disposable database and a local recovery-message sink; never use production
identities or credentials.

## Prerequisites

- Python 3.12, 3.13, or 3.14 with the project synchronized through `uv sync`.
- Playwright Chromium installed for browser journeys.
- A disposable writable directory.
- A local SMTP test sink configured through the planned recovery settings; it
  must not forward messages to real recipients.

Set a strong application secret and point the portal at a fresh disposable
database using the existing `AUTH_PORTAL_SECRET_KEY` and
`AUTH_PORTAL_DATABASE_URL` settings. Configure the recovery adapter with the
planned SMTP host, port, sender, transport-security, and optional authentication
settings. Secret values must come from protected deployment configuration and
must not be pasted into recorded test output.

## 1. Validate First Installation

Start from a database path that does not exist, then run:

```bash
uv run auth-portal bootstrap-admin \
  --email admin@example.test \
  --display-name "Initial Administrator"
```

Expected:

- The command prompts twice using hidden input.
- Schema and one active administrator are created atomically.
- The command prints no supplied password, hash, session, or reset data.
- A second invocation reports already initialized and changes nothing.
- Two concurrently started bootstrap attempts result in exactly one admin.

Before bootstrap, requesting `/sign-in` shows local setup instructions and no
registration form. After bootstrap, start the portal and verify that the new
administrator can sign in and open `/admin/users` within five minutes of starting
the first command.

## 2. Validate Search and Access Explanation

Create groups and service access rules using the existing administration flow,
then create several users through user management. Include active, disabled,
admin, and overlapping-membership examples.

Expected on `/admin/users` and user detail:

- Search/filter results are bounded and stable.
- User detail lists profile, revision, status, memberships, and every effective
  service with all granting groups.
- A disabled user shows retained policy but no currently usable service.
- Removing one of two granting groups preserves access through the other.
- A non-admin and a signed-out browser receive denial without user data.

## 3. Validate Preview, Commit, and Conflict

Open the same user in two admin browser sessions. Preview a membership change in
both, confirm the first, and then confirm the stale second preview.

Expected:

- Preview changes no state and explains group/effective-access differences.
- The first confirmation commits memberships and one revision increment.
- The stale confirmation returns a conflict and changes nothing.
- Refreshing displays the committed state through page and CLI within 5 seconds.
- Audit evidence contains actor, target, operation, safe changes, outcome, and
  reason but no sensitive values.

## 4. Validate CLI Parity

Use an active admin actor and hidden password prompt:

```bash
uv run auth-portal users list \
  --actor-email admin@example.test \
  --format json

uv run auth-portal users show 2 \
  --actor-email admin@example.test \
  --format json

uv run auth-portal users memberships add 2 staff \
  --actor-email admin@example.test \
  --expected-revision 1 \
  --format json

uv run auth-portal users memberships add 2 staff \
  --actor-email admin@example.test \
  --expected-revision 1 \
  --apply \
  --format json
```

Expected:

- The first membership command previews only.
- The applied command matches the preview and returns stable JSON.
- Repeating against the current revision reports `no_change` without a duplicate.
- Invalid input, denied actor, missing target, stale revision, and recovery
  dependency failure use the documented distinct exit codes.
- Table and JSON output contain no password, hash, reset token/digest, session,
  cookie, traceback, SQL, or configuration secret.

## 5. Validate Lifecycle and Lockout Protection

Through both page and CLI, exercise create, setup delivery, profile update,
disable, reactivate, admin demotion, and password-reset initiation.

Expected:

- New users start `setup_required`; setup links exist only in the local SMTP sink.
- Completing setup activates credentials and consumes the link once.
- Disable, password reset completion, and admin demotion revoke all target
  sessions immediately.
- Memberships remain while disabled and become usable again after reactivation.
- Self-disable, self-demotion, and last-active-admin disable/demotion are denied
  without state change.
- Expired, malformed, consumed, and superseded reset links share one safe failure
  message.
- Simulated delivery failure invalidates the request and supports a safe retry
  without exposing the link.

## 6. Run Automated Validation

```bash
uv run pytest tests/unit tests/contract tests/integration tests/security
uv run pytest tests/e2e
uv run pytest --cov=auth_entry_portal --cov-report=term-missing
uv run python -m scripts.release.build_and_check
```

Required coverage includes:

- Empty, successful, invalid, interrupted, repeated, and concurrent bootstrap.
- User normalization and duplicate detection during schema upgrade.
- Web/CLI operation parity and JSON/exit-code contracts.
- Stale revision and missing-group conflict behavior.
- Effective access with overlapping rules and disabled states.
- Last-admin/self-operation safeguards and immediate session revocation.
- Reset expiry, replay, supersession, delivery failure, and secret redaction.
- Search behavior over at least 10,000 generated identities.
- Installed wheel and source-archive smoke tests containing the new templates and
  CLI commands without repository-file dependence.

## 7. Inspect Non-Sensitive Evidence

Confirm audit retention remains at least 90 days and sample events for bootstrap,
view, create, membership, status, privilege, conflict, denial, reset delivery,
and reset completion. Only allowlisted actor/target IDs, operation, outcome,
reason, revision, field names, group IDs, correlation ID, client category, and
timestamps may appear.

Search captured page output, CLI output, application logs, audit rows, and built
artifacts for passwords, password hashes, reset secrets/digests, sessions,
cookies, authorization values, demo credentials, environment secrets, database
contents, and personal data beyond the authorized UI contract. The scan must find
none before the feature is accepted.

## Validation Record — 2026-06-23

- Python 3.12.10: 137 non-browser tests passed.
- Python 3.13.6: 137 non-browser tests passed.
- Python 3.14.5: 147 browser-inclusive tests passed; coverage run passed with
  87% line coverage.
- Accessibility and responsive checks passed for `/admin/users`: keyboard focus
  moved off the document body, narrow viewport rendered the user table, status
  text did not rely on color alone, and empty search state rendered a clear
  heading.
- Release artifact validation passed with forced isolated reinstallation of the
  local artifact to avoid stale package-cache entry points.
- Wheel: `auth_entry_portal-0.1.0-py3-none-any.whl`
  (`8b5f3c8a4674e084cb6af091d3043f8a4ba018f4562e6e79f5106ce21a9e8ab2`).
- Source archive: `auth_entry_portal-0.1.0.tar.gz`
  (`f8941151015f1738d39e3f395572d55c757e2a9518b0df71d65980e67da41946`).
- Artifact content scan passed for known demo credentials and release-token
  sentinel values; wheel/source smoke tests verified new templates and CLI
  commands from installed artifacts.
- Evidence coverage: FR-001–FR-026, SPR-001–SPR-012, SC-001–SC-010, and the
  management, CLI, and UI contracts are covered by contract, unit, integration,
  security, smoke, and browser tests added for this feature.
- Dependency-failure and recovery behavior covered: SMTP delivery failure leaves
  no exposed reset secret, reset requests are digest-only and single-use, replay
  and expiry are denied generically, stale revisions are rejected, and interrupted
  CLI recovery is handled by reading current state before retry.
