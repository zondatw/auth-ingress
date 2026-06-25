# Contract: Page States and Operational Context

The refreshed UI must make operational state more scan-friendly while preserving
existing behavior.

## Required operational summaries

Where the data is already available or safely derivable, pages should show:

- visible/assigned services for the portal user;
- active/disabled user counts on user management surfaces;
- active/deactivated/unused group context on group management surfaces;
- enabled/disabled/proxy service context on service management surfaces;
- recent audit activity or empty audit state on audit surfaces;
- dependency/relationship summaries on user, group, and service detail pages.

## Required state presentations

Each state must have a distinct title, safe message, and next action when
appropriate:

- empty state;
- success/notice state;
- validation error state;
- access denied state;
- setup required state;
- destructive confirmation state;
- stale/conflict state;
- disabled/deactivated/unavailable state.

## Behavior constraints

- Form validation failures must preserve safe submitted values where current
  behavior already does so.
- Empty states must not look like broken tables or missing content.
- Relationship summaries must not expose information to unauthorized users.
- Operational summaries must degrade gracefully if a count or relationship is
  unavailable.
