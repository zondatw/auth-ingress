# Research: Publish Auth Entry Portal to PyPI

## Distribution Name and Existing Names

**Decision**: Keep `auth-entry-portal` as the distribution name. Rename the Python
import namespace to `auth_entry_portal`; keep `auth-portal` as the executable and
`AUTH_PORTAL_*` as the configuration prefix.

**Rationale**: PyPI name normalization treats hyphens, underscores, and dots as
equivalent separators, but it does not remove the word `entry`. The occupied
[`auth-portal` project](https://pypi.org/project/auth-portal/) therefore does not
claim `auth-entry-portal`. Exact-name searches and direct project/simple-index
lookups found no current `auth-entry-portal` project. The repository already uses
that distribution name. Because no public release exists yet, aligning the import
namespace now avoids carrying the shorter conflicting name into the public
package while retaining stable CLI and configuration surfaces. PyPI is the final
authority, so registration must fail closed if the name is unavailable at release
setup time.

**Alternatives considered**:

- `service-entry-portal`: likely distinctive, but unnecessary after confirming
  the existing distribution name does not collide.
- Keep the old `auth_portal` import namespace: rejected because the canonical
  source and distribution naming should align before the first public release.
- Publish as `auth-portal`: rejected because that project is owned by another
  maintainer.

## Canonical Source Repository Name

**Decision**: The GitHub repository was renamed from `zondatw/auth_portal` to
`zondatw/auth-entry-portal` before configuring Trusted Publishers. The local
`origin` uses the new URL. Project URLs, documentation, badges, workflow
references, and publisher claims use the new repository identity. The Python
import namespace remains `auth_entry_portal`.

**Rationale**: Matching the repository and public distribution names reduces
operator ambiguity and makes source links easier to verify. Trusted Publishing
matches the repository claim exactly, so its configuration must use the final
repository name. Python imports are a separate compatibility surface and gain no
automatic behavior from the repository rename, so their explicit rename is
validated separately.

**Alternatives considered**:

- Keep `zondatw/auth_portal`: technically valid, but inconsistent with the chosen
  distribution identity and explicit product naming request.
- Couple the import rename implicitly to the repository operation: rejected
  because imports require an explicit source, test, and packaging migration.
- Rename the local checkout directory automatically: rejected because local paths
  are user-specific and do not affect GitHub, package metadata, or installation.

## CI and Release Workflow Shape

**Decision**: Add two top-level GitHub Actions workflows: `ci.yml` for pull
requests and main-branch pushes, and `release.yml` for published GitHub Releases.
The release workflow builds artifacts once, smoke-tests the wheel and source
archive, publishes them to TestPyPI, verifies the staged package, and then
promotes the same downloaded artifact set to PyPI after environment approval.

**Rationale**: A published GitHub Release is an explicit versioned approval
event. Separate build, TestPyPI publish, TestPyPI verification, and PyPI publish
jobs preserve least privilege and make the artifact handoff inspectable. The
[Python Packaging User Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
recommends distinct build and publish jobs, temporary artifact transfer, Trusted
Publishing, separate PyPI/TestPyPI environments, and manual approval for the
production environment. The PyPI publishing action explicitly discourages
building inside the OIDC-enabled publish job and supports only one upload target
per job.

**Alternatives considered**:

- Publish on every matching tag push: rejected because a published GitHub
  Release provides clearer maintainer intent and release notes.
- Build independently for TestPyPI and PyPI: rejected because the publicly
  uploaded bytes would differ from the staged candidate.
- One workflow job for build and publish: rejected because build scripts would
  run with unnecessary OIDC authority.
- Reusable publish workflow: rejected because PyPI Trusted Publishing does not
  currently support reusable workflows as the trusted publisher identity.

## Publishing Authentication and Approval

**Decision**: Use PyPI and TestPyPI Trusted Publishers bound to this repository,
the top-level `release.yml` workflow, and environments named `pypi` and
`testpypi`. Only the two publish jobs receive job-scoped `id-token: write`; all
other jobs receive `contents: read`. The `pypi` environment requires a reviewer,
prevents self-review where the repository plan supports it, restricts deployment
to version tags, and disables administrator bypass where available.

**Rationale**: [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
exchanges a GitHub OIDC identity for a short-lived project-scoped upload token,
eliminating stored PyPI API credentials. PyPI strongly recommends the official
[`pypa/gh-action-pypi-publish`](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
action with job-level OIDC permission. [GitHub environments](https://docs.github.com/actions/deployment/environments)
can enforce required reviewers and branch/tag restrictions before the publish
job starts.

**Alternatives considered**:

- Repository or environment API token: rejected because it is reusable and must
  be stored and rotated.
- Maintainer password: rejected because it is broadly scoped and unsuitable for
  automation.
- Grant OIDC permission at workflow scope: rejected because test and build jobs
  do not need publication authority.

## Build, Validation, and Versioning

**Decision**: Keep Hatchling as the build backend and use a pinned uv release for
locked dependency installation and `uv build`. Validate the existing test suite
on Python 3.12, 3.13, and 3.14; build exactly one wheel and one source archive;
check metadata and archive contents; install and smoke-test each artifact in an
isolated environment; and require the static project version to equal the GitHub
Release tag after removing the leading `v`.

**Rationale**: The project already uses Hatchling, uv, a lock file, and Python
`>=3.12`. The current [uv GitHub Actions guide](https://docs.astral.sh/uv/guides/integration/github/)
recommends the official setup action, pinned uv versions, locked sync, isolated
wheel/source smoke tests, and Trusted Publishing. Static version validation is
simple and prevents tag/artifact disagreement. Package-content tests are needed
because templates and static files are runtime requirements that ordinary source
tests can accidentally mask.

**Alternatives considered**:

- Introduce a release/version management framework: rejected as unnecessary for
  the first release and contrary to the smallest explicit architecture.
- Dynamic version from source-control metadata: rejected because it adds a build
  dependency and makes local artifact reproduction less explicit.
- Test only the newest Python: rejected because the published metadata promises
  every Python version from 3.12 upward that is currently supported by CI.

## Workflow Supply-Chain Controls

**Decision**: Pin every third-party GitHub Action to a reviewed full commit SHA
with a version comment, set default workflow permissions to read-only, use hosted
ephemeral runners, never execute artifact-provided scripts in an OIDC-enabled
job, enable dependency updates for action pins, retain release artifacts long
enough for promotion and investigation, and use the PyPI action's default
Trusted Publishing attestations.

**Rationale**: Full-SHA pins prevent a mutable action tag from silently changing
release code. The official PyPI action has enabled PEP 740 digital attestations
by default for Trusted Publishing, providing public provenance for each uploaded
artifact. GitHub describes attestations as signed claims tying artifacts to a
workflow, repository, commit, and event in its
[artifact attestation documentation](https://docs.github.com/en/actions/concepts/security/artifact-attestations).

**Alternatives considered**:

- Floating major-version action tags: easier to update but weaker against tag
  mutation; rejected for release jobs.
- A separate custom signing system: rejected because PyPI Trusted Publishing
  already provides supported attestations without another key lifecycle.
- Self-hosted release runners: rejected because their persistent state expands
  the trust boundary without a project requirement.

## Package Metadata and Licensing

**Decision**: Complete standards-based project metadata, including authors or
maintainers, keywords, classifiers, SPDX license expression and license file,
and well-known Homepage, Documentation, Source, Issues, Changelog, and Security
URLs. Publication remains blocked until the repository owner supplies or
approves the license and security contact content.

**Rationale**: The current metadata is insufficient for the public listing
required by the specification. The current
[`pyproject.toml` metadata specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
supports license expressions, license files, import-name declarations, and
project URLs; PyPA also defines standardized
[well-known URL labels](https://packaging.python.org/en/latest/specifications/well-known-project-urls/).
A license cannot be inferred safely as an engineering choice.

**Alternatives considered**:

- Infer MIT from common practice: rejected because license selection requires
  owner/legal approval.
- Publish without a license or security contact: rejected because it fails the
  public metadata contract and operator expectations.

## Failure, Retry, and Recovery

**Decision**: Do not use `skip-existing` for public PyPI. If an upload times out
or reports a duplicate, query the index and compare the expected version and
artifact hashes before any retry. Recover defective releases by yanking the
version, publishing a new version, documenting impact, and revoking the Trusted
Publisher binding if compromise is suspected; never overwrite or delete an
artifact as a retry mechanism.

**Rationale**: Public versions are immutable. Failing loudly on duplicates keeps
version mistakes visible, while hash verification distinguishes a completed
upload from a collision. The official publishing action recommends avoiding
`skip-existing` for public PyPI.

**Alternatives considered**:

- Silently skip duplicate uploads: rejected because a different artifact could
  already own the version.
- Delete and republish: rejected because PyPI versions are immutable and the
  behavior destroys trustworthy release identity.
