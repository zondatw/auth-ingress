# Security Policy

## Supported Versions

Until the first public release, only the latest revision on the default branch is
eligible for security fixes. After release, the latest minor release series will
receive security fixes; older series may be supported when an advisory states so.

| Version | Supported |
|---------|-----------|
| Unreleased default branch | Yes |
| Latest published minor series | Yes |
| Older published series | Advisory-specific |

## Reporting a Vulnerability

Report vulnerabilities privately through the repository's **Security** tab using
GitHub private vulnerability reporting:

https://github.com/zondatw/auth-entry-portal/security/advisories/new

Do not open a public issue for an unpatched vulnerability. Include the affected
version or revision, impact, reproduction details, and any suggested mitigation.
Do not include real passwords, session cookies, publisher tokens, private
database content, or unnecessary personal data.

Maintainers will acknowledge a complete report within five business days, assess
severity and affected versions, and coordinate remediation and disclosure. A
security advisory will identify fixed versions and operator actions when public
disclosure is appropriate.

## Release-Publisher Compromise

If a release, GitHub Actions workflow, Trusted Publisher binding, or package-index
artifact appears compromised, use the same private reporting path and label the
report **release publisher compromise**. Maintainers will cancel pending release
jobs, revoke publisher bindings, preserve non-sensitive evidence, assess
published hashes, yank unverifiable releases, and publish a corrected new version
when required. Application credentials are rotated only when evidence indicates
they were exposed.
