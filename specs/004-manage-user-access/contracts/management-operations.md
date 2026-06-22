# Contract: Shared User-Management Operations

This contract defines behavior shared by web and CLI adapters. Adapters may
format results differently but may not bypass these rules.

## Authorization

- Reads and mutations require a currently active `is_admin=true` actor.
- Authorization is re-evaluated inside every operation; prior page load, preview,
  or CLI authentication is not sufficient after actor state changes.
- Bootstrap is the only unauthenticated operation and is callable only from the
  local CLI while installation state and user count both prove a clean install.
- Unauthorized reads do not disclose whether a target user exists.

## Identity Lookup and Search

Search inputs:

- `query`: Optional bounded email/display-name query.
- `status`: Optional `active` or `disabled` filter.
- `is_admin`: Optional boolean filter.
- `group`: Optional exact group identifier/name filter.
- `page`: Positive page number; page size is bounded by the application.

Search results contain ID, email, display name, status, admin flag, revision,
group names, and timestamps. They never contain password hashes, reset state,
session data, or secrets. Stable ordering uses normalized email then user ID.

## User Detail

The detail result contains the safe user fields, all memberships, all available
groups, and effective-access results with every granting group. Disabled users
show retained policy separately from `currently_usable=false`.

## Preview and Commit

Existing-user mutations require `expected_revision`. A preview:

1. authenticates the actor;
2. loads current target and referenced groups;
3. validates normalized identity, requested status/privilege, and lockout rules;
4. computes changes and effective access;
5. returns `no_change` or the proposed result without writing state.

A commit repeats all five steps in a transaction, compares the expected
revision, applies the full change, increments the target revision once, revokes
sessions when required, creates the audit event without a nested commit, and
commits once. Any error rolls back the complete operation.

## Outcome Codes

| Code | Meaning | State change | Web mapping | CLI exit |
|------|---------|--------------|-------------|----------|
| `success` | Requested operation committed | Complete | 200/201 | 0 |
| `no_change` | Desired state already exists | None | 200 | 0 |
| `invalid_input` | Input or reference is invalid | None | 400 | 2 |
| `denied` | Actor unauthorized or lockout safeguard triggered | None | 403 | 3 |
| `not_found` | Authorized actor requested missing target | None | 404 | 4 |
| `conflict` | Expected revision or preview dependencies are stale | None | 409 | 5 |
| `dependency_failure` | Recovery delivery or storage dependency failed | None | 503 | 6 |

Human messages are safe and actionable. Machine output uses the stable code,
operation, target ID when authorized, revision, changed field names, group
identifiers, and effective-access summary. It excludes traceback, SQL, paths,
configuration secrets, credentials, reset tokens, and session identifiers.

## Membership Changes

- Input is a complete desired group-ID set or explicit add/remove group IDs.
- Duplicate IDs collapse to one membership.
- Missing groups reject the entire operation.
- Removal preserves access granted by other groups.
- Preview reports added/removed groups and services whose explanation or usable
  state would change.
- Commit increments user revision once regardless of membership count.

## User Lifecycle

- Create requires normalized unique email, display name, initial status/admin
  flag, and valid groups. It creates `setup_required` credential state and sends
  a single-use setup link through the recovery adapter; no credential is shown to
  the operator. Creation and memberships commit atomically. Delivery then uses
  the reset-request lifecycle; a delivery failure invalidates that request and
  leaves the intentionally non-sign-in-capable account available for safe setup
  retry rather than representing a partially created identity.
- Disable preserves memberships and revokes all sessions.
- Reactivate restores usability according to current memberships.
- Admin demotion revokes sessions and is rejected for self or last active admin.
- Hard deletion is unavailable.

## Credential Reset

- Initiation invalidates older requests, creates a digest-only request, and sends
  the raw secret through the configured recovery adapter.
- Delivery failure invalidates the new request and returns
  `dependency_failure`; no token appears in output.
- Reset completion accepts a valid raw secret only at the recovery form, replaces
  the password verifier, consumes the request, increments revision, and revokes
  sessions atomically.
- Malformed, expired, consumed, superseded, and invalid secrets receive the same
  safe invalid/expired response.

## Audit Requirements

Mutations and security-significant denials create an event containing actor,
target when known, operation, timestamp, outcome, reason code, revision, changed
field names, group IDs, correlation ID, and client category. No event contains
field values for passwords, password hashes, reset secrets/digests, sessions,
cookies, or tokens.
