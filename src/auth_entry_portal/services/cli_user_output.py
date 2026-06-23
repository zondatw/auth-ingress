from __future__ import annotations

import json
from typing import Any

from auth_entry_portal.services.user_management_types import OperationResult, OutcomeCode

EXIT_CODES = {
    OutcomeCode.SUCCESS: 0,
    OutcomeCode.NO_CHANGE: 0,
    OutcomeCode.INVALID_INPUT: 2,
    OutcomeCode.DENIED: 3,
    OutcomeCode.NOT_FOUND: 4,
    OutcomeCode.CONFLICT: 5,
    OutcomeCode.DEPENDENCY_FAILURE: 6,
}


def exit_code(outcome: OutcomeCode) -> int:
    return EXIT_CODES[outcome]


def render_result(result: OperationResult, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(result.as_dict(), separators=(",", ":"), sort_keys=True)
    parts = [f"{result.outcome.value}: {result.operation}"]
    if result.target_user_id is not None: parts.append(f"user={result.target_user_id}")
    if result.revision is not None: parts.append(f"revision={result.revision}")
    if result.message: parts.append(result.message)
    return " | ".join(parts)


def render_records(operation: str, records: list[dict[str, Any]], output_format: str) -> str:
    if output_format == "json":
        return json.dumps({"schema_version": 1, "operation": operation, "outcome": "success", "records": records}, separators=(",", ":"), sort_keys=True)
    if not records:
        return "No records"
    headers = list(records[0])
    lines = ["\t".join(headers)]
    lines.extend("\t".join(str(record.get(header, "")) for header in headers) for record in records)
    return "\n".join(lines)
