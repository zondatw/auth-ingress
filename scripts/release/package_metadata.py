from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib
from typing import Any, Mapping

from packaging.version import InvalidVersion, Version


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_DISTRIBUTION = "auth-ingress"
EXPECTED_IMPORT = "auth_entry_portal"
EXPECTED_REPOSITORY = "https://github.com/zondatw/auth-ingress"
EXPECTED_WHEEL_PREFIX = "auth_ingress"
PREFERRED_COMMAND = "auth-ingress"
COMPATIBILITY_COMMAND = "auth-portal"
REQUIRED_URLS = {"Homepage", "Documentation", "Source", "Issues", "Changelog", "Security"}
REQUIRED_FILES = {"LICENSE", "README.md", "CHANGELOG.md", "SECURITY.md"}


class ReleaseMetadataError(ValueError):
    """Raised when project or release metadata violates the public contract."""


@dataclass(frozen=True)
class PackageMetadata:
    name: str
    version: Version
    requires_python: str
    import_names: tuple[str, ...]
    urls: Mapping[str, str]


def normalize_distribution_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def load_pyproject(path: Path = PROJECT_ROOT / "pyproject.toml") -> dict[str, Any]:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def validate_project_metadata(
    document: Mapping[str, Any], *, root: Path = PROJECT_ROOT
) -> PackageMetadata:
    project = document.get("project")
    if not isinstance(project, Mapping):
        raise ReleaseMetadataError("missing-project-metadata")

    name = project.get("name")
    if not isinstance(name, str) or normalize_distribution_name(name) != EXPECTED_DISTRIBUTION:
        raise ReleaseMetadataError("unexpected-distribution-name")

    raw_version = project.get("version")
    if not isinstance(raw_version, str) or "version" in project.get("dynamic", ()):
        raise ReleaseMetadataError("version-must-be-static")
    try:
        version = Version(raw_version)
    except InvalidVersion as exc:
        raise ReleaseMetadataError("invalid-version") from exc

    imports = project.get("import-names")
    if imports != [EXPECTED_IMPORT]:
        raise ReleaseMetadataError("unexpected-import-names")

    scripts = project.get("scripts")
    if not isinstance(scripts, Mapping):
        raise ReleaseMetadataError("missing-console-scripts")
    expected_target = f"{EXPECTED_IMPORT}.cli:main"
    if scripts.get(PREFERRED_COMMAND) != expected_target or scripts.get(COMPATIBILITY_COMMAND) != expected_target:
        raise ReleaseMetadataError("unexpected-console-scripts")

    if project.get("license") != "MIT" or project.get("license-files") != ["LICENSE"]:
        raise ReleaseMetadataError("missing-approved-license")

    urls = project.get("urls")
    if not isinstance(urls, Mapping) or not REQUIRED_URLS.issubset(urls):
        raise ReleaseMetadataError("missing-project-urls")
    if any(not str(urls[key]).startswith(EXPECTED_REPOSITORY) for key in REQUIRED_URLS):
        raise ReleaseMetadataError("noncanonical-project-url")

    missing_files = sorted(path for path in REQUIRED_FILES if not (root / path).is_file())
    if missing_files:
        raise ReleaseMetadataError(f"missing-public-files:{','.join(missing_files)}")

    requires_python = project.get("requires-python")
    if not isinstance(requires_python, str) or not requires_python:
        raise ReleaseMetadataError("missing-python-requirement")

    return PackageMetadata(
        name=name,
        version=version,
        requires_python=requires_python,
        import_names=tuple(imports),
        urls={str(key): str(value) for key, value in urls.items()},
    )


def version_from_tag(tag: str) -> Version:
    if not tag.startswith("v") or tag == "v":
        raise ReleaseMetadataError("release-tag-must-start-with-v")
    try:
        return Version(tag[1:])
    except InvalidVersion as exc:
        raise ReleaseMetadataError("invalid-release-tag-version") from exc


def validate_tag_matches(metadata: PackageMetadata, tag: str, *, prerelease: bool) -> None:
    tag_version = version_from_tag(tag)
    if tag_version != metadata.version:
        raise ReleaseMetadataError("tag-version-mismatch")
    if prerelease != metadata.version.is_prerelease:
        raise ReleaseMetadataError("release-type-mismatch")


def load_and_validate(path: Path = PROJECT_ROOT / "pyproject.toml") -> PackageMetadata:
    return validate_project_metadata(load_pyproject(path), root=path.parent)
