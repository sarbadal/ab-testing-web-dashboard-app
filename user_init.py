#!/usr/bin/env python3
"""User management CLI for creating admin and non-admin users."""

import argparse
import getpass
from typing import Optional

from app.users import create_user, ensure_user_store, reset_user_password


def _prompt_password() -> str:
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm Password: ")
    if password != confirm:
        raise ValueError("Passwords do not match")
    return password


def handle_create_user(username: str, password: Optional[str], is_admin: bool) -> None:
    if not password:
        password = _prompt_password()

    user = create_user(username=username, password=password, is_admin=is_admin)
    role = "admin" if user.get("is_admin") else "normal"
    print(f"Created {role} user: {user['username']}")


def handle_reset_password(username: str, password: Optional[str]) -> None:
    if not password:
        password = _prompt_password()

    user = reset_user_password(username=username, new_password=password)
    print(f"Password reset successfully for user: {user['username']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage users for AB Testing app")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_user_parser = subparsers.add_parser("create-user", help="Create a normal user")
    create_user_parser.add_argument("--username", required=True, help="Username for the new user")
    create_user_parser.add_argument("--password", help="Password for the new user")

    create_admin_parser = subparsers.add_parser("create-admin", help="Create an admin user")
    create_admin_parser.add_argument("--username", required=True, help="Username for the new admin")
    create_admin_parser.add_argument("--password", help="Password for the new admin")

    reset_password_parser = subparsers.add_parser("reset-password", help="Reset password for an existing user")
    reset_password_parser.add_argument("--username", required=True, help="Username to reset")
    reset_password_parser.add_argument("--password", help="New password")

    args = parser.parse_args()
    ensure_user_store()

    if args.command == "create-user":
        handle_create_user(args.username, args.password, is_admin=False)
    elif args.command == "create-admin":
        handle_create_user(args.username, args.password, is_admin=True)
    elif args.command == "reset-password":
        handle_reset_password(args.username, args.password)


if __name__ == "__main__":
    main()
