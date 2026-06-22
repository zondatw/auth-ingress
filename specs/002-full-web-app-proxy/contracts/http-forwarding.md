# HTTP Forwarding Contract

## Request Mapping

For every non-reserved path on a known service host:

- Derive the service from Host and validate the service proxy credential and all
  current authorization state.
- Join the fixed service destination base path with the normalized browser path.
- Preserve the raw query string and supported methods: GET, HEAD, POST, PUT,
  PATCH, DELETE, and OPTIONS.
- Stream the request body; do not buffer, inspect, log, audit, or retry it.
- Browser-controlled input MUST NOT choose or alter upstream scheme, host, port,
  or base destination.

## Request Header Policy

Forward safe end-to-end headers required for content negotiation, conditional and
range requests, application behavior, and uploads. Apply these transformations:

- Remove `Connection` and every header it names, plus `Keep-Alive`,
  `Proxy-Authenticate`, `Proxy-Authorization`, `TE`, `Trailer`,
  `Transfer-Encoding`, and `Upgrade` from normal HTTP forwarding.
- Remove portal authorization, portal cookies, the reserved service proxy cookie,
  and any inbound forwarding headers not set by a trusted deployment proxy.
- Set Host from the configured downstream destination.
- Add sanitized forwarding context and the existing correlation identifier.
- Forward all non-reserved downstream application cookies unchanged in value.

## Response Mapping

- Preserve the upstream status code, including redirects, client errors, server
  errors, `206 Partial Content`, and `304 Not Modified`.
- Stream raw upstream bytes and always close the upstream response on completion,
  cancellation, or downstream disconnect.
- Preserve safe content negotiation, encoding, cache, validator, range, download,
  and presentation headers.
- Remove hop-by-hop fields, private upstream authentication challenges, internal
  forwarding fields, and internal destination disclosures.
- Do not add a second content encoding or compute a content length for a streamed
  body when the original length is no longer valid.

## Cookie Policy

- Preserve downstream cookie name/value, expiry, HttpOnly, Secure, SameSite, and
  valid Path behavior where compatible with the service origin.
- Remove an internal Domain attribute so the browser stores a host-only service
  cookie.
- Reject any downstream `Set-Cookie` that uses the reserved service proxy cookie
  name or a reserved portal-cookie prefix.
- Never forward the service proxy cookie to the downstream application.
- Preserve multiple `Set-Cookie` response fields as separate fields.

## Redirect Policy

- Relative redirects remain relative to the service origin.
- Absolute redirects targeting the configured downstream origin are rewritten to
  the public service origin with path, query, and fragment preserved.
- Redirects targeting another configured service, a public origin, a private
  origin other than the fixed destination, a credential-bearing URL, or an
  unsupported scheme are denied in version 1.
- A denied redirect returns a safe portal error and records
  `proxy_redirect_denied` without the target URL.

## Failure Policy

- Connect timeout or refused connection: 503 safe unavailable response.
- Upstream read timeout before response starts: 504 safe timeout response.
- Failure after streaming starts: close the browser response/connection and emit
  a correlatable diagnostic event; do not substitute content mid-stream.
- Client cancellation: cancel upstream streaming and close the response without
  recording payload data.
- No automatic retry of application requests.

