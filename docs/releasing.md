# Release auth-ingress

## Preconditions

- The release revision is on `main` and all required CI checks pass.
- `pyproject.toml` contains the intended static version and approved public
  metadata; `CHANGELOG.md` contains matching release notes and upgrade guidance.
- The GitHub tag is exactly `v<version>` and stable/pre-release status agrees with
  the version.
- PyPI and TestPyPI Trusted Publisher claims match
  `zondatw/auth-ingress`, `release.yml`, and their exact environment names.
- No package-index API token or maintainer password is stored in GitHub.

## Publish

1. Run the complete local package and installed-artifact checks.
2. Merge the reviewed version/changelog change to `main`.
3. Create the annotated `v<version>` tag from that revision.
4. Publish a GitHub Release with the matching release notes.
5. Inspect the one-time build's wheel, source archive, and SHA-256 manifest.
6. Confirm TestPyPI receives those exact filenames and hashes and that an isolated
   exact-version installation passes.
7. Approve the protected `pypi` environment only after staging evidence passes.
8. Confirm PyPI filenames and SHA-256 values match TestPyPI and the workflow
   manifest, and verify public provenance identifies the expected repository,
   workflow, tag, and source revision.

Never overwrite a published file or version. Never use `skip existing` for public
publication. If an upload result is ambiguous, perform only read-only index/hash
verification before deciding whether another workflow run is safe.

## Versioning and Evidence

Stable and pre-release versions follow Python version semantics. A correction
always uses a new version. Keep GitHub Releases, workflow/deployment history,
approvals, SHA-256 manifests, and index upload/yank records for at least 90 days.
Evidence must not contain tokens, application secrets, sessions, database data,
demo passwords, or unnecessary personal information.
