# Research: Preserve Management Form Input

## Decision: Preserve safe form state in the returned server-rendered response

**Rationale**: The application already uses server-rendered management pages. Returning the failed form with request-scoped safe values keeps validation authoritative on the server, avoids adding client-only state as a source of truth, and works for users without relying on JavaScript.

**Alternatives considered**:

- Browser-only client validation: rejected because it cannot be the source of truth for administrative security rules and would not cover stale records or permission changes.
- Persist failed form drafts: rejected because the problem is immediate validation recovery and durable drafts would add privacy, retention, and cleanup concerns.
- Redirect after validation failure: rejected because redirects lose request body state unless additional temporary storage is introduced.

## Decision: Represent validation feedback as field-level and form-level messages

**Rationale**: Some errors map directly to fields, such as missing slug or invalid email. Others are form-level, such as stale revision, missing referenced group, authorization denial, or dependency failure. Supporting both preserves actionable UX without misclassifying security outcomes as field mistakes.

**Alternatives considered**:

- Single page-level error string: rejected because it caused unclear correction steps and does not meet the field-specific success criteria.
- Only field-level errors: rejected because authorization, stale record, dependency, and CSRF failures are not ordinary field mistakes.

## Decision: Never repopulate sensitive fields after failed submissions

**Rationale**: The constitution requires credentials, temporary passwords, tokens, sessions, and recovery values to remain protected. Failed forms must preserve names, descriptions, URLs, statuses, and selections, but must leave sensitive fields blank or display a safe one-time result only after successful actions when already supported.

**Alternatives considered**:

- Repopulate every submitted value: rejected because it risks exposing secrets in HTML, browser history, screenshots, and logs.
- Redact sensitive fields with placeholders: rejected because placeholders can be mistaken for actual submitted values and may lead to accidental submission of placeholder text.

## Decision: Keep duplicate submission and confirmation behavior intact

**Rationale**: Existing user management flows include preview/confirm behavior and revision checks. Preserving form input must not bypass confirmations, expected revision checks, or duplicate-action prevention.

**Alternatives considered**:

- Remove preview/confirm flows to simplify form recovery: rejected because those flows protect administrative changes.
- Treat all failed submissions as retryable validation errors: rejected because denied, conflicted, expired, and dependency-failure outcomes require distinct handling.

## Decision: Validate through current admin surface tests plus targeted regression tests

**Rationale**: The bug is user-visible and route/template-dependent. Contract tests should assert response semantics, integration tests should assert management state remains correct, security tests should assert sensitive values are not echoed or logged, and e2e tests should prove actual browser form fields keep expected values.

**Alternatives considered**:

- Unit tests only: rejected because they would miss template repopulation regressions.
- Manual QA only: rejected because this is a regression-prone UX and security-sensitive behavior.
