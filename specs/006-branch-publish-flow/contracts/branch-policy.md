# Contract: Branch Publish Policy

## Branch Mapping

| Branch | Authorized target | Production status | Publish behavior |
|--------|-------------------|-------------------|------------------|
| `beta` | TestPyPI | Staging | Build, publish to TestPyPI, verify TestPyPI, do not publish to PyPI |
| `release` | PyPI | Production | Build, publish to PyPI, verify PyPI, do not publish to TestPyPI |

## Denied Branches

Any branch not exactly listed above is denied before upload.

Examples:

- `main`
- `006-branch-publish-flow`
- `beta-fix`
- `release-candidate`
- `releases`
- `hotfix`

## Required Safe Reasons

Branch policy failures use stable, non-sensitive reason codes:

- `release-target-not-beta-for-testpypi`
- `release-target-not-release-for-pypi`
- `release-target-unsupported`

## Acceptance Tests

- A `beta` release target authorizes TestPyPI and denies PyPI.
- A `release` release target authorizes PyPI and denies TestPyPI.
- Similar branch names are rejected.
- Rejection occurs before any package upload.
