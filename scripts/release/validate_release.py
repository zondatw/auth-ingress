from __future__ import annotations

import argparse
from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
import subprocess
from typing import Any, Mapping

from scripts.release.package_metadata import (
    BRANCH_TARGETS,
    PROJECT_ROOT,
    PackageMetadata,
    ReleaseMetadataError,
    load_pyproject,
    validate_project_metadata,
    validate_tag_matches,
)


@dataclass(frozen=True)
class ReleaseContext:
    action: str
    tag: str
    prerelease: bool
    target_commitish: str
    target_index: str
    clean: bool


def release_target(branch: str) -> str:
    try:
        return BRANCH_TARGETS[branch]
    except KeyError as exc:
        raise ReleaseMetadataError("release-target-unsupported") from exc


def validate_branch_target(context: ReleaseContext) -> str:
    resolved = release_target(context.target_commitish)
    if context.target_index and context.target_index != resolved:
        if context.target_index == "testpypi":
            raise ReleaseMetadataError("release-target-not-testpypi")
        if context.target_index == "pypi":
            raise ReleaseMetadataError("release-target-not-pypi")
        raise ReleaseMetadataError("release-target-unsupported")
    return resolved


def validate_release(
    context: ReleaseContext,
    document: Mapping[str, Any],
    *,
    root: Path = PROJECT_ROOT,
) -> PackageMetadata:
    if context.action != "published":
        raise ReleaseMetadataError("release-event-not-published")
    if not context.clean:
        raise ReleaseMetadataError("release-input-not-clean")
    target_index = validate_branch_target(context)
    metadata = validate_project_metadata(document, root=root)
    validate_tag_matches(metadata, context.tag, prerelease=context.prerelease)
    return replace(
        metadata,
        target_branch=context.target_commitish,
        target_index=target_index,
    )


def git_is_clean(root: Path = PROJECT_ROOT) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return not result.stdout.strip()


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise argparse.ArgumentTypeError("expected true or false")
    return normalized == "true"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an approved GitHub Release")
    parser.add_argument("--action", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--prerelease", required=True, type=parse_bool)
    parser.add_argument("--target-commitish", required=True)
    parser.add_argument("--target-index", default="")
    parser.add_argument("--require-clean", action="store_true")
    arguments = parser.parse_args()
    context = ReleaseContext(
        action=arguments.action,
        tag=arguments.tag,
        prerelease=arguments.prerelease,
        target_commitish=arguments.target_commitish,
        target_index=arguments.target_index,
        clean=not arguments.require_clean or git_is_clean(),
    )
    try:
        metadata = validate_release(context, load_pyproject())
    except ReleaseMetadataError as exc:
        raise SystemExit(str(exc)) from None
    print(
        "validated "
        f"{metadata.name} {metadata.version} "
        f"branch={metadata.target_branch} index={metadata.target_index}"
    )


if __name__ == "__main__":
    main()
