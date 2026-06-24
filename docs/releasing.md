# Release auth-ingress

## Preconditions

- Staging releases target the exact `beta` branch and publish only to TestPyPI.
- Production releases target the exact `release` branch and publish only to PyPI.
- Branches such as `main`, feature branches, `beta-fix`, `release-candidate`,
  and `releases` are not publishable release targets.
- The release revision is on the intended publish branch and all required CI
  checks pass.
- `pyproject.toml` contains the intended static version and approved public
  metadata; `CHANGELOG.md` contains matching release notes and upgrade guidance.
- The GitHub tag is exactly `v<version>` and stable/pre-release status agrees with
  the version.
- PyPI and TestPyPI Trusted Publisher claims match
  `zondatw/auth-ingress`, `release.yml`, and their exact environment names.
- No package-index API token or maintainer password is stored in GitHub.

## Publish

1. Run the complete local package and installed-artifact checks.
2. Merge the reviewed version/changelog change to the intended publish branch:
   `beta` for staging or `release` for production.
3. Create the annotated `v<version>` tag from that branch revision.
4. Publish a GitHub Release with `target_commitish` set to the same branch and
   with matching release notes.
5. Inspect the one-time build's wheel, source archive, and SHA-256 manifest.
6. For `beta`, confirm TestPyPI receives those exact filenames and hashes and
   that an isolated exact-version installation passes; PyPI jobs must be skipped.
7. For `release`, confirm PyPI receives those exact filenames and hashes and
   verify public provenance identifies the expected repository, workflow, tag,
   and source revision; TestPyPI jobs must be skipped.
8. Preserve the branch, target index, version, artifact filenames, SHA-256
   hashes, verification result, and final outcome in release evidence.

Never overwrite a published file or version. Never use `skip existing` for public
publication. If an upload result is ambiguous, perform only read-only index/hash
verification before deciding whether another workflow run is safe.

## Branch Policy

| Branch | Target index | Required outcome |
|--------|--------------|------------------|
| `beta` | TestPyPI | Publish and verify staging package only |
| `release` | PyPI | Publish and verify production package only |

Wrong-branch and duplicate-version attempts must stop before upload with a safe
reason code. Prepare a new version for any retry that would otherwise overwrite
an uploaded file.

## Versioning and Evidence

Stable and pre-release versions follow Python version semantics. A correction
always uses a new version. Keep GitHub Releases, workflow/deployment history,
approvals, SHA-256 manifests, and index upload/yank records for at least 90 days.
Evidence must not contain tokens, application secrets, sessions, database data,
demo passwords, or unnecessary personal information.
