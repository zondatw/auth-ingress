# Research: Full Web-App Proxy Support

## Decision: Give Each Service a Separate Browser Origin

**Decision**: Serve protected applications from `<service-slug>.<proxy-domain>`.
Keep `/services/{slug}` as the portal launch route, but redirect authorized users
to the service origin after secure bootstrap.

**Rationale**: A browser origin is defined by scheme, host, and port. Separate
hosts let root-relative paths such as `/app.js`, `/api/items`, and `/ws` resolve
to the intended service without rewriting arbitrary HTML, CSS, or JavaScript.
They also isolate downstream cookies and browser storage by service. See the
[MDN origin definition](https://developer.mozilla.org/en-US/docs/Web/API/URL/origin).

**Alternatives considered**:

- Path prefix `/services/{slug}/{path}`: rejected as the primary design because
  root-relative URLs and JavaScript-generated requests escape the prefix, while
  reliable rewriting of arbitrary code is not feasible.
- Iframe embedding: rejected because frame restrictions, storage behavior,
  navigation, downloads, and application security policies break compatibility.
- Shared proxy origin with content rewriting: rejected because it creates cookie,
  storage, service-worker, and route collisions between applications.

## Decision: Bootstrap a Host-Only Service Session with a One-Time Ticket

**Decision**: After portal authorization, create a random, single-use, short-lived
launch ticket. The service host consumes it at a reserved bootstrap endpoint,
sets a reserved host-only HttpOnly proxy cookie bound to the portal session and
service, removes the ticket from the visible URL, and redirects to the app root.

**Rationale**: The existing host-only portal cookie is intentionally unavailable
to sibling service hosts. Sharing it with a parent-domain cookie would expose the
same high-value credential to every service origin. Host-only cookies provide
the narrowest browser scope; `__Host-` cookies additionally require Secure,
`Path=/`, and no Domain attribute in supporting browsers. See
[MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)
and [secure cookie guidance](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Cookies).

**Alternatives considered**:

- Parent-domain portal cookie: rejected because every service subdomain would
  receive the portal credential.
- Long-lived signed launch token in the query string: rejected because replay
  prevention and URL/referrer/log exposure are harder to control.
- Reauthentication on each service host: rejected because it creates unnecessary
  user friction and duplicates the portal login flow.

## Decision: Stream HTTP Requests and Responses End to End

**Decision**: Use one application-lifespan HTTPX `AsyncClient`. Forward the
browser method, raw query, selected end-to-end headers, and asynchronous request
body stream to the fixed destination. Return a Starlette `StreamingResponse`
over raw upstream bytes and close the upstream response in a background task.

**Rationale**: This supports forms, APIs, uploads, downloads, compression, and
range responses without buffering complete payloads in memory. HTTPX documents
shared clients for connection pooling, asynchronous request-body generators,
manual response streaming, and explicit response closure in forwarding
endpoints: [HTTPX async support](https://www.python-httpx.org/async/). Starlette
provides streaming responses for asynchronous iterators:
[Starlette responses](https://www.starlette.io/responses/).

**Alternatives considered**:

- Read full request/response bodies: rejected because 50 MB uploads, 100 MB
  downloads, media, and long responses would create avoidable memory pressure.
- Create a new client per request: rejected because it forfeits pooling and adds
  connection setup overhead.
- Automatically retry all failures: rejected because non-idempotent actions can
  be duplicated. Initial delivery performs no application-level retries.

## Decision: Apply Explicit Header, Cookie, and Redirect Policies

**Decision**: Remove hop-by-hop transport headers and all portal credentials;
set the downstream Host from the fixed destination; append correlation and
forwarded context without exposing private client data; preserve safe end-to-end
content/cache/range/download headers. Forward downstream cookies after removing
internal Domain attributes and rejecting the reserved proxy-cookie name. Rewrite
same-destination redirects to the public service origin and reject unapproved
cross-origin redirects.

**Rationale**: Proxy transport headers apply only to one connection and cannot be
blindly forwarded. Browser cookie Domain and Path determine where state is sent,
while host-only cookies prevent state from crossing service hosts. Redirects
must not disclose internal destinations or allow an application to bypass the
configured boundary. HTTP field semantics are defined in
[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html).

**Alternatives considered**:

- Forward every header unchanged: rejected because connection-specific fields,
  Host, portal cookies, and internal Location values are unsafe or incorrect.
- Drop all downstream cookies: rejected because many applications require state.
- Follow downstream redirects server-side: rejected because it hides navigation
  semantics and increases SSRF/cross-origin risk.

## Decision: Validate Destination Resolution on Every New Connection

**Decision**: Keep service destinations immutable during forwarding. Validate
the configured scheme/host/port, resolve all addresses before each new upstream
connection, reject public, loopback-unapproved, link-local, multicast, reserved,
and metadata-network addresses, and connect only to allowed private/trusted
addresses. Do not follow redirects automatically.

**Rationale**: Configuration-time string validation alone does not prevent DNS
rebinding or a trusted-looking name resolving to an unsafe address later. The
browser must never influence the upstream origin.

**Alternatives considered**:

- Trust `.internal` suffixes without resolution: rejected because DNS answers
  can change.
- Accept a destination URL from each browser request: rejected because that is
  an open proxy and SSRF primitive.
- Follow arbitrary redirects: rejected because redirect targets can cross the
  validated boundary.

## Decision: Proxy WebSockets with a Dedicated Bidirectional Relay

**Decision**: Add the maintained `websockets` client library. Authorize the
service-host handshake, connect only to the corresponding validated downstream
WebSocket URL, negotiate an allowed subprotocol, then relay text/binary frames
and close codes in two supervised asynchronous directions. Bound connections by
session expiry and a configurable maximum lifetime; reauthorize every reconnect.

**Rationale**: Starlette exposes WebSocket handshake, header, query, text/binary,
disconnect, and close primitives, but HTTPX is an HTTP client rather than a
WebSocket frame relay. See [Starlette WebSockets](https://www.starlette.io/websockets/)
and the [websockets asyncio client](https://websockets.readthedocs.io/en/stable/reference/asyncio/client.html).

**Alternatives considered**:

- Exclude WebSockets: rejected because the specification explicitly includes
  real-time applications.
- Tunnel raw upgraded connections through HTTPX: rejected because HTTPX does not
  expose a supported WebSocket frame API.
- Reauthorize every frame: rejected because it adds database load and does not
  create a meaningful new browser request boundary; connection lifetime plus
  reconnect authorization gives a bounded revocation window.

## Decision: Use a Representative Compatibility Fixture, Not App-Specific Rewrites

**Decision**: Build a local downstream fixture containing root-relative and
relative assets, nested navigation, JavaScript data calls, forms, cookies,
redirects, upload/download/range behavior, and WebSockets. Add an administrator
compatibility check that reports fixed absolute internal URLs, unsupported
schemes, unreachable destinations, redirect escapes, and handshake failures.

**Rationale**: Compatibility must be measurable before onboarding real services.
Apps that emit absolute internal origins must be configured with their public
service origin; silently rewriting arbitrary script content is unsafe and
unreliable.

**Alternatives considered**:

- Claim compatibility from a successful home-page request: rejected because it
  misses assets, state, interaction, and real-time behavior.
- Rewrite all textual responses: rejected because content types, compression,
  signatures, script semantics, and generated URLs make broad rewriting unsafe.

