from tests.conftest import sign_in
from tests.ui_style_helpers import assert_contains_markers, assert_has_status_text, assert_safe_summary_cards


def test_public_auth_pages_render_tech_shell(client):
    for path in ("/sign-in", "/reset-password"):
        response = client.get(path)
        assert response.status_code == 200
        assert_contains_markers(response.text)
        assert "old generic light-only" not in response.text


def test_authenticated_pages_render_refreshed_components(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    for path in ("/", "/admin/users", "/admin/groups", "/admin/services", "/admin/audit"):
        response = client.get(path)
        assert response.status_code == 200
        assert_contains_markers(response.text)
        assert_safe_summary_cards(response.text)


def test_denial_page_uses_refreshed_state(client, csrf):
    sign_in(client, csrf)
    response = client.get("/admin/users")

    assert response.status_code == 403
    assert_contains_markers(response.text)
    assert 'class="alert"' in response.text
    assert "Return to service list" in response.text


def test_status_and_state_tokens_exist_in_css():
    css = open("src/auth_ingress/web/static/portal.css", encoding="utf-8").read()

    for token in (
        "--bg:",
        "--surface:",
        "--accent:",
        "--success:",
        "--warning:",
        "--danger:",
        "--focus:",
        ".summary-grid",
        ".metric-card",
        ".timeline-row",
        ".danger-zone",
        ".secret-display",
        ".service-entry-card",
        ".service-avatar",
        "width:30px;height:30px",
        ".service-slug",
        ".service-launch",
        "@media(min-width:900px)",
        "body{font-size:17px}",
        "grid-template-columns:repeat(auto-fit,minmax(300px,1fr))",
        ".panel>form+form",
        ".site-nav{width:100%;justify-content:flex-start;flex-wrap:nowrap",
        ".user-chip{display:none}",
        ":focus-visible",
    ):
        assert token in css


def test_operational_summaries_and_status_text_render(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    users = client.get("/admin/users").text
    groups = client.get("/admin/groups").text
    services = client.get("/admin/services").text
    audit = client.get("/admin/audit").text

    assert_has_status_text(users, "Active users", "Disabled users", "Administrators")
    assert_has_status_text(groups, "Active groups", "Linked to services", "Unused groups")
    assert_has_status_text(services, "Enabled services", "Proxy enabled", "Group linked")
    assert_has_status_text(audit, "Retained events", "Recent denials", "Event timeline")


def test_no_light_only_legacy_css_contract():
    css = open("src/auth_ingress/web/static/portal.css", encoding="utf-8").read()

    assert "color-scheme:dark" in css
    assert "background:white" not in css
    assert "--bg:#f5f7fb" not in css


def test_portal_service_entries_have_visual_identity(client, csrf):
    sign_in(client, csrf)

    response = client.get("/")

    assert response.status_code == 200
    assert "service-entry-card" in response.text
    assert "service-avatar" in response.text
    assert "service-slug" in response.text
    assert "service-launch" in response.text
    assert "demo" in response.text
