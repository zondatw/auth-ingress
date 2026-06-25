# Changelog

All notable changes to auth-ingress are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-25

### Added

- Group management page for administrators to list, inspect, create, edit,
  deactivate, reactivate, and remove groups with dependency guardrails.
- Group lifecycle audit evidence and access-decision handling for deactivated
  groups.

### Changed

- Management forms now preserve safe submitted values and field-specific errors
  after validation failures.

## [0.1.0] - 2026-06-24

### Added

- Authenticated entry portal with administrator-managed service access rules.
- Signed server-side sessions, Argon2 password hashing, CSRF protection, rate
  limiting, and non-sensitive audit events.
- Full web-application proxying for HTTP assets, interactions, streaming
  transfers, service-isolated cookies, redirects, and WebSockets.
- Package distribution under `auth-ingress` with the `auth_ingress` import
  namespace, preferred `auth-ingress` command, and compatibility `auth-portal`
  command.

### Changed

- Renamed the canonical GitHub repository to `zondatw/auth-ingress`.
- Renamed the Python import namespace from `auth_portal` to
  `auth_ingress` before the first public release.

### Upgrade Notes

- Source-based installations must update imports from historical namespaces to
  `auth_ingress`.
- The `auth-portal` command and `AUTH_PORTAL_*` environment variables remain as
  compatibility aliases. Cookie names, audit logger names, and the default
  database filename may retain old internal labels to preserve security state.

[Unreleased]: https://github.com/zondatw/auth-ingress/compare/v0.2.0...main
[0.2.0]: https://github.com/zondatw/auth-ingress/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/zondatw/auth-ingress/releases/tag/v0.1.0
