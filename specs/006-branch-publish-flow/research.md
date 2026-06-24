# Research: Branch Publish Flow

## Branch-to-index release model

**Decision**: Use exact branch names as the release target selector: `beta`
authorizes TestPyPI only and `release` authorizes PyPI only.

**Rationale**: The user requirement names the branches and target indexes
explicitly. Exact matching prevents accidental releases from similarly named
branches such as `beta-fix` or `release-candidate`.

**Alternatives considered**:

- Keep the current single GitHub Release path that publishes TestPyPI then PyPI:
  rejected because it no longer matches the requested branch separation.
- Use tag naming patterns such as `v*-beta` for TestPyPI and `v*` for PyPI:
  rejected because the requirement is branch-based.
- Use `main` for production publishing: rejected because the user requested
  `release` as the production branch.

## Workflow trigger and release target validation

**Decision**: Preserve GitHub Release publication as the maintainer-facing
release action, and validate the release target branch before any publish job
can run.

**Rationale**: The current project already has release validation, artifact
build, upload, verification, protected environments, and OIDC Trusted Publisher
coverage tied to GitHub Releases. Reusing that path minimizes moving parts while
adding the requested branch policy.

**Alternatives considered**:

- Push-triggered publication directly from branch pushes: rejected because
  release publication should remain an explicit maintainer action with release
  notes and durable evidence.
- Manual workflow dispatch only: rejected because it would bypass existing
  GitHub Release evidence and release notes unless additional controls were
  rebuilt.

## Separate publish paths

**Decision**: Split publish/verify jobs so TestPyPI jobs run only for `beta`
release targets and PyPI jobs run only for `release` release targets.

**Rationale**: A single release event must not accidentally publish to both
indexes. Job-level conditions make the intended target visible in workflow
evidence and keep OIDC permissions scoped to only the active publish job.

**Alternatives considered**:

- Always run TestPyPI before PyPI: rejected because a `release` branch production
  release should not publish a new staging artifact as part of the same request
  unless explicitly requested by branch policy.
- Keep both publish jobs but rely on environment approval to stop the wrong one:
  rejected because wrong-target jobs should not request protected environment
  approval at all.

## Duplicate-version handling

**Decision**: Validate target-index availability before upload and fail closed
when the target version already exists or the package-index state is ambiguous.

**Rationale**: Package indexes do not allow replacing an existing distribution
file safely. Early detection prevents wasted release approvals and avoids
ambiguous retry behavior.

**Alternatives considered**:

- Use publisher `skip-existing`: rejected because it can hide partial releases
  and conflicts with existing release policy.
- Delete and republish: rejected because published artifacts must be immutable.

## Evidence and secret handling

**Decision**: Record only non-sensitive release evidence: branch, target index,
version, artifact names, SHA-256 hashes, verification outcome, and reason codes.
Keep OIDC permissions job-scoped and keep publish jobs free of checkout/run
steps.

**Rationale**: Release troubleshooting needs enough detail to determine what was
published and why a release was blocked, without exposing tokens, credentials,
application secrets, sessions, or database data.

**Alternatives considered**:

- Add verbose package-index request/response logging: rejected because it risks
  leaking credentials or service-generated sensitive diagnostics.
- Store release evidence in application storage: rejected because release
  evidence is CI/CD operational data, not application runtime state.
