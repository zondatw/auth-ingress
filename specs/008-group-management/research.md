# Research: Group Management Page

## Decision: Extend existing group records with lifecycle metadata

**Rationale**: The current system already has group records, user memberships, and service access rules. Adding status and revision metadata to the existing group concept supports deactivation, stale-write protection, and lifecycle audit evidence without introducing a second access-control model.

**Alternatives considered**:

- Separate "group lifecycle" table: rejected because it would split one operator concept across two persisted records and increase review complexity.
- Soft-delete-only groups: rejected because the specification needs reversible deactivation and dependency visibility before permanent removal.

## Decision: Deactivation stops a group from granting future access while preserving relationships

**Rationale**: Operators need a reversible incident-response and cleanup path. Keeping memberships and service associations intact makes the access impact visible and allows reactivation without reconstructing relationships. Access evaluation must ignore deactivated groups when determining currently usable service access.

**Alternatives considered**:

- Remove all memberships or access rules during deactivation: rejected because it destroys context and makes recovery error-prone.
- Make deactivation visual-only: rejected because it would not satisfy the requirement that deactivated groups stop granting access.

## Decision: Permanent removal is allowed only for unused groups

**Rationale**: Removing groups with active users or service rules can silently change access for many people. Requiring zero current dependencies keeps removal simple, auditable, and recoverable through explicit cleanup steps in existing user/service management flows.

**Alternatives considered**:

- Cascade delete memberships and access rules: rejected because it can cause broad accidental access changes.
- Provide bulk dependency cleanup inside group management: rejected for initial scope because it expands the feature into a bulk access-editing workflow.

## Decision: Use revision checks for stale group mutations

**Rationale**: Existing user management already uses revision-based conflict handling. Applying the same pattern to groups prevents two operators from silently overwriting each other's changes and gives a clear refresh path.

**Alternatives considered**:

- Last-write-wins updates: rejected because stale group lifecycle changes can affect access boundaries.
- Global management lock: rejected because it reduces operator availability and is unnecessary for the expected scale.

## Decision: Use the existing admin-only authorization boundary

**Rationale**: The current project treats SRE/Admin as the initial management personas and enforces admin access on user and service management. Group management should use the same boundary so operators see a consistent model and so no new privilege system is introduced.

**Alternatives considered**:

- New group-owner role: rejected as out of scope for the initial feature and likely to require a broader delegation model.
- Read-only group visibility for non-admin users: rejected because group relationships reveal access-control data.

## Decision: Reuse request-scoped management form state for validation recovery

**Rationale**: The previous form-preservation feature already introduced safe value preservation, field-level errors, and sensitive-field exclusion. Reusing it keeps group forms consistent with user and service management and addresses validation UX requirements without a new mechanism.

**Alternatives considered**:

- Client-side-only validation recovery: rejected because server-side validation remains the authority and must handle stale/dependency/authorization outcomes.
- Store failed form submissions: rejected because failed form state is request-scoped and should not persist access-control data unnecessarily.

## Decision: Audit every group lifecycle mutation and important denied outcome

**Rationale**: Group changes directly affect service access. Incident response needs actor, target group, operation, outcome, reason category, and changed field names without secret or unnecessary personal data.

**Alternatives considered**:

- Audit only successful mutations: rejected because denied, stale, and dependency-blocked attempts are operationally relevant.
- Include full dependency lists in audit payloads: rejected because large relationship snapshots can expose unnecessary access data; page output can show bounded details to authorized operators.
