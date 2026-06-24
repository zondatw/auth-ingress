from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
from time import perf_counter


def run_smoke() -> None:
    started = perf_counter()
    import auth_ingress
    from auth_ingress.main import app
    from auth_ingress.web.web import WEB_ROOT

    assert auth_ingress.__name__ == "auth_ingress"
    assert app.title == "auth-ingress"
    assert (WEB_ROOT / "templates" / "base.html").is_file()
    assert (WEB_ROOT / "static" / "portal.css").is_file()

    command = Path(sys.executable).with_name("auth-ingress")
    compatibility = Path(sys.executable).with_name("auth-portal")
    assert command.is_file()
    assert compatibility.is_file()
    help_result = subprocess.run(
        [str(command), "--help"], capture_output=True, text=True, check=False
    )
    assert help_result.returncode == 0
    assert all(command in help_result.stdout for command in ("init-db", "seed-demo", "bootstrap-admin", "users", "serve"))
    compatibility_help = subprocess.run(
        [str(compatibility), "--help"], capture_output=True, text=True, check=False
    )
    assert compatibility_help.returncode == 0

    with tempfile.TemporaryDirectory(prefix="auth-entry-portal-smoke-") as directory:
        database = Path(directory) / "smoke.db"
        environment = os.environ.copy()
        environment["AUTH_INGRESS_DATABASE_URL"] = f"sqlite:///{database}"
        init_result = subprocess.run(
            [str(command), "init-db"],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )
        assert init_result.returncode == 0, init_result.stderr
        assert database.is_file()

    assert perf_counter() - started < 300


def test_installed_package_smoke():
    run_smoke()


if __name__ == "__main__":
    run_smoke()
