# Service Compatibility Contract

## Administrator Check

An administrator can run a non-mutating compatibility check for a configured
service before enabling full proxying.

The check reports these categories without exposing destination details to
ordinary users:

- Destination resolution and trusted-network eligibility.
- Initial page reachability and timeout behavior.
- Same-origin relative and root-relative asset compatibility.
- Absolute internal-origin references requiring downstream public-origin
  configuration.
- Internal, external, malformed, and unsupported redirect behavior.
- Cookie attributes that can or cannot be safely represented on the service host.
- Optional WebSocket handshake availability when enabled.
- Overall status: `compatible`, `limited`, or `failed`, with non-sensitive reason
  codes and operator guidance.

## Safety Rules

- The check uses only the service's fixed configured destination.
- It does not submit forms, mutate application data, follow external redirects,
  store downstream bodies, or execute downstream scripts.
- It applies the same destination resolution and header policy as live proxying.
- Results never grant access or override service enabled/access-rule decisions.
- A material destination or proxy-policy change resets status to `unchecked`.

## Version 1 Compatibility Boundary

Supported applications use relative/root-relative URLs or can be configured with
their public service origin. Applications that embed fixed private origins in
script-generated requests are reported as `limited` or `failed`; arbitrary code
rewriting is not promised.

