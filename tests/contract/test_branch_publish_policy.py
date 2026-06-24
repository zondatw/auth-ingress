from __future__ import annotations

import pytest

from scripts.release.validate_release import release_target
from tests.release_helpers import ALLOWED_BRANCH_TARGETS, DENIED_RELEASE_BRANCHES


def test_allowed_branches_map_to_exact_package_indexes():
    for branch, index in ALLOWED_BRANCH_TARGETS.items():
        assert release_target(branch) == index


def test_denied_branches_are_rejected_before_upload():
    for branch in DENIED_RELEASE_BRANCHES:
        with pytest.raises(ValueError, match="release-target-unsupported"):
            release_target(branch)
