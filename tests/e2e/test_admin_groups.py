from tests.conftest import sign_in


def test_browser_group_list_search_and_detail(browser, live_server):
    page = browser.new_page()
    page.goto(f"{live_server}/sign-in")
    page.get_by_label("Email").fill("admin@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.goto(f"{live_server}/admin/groups")

    assert page.get_by_role("heading", name="Groups").is_visible()
    page.get_by_label("Search").fill("staff")
    page.get_by_role("button", name="Filter groups").click()
    assert page.get_by_role("cell", name="staff", exact=True).is_visible()
    page.get_by_role("link", name="Manage").first.click()
    assert page.get_by_role("heading", name="Dependencies").is_visible()
    assert page.get_by_text("member@example.test").is_visible()
    page.close()


def test_browser_group_create_and_lifecycle_guardrails(browser, live_server):
    page = browser.new_page()
    page.goto(f"{live_server}/sign-in")
    page.get_by_label("Email").fill("admin@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.goto(f"{live_server}/admin/groups")

    create = page.locator('form[action="/admin/groups"]')
    create.get_by_label("Name").fill("browser-group")
    create.get_by_label("Description").fill("Browser group")
    create.get_by_role("button", name="Create group").click()
    assert page.get_by_role("heading", name="browser-group").is_visible()

    page.get_by_role("button", name="Preview permanent removal").click()
    assert page.get_by_text("Preview group remove").is_visible()
    page.get_by_role("button", name="Confirm remove").click()
    assert page.get_by_text("Group removed").is_visible()
    page.close()
