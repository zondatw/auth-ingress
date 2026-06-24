# Contract: Management Form State Recovery

## Scope

This contract defines expected user-visible behavior for administrative management forms after failed submissions. It applies to service management, user creation, user profile updates, memberships, status changes, delete confirmations, and password-reset confirmation flows.

## General Response Contract

When a management form submission fails validation:

- Response status is appropriate to the outcome:
  - `400` for invalid input or expired form.
  - `403` for denied management action.
  - `404` for missing target record.
  - `409` for stale revision or conflict.
  - `429` for rate-limited management action.
  - `503` for dependency failure.
- The returned page identifies the error outcome.
- All eligible non-sensitive submitted values remain visible in their original controls.
- Sensitive submitted values are not visible in the returned HTML.
- Field-specific errors are rendered near the affected fields when the error maps to a field.
- Form-level errors are rendered when the error is not field-specific.
- Existing preview/confirm semantics remain intact.

## Service Management Form Contract

Applies to:

- `POST /admin/services`
- `POST /admin/services/{service_slug}`
- `POST /admin/services/{service_slug}/compatibility`

For invalid service submissions:

- Preserve safe submitted values for `slug`, `display_name`, `description`, `destination`, `status`, `group_names`, `proxy_enabled`, and `websocket_enabled`.
- Preserve existing service list and available groups on the returned page.
- Keep selected/entered groups visible even if a different field fails validation.
- If a submitted group does not exist, show a group-specific or form-level missing-group error without clearing other fields.
- If the edited service no longer exists, return the existing not-found outcome and do not expose unrelated submitted data.

## User Creation Form Contract

Applies to:

- `POST /admin/users/preview`
- `POST /admin/users/confirm`

For invalid user creation submissions:

- Preserve safe submitted values for `email`, `display_name`, `status`, `is_admin`, and selected `group_ids`.
- Keep the user list, filter controls, and available groups visible on the returned page.
- Do not display generated temporary passwords unless the user was successfully created.
- If selected groups are invalid or missing, show an actionable error and keep the remaining safe values.

## User Detail Form Contract

Applies to:

- `POST /admin/users/{user_id}/profile`
- `POST /admin/users/{user_id}/memberships`
- `POST /admin/users/{user_id}/status`
- `POST /admin/users/{user_id}/delete`
- `POST /admin/users/{user_id}/reset-password`

For invalid user detail submissions:

- Preserve safe submitted values for the active form being corrected.
- Preserve selected memberships when membership validation fails.
- Preserve profile fields when profile validation fails.
- Preserve selected status when status validation fails.
- Keep sensitive reset or password-related values blank.
- Conflict, denied, and not-found outcomes remain distinct from validation errors.

## Security Contract

- Returned HTML for failed submissions must not contain credentials, temporary passwords, tokens, recovery secrets, session identifiers, or raw CSRF secrets beyond the normal protected form token behavior.
- Audit and diagnostic messages must record outcome categories without storing sensitive submitted values.
- Authorization is checked before any management mutation is applied.

## Regression Contract

The following regressions must be prevented:

- A single invalid field clears all other fields.
- Multi-select groups are lost after another field fails.
- A sensitive value is echoed back after validation failure.
- A conflict or denied action is shown as a normal editable validation error.
- Correcting one invalid field causes duplicate records or repeated destructive actions.
