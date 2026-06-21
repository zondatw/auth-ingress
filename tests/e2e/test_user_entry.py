def test_browser_journey_sign_in_entry_and_sign_out(browser, live_server):
    page = browser.new_page()
    page.goto(f"{live_server}/services/demo")
    assert "/sign-in" in page.url
    page.get_by_label("Email").fill("member@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("**/services/demo")
    assert page.get_by_text("Protected service reached.").is_visible()
    page.goto(f"{live_server}/")
    page.get_by_role("button", name="Sign out").click()
    page.goto(f"{live_server}/services/demo")
    assert "/sign-in" in page.url
    page.close()
