# Contract: Naming Matrix

## Canonical names

| Surface | Preferred value | Compatibility value | Required behavior |
|---------|-----------------|---------------------|-------------------|
| Product display | `auth-ingress` | Historical `Auth Entry Portal` / `Auth Portal` | Current UI and docs use preferred value |
| Package distribution | `auth-ingress` | `auth-entry-portal` | Preferred package metadata uses new value; migration docs explain previous releases |
| CLI command | `auth-ingress` | `auth-portal` | Preferred command is installed and documented; compatibility command remains accepted |
| Repository URL | `zondatw/auth-ingress` | `zondatw/auth-entry-portal` redirect or historical URL | Current docs use preferred URL; historical references may remain in old specs |
| Configuration prefix | `AUTH_INGRESS_*` | `AUTH_PORTAL_*` | Preferred prefix takes precedence; old prefix remains accepted during migration |
| Python import namespace | `auth_entry_portal` | N/A | Remains stable and documented as runtime import namespace |
| Cookie and token internal labels | Existing stable names unless changed deliberately | Existing values | Must not change in a way that breaks active sessions or signed flows without an explicit migration decision |

## UI contract

Current primary UI surfaces must use `auth-ingress` in:

- base page title fallback;
- header brand;
- sign-in, setup-required, reset/change-password, portal, admin services, admin
  users, audit, and access-denied page titles;
- first-install setup guidance command examples.

Historical old names may only appear in migration documentation or tests that
explicitly assert compatibility.

## Documentation contract

Current operator instructions must use:

- `pip install auth-ingress`;
- `auth-ingress --help`;
- `auth-ingress init-db`;
- `auth-ingress bootstrap-admin`;
- `auth-ingress serve`;
- `AUTH_INGRESS_*` environment variables.

Documentation must include a migration section mapping old names to new names.

## Old-name scan contract

Validation must scan source, tests, docs, release scripts, metadata, workflows,
and built artifacts for old-name tokens. Every finding must be classified as one
of:

- migrated;
- compatibility alias;
- historical reference;
- security-stable identifier;
- intentional exception.

Unclassified findings fail release validation.
