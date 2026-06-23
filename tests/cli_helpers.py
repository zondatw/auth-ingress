from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


def run_cli(database: Path, *args: str, input_text: str = "") -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["AUTH_INGRESS_DATABASE_URL"] = f"sqlite:///{database}"
    environment["AUTH_INGRESS_SECRET_KEY"] = "test-cli-secret-with-sufficient-entropy"
    return subprocess.run(
        ["auth-ingress", *args],
        input=input_text,
        text=True,
        capture_output=True,
        env=environment,
        timeout=15,
        check=False,
    )


def json_output(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)
