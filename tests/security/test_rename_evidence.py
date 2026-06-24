from pathlib import Path

from tests.rename_helpers import unclassified_findings


SCAN_ROOTS = (
    Path("README.md"),
    Path("docs"),
    Path(".github"),
    Path("src"),
    Path("tests"),
    Path("scripts"),
    Path("pyproject.toml"),
    Path("specs/003-publish-pypi"),
    Path("specs/004-manage-user-access"),
    Path("specs/005-rename-auth-ingress"),
)


def _paths() -> list[Path]:
    result: list[Path] = []
    for root in SCAN_ROOTS:
        if root.is_file():
            result.append(root)
        elif root.is_dir():
            result.extend(
                path
                for path in root.rglob("*")
                if path.is_file()
                and "__pycache__" not in path.parts
                and not path.name.endswith(".pyc")
            )
    return result


def test_old_name_references_are_classified():
    assert unclassified_findings(_paths()) == []

