from __future__ import annotations

import argparse
from getpass import getpass
import os

import uvicorn
from sqlalchemy import select

from auth_ingress.config import COMPATIBILITY_COMMAND, PREFERRED_COMMAND, get_settings
from auth_ingress.models import AccessRule, Group, GroupMembership, ServiceEntry, User
from auth_ingress.repositories.database import SessionLocal
from auth_ingress.repositories.schema import create_schema
from auth_ingress.security.passwords import hash_password
from auth_ingress.services.bootstrap_service import BootstrapError, bootstrap_admin, mark_installation_initialized
from auth_ingress.services.cli_user_auth import authenticate_cli_actor
from auth_ingress.services.cli_user_output import exit_code, render_records, render_result
from auth_ingress.services.password_reset_service import initiate_reset
from auth_ingress.services.recovery_delivery import SMTPRecoveryDelivery
from auth_ingress.services.user_admin_service import change_memberships, create_user, search_users, set_user_status, update_user, user_detail
from auth_ingress.services.user_management_types import ManagementError, OperationResult, OutcomeCode


def _demo_password(account: str) -> str:
    variable = f"AUTH_INGRESS_DEMO_{account.upper()}_PASSWORD"
    legacy_variable = f"AUTH_PORTAL_DEMO_{account.upper()}_PASSWORD"
    value = os.getenv(variable, os.getenv(legacy_variable, ""))
    if not value: value = getpass(f"Password for demo {account}: ")
    if len(value) < 12: raise SystemExit(f"{variable} must contain at least 12 characters")
    return value


def seed_demo() -> None:
    create_schema()
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)): return
        staff = Group(name="staff", description="Demo staff group")
        admin = User(email="admin@example.test", display_name="Demo Admin", password_hash=hash_password(_demo_password("admin")), is_admin=True)
        member = User(email="member@example.test", display_name="Demo Member", password_hash=hash_password(_demo_password("member")))
        outsider = User(email="outsider@example.test", display_name="Demo Outsider", password_hash=hash_password(_demo_password("outsider")))
        db.add_all([staff, admin, member, outsider]); db.flush()
        db.add_all([GroupMembership(user_id=admin.id, group_id=staff.id), GroupMembership(user_id=member.id, group_id=staff.id)])
        service = ServiceEntry(slug="demo", display_name="Demo Service", description="Seeded service", destination="mock://demo", proxy_enabled=False, websocket_enabled=False)
        db.add(service); db.flush(); db.add(AccessRule(service_entry_id=service.id, group_id=staff.id))
        web_demo = ServiceEntry(slug="web-demo", display_name="Full Web-App Demo", description="Enable after starting the compatibility fixture on port 9001", destination="http://127.0.0.1:9001", status="disabled", proxy_enabled=True, websocket_enabled=True)
        db.add(web_demo); db.flush(); db.add(AccessRule(service_entry_id=web_demo.id, group_id=staff.id))
        mark_installation_initialized(db); db.commit()


def _common_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--actor-email", required=True)
    common.add_argument("--format", choices=("table", "json"), default="table")
    return common


def _mutation_parser(*, revision: bool = True) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, parents=[_common_parser()])
    if revision: parser.add_argument("--expected-revision", type=int, required=True)
    parser.add_argument("--apply", action="store_true")
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PREFERRED_COMMAND,
        epilog=f"`{COMPATIBILITY_COMMAND}` remains available as a compatibility alias for this release.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("init-db"); subcommands.add_parser("seed-demo")
    bootstrap = subcommands.add_parser("bootstrap-admin", help="Create the first administrator on an empty installation")
    bootstrap.add_argument("--email", required=True); bootstrap.add_argument("--display-name", required=True)
    serve = subcommands.add_parser("serve"); serve.add_argument("--host", default="127.0.0.1"); serve.add_argument("--port", type=int, default=8000)
    users = subcommands.add_parser("users", help="Manage portal users")
    user_commands = users.add_subparsers(dest="users_command", required=True)
    listing = user_commands.add_parser("list", parents=[_common_parser()]); listing.add_argument("--query", default=""); listing.add_argument("--status", choices=("active", "disabled")); listing.add_argument("--admin", choices=("true", "false")); listing.add_argument("--group"); listing.add_argument("--page", type=int, default=1)
    showing = user_commands.add_parser("show", parents=[_common_parser()]); showing.add_argument("user_id", type=int)
    create = user_commands.add_parser("create", parents=[_mutation_parser(revision=False)]); create.add_argument("--email", required=True); create.add_argument("--display-name", required=True); create.add_argument("--status", choices=("active", "disabled"), default="active"); create.add_argument("--admin", action="store_true"); create.add_argument("--group", action="append", default=[])
    update = user_commands.add_parser("update", parents=[_mutation_parser()]); update.add_argument("user_id", type=int); update.add_argument("--email"); update.add_argument("--display-name"); update.add_argument("--admin", choices=("true", "false"))
    for name in ("disable", "reactivate", "reset-password"):
        action = user_commands.add_parser(name, parents=[_mutation_parser()]); action.add_argument("user_id", type=int)
    memberships = user_commands.add_parser("memberships")
    membership_commands = memberships.add_subparsers(dest="membership_command", required=True)
    for name in ("add", "remove", "set"):
        action = membership_commands.add_parser(name, parents=[_mutation_parser()]); action.add_argument("user_id", type=int); action.add_argument("groups", nargs="*")
    return parser


def _resolve_groups(db, values: list[str]) -> set[int]:
    result: set[int] = set()
    for value in values:
        group = db.get(Group, int(value)) if value.isdigit() else db.scalar(select(Group).where(Group.name == value))
        if group is None: raise ManagementError(OutcomeCode.INVALID_INPUT, "One or more groups do not exist")
        result.add(group.id)
    return result


def _safe_user(user: User) -> dict:
    return {"id": user.id, "email": user.email, "display_name": user.display_name, "status": user.status, "credential_status": user.credential_status, "is_admin": user.is_admin, "revision": user.revision, "groups": sorted(m.group.name for m in user.memberships)}


def _run_users(args) -> int:
    create_schema(); settings = get_settings()
    with SessionLocal() as db:
        actor = authenticate_cli_actor(db, args.actor_email, getpass("Operator password: "))
        if actor is None:
            print(render_result(OperationResult("authenticate", OutcomeCode.DENIED, message="Administrator authentication failed"), args.format)); return 3
        try:
            if args.users_command == "list":
                records = [_safe_user(user) for user in search_users(db, query=args.query, status=args.status, is_admin=None if args.admin is None else args.admin == "true", group=args.group, page=args.page, page_size=settings.user_search_page_size)]
                print(render_records("users_list", records, args.format)); return 0
            if args.users_command == "show":
                detail = user_detail(db, actor, args.user_id)
                record = _safe_user(detail["user"]); record["effective_access"] = detail["effective_access"]
                print(render_records("users_show", [record], args.format)); return 0
            if args.users_command == "create":
                groups = _resolve_groups(db, args.group)
                result = create_user(db, actor, args.email, args.display_name, args.status, args.admin, groups, apply=args.apply, settings=settings, delivery=SMTPRecoveryDelivery(settings), base_url=f"{settings.proxy_scheme}://{settings.portal_host}")
            elif args.users_command == "update":
                result = update_user(db, actor, args.user_id, args.expected_revision, email=args.email, display_name=args.display_name, is_admin=None if args.admin is None else args.admin == "true", apply=args.apply)
            elif args.users_command in {"disable", "reactivate"}:
                result = set_user_status(db, actor, args.user_id, args.expected_revision, "disabled" if args.users_command == "disable" else "active", apply=args.apply)
            elif args.users_command == "reset-password":
                target = db.get(User, args.user_id)
                if target is None: raise ManagementError(OutcomeCode.NOT_FOUND, "User not found")
                if target.revision != args.expected_revision: raise ManagementError(OutcomeCode.CONFLICT, "User changed; refresh and try again")
                if not args.apply: result = OperationResult("password_reset", OutcomeCode.SUCCESS, target.id, target.revision, message="Preview password reset")
                else:
                    initiate_reset(db, actor, target, settings, SMTPRecoveryDelivery(settings), f"{settings.proxy_scheme}://{settings.portal_host}")
                    result = OperationResult("password_reset", OutcomeCode.SUCCESS, target.id, target.revision, message="Password reset sent")
            else:
                detail = user_detail(db, actor, args.user_id, audit=False); current = {m.id for m in detail["memberships"]}; requested = _resolve_groups(db, args.groups)
                desired = current | requested if args.membership_command == "add" else current - requested if args.membership_command == "remove" else requested
                result = change_memberships(db, actor, args.user_id, desired, args.expected_revision, apply=args.apply, client_category="local_cli")
            print(render_result(result, args.format)); return exit_code(result.outcome)
        except ManagementError as error:
            result = OperationResult(args.users_command, error.code, message=str(error)); print(render_result(result, args.format)); return exit_code(error.code)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init-db": create_schema(); return 0
    if args.command == "seed-demo": seed_demo(); return 0
    if args.command == "bootstrap-admin":
        first, second = getpass("Initial administrator password: "), getpass("Confirm administrator password: ")
        if first != second: print("Bootstrap failed: passwords did not match"); return 2
        create_schema()
        with SessionLocal() as db:
            try: bootstrap_admin(db, args.email, args.display_name, first)
            except BootstrapError as error: print(f"Bootstrap failed: {error}"); return 3 if error.reason == "already_initialized" else 5 if error.reason == "conflict" else 2
        print("Initial administrator created"); return 0
    if args.command == "users": return _run_users(args)
    uvicorn.run("auth_ingress.main:app", host=args.host, port=args.port); return 0
