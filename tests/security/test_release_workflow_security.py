from __future__ import annotations

from pathlib import Path

import yaml

from tests.release_helpers import ROOT


def load_release() -> tuple[Path, dict[str, object]]:
    path = ROOT / ".github" / "workflows" / "release.yml"
    assert path.is_file()
    return path, yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_oidc_is_job_scoped_and_only_publish_jobs_receive_it():
    _, workflow = load_release()
    assert "id-token" not in workflow.get("permissions", {})
    for name, job in workflow["jobs"].items():
        permissions = job.get("permissions", {})
        if name in {"publish-testpypi", "publish-pypi"}:
            assert permissions == {"contents": "read", "id-token": "write"}
        else:
            assert "id-token" not in permissions


def test_branch_conditioned_publish_paths_do_not_cross_activate_oidc():
    _, workflow = load_release()
    jobs = workflow["jobs"]
    assert jobs["publish-testpypi"]["if"] == "github.event.release.target_commitish == 'beta'"
    assert jobs["publish-pypi"]["if"] == "github.event.release.target_commitish == 'release'"
    assert jobs["verify-testpypi"]["if"] == jobs["publish-testpypi"]["if"]
    assert jobs["verify-pypi"]["if"] == jobs["publish-pypi"]["if"]


def test_publish_jobs_do_not_checkout_or_execute_repository_code():
    _, workflow = load_release()
    for name in ("publish-testpypi", "publish-pypi"):
        steps = workflow["jobs"][name]["steps"]
        assert all("run" not in step for step in steps)
        assert all("actions/checkout" not in step.get("uses", "") for step in steps)
        publish_steps = [step for step in steps if "gh-action-pypi-publish" in step.get("uses", "")]
        assert len(publish_steps) == 1
        assert publish_steps[0].get("with", {}).get("skip-existing") not in {"true", True}


def test_workflow_has_no_static_credentials_or_sensitive_diagnostics():
    path, _ = load_release()
    text = path.read_text(encoding="utf-8").lower()
    forbidden = (
        "pypi_api_token",
        "test_pypi_api_token",
        "twine_password",
        "secrets.",
        "session_cookie",
        "demo-admin-password",
    )
    assert not any(value in text for value in forbidden)
