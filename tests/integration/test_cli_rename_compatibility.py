import os
from pathlib import Path
import subprocess


def _env(database: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment["AUTH_PORTAL_DATABASE_URL"] = f"sqlite:///{database}"
    environment["AUTH_PORTAL_SECRET_KEY"] = "test-cli-secret-with-sufficient-entropy"
    return environment


def test_legacy_auth_portal_command_still_runs_help():
    result = subprocess.run(["auth-portal", "--help"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "auth-ingress" in result.stdout


def test_legacy_auth_portal_command_can_initialize_database(tmp_path):
    database = tmp_path / "legacy.db"
    result = subprocess.run(["auth-portal", "init-db"], capture_output=True, text=True, check=False, env=_env(database))
    assert result.returncode == 0
    assert database.is_file()

