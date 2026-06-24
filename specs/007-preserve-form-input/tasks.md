# Tasks: Preserve Management Form Input

**Input**: Design documents from `/specs/007-preserve-form-input/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/management-form-state.md, quickstart.md

**Tests**: Required because this feature changes identity/access management forms and must prove sensitive values are not redisplayed or logged.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm current admin form surfaces and prepare focused regression locations.

- [ ] T001 Inspect current service management form fields and validation branches in src/auth_ingress/web/routes/admin_services.py and src/auth_ingress/web/templates/admin/services.html
- [ ] T002 Inspect current user management form fields and validation branches in src/auth_ingress/web/routes/admin_users.py, src/auth_ingress/web/templates/admin/users.html, and src/auth_ingress/web/templates/admin/user_detail.html
- [ ] T003 [P] Review existing service admin tests for reusable fixtures in tests/contract/test_admin_contract.py, tests/integration/test_admin_services.py, and tests/e2e/test_admin_services.py
- [ ] T004 [P] Review existing user admin tests for reusable fixtures in tests/contract/test_admin_users_contract.py, tests/integration/test_user_lifecycle.py, and tests/e2e/test_admin_users.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared request-scoped form state primitives required by all stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T005 Define request-scoped ManagementFormState, FieldError, and sensitive-field helpers in src/auth_ingress/services/user_management_types.py
- [ ] T006 [P] Add unit tests for ManagementFormState safe-value preservation and sensitive-field exclusion in tests/unit/test_management_form_state.py
- [ ] T007 Add template context conventions for `form_state`, `field_errors`, and `form_errors` in src/auth_ingress/web/web.py
- [ ] T008 Document sensitive management field names and default exclusion behavior in src/auth_ingress/services/user_management_types.py
- [ ] T009 Add shared assertions for preserved safe values and absent sensitive values in tests/cli_helpers.py or tests/conftest.py

**Checkpoint**: Shared form state exists, excludes sensitive values, and can be passed to templates consistently.

---

## Phase 3: User Story 1 - Preserve entered values after validation errors (Priority: P1) 🎯 MVP

**Goal**: Invalid management submissions return the form with safe submitted values still visible, while sensitive values remain blank.

**Independent Test**: Submit invalid values on service and user management forms, confirm non-sensitive values remain visible, sensitive values are absent, and correcting only the invalid value allows success.

### Tests for User Story 1

- [ ] T010 [P] [US1] Add service-create contract test for preserving slug, display_name, description, destination, status, group_names, proxy_enabled, and websocket_enabled after invalid submission in tests/contract/test_admin_contract.py
- [ ] T011 [P] [US1] Add user-create contract test for preserving email, display_name, status, is_admin, and group_ids after invalid submission in tests/contract/test_admin_users_contract.py
- [ ] T012 [P] [US1] Add security regression test proving temporary passwords, credentials, tokens, and recovery values are not echoed after failed management submissions in tests/security/test_management_form_state.py
- [ ] T013 [P] [US1] Add integration test proving corrected service submission succeeds without re-entering unchanged fields in tests/integration/test_admin_services.py
- [ ] T014 [P] [US1] Add integration test proving corrected user creation succeeds without re-entering unchanged fields and only displays temporary password after success in tests/integration/test_user_lifecycle.py

### Implementation for User Story 1

- [ ] T015 [US1] Update service management route rendering to accept and pass request-scoped form_state in src/auth_ingress/web/routes/admin_services.py
- [ ] T016 [US1] Preserve safe submitted service values after ServiceValidationError and CSRF validation failures in src/auth_ingress/web/routes/admin_services.py
- [ ] T017 [US1] Update service management template fields to prefer form_state safe values over blank/default values after failed submissions in src/auth_ingress/web/templates/admin/services.html
- [ ] T018 [US1] Update user creation list rendering to accept and pass request-scoped form_state in src/auth_ingress/web/routes/admin_users.py
- [ ] T019 [US1] Preserve safe submitted user creation values after ManagementError and CSRF validation failures in src/auth_ingress/web/routes/admin_users.py
- [ ] T020 [US1] Update user creation template fields to prefer form_state safe values while keeping temporary_password display success-only in src/auth_ingress/web/templates/admin/users.html
- [ ] T021 [US1] Ensure failed management submission audit or diagnostic paths never include sensitive submitted values in src/auth_ingress/services/audit_service.py and src/auth_ingress/web/routes/admin_users.py

**Checkpoint**: MVP works for core service create/edit and user create validation recovery without sensitive-field echoing.

---

## Phase 4: User Story 2 - Make validation errors actionable at field level (Priority: P2)

**Goal**: Invalid management submissions identify the affected field and describe the correction, while preserving distinct outcomes for authorization, conflicts, not-found records, and dependency failures.

**Independent Test**: Submit missing, malformed, duplicate, unauthorized, stale, and dependency-failure inputs; verify field-level errors for ordinary validation and form-level outcomes for non-validation failures.

### Tests for User Story 2

- [ ] T022 [P] [US2] Add contract tests for field-specific service validation messages in tests/contract/test_admin_contract.py
- [ ] T023 [P] [US2] Add contract tests for field-specific user creation and profile validation messages in tests/contract/test_admin_users_contract.py
- [ ] T024 [P] [US2] Add security tests proving denied, stale, not-found, and dependency-failure management outcomes are not rendered as ordinary field validation in tests/security/test_management_form_outcomes.py
- [ ] T025 [P] [US2] Add integration tests for multiple simultaneous validation errors returning together when safe in tests/integration/test_admin_services.py

### Implementation for User Story 2

- [ ] T026 [US2] Extend service validation errors with stable field/error metadata while preserving existing messages in src/auth_ingress/services/service_admin_service.py
- [ ] T027 [US2] Map service validation metadata to field_errors and form_errors in src/auth_ingress/web/routes/admin_services.py
- [ ] T028 [US2] Render service field-level validation messages near affected fields in src/auth_ingress/web/templates/admin/services.html
- [ ] T029 [US2] Extend user management errors with stable field/error metadata for user create, profile, memberships, and status changes in src/auth_ingress/services/user_admin_service.py and src/auth_ingress/services/user_management_types.py
- [ ] T030 [US2] Map user management validation metadata to field_errors and form_errors in src/auth_ingress/web/routes/admin_users.py
- [ ] T031 [US2] Render user management field-level validation messages near affected fields in src/auth_ingress/web/templates/admin/users.html and src/auth_ingress/web/templates/admin/user_detail.html
- [ ] T032 [US2] Preserve distinct HTTP status and page-level messaging for denied, not-found, conflict, rate-limit, CSRF, and dependency-failure outcomes in src/auth_ingress/web/routes/admin_services.py and src/auth_ingress/web/routes/admin_users.py

**Checkpoint**: Administrators can see exactly what to fix, and security/control-flow failures remain clearly distinct from validation errors.

---

## Phase 5: User Story 3 - Preserve selection state in multi-value controls (Priority: P3)

**Goal**: Group selections, checkboxes, radio controls, dropdowns, status controls, and enabled flags remain selected after unrelated validation failures.

**Independent Test**: Select multiple groups and toggle status/boolean controls, submit another invalid field, and confirm all safe selections remain selected on the returned form.

### Tests for User Story 3

- [ ] T033 [P] [US3] Add service multi-value selection contract tests for group_names, proxy_enabled, websocket_enabled, and status preservation in tests/contract/test_admin_contract.py
- [ ] T034 [P] [US3] Add user multi-value selection contract tests for group_ids, is_admin, status, and membership preservation in tests/contract/test_admin_users_contract.py
- [ ] T035 [P] [US3] Add browser/e2e regression for service form selected groups and enabled flags after unrelated validation failure in tests/e2e/test_admin_services.py
- [ ] T036 [P] [US3] Add browser/e2e regression for user form selected groups, admin flag, and status after unrelated validation failure in tests/e2e/test_admin_users.py

### Implementation for User Story 3

- [ ] T037 [US3] Normalize selected service group names and boolean flags into form_state selected_values in src/auth_ingress/web/routes/admin_services.py
- [ ] T038 [US3] Render service group, status, proxy_enabled, and websocket_enabled controls from selected_values after validation failure in src/auth_ingress/web/templates/admin/services.html
- [ ] T039 [US3] Normalize selected user group IDs, admin flag, status, and membership choices into form_state selected_values in src/auth_ingress/web/routes/admin_users.py
- [ ] T040 [US3] Render user creation and user detail group/status/admin controls from selected_values after validation failure in src/auth_ingress/web/templates/admin/users.html and src/auth_ingress/web/templates/admin/user_detail.html
- [ ] T041 [US3] Preserve existing record context for edited user and service records while applying selected_values only to the active failed form in src/auth_ingress/web/routes/admin_services.py and src/auth_ingress/web/routes/admin_users.py

**Checkpoint**: Multi-value administrative controls no longer reset after unrelated validation failures.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate full feature behavior, documentation, and regression safety.

- [ ] T042 [P] Update quickstart validation notes if actual focused test commands differ in specs/007-preserve-form-input/quickstart.md
- [ ] T043 [P] Add or update user-facing admin form copy for validation guidance in src/auth_ingress/web/templates/admin/services.html, src/auth_ingress/web/templates/admin/users.html, and src/auth_ingress/web/templates/admin/user_detail.html
- [ ] T044 Run focused contract and integration tests from specs/007-preserve-form-input/quickstart.md
- [ ] T045 Run focused e2e tests for admin service and user management form recovery in tests/e2e/test_admin_services.py and tests/e2e/test_admin_users.py
- [ ] T046 Run security tests verifying sensitive values are not echoed or logged in tests/security/
- [ ] T047 Run full test suite with uv run pytest and resolve regressions across tests/
- [ ] T048 Review final diff for sensitive logging, duplicate submission behavior, and authorization/validation separation in src/auth_ingress/web/routes/admin_services.py, src/auth_ingress/web/routes/admin_users.py, and src/auth_ingress/services/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational and can be built after or alongside US1, but template integration is simpler after US1 form_state wiring.
- **User Story 3 (Phase 5)**: Depends on Foundational and benefits from US1 form_state wiring; can be tested independently.
- **Polish (Phase 6)**: Depends on desired stories being complete.

### User Story Dependencies

- **US1 (P1)**: Core MVP. No dependency on US2 or US3.
- **US2 (P2)**: Can start after Foundational; uses form_state conventions from US1 if US1 is already complete.
- **US3 (P3)**: Can start after Foundational; uses selected_values conventions from Phase 2 and US1.

### Parallel Opportunities

- T003 and T004 can run in parallel.
- T006 can run in parallel with T007 and T008 after T005 is drafted.
- US1 tests T010-T014 can run in parallel before implementation.
- US2 tests T022-T025 can run in parallel before implementation.
- US3 tests T033-T036 can run in parallel before implementation.
- Template copy updates for service and user pages can be split by file once shared form_state conventions are stable.

---

## Parallel Example: User Story 1

```bash
Task: "T010 [US1] Add service-create contract test in tests/contract/test_admin_contract.py"
Task: "T011 [US1] Add user-create contract test in tests/contract/test_admin_users_contract.py"
Task: "T012 [US1] Add sensitive-field security regression in tests/security/test_management_form_state.py"
Task: "T013 [US1] Add service correction integration test in tests/integration/test_admin_services.py"
Task: "T014 [US1] Add user correction integration test in tests/integration/test_user_lifecycle.py"
```

---

## Parallel Example: User Story 2

```bash
Task: "T022 [US2] Add service field-error contract tests in tests/contract/test_admin_contract.py"
Task: "T023 [US2] Add user field-error contract tests in tests/contract/test_admin_users_contract.py"
Task: "T024 [US2] Add denied/stale/dependency security tests in tests/security/test_management_form_outcomes.py"
Task: "T025 [US2] Add multiple-error integration tests in tests/integration/test_admin_services.py"
```

---

## Parallel Example: User Story 3

```bash
Task: "T033 [US3] Add service multi-value contract tests in tests/contract/test_admin_contract.py"
Task: "T034 [US3] Add user multi-value contract tests in tests/contract/test_admin_users_contract.py"
Task: "T035 [US3] Add service browser regression in tests/e2e/test_admin_services.py"
Task: "T036 [US3] Add user browser regression in tests/e2e/test_admin_users.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Write and observe failing US1 tests T010-T014.
3. Complete US1 implementation T015-T021.
4. Validate US1 independently with focused contract, integration, and security tests.
5. Stop for review or continue to field-level UX.

### Incremental Delivery

1. Deliver US1 to stop clearing safe values after validation failures.
2. Deliver US2 to make errors field-specific and distinguish non-validation failures.
3. Deliver US3 to preserve all multi-value controls and selected state.
4. Complete polish and full regression validation.

### Validation Commands

```bash
uv run pytest tests/contract/test_admin_contract.py tests/contract/test_admin_users_contract.py -q
uv run pytest tests/integration/test_admin_services.py tests/integration/test_user_lifecycle.py -q
uv run pytest tests/security -q
uv run pytest tests/e2e/test_admin_services.py tests/e2e/test_admin_users.py -q
```

## Notes

- Every task uses the required checklist format.
- Tests for each user story should be written before implementation and fail for the current bug.
- Preserve only request-scoped safe values; do not persist failed form drafts.
- Keep credentials, tokens, temporary passwords, recovery secrets, and unnecessary personal data out of HTML, logs, and audit payloads.
