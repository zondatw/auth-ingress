# Feature Specification: Full Web-App Proxy Support

**Feature Branch**: `002-full-web-app-proxy`

**Created**: 2026-06-22

**Status**: Draft

**Input**: User description: "I want support full web-app requirements, such as CSS, JavaScript, images, and other browser resources."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open a Complete Protected Web App (Priority: P1)

An authorized user opens a protected service and sees the complete downstream
application rather than only its initial page. Styles, scripts, images, fonts,
documents, and nested application routes load through the same protected service
entry.

**Why this priority**: A service is not usable when its initial page loads but
the resources required to render and operate it do not.

**Independent Test**: Open a representative protected application containing
relative and root-relative styles, scripts, images, fonts, and nested pages, then
verify the rendered application matches the directly reachable trusted version
without exposing an unprotected destination.

**Acceptance Scenarios**:

1. **Given** an authorized user opens a protected application, **When** its page
   references styles, scripts, images, and fonts, **Then** each resource loads and
   the application renders correctly within the protected service context.
2. **Given** an application uses nested pages and relative links, **When** the
   user follows those links or refreshes a nested page, **Then** the requested
   application page remains reachable through the protected service entry.
3. **Given** an application resource is missing or unavailable, **When** the
   browser requests it, **Then** the user receives the appropriate safe failure
   without portal internals or protected destinations being exposed.

---

### User Story 2 - Use Interactive and Stateful App Features (Priority: P2)

An authorized user can interact with the protected application normally,
including submitting forms, sending background data requests, using query
parameters, uploading and downloading files, following application redirects,
and maintaining application-specific state.

**Why this priority**: Correct rendering alone is insufficient for applications
whose primary value depends on data changes, navigation, or per-user state.

**Independent Test**: Use a representative protected application to submit a
form, complete a background data update, upload and download a file, follow an
internal redirect, and confirm its state remains isolated from other protected
services and users.

**Acceptance Scenarios**:

1. **Given** an authorized user submits data or triggers a background action,
   **When** the application processes the request, **Then** the response reaches
   the same application view with the intended result.
2. **Given** an application sets browser state, **When** the user makes later
   requests, **Then** the state is available only to the intended protected
   service and cannot replace or disclose the portal session.
3. **Given** an application redirects to another location within itself, **When**
   the browser follows the redirect, **Then** navigation stays inside the
   protected service context.
4. **Given** an application requests a download or accepts an upload, **When**
   the transfer completes, **Then** the content and filename are preserved and
   the transfer remains subject to the user's current authorization.

---

### User Story 3 - Maintain Protection During Advanced Traffic and Failures (Priority: P3)

An authorized user can use applications that stream updates or maintain
long-lived interactive connections, while expired access, permission changes,
downstream failures, and unsafe cross-service navigation are handled without
weakening the portal boundary.

**Why this priority**: Real-time behavior and resilient failure handling broaden
the range of supported services, but the core page and interaction flows deliver
value first.

**Independent Test**: Open a protected real-time application, exchange updates,
then revoke the user's permission and verify new activity is denied; separately
exercise timeout, disconnect, and unsafe redirect cases and verify safe recovery.

**Acceptance Scenarios**:

1. **Given** an authorized user opens a real-time application feature, **When**
   the application exchanges updates, **Then** the connection operates within
   the protected service context for as long as authorization remains valid.
2. **Given** a user's session expires or permission is revoked, **When** the user
   makes another application request or reconnects, **Then** access is denied
   before protected content is returned.
3. **Given** a downstream service times out, disconnects, or returns malformed
   routing information, **When** the portal handles the failure, **Then** the
   user receives a safe, actionable response and the event can be investigated
   without sensitive data exposure.

### Edge Cases

- An application mixes relative, root-relative, and fully qualified resource
  references.
- A user refreshes a deeply nested application route or opens it in a new tab.
- A resource request includes repeated query parameters, encoded path segments,
  or a trailing slash.
- An application returns a redirect to its own destination, another configured
  protected service, an untrusted public location, or a malformed location.
- Two protected services use browser-state names that collide.
- An application attempts to overwrite, read, or clear the portal session.
- A user's permission changes during an upload, download, stream, or real-time
  connection.
- A downstream response is compressed, cached, partially transferred, or
  requests a byte range.
- A script performs a background request using an application-root path rather
  than the currently displayed page path.
- A downstream service returns an error page, closes a connection early, or is
  unavailable after some resources have loaded.
- A page embeds a third-party resource or attempts navigation outside its
  configured protected-service boundary.
- Multiple users share a device and use the same downstream application after
  one user signs out.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST deliver a protected application's pages and nested
  routes through its configured service entry.
- **FR-002**: The system MUST deliver application resources required by standard
  browsers, including styles, scripts, images, fonts, documents, and media, with
  their content type and content preserved.
- **FR-003**: The system MUST resolve relative and application-root navigation
  so requests remain associated with the correct protected service.
- **FR-004**: The system MUST preserve query parameters, encoded path values,
  request bodies, and application responses needed for normal user interaction.
- **FR-005**: The system MUST support form submissions, background data actions,
  file uploads, and file downloads used by protected applications.
- **FR-006**: The system MUST preserve safe application response metadata needed
  for browser behavior, downloads, caching, partial transfers, and content
  presentation.
- **FR-007**: The system MUST keep internal application redirects within the
  protected service context and handle external or malformed redirects according
  to an explicit safe-navigation policy.
- **FR-008**: The system MUST isolate downstream application state by protected
  service and prevent it from replacing, reading, or invalidating portal access
  state.
- **FR-009**: The system MUST support long-lived and real-time application
  interactions where the configured downstream service requires them.
- **FR-010**: The system MUST provide a clear user-facing result for unavailable
  resources, downstream timeouts, interrupted transfers, and disconnected
  real-time interactions.
- **FR-011**: Administrators MUST be able to review whether a configured service
  supports the traffic patterns it requires and identify unsupported behavior
  before making it available to users.
- **FR-012**: Existing protected services that use only a single page or simple
  navigation MUST continue to work without reconfiguration.
- **FR-013**: The system MUST preserve accessibility behavior supplied by the
  downstream application, including keyboard operation, labels, focus behavior,
  and assistive-technology semantics.

### Security & Privacy Requirements *(mandatory for identity/access features)*

- **SPR-001**: The system MUST authenticate and authorize every protected page,
  resource, background action, upload, download, and connection before allowing
  access to the downstream service.
- **SPR-002**: The system MUST re-evaluate current session validity, user status,
  service enabled state, and access rules for each new protected request or
  connection attempt.
- **SPR-003**: The system MUST prevent a user from selecting an arbitrary
  destination, changing the configured downstream origin, crossing into another
  protected service, or using crafted paths and redirects to bypass access
  control.
- **SPR-004**: The system MUST separate portal access state from downstream
  application state and MUST prevent downstream state from being shared across
  unrelated services or users.
- **SPR-005**: The system MUST reject and audit denied, expired, malformed,
  cross-service, unknown-service, disabled-service, unsafe-redirect, and abusive
  traffic using non-sensitive reason codes.
- **SPR-006**: The system MUST NOT log or expose credentials, portal session
  identifiers, downstream secrets, private destination details, sensitive
  request bodies, sensitive response bodies, or unnecessary personal data.
- **SPR-007**: The system MUST remove or neutralize downstream response behavior
  that would expose internal destinations, weaken portal protections, or grant
  access outside the configured service boundary.
- **SPR-008**: Sign-out, expiry, user disablement, service disablement, and access
  rule changes MUST prevent future protected requests and reconnections, even
  when the browser has cached pages or application state.
- **SPR-009**: Security-relevant proxy decisions and failures MUST remain
  auditable under the existing minimum 90-day audit-retention policy without
  recording protected payloads.
- **SPR-010**: Existing controls for failed sign-in throttling, request
  correlation, and safe error disclosure MUST remain effective for proxied
  application traffic.

### Key Entities

- **Protected Application Request**: A browser request associated with an
  authenticated user and one configured service, including its nested path,
  query values, interaction type, and current authorization decision.
- **Protected Application Response**: Content and safe browser behavior returned
  by the configured service, associated with the originating protected request
  without revealing private destination details.
- **Downstream Application State**: Service-specific browser state required by a
  downstream application, isolated from portal access state, other services, and
  other users.
- **Application Connection**: A long-lived or real-time interaction associated
  with one authenticated user, one service entry, and a bounded authorization
  lifetime.
- **Proxy Audit Event**: A non-sensitive record of an allowed, denied, malformed,
  redirected, interrupted, or unavailable protected application interaction.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 98% of pages in the representative compatibility suite
  render with all required styles, scripts, images, and fonts through the portal.
- **SC-002**: At least 95% of representative application interactions—including
  navigation, data updates, uploads, downloads, redirects, and real-time
  updates—complete successfully without application-specific user workarounds.
- **SC-003**: 100% of tested page, resource, data, transfer, and connection
  attempts by signed-out, expired, disabled, or unauthorized users are blocked
  before protected content is returned.
- **SC-004**: 100% of tested attempts to select arbitrary destinations, escape a
  configured service boundary, or overwrite portal access state are rejected.
- **SC-005**: For 95% of normal local-network interactions, users perceive no
  more than 500 milliseconds of additional delay compared with the same trusted
  application accessed directly.
- **SC-006**: Downloads up to 100 MB and uploads up to 50 MB in the compatibility
  suite complete without corruption or sensitive data appearing in audit or
  diagnostic records.
- **SC-007**: At least 90% of administrators can determine whether a candidate
  application is compatible and make it available through the portal in under
  five minutes.
- **SC-008**: 100% of tested downstream failures provide an actionable user
  outcome and a correlatable, non-sensitive diagnostic or audit record.

## Assumptions

- Existing portal authentication, service enabled-state checks, group-based
  access rules, sign-out behavior, and audit-retention policy remain the source
  of truth.
- Downstream applications remain reachable only through the portal or a trusted
  internal network path; this feature does not make public downstream origins
  safe.
- The first compatibility target is standards-based browser applications that
  can operate beneath a protected service context; applications that hard-code
  unrelated public origins may require administrator-visible compatibility
  guidance.
- Standard browser page navigation, static resources, data interactions, forms,
  uploads, downloads, redirects, caching, partial transfers, and real-time
  connections are in scope.
- Third-party resources intentionally embedded by a downstream application may
  load only when allowed by the portal's safe-navigation and content policies;
  the portal does not authenticate independent third-party services.
- Native desktop protocols, raw network tunnels, and non-browser clients are out
  of scope for this feature.
- Active long-lived connections may finish or disconnect according to their
  established authorization lifetime, but every reconnect and new request is
  reauthorized.

