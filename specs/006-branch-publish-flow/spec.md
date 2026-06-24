# Feature Specification: Branch Publish Flow

**Feature Branch**: `006-branch-publish-flow`

**Created**: 2026-06-24

**Status**: Draft

**Input**: User description: "modify CICD flow, beta branch: testpypi, release branch: pypi"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stage releases from beta branch (Priority: P1)

As a release maintainer, I want publishing from the `beta` branch to send the
current package version only to the staging package index so that release
candidates can be validated without making them publicly production-ready.

**Why this priority**: Staging is the safest first step. It lets maintainers
verify package metadata, installability, provenance, and evidence before any
production publication is possible.

**Independent Test**: Can be tested by preparing a release candidate on the
`beta` branch and confirming that the package is available on TestPyPI, is not
available on PyPI, and has matching validation evidence.

**Acceptance Scenarios**:

1. **Given** a maintainer publishes from the `beta` branch, **When** the release
   workflow completes successfully, **Then** the package version appears on
   TestPyPI and no PyPI publication occurs.
2. **Given** a maintainer publishes from any branch other than `beta` for a
   staging release, **When** the workflow evaluates the request, **Then** the
   staging publication is rejected with a clear branch-policy reason.
3. **Given** the package version already exists on TestPyPI, **When** a
   maintainer attempts to stage the same version again, **Then** the workflow
   stops before upload and reports that a new version is required.

---

### User Story 2 - Publish production releases from release branch (Priority: P2)

As a release maintainer, I want publishing from the `release` branch to send the
current package version to the production package index so that public users
install only explicitly approved release builds.

**Why this priority**: Production publication is high-impact and must be tied to
an explicit release branch, separate from development and staging activity.

**Independent Test**: Can be tested by preparing a production release on the
`release` branch and confirming that the package is published to PyPI only when
the branch policy, version policy, and release evidence all pass.

**Acceptance Scenarios**:

1. **Given** a maintainer publishes from the `release` branch, **When** all
   release checks pass, **Then** the package version appears on PyPI with the
   expected public identity and integrity evidence.
2. **Given** a maintainer attempts production publication from any branch other
   than `release`, **When** the workflow evaluates the request, **Then** PyPI
   publication is rejected before any upload.
3. **Given** the package version already exists on PyPI, **When** a maintainer
   attempts to publish the same version again, **Then** the workflow stops and
   instructs the maintainer to prepare a new version.

---

### User Story 3 - Preserve clear release evidence (Priority: P3)

As an SRE or administrator, I want branch-based release outcomes to be easy to
audit so that I can determine which branch produced a staged or production
package and whether the package was verified.

**Why this priority**: Release traceability reduces incident-response time and
prevents confusion between staging packages and production packages.

**Independent Test**: Can be tested by reviewing the release evidence for both
branches and confirming that each outcome records branch, version, target index,
artifact names, integrity hashes, verification status, and failure reason when
applicable.

**Acceptance Scenarios**:

1. **Given** a staging publication succeeds, **When** an operator reviews release
   evidence, **Then** the evidence identifies `beta`, TestPyPI, package version,
   artifact names, integrity hashes, and verification status.
2. **Given** a production publication succeeds, **When** an operator reviews
   release evidence, **Then** the evidence identifies `release`, PyPI, package
   version, artifact names, integrity hashes, and verification status.
3. **Given** a release is rejected, **When** an operator reviews release
   evidence, **Then** the evidence identifies the policy that blocked the
   release without exposing credentials or package-index secrets.

### Edge Cases

- A release request is created from a feature, main, hotfix, or local branch.
- A version exists on one package index but not the other.
- A beta/staging package is approved, but production release is attempted from
  the wrong branch.
- A production version is attempted before staging verification has completed.
- Branch names are similar but not exact, such as `beta-fix`, `release-candidate`,
  or `releases`.
- Release evidence contains failure messages from package-index services.
- A publication upload is interrupted and the package-index state is ambiguous.
- A maintainer attempts to reuse the same version after a failed or partial
  publish.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST treat `beta` as the only branch authorized to
  publish package artifacts to TestPyPI.
- **FR-002**: The system MUST treat `release` as the only branch authorized to
  publish package artifacts to PyPI.
- **FR-003**: The system MUST prevent TestPyPI publication from any branch other
  than `beta`.
- **FR-004**: The system MUST prevent PyPI publication from any branch other than
  `release`.
- **FR-005**: The system MUST prevent a single release request from publishing to
  both TestPyPI and PyPI unless it explicitly satisfies the separate branch
  policy for each target.
- **FR-006**: The system MUST verify that the package name, version, public
  identity, and artifact integrity evidence match the intended target index
  before publication.
- **FR-007**: The system MUST stop before upload when the same package version
  already exists on the intended target index.
- **FR-008**: The system MUST provide clear failure reasons for branch-policy,
  version-exists, metadata, integrity, and verification failures.
- **FR-009**: The system MUST record release evidence for each publish attempt,
  including branch, target index, version, artifact names, integrity hashes,
  verification result, and final outcome.
- **FR-010**: Documentation MUST explain the branch-to-index mapping, expected
  release sequence, retry rules, and how maintainers should recover from blocked
  or ambiguous publication attempts.

### Security & Privacy Requirements *(mandatory for identity/access features)*

- **SPR-001**: Publication credentials, package-index tokens, identity-provider
  tokens, and maintainer credentials MUST NOT be stored in repository content,
  release notes, logs, artifacts, or documentation.
- **SPR-002**: Production publication MUST require an explicit production
  release decision and MUST NOT be reachable through staging-only branch flows.
- **SPR-003**: Rejected, ambiguous, duplicate, or unauthorized publish attempts
  MUST produce non-sensitive evidence sufficient for audit and troubleshooting.
- **SPR-004**: Logs and release evidence MUST NOT expose package-index secrets,
  authentication tokens, application secrets, session cookies, database content,
  or unnecessary personal data.
- **SPR-005**: Release evidence MUST be retained for at least 90 days.

### Key Entities *(include if feature involves data)*

- **Release Branch**: The source branch that authorizes a publication target.
  `beta` authorizes TestPyPI and `release` authorizes PyPI.
- **Target Index**: The package index that receives artifacts. TestPyPI is the
  staging target and PyPI is the production target.
- **Release Attempt**: One maintainer-initiated publication request with branch,
  version, target index, validation result, upload result, and final outcome.
- **Release Evidence**: Non-sensitive records proving what was built, where it
  was intended to publish, which checks ran, and whether publication succeeded.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successful `beta` branch publication attempts publish only
  to TestPyPI and never to PyPI.
- **SC-002**: 100% of successful `release` branch publication attempts publish to
  PyPI only after branch policy, version policy, metadata, and artifact integrity
  checks pass.
- **SC-003**: 100% of wrong-branch publication attempts are rejected before any
  package upload occurs.
- **SC-004**: A maintainer can identify the correct branch for staging and
  production publication in under 2 minutes using project documentation.
- **SC-005**: Each publish attempt leaves enough non-sensitive evidence for an
  operator to identify branch, target index, version, artifact names, integrity
  hashes, verification result, and final outcome in under 5 minutes.

## Assumptions

- The desired staging branch name is exactly `beta`.
- The desired production branch name is exactly `release`.
- TestPyPI is the staging package index and PyPI is the production package index.
- Existing package identity remains `auth-ingress` with the `auth_ingress`
  import namespace.
- Existing release evidence and package integrity expectations remain required.
- Reusing an already-published version is not allowed; maintainers must prepare a
  new version for every retry that would otherwise overwrite an uploaded file.
