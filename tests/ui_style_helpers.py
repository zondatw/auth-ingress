from __future__ import annotations

import re
from collections.abc import Iterable


TECH_STYLE_MARKERS = (
    'class="app-shell"',
    'class="site-header"',
    'class="page-header',
    'class="panel',
)


FORBIDDEN_VISIBLE_VALUES = (
    "test-secret-with-sufficient-entropy",
    "token_digest",
    "password_hash",
    "session_id",
    "sqlite://",
    "csrf_token",
)


RESPONSIVE_ROUTES = (
    "/sign-in",
    "/",
    "/admin/users",
    "/admin/groups",
    "/admin/services",
    "/admin/audit",
)


def assert_contains_markers(html: str, markers: Iterable[str] = TECH_STYLE_MARKERS) -> None:
    missing = [marker for marker in markers if marker not in html]
    assert not missing, f"missing UI markers: {missing}"


def assert_forbidden_values_absent(html: str, values: Iterable[str] = FORBIDDEN_VISIBLE_VALUES) -> None:
    for value in values:
        assert value not in html


def assert_has_status_text(html: str, *labels: str) -> None:
    for label in labels:
        assert re.search(rf">{re.escape(label)}<", html, re.I) or label in html


def assert_safe_summary_cards(html: str) -> None:
    assert 'class="summary-grid"' in html
    assert 'class="metric-card' in html
