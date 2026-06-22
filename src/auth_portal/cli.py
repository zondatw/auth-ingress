from __future__ import annotations

import argparse

import uvicorn
from sqlalchemy import select

from auth_portal.models import AccessRule, Group, GroupMembership, ServiceEntry, User
from auth_portal.repositories.database import SessionLocal
from auth_portal.repositories.schema import create_schema
from auth_portal.security.passwords import hash_password


def seed_demo() -> None:
    create_schema()
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)):
            return
        staff = Group(name="staff", description="Demo staff group")
        admin = User(email="admin@example.test", display_name="Demo Admin", password_hash=hash_password("demo-admin-password"), is_admin=True)
        member = User(email="member@example.test", display_name="Demo Member", password_hash=hash_password("demo-member-password"))
        outsider = User(email="outsider@example.test", display_name="Demo Outsider", password_hash=hash_password("demo-outsider-password"))
        db.add_all([staff, admin, member, outsider])
        db.flush()
        db.add_all([GroupMembership(user_id=admin.id, group_id=staff.id), GroupMembership(user_id=member.id, group_id=staff.id)])
        service = ServiceEntry(slug="demo", display_name="Demo Service", description="Seeded service", destination="mock://demo")
        db.add(service)
        db.flush()
        db.add(AccessRule(service_entry_id=service.id, group_id=staff.id))
        db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(prog="auth-portal")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("init-db")
    subcommands.add_parser("seed-demo")
    serve = subcommands.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.command == "init-db":
        create_schema()
    elif args.command == "seed-demo":
        seed_demo()
    else:
        uvicorn.run("auth_portal.main:app", host=args.host, port=args.port)
