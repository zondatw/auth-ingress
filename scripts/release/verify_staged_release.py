from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from scripts.release.package_metadata import EXPECTED_DISTRIBUTION


INDEXES = {
    "testpypi": {
        "json": f"https://test.pypi.org/pypi/{EXPECTED_DISTRIBUTION}/{{version}}/json",
        "simple": "https://test.pypi.org/simple",
    },
    "pypi": {
        "json": f"https://pypi.org/pypi/{EXPECTED_DISTRIBUTION}/{{version}}/json",
        "simple": "https://pypi.org/simple",
    },
}


class StagedReleaseError(RuntimeError):
    """Raised when the staged package cannot be verified safely."""


def read_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, filename = line.split(maxsplit=1)
        filename = filename.strip()
        if len(digest) != 64 or filename in entries:
            raise StagedReleaseError("invalid-hash-manifest")
        entries[filename] = digest
    if len(entries) != 2:
        raise StagedReleaseError("unexpected-artifact-count")
    return entries


def fetch_release(index: str, version: str, *, timeout: float = 120, interval: float = 5):
    deadline = time.monotonic() + timeout
    url = INDEXES[index]["json"].format(version=version)
    while True:
        try:
            with urlopen(url, timeout=min(interval, 10)) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            if time.monotonic() >= deadline:
                raise StagedReleaseError("index-propagation-timeout") from exc
            time.sleep(interval)


def verify_index_hashes(payload: dict[str, object], expected: dict[str, str]) -> None:
    files = payload.get("urls")
    if not isinstance(files, list):
        raise StagedReleaseError("missing-index-files")
    actual = {
        item["filename"]: item.get("digests", {}).get("sha256")
        for item in files
        if isinstance(item, dict) and isinstance(item.get("filename"), str)
    }
    if actual != expected:
        raise StagedReleaseError("index-artifact-hash-mismatch")


def install_and_smoke(index: str, version: str, smoke_script: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="auth-ingress-index-") as directory:
        subprocess.run(
            [
                "uv",
                "run",
                "--isolated",
                "--no-project",
                "--index",
                INDEXES[index]["simple"],
                "--default-index",
                "https://pypi.org/simple",
                "--with",
                f"{EXPECTED_DISTRIBUTION}=={version}",
                "python",
                str(smoke_script),
            ],
            cwd=directory,
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify an exact staged package release")
    parser.add_argument("--index", choices=sorted(INDEXES), required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--smoke-script", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=120)
    arguments = parser.parse_args()
    version = arguments.version.removeprefix("v")
    expected = read_manifest(arguments.manifest)
    payload = fetch_release(arguments.index, version, timeout=arguments.timeout)
    verify_index_hashes(payload, expected)
    install_and_smoke(arguments.index, version, arguments.smoke_script.resolve())
    manifest_digest = sha256(arguments.manifest.read_bytes()).hexdigest()
    print(f"verified {arguments.index} version={version} manifest={manifest_digest}")


if __name__ == "__main__":
    main()
