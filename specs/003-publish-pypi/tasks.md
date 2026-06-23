# Tasks: Publish auth-ingress to PyPI

**Input**: Design documents from `/specs/003-publish-pypi/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Package publication changes the software supply-chain trust boundary.
Contract, integration, smoke, and security tests are required before the matching
workflow and release implementation tasks.

**Organization**: Tasks are grouped by user story so package installation,
controlled publication, and release recovery can each be implemented and
validated as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes a different file and has no
  dependency on another incomplete task in the same phase.
- **[Story]**: Maps the task to US1, US2, or US3 from spec.md.
- Every task names the exact file or external setup record it changes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish release tooling, test structure, and dependency automation
without changing runtime behavior.

- [X] T001 Add explicit release-validation test dependencies for metadata and GitHub workflow parsing to pyproject.toml and refresh uv.lock
- [X] T002 [P] Configure weekly reviewed full-SHA GitHub Action update proposals in .github/dependabot.yml
- [X] T003 [P] Create the importable release-tool package scaffold in scripts/release/__init__.py
- [X] T004 [P] Create the isolated installed-package smoke-test package scaffold in tests/smoke/__init__.py
- [X] T005 [P] Add shared wheel, source-archive, version, and hash fixtures in tests/release_helpers.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Complete public metadata, artifact boundaries, and reusable release
validation primitives required by every user story.

**⚠️ CRITICAL**: No user story work begins until these package and trust-boundary
prerequisites are complete.

- [X] T006 Obtain and add the owner-approved license text in LICENSE and its SPDX expression/license-file declaration in pyproject.toml
- [X] T007 [P] Add Keep-a-Changelog-compatible initial release history and upgrade notes in CHANGELOG.md
- [X] T008 [P] Add vulnerability reporting, supported-version, disclosure, and release-compromise contacts in SECURITY.md
- [X] T009 Complete authors/maintainers, classifiers, keywords, `auth_entry_portal` import declaration, canonical zondatw/auth-ingress project URLs, and Hatch wheel/source inclusion rules in pyproject.toml
- [X] T010 Implement shared static package name, version, tag, release type, required metadata, and canonical repository validation in scripts/release/package_metadata.py
- [X] T011 Document and verify the renamed origin, default branch, required CI checks, protected environments, and no-token policy in .github/RELEASE_SETUP.md

**Checkpoint**: Public metadata and immutable artifact boundaries are defined;
story-specific package and workflow work can proceed.

---

## Phase 3: User Story 1 - Install a Trusted Public Release (Priority: P1) 🎯 MVP

**Goal**: Produce complete wheel and source artifacts that install and operate in
clean supported environments without access to repository files.

**Independent Test**: Build one wheel and one source archive, install each into an
isolated environment, import `auth_entry_portal`, invoke `auth-ingress --help`,
initialize a disposable database, and resolve every installed template/static
resource within five minutes.

### Tests for User Story 1

> Write these tests first and confirm they expose missing metadata, forbidden
> files, or absent runtime resources before completing the artifact implementation.

- [X] T012 [P] [US1] Add distribution/import/CLI/version/metadata and legacy `auth_portal` import-absence contract tests in tests/contract/test_package_contract.py
- [X] T013 [P] [US1] Add wheel/source filename, count, contents, exclusions, metadata, dependency, and hash integration tests in tests/integration/test_distribution_artifacts.py
- [X] T014 [P] [US1] Add isolated import, CLI help, disposable database, application startup, template, static resource, and five-minute checks in tests/smoke/test_installed_package.py

### Implementation for User Story 1

- [X] T015 [US1] Implement deterministic wheel/source discovery, SHA-256 manifest generation, required-content checks, forbidden-content checks, and metadata checks in scripts/release/check_artifacts.py
- [X] T016 [US1] Implement the clean build, metadata check, artifact inspection, and separate wheel/source smoke-test orchestration in scripts/release/build_and_check.py
- [X] T017 [US1] Add PyPI installation, exact version pinning, upgrade, configuration prerequisites, verification, and removal guidance using `auth_entry_portal` examples in README.md
- [X] T018 [US1] Execute the local artifact and installed-package scenarios and record filenames, hashes, durations, and outcomes in specs/003-publish-pypi/quickstart.md

**Checkpoint**: Both local distribution formats are independently installable and
complete. This is the MVP artifact slice even before automated public promotion.

---

## Phase 4: User Story 2 - Publish an Approved Release Safely (Priority: P2)

**Goal**: Test every pull request and publish an explicitly approved GitHub
Release through TestPyPI to PyPI with identical artifacts and least privilege.

**Independent Test**: Publish a uniquely versioned pre-release to TestPyPI, verify
the exact staged installation, reject the protected PyPI approval during the
rehearsal, and prove no pull-request/build/verification job has publication
authority.

### Tests for User Story 2

> Write these tests first and confirm unsafe triggers, permissions, unpinned
> actions, version mismatches, and failed gates are rejected before workflows are
> completed.

- [X] T019 [P] [US2] Add CI/release trigger, dependency graph, concurrency, immutable artifact handoff, environment, action-pin, and permission contract tests in tests/contract/test_github_workflows.py
- [X] T020 [P] [US2] Add package name, tag/version, release type, required metadata, dirty input, and missing approval validation tests in tests/unit/test_release_validation.py
- [X] T021 [P] [US2] Add tests proving pull-request/build/verification jobs lack OIDC, publish jobs execute no repository code, public duplicates fail, and workflow output excludes secrets in tests/security/test_release_workflow_security.py

### Implementation for User Story 2

- [X] T022 [US2] Implement GitHub Release event, tag/version, pre-release/stable, clean input, package metadata, and prerequisite gate validation in scripts/release/validate_release.py
- [X] T023 [US2] Add locked Python 3.12/3.13/3.14 tests, newest-version Chromium/coverage, and artifact build/smoke jobs with read-only permissions and full-SHA action pins in .github/workflows/ci.yml
- [X] T024 [US2] Add published-release validation and one-time no-OIDC build jobs that upload only the wheel, source archive, and hash manifest in .github/workflows/release.yml
- [X] T025 [US2] Add a separate `testpypi` environment job using job-scoped OIDC and one official PyPI action invocation in .github/workflows/release.yml
- [X] T026 [US2] Implement bounded TestPyPI propagation polling, exact-version isolated installation, dependency-index separation, and staged smoke validation in scripts/release/verify_staged_release.py
- [X] T027 [US2] Add the non-OIDC TestPyPI verification gate and protected `pypi` environment promotion of the unchanged hash-verified artifacts in .github/workflows/release.yml
- [X] T028 [US2] Document exact PyPI/TestPyPI pending-publisher claims, GitHub environment protections, required reviewers, tag restrictions, and prohibited token secrets in .github/RELEASE_SETUP.md
- [ ] T029 [US2] Configure the `testpypi` and `pypi` GitHub environments plus matching PyPI/TestPyPI Trusted Publishers and record non-sensitive configuration evidence in .github/RELEASE_SETUP.md
- [ ] T030 [US2] Run a staged pre-release rehearsal through TestPyPI, reject public approval, and record exact artifacts, hashes, job permissions, timing, and smoke outcomes in specs/003-publish-pypi/quickstart.md

**Checkpoint**: The safe release pipeline is independently demonstrated through
staging, and PyPI publication is possible only after protected approval.

---

## Phase 5: User Story 3 - Operate and Recover Releases (Priority: P3)

**Goal**: Verify published provenance and hashes, diagnose ambiguous failures,
yank defective versions, and revoke publisher access without overwriting history
or exposing application credentials.

**Independent Test**: Inspect a release's source revision, hashes, metadata, and
attestations, then rehearse duplicate/timeout diagnosis, yank-and-replacement, and
Trusted Publisher revocation using only documented non-sensitive evidence.

### Tests for User Story 3

> Write these tests first and confirm blind upload retry, mismatched hashes,
> unsafe deletion/reuse guidance, unbounded polling, and sensitive diagnostics are
> rejected.

- [X] T031 [P] [US3] Add absent/present/mismatched version, bounded retry, exact filename/hash, duplicate, and ambiguous timeout tests in tests/unit/test_index_verification.py
- [X] T032 [P] [US3] Add release runbook contract tests for immutable versions, yank reasons, new replacement versions, publisher revocation, notification, and 90-day evidence retention in tests/contract/test_release_operations_contract.py
- [X] T033 [P] [US3] Add diagnostic and workflow-summary redaction tests for OIDC/API tokens, application secrets, sessions, databases, demo passwords, and personal data in tests/security/test_release_redaction.py

### Implementation for User Story 3

- [X] T034 [US3] Implement read-only PyPI/TestPyPI version lookup, bounded propagation retry, exact artifact/hash comparison, and absent/completed/collision outcomes in scripts/release/verify_index.py
- [X] T035 [US3] Add read-only public metadata, hash, source revision, and attestation verification plus allowlisted workflow summaries in .github/workflows/release.yml
- [X] T036 [US3] Document normal versioning, GitHub Release publication, approval, verification, duplicate diagnosis, and immutable evidence procedures in docs/releasing.md
- [X] T037 [US3] Document defective-release yanking, operator notification, new-version replacement, workflow cancellation, Trusted Publisher revocation, investigation, and re-establishment in docs/release-recovery.md
- [X] T038 [US3] Rehearse failed validation, propagation timeout, duplicate, mismatched hash, rejected approval, yank, and publisher-revocation paths and record safe outcomes in specs/003-publish-pypi/quickstart.md
- [X] T039 [US3] Verify GitHub and package-index release, deployment, approval, hash, upload, yank, and revocation evidence retention for at least 90 days and record policy links in .github/RELEASE_SETUP.md

**Checkpoint**: Published releases are traceable and maintainers can begin a safe
defect or compromise response within the specified 15-minute target.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete release surface and remove cross-story gaps.

- [ ] T040 [P] Run actionlint and a GitHub Actions security scan, resolve all actionable findings, and record tool versions/results in specs/003-publish-pypi/quickstart.md
- [X] T041 [P] Scan wheel/source contents and workflow logs for credentials, databases, repository tooling, tests, caches, environment files, sessions, and demo passwords and record results in specs/003-publish-pypi/quickstart.md
- [X] T042 Verify every third-party action and uv reference is pinned to a reviewed immutable version and document update ownership in .github/RELEASE_SETUP.md
- [X] T043 Run the complete pytest suite with coverage plus clean wheel/source builds and isolated smoke tests on every supported Python version and record results in specs/003-publish-pypi/quickstart.md
- [ ] T044 Recheck `auth-ingress` availability, canonical repository/project links, license/security prerequisites, TestPyPI metadata, and trusted-publisher claims immediately before public registration in .github/RELEASE_SETUP.md
- [ ] T045 Execute the approved stable release, verify identical TestPyPI/PyPI artifacts and public provenance, and record the final release URL, version, hashes, timings, and outcomes in specs/003-publish-pypi/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; T002-T005 can proceed in parallel after
  T001 if they do not need the refreshed test environment.
- **Foundational (Phase 2)**: Depends on Setup and blocks every user story. T007
  and T008 can run in parallel; T009 follows T006-T008; T010 follows T009.
- **US1 (Phase 3)**: Depends on Foundation. Tests T012-T014 run first in parallel;
  T015 and T016 follow in order, while T017 can proceed after T009.
- **US2 (Phase 4)**: Depends on Foundation and consumes US1's validated artifact
  commands. Tests T019-T021 run first in parallel; T022 precedes workflow jobs;
  T024-T027 are sequential artifact promotion gates.
- **US3 (Phase 5)**: Depends on Foundation and can develop its tests/docs in
  parallel with US2, but T035 and live rehearsals require the US2 workflow.
- **Polish (Phase 6)**: Depends on all selected user stories. T045 is last and is
  the only task authorized to create the intended stable public release.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundation; no dependency on another story for local
  artifact validation.
- **US2 (P2)**: Starts after Foundation; reuses US1 artifact checks so the exact
  staged/public files have already passed operator installation criteria.
- **US3 (P3)**: Tests and runbooks start after Foundation; public workflow
  verification integrates with US2 after T027.

### Entity and Contract Mapping

- **Package Release**: T020, T022, T024-T030, T034-T035.
- **Release Artifact**: T013-T016, T019, T024-T027, T031, T034-T035.
- **Release Approval**: T019-T021, T027-T030, T035.
- **Publication Event**: T021, T031-T039.
- **Package distribution contract**: T012-T018.
- **CI workflow contract**: T019-T030.
- **Release operations contract**: T031-T039.

### Within Each User Story

- Story tests MUST be written and observed failing before their matching
  implementation tasks.
- Static metadata and reusable validators precede workflows.
- Build precedes staging; staging verification precedes public approval;
  public upload precedes read-only verification.
- Read-only retry is allowed; upload retry, version overwrite, and silent public
  duplicate skipping are prohibited.
- Each checkpoint must pass before starting the next priority for sequential MVP
  delivery.

## Parallel Opportunities

- T002-T005 modify independent setup files.
- T007 and T008 are independent public-document tasks.
- T012-T014 can be authored together before US1 implementation.
- T019-T021 can be authored together before CI/CD implementation.
- T031-T033 can be authored together before recovery implementation.
- US3 documentation T036-T037 can proceed while US2 workflow implementation is
  underway, but live US3 workflow validation waits for T027.
- Cross-cutting static workflow and artifact scans T040-T041 can run together.

## Parallel Example: User Story 1

```text
Task T012: Package identity and metadata contracts in tests/contract/test_package_contract.py
Task T013: Artifact content integration tests in tests/integration/test_distribution_artifacts.py
Task T014: Installed artifact smoke tests in tests/smoke/test_installed_package.py
```

## Parallel Example: User Story 2

```text
Task T019: Workflow structure contracts in tests/contract/test_github_workflows.py
Task T020: Release validation unit tests in tests/unit/test_release_validation.py
Task T021: Workflow authority/redaction tests in tests/security/test_release_workflow_security.py
```

## Parallel Example: User Story 3

```text
Task T031: Index outcome tests in tests/unit/test_index_verification.py
Task T032: Recovery runbook contracts in tests/contract/test_release_operations_contract.py
Task T033: Release diagnostic redaction tests in tests/security/test_release_redaction.py
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Setup and Foundation.
2. Write T012-T014 and confirm the current incomplete public package fails the
   new contracts where expected.
3. Complete T015-T018.
4. Stop and validate both artifact formats in clean environments.

This MVP proves the public package itself is usable without granting or invoking
publication authority.

### Incremental Delivery

1. **Foundation**: Public metadata, license, release primitives, and setup policy.
2. **US1**: Installable, self-contained wheel and source archive.
3. **US2**: Required CI plus staged and protected public promotion.
4. **US3**: Provenance verification, diagnosis, yank, and compromise recovery.
5. **Polish**: Security scans, full matrix, final availability check, then the
   explicitly approved stable release.

### Parallel Team Strategy

After Foundation:

- Developer A owns US1 package contracts and artifact tooling.
- Developer B starts US2 workflow contracts and release validation.
- Developer C starts US3 index tests and recovery documentation.
- Workflow integration and live index rehearsals merge in dependency order.

## Notes

- The GitHub repository is already renamed to `zondatw/auth-ingress`, the
  local origin is updated, and the `auth_entry_portal` import migration is already
  committed; tasks verify and package that baseline rather than repeat it.
- `[P]` tasks touch different files and have no incomplete same-phase dependency.
- Keep OIDC permission job-scoped and never execute repository code in publish
  jobs.
- Do not add PyPI API tokens as a fallback.
- Manual external setup/publication tasks require explicit maintainer approval and
  must record only non-sensitive evidence.
- Commit after each task or logical task group.
