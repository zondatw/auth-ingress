# Quickstart: Validate PyPI Publication

This guide validates packaging and release behavior without publishing an
unapproved public version. Complete local artifact checks first, then validate the
GitHub/TestPyPI path, and approve PyPI only for an intended release.

## Prerequisites

- Python 3.12, 3.13, and 3.14 available to CI; one supported version locally.
- Current uv and Chromium for the existing browser suite.
- Maintainer access to `zondatw/auth-entry-portal`, PyPI, and a separate TestPyPI
  account.
- Owner-approved `LICENSE`, security contact, maintainer metadata, and public
  project links.
- Exact package name `auth-entry-portal` still accepted by both package indexes.

Do not create PyPI API-token secrets. This design uses OIDC Trusted Publishing.

## Validate Source and Locked Tests

```bash
uv sync --locked --extra test
uv run playwright install chromium
uv run pytest --cov=auth_entry_portal
```

Expected outcome: the existing auth, proxy, security, and real-browser suites pass
without modifying `uv.lock`; release logs contain no credentials or application
secrets.

## Build and Inspect Artifacts

Start with an empty `dist/`, then build and validate exactly one wheel and one
source archive:

```bash
uv build
uvx --from twine twine check dist/*
uv run pytest tests/contract/test_package_contract.py
uv run pytest tests/integration/test_distribution_artifacts.py
```

Expected outcome:

- filenames and embedded metadata use `auth-entry-portal` and the project version;
- the wheel is `py3-none-any`;
- both artifacts include `auth_entry_portal`, all templates/static files, README,
  changelog, and approved license;
- neither artifact includes tests, databases, caches, environment files, secrets,
  or repository metadata.

## Smoke-Test Installed Artifacts

Run the installed-package smoke test once for each artifact in an isolated
environment, not against the repository checkout:

```bash
uv run --isolated --no-project --with dist/auth_entry_portal-*.whl tests/smoke/test_installed_package.py
uv run --isolated --no-project --with dist/auth_entry_portal-*.tar.gz tests/smoke/test_installed_package.py
```

Expected outcome: `auth_entry_portal` imports, `auth-portal --help` succeeds, disposable
database initialization succeeds, and installed templates/static resources are
found. The test finishes within 5 minutes per clean environment.

## Configure Trusted Publishing

1. Verify this clone uses the canonical renamed repository:

   ```bash
   git remote -v
   ```

2. Verify the default branch, branch protections, issues, and public source links
   after the rename.
3. Create pending publishers for `auth-entry-portal` on PyPI and TestPyPI.
4. Bind both to owner `zondatw`, repository `auth-entry-portal`, workflow
   `release.yml`, and environments `pypi` or `testpypi` respectively.
5. Create both GitHub environments and restrict them to version tags.
6. Require a reviewer for `pypi`; prevent self-review and administrator bypass
   where supported.
7. Make the CI workflow jobs required on `main`.

Expected outcome: no long-lived package-index credential exists. A mismatched
repository, workflow, environment, or package claim cannot mint upload authority.

## Validate CI

Open a pull request containing only a harmless documentation change.

Expected outcome:

- locked tests pass on Python 3.12, 3.13, and 3.14;
- the newest-version browser/coverage job passes;
- the package job builds, inspects, and independently smoke-tests both artifacts;
- no pull-request job has `id-token: write` or access to a publish environment.

Then intentionally test a version/tag mismatch and a removed template in a
non-release branch. The relevant package checks must fail before any publish job
can run.

## Validate TestPyPI Candidate

For a new pre-release version reserved for validation:

1. Merge the reviewed version and changelog update.
2. Create tag `v<version>` at that main revision.
3. Publish a GitHub pre-release with matching release notes.
4. Observe validation, one-time build, TestPyPI publication, and staged install.
5. Reject or cancel the `pypi` environment approval so the candidate is not
   promoted during this rehearsal.

Expected outcome: TestPyPI contains one source archive and one wheel with the
workflow-recorded hashes; the exact staged version installs and passes smoke
checks. A pre-release is not selected by a normal stable install.

## Validate Public Promotion

For the approved initial public release, repeat the release flow with the intended
stable version. Review the staging evidence and approve the protected `pypi` job.

Expected outcome:

- PyPI receives the same filenames and SHA-256 hashes tested on TestPyPI;
- the public listing contains required metadata and links;
- provenance/attestations identify the expected repository, workflow, tag, and
  revision;
- a fresh `auth-entry-portal==<version>` install passes the smoke test;
- the complete staged-to-public flow takes no more than 15 minutes excluding
  index delays and human approval time.

## Exercise Failure and Recovery

Before the initial stable release, rehearse these cases without uploading a public
version:

- duplicate version and ambiguous timeout verification;
- invalid metadata, missing asset, failed test, and source/tag mismatch;
- rejected production environment approval;
- TestPyPI propagation delay with bounded read-only retry;
- documented yank/new-version response for a defective candidate;
- Trusted Publisher revocation after a simulated publisher compromise.

Expected outcome: every invalid or unauthorized case stops before public upload,
no upload is retried blindly, and workflow evidence contains only safe version,
revision, hash, outcome, and reason-code data.
