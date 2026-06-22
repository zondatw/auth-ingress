# Data Model: Full Web-App Proxy Support

## Existing Entities Used Without Ownership Changes

### User

The existing authenticated person. `status` must be `active` for launch, every
new HTTP request, and every WebSocket handshake.

### GroupMembership and AccessRule

Existing user-to-group and service-to-group relationships. They are re-read for
every new proxy authorization decision so changes take effect without creating a
new portal session.

### Session

The existing central portal session remains the source of truth. Service-host
authentication references it but never creates an independent authorization
lifetime.

Relevant rules:

- Expired or revoked sessions deny launch, bootstrap, requests, and handshakes.
- Sign-out revokes the central session; service-host cookies may remain in the
  browser but become unusable immediately on their next request.
- A service-host credential expires no later than the central session.

### AuditEvent

The existing non-sensitive security event record gains reason/event values for:

- `proxy_launch_created`, `proxy_launch_consumed`, `proxy_launch_denied`
- `proxy_request_denied`, `proxy_websocket_denied`
- `proxy_redirect_denied`, `proxy_upstream_unavailable`
- `proxy_compatibility_checked`

No event stores tickets, cookies, session identifiers, destinations, request or
response bodies, query values, filenames, or downstream state.

## ServiceEntry Extensions

Represents the fixed downstream application and its public proxy policy.

**New fields**:

- `proxy_enabled`: Whether full web-app forwarding is enabled for this service.
- `websocket_enabled`: Whether WebSocket handshakes may be forwarded.
- `external_redirect_policy`: `deny` for version 1; reserved for a future
  administrator-managed allowlist.
- `compatibility_status`: `unchecked`, `compatible`, `limited`, or `failed`.
- `compatibility_checked_at`: Timestamp of the latest check.
- `compatibility_summary`: Non-sensitive reason codes from the latest check.

**Derived values**:

- `public_host`: `<slug>.<configured proxy base domain>`; never accepted from a
  browser request or stored as an independently editable destination.
- Downstream HTTP/WebSocket URLs: derived from the fixed validated destination
  plus the browser path and raw query.

**Validation rules**:

- Existing slug uniqueness and URL-safety rules define the service host label.
- Proxying requires an enabled service, at least one valid access rule, a trusted
  internal destination, and a configured proxy base domain.
- The destination cannot contain credentials, query parameters, or fragments.
- WebSockets cannot be enabled unless full proxying is enabled.
- Compatibility results do not grant access and cannot override authorization.

**State transitions**:

- `proxy_enabled false -> true`: Allowed after configuration validation; new
  launches use the service origin.
- `proxy_enabled true -> false`: New launches and proxy requests are denied;
  existing long-lived connections close within their bounded lifetime.
- `unchecked -> compatible|limited|failed`: Compatibility check result.
- Any material destination or proxy-policy change -> `unchecked`.

## ProxyLaunchTicket

One-time bridge from an authenticated portal origin to a host-only service
origin.

**Fields**:

- `id`: Stable internal identifier.
- `token_digest`: One-way digest of the random browser token; the raw token is
  never stored.
- `session_id`: Reference to the existing central portal session.
- `service_entry_id`: Service the ticket may bootstrap.
- `created_at`: Creation timestamp.
- `expires_at`: Short expiry timestamp, default 60 seconds.
- `consumed_at`: Timestamp of successful one-time consumption.
- `request_context`: Minimal allowlisted correlation/client category context.

**Relationships**:

- Belongs to exactly one `Session` and one `ServiceEntry`.

**Validation rules**:

- Token digest is unique.
- Raw tokens never appear in logs, audits, diagnostic messages, or database
  records.
- Ticket service must match the service host consuming it.
- Session, user, service, and access rule are revalidated at consumption.
- Expired, consumed, unknown, mismatched, or unauthorized tickets are rejected
  with the same non-sensitive user outcome.

**State transitions**:

- `issued -> consumed`: First valid bootstrap request.
- `issued -> expired`: Time passes beyond `expires_at`.
- Consumed and expired tickets never return to `issued` and are periodically
  deleted after their audit investigation window.

## Service Proxy Credential (Browser State, Not Persisted)

A signed, host-only, HttpOnly cookie created after launch-ticket consumption.

**Claims**:

- Central session reference.
- Service entry reference.
- Issued-at and expiry bounded by the central session.
- Credential format/version.

**Validation rules**:

- Valid only on the service host that set it.
- Service claim must match the request Host-derived service.
- Signature, expiry, central session, user, service enabled state, and access
  rule are checked before forwarding.
- Reserved cookie name is removed before downstream forwarding and cannot be set
  or cleared by downstream responses.

## Protected Application Request (Transient)

**Fields**:

- Service determined exclusively from validated Host.
- Method or connection type.
- Raw path and query.
- Selected safe headers.
- Streaming body or bidirectional frames.
- Correlation identifier and current authorization result.

**Validation rules**:

- Browser input can modify path/query/body but never scheme, host, port, or base
  destination.
- Dot-segment, encoded-separator, malformed-host, and cross-service ambiguity are
  rejected before forwarding.
- Request body is streamed and never added to logs/audits.

## Protected Application Response (Transient)

**Fields**:

- Status or WebSocket close result.
- Selected end-to-end headers.
- Streaming bytes or frames.
- Rewritten safe redirect and cookie metadata.

**Validation rules**:

- Hop-by-hop fields and internal destination disclosures are removed.
- Reserved portal/proxy cookies cannot be overwritten.
- Same-destination redirects map to the service origin; other redirects are
  denied under the version 1 policy.
- Response bodies are streamed without audit/log capture.

