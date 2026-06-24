from __future__ import annotations

import pytest

from scripts.release.verify_index import (
    IndexOutcome,
    IndexVerificationError,
    compare_release,
    poll_release,
)


EXPECTED = {
    "auth_ingress-0.1.0-py3-none-any.whl": "a" * 64,
    "auth_ingress-0.1.0.tar.gz": "b" * 64,
}


def payload(hashes=EXPECTED):
    return {
        "info": {"name": "auth-ingress", "version": "0.1.0"},
        "urls": [
            {"filename": name, "digests": {"sha256": digest}}
            for name, digest in hashes.items()
        ],
    }


def test_absent_completed_and_collision_outcomes():
    assert compare_release(None, EXPECTED, version="0.1.0").outcome is IndexOutcome.ABSENT
    complete = compare_release(payload(), EXPECTED, version="0.1.0")
    assert complete.outcome is IndexOutcome.COMPLETED
    assert complete.hashes == EXPECTED
    mismatched = {**EXPECTED, next(iter(EXPECTED)): "c" * 64}
    collision = compare_release(payload(mismatched), EXPECTED, version="0.1.0")
    assert collision.outcome is IndexOutcome.COLLISION


def test_wrong_version_or_filename_set_is_collision():
    wrong_version = payload()
    wrong_version["info"]["version"] = "0.2.0"
    assert compare_release(wrong_version, EXPECTED, version="0.1.0").outcome is IndexOutcome.COLLISION
    missing = payload({next(iter(EXPECTED)): "a" * 64})
    assert compare_release(missing, EXPECTED, version="0.1.0").outcome is IndexOutcome.COLLISION


def test_polling_is_bounded_and_never_uploads_or_retries_mutations():
    calls = []
    times = iter([0.0, 0.0, 1.0, 2.0, 3.0])

    def fetch():
        calls.append("read")
        return None

    with pytest.raises(IndexVerificationError, match="index-propagation-timeout"):
        poll_release(
            fetch,
            EXPECTED,
            version="0.1.0",
            timeout=2,
            interval=1,
            monotonic=lambda: next(times),
            sleep=lambda _: None,
        )
    assert calls and set(calls) == {"read"}


def test_invalid_expected_hashes_fail_closed():
    with pytest.raises(IndexVerificationError, match="invalid-expected-hash"):
        compare_release(payload(), {"file.whl": "secret"}, version="0.1.0")
