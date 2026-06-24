from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from auth_ingress.models import InstallationState, User
from auth_ingress.repositories.schema import create_schema
from auth_ingress.services.bootstrap_service import BootstrapError, bootstrap_admin


def test_bootstrap_creates_one_admin_and_then_closes(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'bootstrap.db'}", connect_args={"check_same_thread": False})
    create_schema(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        user = bootstrap_admin(db, " Admin@Example.test ", "Initial Admin", "long-enough-password")
        assert user.is_admin and user.normalized_email == "admin@example.test"
    with factory() as db:
        try:
            bootstrap_admin(db, "second@example.test", "Second", "long-enough-password")
        except BootstrapError as error:
            assert error.reason == "already_initialized"
        else:
            raise AssertionError("second bootstrap was accepted")
        assert db.scalar(select(func.count()).select_from(User)) == 1
        assert db.get(InstallationState, 1).state == "initialized"


def test_concurrent_bootstrap_creates_exactly_one_admin(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'concurrent.db'}", connect_args={"check_same_thread": False, "timeout": 5})
    create_schema(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def attempt(number: int) -> str:
        with factory() as db:
            try:
                bootstrap_admin(db, f"admin{number}@example.test", f"Admin {number}", "long-enough-password")
                return "created"
            except BootstrapError as error:
                return error.reason

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(attempt, (1, 2)))
    with factory() as db:
        assert outcomes.count("created") == 1
        assert db.scalar(select(func.count()).select_from(User)) == 1
