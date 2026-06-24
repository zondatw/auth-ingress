# Data Model: Group Management Page

## Group

Represents an access-control collection used by user memberships and service access rules.

### Fields

- `id`: Stable internal identifier.
- `name`: Unique operator-facing group name.
- `normalized_name`: Canonical name used for uniqueness checks.
- `description`: Optional purpose or human-readable notes.
- `status`: `active` or `deactivated`.
- `revision`: Monotonic version used to detect stale management forms.
- `created_at`: Creation timestamp.
- `updated_at`: Last metadata or lifecycle change timestamp.

### Validation Rules

- Name is required.
- Normalized name is unique across all current groups.
- Name normalization trims surrounding whitespace and compares case-insensitively.
- Status must be `active` or `deactivated`.
- Description is optional and bounded to a safe display length.
- Mutations must include the expected revision and fail on mismatch.

### State Transitions

```text
active ──deactivate──▶ deactivated
deactivated ──reactivate──▶ active
active/deactivated ──remove when unused──▶ removed from active management views
```

Removal is allowed only when the group has no current user memberships and no current service associations.

## Group Dependency

Represents current relationships that make a group operationally significant.

### Fields

- `group_id`: Group being inspected.
- `assigned_user_count`: Number of users currently assigned to the group.
- `associated_service_count`: Number of services currently using the group for access.
- `sample_users`: Bounded list of assigned users for detail display.
- `sample_services`: Bounded list of associated services for detail display.
- `has_more_users`: Whether additional assigned users exist beyond the displayed list.
- `has_more_services`: Whether additional services exist beyond the displayed list.

### Validation Rules

- Dependency information is visible only to authorized management operators.
- Permanent removal requires both counts to be zero at confirmation time.
- Deactivation preview and detail views must show dependency impact without unbounded output.

## Group Management Operation

Represents a requested group create, update, deactivate, reactivate, or remove action.

### Fields

- `operation`: One of `group_create`, `group_update`, `group_deactivate`, `group_reactivate`, `group_remove`.
- `actor_user_id`: Authorized operator requesting the action.
- `target_group_id`: Target group when one exists.
- `expected_revision`: Revision submitted by the operator for existing groups.
- `changes`: Non-sensitive changed fields or lifecycle action.
- `dependency_summary`: Counts and reason category for dependency-blocked operations.
- `outcome`: `success`, `preview`, `invalid_input`, `conflict`, `denied`, `dependency_blocked`, or `no_change`.
- `message`: Safe operator-facing summary.

### Validation Rules

- Authorization is checked at execution time.
- Preview must not mutate state.
- Confirmed mutation is atomic.
- Stale revisions produce conflict outcomes.
- Last-active-administrator-risk outcomes are denied and make no change.
- Field-level validation errors preserve safe submitted values.

## Effective Access Impact

Derived view explaining how a group status affects user ability to access services.

### Fields

- `group_id`: Group being evaluated.
- `affected_users`: Bounded list or count of users whose access may change.
- `affected_services`: Bounded list or count of services associated with the group.
- `currently_grants_access`: Whether the group is active and can grant access.
- `impact_summary`: Safe explanation displayed during lifecycle preview.

### Validation Rules

- Deactivated groups do not grant current access.
- Existing memberships and service associations remain visible after deactivation.
- Effective access calculations must agree with portal authorization behavior.

## Audit Event

Non-sensitive evidence of group management activity.

### Fields

- `event_type`: Group management event category.
- `outcome`: Success, denied, conflict, invalid input, dependency blocked, or no-change.
- `actor_user_id`: Acting operator.
- `target_group_id`: Group affected when available.
- `reason`: Safe reason category.
- `change_summary`: Changed field names, lifecycle action, and dependency counts where appropriate.
- `created_at`: Event timestamp.

### Validation Rules

- No credentials, session identifiers, tokens, password hashes, recovery secrets, or unnecessary personal data.
- Denied, stale, dependency-blocked, and successful mutations are auditable.
- Audit retention follows existing administrative audit policy.
