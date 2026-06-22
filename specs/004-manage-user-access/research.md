# Research: Manage User Access

## One-Time Bootstrap Serialization

**Decision**: Create a singleton installation-state record during schema setup
and lock/update it in the same transaction that creates the first administrator.
The SQLite implementation begins a write transaction before testing the state;
the portable repository boundary can use row locking on databases that support
it. Bootstrap is allowed only when the state is `needs_bootstrap` and no user
exists, and commits the administrator plus `initialized` state atomically.

**Rationale**: Checking whether the user table is empty without serialization
allows two processes to create privileged users. A singleton state provides an
explicit first-run state and a lock target while retaining the empty-user check
as defense in depth.

**Alternatives considered**: Derive setup state only from user count (race-prone);
ship a default administrator (unacceptable credential exposure); expose a web
setup wizard (creates a remotely reachable bootstrap surface); use a filesystem
lock (not portable across deployment/storage boundaries).

## Bootstrap Secret Input

**Decision**: `auth-portal bootstrap-admin` accepts email and display name but
collects the password twice through hidden interactive input. It does not accept
a password argument, environment value, generated default, or normal stdin. The
initial version intentionally excludes unattended bootstrap.

**Rationale**: Hidden terminal input avoids process-list, shell-history, and
routine-output disclosure. Requiring confirmation reduces accidental lockout
without creating a second secret channel.

**Alternatives considered**: Command argument (visible in history/processes);
environment variable (often exposed through process/debug tooling); generated
password printed once (still disclosed in terminal/log capture); password file
(adds ownership, permissions, deletion, and rotation requirements not needed for
the initial single-admin bootstrap).

## Operator Authorization Model

**Decision**: Reuse `User.is_admin` as application management authority. “SRE”
and “Admin” remain operator personas rather than separate application roles in
this release. Every CLI management command authenticates a named active admin
using a hidden password prompt, then invokes the same service authorization as
the web interface.

**Rationale**: The current portal has one administrative boundary. Introducing
role delegation solely to rename equivalent operators would add policy states
without changing allowed actions. Explicit CLI authentication produces an
accountable actor instead of trusting an arbitrary `--actor` value.

**Alternatives considered**: Add an SRE role with identical permissions
(unnecessary policy duplication); trust operating-system identity (not represented
in portal audit data); reuse browser cookies in the CLI (secret handling and
cross-interface coupling); add API tokens (new lifecycle and leakage boundary).

## Shared Management Service

**Decision**: Put lookup, preview, validation, mutation, effective-access
calculation, last-admin protection, session revocation, and audit creation in a
single service layer called by thin web and CLI adapters.

**Rationale**: Page/CLI parity is a security property. Duplicating mutation logic
would allow different validation, authorization, and audit behavior.

**Alternatives considered**: CLI calls the web application (requires network/API
authentication and adds a public interface); duplicate route/CLI logic (drift);
write database rows directly in CLI commands (bypasses safeguards).

## Stale Access-List Protection

**Decision**: Add a monotonically increasing `revision` to each user. Every
profile, privilege, status, credential-reset, or membership mutation compares an
expected revision and increments it atomically. Previews return that revision;
stale confirmations fail with `conflict` and current non-sensitive state.

**Rationale**: Membership rows do not have one timestamp representing the whole
access list. A user-level revision provides one cheap concurrency boundary for
all security-relevant user state and works on SQLite.

**Alternatives considered**: Last-write-wins (silent access loss); compare only
`updated_at` (timestamp precision and membership coverage issues); hold a database
lock between page preview and human confirmation (long transaction and poor
failure behavior).

## Effective Access Calculation

**Decision**: Derive effective access at read/preview time by joining active user
memberships to current group access rules and service state. Return all granting
groups for each service. Disabled users retain membership policy but receive a
separate `currently_usable=false` result.

**Rationale**: Derived results prevent a second grant store from becoming stale
and explain overlapping group grants correctly.

**Alternatives considered**: Persist per-user grants (violates scope and creates
dual truth); cache materialized results (invalidations add complexity at current
scale); show memberships without services (does not answer why access exists).

## Account Disable and Privilege Changes

**Decision**: Disabling a user, completing a password reset, or removing admin
authority revokes all of that user's active sessions in the same transaction.
Before disable/demotion, count other active admins and reject changes that would
leave none. Risky self-disable and self-demotion are rejected.

**Rationale**: Existing session validation already rejects disabled accounts, but
explicit revocation provides immediate evidence and covers privilege removal.
Last-admin protection preserves a recovery path.

**Alternatives considered**: Wait for session expiry (continued management
capability); allow self-demotion if another admin exists (unnecessary operator
error risk); require two-person approval (valuable at larger scale but beyond the
current portal's role model).

## Credential Reset Delivery

**Decision**: Store only a cryptographic digest of a random, single-use reset
secret with user, expiry, creation, and consumption state. Send the raw link only
through a configured SMTP recovery adapter. A newer request invalidates prior
active requests. Delivery failure invalidates the new request and reports a safe
dependency error. Successful reset changes the password, consumes the request,
increments user revision, and revokes sessions atomically.

On first opening the recovery URL, validate the secret generically, place it in a
short-lived signed, HttpOnly, Secure, SameSite=Strict reset-flow cookie, and
redirect immediately to a clean URL. The password form never contains the raw
secret, the reset page sends `Referrer-Policy: no-referrer`, and request logging
must omit query strings and reset cookies.

**Rationale**: The spec prohibits showing reset secrets in page/CLI output. SMTP
is a conventional external recovery channel and is available without a new
runtime package. Digest-only storage limits database disclosure.

**Alternatives considered**: Display a reset link to the operator (secret exposed
in UI/CLI); let the operator choose a password (not time-limited or single-use);
add a vendor email SDK (unnecessary dependency); background delivery queue
(unneeded operational complexity for current scale); keep the secret in the
rendered form or URL (leaks through history, referrers, screenshots, and logs).

## Audit Shape and Retention

**Decision**: Extend audit events with an optional target user and an allowlisted
change summary containing field names and non-secret identifiers only. Record
bootstrap, management reads where required, previews, changes, conflicts,
denials, reset delivery outcomes, and session revocation reason categories.
Retain the existing minimum 90-day configuration.

**Rationale**: Actor-only audit data cannot identify the managed user, while
placing target/change data in unrestricted context risks secret or personal-data
leakage.

**Alternatives considered**: Put full before/after values in JSON (excess data and
credential risk); use application logs only (retention and queryability are not
guaranteed); add a separate audit subsystem (unnecessary for this scale).

## Search and Result Bounding

**Decision**: Normalize email for exact identity matching, use case-insensitive
bounded search over email/display name, filter by status/admin/group, use stable
ID ordering as a tie-breaker, and cap each page. Add indexes for normalized email,
status, admin flag, and membership joins.

**Rationale**: Bounded deterministic results meet the 10,000-user target and keep
page and CLI output predictable without introducing a search service.

**Alternatives considered**: Load all users and filter in application memory
(unbounded); external search index (operationally excessive); offset-free opaque
cursors in the initial version (more contract complexity than needed at this
scale).
