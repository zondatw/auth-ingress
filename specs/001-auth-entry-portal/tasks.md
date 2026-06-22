# Tasks: Auth Entry Portal

**Input**: Design documents from `/specs/001-auth-entry-portal/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: All three stories affect authentication or authorization, so their security-sensitive tests are required and must be written before implementation.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes a different file and has no dependency on another incomplete task in the same phase
- **[Story]**: Maps the task to User Story 1, 2, or 3
- Every task names the exact file it creates or changes

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python application, dependency set, and test layout.

- [X] T001 Create the Python 3.12 project metadata, runtime dependencies, test dependencies, and `auth-portal` CLI entry point in pyproject.toml
- [X] T002 Create the application package and FastAPI application factory in src/auth_portal/main.py
- [X] T003 [P] Define environment-based SQLite, session, rate-limit, audit-retention, and downstream timeout settings in src/auth_portal/config.py
- [X] T004 [P] Configure shared pytest fixtures and temporary SQLite databases in tests/conftest.py
- [X] T005 [P] Add local database, secret, cache, coverage, and Playwright artifact exclusions in .gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared trust boundary, persistence, session, audit, and web infrastructure required by every story.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [X] T006 Define SQLAlchemy engine, transaction-scoped session factory, and declarative base in src/auth_portal/repositories/database.py
- [X] T007 Create User, Group, and GroupMembership models with uniqueness and status constraints in src/auth_portal/models/identity.py
- [X] T008 [P] Create ServiceEntry and AccessRule models with slug, destination, enabled-state, and group-rule constraints in src/auth_portal/models/service_entry.py
- [X] T009 [P] Create Session model with expiry and revocation fields in src/auth_portal/models/session.py
- [X] T010 [P] Create AuditEvent model with typed non-sensitive event, decision, reason, context, and retention fields in src/auth_portal/models/audit_event.py
- [X] T011 Create schema initialization and database lifecycle helpers in src/auth_portal/repositories/schema.py
- [X] T012 Implement password hashing and constant-behavior credential verification helpers in src/auth_portal/security/passwords.py
- [X] T013 [P] Implement signed, HttpOnly, SameSite session-cookie encoding and decoding in src/auth_portal/security/cookies.py
- [X] T014 Implement server-side session creation, validation, expiry, last-seen update, and revocation in src/auth_portal/services/session_service.py
- [X] T015 [P] Implement structured audit recording with an allowlist that excludes passwords, session identifiers, secrets, and unnecessary personal data in src/auth_portal/services/audit_service.py
- [X] T016 Implement reusable current-user, active-session, and administrator authorization dependencies in src/auth_portal/security/dependencies.py
- [X] T017 [P] Configure Jinja rendering, static assets, CSRF protection, cache-control headers, and safe exception responses in src/auth_portal/web/web.py
- [X] T018 Register public, protected-service, and admin route modules and application lifecycle hooks in src/auth_portal/main.py
- [X] T019 Implement `init-db`, `seed-demo`, and `serve` commands without emitting seeded credentials or secrets in src/auth_portal/cli.py

**Checkpoint**: Shared authentication, persistence, audit, and routing infrastructure is ready.

---

## Phase 3: User Story 1 - Enter Protected Services After Sign-In (Priority: P1) 🎯 MVP

**Goal**: Let a user sign in, see only allowed services, preserve an originally requested service, enter it through the portal, and sign out securely.

**Independent Test**: Open `/services/{service_slug}` while signed out, sign in with an authorized account, verify arrival at that same protected route, then sign out and confirm browser history cannot restore access.

### Tests for User Story 1 (write first and verify they fail)

- [X] T020 [P] [US1] Add contract tests for `/`, `/sign-in`, `/sign-out`, and successful `/services/{service_slug}` responses from contracts/openapi.yaml in tests/contract/test_user_entry_contract.py
- [X] T021 [P] [US1] Add integration tests for direct sign-in, allowed-service listing, empty state, preserved return path, and already-signed-in entry in tests/integration/test_user_entry.py
- [X] T022 [P] [US1] Add security tests for expired and revoked sessions, disabled users, open-redirect return paths, cookie flags, and sign-out browser-history behavior in tests/security/test_session_boundary.py
- [X] T023 [P] [US1] Add Playwright journey coverage for signed-out service entry through sign-in and sign-out in tests/e2e/test_user_entry.py

### Implementation for User Story 1

- [X] T024 [P] [US1] Implement credential authentication and active-user checks in src/auth_portal/services/authentication_service.py
- [X] T025 [P] [US1] Implement enabled-service listing and group-based allow decisions in src/auth_portal/services/access_service.py
- [X] T026 [US1] Implement sign-in, safe portal-local return-path preservation, and sign-out routes with audit events in src/auth_portal/web/routes/auth.py
- [X] T027 [US1] Implement the authenticated portal list and no-services empty-state route in src/auth_portal/web/routes/portal.py
- [X] T028 [US1] Implement the protected service-entry route with per-request session, service-state, and access-rule revalidation plus downstream timeout handling in src/auth_portal/web/routes/services.py
- [X] T029 [P] [US1] Create accessible sign-in, generic failure, and signed-out templates in src/auth_portal/web/templates/auth/sign_in.html
- [X] T030 [P] [US1] Create responsive allowed-service list and empty-state views in src/auth_portal/web/templates/portal/index.html
- [X] T031 [P] [US1] Add responsive layout, visible focus states, status messages, and service-card styling in src/auth_portal/web/static/portal.css

**Checkpoint**: User Story 1 works independently as the MVP.

---

## Phase 4: User Story 2 - Block Unauthorized Service Access (Priority: P2)

**Goal**: Block signed-out, unauthorized, expired, malformed, unknown, disabled, and abusive access attempts with clear safe next steps.

**Independent Test**: Request a protected service while signed out and while signed in without its group permission, then verify the downstream service is never reached and each denial has a clear response and non-sensitive audit event.

### Tests for User Story 2 (write first and verify they fail)

- [X] T032 [P] [US2] Add contract tests for 302, 403, 404, 429, and 503 denial responses from contracts/openapi.yaml in tests/contract/test_access_denial_contract.py
- [X] T033 [P] [US2] Add integration tests for unauthorized, unknown, disabled, malformed, permission-changed, and unavailable-downstream service requests in tests/integration/test_access_denials.py
- [X] T034 [P] [US2] Add security tests for repeated sign-in failures, account/client throttling recovery, audit redaction, and denial-before-forwarding in tests/security/test_access_abuse.py
- [X] T035 [P] [US2] Add Playwright coverage for denial recovery, unavailable services, empty lists, and shared-device user switching in tests/e2e/test_access_denials.py

### Implementation for User Story 2

- [X] T036 [US2] Implement bounded account-and-client failed-sign-in throttling with automatic recovery in src/auth_portal/security/rate_limit.py
- [X] T037 [US2] Integrate generic credential failures, 429 retry guidance, and non-sensitive failure auditing into src/auth_portal/web/routes/auth.py
- [X] T038 [US2] Add indistinguishable unknown/malformed service handling, explicit disabled/downstream-unavailable responses, and denial auditing before forwarding in src/auth_portal/web/routes/services.py
- [X] T039 [US2] Re-evaluate current group membership and service state on every list and entry decision in src/auth_portal/services/access_service.py
- [X] T040 [P] [US2] Create accessible unauthorized, unavailable, expired-session, and retry-later messages with portal recovery links in src/auth_portal/web/templates/errors/access_denied.html
- [X] T041 [US2] Filter unavailable services from the user list and preserve an actionable empty state in src/auth_portal/web/routes/portal.py

**Checkpoint**: User Story 2 independently proves the portal blocks all specified denial paths.

---

## Phase 5: User Story 3 - Manage Service Entries (Priority: P3)

**Goal**: Let administrators create, review, update, disable, and audit service entries and their group-based access rules.

**Independent Test**: As an administrator, create a service assigned to one group, verify a member can see and enter it while a non-member cannot, then disable it and verify all new entry attempts are blocked.

### Tests for User Story 3 (write first and verify they fail)

- [X] T042 [P] [US3] Add contract tests for `/admin/services`, `/admin/services/{service_slug}`, and `/admin/audit` from contracts/openapi.yaml in tests/contract/test_admin_contract.py
- [X] T043 [P] [US3] Add integration tests for create, review, update, access-rule replacement, disable, visibility changes, and audit review in tests/integration/test_admin_services.py
- [X] T044 [P] [US3] Add security tests for non-admin denial, forged form submissions, unsafe destinations, invalid groups, missing rules, and sensitive audit fields in tests/security/test_admin_boundary.py
- [X] T045 [P] [US3] Add Playwright coverage for the administrator create-update-disable journey in tests/e2e/test_admin_services.py

### Implementation for User Story 3

- [X] T046 [US3] Implement transactional service-entry creation, update, rule replacement, disable, and validation in src/auth_portal/services/service_admin_service.py
- [X] T047 [US3] Implement administrator-only service list, create, update, and disable routes with CSRF checks and change audit events in src/auth_portal/web/routes/admin_services.py
- [X] T048 [US3] Implement administrator-only paginated audit review with a 90-day minimum retention filter in src/auth_portal/web/routes/admin_audit.py
- [X] T049 [P] [US3] Create accessible service-entry list and edit form views with inline validation in src/auth_portal/web/templates/admin/services.html
- [X] T050 [P] [US3] Create a redacted audit-event review table in src/auth_portal/web/templates/admin/audit.html
- [X] T051 [US3] Register administrator service and audit routes in src/auth_portal/main.py

**Checkpoint**: All three user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate security, operations, performance, documentation, and complete journeys across the delivered stories.

- [X] T052 [P] Add unit coverage for password, cookie, rate-limit, return-path, destination, and audit-redaction helpers in tests/unit/test_security_helpers.py
- [X] T053 [P] Document the portal/downstream trust boundary, required network isolation, configuration, audit retention, and operator recovery procedures in README.md
- [X] T054 Add correlation IDs and structured application logging with explicit sensitive-field filtering in src/auth_portal/main.py
- [X] T055 Implement HTTPX downstream connection pooling, bounded timeouts, and safe dependency-failure cleanup in src/auth_portal/services/downstream_service.py
- [X] T056 Verify the under-60-second entry, one-second page response, and service-change performance goals with repeatable checks in tests/integration/test_performance_goals.py
- [X] T057 Execute every setup, journey, denial, admin, audit, and automated-check scenario and record validation results in specs/001-auth-entry-portal/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks every user story.
- **Phase 3 (US1)**: Depends only on Phase 2 and is the MVP.
- **Phase 4 (US2)**: Depends on Phase 2; it extends shared routes from US1, so the recommended sequence is after Phase 3 even though its denial logic remains independently testable.
- **Phase 5 (US3)**: Depends on Phase 2; it can be implemented alongside US1/US2 after the foundation, but its end-to-end visibility check uses the portal entry path.
- **Phase 6 (Polish)**: Depends on all user stories selected for release.

### User Story Dependency Graph

```text
Setup → Foundation → US1 (MVP) → Polish
                   ├→ US2 ──────┤
                   └→ US3 ──────┘
```

- **US1** has no user-story prerequisite.
- **US2** has no conceptual dependency on US1, but sequential implementation avoids conflicts in shared auth, service, and portal route files.
- **US3** has no implementation dependency on US2; its acceptance test consumes the service list and entry behavior delivered by US1.

### Within Each User Story

- Write the story's tests first and confirm they fail for the expected missing behavior.
- Implement domain services before routes, then templates and integration.
- Complete and run the independent test before moving to the next story.
- Audit success, denial, and administrative change paths without recording sensitive values.

## Parallel Execution Examples

### User Story 1

Run T020-T023 in parallel, then T024 and T025 in parallel. After routes are stable, T029-T031 can run in parallel.

### User Story 2

Run T032-T035 in parallel. After T036-T039 establish behavior, T040 can proceed independently while T041 updates the portal list.

### User Story 3

Run T042-T045 in parallel. After T046 defines service administration, T049 and T050 can run in parallel while T047-T048 connect the routes.

## Implementation Strategy

### MVP First

1. Complete Setup (T001-T005).
2. Complete Foundation (T006-T019).
3. Complete US1 (T020-T031).
4. Run the US1 contract, integration, security, and browser tests and validate the independent test.
5. Deploy only where downstream services cannot bypass the portal trust boundary.

### Incremental Delivery

1. Deliver US1 as the authenticated entry MVP.
2. Add US2 and validate every denied path before exposing real downstream services.
3. Add US3 and validate administration and audit review independently.
4. Complete cross-cutting hardening and the full quickstart before release.

## Notes

- `[P]` means the task can proceed concurrently without editing the same file or consuming unfinished behavior.
- Tests in each story precede implementation because every story changes a security boundary.
- Downstream services must be private or otherwise unreachable except through the portal-controlled route.
- Credentials, session identifiers, secrets, and unnecessary personal data must never enter logs or audit payloads.
- Commit after each task or coherent task group, and stop at each checkpoint for independent validation.
