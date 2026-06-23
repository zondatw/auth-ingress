# Data Model: Manage User Access

## InstallationState

Singleton record that makes first-install readiness explicit and serializes
creation of the first administrator.

**Fields**:

- `id`: Fixed singleton identifier.
- `state`: `needs_bootstrap` or `initialized`.
- `revision`: Monotonically increasing state revision.
- `initialized_at`: Timestamp of successful first-administrator creation.
- `updated_at`: Last state transition timestamp.

**Validation rules**:

- Exactly one row exists after schema initialization.
- `needs_bootstrap` is valid only when no user exists.
- `initialized` requires at least one active administrator.
- State and first-administrator creation commit in the same serialized
  transaction.
- No raw bootstrap credential or installer-supplied secret is stored.

**State transitions**:

- `absent -> needs_bootstrap`: Schema setup creates the singleton.
- `needs_bootstrap -> initialized`: Successful atomic first-admin creation.
- `initialized`: Terminal for normal operation; bootstrap cannot reset it.

## Managed User

Extends the existing user identity with normalized lookup, concurrency, and
credential lifecycle state.

**Fields**:

- `id`: Stable unique identifier.
- `email`: Canonical sign-in and recovery address shown to authorized operators.
- `normalized_email`: Trimmed, case-normalized unique identity key.
- `display_name`: Operator- and user-facing name.
- `password_hash`: Optional Argon2 password verifier; never returned or audited.
- `credential_status`: `setup_required` or `active`.
- `status`: `active` or `disabled`.
- `is_admin`: Whether the active user has SRE/Admin management authority.
- `revision`: Monotonically increasing value covering profile, status,
  privilege, password reset, and membership mutations.
- `created_at`: Creation timestamp.
- `updated_at`: Last mutation timestamp.

**Relationships**:

- Has zero or more `GroupMembership` records.
- Has zero or more `PortalSession` records.
- Has zero or more `PasswordResetRequest` records.
- May be actor or target on `AuditEvent` records.

**Validation rules**:

- `normalized_email` is non-empty, valid, unique, and derived from `email`.
- Display name is trimmed and within the existing 120-character limit.
- Status is one of the two allowed states.
- Password verifier is never emitted outside password verification.
- Authentication is denied while credential status is `setup_required` or the
  password verifier is absent.
- A mutation requires the expected current revision and increments it once.
- At least one user must remain both active and admin after every committed
  mutation.
- An operator cannot disable or demote their own account.

**State transitions**:

- `absent -> active`: Bootstrap or authorized creation.
- `absent -> setup_required`: Authorized creation sends a single-use setup link;
  memberships may be prepared but sign-in remains unavailable.
- `setup_required -> active`: Successful single-use password setup.
- `active -> disabled`: Revoke all sessions; memberships remain stored.
- `disabled -> active`: Retained memberships again determine usable access.
- `admin -> non-admin`: Allowed only for another user when another active admin
  remains; revoke the target's sessions.
- `password reset pending -> completed`: Replace verifier, consume request,
  increment revision, and revoke all sessions atomically.

## GroupMembership

Existing relationship connecting a user to a group. It remains the only
user-level input to protected-service access.

**Fields**:

- `id`: Stable unique identifier.
- `user_id`: Managed-user reference.
- `group_id`: Group reference.
- `created_at`: Membership creation timestamp.

**Validation rules**:

- The `(user_id, group_id)` pair is unique.
- A membership mutation participates in the target user's revision check and
  increment.
- Disabled users may retain membership policy but cannot currently use it.
- Missing group identifiers reject the whole mutation.

## EffectiveAccessResult

Read-only derived projection explaining service access; it is not persisted.

**Fields**:

- `service_id`, `service_slug`, `display_name`: Service identity.
- `service_status`: Current enabled/disabled state.
- `granting_groups`: Stable list of all current groups whose rules match the
  user's memberships.
- `policy_granted`: Whether any current group rule grants the service.
- `currently_usable`: Whether user and service status permit actual use.
- `denial_reason`: Safe reason such as `user_disabled`, `service_disabled`, or
  `no_matching_group` when not usable.

**Validation rules**:

- Results are recomputed from current memberships, rules, user status, and
  service status.
- Removing one granting group does not deny a service while another granting
  group remains.
- Direct per-user grants are never read or written.

## PasswordResetRequest

Single-use recovery request created by an authorized operator and delivered to
the managed user's configured address.

**Fields**:

- `id`: Stable unique identifier.
- `user_id`: Target user reference.
- `token_digest`: Cryptographic digest of the random reset secret.
- `expires_at`: Absolute expiration timestamp.
- `consumed_at`: Successful-use timestamp, if any.
- `invalidated_at`: Supersession or delivery-failure timestamp, if any.
- `requested_by_user_id`: Admin actor reference.
- `created_at`: Request timestamp.

**Validation rules**:

- Raw reset secrets are never persisted or audited.
- Only one unexpired, unconsumed, non-invalidated request per user is active.
- Creating a newer request invalidates every prior active request.
- Delivery failure invalidates the new request before returning failure.
- Expired, consumed, invalidated, or malformed secrets cannot reset a password.

**State transitions**:

- `absent -> active`: Authorized initiation and successful delivery.
- `active -> invalidated`: Newer request or delivery failure.
- `active -> expired`: Time passes beyond `expires_at`.
- `active -> consumed`: Successful password change; terminal.

## PortalSession

Existing authenticated session, with bulk revocation used by management changes.

**Relevant fields**: `id`, `user_id`, `created_at`, `expires_at`, `revoked_at`,
`last_seen_at`.

**Additional rules**:

- Disable, password reset, and admin demotion revoke all active sessions for the
  target in the same transaction as the user mutation.
- Session validation continues to reject disabled users and must re-read current
  admin authority for each management operation.
- Session identifiers never enter audit or CLI output.

## ManagementOperation

Ephemeral command object shared by page and CLI; not stored as a separate table.

**Fields**:

- `operation`: `create`, `update`, `disable`, `reactivate`, `reset`,
  `membership_add`, or `membership_remove`.
- `actor_user_id`: Authenticated active administrator.
- `target_user_id`: Existing target when applicable.
- `expected_revision`: Required for every existing-user mutation.
- `requested_fields`: Allowlisted requested field names and identifiers.
- `preview`: Whether state changes are prohibited.

**Outcome**:

- `code`: `success`, `no_change`, `invalid_input`, `conflict`, `denied`, or
  `dependency_failure`.
- `revision`: Current or newly committed target revision.
- `changes`: Safe field names plus group identifiers/names; never secret values.
- `effective_access`: Recomputed before/after summary where membership changes
  apply.

**Validation rules**:

- Preview and commit use the same validation/calculation path.
- Commit rechecks actor authorization, target revision, referenced groups, and
  last-admin safety inside the transaction.
- All requested changes and the audit event commit together or all roll back.

## AuditEvent

Extends existing audit evidence for user-management operations.

**Fields**:

- Existing: `id`, `event_type`, `actor_user_id`, `service_entry_id`, `decision`,
  `reason`, `request_context`, `created_at`.
- `target_user_id`: Optional managed-user target.
- `change_summary`: Allowlisted field names, group identifiers, counts, and
  revision numbers; never credentials or reset/session secrets.

**Event families**:

- `bootstrap_succeeded`, `bootstrap_rejected`, `bootstrap_failed`.
- `user_viewed`, `user_created`, `user_updated`, `user_disabled`,
  `user_reactivated`, `user_admin_changed`.
- `membership_changed`, `management_conflict`, `management_denied`.
- `password_reset_requested`, `password_reset_delivery_failed`,
  `password_reset_completed`.

**Validation rules**:

- Actor is required for authenticated management mutations; bootstrap has no
  portal actor and uses a local client category.
- Target is recorded when known.
- Context accepts only correlation ID and client category.
- Change summaries accept only explicitly allowlisted non-secret keys.
- Events are retained for at least 90 days.

## Schema Evolution

Schema upgrade logic must add and backfill `normalized_email` and `revision` for
existing users, create installation/reset tables, and extend audit events. The
upgrade normalizes existing identities and fails safely if normalization exposes
duplicates. Existing installations with users are marked `initialized`; a clean
installation remains `needs_bootstrap`.
