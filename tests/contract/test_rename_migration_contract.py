from pathlib import Path


def test_migration_mapping_documents_old_and_new_names():
    text = Path("README.md").read_text(encoding="utf-8")
    for value in ("auth-entry-portal", "auth-ingress", "auth-portal", "AUTH_PORTAL_*", "AUTH_INGRESS_*", "auth_ingress"):
        assert value in text

