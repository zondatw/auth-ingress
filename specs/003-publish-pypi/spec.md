# Feature Specification: Publish Auth Entry Portal to PyPI

**Feature Branch**: `003-publish-pypi`

**Created**: 2026-06-22

**Status**: Draft

**Input**: User description: "planning: Publish to pypi"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install a Trusted Public Release (Priority: P1)

An operator can find Auth Entry Portal on the public Python package index,
install a selected stable version in a clean supported environment, and invoke
its command-line entry point without cloning the source repository.

**Why this priority**: Public, repeatable installation is the primary value of
publishing the project as a package.

**Independent Test**: Install the published stable release into a clean
environment using only its public package name, invoke its help command, and
initialize a disposable portal database.

**Acceptance Scenarios**:

1. **Given** a clean environment using a supported Python version, **When** an
   operator installs the public package by name, **Then** the requested release
   and all required runtime dependencies install successfully.
2. **Given** the installed public package, **When** the operator invokes the
   documented command-line help and database initialization commands, **Then**
   both commands complete without requiring repository files.
3. **Given** a published release, **When** an operator reviews its public listing,
   **Then** the listing clearly identifies the project, supported Python versions,
   license, documentation, source, release version, and security contact path.

---

### User Story 2 - Publish an Approved Release Safely (Priority: P2)

A maintainer can turn an approved, uniquely versioned project release into a
public package through a repeatable release process that validates the exact
artifacts before publication.

**Why this priority**: A safe and repeatable maintainer flow prevents broken,
mutable, or accidental releases from reaching operators.

**Independent Test**: Run the documented release flow for a new version against
the staging package index, verify installation and smoke checks, then confirm
that only an explicitly approved release can proceed to public publication.

**Acceptance Scenarios**:

1. **Given** an approved version that has not been published, **When** the release
   process runs, **Then** it builds one source archive and one universal wheel,
   validates both, and publishes the unchanged artifacts.
2. **Given** a version that already exists, uncommitted release inputs, failing
   tests, invalid metadata, or a failed installation smoke check, **When** a
   maintainer attempts publication, **Then** publication is blocked with an
   actionable, non-sensitive explanation.
3. **Given** a candidate successfully published to the staging index, **When** it
   is installed and exercised in a clean environment, **Then** its package data,
   command-line entry point, and basic database initialization work before public
   approval is allowed.
4. **Given** the publishing integration is configured, **When** a maintainer
   follows a source link or reviews the publisher identity, **Then** both identify
   the canonical `zondatw/auth-entry-portal` repository.

---

### User Story 3 - Operate and Recover Releases (Priority: P3)

A maintainer can identify what was published, trace it to an approved source
release, communicate changes, and follow a documented recovery procedure when a
release is defective or compromised.

**Why this priority**: Public packages require durable traceability and a safe
response path after publication, because published versions cannot be silently
replaced.

**Independent Test**: Select a published version, verify its release notes and
source traceability, then rehearse the documented yank-and-replacement procedure
without deleting or overwriting the original version.

**Acceptance Scenarios**:

1. **Given** a public package version, **When** a maintainer or operator inspects
   it, **Then** they can determine the corresponding approved source release,
   artifact integrity information, and user-visible changes.
2. **Given** a defective release, **When** a maintainer follows the recovery
   procedure, **Then** new installations are steered away from that version,
   existing evidence remains available, and a corrected version uses a new
   version number.
3. **Given** a suspected publisher credential compromise, **When** the incident
   procedure is invoked, **Then** publication access can be revoked without
   changing application user credentials or runtime secrets.

### Edge Cases

- Publication is retried after an ambiguous network timeout and the target
  version may already exist.
- The package builds successfully but omits templates or other runtime resources.
- A dependency is available during development but is absent from declared
  runtime requirements.
- The project version, release identifier, artifact metadata, and public listing
  disagree.
- A release is created from a branch or revision that has not passed required
  checks.
- The staging index succeeds while the public index is unavailable or rejects
  the artifacts.
- A release needs urgent withdrawal after some operators have already installed
  it.
- A pre-release version is created and must not be presented as the default
  stable installation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST be published on the public Python package index
  under the unambiguous package name `auth-entry-portal`.
- **FR-002**: Every release MUST provide both a source archive and an installable
  wheel containing all code, templates, and other resources required at runtime.
- **FR-003**: The public listing MUST state the package name, unique version,
  purpose, supported Python versions, license, documentation link, source link,
  issue-reporting link, and security contact path.
- **FR-004**: Every runtime dependency required for installation and normal
  operation MUST be declared by the package; test and development dependencies
  MUST remain optional for operators.
- **FR-005**: The release process MUST validate tests, package metadata, artifact
  contents, artifact integrity, clean-environment installation, command-line
  invocation, and basic database initialization before public publication.
- **FR-006**: Maintainers MUST be able to publish and install an exact candidate
  through a staging package index before approving public publication.
- **FR-007**: Public publication MUST require an explicit, approved, uniquely
  versioned source release and MUST publish the same artifacts that passed
  candidate validation.
- **FR-008**: The release process MUST reject an existing version, mismatched
  version identifiers, unapproved source revision, dirty release inputs, invalid
  metadata, missing runtime resources, or any failed release check.
- **FR-009**: Stable and pre-release versions MUST be distinguishable, and a
  pre-release MUST NOT become the default stable installation.
- **FR-010**: Each public version MUST include release notes describing material
  user-visible changes, upgrade considerations, and known limitations.
- **FR-011**: Installation and upgrade documentation MUST cover supported
  environments, version pinning, verification, configuration prerequisites, and
  removal.
- **FR-012**: Maintainers MUST have a documented recovery process for yanking a
  defective release, revoking publication access, notifying operators, and
  issuing a corrected release with a new version.
- **FR-013**: Published versions MUST be immutable; the process MUST never delete
  and replace an artifact or reuse a previously published version number.
- **FR-014**: Publication failures MUST report whether no release occurred, the
  version already exists, or operator verification is required, without exposing
  credentials or internal secrets.
- **FR-015**: Release automation, package metadata, documentation, clone
  instructions, and Trusted Publisher bindings MUST use the canonical
  `zondatw/auth-entry-portal` repository identity.
- **FR-016**: The Python import namespace MUST be renamed from `auth_portal` to
  `auth_entry_portal` throughout the packaged source, tests, executable target,
  documentation, and declared package metadata.

### Security & Privacy Requirements

- **SPR-001**: Publication authority MUST be limited to approved maintainers and
  an approved release context; ordinary contributors and application operators
  MUST NOT receive publication authority.
- **SPR-002**: Publication MUST use package-scoped, revocable, short-lived or
  environment-bound authority rather than a reusable maintainer password or a
  broadly scoped long-lived credential.
- **SPR-003**: Every public artifact MUST have verifiable integrity information
  and traceability to the approved source release that produced it.
- **SPR-004**: Release output, public metadata, logs, artifacts, and diagnostic
  messages MUST NOT contain publisher credentials, application secrets,
  database contents, demo passwords, session material, or unnecessary personal
  data.
- **SPR-005**: Failed authorization, publication attempts, approvals, successful
  publications, yanks, and access revocations MUST remain auditable for at least
  90 days through the release and package-index records available to maintainers.
- **SPR-006**: A publisher-access compromise MUST be recoverable independently of
  application authentication data and deployed portal configuration.

### Key Entities

- **Package Release**: A uniquely versioned, immutable public release with status
  (candidate, stable, pre-release, or yanked), supported environments, release
  notes, approval, and a corresponding source release.
- **Release Artifact**: A source archive or wheel belonging to one package
  release, with type, filename, size, integrity information, validation result,
  and publication destination.
- **Release Approval**: Evidence that a specific version and exact artifact set
  passed required checks and was authorized for public publication by the
  permitted release context.
- **Publication Event**: A non-sensitive record of an attempted or completed
  candidate publication, public publication, yank, or access revocation and its
  outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An operator can install a selected stable release in a clean
  supported environment and complete the documented command-line and database
  smoke checks within 5 minutes, without accessing the source repository.
- **SC-002**: 100% of supported Python-version smoke checks install successfully
  from the built release artifacts and find all required runtime resources.
- **SC-003**: 100% of public releases have matching unique versions, complete
  required metadata, release notes, two validated artifact types, integrity
  information, and traceability to an approved source release.
- **SC-004**: 100% of simulated unauthorized, duplicate-version, dirty-input,
  invalid-artifact, and failed-validation publication attempts are blocked before
  a new public version is created.
- **SC-005**: A maintainer can complete the documented staging validation and
  public approval flow within 15 minutes, excluding package-index availability
  delays.
- **SC-006**: A maintainer can identify and begin the documented yank,
  notification, credential-revocation, and replacement-release response within
  15 minutes of confirming a defective or compromised release.
- **SC-007**: Validation of release logs and artifacts finds zero publisher
  credentials, application secrets, session data, database content, or demo
  passwords.

## Assumptions

- The public distribution name `auth-entry-portal` currently has no visible
  project or simple-index entry. Availability will be verified again immediately
  before registration, and publication will stop if PyPI rejects the name.
- Distribution names and Python import namespaces are distinct. The Python import
  namespace is renamed to `auth_entry_portal`; the `auth-portal` command and
  `AUTH_PORTAL_*` configuration keys remain unchanged.
- The GitHub repository is `zondatw/auth-entry-portal`. Existing local clones must
  update their `origin` URL; the local checkout directory does not need to be
  renamed for package correctness.
- The first public release retains the current `0.1.0` version unless that version
  is already occupied or release review requires a new version.
- The project is intended for public distribution rather than a private package
  index; private-index publication and container-image distribution are out of
  scope.
- The existing command-line interface is the supported package entry point, and
  publishing does not add a hosted portal service or deploy an operator's
  environment.
- Stable releases follow standard Python version semantics; release versions are
  never overwritten, and fixes use a new version.
- The source hosting and public package-index services provide maintainer-visible
  release and authorization records sufficient for the 90-day audit requirement.
- Legal approval of the chosen license, project name, and public content is an
  organizational prerequisite and is not automated by this feature.
