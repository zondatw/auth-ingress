# Contract: Release Evidence

## Required Evidence Fields

Every release attempt records:

- release target branch;
- target package index;
- package version;
- final outcome;
- safe reason code for success or failure.

After build, evidence also records:

- wheel filename;
- source archive filename;
- SHA-256 hash for each artifact.

After verification, evidence also records:

- package-index metadata result;
- hash comparison result;
- isolated install smoke result;
- provenance result when available for the target.

## Redaction Rules

Evidence must not contain:

- package-index tokens;
- OIDC tokens;
- maintainer passwords;
- application secrets;
- session cookies;
- database content;
- demo passwords;
- unnecessary personal data.

## Retention

Release evidence is retained for at least 90 days through workflow logs,
artifacts, package-index metadata, and release records.

## Acceptance Tests

- Runbooks mention branch-to-index mapping, immutable versions, SHA-256 evidence,
  blocked-release recovery, and 90-day retention.
- Security tests scan workflow and release docs for forbidden credential
  patterns.
- Quickstart validation records branch, target index, version, hashes,
  verification outcome, and final outcome without secrets.
