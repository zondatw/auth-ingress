from auth_ingress.cli import main


def test_cli_list_and_membership_preview_use_shared_services(monkeypatch, capsys, db_factory, db):
    monkeypatch.setattr("auth_ingress.cli.SessionLocal", db_factory)
    monkeypatch.setattr("auth_ingress.cli.create_schema", lambda: None)
    monkeypatch.setattr("auth_ingress.cli.getpass", lambda _prompt: "correct-password")
    assert main(["users", "list", "--actor-email", "admin@example.test", "--format", "json"]) == 0
    output = capsys.readouterr().out
    assert '"email":"admin@example.test"' in output
    assert "password_hash" not in output and "session" not in output
