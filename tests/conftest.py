from __future__ import annotations

import socket
import threading
import time
from dataclasses import replace

import pytest
import uvicorn
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from auth_ingress.config import Settings, get_settings
from auth_ingress.main import create_app
from auth_ingress.models import AccessRule, Group, GroupMembership, ServiceEntry, User
from auth_ingress.repositories.database import Base, get_db
from auth_ingress.security.csrf import csrf_token
from auth_ingress.security.passwords import hash_password
from auth_ingress.web.routes.auth import _limiters
from tests.fixtures.downstream_app import create_downstream_app


@pytest.fixture
def settings() -> Settings:
    return Settings(
        database_url="sqlite://",
        secret_key="test-secret-with-sufficient-entropy",
        session_ttl_seconds=3600,
        rate_limit_attempts=3,
        portal_host="testserver",
        proxy_base_domain="apps.test",
        proxy_scheme="http",
    )


@pytest.fixture
def db_factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db(db_factory) -> Session:
    with db_factory() as session:
        def make_user(email: str, display_name: str, *, admin: bool = False, status: str = "active") -> User:
            return User(
                email=email,
                display_name=display_name,
                password_hash=hash_password("correct-password"),
                status=status,
                credential_status="active",
                is_admin=admin,
            )

        staff = Group(name="staff", description="Staff")
        admins = Group(name="admins", description="Administrators")
        member = make_user("member@example.test", "Member")
        outsider = make_user("outsider@example.test", "Outsider")
        admin = make_user("admin@example.test", "Admin", admin=True)
        disabled = make_user("disabled@example.test", "Disabled", status="disabled")
        session.add_all([staff, admins, member, outsider, admin, disabled])
        session.flush()
        session.add_all([
            GroupMembership(user_id=member.id, group_id=staff.id),
            GroupMembership(user_id=admin.id, group_id=admins.id),
        ])
        demo = ServiceEntry(slug="demo", display_name="Demo Service", description="Protected demo", destination="mock://demo")
        disabled_service = ServiceEntry(slug="offline", display_name="Offline", destination="mock://offline", status="disabled")
        broken = ServiceEntry(slug="broken", display_name="Broken", destination="http://127.0.0.1:1")
        session.add_all([demo, disabled_service, broken])
        session.flush()
        session.add_all([
            AccessRule(service_entry_id=demo.id, group_id=staff.id),
            AccessRule(service_entry_id=disabled_service.id, group_id=staff.id),
            AccessRule(service_entry_id=broken.id, group_id=staff.id),
        ])
        session.commit()
        yield session


@pytest.fixture
def client(db_factory, db, settings):
    _limiters.clear()
    app = create_app(initialize_schema=False, proxy_settings=settings, proxy_session_factory=db_factory)

    def override_db():
        with db_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client
    _limiters.clear()


@pytest.fixture
def csrf(settings):
    return csrf_token(settings)


@pytest.fixture
def live_server(db_factory, db, settings):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    live_settings = replace(settings, portal_host=f"127.0.0.1:{port}", proxy_base_domain=f"localhost:{port}")
    app = create_app(initialize_schema=False, proxy_settings=live_settings, proxy_session_factory=db_factory)

    def override_db():
        with db_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: live_settings
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.02)
    if not server.started:
        raise RuntimeError("test server did not start")
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture
def downstream_server():
    app = create_downstream_app()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.02)
    if not server.started:
        raise RuntimeError("downstream test server did not start")
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture
def proxy_service(db_factory, db, downstream_server):
    with db_factory() as session:
        service = session.query(ServiceEntry).filter_by(slug="demo").one()
        service.destination = downstream_server
        service.proxy_enabled = True
        service.websocket_enabled = True
        session.commit()
    return downstream_server


@pytest.fixture
def proxy_live_server(db_factory, db, downstream_server, settings):
    with db_factory() as session:
        service = session.query(ServiceEntry).filter_by(slug="demo").one()
        service.destination = downstream_server
        service.proxy_enabled = True
        service.websocket_enabled = True
        session.commit()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    live_settings = replace(settings, portal_host=f"127.0.0.1:{port}", proxy_base_domain=f"localhost:{port}")
    app = create_app(initialize_schema=False, proxy_settings=live_settings, proxy_session_factory=db_factory)

    def override_db():
        with db_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: live_settings
    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.02)
    if not server.started:
        raise RuntimeError("proxy browser test server did not start")
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


def sign_in(client: TestClient, csrf: str, email: str = "member@example.test", password: str = "correct-password", return_to: str = "/"):
    return client.post("/sign-in", data={"email": email, "password": password, "return_to": return_to, "csrf": csrf}, follow_redirects=False)


def launch_proxy(client: TestClient, csrf: str, email: str = "member@example.test") -> str:
    sign_in(client, csrf, email=email)
    launch = client.get("/services/demo", follow_redirects=False)
    assert launch.status_code == 302
    bootstrap = client.get(launch.headers["location"], follow_redirects=False)
    assert bootstrap.status_code == 302
    assert bootstrap.headers["location"] == "/"
    return launch.headers["location"].split("/__portal/", 1)[0]


def assert_contains_all(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text


def assert_contains_none(text: str, values: list[str]) -> None:
    for value in values:
        assert value not in text
