# Tasks: Branch Publish Flow

**Input**: Design documents from `/specs/006-branch-publish-flow/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included because this feature controls package publication, OIDC trust boundaries, release evidence, and secret redaction.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish shared release-target constants and fixtures used by all branch-publishing stories.

- [ ] T001 Add release target constants for beta/TestPyPI and release/PyPI in scripts/release/package_metadata.py
- [ ] T002 [P] Add branch publish policy fixture helpers for allowed and denied branches in tests/release_helpers.py
- [ ] T003 [P] Add package-index duplicate-version fixture helpers for TestPyPI and PyPI cases in tests/release_helpers.py
- [ ] T004 [P] Add branch publish flow contract references to docs/releasing.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add reusable release validation support that all branch-specific publishing paths depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T005 Extend ReleaseContext with target branch and intended package index fields in scripts/release/validate_release.py
- [ ] T006 Implement exact branch-to-index policy resolution with safe reason codes in scripts/release/validate_release.py
- [ ] T007 Add target-index duplicate-version preflight interface in scripts/release/verify_index.py
- [ ] T008 [P] Add unit tests for branch-to-index policy resolution in tests/unit/test_release_validation.py
- [ ] T009 [P] Add unit tests for duplicate-version preflight outcomes in tests/unit/test_index_verification.py
- [ ] T010 [P] Update release workflow contract tests to parse branch conditions in tests/contract/test_github_workflows.py
- [ ] T011 [P] Update release workflow security tests for branch-conditioned OIDC jobs in tests/security/test_release_workflow_security.py

**Checkpoint**: Shared validation can identify the release target, reject unsupported branches, and detect existing target-index versions before any upload.

---

## Phase 3: User Story 1 - Stage releases from beta branch (Priority: P1) 🎯 MVP

**Goal**: Publishing from `beta` sends the current package version only to TestPyPI and blocks every non-beta staging attempt before upload.

**Independent Test**: Simulate a release targeting `beta` and verify TestPyPI validation/publish jobs are active while PyPI jobs are inactive; simulate non-beta staging attempts and verify safe rejection before upload.

### Tests for User Story 1

- [ ] T012 [P] [US1] Add branch policy contract tests for beta-to-TestPyPI and non-beta staging denial in tests/contract/test_branch_publish_policy.py
- [ ] T013 [P] [US1] Add workflow contract tests proving TestPyPI publish and verify jobs run only for beta in tests/contract/test_github_workflows.py
- [ ] T014 [P] [US1] Add security tests proving beta flow does not activate PyPI OIDC permission in tests/security/test_release_workflow_security.py
- [ ] T015 [P] [US1] Add duplicate TestPyPI version denial tests in tests/unit/test_index_verification.py

### Implementation for User Story 1

- [ ] T016 [US1] Update release validation to accept beta as TestPyPI target and reject non-beta TestPyPI attempts in scripts/release/validate_release.py
- [ ] T017 [US1] Update release workflow TestPyPI publish and verify jobs with beta-only conditions in .github/workflows/release.yml
- [ ] T018 [US1] Add TestPyPI duplicate-version preflight before TestPyPI upload in .github/workflows/release.yml
- [ ] T019 [US1] Ensure TestPyPI verification records beta branch, target index, version, artifact names, and hashes in scripts/release/verify_staged_release.py
- [ ] T020 [US1] Document beta branch staging release flow, blocked-branch handling, and retry rules in docs/releasing.md

**Checkpoint**: User Story 1 is independently functional; beta branch can stage to TestPyPI only and wrong-branch staging is blocked before upload.

---

## Phase 4: User Story 2 - Publish production releases from release branch (Priority: P2)

**Goal**: Publishing from `release` sends the current package version to PyPI only after branch, version, metadata, and integrity checks pass.

**Independent Test**: Simulate a release targeting `release` and verify PyPI validation/publish jobs are active while TestPyPI jobs are inactive; simulate non-release production attempts and verify safe rejection before upload.

### Tests for User Story 2

- [ ] T021 [P] [US2] Add branch policy contract tests for release-to-PyPI and non-release production denial in tests/contract/test_branch_publish_policy.py
- [ ] T022 [P] [US2] Add workflow contract tests proving PyPI publish and verify jobs run only for release in tests/contract/test_github_workflows.py
- [ ] T023 [P] [US2] Add security tests proving release flow does not activate TestPyPI OIDC permission in tests/security/test_release_workflow_security.py
- [ ] T024 [P] [US2] Add duplicate PyPI version denial tests in tests/unit/test_index_verification.py

### Implementation for User Story 2

- [ ] T025 [US2] Update release validation to accept release as PyPI target and reject non-release PyPI attempts in scripts/release/validate_release.py
- [ ] T026 [US2] Update release workflow PyPI publish and verify jobs with release-only conditions in .github/workflows/release.yml
- [ ] T027 [US2] Add PyPI duplicate-version preflight before PyPI upload in .github/workflows/release.yml
- [ ] T028 [US2] Ensure PyPI verification records release branch, target index, version, artifact names, hashes, and provenance status in scripts/release/verify_index.py
- [ ] T029 [US2] Document release branch production release flow, blocked-branch handling, and retry rules in docs/releasing.md

**Checkpoint**: User Story 2 is independently functional; release branch can publish to PyPI only and wrong-branch production attempts are blocked before upload.

---

## Phase 5: User Story 3 - Preserve clear release evidence (Priority: P3)

**Goal**: Release evidence clearly shows branch, target index, version, artifacts, hashes, verification status, final outcome, and safe failure reasons.

**Independent Test**: Review successful and rejected release simulations and confirm evidence is complete, non-sensitive, retained, and understandable in under five minutes.

### Tests for User Story 3

- [ ] T030 [P] [US3] Add release evidence contract tests for required branch/index/version/hash fields in tests/contract/test_release_operations_contract.py
- [ ] T031 [P] [US3] Add release evidence redaction tests for docs and workflow summaries in tests/security/test_release_workflow_security.py
- [ ] T032 [P] [US3] Add blocked and ambiguous release evidence reason-code tests in tests/unit/test_release_validation.py

### Implementation for User Story 3

- [ ] T033 [US3] Add non-sensitive release target summary output to scripts/release/validate_release.py
- [ ] T034 [US3] Add safe branch/index/version/hash evidence output to scripts/release/verify_staged_release.py
- [ ] T035 [US3] Add safe branch/index/version/hash/provenance evidence output to scripts/release/verify_index.py
- [ ] T036 [US3] Update release workflow summaries to include branch, target index, version, artifacts, hashes, verification result, and final outcome in .github/workflows/release.yml
- [ ] T037 [US3] Update recovery guidance for duplicate, blocked, and ambiguous branch-publish attempts in docs/release-recovery.md
- [ ] T038 [US3] Update feature quickstart validation evidence placeholders in specs/006-branch-publish-flow/quickstart.md

**Checkpoint**: User Story 3 is independently functional; operators can audit staging, production, blocked, and ambiguous release outcomes without secret exposure.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation consistency, and release safety checks across all stories.

- [ ] T039 [P] Update .github/RELEASE_SETUP.md with beta/TestPyPI and release/PyPI branch-to-environment setup requirements
- [ ] T040 [P] Update specs/003-publish-pypi release docs to reflect branch-specific publishing in specs/003-publish-pypi/quickstart.md
- [ ] T041 Run release validation focused tests and record results in specs/006-branch-publish-flow/quickstart.md
- [ ] T042 Run workflow contract and release security tests and record results in specs/006-branch-publish-flow/quickstart.md
- [ ] T043 Run full regression suite with uv run pytest -q and record results in specs/006-branch-publish-flow/quickstart.md
- [ ] T044 Run uv run python -m scripts.release.build_and_check and record artifact hash evidence in specs/006-branch-publish-flow/quickstart.md
- [ ] T045 Verify FR-001–FR-010, SPR-001–SPR-005, SC-001–SC-005, and all contracts have passing evidence in specs/006-branch-publish-flow/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundation; MVP staging flow.
- **User Story 2 (Phase 4)**: Depends on Foundation; can proceed in parallel with US1 after branch policy foundations exist.
- **User Story 3 (Phase 5)**: Depends on Foundation and integrates with US1/US2 evidence outputs.
- **Polish (Phase 6)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Beta-to-TestPyPI staging. Requires Setup + Foundation only.
- **US2 (P2)**: Release-to-PyPI production. Requires Setup + Foundation only.
- **US3 (P3)**: Release evidence. Requires shared evidence outputs from Foundation and benefits from US1/US2 publish paths.

### Within Each User Story

- Tests first for branch policy, workflow structure, duplicate-version denial, and secret redaction.
- Release validator changes before workflow publish job changes.
- Workflow publish job changes before verification/evidence output changes.
- Documentation and recovery guidance after behavior is defined.

### Parallel Opportunities

- T002–T004 can run in parallel.
- T008–T011 can run in parallel after T005–T007 interfaces are understood.
- US1 tests T012–T015 can run in parallel.
- US2 tests T021–T024 can run in parallel.
- US3 tests T030–T032 can run in parallel.
- US1 and US2 implementation can proceed in parallel after Foundation, with coordination on .github/workflows/release.yml.
- Polish documentation tasks T039–T040 can run in parallel.

---

## Parallel Example: User Story 1

```text
Task: "Add branch policy contract tests for beta-to-TestPyPI and non-beta staging denial in tests/contract/test_branch_publish_policy.py"
Task: "Add workflow contract tests proving TestPyPI publish and verify jobs run only for beta in tests/contract/test_github_workflows.py"
Task: "Add security tests proving beta flow does not activate PyPI OIDC permission in tests/security/test_release_workflow_security.py"
Task: "Add duplicate TestPyPI version denial tests in tests/unit/test_index_verification.py"
```

## Parallel Example: User Story 2

```text
Task: "Add branch policy contract tests for release-to-PyPI and non-release production denial in tests/contract/test_branch_publish_policy.py"
Task: "Add workflow contract tests proving PyPI publish and verify jobs run only for release in tests/contract/test_github_workflows.py"
Task: "Add security tests proving release flow does not activate TestPyPI OIDC permission in tests/security/test_release_workflow_security.py"
Task: "Add duplicate PyPI version denial tests in tests/unit/test_index_verification.py"
```

## Parallel Example: User Story 3

```text
Task: "Add release evidence contract tests for required branch/index/version/hash fields in tests/contract/test_release_operations_contract.py"
Task: "Add release evidence redaction tests for docs and workflow summaries in tests/security/test_release_workflow_security.py"
Task: "Add blocked and ambiguous release evidence reason-code tests in tests/unit/test_release_validation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: US1 beta-to-TestPyPI staging.
4. Stop and validate: beta releases can publish only to TestPyPI and wrong-branch staging attempts are denied.

### Incremental Delivery

1. Setup + Foundation → branch target classification, duplicate preflight, and workflow-test scaffolding.
2. US1 → beta branch staging to TestPyPI only.
3. US2 → release branch production to PyPI only.
4. US3 → complete release evidence and recovery guidance.
5. Polish → full regression, build/check, and evidence mapping.

### Parallel Team Strategy

With multiple developers after Foundation:

1. Developer A: US1 beta/TestPyPI branch policy and workflow conditions.
2. Developer B: US2 release/PyPI branch policy and workflow conditions.
3. Developer C: US3 release evidence, docs, and redaction validation.
4. Coordinate changes to .github/workflows/release.yml to avoid conflicting edits.

## Notes

- [P] tasks = different files, no dependencies.
- [US1], [US2], [US3] map to prioritized stories in spec.md.
- Keep OIDC permission job-scoped and absent at workflow scope.
- Keep publish jobs free of checkout and arbitrary run steps.
- Never enable skip-existing or overwrite an uploaded package file.
- Keep credentials, tokens, sessions, application secrets, database content, and unnecessary personal data out of release logs and evidence.
