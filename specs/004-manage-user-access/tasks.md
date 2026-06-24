# Tasks: Manage User Access

**Input**: Design documents from `/specs/004-manage-user-access/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Every story crosses an identity or authorization boundary, so contract,
unit/integration, security, and applicable browser/CLI tests are required and
must be written before the corresponding implementation.

**Organization**: Tasks are grouped by user story so first-install bootstrap,
visual access control, lifecycle/recovery, and CLI automation can be implemented
and validated as explicit increments.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes different files and has no
  dependency on another incomplete task in the same phase.
- **[Story]**: Maps the task to US1, US2, US3, or US4 from spec.md.
- Every task names the exact file path or paths it changes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add reusable configuration and test support without implementing a
user story.

- [X] T001 Add validated recovery SMTP, reset TTL/cookie, user-search page-size, and management rate-limit settings in src/auth_ingress/config.py
- [X] T002 [P] Add a local capture/failure recovery-delivery fixture in tests/fixtures/recovery_delivery.py
- [X] T003 [P] Add subprocess, hidden-input, JSON, and exit-code CLI helpers in tests/cli_helpers.py
- [X] T004 [P] Add managed-user, group-rule, revision, and session test factories in tests/user_management_helpers.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared identity schema, transaction outcomes, audit safety,
and session controls used by every story.

**⚠️ CRITICAL**: No user-story implementation begins until these shared schema
and trust-boundary tasks are complete.

- [X] T005 [P] Add schema/backfill/duplicate-normalization contract tests for existing and clean installations in tests/contract/test_user_management_schema.py
- [X] T006 [P] Add audit allowlist, target/change-summary, nested-transaction, and secret-redaction tests in tests/security/test_user_management_audit.py
- [X] T007 Extend User with normalized_email, credential_status, and revision validation in src/auth_ingress/models/identity.py
- [X] T008 [P] Extend AuditEvent with target_user_id and allowlisted change_summary storage in src/auth_ingress/models/audit_event.py
- [X] T009 Export the new and extended identity/audit model surface in src/auth_ingress/models/__init__.py
- [X] T010 Implement portable user/audit column upgrades, normalized-email backfill, duplicate failure, and indexes in src/auth_ingress/repositories/schema.py
- [X] T011 [P] Define shared operation requests, previews, outcomes, error codes, and serialization types in src/auth_ingress/services/user_management_types.py
- [X] T012 Refactor audit recording for caller-owned transactions and strict management change-summary allowlists in src/auth_ingress/services/audit_service.py
- [X] T013 [P] Add bulk user-session revocation without nested commits in src/auth_ingress/services/session_service.py
- [X] T014 Update database fixtures and existing user constructors for normalized identity, credential state, revision, and transaction-safe audit behavior in tests/conftest.py

**Checkpoint**: Existing installations upgrade safely and all later stories can
share one revision, outcome, audit, and session-revocation contract.

---

## Phase 3: User Story 1 - Bootstrap the First Administrator (Priority: P1) 🎯

**Goal**: Move a clean packaged installation to one active administrator through
a local one-time command with no default or disclosed credential.

**Independent Test**: Start from a clean database, bootstrap one administrator,
sign in, view the authenticated admin boundary, and prove invalid, repeated,
interrupted, remote, and concurrent attempts create no extra or partial user.

### Tests for User Story 1

> Write these tests first and confirm bootstrap/setup behavior is absent or unsafe
> before implementing it.

- [X] T015 [P] [US1] Add bootstrap CLI grammar, hidden double-entry, exit-code, and already-initialized contract tests in tests/contract/test_bootstrap_contract.py
- [X] T016 [P] [US1] Add pre-bootstrap sign-in and no-remote-bootstrap route contract tests in tests/contract/test_first_install_ui.py
- [X] T017 [P] [US1] Add empty, successful, repeated, interrupted, migrated-install, demo-seed, and concurrent bootstrap integration tests in tests/integration/test_first_install_bootstrap.py
- [X] T018 [P] [US1] Add password argument/environment/output/log redaction and partial-state security tests in tests/security/test_bootstrap_security.py
- [X] T019 [P] [US1] Add clean-install bootstrap-to-admin-sign-in browser journey in tests/e2e/test_first_install.py

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement singleton InstallationState model and state invariants in src/auth_ingress/models/installation.py
- [X] T021 [US1] Create/backfill serialized installation state for clean and existing databases in src/auth_ingress/repositories/schema.py
- [X] T022 [US1] Implement atomic SQLite bootstrap serialization, first-admin creation, and audit outcomes in src/auth_ingress/services/bootstrap_service.py
- [X] T023 [US1] Add bootstrap-admin parsing, hidden password confirmation, safe outcomes, exit codes, and seed-demo installation-state consistency in src/auth_ingress/cli.py
- [X] T024 [P] [US1] Add the non-sensitive setup-required page in src/auth_ingress/web/templates/auth/setup_required.html
- [X] T025 [US1] Gate sign-in on installation state and render setup guidance without a remote registration path in src/auth_ingress/web/routes/auth.py
- [X] T026 [US1] Document first-run prerequisites, bootstrap, verification, retry, and already-initialized behavior in README.md

**Checkpoint**: A first-time installer can create exactly one administrator and
sign in; bootstrap is permanently closed afterward.

---

## Phase 4: User Story 2 - Control User Access (Priority: P2) 🎯 MVP

**Goal**: Let an authorized operator search users, inspect group-derived service
access, and safely preview/commit membership changes from the management page.

**Independent Test**: With seeded users/groups/services, use only the page to
find a user, explain overlapping grants, preview and commit additions/removals,
then prove denied, missing-group, and stale-revision operations change nothing.

### Tests for User Story 2

> Write these tests first and confirm the management route, explanation, and
> conflict guarantees fail before implementation.

- [X] T027 [P] [US2] Add list/detail/filter/pagination and preview/confirm route contract tests in tests/contract/test_admin_users_contract.py
- [X] T028 [P] [US2] Add effective-access explanation tests for overlapping grants, disabled users, and disabled services in tests/unit/test_effective_user_access.py
- [X] T029 [P] [US2] Add atomic membership, idempotency, missing-group, and stale-revision integration tests in tests/integration/test_user_memberships.py
- [X] T030 [P] [US2] Add signed-out, non-admin, revoked-admin, CSRF, enumeration, and stale-form security tests in tests/security/test_user_management_authorization.py
- [X] T031 [P] [US2] Add bounded search/filter validation over 10,000 identities in tests/integration/test_user_search_performance.py
- [X] T032 [P] [US2] Add browser journeys for empty state, access explanation, preview, success, denial, and conflict in tests/e2e/test_admin_users.py

### Implementation for User Story 2

- [X] T033 [P] [US2] Implement group-derived effective access with all granting groups and usable/policy separation in src/auth_ingress/services/access_service.py
- [X] T034 [US2] Implement authorized bounded user search, detail projections, and non-sensitive management-read audit outcomes in src/auth_ingress/services/user_admin_service.py
- [X] T035 [US2] Implement membership preview/commit, expected-revision comparison, idempotency, atomic audit, and effective-access differences in src/auth_ingress/services/user_admin_service.py
- [X] T036 [US2] Implement admin user list/detail and membership preview/confirm routes in src/auth_ingress/web/routes/admin_users.py
- [X] T037 [P] [US2] Build accessible list/filter/empty-state and user access-detail templates in src/auth_ingress/web/templates/admin/users.html and src/auth_ingress/web/templates/admin/user_detail.html
- [X] T038 [US2] Add bounded pagination and per-actor management request protections in src/auth_ingress/security/rate_limit.py and src/auth_ingress/web/routes/admin_users.py
- [X] T039 [US2] Register user routes and admin navigation in src/auth_ingress/main.py, src/auth_ingress/web/routes/__init__.py, and src/auth_ingress/web/templates/base.html
- [X] T040 [US2] Add management states, confirmation warnings, focus treatment, and non-color status styling in src/auth_ingress/web/static/portal.css

**Checkpoint**: The practical MVP is complete: a new installation can bootstrap
an admin who can then manage group-based user access from the page.

---

## Phase 5: User Story 3 - Manage User Lifecycle (Priority: P3)

**Goal**: Create, update, disable/reactivate, demote, and recover users without
exposing secrets, preserving lockout safety and immediate session invalidation.

**Independent Test**: Create a setup-required user, deliver and consume a setup
link, update/disable/reactivate the account, initiate reset, and prove replay,
delivery failure, self/last-admin changes, and old sessions are safely rejected.

### Tests for User Story 3

> Write these tests first and confirm lifecycle, recovery, and lockout behavior
> fail safely before implementation.

- [X] T041 [P] [US3] Add create/profile/status/admin/reset preview-confirm and recovery-route contract tests in tests/contract/test_user_lifecycle_contract.py
- [X] T042 [P] [US3] Add digest, expiry, supersession, reset-cookie exchange, and single-use unit tests in tests/unit/test_password_reset_service.py
- [X] T043 [P] [US3] Add create/setup delivery/update/disable/reactivate/reset and session-revocation integration tests in tests/integration/test_user_lifecycle.py
- [X] T044 [P] [US3] Add self-change, last-active-admin, revoked-actor, atomic rollback, and delivery-failure security tests in tests/security/test_user_lifecycle_security.py
- [X] T045 [P] [US3] Add malformed/expired/replayed token, query/referrer/cookie logging, CSRF, and secret-redaction tests in tests/security/test_password_reset_security.py
- [X] T046 [P] [US3] Add browser journeys for create/setup, disable/reactivate, demotion denial, reset success, and safe failure in tests/e2e/test_user_lifecycle.py

### Implementation for User Story 3

- [X] T047 [P] [US3] Implement digest-only PasswordResetRequest model, lifecycle fields, constraints, and relationships in src/auth_ingress/models/password_reset.py
- [X] T048 [US3] Add password-reset tables, credential-state backfill, indexes, and model exports in src/auth_ingress/repositories/schema.py and src/auth_ingress/models/__init__.py
- [X] T049 [P] [US3] Implement synchronous SMTP setup/reset delivery with transport security, safe timeouts, and test adapter injection in src/auth_ingress/services/recovery_delivery.py
- [X] T050 [US3] Implement request supersession, digest lookup, rate-limited cookie exchange, expiry, completion, rollback, and safe delivery failure in src/auth_ingress/services/password_reset_service.py
- [X] T051 [US3] Implement create/profile/status/admin preview-commit, normalized uniqueness, self/last-admin protection, and session revocation in src/auth_ingress/services/user_admin_service.py
- [X] T052 [US3] Extend admin user routes with create, profile, status, admin, retry-setup, and reset preview/confirm operations in src/auth_ingress/web/routes/admin_users.py
- [X] T053 [US3] Extend user list/detail templates with lifecycle forms, setup-required state, delivery outcomes, and lockout warnings in src/auth_ingress/web/templates/admin/users.html and src/auth_ingress/web/templates/admin/user_detail.html
- [X] T054 [US3] Implement clean-URL reset-cookie exchange and password completion routes in src/auth_ingress/web/routes/password_reset.py
- [X] T055 [P] [US3] Build no-referrer, token-free password setup/reset and generic invalid-request templates in src/auth_ingress/web/templates/auth/reset_password.html
- [X] T056 [US3] Reject setup-required credentials and recheck current account/admin state during authentication in src/auth_ingress/services/authentication_service.py and src/auth_ingress/security/dependencies.py
- [X] T057 [US3] Register recovery routes and enforce query/reset-cookie redaction plus recovery security headers in src/auth_ingress/main.py and src/auth_ingress/web/routes/__init__.py

**Checkpoint**: Authorized operators can manage the complete non-destructive user
lifecycle and users can securely establish or reset credentials.

---

## Phase 6: User Story 4 - Automate Access Operations with the CLI (Priority: P4)

**Goal**: Expose page-equivalent reads, previews, mutations, outcomes, and audit
behavior through an authenticated, idempotent, machine-readable CLI.

**Independent Test**: Use only packaged CLI commands to list/show/create/update,
disable/reactivate/reset, and change memberships; verify page parity, preview by
default, stable JSON/exit codes, idempotency, conflicts, denial, interruption
recovery, and redaction.

### Tests for User Story 4

> Write these tests first and confirm the existing CLI lacks the required grammar
> and safe machine interface before implementation.

- [X] T058 [P] [US4] Add users subcommand grammar, preview/apply, JSON schema, and exit-code contract tests in tests/contract/test_user_cli_contract.py
- [X] T059 [P] [US4] Add subprocess parity, idempotency, stale-revision, delivery-failure, and interruption integration tests in tests/integration/test_user_cli.py
- [X] T060 [P] [US4] Add hidden actor authentication, revoked/non-admin denial, enumeration resistance, and output/log redaction tests in tests/security/test_user_cli_security.py
- [X] T061 [P] [US4] Extend installed-distribution smoke tests for bootstrap and users command availability in tests/smoke/test_installed_package.py

### Implementation for User Story 4

- [X] T062 [US4] Implement hidden, rate-limited actor authentication and CLI-safe management context in src/auth_ingress/services/cli_user_auth.py
- [X] T063 [US4] Implement table/JSON result rendering and stable exit-code mapping in src/auth_ingress/services/cli_user_output.py
- [X] T064 [US4] Add users list/show/create/update/status/reset/membership parsers with preview-by-default semantics in src/auth_ingress/cli.py
- [X] T065 [US4] Wire all users commands to shared management services with expected revisions, atomic outcomes, and CLI audit category in src/auth_ingress/cli.py
- [X] T066 [US4] Document CLI grammar, automation-safe JSON, exit codes, preview/apply, conflict recovery, and secret handling in docs/user-management.md

**Checkpoint**: All requested management operations work consistently through
both page and packaged CLI.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete security, performance, packaging, migration,
documentation, and operator experience surface.

- [X] T067 [P] Add cross-story audit retention, allowlist, actor/target/outcome coverage, and captured-output secret scans in tests/security/test_user_management_evidence.py
- [X] T068 [P] Add real prior-schema upgrade and normalized-email collision rehearsal fixtures in tests/integration/test_user_management_migration.py
- [X] T069 [P] Update installation, recovery SMTP, first-run, management page, CLI, and incident-recovery guidance in README.md and docs/user-management.md
- [X] T070 Run keyboard, focus, non-color, empty/loading/error, and responsive browser checks and record outcomes in specs/004-manage-user-access/quickstart.md
- [X] T071 Run the full pytest/coverage suite on Python 3.12, 3.13, and 3.14 and record versions/results in specs/004-manage-user-access/quickstart.md
- [X] T072 Build wheel/source artifacts, run isolated smoke tests, scan contents for secrets/databases/tooling, and record hashes/results in specs/004-manage-user-access/quickstart.md
- [X] T073 Execute all first-install, page, lifecycle/recovery, CLI, conflict, denial, dependency-failure, and audit scenarios in specs/004-manage-user-access/quickstart.md
- [X] T074 Verify every FR-001–FR-026, SPR-001–SPR-012, SC-001–SC-010, and management/CLI/UI contract has passing evidence and record the mapping in specs/004-manage-user-access/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; T002-T004 can run in parallel after the
  current project state is inspected.
- **Foundational (Phase 2)**: Depends on Setup and blocks every user story. Tests
  T005-T006 are written first; schema/model tasks precede fixture migration.
- **US1 (Phase 3)**: Depends on Foundation and establishes first-install entry.
- **US2 (Phase 4)**: Depends on Foundation. It is independently testable with a
  seeded admin, but follows US1 for a deployable new-install workflow.
- **US3 (Phase 5)**: Depends on Foundation and reuses US2 management service/page;
  recovery-model and delivery work can begin in parallel with late US2 UI work.
- **US4 (Phase 6)**: Depends on the shared operations delivered by US2 and US3;
  its contract/security tests can be written earlier.
- **Polish (Phase 7)**: Depends on every selected story.

### User Story Dependencies

- **US1 (P1)**: No other story dependency; yields secure first-admin bootstrap.
- **US2 (P2)**: No code dependency on US1 when tested with fixtures, but US1+US2
  form the practical access-management MVP for a fresh installation.
- **US3 (P3)**: Extends US2 routes, templates, and shared service with lifecycle
  and recovery behavior.
- **US4 (P4)**: Consumes all shared US2/US3 operations and adds no parallel policy
  implementation of its own.

### Within Each User Story

- Security-sensitive tests MUST be written and observed failing before matching
  implementation tasks.
- Models/schema precede services; services precede route/CLI adapters; adapters
  precede browser/subprocess acceptance completion.
- Preview and commit share validation; audit creation participates in the same
  database transaction as each mutation.
- A checkpoint is accepted only when its independent test passes without relying
  on a later story.

### Entity and Contract Mapping

- **InstallationState**: T015-T025 (US1).
- **Managed User, revision, AuditEvent**: T005-T014 (Foundation), extended by
  T034-T035 (US2) and T051 (US3).
- **EffectiveAccessResult and GroupMembership**: T027-T040 (US2).
- **PasswordResetRequest and recovery cookie**: T041-T057 (US3).
- **Management operation contract**: T011-T014, T034-T035, T050-T051.
- **CLI contract**: T058-T066 (US4).
- **UI flow contract**: T015-T025, T027-T040, T041-T057.

## Parallel Opportunities

- Setup helpers T002-T004 change independent test-support files.
- Foundational tests T005-T006 and independent model/type/session tasks T008,
  T011, and T013 can proceed concurrently before integration in T014.
- All test tasks within each user story are parallelizable before implementation.
- US1 template T024 can proceed while bootstrap service/CLI work is underway.
- US2 effective-access service T033 and templates T037 can proceed after their
  contracts are stable, before route integration.
- US3 reset model T047, delivery adapter T049, reset route T054, and template T055
  touch independent files and can proceed concurrently after tests.
- US4 contract, integration, security, and smoke tests T058-T061 can be authored
  together before CLI implementation.
- Polish evidence, migration, and documentation tasks T067-T069 are independent.

## Parallel Examples

### User Story 1

```text
Task T015: Bootstrap CLI contract tests
Task T016: First-install UI contract tests
Task T017: Bootstrap integration/concurrency tests
Task T018: Bootstrap secret-boundary security tests
Task T019: First-install browser journey
```

### User Story 2

```text
Task T027: Admin user route contracts
Task T028: Effective-access unit tests
Task T029: Membership integration tests
Task T030: Management authorization security tests
Task T031: Search performance validation
Task T032: User-management browser journeys
```

### User Story 3

```text
Task T041: Lifecycle/recovery route contracts
Task T042: Password-reset unit tests
Task T043: Lifecycle integration tests
Task T044: Lifecycle lockout security tests
Task T045: Reset-token security tests
Task T046: Lifecycle browser journeys
```

### User Story 4

```text
Task T058: CLI grammar/JSON/exit contracts
Task T059: CLI integration and parity tests
Task T060: CLI actor/redaction security tests
Task T061: Installed CLI smoke tests
```

## Implementation Strategy

### First-Install Increment (US1)

1. Complete Setup and Foundation.
2. Complete T015-T026 in test-first order.
3. Stop and validate bootstrap, setup-required UI, sign-in, concurrency, and
   redaction independently.

### Practical MVP (US1 + US2)

1. Deliver secure first-admin bootstrap.
2. Add searchable user detail, access explanations, and membership changes.
3. Stop and run the complete first-install-to-access-change browser scenario.
4. Deploy only if last-admin, stale revision, denial, audit, and secret scans pass.

### Incremental Delivery

1. Foundation → schema and shared trust boundaries ready.
2. US1 → first install works safely.
3. US2 → SRE/Admin can control access lists from the page.
4. US3 → complete lifecycle and secure recovery.
5. US4 → equivalent automation through the CLI.
6. Polish → full matrix, packaging, migration, accessibility, and evidence.

## Notes

- `[P]` marks tasks that touch different files and do not depend on incomplete
  tasks in the same phase.
- Story labels provide traceability to the prioritized journeys in spec.md.
- Do not add direct per-user service grants, hard deletion, default credentials,
  public bootstrap, or an alternate CLI authorization path.
- Keep passwords, hashes, reset secrets/digests, sessions, cookies, tokens,
  configuration secrets, and unnecessary personal data out of output and audit.
- Commit after each task or coherent dependency group; every checkpoint is a safe
  place to pause and validate independently.
