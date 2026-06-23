from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

from scripts.release.check_artifacts import inspect_artifacts, write_hash_manifest
from scripts.release.package_metadata import EXPECTED_DISTRIBUTION, PROJECT_ROOT, load_and_validate


def build_and_check(output: Path, *, smoke: bool = True) -> None:
    load_and_validate()
    output = output.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    subprocess.run(["uv", "build", "--out-dir", str(output)], cwd=PROJECT_ROOT, check=True)
    artifacts = sorted((*output.glob("*.whl"), *output.glob("*.tar.gz")))
    report = inspect_artifacts(artifacts)
    write_hash_manifest(report, output / "SHA256SUMS")

    if smoke:
        smoke_script = PROJECT_ROOT / "tests" / "smoke" / "test_installed_package.py"
        for artifact in artifacts:
            with tempfile.TemporaryDirectory(prefix="auth-ingress-installed-") as directory:
                subprocess.run(
                    [
                        "uv",
                        "run",
                        "--isolated",
                        "--no-project",
                        "--reinstall-package",
                        EXPECTED_DISTRIBUTION,
                        "--with",
                        str(artifact),
                        "python",
                        str(smoke_script),
                    ],
                    cwd=directory,
                    check=True,
                )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and validate release artifacts")
    parser.add_argument("--out-dir", type=Path, default=PROJECT_ROOT / "dist")
    parser.add_argument("--skip-smoke", action="store_true")
    arguments = parser.parse_args()
    build_and_check(arguments.out_dir, smoke=not arguments.skip_smoke)


if __name__ == "__main__":
    main()
