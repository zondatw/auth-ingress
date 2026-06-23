from auth_entry_portal.cli import build_parser
from auth_entry_portal.services.cli_user_output import exit_code, render_result
from auth_entry_portal.services.user_management_types import OperationResult, OutcomeCode


def test_users_cli_grammar_and_preview_default():
    parser = build_parser()
    args = parser.parse_args(["users", "memberships", "add", "2", "staff", "--actor-email", "admin@example.test", "--expected-revision", "3", "--format", "json"])
    assert args.command == "users" and args.users_command == "memberships"
    assert args.membership_command == "add" and args.apply is False


def test_json_schema_and_exit_codes_are_stable():
    result = OperationResult("membership_add", OutcomeCode.SUCCESS, 2, 4, changes={"groups_added": [1]})
    rendered = render_result(result, "json")
    assert '"schema_version":1' in rendered and '"outcome":"success"' in rendered
    assert exit_code(OutcomeCode.SUCCESS) == 0
    assert exit_code(OutcomeCode.CONFLICT) == 5
    assert exit_code(OutcomeCode.DEPENDENCY_FAILURE) == 6
