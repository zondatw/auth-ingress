from __future__ import annotations

from copy import deepcopy

import pytest

from scripts.release.package_metadata import load_pyproject
from scripts.release.validate_release import ReleaseContext, validate_release


def valid_context(**changes) -> ReleaseContext:
    values = {
        "action": "published",
        "tag": "v0.1.0",
        "prerelease": False,
        "target_commitish": "main",
        "clean": True,
    }
    values.update(changes)
    return ReleaseContext(**values)


def test_valid_stable_release_passes():
    metadata = validate_release(valid_context(), load_pyproject())
    assert str(metadata.version) == "0.1.0"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"action": "created"}, "release-event-not-published"),
        ({"tag": "0.1.0"}, "release-tag-must-start-with-v"),
        ({"tag": "v0.2.0"}, "tag-version-mismatch"),
        ({"prerelease": True}, "release-type-mismatch"),
        ({"target_commitish": "feature"}, "release-target-not-main"),
        ({"clean": False}, "release-input-not-clean"),
    ],
)
def test_invalid_release_context_fails_with_safe_reason(changes, reason):
    with pytest.raises(ValueError, match=reason):
        validate_release(valid_context(**changes), load_pyproject())


def test_wrong_package_name_and_missing_metadata_fail():
    document = deepcopy(load_pyproject())
    document["project"]["name"] = "auth-portal"
    with pytest.raises(ValueError, match="unexpected-distribution-name"):
        validate_release(valid_context(), document)


def test_prerelease_requires_matching_prerelease_version():
    document = deepcopy(load_pyproject())
    document["project"]["version"] = "0.2.0rc1"
    context = valid_context(tag="v0.2.0rc1", prerelease=True)
    metadata = validate_release(context, document)
    assert metadata.version.is_prerelease
