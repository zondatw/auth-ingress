# Tasks: Full Web-App Proxy Support

**Input**: Design documents from `/specs/002-full-web-app-proxy/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Every story changes the portal authorization boundary, so contract,
integration, security, and real-browser tests are required before implementation.

**Organization**: Tasks are grouped by independently testable user story and
ordered so the shared origin, ticket, destination, and header policies block all
story implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes a different file and has no
  dependency on another incomplete task in the same phase
- **[Story]**: Maps the task to User Story 1, 2, or 3
- Every task names the exact file it creates or changes

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the proxy dependency and establish configuration and test
fixtures shared by every story.

- [X] T001 Add the maintained `websockets` runtime dependency and refresh resolved packages in pyproject.toml and uv.lock
- [X] T002 Add validated portal host, proxy base domain, trusted proxy/network, launch-ticket TTL, transfer limit, timeout, and WebSocket lifetime settings in src/auth_portal/config.py
- [X] T003 [P] Create a representative downstream application with relative/root assets, nested routes, forms, JSON, cookies, redirects, uploads, downloads, ranges, and WebSocket echo in tests/fixtures/downstream_app.py
- [X] T004 Extend isolated database, wildcard service-host, downstream server, and Playwright live-server fixtures for proxy tests in tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared persisted state and security policies required by
all HTTP and WebSocket proxy stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [X] T005 [P] Add proxy-enabled, WebSocket-enabled, redirect-policy, and compatibility fields with validation defaults to ServiceEntry in src/auth_portal/models/service_entry.py
- [X] T006 [P] Create the one-time ProxyLaunchTicket model with digest uniqueness, expiry, consumption, session, service, and allowlisted context fields in src/auth_portal/models/proxy_launch_ticket.py
- [X] T007 Register ProxyLaunchTicket and its relationships in src/auth_portal/models/__init__.py
- [X] T008 Implement an idempotent schema upgrade for existing ServiceEntry rows plus proxy launch-ticket table creation in src/auth_portal/repositories/schema.py
- [X] T009 [P] Implement strict portal/service Host parsing, slug derivation, unknown-host rejection, and public service-origin construction in src/auth_portal/security/proxy_host.py
- [X] T010 [P] Implement fixed-destination URL joining, DNS resolution, trusted-address enforcement, rebinding checks, and HTTP-to-WebSocket scheme conversion in src/auth_portal/security/proxy_destination.py
- [X] T011 Extend signed-cookie helpers with a reserved host-only service proxy credential bound to session, service, version, and bounded expiry in src/auth_portal/security/cookies.py
- [X] T012 Implement launch-ticket issue, digest lookup, atomic one-time consumption, and per-request session/user/service/access-rule revalidation in src/auth_portal/services/proxy_authorization_service.py
- [X] T013 [P] Implement request/response hop-by-hop filtering, reserved credential removal, forwarding context, cookie parsing, and multi-value header preservation in src/auth_portal/services/proxy_header_policy.py
- [X] T014 Extend non-sensitive audit reason/event coverage for proxy launch, denial, redirect, upstream, WebSocket, and compatibility decisions in src/auth_portal/services/audit_service.py
- [X] T015 Seed a proxy-enabled demo service and compatibility defaults without emitting credentials, tickets, cookies, or destinations in src/auth_portal/cli.py

**Checkpoint**: Host routing, persistence, authorization, destination validation,
credential isolation, header policy, and fixtures are ready.

---

## Phase 3: User Story 1 - Open a Complete Protected Web App (Priority: P1) 🎯 MVP

**Goal**: Launch an authorized service on its isolated service host and render
pages, nested routes, CSS, JavaScript, images, fonts, and documents without
exposing the internal destination.

**Independent Test**: Open the representative fixture from the portal, complete
one-time bootstrap, verify all relative/root-relative assets and scripts render,
then refresh and open a nested route directly while the URL remains on the
service host.

### Tests for User Story 1 (write first and verify they fail)

- [X] T016 [P] [US1] Add host launch, bootstrap, direct-host, reserved-path, and unknown-host contract tests from contracts/host-routing.md in tests/contract/test_proxy_host_contract.py
- [X] T017 [P] [US1] Add integration tests for relative/root-relative CSS, JavaScript, image, font, document, nested route, refresh, HEAD, 404, and content-type behavior in tests/integration/test_proxy_assets.py
- [X] T018 [P] [US1] Add security tests for missing/expired/replayed/mismatched tickets, malformed hosts and paths, arbitrary destination input, DNS rebinding, and internal-detail disclosure in tests/security/test_proxy_authorization.py
- [X] T019 [P] [US1] Add a Playwright journey for portal launch, ticket removal, complete rendering, nested navigation, refresh, and new-tab access in tests/e2e/test_full_web_app_proxy.py

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement service-host bootstrap, local proxy-cookie creation/clearing, direct-access recovery, and reserved-path denial in src/auth_portal/web/routes/proxy.py
- [X] T021 [P] [US1] Replace buffered single-page fetching with pooled streaming GET/HEAD forwarding, path/query mapping, and guaranteed upstream closure in src/auth_portal/services/proxy_http_service.py
- [X] T022 [P] [US1] Implement non-mutating destination reachability, asset/reference, redirect, cookie, and WebSocket capability checks with reason codes in src/auth_portal/services/service_compatibility_service.py
- [X] T023 [US1] Update the portal `/services/{slug}` route to authorize, issue a 60-second one-time launch ticket, and redirect to the derived service host in src/auth_portal/web/routes/services.py
- [X] T024 [US1] Add service-host catch-all GET/HEAD dispatch with authorization, safe error mapping, and allowed-entry/upstream audit events in src/auth_portal/web/routes/proxy.py
- [X] T025 [US1] Apply safe response status, content type/encoding, validator/cache, and internal redirect rewriting for rendered resources in src/auth_portal/services/proxy_http_service.py
- [X] T026 [US1] Add administrator compatibility-check action and proxy-policy validation to service management routes in src/auth_portal/web/routes/admin_services.py
- [X] T027 [US1] Add proxy/WebSocket controls, derived service host, compatibility status, check action, and operator guidance to src/auth_portal/web/templates/admin/services.html
- [X] T028 [US1] Register host-aware proxy HTTP routing and shared HTTPX client startup/shutdown without changing portal-host behavior in src/auth_portal/main.py

**Checkpoint**: User Story 1 independently renders a complete protected browser
application and is the deployable MVP.

---

## Phase 4: User Story 2 - Use Interactive and Stateful App Features (Priority: P2)

**Goal**: Support forms, background data actions, query strings, uploads,
downloads, range responses, redirects, and service-isolated downstream cookies.

**Independent Test**: Through one service host, submit a form and JSON action,
upload and download checksum-verified files, request a byte range, follow an
internal redirect, reject an external redirect, and prove a same-named cookie in
another service does not collide or replace the portal credential.

### Tests for User Story 2 (write first and verify they fail)

- [X] T029 [P] [US2] Add method, raw-query, streaming-body, response-header, cookie, redirect, range, upload, download, cancellation, and timeout contract tests from contracts/http-forwarding.md in tests/contract/test_proxy_http_contract.py
- [X] T030 [P] [US2] Add integration tests for forms, JSON actions, repeated query values, 50 MB streaming uploads, 100 MB downloads, checksums, filenames, ranges, caching, and internal redirects in tests/integration/test_proxy_interactions.py
- [X] T031 [P] [US2] Add security tests for portal/proxy cookie stripping, reserved-cookie replacement, cross-service state collision, redirect escape, credential-bearing URLs, payload redaction, and authorization changes during later requests in tests/security/test_proxy_state_isolation.py
- [X] T032 [P] [US2] Extend the Playwright compatibility journey with JavaScript data calls, form submission, upload/download, application state, two-service isolation, and redirect behavior in tests/e2e/test_full_web_app_proxy.py

### Implementation for User Story 2

- [X] T033 [US2] Extend proxy forwarding to GET, HEAD, POST, PUT, PATCH, DELETE, and OPTIONS with raw query preservation and asynchronous request-body streaming in src/auth_portal/services/proxy_http_service.py
- [X] T034 [US2] Implement downstream Cookie forwarding plus separate Set-Cookie parsing, internal Domain removal, Path preservation, and reserved-name rejection in src/auth_portal/services/proxy_header_policy.py
- [X] T035 [US2] Implement relative and fixed-destination redirect preservation plus safe denial of external, cross-service, credential-bearing, malformed, and unsupported targets in src/auth_portal/services/proxy_http_service.py
- [X] T036 [US2] Preserve content disposition, multiple cookies, cache validators, byte ranges, partial status, raw encoding, and valid content length in streamed responses in src/auth_portal/services/proxy_http_service.py
- [X] T037 [US2] Enforce configured request/transfer limits, distinguish connect/read timeout outcomes, cancel upstream work on browser disconnect, and prohibit automatic action retries in src/auth_portal/services/proxy_http_service.py
- [X] T038 [US2] Extend service-host catch-all routing to all supported methods with interaction denial, timeout, interruption, and unsafe-redirect responses/audits in src/auth_portal/web/routes/proxy.py

**Checkpoint**: User Story 2 independently proves normal interactive and stateful
web-app behavior through the protected service origin.

---

## Phase 5: User Story 3 - Maintain Protection During Advanced Traffic and Failures (Priority: P3)

**Goal**: Relay real-time text/binary traffic with bounded authorization and
close both sides safely during expiry, revocation, timeout, disconnect, or
downstream failure.

**Independent Test**: Exchange text and binary frames through the representative
service, verify subprotocol and close behavior, revoke permission and confirm a
reconnect is denied, then exercise downstream disconnect and bounded-lifetime
closure without leaking frame content or destination details.

### Tests for User Story 3 (write first and verify they fail)

- [X] T039 [P] [US3] Add handshake, query, cookie, origin, subprotocol, text/binary frame, close, and lifetime contract tests from contracts/websocket-forwarding.md in tests/contract/test_proxy_websocket_contract.py
- [X] T040 [P] [US3] Add integration tests for bidirectional text/binary relay, reconnect authorization, subprotocol negotiation, downstream disconnect, cancellation, and maximum lifetime in tests/integration/test_proxy_websocket.py
- [X] T041 [P] [US3] Add security tests for signed-out/expired/revoked/disabled handshakes, WebSocket-disabled services, unsafe resolution, reserved credentials, cross-service hosts, and frame redaction in tests/security/test_proxy_websocket_security.py
- [X] T042 [P] [US3] Extend the Playwright journey with real-time updates, reconnect denial after permission removal, and safe disconnected-service recovery in tests/e2e/test_full_web_app_proxy.py

### Implementation for User Story 3

- [X] T043 [US3] Implement validated downstream WebSocket connection setup, allowed cookie/origin/subprotocol forwarding, and text/binary bidirectional frame relay in src/auth_portal/services/proxy_websocket_service.py
- [X] T044 [US3] Add service-host WebSocket catch-all routing with pre-accept authorization and safe unknown/disabled/malformed handshake denial in src/auth_portal/web/routes/proxy.py
- [X] T045 [US3] Supervise both relay directions, preserve safe close codes, cancel peer work on disconnect, and enforce central-session/configured maximum lifetime in src/auth_portal/services/proxy_websocket_service.py
- [X] T046 [US3] Add non-sensitive WebSocket start/end diagnostics and denied/expired/upstream-failure audit reason codes without frame, query, cookie, or destination data in src/auth_portal/services/audit_service.py
- [X] T047 [US3] Register WebSocket host routing and ensure application shutdown closes active upstream HTTP and WebSocket resources in src/auth_portal/main.py

**Checkpoint**: All three user stories are independently functional and the full
standards-based browser compatibility target is covered.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate security, deployment, performance, compatibility,
documentation, and regressions across all stories.

- [X] T048 [P] Add focused unit coverage for Host parsing, path joining, DNS/IP classification, cookie filtering, header filtering, redirects, ticket digests, and expiry boundaries in tests/unit/test_proxy_security_helpers.py
- [X] T049 [P] Document wildcard DNS/TLS, trusted proxy/network settings, cookie requirements, limits, compatibility boundaries, and production rollout/rollback in README.md
- [X] T050 Verify p95 proxy overhead, constant-memory 50 MB upload, constant-memory 100 MB download, connection pooling, and cancellation cleanup in tests/integration/test_proxy_performance.py
- [X] T051 Verify proxy logs/audits exclude credentials, tickets, sessions, cookies, destinations, queries, filenames, bodies, frames, and unnecessary personal data in tests/security/test_proxy_redaction.py
- [X] T052 Validate 98% rendering, 95% interaction, 100% denial/boundary, administrator compatibility, and actionable-failure criteria in tests/e2e/test_full_web_app_proxy.py
- [X] T053 Execute every deployment, rendering, interaction, authorization, WebSocket, failure, and automated-check scenario and record results in specs/002-full-web-app-proxy/quickstart.md
- [X] T054 Run the complete existing and new test suite with coverage and resolve all regressions in tests/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Setup and blocks every story.
- **Phase 3 (US1)**: Depends only on Foundation and delivers the complete-rendering
  MVP.
- **Phase 4 (US2)**: Depends on US1's HTTP transport and service-host routing;
  its tests and policy work can start after Foundation, but implementation merges
  after US1.
- **Phase 5 (US3)**: Depends on Foundation and service-host bootstrap from US1;
  WebSocket service/test work can proceed alongside US2.
- **Phase 6 (Polish)**: Depends on all stories selected for release.

### User Story Dependency Graph

```text
Setup → Foundation → US1 (MVP) → US2 ─┐
                         └────→ US3 ──┼→ Polish
```

- **US1** establishes service origin, ticket bootstrap, and GET/HEAD transport.
- **US2** extends the US1 HTTP transport; it does not depend on US3.
- **US3** reuses US1 authorization/bootstrap but has a separate transport and
  does not depend on US2.

### Within Each User Story

- Write contract, integration, security, and Playwright tests first and confirm
  they fail for the missing behavior.
- Implement models/policies before transport services, services before routes,
  and routes before browser integration.
- Revalidate session, user, service, and access rule before each new HTTP request
  and WebSocket handshake.
- Never capture browser/downstream payloads or credentials in logs, audits, or
  failing-test output.
- Run the story's independent test at its checkpoint before starting dependent
  implementation.

## Parallel Execution Examples

### User Story 1

Run T016-T019 in parallel. After the Foundation, T020-T022 can proceed in
parallel; then complete T023-T028 in dependency order.

### User Story 2

Run T029-T032 in parallel. Cookie policy T034 can proceed independently while
T033 extends streaming methods; merge redirect, response, limit, and route work
sequentially in T035-T038.

### User Story 3

Run T039-T042 in parallel. T043 starts after the tests fail; T044-T047 then
integrate route, lifetime, audit, and lifecycle behavior in order.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup (T001-T004).
2. Complete Foundation (T005-T015).
3. Complete US1 tests and implementation (T016-T028).
4. Run the US1 independent browser test for full rendering and nested routes.
5. Deploy only after wildcard DNS/TLS and private downstream reachability are
   verified; keep existing services on simple entry until explicitly proxy-enabled.

### Incremental Delivery

1. Deliver US1 for complete read/navigation rendering.
2. Add US2 for forms, APIs, transfers, cookies, and redirects.
3. Add US3 for WebSockets and bounded real-time failure behavior.
4. Complete compatibility, performance, audit-redaction, documentation, and full
   regression gates before enabling proxy mode broadly.

## Notes

- `[P]` means different files and no incomplete dependency conflict.
- Tests precede implementation because every story changes a security boundary.
- The browser never chooses the upstream origin; only path, query, safe headers,
  body stream, and frames are forwarded to a fixed validated destination.
- Separate service hosts are required for root-relative resource and state
  compatibility; arbitrary HTML/CSS/JavaScript rewriting is out of scope.
- Commit after each task or coherent task group and stop at each story checkpoint
  for independent validation.

