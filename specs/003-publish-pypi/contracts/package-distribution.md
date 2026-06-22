# Contract: Package Distribution

## Stable Identities

| Surface | Required value |
|---------|----------------|
| PyPI/TestPyPI distribution | `auth-entry-portal` |
| Python import namespace | `auth_entry_portal` |
| Command-line executable | `auth-portal` |
| Configuration prefix | `AUTH_PORTAL_` |
| Wheel compatibility | `py3-none-any` |

The occupied PyPI name `auth-portal` is not used as the distribution identity.
Hyphens in the public distribution do not require a Python namespace rename.

## Version Contract

- `pyproject.toml` contains one static normalized version.
- A public release tag is `v<version>` and exactly matches package metadata.
- Stable and pre-release semantics follow standard Python version ordering.
- A version is published at most once and its files are never replaced.
- Duplicate versions fail loudly; `skip-existing` is prohibited for public PyPI.

## Artifact Contract

Every release produces exactly:

1. One source archive named for `auth-entry-portal` and the release version.
2. One universal wheel named for `auth-entry-portal`, the release version, and
   `py3-none-any` compatibility.

Both artifacts MUST include:

- all `auth_entry_portal` Python modules;
- all templates under `auth_entry_portal/web/templates/`;
- all static resources under `auth_entry_portal/web/static/`;
- package metadata, README, changelog, and owner-approved license file;
- the `auth-portal` entry point and complete runtime dependency metadata.

Tests, local databases, caches, coverage files, `.env` files, VCS history, CI
configuration, and credentials MUST NOT be installed as runtime package data. A
generic root `.gitignore` added by the build backend is permitted in the source
archive but is never installed by the wheel.

## Public Metadata Contract

The public metadata includes:

- name, version, one-line description, long description, and Python >=3.12;
- owner-approved SPDX license expression and included license file;
- maintainers/authors, relevant keywords, and accurate classifiers;
- Homepage, Documentation, Source, Issues, Changelog/Release Notes, and Security
  links using recognized project URL labels;
- declared `auth_entry_portal` import name and all runtime/optional dependencies.

Metadata links resolve to the canonical `zondatw/auth-entry-portal` repository.
Publication stops if required owner/legal/security content is missing or any
public link still identifies the former repository name.

## Installed-Package Smoke Contract

The wheel and source archive are tested separately in clean isolated environments
without access to the repository checkout. Each test MUST prove:

1. `import auth_entry_portal` succeeds.
2. `auth-portal --help` exits successfully and lists supported subcommands.
3. `auth-portal init-db` creates a disposable schema using an isolated path.
4. The application can be created and resolves every required template/static
   resource from the installed distribution.
5. Runtime imports do not depend on test or development extras.
6. Logs and errors contain no release credential, application secret, session,
   database content, or demo password.

The same checks run against the exact version installed from TestPyPI before
public approval.
