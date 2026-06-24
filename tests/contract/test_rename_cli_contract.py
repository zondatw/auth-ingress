from auth_ingress.cli import build_parser
from auth_ingress.config import COMPATIBILITY_COMMAND, PREFERRED_COMMAND


def test_cli_prefers_auth_ingress_name():
    parser = build_parser()
    help_text = parser.format_help()
    assert parser.prog == PREFERRED_COMMAND
    assert PREFERRED_COMMAND in help_text
    assert COMPATIBILITY_COMMAND in help_text
    for command in ("init-db", "seed-demo", "bootstrap-admin", "users", "serve"):
        assert command in help_text

