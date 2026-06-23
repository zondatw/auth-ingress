from pathlib import Path

from tests.fixtures.rename_inventory import ALLOWED_CLASSIFICATIONS, INTENTIONAL_OLD_NAME_REFERENCES
from tests.rename_helpers import unclassified_findings


def test_old_name_inventory_classifications_are_known():
    assert INTENTIONAL_OLD_NAME_REFERENCES
    assert set(INTENTIONAL_OLD_NAME_REFERENCES.values()) <= ALLOWED_CLASSIFICATIONS


def test_current_primary_files_have_no_unclassified_old_names():
    paths = [
        Path("pyproject.toml"),
        Path("README.md"),
        Path("docs/releasing.md"),
        Path("docs/user-management.md"),
        Path("src/auth_entry_portal/config.py"),
    ]
    assert unclassified_findings(paths) == []

