from auth_ingress.cli import build_parser


def test_bootstrap_grammar_has_no_password_argument():
    parser = build_parser()
    help_text = parser.format_help()
    args = parser.parse_args(["bootstrap-admin", "--email", "admin@example.test", "--display-name", "Admin"])
    assert args.command == "bootstrap-admin"
    assert not hasattr(args, "password")
    assert "--password" not in help_text
