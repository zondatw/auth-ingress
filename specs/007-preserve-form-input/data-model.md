# Data Model: Preserve Management Form Input

## Overview

This feature does not introduce new durable database tables. It defines request-scoped form state and validation feedback that existing admin routes pass to templates after failed submissions.

## Entities

### Management Form State

Represents the safe values submitted by an administrator during a create or update attempt.

**Fields**:

- `form_name`: identifies the management form, such as service create, service edit, user create, profile edit, memberships, status change, delete confirmation, or password reset confirmation.
- `record_id`: optional identifier for the existing record being edited.
- `safe_values`: submitted values that may be redisplayed, such as display name, slug, description, destination URL, status, admin flag, selected group IDs, selected group names, enabled flags, and expected revision.
- `sensitive_fields`: submitted field names that must not be redisplayed, such as password, temporary password, token, secret, recovery value, and any future sensitive value.
- `selected_values`: normalized selections for multi-select, checkbox, radio, dropdown, and status controls.
- `form_errors`: page-level messages for non-field-specific failures.
- `field_errors`: field-specific validation messages keyed by field name.

**Validation rules**:

- Sensitive fields are excluded from `safe_values`.
- Values are normalized only enough to redisplay safely; business validation remains owned by existing management services.
- Unknown field names are ignored unless the route explicitly supports them.
- Existing record identity must be preserved for edit forms even when submitted values are invalid.

### Validation Error

Represents a user-correctable validation problem.

**Fields**:

- `field`: optional field associated with the error.
- `message`: plain-language correction guidance.
- `code`: stable outcome category for testing and audit correlation.
- `severity`: error or warning.

**Validation rules**:

- Field-specific errors must identify the affected field.
- Form-level errors must not pretend authorization, CSRF, stale revision, or dependency failures are ordinary input mistakes.
- Error messages must not include credentials, temporary passwords, tokens, recovery secrets, or unnecessary personal data.

### Sensitive Field Classification

Represents the classification used to decide whether a submitted value can be echoed back.

**Fields**:

- `field_name`: submitted form field name.
- `classification`: safe-to-redisplay or sensitive.
- `reason`: credential, temporary password, token, recovery value, session data, secret, or project-defined sensitive data.

**Validation rules**:

- Sensitive classification always wins over preservation.
- Future management forms must classify new secret-bearing fields before they can participate in preserved-input behavior.

### Referenced Management Record

Represents records selected or edited by the form.

**Fields**:

- `record_type`: user, group, service, access rule, or status-like management record.
- `record_id`: stable identifier when available.
- `display_label`: safe label for redisplay.
- `exists_at_submission`: whether the record was present when validating the submission.
- `authorized_for_actor`: whether the current administrator may act on the record.

**Validation rules**:

- Missing records produce a distinct not-found or stale-reference outcome.
- Unauthorized records produce a denial outcome and must not expose unauthorized record details.

## State Transitions

```text
blank or loaded form
  -> submit
  -> validation failed
  -> returned form with safe values + errors
  -> corrected submit
  -> success or another specific failure

loaded form
  -> submit
  -> authorization denied / stale record / CSRF expired
  -> distinct denial, conflict, or expired-form response

submit with sensitive values
  -> validation failed
  -> returned form with sensitive values blank
```

## Relationships

- Management Form State references zero or one existing management record for edit flows.
- Management Form State contains zero or more Validation Errors.
- Management Form State applies Sensitive Field Classification before values are sent to templates.
- Referenced Management Records inform selected-values preservation and stale-record errors.
