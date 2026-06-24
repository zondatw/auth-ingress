# Contract: Release Workflow

## Workflow Outcomes

| Release target branch | Jobs that may publish | Jobs that must not publish |
|-----------------------|-----------------------|----------------------------|
| `beta` | TestPyPI publish and TestPyPI verification | PyPI publish and PyPI verification |
| `release` | PyPI publish and PyPI verification | TestPyPI publish and TestPyPI verification |
| Any other branch | None | TestPyPI and PyPI publish jobs |

## Permission Boundaries

- Workflow-level permissions do not include package-index identity tokens.
- Only active publish jobs receive package-index OIDC permission.
- Publish jobs do not checkout repository code.
- Publish jobs do not execute arbitrary repository commands.
- Static package-index secrets are not referenced by the workflow.
- `skip-existing` is not enabled for package publication.

## Validation Boundaries

Before upload, the workflow must validate:

- release action is a publication event;
- tag matches package version;
- prerelease flag matches version semantics;
- target branch maps to exactly one package index;
- package metadata uses the expected public identity;
- target package version does not already exist on the intended package index.

## Acceptance Tests

- Workflow contract tests prove branch conditions on publish and verify jobs.
- Security tests prove OIDC remains job-scoped and static secrets are absent.
- Unit tests prove invalid release contexts fail with safe reason codes.
