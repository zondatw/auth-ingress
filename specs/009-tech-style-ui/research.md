# Research: Tech Style UI Refresh

## Decision: Use a dark technical console visual direction

**Rationale**: The requested `agent-interlude` reference presents a monitoring
console impression: dark surface, dense operational context, cards, timelines,
metrics, and inspectable details. auth-ingress can adapt that direction to an
identity/access-control portal by emphasizing secure service access, admin
state, relationships, and safe diagnostic context.

**Alternatives considered**:

- Keep the current light generic admin style: rejected because it does not meet
  the requested "more tech style" direction.
- Copy the reference project's exact UI: rejected because auth-ingress has
  different users, data, security needs, and workflows.

## Decision: Keep the implementation server-rendered and local-static

**Rationale**: The current product is a small server-rendered application with
Jinja templates and one static CSS file. The requested change is visual and
interaction-level, not a need for a new frontend runtime. Keeping it local
preserves simplicity, avoids new supply-chain/availability risks, and fits the
existing package.

**Alternatives considered**:

- Add a client-side design framework: rejected because it increases complexity
  and is unnecessary for the required workflows.
- Use hosted fonts/icons/scripts: rejected because auth-ingress should render
  without third-party hosted assets.

## Decision: Add safe operational summaries only where existing data supports them

**Rationale**: Admin pages benefit from scan-friendly cards and relationship
summaries, but the feature must not introduce new persistence or sensitive
data exposure. Summaries should reuse existing users, groups, services, access
rules, and audit records.

**Alternatives considered**:

- Add a new dashboard data store: rejected because appearance and aggregate
  context do not justify schema or retention changes.
- Show raw audit/user/service internals everywhere: rejected because it hurts
  readability and increases privacy risk.

## Decision: Treat accessibility and security as part of the visual contract

**Rationale**: Dark technical themes can easily fail contrast, focus visibility,
and error clarity. auth-ingress also handles credentials, temporary passwords,
CSRF-protected forms, and destructive access changes. The design must make
those states more legible, not just more stylized.

**Alternatives considered**:

- Defer accessibility/security checks to implementation review: rejected
  because this feature touches every visible security-sensitive flow.
- Use color-only status language: rejected because users need accessible,
  unambiguous state cues.

## Decision: Use progressive enhancement for optional interaction polish

**Rationale**: Temporary-password copy behavior already uses small inline client
logic. Any new polish should keep core forms and navigation usable without
depending on complex client state.

**Alternatives considered**:

- Make rich dashboard interactions mandatory: rejected because the product must
  remain reliable for admin tasks and browser/security constraints.
- Avoid all client behavior: rejected because copy controls and simple
  interaction affordances are useful when implemented safely.
