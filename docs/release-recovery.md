# Release Recovery

## Defective Release

1. Start an investigation and record the version, source revision, filenames,
   SHA-256 values, impact, and non-sensitive workflow outcome.
2. Yank the defective version with a concise public reason so new resolution
   avoids it by default. Preserve the original files and evidence; never overwrite
   or delete and republish them.
3. Notify operators through release notes and a GitHub Security Advisory when the
   defect has security impact. Include mitigation and affected/fixed versions.
4. Correct the defect and publish a strictly new version through the complete
   staged and protected release process.
5. Verify the replacement before closing the investigation. Do not unyank the
   original unless the diagnosis was demonstrably incorrect.

## Suspected Publisher Compromise

1. Cancel pending release workflow runs and revoke the PyPI and TestPyPI Trusted
   Publisher associations.
2. Review GitHub access, environment approvals, action pins, release history, and
   index records. Preserve evidence for at least 90 days.
3. Compare all affected artifact SHA-256 values and provenance with the approved
   source revisions. Yank unverifiable or unauthorized versions.
4. Notify operators privately first when disclosure would expose an unpatched
   vulnerability, then publish coordinated guidance and fixed versions.
5. Re-establish Trusted Publisher bindings only after maintainer access,
   environments, workflow code, and repository settings are verified.

Publisher authority is separate from runtime application credentials. Do not
rotate user passwords, portal sessions, database secrets, or deployment keys
unless the investigation finds evidence that those assets were exposed.

## Ambiguous Upload or Duplicate

Do not retry an upload blindly. Query the exact name/version, compare every
filename and SHA-256 value with the workflow manifest, and classify the outcome:

- **Absent**: no release is visible after the bounded propagation window;
  maintainers decide whether a new workflow run is safe.
- **Completed**: all filenames and hashes match; rerun verification only.
- **Collision**: any identity, filename, or hash differs; stop publication,
  revoke authority if compromise is plausible, and investigate.

## Blocked Branch Publish

Branch policy blocks before upload when a staging release is not targeted at
`beta`, a production release is not targeted at `release`, or a similar branch
name such as `beta-fix`, `release-candidate`, or `releases` is used. Record the
safe reason code, branch, target index, version, and release URL. Do not change
environment approvals or Trusted Publisher settings to bypass the policy.

If a version exists on the target index, treat it as immutable. Compare
read-only index metadata and hashes with the workflow manifest. If the files
match, rerun verification only. If the files differ or the state is ambiguous,
stop, investigate, and prepare a new version for any corrected release.
