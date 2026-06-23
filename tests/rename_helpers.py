from __future__ import annotations

from pathlib import Path

from tests.fixtures.rename_inventory import (
    ALLOWED_CLASSIFICATIONS,
    INTENTIONAL_OLD_NAME_REFERENCES,
    OLD_NAME_TOKENS,
    RenameFinding,
)


def classify_path(path: Path) -> str | None:
    normalized = path.as_posix()
    for prefix, classification in INTENTIONAL_OLD_NAME_REFERENCES.items():
        if normalized == prefix.rstrip("/") or normalized.startswith(prefix):
            return classification
    return None


def scan_paths(paths: list[Path]) -> list[RenameFinding]:
    findings: list[RenameFinding] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        classification = classify_path(path)
        for token in OLD_NAME_TOKENS:
            if token in text:
                findings.append(RenameFinding(path, token, classification or "unclassified"))
    return findings


def unclassified_findings(paths: list[Path]) -> list[RenameFinding]:
    return [
        finding
        for finding in scan_paths(paths)
        if finding.classification not in ALLOWED_CLASSIFICATIONS
    ]

