# Feature Specification: Manage User Access

**Feature Branch**: `004-manage-user-access`

**Created**: 2026-06-22

**Status**: Draft

**Input**: User description: "Create the user management page and CLI so SRE and Admin operators can easily control access lists, including the first-time installation use case"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bootstrap the First Administrator (Priority: P1)

On a new installation with no identities, a trusted installer initializes the
portal and creates the first administrator through a local command-line flow.
The flow requires the installer to provide an explicit identity and a strong
credential through a non-disclosing input method. Once the first administrator
exists, the bootstrap operation can no longer create another account.

**Why this priority**: A new installation cannot use authenticated management
features until it has a trusted administrator, and shipping a default credential
would create an unacceptable takeover risk.

**Independent Test**: Start with a clean installation, run the documented
bootstrap flow, sign in as the created administrator, and verify that rerunning
bootstrap cannot create or modify any identity.

**Acceptance Scenarios**:

1. **Given** a clean installation with no identities, **When** a trusted installer supplies a valid unique identity and strong credential through the bootstrap command, **Then** the system atomically initializes required state and creates one active administrator.
2. **Given** a newly bootstrapped installation, **When** the first administrator signs in, **Then** they can open user management and begin creating users and assigning group memberships.
3. **Given** an installation that already contains any identity, **When** anyone reruns the bootstrap command, **Then** no account or privilege changes occur and the command returns a safe already-initialized outcome.
4. **Given** a clean installation, **When** a person visits the portal before bootstrap is complete, **Then** the portal explains that local administrator setup is required without offering public account creation or revealing environment details.
5. **Given** invalid, incomplete, or interrupted bootstrap input, **When** initialization fails, **Then** no partial administrator is left behind and the installer can safely retry with corrected input.

---

### User Story 2 - Control User Access (Priority: P2)

An authorized SRE or Admin finds a user, sees the user's status, group
memberships, and resulting service access, then adds or removes group memberships
from one management page. The operator sees the proposed access change before
confirming it and receives a clear success or denial outcome.

**Why this priority**: Group membership is the existing source of service access.
Making it visible and safely editable solves the primary operational need without
introducing a second access-control model.

**Independent Test**: Sign in as an authorized operator, select an existing user,
add and remove groups, and verify that the displayed effective service access and
actual authorization outcomes change accordingly.

**Acceptance Scenarios**:

1. **Given** an active user and an authorized operator, **When** the operator opens the user, **Then** the page shows identity details, account status, group memberships, effective services, and the reason each service is available.
2. **Given** an active user who is not in a selected group, **When** the operator reviews and confirms adding that membership, **Then** the user gains the services granted by that group and the outcome is audited.
3. **Given** a user who belongs to a selected group, **When** the operator reviews and confirms removing that membership, **Then** access granted only by that group is removed while access granted by other groups remains.
4. **Given** an unauthenticated or unauthorized person, **When** they attempt to view or change user access, **Then** the system denies the operation without revealing user or access-list data and records a safe denial event.

---

### User Story 3 - Manage User Lifecycle (Priority: P3)

An authorized SRE or Admin creates a user, updates non-credential profile fields,
disables or reactivates the account, and securely initiates a credential reset.
Disabled users immediately lose portal and protected-service access while their
identity and audit history remain available to operators.

**Why this priority**: Access-list changes are incomplete if operators cannot
onboard, suspend, or recover the users represented in those lists.

**Independent Test**: Create a user, update the profile, assign a group, disable
and reactivate the account, and verify the account's access and audit history at
each step.

**Acceptance Scenarios**:

1. **Given** a unique valid identity, **When** an authorized operator creates the user, **Then** the account is created in the intended initial state without displaying or logging credentials.
2. **Given** an active user, **When** an authorized operator disables the account, **Then** existing and new access attempts are denied promptly while memberships and audit history are preserved.
3. **Given** a disabled user, **When** an authorized operator reactivates the account, **Then** the user's retained group memberships again determine service access.
4. **Given** a request that would disable, demote, or remove access from the last active administrator, **When** the operator attempts to confirm it, **Then** the system rejects the change and explains the recovery-safe reason.

---

### User Story 4 - Automate Access Operations with the CLI (Priority: P4)

An authorized SRE or Admin performs the same common lookup, lifecycle, and group
membership operations through a command-line interface. The operator can preview
mutating commands, receive stable machine-readable outcomes, and safely repeat an
operation without creating duplicate memberships or ambiguous state.

**Why this priority**: A CLI supports incident response, repeatable operations,
and controlled automation while the management page remains the primary visual
workflow.

**Independent Test**: Use only CLI commands to list and inspect users, create or
disable a user, preview and apply membership changes, and verify exit outcomes,
effective access, and audit events.

**Acceptance Scenarios**:

1. **Given** valid operator authorization, **When** the operator lists or inspects users through the CLI, **Then** the result matches the management page and excludes credential or session data.
2. **Given** a valid membership change, **When** the operator runs it in preview mode, **Then** the CLI reports the expected additions, removals, and effective-access changes without modifying state.
3. **Given** a confirmed mutating command, **When** it succeeds, **Then** the CLI returns a stable success outcome and the page immediately reflects the same state.
4. **Given** an already-satisfied membership request, **When** the command is repeated, **Then** it reports no change rather than creating a duplicate or failing ambiguously.
5. **Given** invalid input, insufficient authorization, or a lockout-risk operation, **When** the command runs, **Then** it makes no partial change and returns a distinct non-success outcome with a safe explanation.

### Edge Cases

- Two operators update the same user's memberships at nearly the same time; a
  stale view must not silently overwrite the newer access list.
- A group is removed or disabled between preview and confirmation; the operation
  must stop and show the current state.
- A user's email or identifier differs only by case or surrounding whitespace;
  uniqueness rules must prevent confusing duplicate identities.
- A user belongs to multiple groups that grant the same service; removing one
  membership must not incorrectly remove access granted by another.
- A disabled user retains memberships; effective-access displays must clearly
  distinguish retained policy from currently usable access.
- Search returns no users or a large result set; the operator receives a clear
  empty state and bounded, navigable results.
- A CLI process is interrupted during a requested change; the change is either
  complete or absent, never partially applied.
- An operator attempts to change their own privileged status or disable their own
  account; the same lockout protections apply and risky self-service is denied.
- A new installation is started twice or two bootstrap commands race; exactly one
  first administrator may be created and the other attempt must make no change.
- Storage is initialized but the first identity is not created; the installation
  must remain safely bootstrap-eligible without accepting normal sign-in.
- A packaged installation cannot write required state or is missing required
  configuration; bootstrap must fail with actionable non-secret diagnostics.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an authenticated user-management page that is available only to authorized SRE and Admin operators.
- **FR-002**: Operators MUST be able to search, filter, and navigate users by identity, display name, account status, privileged status, and group membership.
- **FR-003**: The user detail view MUST show the user's profile, account status, privileged status, group memberships, effective service access, and the group-based reason for each effective access result.
- **FR-004**: Operators MUST be able to preview, confirm, and apply one or more group-membership additions and removals for a user.
- **FR-005**: The system MUST calculate effective access from the current group-to-service rules and MUST NOT introduce direct per-user service grants in this feature.
- **FR-006**: Operators MUST be able to create a user with a unique normalized identity, display name, initial account status, privileged status, and initial group memberships.
- **FR-007**: Operators MUST be able to update permitted profile fields and disable or reactivate an account without deleting its memberships or audit history.
- **FR-008**: Operators MUST be able to initiate a credential reset without viewing, retrieving, or logging the user's existing credential.
- **FR-009**: The system MUST invalidate or reject active access for a disabled user promptly enough to prevent continued portal or protected-service use.
- **FR-010**: The system MUST prevent any operation that would leave no active administrator able to recover or manage access.
- **FR-011**: The system MUST detect stale management views and reject conflicting writes rather than silently replacing a newer user or membership state.
- **FR-012**: Every mutating operation MUST be atomic: all validated user and membership changes succeed together or none are applied.
- **FR-013**: The CLI MUST support listing and inspecting users, creating users, updating allowed profile fields, disabling and reactivating accounts, initiating credential resets, and adding or removing group memberships.
- **FR-014**: Every mutating CLI operation MUST support a preview mode that reports intended changes without changing state.
- **FR-015**: CLI operations MUST provide stable human-readable and machine-readable outcomes, including distinct success, no-change, invalid-input, conflict, and denied results.
- **FR-016**: Repeating an already-satisfied CLI membership or status operation MUST safely report no change.
- **FR-017**: The page and CLI MUST apply the same validation, authorization, lockout protection, and access-calculation rules.
- **FR-018**: Successful changes MUST be visible through both operator interfaces on the next fresh read.
- **FR-019**: The system MUST present clear empty, loading, success, validation, conflict, denied, and dependency-failure states without exposing internal or sensitive details.
- **FR-020**: Hard deletion of users, groups, memberships, or audit history MUST NOT be available in this feature.
- **FR-021**: A clean installation MUST provide a documented local CLI bootstrap operation that initializes required state and creates the first active administrator atomically.
- **FR-022**: Bootstrap MUST require an installer-supplied unique identity and strong credential and MUST NOT ship, generate, display, or log a shared default credential.
- **FR-023**: Secret bootstrap input MUST NOT be accepted through a command argument or other mechanism that commonly exposes it in process listings, shell history, or routine command output.
- **FR-024**: Bootstrap MUST be permitted only while the installation contains no identities; after any identity exists, repeat or concurrent attempts MUST make no user, privilege, membership, or credential change.
- **FR-025**: Before bootstrap is complete, the portal MUST deny normal sign-in and management use while displaying a non-sensitive instruction to complete local setup.
- **FR-026**: The installation documentation MUST describe first-run prerequisites, bootstrap, sign-in verification, safe retry after failure, and the already-initialized outcome.

### Security & Privacy Requirements *(mandatory for identity/access features)*

- **SPR-001**: User identities, group memberships, privileged status, effective access, credential-reset state, operator sessions, and audit evidence MUST be treated as confidential security data.
- **SPR-002**: Only an authenticated account with active SRE or Admin management authority MAY view user-management data or execute user-management operations.
- **SPR-003**: Authorization MUST be checked at the time each read or mutation is executed; a previously rendered page, preview, or authenticated CLI session MUST NOT bypass a later role or account-status change.
- **SPR-004**: Denied, malformed, stale, abusive, and lockout-risk operations MUST make no state change and MUST emit a safe audit outcome.
- **SPR-005**: The page, CLI, and audit records MUST NOT expose passwords, password hashes, credential-reset secrets, session identifiers, security tokens, or unnecessary personal data.
- **SPR-006**: Audit events MUST record the acting identity, target identity, operation, timestamp, outcome, reason category, and changed security-relevant fields without recording secret values.
- **SPR-007**: Audit evidence for user lifecycle, privilege, and access-list changes MUST be retained for at least 90 days and remain queryable for incident investigation.
- **SPR-008**: Search and mutation attempts MUST be subject to protections against enumeration, excessive requests, and repeated unauthorized use while preserving normal operator workflows.
- **SPR-009**: Credential-reset initiation MUST use a time-limited, single-use recovery path and MUST invalidate superseded reset attempts.
- **SPR-010**: Disabling an account or removing operator authority MUST invalidate existing management capability and protected access without waiting for a new sign-in.
- **SPR-011**: Bootstrap authority MUST depend on trusted local installation access and empty identity state; it MUST NOT be exposed as an unauthenticated remote account-creation path.
- **SPR-012**: Bootstrap success, failure, rejection, and concurrent-attempt outcomes MUST emit non-sensitive operational evidence, including time and outcome, without recording the supplied credential.

### Key Entities *(include if feature involves data)*

- **Managed User**: A portal identity with a unique normalized identifier, display name, active or disabled status, privileged-management status, credential state, and membership history.
- **Group Membership**: The relationship between a managed user and a group, including its current state and audit context; memberships are the only user-level input to service access in this feature.
- **Effective Access Result**: A derived view of whether a user can currently use a service and which group rules produce that result; it is not a separate grant.
- **Management Operation**: A requested create, update, lifecycle, reset, privilege, or membership change with previewed intent, validation state, actor, target, outcome, and conflict context.
- **Audit Event**: Non-sensitive evidence of a management read or mutation, including actor, target, operation, time, outcome, and reason category.
- **Installation State**: Whether required portal state is unavailable, ready for first-administrator bootstrap, or initialized; this state controls whether bootstrap or normal authenticated use is allowed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In usability testing, at least 90% of authorized operators can find a user, determine why the user can access a service, and apply a membership change correctly on their first attempt.
- **SC-002**: An operator can complete a single-user membership change through the page in under 60 seconds and through the CLI in under 30 seconds, excluding approval or credential-entry time.
- **SC-003**: Successful user, status, privilege, and membership changes are reflected in effective access and both operator interfaces within 5 seconds.
- **SC-004**: All tested unauthorized, stale, malformed, and last-administrator-risk operations produce no partial state change and a traceable non-sensitive audit outcome.
- **SC-005**: For every sampled service-access result, operators can identify all granting groups with 100% agreement between the displayed explanation and actual authorization behavior.
- **SC-006**: Repeating any supported idempotent CLI operation 10 times produces one intended state and no duplicate memberships.
- **SC-007**: User searches over at least 10,000 managed identities show the first bounded result set within 2 seconds for at least 95% of normal operator requests.
- **SC-008**: During operational acceptance testing, no credential, session identifier, reset secret, or password hash appears in page output, CLI output, or audit evidence.
- **SC-009**: A first-time installer can move from a clean packaged installation to a verified administrator sign-in in under 5 minutes using only the documented setup flow.
- **SC-010**: Across 20 sequential and concurrent bootstrap retry tests, exactly one first administrator is created and no default or supplied credential appears in command history, process arguments, normal output, or audit evidence.

## Assumptions

- SRE and Admin are organizational operator personas with the same user-management authority in the initial release; finer-grained delegation is outside this feature.
- Existing portal authentication and group-to-service access rules remain the source of identity and authorization truth.
- A first-time installer has trusted local command access to the deployed portal and can provide required configuration and a strong initial administrator credential.
- The identity store is empty on first installation; importing pre-existing users is a migration workflow and does not use bootstrap.
- Access-list control means managing user group memberships and viewing derived service access, not granting services directly to individual users.
- Existing users can be migrated or interpreted as active accounts without changing their current memberships.
- Disabling rather than deleting a user is the standard offboarding path so historical evidence remains intact.
- Credential reset delivery uses the portal's approved recovery channel; choosing or replacing that channel belongs in implementation planning.
- Bulk file import, directory synchronization, external identity-provider provisioning, group creation/deletion, and direct service-rule editing are outside the initial scope.
- Desktop web and command-line operator workflows are in scope; a dedicated mobile management experience is not.
