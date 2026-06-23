# Contract: User-Management UI Flows

The UI remains server-rendered and uses the existing signed session, CSRF, secure
response headers, and no-store policy. All `/admin/users` routes require a current
active admin through the shared dependency and operation service.

## First-Install State

### `GET /sign-in`

- When installation state is `needs_bootstrap`, return a setup-required page.
- The page says that a trusted local operator must run
  `auth-ingress bootstrap-admin`; it contains no registration form, database path,
  environment value, stack trace, or host detail.
- Normal credential submission remains denied until state is `initialized`.
- After bootstrap, the standard sign-in form is available immediately.

There is no remote bootstrap endpoint.

## User List

### `GET /admin/users`

Accepted query fields: `q`, `status`, `admin`, `group`, and `page`.

The page shows bounded rows with email, display name, status, admin indicator,
group summary, revision, and detail link. It provides explicit empty and invalid
filter states. Search terms are never copied into logs or audit context.

Outcomes:

- `200`: Results or clear empty state.
- `401`: Authentication required, without user-list content.
- `403`: Administrator authority required, without user-list content.
- `400`: Invalid bounded filter/page request.

## User Detail and Access Explanation

### `GET /admin/users/{user_id}`

Shows safe profile fields, revision, account/credential status, memberships,
available groups, and effective services. Every service result lists all granting
groups and distinguishes retained policy from currently usable access.

An authorized missing target receives `404`; unauthorized callers receive the
standard denial before target lookup.

## Preview and Confirm

Mutation forms contain CSRF and `expected_revision`. The first submission is a
preview and does not mutate. It renders:

- changed field names;
- groups to add/remove;
- effective-access explanation changes;
- session-revocation effect where applicable;
- a confirm control carrying the same expected revision and requested values.

Confirmation calls the shared operation service, which recalculates and
revalidates inside the transaction. A stale revision returns `409` with current
safe state and requires a new preview. Invalid input returns `400`; authorization
or last-admin/self-operation denial returns `403`; dependency failure returns
`503`. No partial result is displayed as success.

## User Creation

### `POST /admin/users/preview`
### `POST /admin/users/confirm`

Fields: email, display name, active/disabled status, admin flag, selected group
IDs, CSRF, and confirmation marker. Creation never accepts a password. Confirmed
creation starts credential state at `setup_required` and attempts delivery of a
single-use setup link. If delivery fails, the non-sign-in-capable account remains
visible as a successfully created identity with a separate safe retry-setup
action and delivery warning; user fields and memberships were committed together.

## Existing User Changes

### `POST /admin/users/{user_id}/profile`
### `POST /admin/users/{user_id}/status`
### `POST /admin/users/{user_id}/memberships`
### `POST /admin/users/{user_id}/reset-password`

Every route implements the same preview/confirm contract. Profile handles email,
display name, and admin status. Status handles disable/reactivate. Memberships
submits the complete desired group-ID set. Reset initiation displays only whether
delivery succeeded; no reset link or token appears.

## Password Setup/Reset

### `GET /reset-password?token=...`
### `POST /reset-password`

The initial GET does not reveal whether a token maps to a user. It validates the
secret generically, stores the reset flow in a short-lived signed, HttpOnly,
Secure, SameSite=Strict cookie, and redirects immediately to the clean
`/reset-password` URL. The clean page sends `Referrer-Policy: no-referrer` and
contains no raw token. POST accepts new password, confirmation, and CSRF; it
obtains reset state only from the protected cookie. Valid completion consumes the
request, activates credential state, increments user revision, revokes existing
sessions, clears the reset cookie, and redirects to sign-in. Invalid, expired,
consumed, and superseded requests share one safe failure message and do not
identify the user.

The raw secret may appear only in the original recovery URL and transient reset
cookie. It is excluded from application and proxy logs, audit events, referrers,
HTML/form fields, and rendered follow-up pages. Query strings and reset cookies
are never logged.

## Navigation and Accessibility

- The existing admin navigation adds “Users” for admins only.
- Labels, error summaries, confirmation warnings, status changes, and empty
  states are keyboard accessible and understandable without color alone.
- Focus moves to the error summary after failed preview/confirm and to the success
  summary after commit.
- Destructive-looking actions use explicit verbs and name the target, but hard
  delete is never offered.
