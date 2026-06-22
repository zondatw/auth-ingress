# Data Model: PyPI Release Publication

This feature adds no application database tables. The entities below describe
immutable release and workflow state held by source hosting and package indexes.

## Package Release

Represents one uniquely versioned release of `auth-entry-portal`.

| Field | Description | Validation |
|-------|-------------|------------|
| distribution_name | Public package identity | Exactly `auth-entry-portal` after name normalization |
| version | Public immutable version | Valid normalized Python version; equals source metadata and release tag without `v` |
| release_tag | Approved source reference | Exactly `v<version>` and points to the published GitHub Release commit |
| source_revision | Source commit identifier | Full immutable revision associated with the tag |
| release_type | Stable or pre-release | Derived from version; pre-releases cannot be default stable installs |
| release_notes | User-visible changes and upgrade notes | Non-empty before public approval |
| status | Current lifecycle state | Draft, validated, staged, approved, published, failed, or yanked |
| created_at | Release creation time | Supplied by source hosting |
| published_at | Public publication time | Present only for published/yanked releases |
| yank_reason | Operator-facing withdrawal reason | Required only when yanked; contains no secrets |

### State Transitions

```text
Draft -> Validated -> Staged -> Approved -> Published -> Yanked
   \          \          \         \
    +----------+----------+---------+-> Failed
```

- `Validated` requires all tests, metadata checks, archive checks, and isolated
  artifact smoke tests.
- `Staged` requires both exact artifacts to exist on TestPyPI and pass an exact
  staged-install smoke test.
- `Approved` requires the protected `pypi` environment gate.
- `Published` requires both exact artifacts and their expected hashes on PyPI.
- `Yanked` never returns to `Published`; a correction uses a new version.

## Release Artifact

Represents one immutable output belonging to a Package Release.

| Field | Description | Validation |
|-------|-------------|------------|
| filename | Artifact filename | Normalized distribution/version; unique within release |
| kind | Wheel or source archive | Exactly one of each per release |
| size | Byte length | Positive and stable across handoffs |
| sha256 | Artifact integrity digest | 64 lowercase hexadecimal characters |
| package_version | Embedded metadata version | Equals Package Release version |
| package_name | Embedded distribution name | Normalizes to `auth-entry-portal` |
| content_manifest | Included file list | Contains runtime modules, templates, static assets, metadata, README, and license |
| validation_result | Artifact check outcome | All metadata, content, and isolated smoke checks pass |
| source_revision | Producing revision | Equals Package Release source revision |

### Relationships

- Each Package Release owns exactly two Release Artifacts.
- Both TestPyPI and PyPI receive the same two artifact byte streams and hashes.
- No artifact may be reused by another version or replaced after publication.

## Release Approval

Represents permission to move one staged release into public publication.

| Field | Description | Validation |
|-------|-------------|------------|
| release_version | Approved version | References one Staged Package Release |
| artifact_hashes | Approved artifact set | Exactly matches staged workflow artifact manifest |
| environment | GitHub protected environment | Exactly `pypi` for public publication |
| source_revision | Approved source | Matches artifacts and release tag |
| reviewer_context | Source-hosting approval record | Maintainer-visible; not copied into package metadata |
| approved_at | Approval time | After staged verification and before public upload |

Approval is single-release evidence, not a reusable publisher credential.

## Publication Event

Represents non-sensitive operational evidence for release investigation.

| Field | Description | Allowed values/content |
|-------|-------------|------------------------|
| event_type | Lifecycle action | validation, staging, approval, publication, verification, failure, yank, revocation |
| release_version | Related public version | Valid version or absent before version parsing |
| source_revision | Related source commit | Full revision when known |
| workflow_run | Source-hosting run identifier | Non-secret link or identifier |
| artifact_hashes | Expected/published digests | SHA-256 only; never artifact bodies |
| outcome | Coarse result | allowed, denied, succeeded, failed, ambiguous |
| reason_code | Non-sensitive diagnosis | Enumerated stable code; no token, body, or personal data |
| occurred_at | Event time | Source or index timestamp |

Publication Events are retained through GitHub and package-index histories for at
least 90 days. They never include OIDC tokens, API tokens, application secrets,
database contents, session values, demo passwords, or unnecessary personal data.
