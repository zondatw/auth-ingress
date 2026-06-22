# Contract: Release Operations

## One-Time Setup

1. Verify `zondatw/auth-entry-portal` is the canonical GitHub repository and that
   local clone remotes, default branch, protections, issues, and source links use
   it.
2. Recheck that `auth-entry-portal` can be registered on PyPI and TestPyPI.
3. Obtain owner approval for the license, license file, maintainer identity,
   security contact, and all public project links.
4. Create pending Trusted Publishers on both indexes using the exact repository,
   `release.yml`, and environment claims from [ci-workflow.md](./ci-workflow.md).
5. Create `testpypi` and `pypi` GitHub environments and configure their tag and
   reviewer protections.
6. Require the CI workflow jobs on `main` before merge and release.
7. Confirm no `PYPI_API_TOKEN`, TestPyPI token, or maintainer password is stored
   in repository, organization, or environment secrets for this workflow.

Setup is incomplete until both pending publishers and both environment names
match the workflow exactly.

## Normal Release

1. Update the static project version and changelog on a reviewed branch.
2. Run the quickstart checks and merge only after required CI passes.
3. Create tag `v<version>` from the reviewed main revision.
4. Create and publish a GitHub Release for that tag with matching release notes.
5. Inspect the validate, build, TestPyPI publication, and staged-install evidence.
6. Confirm filenames, versions, source revision, and SHA-256 values.
7. A maintainer who satisfies the environment policy approves `pypi` promotion.
8. Verify the public listing, exact hashes, project links, attestations, and clean
   installation before declaring the release complete.

## Ambiguous or Failed Publication

1. Do not rerun upload automatically and do not enable public `skip-existing`.
2. Query the target index for the exact normalized name and version.
3. If absent after the documented propagation window, retain failure status and
   rerun only after a maintainer determines the upload did not complete.
4. If present, compare every filename and SHA-256 value with the workflow manifest.
5. Matching artifacts mean publication completed and only verification should be
   rerun. Any mismatch is a collision/security incident; stop immediately.
6. Record a safe outcome and reason code in the workflow/release history.

## Defective Release

1. Confirm impact and affected version without deleting files or editing history.
2. Yank the version with a concise public reason so resolvers avoid it by default.
3. Publish an advisory or release-note update with operator mitigation.
4. Prepare a fix using a strictly new version and run the complete release flow.
5. Verify the replacement before closing the incident. Do not unyank the original
   unless the original diagnosis was demonstrably incorrect.

## Suspected Publisher Compromise

1. Cancel pending release jobs and disable or remove both Trusted Publisher
   associations.
2. Review source-hosting release, environment approval, workflow, and index event
   histories; identify versions, revisions, and hashes involved.
3. Yank unauthorized or unverifiable releases and notify operators through the
   documented security contact/advisory path.
4. Review repository/environment access and workflow action pins before creating
   new publisher associations.
5. Re-establish OIDC trust only after the workflow and maintainer access are
   verified. Application passwords, sessions, and deployment secrets are not
   rotated unless separate evidence shows they were exposed.

## Audit and Retention

Retain GitHub Releases, workflow/deployment histories, approvals, artifact hash
manifests, and package-index upload/yank records for at least 90 days. Evidence
must exclude OIDC tokens, API credentials, application secrets, session values,
database contents, demo passwords, and unnecessary personal data.
