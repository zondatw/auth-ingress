# Quickstart: Group Management Page

## Prerequisites

- Dependencies installed with `uv sync --locked --extra test`.
- Test database fixtures include an administrator, users, groups, services, memberships, and service access rules.
- Current feature pointer is `specs/008-group-management`.

## Focused Validation Commands

Run the planned focused suites after implementation:

```bash
uv run pytest tests/unit/test_group_admin_service.py -q
uv run pytest tests/contract/test_admin_groups_contract.py -q
uv run pytest tests/integration/test_admin_groups.py -q
uv run pytest tests/security/test_group_management_security.py -q
uv run pytest tests/e2e/test_admin_groups.py -q
```

Run broader regression coverage before merge:

```bash
uv run pytest tests/contract/test_admin_users_contract.py tests/contract/test_admin_contract.py -q
uv run pytest tests/integration/test_user_memberships.py tests/integration/test_admin_services.py -q
uv run pytest tests/security/test_user_management_authorization.py tests/security/test_admin_boundary.py -q
uv run pytest -q
```

## Manual Validation Scenarios

### View group dependencies

1. Sign in as an administrator.
2. Open the group management page.
3. Search for an existing group such as a staff or admin group.
4. Open the group detail page.
5. Expected outcome:
   - Group metadata is visible.
   - Assigned user count and associated service count are visible.
   - Bounded user/service dependency details are visible.
   - No credentials, session identifiers, tokens, or recovery values appear.

### Create and edit a group

1. Open group management as an administrator.
2. Create a group with a unique name and description.
3. Attempt to create another group with the same name using different case or surrounding whitespace.
4. Edit the original group's description.
5. Expected outcome:
   - Valid create succeeds.
   - Duplicate create is rejected with a field-level error and safe values preserved.
   - Edit succeeds without changing existing memberships or service associations.

### Handle stale edit

1. Open the same group detail page in two browser tabs.
2. Save a metadata change in the first tab.
3. Attempt a different metadata change from the second tab.
4. Expected outcome:
   - The second submission is rejected as stale.
   - No newer group state is overwritten.
   - The page asks the operator to refresh.

### Deactivate and reactivate a group

1. Open a group that has at least one user and one associated service.
2. Preview deactivation.
3. Confirm deactivation.
4. Verify effective access no longer treats that group as currently granting access.
5. Preview and confirm reactivation.
6. Expected outcome:
   - Preview shows affected users and services.
   - Deactivation preserves relationships and history.
   - Reactivation restores the group to access evaluation.

### Block unsafe removal

1. Open a group with current users or service rules.
2. Attempt permanent removal.
3. Expected outcome:
   - Removal is blocked.
   - Dependency counts or bounded details explain what must be cleared.
   - No memberships or service associations are deleted.

### Remove unused group

1. Create a group with no users and no service associations.
2. Preview permanent removal.
3. Confirm permanent removal.
4. Expected outcome:
   - Group is removed from active management views.
   - Audit evidence remains available.
   - Related user and service management pages do not show dangling references.

### Authorization and sensitive-output checks

1. Sign in as a non-admin user and attempt to open group management.
2. Submit group management actions after losing admin authority or with an expired form.
3. Inspect page output and audit evidence.
4. Expected outcome:
   - Unauthorized access is denied without group relationship data.
   - Expired/stale submissions make no state change.
   - No secrets or unnecessary personal data are exposed.

## Expected Completion Signal

The feature is ready when focused unit, contract, integration, security, and e2e tests pass; full regression tests pass; and manual validation confirms group dependency visibility, safe lifecycle controls, authorization boundaries, and non-sensitive audit evidence.
