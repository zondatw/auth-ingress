# Contract: Accessibility and Security

The visual refresh must improve perceived polish without weakening accessibility
or security clarity.

## Accessibility requirements

- Keyboard-only users can reach every interactive control.
- Focus indicators are visible on dark and elevated surfaces.
- Interactive controls have accessible names through visible labels or
  equivalent markup.
- Text, muted text, status chips, buttons, alerts, and form errors have usable
  contrast.
- Status is communicated with text and structure, not color alone.
- Tables remain usable through semantic headers and responsive containers.
- Copy controls report success/failure through visible and announced feedback.

## Security requirements

- Visible UI must not expose credentials, session identifiers, reset secrets,
  CSRF token values, database details, or unnecessary personal data.
- Temporary passwords remain visible only in the existing one-time result flow.
- Admin navigation and admin content remain authorized-only.
- Denied, stale, destructive, and dependency-blocked states provide safe
  messages without revealing protected relationships to unauthorized users.
- The refresh must not add analytics, external scripts, or hosted assets.

## Required test surfaces

- Rendered template/content inspection for forbidden values.
- Browser/keyboard journey for auth, portal, admin, and denial pages.
- Regression tests for preserved validation values and copy-button behavior.
- Authorization denial tests for non-admin access to admin surfaces.
