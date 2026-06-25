def _browser_sign_in(page, live_server, email="admin@example.test"):
    page.goto(f"{live_server}/sign-in")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()


def test_tech_style_admin_navigation_and_responsive_layout(browser, live_server):
    page = browser.new_page(viewport={"width": 390, "height": 844})
    _browser_sign_in(page, live_server)

    page.goto(f"{live_server}/admin/users")
    assert page.locator(".app-shell").is_visible()
    assert page.locator(".summary-grid").first.is_visible()
    assert page.get_by_role("link", name="Groups").is_visible()
    assert page.get_by_role("link", name="Services").is_visible()
    header_box = page.locator(".site-header").bounding_box()
    assert header_box is not None
    assert header_box["height"] <= 96
    assert page.locator(".user-chip").is_hidden()
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement !== document.body")
    page.close()


def test_tech_style_empty_state_and_validation_preservation(browser, live_server):
    page = browser.new_page()
    _browser_sign_in(page, live_server)

    page.goto(f"{live_server}/admin/users")
    page.get_by_label("Search").fill("no-such-user")
    page.get_by_role("button", name="Filter users").click()
    assert page.get_by_role("heading", name="No users found").is_visible()

    page.goto(f"{live_server}/admin/services")
    page.locator('form[action="/admin/services"]').get_by_label("Slug").fill("bad slug")
    page.locator('form[action="/admin/services"]').get_by_label("Display name").fill("Reports")
    page.locator('form[action="/admin/services"]').get_by_label("Internal destination").fill("mock://reports")
    page.locator('form[action="/admin/services"]').get_by_label("Groups").fill("staff")
    page.locator('form[action="/admin/services"]').get_by_role("button", name="Add service").click()
    assert page.get_by_role("alert").is_visible()
    assert page.locator('form[action="/admin/services"]').get_by_label("Slug").input_value() == "bad slug"
    page.close()


def test_laptop_portal_objects_are_readable_scale(browser, live_server):
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    _browser_sign_in(page, live_server, email="member@example.test")

    page.goto(f"{live_server}/")
    card_box = page.locator(".service-entry-card").first.bounding_box()
    metric_box = page.locator(".metric-card").first.bounding_box()
    font_size = page.evaluate("getComputedStyle(document.body).fontSize")

    assert card_box is not None
    assert metric_box is not None
    assert card_box["width"] >= 300
    assert card_box["height"] >= 230
    assert metric_box["width"] >= 210
    assert font_size == "17px"
    page.close()
