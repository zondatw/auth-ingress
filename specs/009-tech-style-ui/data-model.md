# Data Model: Tech Style UI Refresh

This feature does not introduce persistent application entities. The following
view-model entities describe rendered UI state and safe aggregate data.

## Visual System

Represents the shared product presentation.

**Fields**:

- `color_roles`: background, surface, elevated surface, text, muted text,
  accent, success, warning, danger, disabled, focus.
- `typography_roles`: product title, page title, section heading, body,
  helper text, status label, monospace/value text.
- `spacing_roles`: page shell, panel padding, grid gap, form gap, table cell
  spacing, compact chip spacing.
- `component_roles`: shell, navigation, panel, card, table, form, button,
  status chip, alert, notice, empty state, confirmation, secret display.

**Validation rules**:

- Every visible page must use shared roles rather than one-off legacy styling.
- Status and alert roles must not rely on color alone.
- Focus role must be visible against all interactive surfaces.

## Operational Summary

Represents safe aggregate context for portal/admin views.

**Fields**:

- `label`: short human-readable name.
- `value`: aggregate count or status text.
- `status`: neutral, success, warning, danger, disabled, or unavailable.
- `hint`: safe explanatory text.
- `target`: optional navigation target for authorized users.

**Validation rules**:

- Must be aggregate or already-visible contextual information.
- Must not include credentials, session identifiers, reset secrets, database
  details, or unnecessary personal data.
- Must render an unavailable/empty state when source data is absent.

## Page State

Represents a visible UI condition.

**Fields**:

- `state_type`: empty, success, validation_error, denied, destructive,
  disabled, unavailable, conflict, or informational.
- `title`: concise state title.
- `message`: safe explanatory copy.
- `next_action`: optional safe next action.
- `severity`: neutral, success, warning, or danger.

**Validation rules**:

- Error and denial states must provide safe recovery guidance.
- Destructive states must name the target and risk.
- State copy must not expose protected data.

## Navigation Surface

Represents the user-visible wayfinding shell.

**Fields**:

- `brand`: product identity.
- `current_user_context`: safe user display context.
- `allowed_destinations`: links allowed by authorization state.
- `current_section`: active section indicator.
- `session_action`: sign-out or related safe action.

**Validation rules**:

- Admin destinations are visible only to authorized administrators.
- Mobile navigation must preserve access to allowed destinations.
- Current user context must not include secrets or session identifiers.

## Security-Sensitive Interaction

Represents an interaction needing special clarity and redaction.

**Fields**:

- `interaction_type`: sign-in, password_change, temporary_password,
  destructive_action, access_change, denied, validation_error, audit_review.
- `primary_message`: visible guidance.
- `risk_summary`: concise risk or security implication.
- `confirmation_required`: boolean.
- `sensitive_values_visible`: allowed only where explicitly required, such as
  one-time temporary password display.

**Validation rules**:

- Temporary passwords may be visible only in the one-time creation/reset result
  flow already defined by the product.
- Hidden form protections may remain in markup where required, but visible UI
  and diagnostics must not reveal token values.
- Destructive/access-changing actions require clear confirmation affordance.
