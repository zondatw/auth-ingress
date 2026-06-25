# Tasks: Tech Style UI Refresh

**Input**: Design documents from `/specs/009-tech-style-ui/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required because this feature changes every visible authentication, portal, admin, audit, error, password, and security-sensitive interaction surface.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inventory the current UI and establish focused test locations for the tech-style refresh.

- [ ] T001 Inspect all existing templates under src/auth_ingress/web/templates/ for visible auth, portal, admin, audit, error, and password flows
- [ ] T002 Inspect existing visual styling and responsive behavior in src/auth_ingress/web/static/portal.css
- [ ] T003 [P] Inspect route-provided view data for portal, users, groups, services, audit, auth, and error pages in src/auth_ingress/web/routes/
- [ ] T004 [P] Inspect existing UI/browser/security tests in tests/contract/, tests/security/, tests/integration/, and tests/e2e/ for reusable fixtures and assertions
- [ ] T005 [P] Add shared UI contract fixture helpers for rendered pages, forbidden values, and responsive route lists in tests/ui_style_helpers.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared visual tokens, shell structure, component class contracts, and safe summary primitives required by all stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Define dark technical visual tokens, typography roles, spacing roles, status roles, and focus roles in src/auth_ingress/web/static/portal.css
- [ ] T007 Refactor base product shell, navigation landmarks, current-user context, admin links, and responsive nav structure in src/auth_ingress/web/templates/base.html
- [ ] T008 Add shared CSS component classes for panels, metric cards, page headers, action groups, status chips, alerts, notices, confirmations, empty states, tables, forms, and secret display in src/auth_ingress/web/static/portal.css
- [ ] T009 Add safe operational-summary view-model helpers for aggregate page context in src/auth_ingress/web/routes/portal.py, src/auth_ingress/web/routes/admin_users.py, src/auth_ingress/web/routes/admin_groups.py, src/auth_ingress/web/routes/admin_services.py, and src/auth_ingress/web/routes/admin_audit.py
- [ ] T010 [P] Add visual-system contract tests for required pages/components in tests/contract/test_ui_style_contract.py
- [ ] T011 [P] Add baseline security redaction tests for refreshed rendered pages in tests/security/test_ui_style_security.py
- [ ] T012 [P] Add browser fixture coverage for authenticated admin and non-admin UI journeys in tests/e2e/test_tech_style_ui.py

**Checkpoint**: Shared styling, shell, component contracts, and safe summary data are available for all refreshed pages.

---

## Phase 3: User Story 1 - Use a modern technical visual system across the portal (Priority: P1) 🎯 MVP

**Goal**: Every visible page uses the same dark technical control-surface style without changing existing business behavior.

**Independent Test**: Open sign-in, setup-required, change/reset password, portal, admin users/groups/services/audit, and access-denied pages and verify consistent shell, panels, forms, tables, status chips, responsive layout, and unchanged workflows.

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract tests proving all required pages render refreshed shell/component markers in tests/contract/test_ui_style_contract.py
- [ ] T014 [P] [US1] Add contract tests proving no page relies on legacy light-only body/panel/table styling in tests/contract/test_ui_style_contract.py
- [ ] T015 [P] [US1] Add browser tests for portal/auth/admin responsive layout and navigation reachability in tests/e2e/test_tech_style_ui.py
- [ ] T016 [P] [US1] Add regression assertions that existing auth, portal, admin, and audit routes still render successful responses in tests/integration/test_ui_style_routes.py

### Implementation for User Story 1

- [ ] T017 [US1] Refresh global page background, shell, typography, links, buttons, focus indicators, panels, grids, tables, forms, and responsive rules in src/auth_ingress/web/static/portal.css
- [ ] T018 [US1] Refresh sign-in, setup-required, change-password, and reset-password templates with shared shell/page-header/form/state classes in src/auth_ingress/web/templates/auth/sign_in.html, src/auth_ingress/web/templates/auth/setup_required.html, src/auth_ingress/web/templates/auth/change_password.html, and src/auth_ingress/web/templates/auth/reset_password.html
- [ ] T019 [US1] Refresh portal service list layout, service cards, sign-out action, admin links, and empty state in src/auth_ingress/web/templates/portal/index.html
- [ ] T020 [US1] Refresh access-denied/error page layout, state messaging, and return action in src/auth_ingress/web/templates/errors/access_denied.html
- [ ] T021 [US1] Refresh admin users list/detail templates with consistent headers, panels, tables, action groups, form grids, and status chips in src/auth_ingress/web/templates/admin/users.html and src/auth_ingress/web/templates/admin/user_detail.html
- [ ] T022 [US1] Refresh admin groups list/detail templates with consistent headers, panels, dependency sections, lifecycle actions, and status chips in src/auth_ingress/web/templates/admin/groups.html and src/auth_ingress/web/templates/admin/group_detail.html
- [ ] T023 [US1] Refresh admin services and audit templates with consistent form panels, service cards/sections, table styling, and state presentation in src/auth_ingress/web/templates/admin/services.html and src/auth_ingress/web/templates/admin/audit.html

**Checkpoint**: User Story 1 is independently functional; all visible pages share the refreshed technical visual system and existing workflows still render.

---

## Phase 4: User Story 2 - Surface operational context like a monitoring console (Priority: P2)

**Goal**: Portal and admin screens show safe dashboard-like context, relationship/dependency summaries, and scan-friendly state cues using existing data.

**Independent Test**: Open populated and empty portal/admin list/detail pages and verify safe cards, counts, dependency summaries, audit context, and next actions are visible without exposing secrets or changing authorization.

### Tests for User Story 2

- [ ] T024 [P] [US2] Add contract tests for portal service summary cards and service card context in tests/contract/test_ui_style_contract.py
- [ ] T025 [P] [US2] Add contract tests for user, group, service, and audit operational summaries in tests/contract/test_ui_style_contract.py
- [ ] T026 [P] [US2] Add security tests proving operational summaries are aggregate-only and admin-only where required in tests/security/test_ui_style_security.py
- [ ] T027 [P] [US2] Add browser tests for populated and empty admin summary states in tests/e2e/test_tech_style_ui.py

### Implementation for User Story 2

- [ ] T028 [US2] Add safe portal service summary values for assigned service count and admin navigation context in src/auth_ingress/web/routes/portal.py
- [ ] T029 [US2] Add safe user management summary values for active, disabled, administrator, and filtered result counts in src/auth_ingress/web/routes/admin_users.py
- [ ] T030 [US2] Add safe group management summary values for active, deactivated, used, unused, assigned-user, and associated-service context in src/auth_ingress/web/routes/admin_groups.py
- [ ] T031 [US2] Add safe service management summary values for enabled, disabled, proxy-enabled, websocket-enabled, and group-linked service context in src/auth_ingress/web/routes/admin_services.py
- [ ] T032 [US2] Add safe audit summary values for retained event count, recent denial count, and empty audit state in src/auth_ingress/web/routes/admin_audit.py
- [ ] T033 [US2] Render portal/admin summary cards and scan-friendly context sections in src/auth_ingress/web/templates/portal/index.html, src/auth_ingress/web/templates/admin/users.html, src/auth_ingress/web/templates/admin/groups.html, src/auth_ingress/web/templates/admin/services.html, and src/auth_ingress/web/templates/admin/audit.html
- [ ] T034 [US2] Render relationship/dependency summary cards on detail pages in src/auth_ingress/web/templates/admin/user_detail.html, src/auth_ingress/web/templates/admin/group_detail.html, and relevant service sections in src/auth_ingress/web/templates/admin/services.html
- [ ] T035 [US2] Add timeline-like or event-list visual treatment for audit rows and recent context without exposing extra audit payloads in src/auth_ingress/web/templates/admin/audit.html and src/auth_ingress/web/static/portal.css

**Checkpoint**: User Story 2 is independently functional; administrators get safe operational context and relationship summaries from existing data.

---

## Phase 5: User Story 3 - Preserve security clarity and accessibility in the new style (Priority: P3)

**Goal**: Security-sensitive states remain clear, accessible, keyboard-usable, and free of secret leakage after the visual refresh.

**Independent Test**: Exercise failed sign-in, setup-required, password-change, temporary-password copy, validation errors, destructive confirmations, unauthorized admin access, access denial, and keyboard navigation; verify clarity, accessibility, and redaction.

### Tests for User Story 3

- [ ] T036 [P] [US3] Add security tests for forbidden credentials, tokens, reset secrets, session identifiers, database details, and unnecessary personal data in tests/security/test_ui_style_security.py
- [ ] T037 [P] [US3] Add security tests for non-admin denial and admin-only summary visibility in tests/security/test_ui_style_security.py
- [ ] T038 [P] [US3] Add browser tests for keyboard focus order and visible focus indicators across auth, portal, admin, copy, and destructive confirmation controls in tests/e2e/test_tech_style_ui.py
- [ ] T039 [P] [US3] Add browser tests for temporary password copy feedback, validation error preservation, and destructive confirmation emphasis in tests/e2e/test_tech_style_ui.py
- [ ] T040 [P] [US3] Add contrast/state contract checks for status, alert, notice, danger, disabled, muted, and focus tokens in tests/contract/test_ui_style_contract.py

### Implementation for User Story 3

- [ ] T041 [US3] Strengthen alert, notice, field-error, empty, unavailable, denied, stale/conflict, and destructive-confirmation visual states in src/auth_ingress/web/static/portal.css
- [ ] T042 [US3] Update validation-error rendering and safe value preservation presentation in src/auth_ingress/web/templates/admin/users.html, src/auth_ingress/web/templates/admin/user_detail.html, src/auth_ingress/web/templates/admin/groups.html, src/auth_ingress/web/templates/admin/group_detail.html, and src/auth_ingress/web/templates/admin/services.html
- [ ] T043 [US3] Update temporary password display, copy control, copy status, and sensitive-value warning presentation in src/auth_ingress/web/templates/admin/users.html and src/auth_ingress/web/static/portal.css
- [ ] T044 [US3] Update destructive and access-changing confirmations for user deletion/status, group lifecycle, membership changes, and service changes in src/auth_ingress/web/templates/admin/user_detail.html, src/auth_ingress/web/templates/admin/group_detail.html, and src/auth_ingress/web/templates/admin/services.html
- [ ] T045 [US3] Ensure status chips include readable text and non-color cues for active, disabled, deactivated, removed, enabled, denied, unavailable, success, warning, and danger states in src/auth_ingress/web/static/portal.css and affected admin templates under src/auth_ingress/web/templates/admin/
- [ ] T046 [US3] Ensure mobile navigation, table scroll regions, form controls, copy controls, and action buttons remain keyboard-accessible and responsive in src/auth_ingress/web/templates/base.html and src/auth_ingress/web/static/portal.css
- [ ] T047 [US3] Review rendered markup to keep CSRF values only in required hidden inputs and remove any debug/diagnostic exposure in templates under src/auth_ingress/web/templates/

**Checkpoint**: User Story 3 is independently functional; the refreshed style preserves security clarity and accessibility.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate visual consistency, security boundaries, regression safety, and implementation evidence across all stories.

- [ ] T048 [P] Update specs/009-tech-style-ui/quickstart.md if actual validation commands or routes differ from planned commands
- [ ] T049 [P] Review final UI copy for consistent product language, safe guidance, and no reference-project-specific unrelated content in src/auth_ingress/web/templates/
- [ ] T050 [P] Review src/auth_ingress/web/static/portal.css for unused legacy selectors, inconsistent tokens, mobile overflow risks, and duplicated component styles
- [ ] T051 Run focused UI contract and security tests with uv run pytest tests/contract/test_ui_style_contract.py tests/security/test_ui_style_security.py -q and record results in specs/009-tech-style-ui/quickstart.md
- [ ] T052 Run browser UI tests with uv run pytest tests/e2e/test_tech_style_ui.py -q and record results in specs/009-tech-style-ui/quickstart.md
- [ ] T053 Run existing auth/admin/security regression tests from specs/009-tech-style-ui/quickstart.md and record results in specs/009-tech-style-ui/quickstart.md
- [ ] T054 Run full regression suite with uv run pytest -q and record results in specs/009-tech-style-ui/quickstart.md
- [ ] T055 Verify FR-001–FR-015, SPR-001–SPR-005, SC-001–SC-007, and all UI contracts have passing evidence in specs/009-tech-style-ui/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundation; MVP full visual-system refresh.
- **User Story 2 (Phase 4)**: Depends on Foundation and benefits from US1 component/card styling.
- **User Story 3 (Phase 5)**: Depends on Foundation and should run after or alongside US1/US2 to harden final states.
- **Polish (Phase 6)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational; provides the minimum coherent tech-style UI.
- **US2 (P2)**: Can start after Foundational, but summary cards and relationship sections are easier after US1 component classes exist.
- **US3 (P3)**: Can start after Foundational, but final accessibility/security checks should be repeated after US1 and US2 template changes.

### Within Each User Story

- Tests must be written and observed failing before implementation.
- Shared CSS/component contracts before template-wide class updates.
- Route summary data before templates that render summary cards.
- Security/accessibility tests before final state styling is accepted.

### Parallel Opportunities

- T003–T005 can run in parallel during setup.
- T010–T012 can run in parallel after shared class/data expectations are understood.
- US1 tests T013–T016 can run in parallel.
- US2 tests T024–T027 can run in parallel.
- US3 tests T036–T040 can run in parallel.
- Template refresh tasks can be split by page group after base shell and CSS tokens land.
- Polish review tasks T048–T050 can run in parallel before final validation commands.

---

## Parallel Example: User Story 1

```text
Task: "T013 [US1] Add contract tests proving all required pages render refreshed shell/component markers in tests/contract/test_ui_style_contract.py"
Task: "T014 [US1] Add contract tests proving no page relies on legacy light-only body/panel/table styling in tests/contract/test_ui_style_contract.py"
Task: "T015 [US1] Add browser tests for portal/auth/admin responsive layout and navigation reachability in tests/e2e/test_tech_style_ui.py"
Task: "T016 [US1] Add regression assertions that existing auth, portal, admin, and audit routes still render successful responses in tests/integration/test_ui_style_routes.py"
```

## Parallel Example: User Story 2

```text
Task: "T024 [US2] Add contract tests for portal service summary cards and service card context in tests/contract/test_ui_style_contract.py"
Task: "T025 [US2] Add contract tests for user, group, service, and audit operational summaries in tests/contract/test_ui_style_contract.py"
Task: "T026 [US2] Add security tests proving operational summaries are aggregate-only and admin-only where required in tests/security/test_ui_style_security.py"
Task: "T027 [US2] Add browser tests for populated and empty admin summary states in tests/e2e/test_tech_style_ui.py"
```

## Parallel Example: User Story 3

```text
Task: "T036 [US3] Add security tests for forbidden credentials, tokens, reset secrets, session identifiers, database details, and unnecessary personal data in tests/security/test_ui_style_security.py"
Task: "T038 [US3] Add browser tests for keyboard focus order and visible focus indicators across auth, portal, admin, copy, and destructive confirmation controls in tests/e2e/test_tech_style_ui.py"
Task: "T039 [US3] Add browser tests for temporary password copy feedback, validation error preservation, and destructive confirmation emphasis in tests/e2e/test_tech_style_ui.py"
Task: "T040 [US3] Add contrast/state contract checks for status, alert, notice, danger, disabled, muted, and focus tokens in tests/contract/test_ui_style_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Write and observe failing US1 tests T013–T016.
3. Complete US1 implementation T017–T023.
4. Stop and validate: every visible page renders with a coherent technical visual system and existing route behavior remains intact.

### Incremental Delivery

1. Setup + Foundation → shared dark technical shell, component classes, and test scaffolding.
2. US1 → full-page visual-system coverage.
3. US2 → safe operational context and relationship summaries.
4. US3 → accessibility/security hardening for sensitive states.
5. Polish → final quickstart evidence and full regression.

### Parallel Team Strategy

With multiple developers after Foundation:

1. Developer A: US1 auth/portal/admin template refresh.
2. Developer B: US2 safe summary route data and summary cards.
3. Developer C: US3 accessibility/security tests and sensitive state styling.
4. Coordinate changes to src/auth_ingress/web/static/portal.css and src/auth_ingress/web/templates/base.html to avoid conflicting edits.

## Notes

- [P] tasks = different files, no dependencies.
- [US1], [US2], [US3] map to prioritized stories in spec.md.
- Keep the feature inside the existing server-rendered UI; do not add a new frontend runtime.
- Use the agent-interlude reference as inspiration for a dark technical console, not as content or implementation to copy.
- Do not introduce external hosted fonts, analytics, scripts, or design services.
- Keep credentials, session identifiers, reset secrets, CSRF token values outside required hidden inputs, database details, and unnecessary personal data out of visible UI and diagnostics.
