from pathlib import Path


PRIMARY_TEMPLATES = [
    Path("src/auth_ingress/web/templates/base.html"),
    Path("src/auth_ingress/web/templates/auth/sign_in.html"),
    Path("src/auth_ingress/web/templates/auth/setup_required.html"),
    Path("src/auth_ingress/web/templates/portal/index.html"),
    Path("src/auth_ingress/web/templates/admin/services.html"),
    Path("src/auth_ingress/web/templates/admin/users.html"),
    Path("src/auth_ingress/web/templates/admin/audit.html"),
]


def test_primary_templates_use_auth_ingress_display_name():
    for path in PRIMARY_TEMPLATES:
        text = path.read_text(encoding="utf-8")
        assert "auth-ingress" in text
        assert "Auth Portal" not in text
        assert "Auth Entry Portal" not in text

