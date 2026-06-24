from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path

from scripts.release.package_metadata import (
    EXPECTED_DISTRIBUTION,
    EXPECTED_IMPORT,
    EXPECTED_REPOSITORY,
    load_and_validate,
)
from tests.release_helpers import ROOT, project_metadata


def test_distribution_import_and_cli_names_are_stable():
    project = project_metadata()
    assert project["name"] == EXPECTED_DISTRIBUTION
    assert project["import-names"] == [EXPECTED_IMPORT]
    assert project["scripts"] == {
        "auth-ingress": "auth_ingress.cli:main",
        "auth-portal": "auth_ingress.cli:main",
    }
    assert (ROOT / "src" / EXPECTED_IMPORT).is_dir()
    assert not (ROOT / "src" / "auth_entry_portal").exists()
    assert not (ROOT / "src" / "auth_portal").exists()
    assert find_spec(EXPECTED_IMPORT) is not None
    assert find_spec("auth_entry_portal") is None
    assert find_spec("auth_portal") is None


def test_public_metadata_and_runtime_dependency_contract():
    metadata = load_and_validate()
    project = project_metadata()
    assert str(metadata.version) == project["version"]
    assert metadata.requires_python == ">=3.12"
    assert all(url.startswith(EXPECTED_REPOSITORY) for url in metadata.urls.values())
    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]
    assert project["dependencies"]
    assert set(project["optional-dependencies"]) == {"test"}
    assert all("pytest" not in dependency for dependency in project["dependencies"])


def test_required_public_files_are_present():
    for relative in ("README.md", "CHANGELOG.md", "SECURITY.md", "LICENSE"):
        path = Path(ROOT, relative)
        assert path.is_file() and path.stat().st_size > 0
