from fastapi.testclient import TestClient

from auth_entry_portal.config import get_settings
from auth_entry_portal.main import create_app
from auth_entry_portal.repositories.database import get_db


def test_clean_install_shows_local_setup_without_registration(db_factory, settings):
    app = create_app(initialize_schema=False, proxy_settings=settings, proxy_session_factory=db_factory)

    def override_db():
        with db_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as client:
        response = client.get("/sign-in")
    assert response.status_code == 503
    assert "bootstrap-admin" in response.text
    assert "password" not in response.text.casefold()
    assert all("bootstrap" not in route.path for route in app.routes if hasattr(route, "methods") and "POST" in route.methods)
