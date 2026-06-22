# WebSocket Forwarding Contract

## Handshake

- Match a WebSocket request only on a known service host and non-reserved path.
- Require proxy-enabled and WebSocket-enabled service state, a valid service
  proxy credential, active central session and user, and a current access rule.
- Resolve and validate the fixed downstream destination before connecting.
- Preserve the path and raw query; convert only the validated destination scheme
  to its corresponding WebSocket scheme.
- Forward allowed application cookies after removing reserved portal/proxy
  cookies. Forward Origin as the configured public service origin or the
  administrator-approved downstream expectation, never a browser-selected host.
- Negotiate only a subprotocol offered by the browser and accepted downstream.
- Reject invalid/denied handshakes before accepting the browser connection.

## Frame Relay

- Relay text frames as text and binary frames as binary in both directions.
- Do not parse, log, audit, transform, or persist frame payloads.
- Supervise both relay directions so completion or failure in either direction
  cancels the other and closes both connections.
- Propagate normal close codes/reasons when safe; map internal failures to a
  generic server-error close without leaking destination details.

## Authorization Lifetime

- Every new handshake and reconnect is fully reauthorized.
- A connection expires no later than the central session expiry or configured
  maximum connection lifetime.
- Permission/service changes are guaranteed to affect reconnects immediately and
  active connections within the bounded lifetime.

## Audit and Diagnostics

- Audit denied, expired, unknown-service, disabled-service, unsafe-destination,
  and malformed handshakes with non-sensitive reason codes.
- Record connection start/end duration and generic close category as diagnostics,
  not frame data, cookies, query values, or destination details.

