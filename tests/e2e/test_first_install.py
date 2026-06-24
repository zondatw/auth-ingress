from fastapi.testclient import TestClient

from auth_ingress.config import get_settings
from auth_ingress.main import create_app
from auth_ingress.repositories.database import get_db


def test_first_install_page_is_actionable_and_non_sensitive(db_factory, settings):
    app = create_app(initialize_schema=False, proxy_settings=settings, proxy_session_factory=db_factory)

    def override_db():
        with db_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as client:
        response = client.get("/sign-in")
    assert response.status_code == 503
    assert "auth-ingress bootstrap-admin" in response.text
    assert "AUTH_INGRESS_DATABASE_URL" not in response.text
