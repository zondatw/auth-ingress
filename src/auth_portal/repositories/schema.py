from auth_portal import models  # noqa: F401
from auth_portal.repositories.database import Base, engine


def create_schema(bind=engine) -> None:
    Base.metadata.create_all(bind)


def drop_schema(bind=engine) -> None:
    Base.metadata.drop_all(bind)
