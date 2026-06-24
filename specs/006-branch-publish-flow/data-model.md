# Data Model: Branch Publish Flow

## Release Branch

Represents the exact source branch that authorizes a package-index target.

| Field | Description | Validation |
|-------|-------------|------------|
| name | Branch name associated with the release request | Exactly `beta` or `release` for publishable releases |
| target_index | Package index authorized by the branch | `beta` maps to TestPyPI; `release` maps to PyPI |
| publish_scope | Whether the branch is staging or production | `beta` is staging; `release` is production |

### Rules

- Branch matching is exact and case-sensitive.
- Similar names such as `beta-fix`, `release-candidate`, and `releases` are not
  publishable.
- Branch policy is evaluated before any upload to a package index.

## Target Index

Represents the package index intended to receive release artifacts.

| Field | Description | Validation |
|-------|-------------|------------|
| name | Human-readable target | TestPyPI or PyPI |
| package_project | Public project identity | `auth-ingress` |
| environment | Protected publishing environment | `testpypi` for TestPyPI, `pypi` for PyPI |
| duplicate_policy | Behavior when version exists | Stop before upload and require a new version |

### Rules

- TestPyPI may only be targeted from `beta`.
- PyPI may only be targeted from `release`.
- Static package-index credentials are prohibited.

## Release Attempt

Represents one maintainer-initiated publication request.

| Field | Description | Validation |
|-------|-------------|------------|
| action | Maintainer release event | Must be a publication event |
| branch | Release Branch for the request | Must authorize the requested Target Index |
| tag | Version tag for the package | Must match the package version |
| version | Package version being published | Must not already exist on the target index |
| target_index | Intended package index | Derived from branch policy |
| prerelease | Whether the release is marked as prerelease | Must match package version semantics |
| clean_input | Whether the release input is internally consistent | Must be true before build/publish |
| outcome | Final result | `blocked`, `published`, `verified`, or `ambiguous` |
| reason | Safe failure or success reason | Must not include secrets or credentials |

### State Transitions

```text
requested
  -> blocked                # wrong branch, duplicate version, metadata mismatch, unsafe input
  -> validated              # branch/version/metadata checks pass
  -> built                  # artifacts and hashes produced
  -> published              # upload to authorized target completes
  -> verified               # target index metadata/hash/install checks pass
  -> ambiguous              # upload or index state cannot be determined safely
```

### Rules

- `blocked` attempts stop before upload.
- `ambiguous` attempts require read-only index/hash verification before retry.
- Reusing a published version is never allowed.

## Release Evidence

Non-sensitive proof of what happened during a Release Attempt.

| Field | Description | Validation |
|-------|-------------|------------|
| branch | Branch used for the request | Present for every attempt |
| target_index | Intended package index | Present for every attempt |
| version | Package version | Present for every attempt |
| artifact_names | Built distribution names | Present after build |
| sha256_hashes | Artifact integrity hashes | Present after build |
| verification_result | Index and install verification result | Present after verification or failure |
| final_outcome | Final release state | Present for every attempt |
| safe_reason | Non-sensitive success/failure reason | No tokens, credentials, sessions, secrets, or database data |

### Retention

- Release evidence is retained for at least 90 days.
- Evidence must support operator review of branch, target index, version,
  artifact names, hashes, verification result, and final outcome in under five
  minutes.
