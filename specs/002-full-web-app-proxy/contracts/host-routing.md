# Host Routing Contract

## Deployment Hosts

- Portal UI: `https://<portal-host>/`
- Protected service: `https://<service-slug>.<proxy-base-domain>/`
- Wildcard DNS and TLS MUST cover `*.<proxy-base-domain>`.
- The portal host MUST NOT be accepted as a protected service host, and unknown
  service hosts MUST fail closed.

## Portal Launch

### `GET /services/{service_slug}` on the portal host

1. Validate the portal session, active user, enabled service, proxy-enabled
   state, and current access rule.
2. On success, create a random one-time launch ticket with a maximum 60-second
   lifetime and redirect to:
   `https://{service_slug}.{proxy-base-domain}/__portal/bootstrap?ticket=<opaque>`.
3. Send `Cache-Control: no-store` and a restrictive referrer policy.
4. On signed-out access, preserve the existing safe return path through sign-in.
5. On denial, do not create a ticket or disclose the internal destination.

## Service Bootstrap

### `GET /__portal/bootstrap?ticket=...` on a service host

1. Derive the service only from the validated request host.
2. Hash and look up the ticket; require matching service, unconsumed state,
   unexpired state, valid central session, active user, enabled/proxy-enabled
   service, and current access rule.
3. Atomically mark the ticket consumed.
4. Set a reserved host-only, HttpOnly, Secure, SameSite=Lax service proxy cookie
   with `Path=/` and an expiry no later than the central session.
5. Redirect to `/` without the ticket and with `Cache-Control: no-store`.
6. Return the same safe denial for unknown, expired, consumed, mismatched, and
   unauthorized tickets; never echo or log the token.

## Direct Service-Host Access

- A request without a valid service proxy cookie redirects to the portal launch
  route for that same known service.
- An unknown or malformed service host returns a generic 404 without redirecting
  to a browser-controlled host or service.
- Reserved `__portal/*` paths are never forwarded downstream.

## Sign-Out and Revocation

- Portal sign-out revokes the central session.
- Service-host cookies do not need cross-host deletion to become ineffective;
  the next request or reconnect revalidates and denies the revoked session.
- Denial responses clear the local service proxy cookie when safe to do so.

