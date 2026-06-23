from pathlib import Path


def test_current_operator_docs_prefer_auth_ingress():
    for path in (Path("README.md"), Path("docs/releasing.md"), Path("docs/user-management.md")):
        text = path.read_text(encoding="utf-8")
        assert "auth-ingress" in text
        assert "auth-ingress --help" in text or path.name != "README.md"
        if path.name != "releasing.md":
            assert "AUTH_INGRESS_" in text


def test_readme_documents_legacy_compatibility():
    text = Path("README.md").read_text(encoding="utf-8")
    assert "auth-portal" in text
    assert "AUTH_PORTAL_*" in text
    assert "compatibility" in text.casefold()
