def test_browser_admin_create_update_disable_journey(browser, live_server):
    page = browser.new_page()
    page.goto(f"{live_server}/sign-in")
    page.get_by_label("Email").fill("admin@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.goto(f"{live_server}/admin/services")
    assert page.get_by_role("heading", name="Service entries").is_visible()
    form = page.locator('form[action="/admin/services"]')
    form.get_by_label("Slug").fill("docs")
    form.get_by_label("Display name").fill("Docs")
    form.get_by_label("Internal destination").fill("mock://docs")
    form.get_by_label("Groups (comma separated)").fill("staff")
    form.get_by_role("button", name="Add service").click()
    edit = page.locator('form[action="/admin/services/docs"]')
    edit.get_by_label("Status").select_option("disabled")
    edit.get_by_label("Groups (comma separated)").fill("")
    edit.get_by_role("button", name="Save changes").click()
    assert page.locator('form[action="/admin/services/docs"] option:checked').text_content() == "disabled"
    page.close()


def test_browser_service_form_preserves_values_after_validation_error(browser, live_server):
    page = browser.new_page()
    page.goto(f"{live_server}/sign-in")
    page.get_by_label("Email").fill("admin@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.goto(f"{live_server}/admin/services")

    form = page.locator('form[action="/admin/services"]')
    form.get_by_label("Slug").fill("bad slug")
    form.get_by_label("Display name").fill("Docs")
    form.get_by_label("Internal destination").fill("mock://docs")
    form.get_by_label("Groups (comma separated)").fill("staff")
    form.get_by_label("Full web-app proxy").check()
    form.get_by_label("WebSockets").check()
    form.get_by_role("button", name="Add service").click()

    assert page.get_by_role("alert").is_visible()
    form = page.locator('form[action="/admin/services"]')
    assert form.get_by_label("Display name").input_value() == "Docs"
    assert form.get_by_label("Internal destination").input_value() == "mock://docs"
    assert form.get_by_label("Groups (comma separated)").input_value() == "staff"
    assert form.get_by_label("Full web-app proxy").is_checked()
    assert form.get_by_label("WebSockets").is_checked()
    page.close()
