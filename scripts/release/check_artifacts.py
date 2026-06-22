from __future__ import annotations

import argparse
from dataclasses import dataclass
from email.parser import BytesParser
from hashlib import sha256
from pathlib import Path, PurePosixPath
import tarfile
from typing import Iterable
import zipfile

from packaging.version import Version

from scripts.release.package_metadata import EXPECTED_DISTRIBUTION, EXPECTED_IMPORT


FORBIDDEN_SOURCE_ROOTS = {
    ".agents",
    ".github",
    ".specify",
    ".env",
    "AGENTS.md",
    "memory",
    "tests",
}
REQUIRED_PUBLIC_FILES = {"CHANGELOG.md", "LICENSE", "README.md", "SECURITY.md"}
REQUIRED_RUNTIME_FILES = {
    f"{EXPECTED_IMPORT}/__init__.py",
    f"{EXPECTED_IMPORT}/web/static/portal.css",
    f"{EXPECTED_IMPORT}/web/templates/base.html",
}
FORBIDDEN_SECRET_VALUES = (
    b"demo-admin-password",
    b"demo-member-password",
    b"demo-outsider-password",
    b"PYPI_API_TOKEN",
)


class ArtifactValidationError(ValueError):
    """Raised when a release artifact violates the package contract."""


@dataclass(frozen=True)
class ArtifactReport:
    version: str
    hashes: dict[str, str]


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _metadata_from_wheel(path: Path):
    with zipfile.ZipFile(path) as archive:
        metadata_names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ArtifactValidationError("wheel-metadata-count")
        return BytesParser().parsebytes(archive.read(metadata_names[0])), set(archive.namelist())


def _source_names(path: Path) -> tuple[PurePosixPath, set[PurePosixPath]]:
    with tarfile.open(path, "r:gz") as archive:
        names = {PurePosixPath(name) for name in archive.getnames()}
    roots = {name.parts[0] for name in names if name.parts}
    if len(roots) != 1:
        raise ArtifactValidationError("source-root-count")
    return PurePosixPath(next(iter(roots))), names


def _contains_forbidden_values(wheel: Path, source: Path) -> bool:
    with zipfile.ZipFile(wheel) as archive:
        wheel_values = (
            archive.read(name)
            for name in archive.namelist()
            if not name.endswith("/")
        )
        if any(secret in value for value in wheel_values for secret in FORBIDDEN_SECRET_VALUES):
            return True
    with tarfile.open(source, "r:gz") as archive:
        for member in archive.getmembers():
            stream = archive.extractfile(member) if member.isfile() else None
            if stream is not None:
                value = stream.read()
                if any(secret in value for secret in FORBIDDEN_SECRET_VALUES):
                    return True
    return False


def inspect_artifacts(paths: Iterable[Path]) -> ArtifactReport:
    artifacts = tuple(Path(path) for path in paths)
    wheels = [path for path in artifacts if path.suffix == ".whl"]
    sources = [path for path in artifacts if path.name.endswith(".tar.gz")]
    if len(artifacts) != 2 or len(wheels) != 1 or len(sources) != 1:
        raise ArtifactValidationError("expected-one-wheel-and-one-source")

    wheel, source = wheels[0], sources[0]
    metadata, wheel_names = _metadata_from_wheel(wheel)
    if metadata["Name"] != EXPECTED_DISTRIBUTION:
        raise ArtifactValidationError("wheel-name-mismatch")
    version = metadata["Version"]
    if not version:
        raise ArtifactValidationError("wheel-version-missing")
    Version(version)
    expected_prefix = f"auth_entry_portal-{version}"
    if wheel.name != f"{expected_prefix}-py3-none-any.whl":
        raise ArtifactValidationError("wheel-filename-mismatch")
    if source.name != f"{expected_prefix}.tar.gz":
        raise ArtifactValidationError("source-filename-mismatch")
    if metadata["License-Expression"] != "MIT" or "LICENSE" not in metadata.get_all(
        "License-File", []
    ):
        raise ArtifactValidationError("wheel-license-metadata")
    if not REQUIRED_RUNTIME_FILES.issubset(wheel_names):
        raise ArtifactValidationError("wheel-runtime-files-missing")
    if any(name.startswith(("tests/", ".github/", ".specify/", ".agents/")) for name in wheel_names):
        raise ArtifactValidationError("wheel-forbidden-content")

    root, source_names = _source_names(source)
    required_source = {
        *(root / name for name in REQUIRED_PUBLIC_FILES),
        *(root / "src" / name for name in REQUIRED_RUNTIME_FILES),
        root / "pyproject.toml",
    }
    if not required_source.issubset(source_names):
        raise ArtifactValidationError("source-required-content-missing")
    if any(len(name.parts) > 1 and name.parts[1] in FORBIDDEN_SOURCE_ROOTS for name in source_names):
        raise ArtifactValidationError("source-forbidden-content")
    if _contains_forbidden_values(wheel, source):
        raise ArtifactValidationError("artifact-sensitive-value")

    return ArtifactReport(
        version=version,
        hashes={path.name: file_sha256(path) for path in sorted(artifacts)},
    )


def write_hash_manifest(report: ArtifactReport, path: Path) -> None:
    lines = [f"{digest}  {name}" for name, digest in sorted(report.hashes.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate release artifacts and write hashes")
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--manifest", type=Path)
    arguments = parser.parse_args()
    report = inspect_artifacts(arguments.artifacts)
    if arguments.manifest:
        write_hash_manifest(report, arguments.manifest)
    for name, digest in sorted(report.hashes.items()):
        print(f"{digest}  {name}")


if __name__ == "__main__":
    main()
