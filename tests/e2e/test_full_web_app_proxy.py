def test_complete_application_renders_in_real_browser(browser, proxy_live_server):
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{proxy_live_server}/services/demo")
    page.get_by_label("Email").fill("member@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("**demo.localhost*/")
    assert "ticket=" not in page.url
    assert page.get_by_role("heading", name="Fixture App").is_visible()
    assert page.get_by_alt_text("Fixture logo").is_visible()
    page.get_by_role("link", name="Nested page").click()
    assert page.get_by_role("heading", name="Nested Page").is_visible()
    page.reload()
    assert page.get_by_role("heading", name="Nested Page").is_visible()
    second = context.new_page()
    second.goto(page.url)
    assert second.get_by_role("heading", name="Nested Page").is_visible()
    context.close()


def test_interactive_application_features_in_real_browser(browser, proxy_live_server):
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    page.goto(f"{proxy_live_server}/services/demo")
    page.get_by_label("Email").fill("member@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("**demo.localhost*/")
    page.wait_for_function("document.querySelector('#api-result').textContent === 'a,b'")
    page.get_by_role("button", name="Submit").click()
    assert page.get_by_role("heading", name="Form Result").is_visible()
    page.goto(page.url.split("/form", 1)[0] + "/redirect/internal")
    assert page.get_by_role("heading", name="Nested Page").is_visible()
    context.close()


def test_real_time_application_and_reconnect_denial(browser, proxy_live_server, db_factory):
    from sqlalchemy import select

    from auth_entry_portal.models import AccessRule, ServiceEntry

    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{proxy_live_server}/services/demo")
    page.get_by_label("Email").fill("member@example.test")
    page.get_by_label("Password").fill("correct-password")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("**demo.localhost*/")
    echoed = page.evaluate("""() => new Promise((resolve, reject) => {
      const ws = new WebSocket(`ws://${location.host}/ws`, 'fixture');
      ws.onopen = () => ws.send('browser-echo');
      ws.onmessage = event => { resolve(event.data); ws.close(); };
      ws.onerror = () => reject(new Error('websocket failed'));
    })""")
    assert echoed == "browser-echo"
    with db_factory() as db:
        service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == "demo"))
        db.query(AccessRule).filter(AccessRule.service_entry_id == service.id).delete()
        db.commit()
    denied = page.evaluate("""() => new Promise(resolve => {
      const ws = new WebSocket(`ws://${location.host}/ws`);
      ws.onopen = () => resolve(false);
      ws.onerror = () => resolve(true);
      ws.onclose = () => resolve(true);
    })""")
    assert denied is True
    context.close()
