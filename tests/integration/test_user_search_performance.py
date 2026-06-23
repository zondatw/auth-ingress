from time import monotonic

from auth_entry_portal.models import User
from auth_entry_portal.services.user_admin_service import search_users


def test_search_is_bounded_and_fast(db):
    password_hash = db.query(User).first().password_hash
    db.add_all(User(email=f"load-{index:05d}@example.test", display_name=f"Load {index}", password_hash=password_hash) for index in range(10_000))
    db.commit()
    started = monotonic()
    results = search_users(db, query="load-099", page=1, page_size=50)
    assert len(results) <= 50
    assert monotonic() - started < 2
