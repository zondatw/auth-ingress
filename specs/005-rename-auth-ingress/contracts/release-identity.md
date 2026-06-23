# Contract: Release Identity

## Package metadata

Release metadata must identify the distribution as `auth-ingress`.

Required fields:

- package/distribution name: `auth-ingress`;
- description: reflects an authenticated ingress/entry point for internal
  services;
- project URLs: canonical repository, documentation, issues, changelog, and
  security policy point at `zondatw/auth-ingress`;
- installed commands include `auth-ingress`;
- compatibility command `auth-portal` may remain.

## Artifact files

Built artifacts must use the normalized package filename prefix:

- `auth_ingress-<version>-py3-none-any.whl`
- `auth_ingress-<version>.tar.gz`

If the build backend normalizes differently, the release validation must record
the actual normalized value and confirm that embedded metadata still names the
project `auth-ingress`.

## Availability gate

Before publication:

1. Check PyPI exact package JSON endpoint for `auth-ingress`.
2. Check TestPyPI exact package JSON endpoint for `auth-ingress`.
3. Record result, timestamp, and fallback decision if either name is unavailable.

## Artifact smoke contract

An isolated installed artifact must prove:

1. `auth-ingress --help` succeeds.
2. `auth-portal --help` succeeds when compatibility command is retained.
3. Importing the documented runtime namespace succeeds.
4. `auth-ingress init-db` succeeds against a disposable database.
5. Artifact content includes templates/static files and excludes secrets,
   database files, and local build caches.
