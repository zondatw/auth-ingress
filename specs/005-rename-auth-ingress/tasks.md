# Tasks: Rename Auth Ingress

**Input**: Design documents from `/specs/005-rename-auth-ingress/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included because this feature touches identity, release, CLI, configuration, and security-sensitive auth surfaces.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish rename constants, scan fixtures, and compatibility expectations used by all stories.

- [X] T001 Add shared rename constants for display name, distribution name, preferred command, compatibility command, repository URL, preferred config prefix, and legacy config prefix in src/auth_entry_portal/config.py
- [X] T002 [P] Add old-name token inventory fixture and allowed-classification schema in tests/fixtures/rename_inventory.py
- [X] T003 [P] Add rename scan helper for source/docs/artifact text classification in tests/rename_helpers.py
- [X] T004 [P] Add release artifact filename and metadata expectation constants for auth-ingress in scripts/release/package_metadata.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core compatibility and validation infrastructure that MUST be complete before user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Add AUTH_INGRESS_* environment-variable lookup with AUTH_PORTAL_* fallback and new-prefix precedence in src/auth_entry_portal/config.py
- [X] T006 [P] Add configuration prefix precedence and fallback unit tests in tests/unit/test_config_rename.py
- [X] T007 [P] Add old-name scan contract tests with required classifications in tests/contract/test_rename_inventory_contract.py
- [X] T008 Add preferred and compatibility console-script metadata to pyproject.toml
- [X] T009 [P] Update installed-package smoke helpers to invoke both auth-ingress and auth-portal in tests/smoke/test_installed_package.py
- [X] T010 [P] Add CLI alias security parity tests for privileged users commands in tests/security/test_cli_rename_security.py
- [X] T011 Add release validation support for auth-ingress metadata and compatibility command checks in scripts/release/check_artifacts.py and scripts/release/build_and_check.py
- [X] T012 [P] Add release validation unit tests for renamed artifacts and aliases in tests/unit/test_release_validation.py

**Checkpoint**: Rename constants, config aliases, CLI metadata, and scan validation are ready for story work.

---

## Phase 3: User Story 1 - Operators see one consistent product name (Priority: P1) 🎯 MVP

**Goal**: Current install, command, startup, documentation, and web UI surfaces show `auth-ingress` as the primary identity.

**Independent Test**: From a fresh checkout, inspect command help, README install/startup instructions, setup guidance, and primary UI pages; all current primary surfaces show `auth-ingress`.

### Tests for User Story 1

- [X] T013 [P] [US1] Add documentation naming contract test for README and docs current instructions in tests/contract/test_rename_docs_contract.py
- [X] T014 [P] [US1] Add CLI preferred-command contract test for auth-ingress help and subcommands in tests/contract/test_rename_cli_contract.py
- [X] T015 [P] [US1] Add browser/UI identity assertions for base header, page titles, setup guidance, and admin pages in tests/e2e/test_rename_identity.py
- [X] T016 [P] [US1] Add old-primary-label absence checks for current UI templates in tests/contract/test_rename_ui_contract.py

### Implementation for User Story 1

- [X] T017 [US1] Rename package metadata, project URLs, keywords, and preferred script entry point to auth-ingress in pyproject.toml
- [X] T018 [US1] Update README install, startup, first-install, demo, user-management, proxy, and configuration examples to auth-ingress and AUTH_INGRESS_* in README.md
- [X] T019 [P] [US1] Update user-management and release operator docs to use auth-ingress primary naming in docs/user-management.md and docs/releasing.md
- [X] T020 [P] [US1] Update release recovery and GitHub release setup docs to use zondatw/auth-ingress and auth-ingress in docs/release-recovery.md and .github/RELEASE_SETUP.md
- [X] T021 [US1] Rename web UI product labels and page titles to auth-ingress in src/auth_entry_portal/web/templates/base.html
- [X] T022 [P] [US1] Rename auth page titles, setup command examples, and recovery page labels to auth-ingress in src/auth_entry_portal/web/templates/auth/sign_in.html, src/auth_entry_portal/web/templates/auth/setup_required.html, src/auth_entry_portal/web/templates/auth/reset_password.html, and src/auth_entry_portal/web/templates/auth/change_password.html
- [X] T023 [P] [US1] Rename portal/admin/error page titles to auth-ingress in src/auth_entry_portal/web/templates/portal/index.html, src/auth_entry_portal/web/templates/admin/services.html, src/auth_entry_portal/web/templates/admin/users.html, src/auth_entry_portal/web/templates/admin/user_detail.html, src/auth_entry_portal/web/templates/admin/audit.html, and src/auth_entry_portal/web/templates/errors/access_denied.html
- [X] T024 [US1] Update CLI parser program name and help epilog to prefer auth-ingress while mentioning auth-portal compatibility in src/auth_entry_portal/cli.py
- [X] T025 [US1] Update tests and helper command invocations from auth-portal to auth-ingress where they represent current primary usage in tests/cli_helpers.py, tests/e2e/test_first_install.py, specs/004-manage-user-access/quickstart.md, and specs/004-manage-user-access/contracts/ui-flows.md

**Checkpoint**: User Story 1 is independently functional; primary operator and UI surfaces consistently show auth-ingress.

---

## Phase 4: User Story 2 - Existing deployments have a safe migration path (Priority: P2)

**Goal**: Old command, configuration, repository, and historical naming references have documented compatibility behavior and do not break security.

**Independent Test**: Run existing automation through old CLI/config names and verify it still works or gives documented remediation while maintaining the same security behavior.

### Tests for User Story 2

- [X] T026 [P] [US2] Add compatibility CLI smoke tests for auth-portal help, init-db, and users command denial behavior in tests/integration/test_cli_rename_compatibility.py
- [X] T027 [P] [US2] Add old/new environment prefix migration tests covering precedence and fallback in tests/integration/test_config_rename_compatibility.py
- [X] T028 [P] [US2] Add migration documentation contract tests for old-to-new mapping coverage in tests/contract/test_rename_migration_contract.py
- [X] T029 [P] [US2] Add historical reference classification security test ensuring old audit/log names are documented and non-sensitive in tests/security/test_rename_history_security.py

### Implementation for User Story 2

- [X] T030 [US2] Implement auth-portal compatibility command behavior through project script metadata and shared CLI entry in pyproject.toml and src/auth_entry_portal/cli.py
- [X] T031 [US2] Add compatibility help text and migration notice for old CLI usage in src/auth_entry_portal/cli.py
- [X] T032 [US2] Implement configuration lookup helper that supports AUTH_INGRESS_* preferred keys and AUTH_PORTAL_* legacy keys without logging secret values in src/auth_entry_portal/config.py
- [X] T033 [US2] Document CLI, package, repository, configuration, import namespace, cookie/internal-label, and historical-reference migration mapping in README.md
- [X] T034 [P] [US2] Add compatibility notes for SRE/Admin workflows in docs/user-management.md
- [X] T035 [P] [US2] Add release and rollback migration notes for old package/repository names in docs/releasing.md and docs/release-recovery.md
- [X] T036 [US2] Classify intentional old-name references in test fixtures, security-stable cookie/token labels, historical specs, and compatibility docs using tests/fixtures/rename_inventory.py
- [X] T037 [US2] Update GitHub workflow URLs, release environment URLs, and release setup references to the canonical auth-ingress repository and distribution in .github/workflows/ci.yml, .github/workflows/release.yml, and .github/RELEASE_SETUP.md

**Checkpoint**: User Story 2 is independently functional; old operational names have safe compatibility or explicit migration guidance.

---

## Phase 5: User Story 3 - Published artifacts use the new identity (Priority: P3)

**Goal**: Built artifacts, package metadata, repository links, and release validation use the auth-ingress identity and prove installability.

**Independent Test**: Build wheel/source artifacts, inspect metadata and filenames, install artifacts in isolation, and verify auth-ingress help/init-db works.

### Tests for User Story 3

- [X] T038 [P] [US3] Add package metadata contract test for auth-ingress distribution, URLs, scripts, and import namespace in tests/contract/test_package_contract.py
- [X] T039 [P] [US3] Add artifact filename/content tests for auth_ingress wheel and sdist names in tests/unit/test_release_validation.py
- [X] T040 [P] [US3] Add staged index verification tests for auth-ingress exact package name and canonical URLs in tests/unit/test_index_verification.py
- [X] T041 [P] [US3] Add installed artifact smoke tests requiring auth-ingress help and init-db plus auth-portal compatibility help in tests/smoke/test_installed_package.py

### Implementation for User Story 3

- [X] T042 [US3] Update release metadata constants to auth-ingress distribution and zondatw/auth-ingress repository in scripts/release/package_metadata.py
- [X] T043 [US3] Update artifact prefix checks, content scans, and installed command expectations for auth_ingress artifacts in scripts/release/check_artifacts.py
- [X] T044 [US3] Update isolated build smoke command to reinstall auth-ingress and validate both command names in scripts/release/build_and_check.py
- [X] T045 [US3] Update PyPI/TestPyPI verification endpoints, staged-release package specs, and integrity URLs to auth-ingress in scripts/release/verify_index.py and scripts/release/verify_staged_release.py
- [X] T046 [US3] Update release workflow artifact names, TestPyPI/PyPI project URLs, and trusted-publisher documentation to auth-ingress in .github/workflows/release.yml and .github/RELEASE_SETUP.md
- [X] T047 [US3] Update release contracts and historical publish docs for the new artifact identity in specs/003-publish-pypi/contracts/package-distribution.md, specs/003-publish-pypi/contracts/release-operations.md, specs/003-publish-pypi/quickstart.md, and specs/003-publish-pypi/tasks.md
- [X] T048 [US3] Recheck PyPI and TestPyPI exact auth-ingress availability and record timestamped results in specs/005-rename-auth-ingress/quickstart.md
- [X] T049 [US3] Build wheel/source artifacts and update validation hash/evidence records in specs/005-rename-auth-ingress/quickstart.md

**Checkpoint**: User Story 3 is independently functional; release artifacts and release validation use auth-ingress.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, classification, and documentation consistency across all rename stories.

- [X] T050 [P] Add comprehensive old-name scan report test over source, docs, tests, workflows, scripts, and built artifacts in tests/security/test_rename_evidence.py
- [X] T051 Run old-name scan and record every remaining compatibility, historical, security-stable, or intentional exception in specs/005-rename-auth-ingress/quickstart.md
- [X] T052 Run full regression suite with coverage and record results in specs/005-rename-auth-ingress/quickstart.md
- [X] T053 Run Python 3.12, 3.13, and 3.14 non-browser validation matrix and record results in specs/005-rename-auth-ingress/quickstart.md
- [X] T054 Run browser identity checks for sign-in, setup, portal home, admin users/services/audit, reset/change-password, and access-denied pages and record results in specs/005-rename-auth-ingress/quickstart.md
- [X] T055 Run release build/check workflow and installed artifact smoke checks, then record artifact hashes and command validation in specs/005-rename-auth-ingress/quickstart.md
- [X] T056 Verify all FR-001–FR-010, SPR-001–SPR-005, SC-001–SC-005, and all contracts have passing evidence and record the mapping in specs/005-rename-auth-ingress/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational; can proceed in parallel with US1 after shared constants/config foundations exist, but final docs should align with US1 naming.
- **User Story 3 (Phase 5)**: Depends on Foundational and benefits from US1/US2 docs and metadata decisions.
- **Polish (Phase 6)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Operators see one consistent product name. Requires Setup + Foundation only.
- **US2 (P2)**: Existing deployments have safe migration. Requires Setup + Foundation; integrates with US1 documentation.
- **US3 (P3)**: Published artifacts use new identity. Requires Setup + Foundation; should be finalized after US1/US2 naming and compatibility decisions.

### Within Each User Story

- Tests first for rename, compatibility, and security-sensitive behavior.
- Documentation and UI updates before final old-name scan classification.
- Release metadata updates before artifact builds.
- Quickstart evidence updates after validation commands pass.

### Parallel Opportunities

- T002–T004 can run in parallel.
- T006, T007, T009, T010, and T012 can run in parallel after T001.
- US1 tests T013–T016 can run in parallel.
- US1 template/doc batches T019, T022, and T023 can run in parallel after naming constants are defined.
- US2 tests T026–T029 can run in parallel.
- US2 docs T034 and T035 can run in parallel with compatibility implementation.
- US3 tests T038–T041 can run in parallel.
- Polish evidence tests and validation record preparation can be split after implementation stabilizes.

---

## Parallel Example: User Story 1

```text
Task: "Add documentation naming contract test for README and docs current instructions in tests/contract/test_rename_docs_contract.py"
Task: "Add CLI preferred-command contract test for auth-ingress help and subcommands in tests/contract/test_rename_cli_contract.py"
Task: "Add browser/UI identity assertions for base header, page titles, setup guidance, and admin pages in tests/e2e/test_rename_identity.py"
Task: "Add old-primary-label absence checks for current UI templates in tests/contract/test_rename_ui_contract.py"
```

## Parallel Example: User Story 2

```text
Task: "Add compatibility CLI smoke tests for auth-portal help, init-db, and users command denial behavior in tests/integration/test_cli_rename_compatibility.py"
Task: "Add old/new environment prefix migration tests covering precedence and fallback in tests/integration/test_config_rename_compatibility.py"
Task: "Add migration documentation contract tests for old-to-new mapping coverage in tests/contract/test_rename_migration_contract.py"
Task: "Add historical reference classification security test ensuring old audit/log names are documented and non-sensitive in tests/security/test_rename_history_security.py"
```

## Parallel Example: User Story 3

```text
Task: "Add package metadata contract test for auth-ingress distribution, URLs, scripts, and import namespace in tests/contract/test_package_contract.py"
Task: "Add artifact filename/content tests for auth_ingress wheel and sdist names in tests/unit/test_release_validation.py"
Task: "Add staged index verification tests for auth-ingress exact package name and canonical URLs in tests/unit/test_index_verification.py"
Task: "Add installed artifact smoke tests requiring auth-ingress help and init-db plus auth-portal compatibility help in tests/smoke/test_installed_package.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: US1 primary identity rename.
4. Stop and validate: CLI preferred command, README/docs, UI page labels, and setup guidance show `auth-ingress`.

### Incremental Delivery

1. Setup + Foundation → constants, config aliases, CLI metadata, scan harness ready.
2. US1 → preferred current identity visible everywhere operators use the product.
3. US2 → compatibility and migration safety for existing deployments.
4. US3 → package/release artifacts and publication checks.
5. Polish → old-name classification, full regression matrix, artifact hashes, and evidence mapping.

### Parallel Team Strategy

With multiple developers after Foundation:

1. Developer A: US1 docs/UI/CLI primary naming.
2. Developer B: US2 compatibility config/CLI migration behavior.
3. Developer C: US3 release metadata/artifact validation.
4. Coordinate through the old-name scan inventory so remaining legacy strings are consistently classified.

## Notes

- [P] tasks = different files, no dependencies.
- [US1], [US2], [US3] map to prioritized stories in spec.md.
- Keep `auth_entry_portal` import namespace stable unless a later explicit task changes the plan.
- Keep credentials, tokens, sessions, reset secrets, and unnecessary personal data out of logs, docs, tests, and release output.
- Do not rewrite historical audit records or security-stable token/cookie labels without a documented migration decision.
