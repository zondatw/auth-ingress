# Data Model: Rename Auth Ingress

This feature does not introduce new persisted application entities. It defines
rename-related identity records and validation categories used by release,
documentation, and compatibility checks.

## Product Identity

Represents the canonical public identity after the rename.

| Field | Meaning | Validation |
|-------|---------|------------|
| display_name | Human-readable product name | Uses `auth-ingress` or an approved title-cased equivalent in user-facing UI |
| distribution_name | Public package identity | Normalizes to `auth-ingress` |
| preferred_command | Primary CLI command | Exactly `auth-ingress` |
| repository_url | Canonical source URL | Points to the approved `auth-ingress` repository |
| documentation_name | Name used in current docs | Uses `auth-ingress` for current instructions |

## Compatibility Alias

Represents an old name that remains accepted during migration.

| Field | Meaning | Validation |
|-------|---------|------------|
| old_name | Previous visible or operator-facing name | One of the documented legacy names |
| new_name | Preferred replacement | Maps to `auth-ingress` equivalent |
| surface | Where the alias applies | CLI, environment configuration, repository redirect, package migration, docs, or historical evidence |
| behavior | What happens when old name is used | Accepted, redirected, warns, documented-only, or rejected with remediation |
| expiry_policy | Migration support window | Documented as one release cycle minimum where operator automation would otherwise break |

### State Transitions

```text
legacy-only -> dual-supported -> preferred-new -> legacy-retired
```

The implementation should only move a surface to `legacy-retired` when the
release notes and migration docs identify the retirement.

## Historical Reference

Represents an old-name occurrence that should remain understandable rather than
be rewritten.

| Field | Meaning | Validation |
|-------|---------|------------|
| value | Old-name text | Classified as historical or compatibility |
| location | Where it appears | Audit history, older spec, release notes, package history, logs, or compatibility docs |
| reason | Why it remains | Preserves evidence, avoids breaking existing credentials/sessions, documents migration, or explains previous releases |
| sensitivity | Whether it may include sensitive data | Must not include credentials, session IDs, reset secrets, or unnecessary personal data |

## Release Artifact

Represents the built distribution and verification output.

| Field | Meaning | Validation |
|-------|---------|------------|
| filename | Wheel/source archive name | Uses normalized `auth_ingress` file prefix after rename |
| metadata_name | Embedded package name | Normalizes to `auth-ingress` |
| commands | Installed command names | Includes preferred `auth-ingress`; compatibility `auth-portal` allowed |
| import_namespace | Runtime import name | Remains documented as `auth_ingress` unless a later plan changes it |
| smoke_result | Installed artifact validation | Confirms preferred command help and basic initialization behavior |

## Old-Name Scan Finding

Represents one detected old-name reference during validation.

| Field | Meaning | Validation |
|-------|---------|------------|
| token | Old name found | `auth-entry-portal`, `auth_ingress`, `auth-portal`, `Auth Entry Portal`, `Auth Portal`, `auth_portal`, or `AUTH_PORTAL` |
| file_or_artifact | Location | Source, docs, tests, release metadata, built artifact, generated docs, historical spec |
| classification | Required disposition | migrated, compatibility alias, historical reference, security-stable identifier, or intentional exception |
| owner_action | Next step | Update, document, test, or accept with reason |

No finding may remain unclassified before release.
