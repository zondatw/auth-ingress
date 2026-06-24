# Research: Rename Auth Ingress

## Public package name availability

**Decision**: Plan to publish the distribution as `auth-ingress`, with a required
final PyPI and TestPyPI availability recheck immediately before release.

**Rationale**: On 2026-06-23, direct JSON checks returned 404 for both
`https://pypi.org/pypi/auth-ingress/json` and
`https://test.pypi.org/pypi/auth-ingress/json`, indicating no currently visible
project at that exact normalized name. Package indexes are mutable, so the
implementation must recheck before publishing.

**Alternatives considered**:

- Keep `auth-entry-portal`: rejected because the requested rename is to
  `auth-ingress`.
- Use a scoped or suffixed package name immediately: rejected unless final
  availability fails because it weakens the requested canonical identity.

## Repository name state

**Decision**: Treat `zondatw/auth-ingress` as the desired repository identity and
update local repository metadata/docs accordingly, while noting that the current
local remote still points to `git@github.com:zondatw/auth-entry-portal.git`.

**Rationale**: On 2026-06-23, `https://github.com/zondatw/auth-ingress` returned
200 and `https://github.com/zondatw/auth-entry-portal` returned 301. This
suggests the target repository identity already exists or has become the
canonical redirect target. The local remote and repository-facing documentation
still need alignment.

**Alternatives considered**:

- Keep repository docs on `auth-entry-portal`: rejected because it conflicts with
  the new public identity.
- Rename only package metadata: rejected because operators use repository URLs in
  release setup, incident recovery, and support material.

## Runtime import namespace

**Decision**: Keep `auth_ingress` as the Python import namespace for this
rename phase and document it as an internal compatibility namespace, while
changing public distribution and command identity to `auth-ingress`.

**Rationale**: The import namespace is referenced across all runtime modules and
tests. Renaming it would be a large mechanical change with higher breakage risk
and limited operator value. The project has already performed one import
namespace rename; preserving the current namespace reduces upgrade risk while
still satisfying the visible product rename.

**Alternatives considered**:

- Rename the import namespace to `auth_ingress`: rejected for this feature
  because it increases risk and churn without changing the operator-facing
  experience.
- Provide both import namespaces: rejected unless implementation discovers a
  concrete external import compatibility requirement.

## CLI compatibility

**Decision**: Add `auth-ingress` as the preferred command and retain
`auth-portal` as a compatibility command for at least one release cycle.

**Rationale**: Operators and tests currently use `auth-portal` in automation and
docs. A compatibility command avoids breaking existing runbooks while allowing
new documentation and help output to point users to `auth-ingress`.

**Alternatives considered**:

- Remove `auth-portal` immediately: rejected because it would break existing
  automation without functional benefit.
- Keep only `auth-portal`: rejected because it fails the requested rename.

## Configuration compatibility

**Decision**: Keep existing `AUTH_PORTAL_*` environment variables accepted and
introduce `AUTH_INGRESS_*` as the preferred configuration prefix. If both are
present, `AUTH_INGRESS_*` takes precedence and docs explain the migration.

**Rationale**: Configuration names are embedded in deployment environments and
secret managers. A prefix alias strategy lets operators migrate gradually without
changing authentication semantics. Precedence makes the preferred name
deterministic.

**Alternatives considered**:

- Rename all configuration variables with no aliases: rejected because it risks
  startup failures during upgrade.
- Never introduce new configuration names: rejected because primary operator
  surfaces would still expose old product identity.

## UI and security-stable identifiers

**Decision**: Rename user-facing product labels to `auth-ingress`, but preserve
historical records and security-stable internal identifiers unless the
identifier is purely presentational.

**Rationale**: Page titles, setup guidance, release docs, and command examples
should show the new product identity. Audit history, existing database values,
cookie names, and signed-token salts may contain old strings but changing them
can invalidate sessions or obscure history. Remaining old references must be
classified during validation.

**Alternatives considered**:

- Rewrite all old strings globally: rejected because it may break sessions,
  reset links, audit interpretation, and compatibility.
- Leave UI labels unchanged: rejected because it fails the operator-facing rename
  requirement.
