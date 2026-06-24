# Contract: Group Management UI

This contract defines user-visible behavior for the group management page and related forms. It is intentionally technology-neutral and describes page responsibilities, accepted inputs, and expected outcomes.

## Authorization Boundary

- Only authenticated active SRE/Admin operators can access group management.
- Unauthorized requests to any group management page or action must receive a denial outcome without group names, dependency counts, service relationships, or user membership data.
- Authorization must be checked when the page is rendered and again when previewing or confirming any mutation.

## Group List Page

### Purpose

Allow an operator to find groups and understand high-level usage before opening a group detail view.

### Required Display

- Page title identifying group management.
- Search and filter controls for name, status, user usage, and service usage.
- For each group in the bounded result set:
  - Name.
  - Description or purpose when present.
  - Status.
  - Assigned user count.
  - Associated service count.
  - Most recent management outcome or last changed time when available.
  - Link or action to open the group detail view.
- Empty state when no groups match.
- Create-group form.

### Create Group Form

Inputs:

- `name`: Required group name.
- `description`: Optional group purpose.
- `csrf`: Required form protection value.

Outcomes:

- Valid create: group exists, success message shown, group appears in list.
- Invalid name: field-level error near name, safe entered values preserved.
- Duplicate or ambiguous name: field-level error near name, no new group.
- Expired form: form-level retry message, no group change.
- Unauthorized actor: denied outcome, no group data leak.

## Group Detail Page

### Purpose

Show group metadata, dependencies, lifecycle state, and available safe actions.

### Required Display

- Group name, description, status, revision/currentness indicator, created and updated metadata when available.
- Assigned user count with bounded visible user list or linkable summary.
- Associated service count with bounded visible service list or linkable summary.
- Current access impact summary.
- Recent non-sensitive group audit outcomes.
- Edit metadata form.
- Deactivate/reactivate preview form.
- Permanent removal form only when removal is eligible, or a blocked-removal explanation when dependencies exist.

### Edit Metadata Form

Inputs:

- `expected_revision`: Required current group revision.
- `name`: Required group name.
- `description`: Optional group purpose.
- `csrf`: Required form protection value.

Outcomes:

- Valid preview: shows changed fields and confirms existing dependencies remain attached.
- Valid confirm: metadata changes are saved, existing user/service relationships remain attached.
- Invalid or duplicate name: field-level error, safe values preserved.
- Stale revision: conflict message instructing refresh, no state change.
- Unauthorized actor: denied outcome, no state change.

## Lifecycle Actions

### Deactivate Group

Inputs:

- `expected_revision`: Required current group revision.
- `confirm`: Indicates preview or confirmation.
- `csrf`: Required form protection value.

Outcomes:

- Preview: shows affected user and service counts plus bounded dependency details.
- Confirm: group status becomes deactivated, group no longer grants current service access, relationships are preserved.
- No-change: already deactivated groups report no unsafe mutation.
- Stale revision: conflict message, no state change.
- Last-administrator risk: denied with safe explanation, no state change.

### Reactivate Group

Inputs:

- `expected_revision`: Required current group revision.
- `confirm`: Indicates preview or confirmation.
- `csrf`: Required form protection value.

Outcomes:

- Preview: shows associated users/services that may regain usable access.
- Confirm: group status becomes active and can again participate in access decisions.
- No-change: already active groups report no unsafe mutation.
- Stale revision: conflict message, no state change.

### Permanent Removal

Inputs:

- `expected_revision`: Required current group revision.
- `confirm`: Indicates preview or confirmation.
- `csrf`: Required form protection value.

Outcomes:

- Eligible preview: states that the group has no current user memberships or service associations.
- Eligible confirm: group is removed from active management views and audit evidence remains.
- Dependency-blocked: shows user/service dependency counts or bounded dependency summary, no removal.
- Stale revision: conflict message, no state change.
- Last-administrator risk: denied with safe explanation, no state change.

## Audit Contract

Group management must emit non-sensitive evidence for:

- Group created.
- Group metadata updated.
- Group deactivated.
- Group reactivated.
- Group removed.
- Mutation denied.
- Mutation rejected due to stale revision.
- Mutation blocked by dependencies.
- Invalid input where operationally relevant.

Audit evidence must include actor, target group when available, operation, outcome, reason category, timestamp, and changed field names or dependency counts. It must not include credentials, session identifiers, recovery secrets, tokens, password hashes, or unnecessary personal data.

## Cross-Page Consistency

- User management must reflect group status and availability on the next fresh read.
- Service management must reject references to removed or unavailable groups and reflect status where useful.
- Effective access views must not treat deactivated groups as granting current service access.
