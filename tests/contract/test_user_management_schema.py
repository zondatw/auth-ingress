from sqlalchemy import create_engine, inspect, text

from auth_ingress.repositories.schema import create_schema


def test_clean_schema_contains_user_management_columns_and_tables():
    engine = create_engine("sqlite://")
    create_schema(engine)
    inspector = inspect(engine)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    audit_columns = {column["name"] for column in inspector.get_columns("audit_events")}
    assert {"normalized_email", "credential_status", "revision"} <= user_columns
    assert {"target_user_id", "change_summary"} <= audit_columns
    assert {"installation_state", "password_reset_requests"} <= set(inspector.get_table_names())


def test_existing_case_collisions_fail_upgrade():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(320), display_name VARCHAR(120), password_hash VARCHAR(512), status VARCHAR(16), is_admin BOOLEAN, created_at DATETIME, updated_at DATETIME)"))
        connection.execute(text("INSERT INTO users (email) VALUES ('Admin@Example.test'), (' admin@example.test ' )"))
    try:
        create_schema(engine)
    except RuntimeError as error:
        assert "normalized email" in str(error).lower()
    else:
        raise AssertionError("normalization collision was accepted")
