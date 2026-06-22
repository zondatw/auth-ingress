from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any, Mapping

from scripts.release.package_metadata import (
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
    clean: bool


def validate_release(
    context: ReleaseContext,
    document: Mapping[str, Any],
    *,
    root: Path = PROJECT_ROOT,
) -> PackageMetadata:
    if context.action != "published":
        raise ReleaseMetadataError("release-event-not-published")
    if context.target_commitish != "main":
        raise ReleaseMetadataError("release-target-not-main")
    if not context.clean:
        raise ReleaseMetadataError("release-input-not-clean")
    metadata = validate_project_metadata(document, root=root)
    validate_tag_matches(metadata, context.tag, prerelease=context.prerelease)
    return metadata


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
    parser.add_argument("--require-clean", action="store_true")
    arguments = parser.parse_args()
    context = ReleaseContext(
        action=arguments.action,
        tag=arguments.tag,
        prerelease=arguments.prerelease,
        target_commitish=arguments.target_commitish,
        clean=not arguments.require_clean or git_is_clean(),
    )
    metadata = validate_release(context, load_pyproject())
    print(f"validated {metadata.name} {metadata.version}")


if __name__ == "__main__":
    main()
