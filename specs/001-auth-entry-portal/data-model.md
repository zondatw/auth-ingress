# Data Model: Auth Entry Portal

## User

Represents a person who can sign in to the portal and request access to protected
services.

**Fields**:

- `id`: Stable unique identifier.
- `email`: Unique sign-in identifier.
- `display_name`: Human-readable name shown in admin/audit contexts.
- `password_hash`: Protected password verifier; never logged or displayed.
- `status`: `active`, `disabled`.
- `is_admin`: Whether the user may manage service entries and review audit data.
- `created_at`: Creation timestamp.
- `updated_at`: Last update timestamp.

**Relationships**:

- Belongs to zero or more groups through `GroupMembership`.
- Owns zero or more active sessions.
- May appear as actor on audit events.

**Validation Rules**:

- Email must be unique and normalized for comparison.
- Disabled users cannot sign in or enter services.
- Password hash must never be returned in UI, contracts, logs, or audit payloads.

## Group

Represents an administrator-managed access grouping.

**Fields**:

- `id`: Stable unique identifier.
- `name`: Unique group name.
- `description`: Optional administrator-facing description.
- `created_at`: Creation timestamp.
- `updated_at`: Last update timestamp.

**Relationships**:

- Has many users through `GroupMembership`.
- May be referenced by access rules.

**Validation Rules**:

- Name must be non-empty and unique.

## GroupMembership

Connects users to groups for access decisions.

**Fields**:

- `user_id`: User reference.
- `group_id`: Group reference.
- `created_at`: Membership creation timestamp.

**Relationships**:

- Belongs to one user.
- Belongs to one group.

**Validation Rules**:

- A user can appear in the same group only once.
- Disabled users may remain in groups but cannot use memberships for service
  entry.

## ServiceEntry

Represents a downstream service protected by the portal.

**Fields**:

- `id`: Stable unique identifier.
- `slug`: Unique URL-safe service identifier.
- `display_name`: Name shown to users.
- `description`: Optional user-facing description.
- `destination`: Internal downstream destination or launch target.
- `status`: `enabled`, `disabled`.
- `created_at`: Creation timestamp.
- `updated_at`: Last update timestamp.

**Relationships**:

- Has one or more access rules.
- Appears on service-entry and denied-access audit events.

**Validation Rules**:

- Slug must be unique, stable, and URL-safe.
- Disabled service entries cannot accept new user entry attempts.
- Destination must not contain credentials or embedded secrets.

**State Transitions**:

- `enabled -> disabled`: Prevent new access attempts; existing forwarded
  requests must be rechecked before each entry decision.
- `disabled -> enabled`: Allow access only after access rules are valid.

## AccessRule

Defines who may enter a service.

**Fields**:

- `id`: Stable unique identifier.
- `service_entry_id`: Service entry reference.
- `rule_type`: `group`.
- `group_id`: Group reference for group-based rules.
- `created_at`: Creation timestamp.
- `updated_at`: Last update timestamp.

**Relationships**:

- Belongs to one service entry.
- References one group.

**Validation Rules**:

- Each enabled service entry must have at least one access rule.
- Version 1 supports group-based rules only.
- Rules referencing missing groups are invalid and must not grant access.

## Session

Represents the user's current authenticated portal state.

**Fields**:

- `id`: Stable unique identifier.
- `user_id`: User reference.
- `created_at`: Creation timestamp.
- `expires_at`: Expiry timestamp.
- `revoked_at`: Revocation timestamp, if signed out or invalidated.
- `last_seen_at`: Last successful portal interaction timestamp.

**Relationships**:

- Belongs to one user.

**Validation Rules**:

- Expired or revoked sessions cannot authorize service entry.
- Session identifiers must be stored and transmitted only through protected
  mechanisms and must never be logged.

**State Transitions**:

- `active -> expired`: Time-based expiry.
- `active -> revoked`: User sign-out or administrator invalidation.

## AuditEvent

Non-sensitive record of a security-relevant action or decision.

**Fields**:

- `id`: Stable unique identifier.
- `event_type`: `sign_in_success`, `sign_in_failure`, `sign_out`,
  `service_entry_allowed`, `service_entry_denied`, `service_entry_created`,
  `service_entry_updated`, `service_entry_disabled`.
- `actor_user_id`: Optional user reference when known.
- `service_entry_id`: Optional service entry reference.
- `decision`: `allowed`, `denied`, `changed`, `informational`.
- `reason`: Short non-sensitive reason code.
- `request_context`: Minimal non-sensitive context such as correlation id and
  client category.
- `created_at`: Event timestamp.

**Relationships**:

- May reference a user.
- May reference a service entry.

**Validation Rules**:

- Must not store passwords, session identifiers, secrets, or unnecessary personal
  data.
- Sign-in failures for unknown users may store only normalized, non-sensitive
  identifiers needed for abuse prevention and audit review.
- Records are retained for at least 90 days unless stricter policy is added.
