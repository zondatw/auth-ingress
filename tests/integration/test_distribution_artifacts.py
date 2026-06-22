from __future__ import annotations

from email.parser import BytesParser
from pathlib import PurePosixPath
import tarfile
import zipfile

from scripts.release.check_artifacts import inspect_artifacts
from tests.release_helpers import (
    BuiltArtifacts,
    artifact_sha256,
    built_artifacts,
    project_metadata,
)


def test_artifact_names_counts_hashes_and_metadata(built_artifacts: BuiltArtifacts):
    version = project_metadata()["version"]
    assert built_artifacts.wheel.name == f"auth_entry_portal-{version}-py3-none-any.whl"
    assert built_artifacts.source.name == f"auth_entry_portal-{version}.tar.gz"
    assert all(len(artifact_sha256(path)) == 64 for path in built_artifacts.all)
    report = inspect_artifacts(built_artifacts.all)
    assert report.version == version
    assert len(report.hashes) == 2


def test_wheel_contains_runtime_assets_and_public_metadata(built_artifacts: BuiltArtifacts):
    with zipfile.ZipFile(built_artifacts.wheel) as archive:
        names = set(archive.namelist())
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = BytesParser().parsebytes(archive.read(metadata_name))
    assert "auth_entry_portal/__init__.py" in names
    assert "auth_entry_portal/web/static/portal.css" in names
    assert "auth_entry_portal/web/templates/base.html" in names
    assert metadata["Name"] == "auth-entry-portal"
    assert metadata["License-Expression"] == "MIT"
    assert "LICENSE" in metadata.get_all("License-File", [])


def test_source_archive_is_minimal_and_complete(built_artifacts: BuiltArtifacts):
    with tarfile.open(built_artifacts.source, "r:gz") as archive:
        names = {PurePosixPath(name) for name in archive.getnames()}
    root = PurePosixPath(f"auth_entry_portal-{project_metadata()['version']}")
    assert root / "src/auth_entry_portal/__init__.py" in names
    assert root / "src/auth_entry_portal/web/templates/base.html" in names
    assert root / "src/auth_entry_portal/web/static/portal.css" in names
    assert root / "README.md" in names
    assert root / "CHANGELOG.md" in names
    assert root / "SECURITY.md" in names
    assert root / "LICENSE" in names
    forbidden = {".agents", ".github", ".specify", "tests", "memory", ".env", ".git"}
    assert not any(path.parts[1] in forbidden for path in names if len(path.parts) > 1)
