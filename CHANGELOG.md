# Changelog

All notable changes to Auth Entry Portal are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Authenticated entry portal with administrator-managed service access rules.
- Signed server-side sessions, Argon2 password hashing, CSRF protection, rate
  limiting, and non-sensitive audit events.
- Full web-application proxying for HTTP assets, interactions, streaming
  transfers, service-isolated cookies, redirects, and WebSockets.
- Package distribution under `auth-entry-portal` with the
  `auth_entry_portal` import namespace and `auth-portal` command.

### Changed

- Renamed the canonical GitHub repository to `zondatw/auth-entry-portal`.
- Renamed the Python import namespace from `auth_portal` to
  `auth_entry_portal` before the first public release.

### Upgrade Notes

- Source-based installations must update imports to `auth_entry_portal`.
- The `auth-portal` command, `AUTH_PORTAL_*` environment variables, cookie names,
  audit logger names, and default database filename remain unchanged.

[Unreleased]: https://github.com/zondatw/auth-entry-portal/commits/main
