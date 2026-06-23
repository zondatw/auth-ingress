# Contract: User-Management CLI

Executable: `auth-portal`

The CLI is a thin adapter to the shared management operations. Except for local
bootstrap, every command requires an active administrator identity and verifies
that identity with a hidden password prompt. Passwords and reset secrets are not
accepted as command arguments, environment variables, or JSON fields.

## Global User-Management Options

- `--actor-email EMAIL`: Required for authenticated `users` commands.
- `--format table|json`: Output format; default `table` for a terminal.
- `--database-url URL`: Not exposed as a command option; deployment configuration
  selects the database using the application's existing configuration mechanism.

Interactive authentication failure returns `denied` without confirming whether
the actor email exists. The CLI never echoes the entered password.

## First-Install Bootstrap

```text
auth-portal bootstrap-admin --email EMAIL --display-name NAME
```

Behavior:

- Initializes schema and serialized installation state.
- Prompts twice for the initial password using hidden terminal input.
- Rejects non-interactive input rather than accepting a visible secret channel.
- Creates exactly one active admin only on an empty installation.
- Returns success exit `0`, invalid input `2`, already initialized `3`, conflict
  `5`, or dependency failure `6`.
- Repeated or concurrent execution never creates another user or modifies the
  existing administrator.

No `--password`, password environment variable, printed default, or JSON secret
field exists.

## Read Commands

```text
auth-portal users list --actor-email EMAIL [--query TEXT]
    [--status active|disabled] [--admin true|false] [--group GROUP]
    [--page NUMBER] [--format table|json]

auth-portal users show USER_ID --actor-email EMAIL [--format table|json]
```

`list` returns a bounded stable page and pagination metadata. `show` returns safe
profile fields, revision, memberships, and effective service access with all
granting groups. Credential, reset, and session data are excluded.

## Create and Update

```text
auth-portal users create --actor-email EMAIL --email USER_EMAIL
    --display-name NAME [--status active|disabled] [--admin]
    [--group GROUP ...] [--apply] [--format table|json]

auth-portal users update USER_ID --actor-email EMAIL
    --expected-revision NUMBER [--email USER_EMAIL] [--display-name NAME]
    [--admin true|false] [--apply] [--format table|json]
```

Without `--apply`, mutating commands preview only. Create preview validates all
fields and groups. Applied create stores no operator-supplied password; the user
starts in `setup_required` credential state and receives a one-time setup link
through the configured recovery channel.

## Status and Credential Commands

```text
auth-portal users disable USER_ID --actor-email EMAIL
    --expected-revision NUMBER [--apply] [--format table|json]

auth-portal users reactivate USER_ID --actor-email EMAIL
    --expected-revision NUMBER [--apply] [--format table|json]

auth-portal users reset-password USER_ID --actor-email EMAIL
    --expected-revision NUMBER [--apply] [--format table|json]
```

Disable and admin demotion revoke target sessions and enforce self/last-admin
protection. Reset initiation sends a new single-use link and never returns the
link or token.

## Membership Commands

```text
auth-portal users memberships add USER_ID GROUP [GROUP ...]
    --actor-email EMAIL --expected-revision NUMBER [--apply]
    [--format table|json]

auth-portal users memberships remove USER_ID GROUP [GROUP ...]
    --actor-email EMAIL --expected-revision NUMBER [--apply]
    [--format table|json]

auth-portal users memberships set USER_ID [GROUP ...]
    --actor-email EMAIL --expected-revision NUMBER [--apply]
    [--format table|json]
```

Groups accept stable IDs or exact names. Preview returns added/removed groups and
effective-access differences. Repeating a satisfied operation returns
`no_change`, exit `0`.

## JSON Output

Every JSON response is one object:

```json
{
  "schema_version": 1,
  "operation": "membership_add",
  "outcome": "success",
  "target_user_id": 42,
  "revision": 8,
  "changes": {
    "groups_added": [{"id": 3, "name": "staff"}],
    "groups_removed": []
  },
  "effective_access_changes": []
}
```

Keys not applicable to an operation are omitted. Output never includes email for
denied/unknown actors, password data, reset secret/digest, session identifier,
cookie, token, traceback, SQL, or configuration secret.

## Exit Codes

| Exit | Outcome |
|------|---------|
| 0 | `success` or `no_change` |
| 2 | `invalid_input` |
| 3 | `denied` or already initialized bootstrap |
| 4 | `not_found` for an authorized actor |
| 5 | `conflict` |
| 6 | `dependency_failure` |

An interrupted command either commits the complete transaction and reports the
new revision on the next read, or commits nothing. Operators resolve ambiguous
interruptions by running `users show`; they do not blindly repeat with a stale
revision.
