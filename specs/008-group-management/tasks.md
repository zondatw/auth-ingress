# Tasks: Group Management Page

**Input**: Design documents from `/specs/008-group-management/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/group-management-ui.md, quickstart.md

**Tests**: Required because group management changes access-control behavior, administrative authorization boundaries, audit evidence, and service access decisions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm existing group/access surfaces and prepare focused regression locations.

- [ ] T001 Inspect existing Group, GroupMembership, AccessRule, and audit models in src/auth_ingress/models/identity.py, src/auth_ingress/models/service_entry.py, and src/auth_ingress/models/audit_event.py
- [ ] T002 Inspect existing schema upgrade behavior for users, services, and audits in src/auth_ingress/repositories/schema.py
- [ ] T003 [P] Inspect existing admin route/template patterns in src/auth_ingress/web/routes/admin_users.py, src/auth_ingress/web/routes/admin_services.py, src/auth_ingress/web/templates/admin/users.html, and src/auth_ingress/web/templates/admin/services.html
- [ ] T004 [P] Inspect existing admin authorization, CSRF, rate limiting, and form-state helpers in src/auth_ingress/security/dependencies.py, src/auth_ingress/security/csrf.py, src/auth_ingress/security/rate_limit.py, and src/auth_ingress/services/user_management_types.py
- [ ] T005 [P] Inspect reusable group/user/service test fixtures and helpers in tests/conftest.py, tests/user_management_helpers.py, tests/contract/test_admin_users_contract.py, tests/integration/test_user_memberships.py, and tests/e2e/test_admin_users.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared group lifecycle schema, service primitives, routing registration, and access-evaluation behavior required by all stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Add group lifecycle fields normalized_name, status, revision, and timestamp defaults to Group in src/auth_ingress/models/identity.py
- [ ] T007 Add schema upgrade and backfill behavior for existing groups in src/auth_ingress/repositories/schema.py
- [ ] T008 [P] Add unit tests for group name normalization, status validation, and revision defaults in tests/unit/test_group_admin_service.py
- [ ] T009 Add GroupValidationError and group operation result helpers in src/auth_ingress/services/group_admin_service.py
- [ ] T010 Add require-admin actor validation and stale revision helpers for group operations in src/auth_ingress/services/group_admin_service.py
- [ ] T011 Update effective access calculations to ignore deactivated groups in src/auth_ingress/services/access_service.py
- [ ] T012 Update service entry authorization to ignore deactivated groups in src/auth_ingress/services/proxy_authorization_service.py
- [ ] T013 Register the admin group route module in src/auth_ingress/main.py
- [ ] T014 Add admin navigation entry for group management in src/auth_ingress/web/templates/base.html
- [ ] T015 Verify Python and universal ignore patterns cover generated caches in ./.gitignore

**Checkpoint**: Group lifecycle metadata exists, schema upgrades are planned, route registration is available, and deactivated groups can be excluded from access decisions.

---

## Phase 3: User Story 1 - View and understand groups (Priority: P1) 🎯 MVP

**Goal**: Authorized operators can list, search, filter, and inspect groups with user/service dependency summaries without changing state.

**Independent Test**: Sign in as an authorized operator, open group management, verify group list usage summaries, filter results, open a group detail view, and confirm non-admin users are denied without leaked group data.

### Tests for User Story 1

- [ ] T016 [P] [US1] Add contract tests for group list and detail display requirements in tests/contract/test_admin_groups_contract.py
- [ ] T017 [P] [US1] Add integration tests for group search, filters, dependency counts, and empty state in tests/integration/test_admin_groups.py
- [ ] T018 [P] [US1] Add security tests for unauthenticated and non-admin group management denial without group data leakage in tests/security/test_group_management_security.py
- [ ] T019 [P] [US1] Add browser regression for group list, search, and detail dependency visibility in tests/e2e/test_admin_groups.py

### Implementation for User Story 1

- [ ] T020 [US1] Implement group listing, filtering, dependency summary, and bounded detail query functions in src/auth_ingress/services/group_admin_service.py
- [ ] T021 [US1] Implement group list and detail GET routes with admin authorization and rate limiting in src/auth_ingress/web/routes/admin_groups.py
- [ ] T022 [US1] Create group management list template with search, filters, counts, empty state, and create form in src/auth_ingress/web/templates/admin/groups.html
- [ ] T023 [US1] Create group detail template with metadata, dependency summaries, audit summary area, and read-only access impact in src/auth_ingress/web/templates/admin/group_detail.html
- [ ] T024 [US1] Add safe audit evidence for group detail reads or dependency inspections where required in src/auth_ingress/services/audit_service.py and src/auth_ingress/web/routes/admin_groups.py
- [ ] T025 [US1] Ensure group list/detail pages do not expose credentials, sessions, tokens, or recovery data in src/auth_ingress/web/templates/admin/groups.html and src/auth_ingress/web/templates/admin/group_detail.html

**Checkpoint**: MVP group management is read-only, authorized, searchable, and independently testable.

---

## Phase 4: User Story 2 - Create and edit groups safely (Priority: P2)

**Goal**: Authorized operators can create groups and update safe group metadata with duplicate-name protection, stale-edit protection, field-level validation, preserved form input, and audit evidence.

**Independent Test**: Create a group, submit invalid and duplicate names, edit metadata, attempt stale edits from two views, and verify no duplicate or partial change occurs.

### Tests for User Story 2

- [ ] T026 [P] [US2] Add contract tests for create group form outcomes, duplicate names, preserved values, and field errors in tests/contract/test_admin_groups_contract.py
- [ ] T027 [P] [US2] Add contract tests for edit group preview, confirm, and stale revision outcomes in tests/contract/test_admin_groups_contract.py
- [ ] T028 [P] [US2] Add unit tests for create/update validation, normalized-name uniqueness, no-change, and stale revision logic in tests/unit/test_group_admin_service.py
- [ ] T029 [P] [US2] Add integration tests for create, edit, duplicate rejection, and stale edit recovery in tests/integration/test_admin_groups.py
- [ ] T030 [P] [US2] Add security tests for denied create/edit attempts, CSRF failures, excessive requests, and sensitive-output exclusion in tests/security/test_group_management_security.py

### Implementation for User Story 2

- [ ] T031 [US2] Implement create_group, preview_update_group, and update_group service operations in src/auth_ingress/services/group_admin_service.py
- [ ] T032 [US2] Add group create POST route with CSRF validation, form_state preservation, field errors, and audit outcomes in src/auth_ingress/web/routes/admin_groups.py
- [ ] T033 [US2] Add group edit preview and confirm POST routes with expected_revision conflict handling in src/auth_ingress/web/routes/admin_groups.py
- [ ] T034 [US2] Render create group field errors and preserved values in src/auth_ingress/web/templates/admin/groups.html
- [ ] T035 [US2] Render edit group form, preview confirmation, conflict messages, and preserved values in src/auth_ingress/web/templates/admin/group_detail.html
- [ ] T036 [US2] Add non-sensitive audit events for group create, update, invalid input, denied, and conflict outcomes in src/auth_ingress/services/group_admin_service.py and src/auth_ingress/web/routes/admin_groups.py
- [ ] T037 [US2] Ensure created and edited groups appear consistently in user and service management group selectors in src/auth_ingress/web/routes/admin_users.py and src/auth_ingress/web/routes/admin_services.py

**Checkpoint**: Operators can safely create and edit group metadata without losing safe form values or overwriting newer changes.

---

## Phase 5: User Story 3 - Deactivate, reactivate, or remove groups with dependency guardrails (Priority: P3)

**Goal**: Authorized operators can preview and confirm group deactivation/reactivation, remove only unused groups, and receive clear dependency-blocked and lockout-risk outcomes.

**Independent Test**: Deactivate and reactivate a group with dependencies, verify access impact changes, attempt to remove a used group, remove an unused group, and confirm audit evidence and no dangling references.

### Tests for User Story 3

- [ ] T038 [P] [US3] Add contract tests for deactivate, reactivate, remove eligible, and dependency-blocked UI outcomes in tests/contract/test_admin_groups_contract.py
- [ ] T039 [P] [US3] Add unit tests for dependency summaries, lifecycle transitions, removal eligibility, and last-admin-risk checks in tests/unit/test_group_admin_service.py
- [ ] T040 [P] [US3] Add integration tests proving deactivated groups stop granting effective access and reactivation restores group access behavior in tests/integration/test_admin_groups.py
- [ ] T041 [P] [US3] Add integration tests proving removal is blocked for groups with users/services and succeeds for unused groups in tests/integration/test_admin_groups.py
- [ ] T042 [P] [US3] Add security tests for denied lifecycle operations, stale lifecycle submissions, and audit redaction in tests/security/test_group_management_security.py
- [ ] T043 [P] [US3] Add browser regression for lifecycle preview, dependency-blocked removal, and unused-group removal in tests/e2e/test_admin_groups.py

### Implementation for User Story 3

- [ ] T044 [US3] Implement group dependency summary, lifecycle preview, deactivate_group, reactivate_group, and remove_group operations in src/auth_ingress/services/group_admin_service.py
- [ ] T045 [US3] Implement last-active-administrator-risk detection for group deactivation/removal in src/auth_ingress/services/group_admin_service.py
- [ ] T046 [US3] Add lifecycle preview and confirm POST routes for deactivate, reactivate, and remove in src/auth_ingress/web/routes/admin_groups.py
- [ ] T047 [US3] Render lifecycle preview panels, dependency-blocked removal explanations, and eligible removal confirmation in src/auth_ingress/web/templates/admin/group_detail.html
- [ ] T048 [US3] Update user management group selectors to distinguish active and deactivated groups where needed in src/auth_ingress/web/templates/admin/users.html and src/auth_ingress/web/templates/admin/user_detail.html
- [ ] T049 [US3] Update service management group validation and selectors to reject removed/unavailable groups and surface clear errors in src/auth_ingress/services/service_admin_service.py and src/auth_ingress/web/templates/admin/services.html
- [ ] T050 [US3] Add non-sensitive audit events for group deactivation, reactivation, removal, dependency-blocked removal, and lockout-risk denial in src/auth_ingress/services/group_admin_service.py and src/auth_ingress/services/audit_service.py

**Checkpoint**: Group lifecycle controls are safe, reversible where intended, dependency-aware, audited, and reflected in access decisions.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate full feature behavior, documentation, and regression safety.

- [ ] T051 [P] Update quickstart validation notes if actual focused test commands differ in specs/008-group-management/quickstart.md
- [ ] T052 [P] Add or update user-facing admin copy for group management guidance in src/auth_ingress/web/templates/admin/groups.html and src/auth_ingress/web/templates/admin/group_detail.html
- [ ] T053 Run focused group management unit, contract, integration, security, and e2e tests from specs/008-group-management/quickstart.md
- [ ] T054 Run user/service/access regression tests listed in specs/008-group-management/quickstart.md
- [ ] T055 Run full test suite with uv run pytest and resolve regressions across tests/ using tests/
- [ ] T056 Review final diff for sensitive logging, authorization boundaries, stale-write behavior, dependency guardrails, and audit evidence in src/auth_ingress/services/group_admin_service.py, src/auth_ingress/web/routes/admin_groups.py, src/auth_ingress/services/access_service.py, and src/auth_ingress/services/proxy_authorization_service.py
- [ ] T057 Verify all tasks are complete and update specs/008-group-management/tasks.md task statuses

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP read-only group management.
- **User Story 2 (Phase 4)**: Depends on Foundational and benefits from US1 route/template surfaces.
- **User Story 3 (Phase 5)**: Depends on Foundational and benefits from US1 dependency display plus US2 revision/form patterns.
- **Polish (Phase 6)**: Depends on all desired stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational and provides the minimum useful group management page.
- **US2 (P2)**: Can start after Foundational, but implementation is simpler after US1 list/detail routes exist.
- **US3 (P3)**: Can start after Foundational, but lifecycle preview depends on dependency summaries introduced for US1.

### Parallel Opportunities

- T003, T004, and T005 can run in parallel during setup.
- T008 can run in parallel with T009-T014 once the schema direction is clear.
- US1 tests T016-T019 can run in parallel before US1 implementation.
- US2 tests T026-T030 can run in parallel before US2 implementation.
- US3 tests T038-T043 can run in parallel before US3 implementation.
- Template copy updates for group list/detail can be split by file once route context names are stable.

---

## Parallel Example: User Story 1

```bash
Task: "T016 [US1] Add contract tests for group list and detail display requirements in tests/contract/test_admin_groups_contract.py"
Task: "T017 [US1] Add integration tests for group search, filters, dependency counts, and empty state in tests/integration/test_admin_groups.py"
Task: "T018 [US1] Add security tests for unauthenticated and non-admin group management denial without group data leakage in tests/security/test_group_management_security.py"
Task: "T019 [US1] Add browser regression for group list, search, and detail dependency visibility in tests/e2e/test_admin_groups.py"
```

---

## Parallel Example: User Story 2

```bash
Task: "T026 [US2] Add contract tests for create group form outcomes, duplicate names, preserved values, and field errors in tests/contract/test_admin_groups_contract.py"
Task: "T028 [US2] Add unit tests for create/update validation, normalized-name uniqueness, no-change, and stale revision logic in tests/unit/test_group_admin_service.py"
Task: "T029 [US2] Add integration tests for create, edit, duplicate rejection, and stale edit recovery in tests/integration/test_admin_groups.py"
Task: "T030 [US2] Add security tests for denied create/edit attempts, CSRF failures, excessive requests, and sensitive-output exclusion in tests/security/test_group_management_security.py"
```

---

## Parallel Example: User Story 3

```bash
Task: "T038 [US3] Add contract tests for deactivate, reactivate, remove eligible, and dependency-blocked UI outcomes in tests/contract/test_admin_groups_contract.py"
Task: "T039 [US3] Add unit tests for dependency summaries, lifecycle transitions, removal eligibility, and last-admin-risk checks in tests/unit/test_group_admin_service.py"
Task: "T040 [US3] Add integration tests proving deactivated groups stop granting effective access and reactivation restores group access behavior in tests/integration/test_admin_groups.py"
Task: "T043 [US3] Add browser regression for lifecycle preview, dependency-blocked removal, and unused-group removal in tests/e2e/test_admin_groups.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Write and observe failing US1 tests T016-T019.
3. Complete US1 implementation T020-T025.
4. Validate US1 independently with focused contract, integration, security, and e2e tests.
5. Stop for review or continue to mutation workflows.

### Incremental Delivery

1. Deliver US1 to provide group visibility and dependency understanding.
2. Deliver US2 to allow safe create/edit group metadata.
3. Deliver US3 to add lifecycle and removal guardrails.
4. Complete polish, cross-page regression coverage, and full test validation.

### Notes

- Security-sensitive tests must fail before implementation.
- Keep group names, memberships, service associations, operator data, and audit evidence protected as access-control data.
- Do not log credentials, session identifiers, recovery secrets, tokens, password hashes, or unnecessary personal data.
- Preserve existing user and service management behavior while adding group lifecycle awareness.
