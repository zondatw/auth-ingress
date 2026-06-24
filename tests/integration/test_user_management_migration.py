from sqlalchemy import create_engine, inspect, text

from auth_ingress.repositories.schema import create_schema


def test_prior_user_schema_upgrades_and_marks_installation_initialized(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'prior.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(320) UNIQUE, display_name VARCHAR(120), password_hash VARCHAR(512), status VARCHAR(16), is_admin BOOLEAN, created_at DATETIME, updated_at DATETIME)"))
        connection.execute(text("INSERT INTO users (email, display_name, password_hash, status, is_admin) VALUES (' Admin@Example.test ', 'Admin', 'hash', 'active', 1)"))
    create_schema(engine)
    with engine.connect() as connection:
        row = connection.execute(text("SELECT email, normalized_email, credential_status, revision FROM users")).one()
        state = connection.execute(text("SELECT state FROM installation_state WHERE id = 1")).scalar_one()
    assert row == ("Admin@Example.test", "admin@example.test", "active", 1)
    assert state == "initialized"
    assert "ix_users_normalized_email" in {index["name"] for index in inspect(engine).get_indexes("users")}
