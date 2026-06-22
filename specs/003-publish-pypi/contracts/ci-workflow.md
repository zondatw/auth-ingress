# Contract: GitHub Actions CI/CD

## Global Workflow Rules

- Workflow permissions default to `contents: read`.
- Every third-party action reference is pinned to a reviewed full commit SHA and
  carries a human-readable version comment.
- Jobs use GitHub-hosted ephemeral runners.
- Dependency caches contain no credentials or built release artifacts.
- Concurrency cancels obsolete CI runs but never cancels an active public publish
  after approval.
- Untrusted pull-request code never receives OIDC publication permission.
- Only dedicated publish jobs receive `id-token: write`; those jobs do not check
  out or execute repository code.

## Continuous Integration Workflow

**File**: `.github/workflows/ci.yml`

**Triggers**:

- Pull request targeting `main`.
- Push to `main`.
- Manual dispatch for maintainers.

**Required jobs**:

| Job | Inputs | Required checks | Permissions |
|-----|--------|-----------------|-------------|
| tests | Source + lock file; Python 3.12/3.13/3.14 matrix | Locked sync; complete non-browser suite | `contents: read` |
| browser-and-coverage | Source + lock file; newest supported Python | Chromium setup; complete suite; coverage report | `contents: read` |
| package | Source after tests | Build; metadata/content checks; isolated wheel and source smoke checks | `contents: read` |

All jobs fail closed. CI success is a branch/release prerequisite.

## Release Workflow

**File**: `.github/workflows/release.yml`

**Trigger**: GitHub Release `published`. Draft releases do not trigger. A
pre-release may publish only a valid pre-release version and remains non-default.

**Concurrency**: One run per release tag; no cancel-in-progress after public
approval begins.

| Job | Needs | Environment | Permission | Contract |
|-----|-------|-------------|------------|----------|
| validate | none | none | `contents: read` | Tag/version/name/metadata/license/release checks; required CI conclusion |
| build | validate | none | `contents: read` | Build once; check and smoke-test both artifacts; hash manifest; upload artifact |
| publish-testpypi | build | `testpypi` | `contents: read`, `id-token: write` | Download artifact only; publish once with official PyPI action |
| verify-testpypi | publish-testpypi | none | `contents: read` | Bounded propagation retry; install exact staged version; smoke test; compare metadata |
| publish-pypi | verify-testpypi | `pypi` | `contents: read`, `id-token: write` | Wait for reviewer; download same artifact; verify hashes; publish once |
| verify-pypi | publish-pypi | none | `contents: read` | Read-only public metadata/hash/provenance verification and summary |

The build artifact contains only the wheel, source archive, and SHA-256 manifest.
Artifact downloads use the run-local immutable artifact identifier, not a mutable
name from another run.

## Trusted Publisher Binding

Create separate pending publishers on PyPI and TestPyPI with exact claims:

- GitHub owner: `zondatw`.
- Repository: `auth-entry-portal`.
- Workflow file: `release.yml`.
- Environments: `pypi` and `testpypi`, respectively.
- Project: `auth-entry-portal`.

No API-token secret is a valid fallback. A publisher-claim mismatch stops the
release and requires configuration correction.

## Environment Protection

`pypi` MUST:

- require an approved maintainer reviewer;
- prevent self-review and administrator bypass where supported;
- permit only version-tag deployments;
- expose no long-lived package-index secret.

`testpypi` MUST permit only version-tag deployments. It may omit manual review,
but it has a separate Trusted Publisher and no authority over public PyPI.

## Failure Contract

- Validation/build/smoke/TestPyPI failures prevent the `pypi` job from becoming
  eligible for approval.
- A duplicate public version is an error, never silently skipped.
- An upload timeout produces `ambiguous` status and a read-only version/hash
  check; automation does not retry the upload blindly.
- Index propagation retries reads with a bounded timeout and never retries upload.
- Workflow summaries contain version, source revision, hashes, job outcomes, and
  safe reason codes only.
