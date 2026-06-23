from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class OutcomeCode(StrEnum):
    SUCCESS = "success"
    NO_CHANGE = "no_change"
    INVALID_INPUT = "invalid_input"
    DENIED = "denied"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    DEPENDENCY_FAILURE = "dependency_failure"


@dataclass(slots=True)
class OperationResult:
    operation: str
    outcome: OutcomeCode
    target_user_id: int | None = None
    revision: int | None = None
    changes: dict[str, Any] = field(default_factory=dict)
    effective_access_changes: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"schema_version": 1, "operation": self.operation, "outcome": self.outcome.value}
        for key in ("target_user_id", "revision"):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        if self.changes:
            result["changes"] = self.changes
        if self.effective_access_changes:
            result["effective_access_changes"] = self.effective_access_changes
        if self.message:
            result["message"] = self.message
        return result


class ManagementError(RuntimeError):
    def __init__(self, code: OutcomeCode, message: str):
        super().__init__(message)
        self.code = code
