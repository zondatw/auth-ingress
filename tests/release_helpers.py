from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import subprocess
import tomllib

import pytest


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_BRANCH_TARGETS = {
    "beta": "testpypi",
    "release": "pypi",
}
DENIED_RELEASE_BRANCHES = (
    "main",
    "006-branch-publish-flow",
    "beta-fix",
    "release-candidate",
    "releases",
    "hotfix",
)
TESTPYPI_EXISTING_VERSION = "0.1.0"
PYPI_EXISTING_VERSION = "0.1.0"


@dataclass(frozen=True)
class BuiltArtifacts:
    wheel: Path
    source: Path

    @property
    def all(self) -> tuple[Path, Path]:
        return self.wheel, self.source


def project_metadata() -> dict[str, object]:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        return tomllib.load(stream)["project"]


def artifact_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_built_artifacts(directory: Path) -> BuiltArtifacts:
    wheels = sorted(directory.glob("*.whl"))
    sources = sorted(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sources) != 1:
        raise AssertionError(
            f"expected one wheel and one source archive, found {wheels!r} and {sources!r}"
        )
    return BuiltArtifacts(wheel=wheels[0], source=sources[0])


@pytest.fixture(scope="session")
def built_artifacts(tmp_path_factory: pytest.TempPathFactory) -> BuiltArtifacts:
    output = tmp_path_factory.mktemp("release-dist")
    subprocess.run(
        ["uv", "build", "--out-dir", str(output)],
        cwd=ROOT,
        check=True,
        text=True,
    )
    return find_built_artifacts(output)
