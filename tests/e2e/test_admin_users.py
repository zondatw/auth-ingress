from tests.conftest import sign_in


def test_admin_can_preview_and_apply_access_change(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    models = __import__("auth_ingress.models", fromlist=["User", "Group"])
    target = db.query(models.User).filter_by(email="outsider@example.test").one()
    staff = db.query(models.Group).filter_by(name="staff").one()
    preview = client.post(f"/admin/users/{target.id}/memberships", data={"csrf": csrf, "expected_revision": target.revision, "group_ids": str(staff.id)})
    assert "Preview changes" in preview.text
    applied = client.post(f"/admin/users/{target.id}/memberships", data={"csrf": csrf, "expected_revision": target.revision, "group_ids": str(staff.id), "confirm": "true"})
    assert applied.status_code == 200
    assert "Access updated" in applied.text


def test_user_management_is_keyboard_and_narrow_viewport_usable(browser, live_server):
    page = browser.new_page(viewport={"width": 375, "height": 812})
    page.goto(f"{live_server}/sign-in")
    page.get_by_label("Email").fill("admin@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.goto(f"{live_server}/admin/users")
    assert page.get_by_role("heading", name="Users").is_visible()
    assert page.locator("tbody tr").count() >= 1
    assert page.locator(".status").first.text_content().strip() in {"active", "disabled"}
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement !== document.body")
    page.get_by_label("Search").fill("no-such-user")
    page.get_by_role("button", name="Filter users").click()
    assert page.get_by_role("heading", name="No users found").is_visible()
    page.close()


def test_browser_user_create_preserves_values_after_validation_error(browser, live_server):
    page = browser.new_page()
    page.goto(f"{live_server}/sign-in")
    page.get_by_label("Email").fill("admin@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.goto(f"{live_server}/admin/users")

    form = page.locator('form[action="/admin/users/preview"]')
    form.get_by_label("Email").fill("admin@example.test")
    form.get_by_label("Display name").fill("New User")
    form.get_by_label("Status").select_option("disabled")
    form.get_by_label("Administrator").check()
    form.get_by_label("staff").check()
    form.get_by_role("button", name="Preview new user").click()

    assert page.get_by_role("alert").is_visible()
    form = page.locator('form[action="/admin/users/preview"]')
    assert form.get_by_label("Email").input_value() == "admin@example.test"
    assert form.get_by_label("Display name").input_value() == "New User"
    assert form.get_by_label("Status").input_value() == "disabled"
    assert form.get_by_label("Administrator").is_checked()
    assert form.get_by_label("staff").is_checked()
    assert page.get_by_text("Temporary password").count() == 0
    page.close()
