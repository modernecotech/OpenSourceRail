#!/usr/bin/env python3
"""Create and update the private Ops Core PBKDF2 user store."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import secrets
from pathlib import Path


ROLES = {
    "admin",
    "planner",
    "maintainer",
    "inspector",
    "approver",
    "document_controller",
    "auditor",
}
ITERATIONS = 600_000


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="private JSON user-store path")
    parser.add_argument("username")
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--roles", required=True, help="comma-separated authority roles")
    parser.add_argument("--cities", default="*", help="comma-separated city slugs or *")
    args = parser.parse_args()

    roles = sorted({value.strip() for value in args.roles.split(",") if value.strip()})
    unknown = set(roles) - ROLES
    if not roles or unknown:
        parser.error(f"roles must be selected from {', '.join(sorted(ROLES))}; invalid: {', '.join(sorted(unknown))}")
    username = args.username.strip().lower()
    if not username or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789._-" for character in username):
        parser.error("username may contain lowercase letters, digits, dot, underscore and hyphen")
    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        parser.error("password confirmation does not match")
    if len(password) < 12:
        parser.error("password must contain at least 12 characters")

    path = args.file.resolve()
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = {"schema_version": "1.0", "users": []}
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    user = {
        "user_id": username,
        "username": username,
        "display_name": args.display_name.strip(),
        "roles": roles,
        "city_scopes": sorted({value.strip() for value in args.cities.split(",") if value.strip()}),
        "active": True,
        "password": {
            "algorithm": "PBKDF2-HMAC-SHA256",
            "iterations": ITERATIONS,
            "salt_hex": salt.hex(),
            "hash_hex": password_hash.hex(),
        },
    }
    users = [row for row in payload.get("users", []) if row.get("username") != username]
    users.append(user)
    payload["users"] = sorted(users, key=lambda row: row["username"])
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    path.chmod(0o600)
    print(f"saved {username} ({', '.join(roles)}) to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
