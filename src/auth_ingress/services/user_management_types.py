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


SENSITIVE_MANAGEMENT_FIELDS = frozenset(
    {
        "password",
        "current_password",
        "new_password",
        "temporary_password",
        "token",
        "secret",
        "recovery_value",
        "recovery_token",
        "session_id",
    }
)


@dataclass(frozen=True, slots=True)
class FieldError:
    field: str | None
    message: str
    code: str = "invalid_input"
    severity: str = "error"


@dataclass(slots=True)
class ManagementFormState:
    form_name: str
    record_id: str | int | None = None
    safe_values: dict[str, Any] = field(default_factory=dict)
    selected_values: dict[str, set[str]] = field(default_factory=dict)
    field_errors: dict[str, list[FieldError]] = field(default_factory=dict)
    form_errors: list[str] = field(default_factory=list)

    @classmethod
    def from_submitted(
        cls,
        form_name: str,
        values: dict[str, Any],
        *,
        record_id: str | int | None = None,
        selected: dict[str, Any] | None = None,
        sensitive_fields: set[str] | frozenset[str] = SENSITIVE_MANAGEMENT_FIELDS,
        field_errors: list[FieldError] | None = None,
        form_errors: list[str] | None = None,
    ) -> "ManagementFormState":
        safe_values = {
            key: value
            for key, value in values.items()
            if key not in sensitive_fields and value is not None
        }
        selected_values = {
            key: {str(item) for item in (value if isinstance(value, (list, tuple, set, frozenset)) else [value])}
            for key, value in (selected or {}).items()
            if key not in sensitive_fields and value is not None
        }
        errors: dict[str, list[FieldError]] = {}
        for error in field_errors or []:
            if error.field:
                errors.setdefault(error.field, []).append(error)
        return cls(
            form_name=form_name,
            record_id=record_id,
            safe_values=safe_values,
            selected_values=selected_values,
            field_errors=errors,
            form_errors=list(form_errors or []),
        )

    def applies_to(self, form_name: str, record_id: str | int | None = None) -> bool:
        return self.form_name == form_name and (record_id is None or str(self.record_id) == str(record_id))

    def value(self, field_name: str, default: Any = "") -> Any:
        return self.safe_values.get(field_name, default)

    def is_selected(self, field_name: str, value: Any) -> bool:
        return str(value) in self.selected_values.get(field_name, set())

    def checked(self, field_name: str, default: bool = False) -> bool:
        if field_name not in self.safe_values and field_name not in self.selected_values:
            return default
        if field_name in self.selected_values:
            return "true" in self.selected_values[field_name] or "1" in self.selected_values[field_name]
        value = self.safe_values.get(field_name)
        return value in {True, "true", "1", "on", "yes"}

    def error_text(self, field_name: str) -> str:
        return " ".join(error.message for error in self.field_errors.get(field_name, []))


@dataclass(slots=True)
class OperationResult:
    operation: str
    outcome: OutcomeCode
    target_user_id: int | None = None
    revision: int | None = None
    changes: dict[str, Any] = field(default_factory=dict)
    effective_access_changes: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""
    temporary_password: str | None = None

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
        if self.temporary_password:
            result["temporary_password"] = self.temporary_password
        return result


class ManagementError(RuntimeError):
    def __init__(self, code: OutcomeCode, message: str, *, field: str | None = None):
        super().__init__(message)
        self.code = code
        self.field = field
