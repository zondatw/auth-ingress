from __future__ import annotations

from pathlib import Path
import re

import yaml

from tests.release_helpers import ROOT


FULL_SHA = re.compile(r"^[^@]+@[0-9a-f]{40}$")


def load_workflow(name: str) -> dict[str, object]:
    path = ROOT / ".github" / "workflows" / name
    assert path.is_file(), f"missing workflow: {path}"
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def all_steps(workflow: dict[str, object]):
    for job in workflow["jobs"].values():
        yield from job.get("steps", ())


def test_ci_trigger_matrix_jobs_permissions_and_pins():
    workflow = load_workflow("ci.yml")
    assert set(workflow["on"]) == {"pull_request", "push", "workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert {"tests", "browser-and-coverage", "package"}.issubset(workflow["jobs"])
    matrix = workflow["jobs"]["tests"]["strategy"]["matrix"]["python-version"]
    assert matrix == ["3.12", "3.13", "3.14"]
    assert workflow["jobs"]["package"]["needs"] == ["tests", "browser-and-coverage"]
    uses = [step["uses"] for step in all_steps(workflow) if "uses" in step]
    assert uses and all(FULL_SHA.fullmatch(reference) for reference in uses)


def test_release_trigger_graph_environments_artifact_handoff_and_pins():
    workflow = load_workflow("release.yml")
    assert workflow["on"] == {"release": {"types": ["published"]}}
    assert workflow["permissions"] == {"contents": "read"}
    jobs = workflow["jobs"]
    expected = {
        "validate",
        "build",
        "publish-testpypi",
        "verify-testpypi",
        "publish-pypi",
        "verify-pypi",
    }
    assert expected == set(jobs)
    assert jobs["build"]["needs"] == "validate"
    assert jobs["publish-testpypi"]["needs"] == "build"
    assert jobs["verify-testpypi"]["needs"] == "publish-testpypi"
    assert jobs["publish-pypi"]["needs"] == "verify-testpypi"
    assert jobs["verify-pypi"]["needs"] == "publish-pypi"
    assert jobs["publish-testpypi"]["environment"]["name"] == "testpypi"
    assert jobs["publish-pypi"]["environment"]["name"] == "pypi"
    uses = [step["uses"] for step in all_steps(workflow) if "uses" in step]
    assert uses and all(FULL_SHA.fullmatch(reference) for reference in uses)


def test_release_concurrency_never_cancels_publication():
    workflow = load_workflow("release.yml")
    concurrency = workflow["concurrency"]
    assert "github.event.release.tag_name" in concurrency["group"]
    assert concurrency["cancel-in-progress"] == "false"
