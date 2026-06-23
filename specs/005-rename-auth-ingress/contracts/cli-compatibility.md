# Contract: CLI Compatibility

## Preferred command

`auth-ingress` is the primary command for all current docs, help examples, and
release smoke checks.

Required subcommands:

- `auth-ingress --help`
- `auth-ingress init-db`
- `auth-ingress seed-demo`
- `auth-ingress serve`
- `auth-ingress bootstrap-admin`
- `auth-ingress users ...`

## Compatibility command

`auth-portal` remains accepted for at least one release cycle.

Required behavior:

1. It invokes the same behavior as `auth-ingress`.
2. It must not bypass actor authentication, hidden password entry, preview/apply
   semantics, CSRF protections, or rate limiting.
3. Help text or migration docs must identify `auth-ingress` as the preferred
   command.
4. Automation-safe outputs remain schema-compatible with current CLI contracts.

## Configuration precedence

When both configuration prefixes are present for the same setting:

1. `AUTH_INGRESS_*` wins.
2. `AUTH_PORTAL_*` remains accepted when the new prefix is absent.
3. Documentation must list both during migration and mark `AUTH_INGRESS_*` as
   preferred.

## Validation scenarios

- Preferred command help exits successfully.
- Compatibility command help exits successfully.
- Preferred and compatibility commands can initialize a disposable database.
- User-management command security behavior is identical under both command
  names.
- New-prefix configuration overrides old-prefix configuration for the same
  setting.
