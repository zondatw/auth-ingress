# Research: Auth Entry Portal

## Decision: Use a Single Server-Rendered Web Application

**Rationale**: The feature is a small internal portal with straightforward user
and administrator flows. A single server-rendered application keeps the first
version easier to secure, test, deploy, and review than a separate frontend and
API service. It also centralizes session handling, authorization checks, audit
events, and service-entry decisions in one trust boundary.

**Alternatives considered**:

- Separate frontend and backend: rejected for initial scope because it adds
  cross-origin session complexity and more moving parts without clear user value.
- Static portal plus backend auth API: rejected because protected downstream
  service entry requires server-side authorization decisions.

## Decision: Protect Services Through Portal-Controlled Entry Routes

**Rationale**: Downstream services do not have their own auth flow. A plain link
directory cannot block users who know the downstream URL. The portal must be the
only user-facing path to protected services, either by forwarding service traffic
through authenticated routes or by launching only destinations that are otherwise
network-restricted from direct user access.

**Alternatives considered**:

- Redirect users directly to public downstream URLs: rejected because direct URLs
  would bypass the portal.
- Require every downstream service to implement auth: rejected because it
  contradicts the feature goal.

## Decision: Use SQLite for the Initial Mini Portal Store

**Rationale**: The initial scope is small and internal. SQLite is enough for local
validation, simple deployment, and early iteration over users, service entries,
access rules, sessions, and audit events. The data model avoids database-specific
behavior so a later move to PostgreSQL remains possible.

**Alternatives considered**:

- PostgreSQL from day one: viable for production scale, but unnecessary for the
  first mini portal unless deployment requirements demand it.
- File-based configuration only: rejected because admin-managed service entries,
  access rules, sessions, and audit records need controlled persistence.

## Decision: Use Group-Based Access Rules for Version 1

**Rationale**: Group-based rules are understandable for administrators and map
well to the user story: assign a service to a set of eligible users. The model
also allows future expansion to user-specific or policy-expression rules without
changing the core service-entry flow.

**Alternatives considered**:

- User-by-user allow lists only: rejected because they become hard to maintain
  as service count grows.
- Arbitrary policy language: rejected for version 1 because it increases review
  and testing complexity.

## Decision: Use Non-Sensitive Structured Audit Events

**Rationale**: The constitution requires observability without exposing secrets
or unnecessary personal data. Audit records should capture actor identity,
service entry, event type, decision, timestamp, and request correlation data
while excluding passwords, session identifiers, raw secrets, and full sensitive
payloads.

**Alternatives considered**:

- Application logs only: rejected because audit review needs durable,
  queryable event records.
- Full request/response capture: rejected because it risks collecting secrets
  and personal data.

## Decision: Rate-Limit Failed Sign-In Attempts

**Rationale**: The portal is an authentication boundary, so repeated failed
sign-in attempts must be throttled to reduce abuse while preserving a legitimate
retry path. The first version can use account and client-context counters with
clear user-facing messaging.

**Alternatives considered**:

- No throttling: rejected because it weakens the auth boundary.
- Immediate hard lockout: rejected because it can create denial-of-service risk
  against legitimate users.
