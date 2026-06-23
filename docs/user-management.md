# User management

Bootstrap a new installation locally with `auth-portal bootstrap-admin`; the
initial password is requested twice through hidden input and is never accepted as
an argument. After sign-in, administrators manage users at `/admin/users`.

The page and CLI use group memberships as the only per-user access-list input.
User detail explains every service grant and all granting groups. Mutations use a
user revision: a conflict means another operator changed the user, so refresh,
review, and preview again.

CLI reads use `auth-portal users list|show`. Mutations include `create`, `update`,
`disable`, `reactivate`, `reset-password`, and `memberships add|remove|set`.
Provide `--actor-email`; the CLI prompts for the actor password. Mutations preview
unless `--apply` is present. `--format json` emits schema version 1.

Exit codes are 0 success/no-change, 2 invalid input, 3 denied, 4 not found, 5
conflict, and 6 dependency failure. Never pass passwords or reset secrets in
arguments or environment variables. Resolve an interrupted command with `users
show`; do not blindly repeat a stale mutation.

## Temporary passwords and recovery delivery

New user creation generates a one-time temporary password. The password is shown
only in the create response on the admin page or CLI output, is stored only as a
hash, and places the account in `temporary` credential state. The user can sign
in with that value only to reach `/change-password`; normal portal, service, and
admin access is blocked until the user chooses a new password.

Configure `AUTH_PORTAL_SMTP_HOST`, `AUTH_PORTAL_SMTP_PORT`, and
`AUTH_PORTAL_SMTP_SENDER`. Production delivery should enable STARTTLS and use
protected SMTP credentials where required. Password reset uses single-use links
over SMTP. If delivery fails, no reset secret is displayed; correct SMTP
configuration and send a new reset, which invalidates older links.

Disabling a user, completing a reset, or demoting an administrator revokes active
sessions. Memberships remain attached to disabled users but grant no currently
usable service. Self-disable, self-demotion, and changes that would remove the
last active administrator are rejected.

## Incident recovery

Use audit events to correlate actor, target, operation, outcome, revision, and
changed field names. Audit context intentionally excludes passwords, hashes,
reset links/digests, sessions, cookies, and configuration secrets. Retain evidence
for at least 90 days. If an operation is interrupted, read the current revision
before deciding whether a new preview is necessary.
