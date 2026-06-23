from auth_entry_portal.models import User
from auth_entry_portal.services.authentication_service import authenticate
from auth_entry_portal.services.user_admin_service import create_user


def test_temporary_password_login_forces_self_change(client, csrf, db):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    created = create_user(db, actor, "temp@example.test", "Temp User", "active", False, set(), apply=True)

    sign_in = client.post(
        "/sign-in",
        data={"email": "temp@example.test", "password": created.temporary_password, "return_to": "/", "csrf": csrf},
        follow_redirects=False,
    )
    assert sign_in.status_code == 302
    assert sign_in.headers["location"] == "/change-password"

    home = client.get("/", follow_redirects=False)
    assert home.status_code == 302
    assert home.headers["location"] == "/change-password"

    changed = client.post(
        "/change-password",
        data={"password": "new-correct-password", "password_confirm": "new-correct-password", "csrf": csrf},
        follow_redirects=False,
    )
    assert changed.status_code == 303
    assert changed.headers["location"] == "/"

    target = db.query(User).filter_by(email="temp@example.test").one()
    db.refresh(target)
    assert target.credential_status == "active"
    assert authenticate(db, "temp@example.test", created.temporary_password) is None
    assert authenticate(db, "temp@example.test", "new-correct-password") is not None
