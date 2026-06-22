from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import re
import time
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

from scripts.release.verify_staged_release import INDEXES, read_manifest


class IndexVerificationError(RuntimeError):
    """Raised when read-only index verification cannot produce a safe outcome."""


class IndexOutcome(str, Enum):
    ABSENT = "absent"
    COMPLETED = "completed"
    COLLISION = "collision"


@dataclass(frozen=True)
class IndexResult:
    outcome: IndexOutcome
    version: str
    hashes: dict[str, str]
    reason: str


def _valid_hash(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value))


def compare_release(
    payload: Mapping[str, object] | None,
    expected: Mapping[str, str],
    *,
    version: str,
) -> IndexResult:
    if not expected or any(not _valid_hash(digest) for digest in expected.values()):
        raise IndexVerificationError("invalid-expected-hash")
    if payload is None:
        return IndexResult(IndexOutcome.ABSENT, version, {}, "version-not-found")
    info = payload.get("info")
    files = payload.get("urls")
    if not isinstance(info, Mapping) or not isinstance(files, list):
        return IndexResult(IndexOutcome.COLLISION, version, {}, "malformed-index-response")
    actual = {
        item["filename"]: item.get("digests", {}).get("sha256")
        for item in files
        if isinstance(item, Mapping)
        and isinstance(item.get("filename"), str)
        and isinstance(item.get("digests"), Mapping)
    }
    safe_actual = {
        str(name): str(digest)
        for name, digest in actual.items()
        if isinstance(digest, str) and _valid_hash(digest)
    }
    matches = (
        info.get("name") == "auth-entry-portal"
        and info.get("version") == version
        and safe_actual == dict(expected)
    )
    if matches:
        return IndexResult(IndexOutcome.COMPLETED, version, safe_actual, "hashes-match")
    return IndexResult(IndexOutcome.COLLISION, version, safe_actual, "identity-or-hash-mismatch")


def poll_release(
    fetch: Callable[[], Mapping[str, object] | None],
    expected: Mapping[str, str],
    *,
    version: str,
    timeout: float,
    interval: float,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> IndexResult:
    deadline = monotonic() + timeout
    while True:
        result = compare_release(fetch(), expected, version=version)
        if result.outcome is not IndexOutcome.ABSENT:
            return result
        if monotonic() >= deadline:
            raise IndexVerificationError("index-propagation-timeout")
        sleep(interval)


def fetch_release(index: str, version: str) -> Mapping[str, object] | None:
    url = INDEXES[index]["json"].format(version=quote(version, safe=""))
    try:
        with urlopen(url, timeout=10) as response:
            payload = json.load(response)
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise IndexVerificationError("index-read-failed") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise IndexVerificationError("index-read-failed") from exc
    if not isinstance(payload, Mapping):
        raise IndexVerificationError("malformed-index-response")
    return payload


def verify_provenance(index: str, version: str, filenames: Mapping[str, str]) -> None:
    domain = "pypi.org" if index == "pypi" else "test.pypi.org"
    for filename in filenames:
        url = (
            f"https://{domain}/integrity/auth-entry-portal/"
            f"{quote(version, safe='')}/{quote(filename, safe='')}/provenance"
        )
        try:
            with urlopen(url, timeout=10) as response:
                payload = json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise IndexVerificationError("provenance-verification-failed") from exc
        if not payload:
            raise IndexVerificationError("provenance-verification-failed")


def safe_summary(source: Mapping[str, object]) -> dict[str, object]:
    allowed = ("version", "revision", "outcome", "reason", "hashes")
    return {key: source[key] for key in allowed if key in source}


def main() -> None:
    parser = argparse.ArgumentParser(description="Read and verify an immutable package-index release")
    parser.add_argument("--index", choices=sorted(INDEXES), required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--interval", type=float, default=5)
    parser.add_argument("--revision", default="")
    parser.add_argument("--require-provenance", action="store_true")
    arguments = parser.parse_args()
    version = arguments.version.removeprefix("v")
    expected = read_manifest(arguments.manifest)
    result = poll_release(
        lambda: fetch_release(arguments.index, version),
        expected,
        version=version,
        timeout=arguments.timeout,
        interval=arguments.interval,
    )
    if result.outcome is IndexOutcome.COLLISION:
        raise IndexVerificationError(result.reason)
    if arguments.require_provenance:
        verify_provenance(arguments.index, version, expected)
    summary = safe_summary(
        {
            "version": version,
            "revision": arguments.revision,
            "outcome": result.outcome.value,
            "reason": result.reason,
            "hashes": result.hashes,
        }
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
