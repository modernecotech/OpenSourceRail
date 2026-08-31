#!/usr/bin/env python3
"""Serve the OSR operations portal with a small SQLite Ops Core API."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = REPO_ROOT / "var" / "ops-core.sqlite3"
DEFAULT_EVIDENCE = REPO_ROOT / "var" / "ops-evidence"
CITY_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MAX_EVIDENCE_BYTES = 25 * 1024 * 1024
SESSION_SECONDS = 8 * 60 * 60

RECORD_TABLES = {
    "workOrders": "work_orders",
    "inspections": "inspections",
    "approvals": "approvals",
    "defects": "defects",
    "documents": "documents",
    "audit": "audit_events",
}

PROJECT_RECORD_KINDS = {
    "purchaseOrders": "purchase-order",
    "deliveries": "delivery",
    "invoices": "invoice",
    "payments": "payment",
    "progressUpdates": "progress-update",
    "projectRevisions": "project-revision",
}

ROLE_COLLECTIONS = {
    "admin": set(RECORD_TABLES) | set(PROJECT_RECORD_KINDS),
    "planner": {"workOrders", "purchaseOrders", "deliveries", "invoices", "payments", "progressUpdates", "projectRevisions"},
    "maintainer": {"workOrders", "defects"},
    "inspector": {"workOrders", "inspections", "defects"},
    "approver": {"workOrders", "approvals"},
    "document_controller": {"documents"},
    "auditor": set(),
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Serve the operations portal and persist Ops Core records in SQLite."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8008)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument(
        "--users",
        type=Path,
        help="JSON user store created by ops-user-admin.py; required off localhost",
    )
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument(
        "--signing-key",
        type=Path,
        help="server attestation key (default: next to the selected database)",
    )
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="delete the selected database before startup (intended for isolated tests)",
    )
    args = parser.parse_args()

    db_path = args.db.resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if args.reset_db and db_path.exists():
        db_path.unlink()
    with connect(db_path) as con:
        init_db(con)

    users = load_users(args.users.resolve()) if args.users else None
    if users is None and args.host not in {"127.0.0.1", "localhost", "::1"}:
        parser.error("--users is required when binding beyond localhost")
    evidence_path = args.evidence_dir.resolve()
    evidence_path.mkdir(parents=True, exist_ok=True)
    signing_key_path = (args.signing_key or db_path.with_suffix(".signing-key")).resolve()
    signing_key = load_or_create_signing_key(signing_key_path)

    class Handler(OpsCoreHandler):
        database_path = db_path
        evidence_root = evidence_path
        user_store = users
        attestation_key = signing_key
        sessions: dict[str, dict] = {}
        private_paths = tuple(
            path for path in (db_path, evidence_path, signing_key_path, args.users.resolve() if args.users else None)
            if path is not None
        )

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"serving {REPO_ROOT} on http://{args.host}:{args.port}/")
    print(f"ops core sqlite: {db_path}")
    print(f"ops evidence: {evidence_path}")
    print("ops auth: configured users" if users is not None else "ops auth: localhost trusted-development mode")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


class OpsCoreHandler(SimpleHTTPRequestHandler):
    database_path: Path = DEFAULT_DB
    evidence_root: Path = DEFAULT_EVIDENCE
    user_store: dict[str, dict] | None = None
    attestation_key: bytes = b""
    sessions: dict[str, dict] = {}
    private_paths: tuple[Path, ...] = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

    def handle(self) -> None:
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            return

    def do_OPTIONS(self) -> None:
        if not urlparse(self.path).path.startswith("/api/"):
            self.send_error(404)
            return
        self.send_response(204)
        self._send_api_headers("application/json")
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/ops-auth/session":
            actor = self._actor(required=False)
            self._send_json(200, {"authenticated": actor is not None, "actor": public_actor(actor) if actor else None})
            return
        try:
            route = self._api_route()
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        if route is None:
            if not self._static_path_allowed(path):
                self.send_error(404)
                return
            super().do_GET()
            return
        city, tail = route
        actor = self._actor()
        if actor is None or not actor_can_access_city(actor, city):
            self._send_json(403 if actor else 401, {"error": "authentication or city access required"})
            return
        if tail:
            if len(tail) == 2 and tail[0] == "evidence":
                self._send_evidence(city, tail[1])
                return
            self.send_error(404)
            return
        with connect(self.database_path) as con:
            init_db(con)
            payload = {
                "mode": "sqlite",
                "city_slug": city,
                "state": load_state(con, city),
                "actor": public_actor(actor),
            }
        self._send_json(200, payload)

    def do_PUT(self) -> None:
        try:
            route = self._api_route()
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        if route is None or route[1]:
            self.send_error(404)
            return
        city, _ = route
        actor = self._actor()
        if actor is None or not actor_can_access_city(actor, city):
            self._send_json(403 if actor else 401, {"error": "authentication or city access required"})
            return
        if not self._valid_csrf(actor):
            self._send_json(403, {"error": "valid CSRF token required"})
            return
        try:
            state = self._read_json()
            with connect(self.database_path) as con:
                init_db(con)
                saved = save_state(con, city, state, actor=actor, signing_key=self.attestation_key)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except PermissionError as exc:
            self._send_json(403, {"error": str(exc)})
            return
        self._send_json(200, {"mode": "sqlite", "city_slug": city, "state": saved, "actor": public_actor(actor)})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/ops-auth/login":
            self._login()
            return
        if path == "/api/ops-auth/logout":
            actor = self._actor()
            if actor is None or not self._valid_csrf(actor):
                self._send_json(403, {"error": "valid session and CSRF token required"})
                return
            token = self._session_token()
            if token:
                self.sessions.pop(token, None)
            self._send_json(200, {"authenticated": False}, clear_cookie=True)
            return
        try:
            route = self._api_route()
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        if route is None or route[1] != ["evidence"]:
            self.send_error(404)
            return
        city, _ = route
        actor = self._actor()
        if actor is None or not actor_can_access_city(actor, city):
            self._send_json(403 if actor else 401, {"error": "authentication or city access required"})
            return
        if not actor_has_role(actor, {"admin", "inspector", "document_controller"}):
            self._send_json(403, {"error": "evidence upload requires inspector or document-controller authority"})
            return
        if not self._valid_csrf(actor):
            self._send_json(403, {"error": "valid CSRF token required"})
            return
        try:
            metadata = self._receive_evidence(city, actor)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(201, {"evidence": metadata})

    def _api_route(self) -> tuple[str, list[str]] | None:
        path = urlparse(self.path).path
        prefix = "/api/ops-core/"
        if not path.startswith(prefix):
            return None
        parts = [unquote(part) for part in path[len(prefix):].strip("/").split("/") if part]
        if not parts or not CITY_RE.match(parts[0]):
            raise ValueError("invalid city slug")
        if any(part in {".", ".."} for part in parts):
            raise ValueError("invalid API path")
        return parts[0], parts[1:]

    def _api_city(self) -> str | None:
        """Compatibility helper for integrated servers using the state route."""
        route = self._api_route()
        return route[0] if route is not None and not route[1] else None

    def _static_path_allowed(self, request_path: str) -> bool:
        relative = unquote(request_path).lstrip("/")
        target = (REPO_ROOT / relative).resolve()
        try:
            target.relative_to(REPO_ROOT)
        except ValueError:
            return False
        if ".git" in target.relative_to(REPO_ROOT).parts:
            return False
        for private in self.private_paths:
            if target == private or (private.is_dir() and private in target.parents):
                return False
        return True

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            raise ValueError("empty request body")
        if length > 10_000_000:
            raise ValueError("request body too large")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("invalid JSON") from exc

    def _send_json(self, status: int, payload: dict, *, clear_cookie: bool = False, cookie: str = "") -> None:
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_api_headers("application/json; charset=utf-8")
        if clear_cookie:
            self.send_header("Set-Cookie", "osr_ops_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0")
        elif cookie:
            self.send_header("Set-Cookie", f"osr_ops_session={cookie}; Path=/; HttpOnly; SameSite=Strict; Max-Age={SESSION_SECONDS}")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_api_headers(self, content_type: str) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-CSRF-Token, X-OSR-Filename, X-OSR-Mime")
        self.send_header("Cache-Control", "no-store")

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        super().end_headers()

    def _login(self) -> None:
        if self.user_store is None:
            actor = trusted_actor()
        else:
            try:
                payload = self._read_json()
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            username = str(payload.get("username", "")).strip().lower()
            password = str(payload.get("password", ""))
            user = self.user_store.get(username)
            if user is None or not verify_password(user, password):
                time.sleep(0.15)
                self._send_json(401, {"error": "invalid username or password"})
                return
            actor = actor_from_user(user)
        token = secrets.token_urlsafe(32)
        actor["csrf"] = secrets.token_urlsafe(24)
        actor["expires_at"] = int(time.time()) + SESSION_SECONDS
        self.sessions[token] = actor
        self._send_json(200, {"authenticated": True, "actor": public_actor(actor)}, cookie=token)

    def _session_token(self) -> str:
        for part in self.headers.get("Cookie", "").split(";"):
            name, _, value = part.strip().partition("=")
            if name == "osr_ops_session":
                return value
        return ""

    def _actor(self, *, required: bool = True) -> dict | None:
        if self.user_store is None:
            return trusted_actor()
        token = self._session_token()
        actor = self.sessions.get(token)
        if actor and int(actor.get("expires_at", 0)) > int(time.time()):
            return actor
        if token:
            self.sessions.pop(token, None)
        return None

    def _valid_csrf(self, actor: dict) -> bool:
        if self.user_store is None:
            return True
        return hmac.compare_digest(str(actor.get("csrf", "")), self.headers.get("X-CSRF-Token", ""))

    def _receive_evidence(self, city: str, actor: dict) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            raise ValueError("empty evidence file")
        if length > MAX_EVIDENCE_BYTES:
            raise ValueError("evidence file exceeds 25 MiB")
        raw_name = unquote(self.headers.get("X-OSR-Filename", "evidence.bin"))
        file_name = safe_filename(raw_name)
        mime = self.headers.get("X-OSR-Mime", "").strip() or mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        body = self.rfile.read(length)
        sha256 = hashlib.sha256(body).hexdigest()
        target_dir = self.evidence_root / city / sha256[:2]
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{sha256}-{file_name}"
        if not target.exists():
            target.write_bytes(body)
            target.chmod(0o640)
        metadata = {
            "id": f"EVID-{sha256[:16]}",
            "city_slug": city,
            "file_name": file_name,
            "mime_type": mime,
            "size_bytes": len(body),
            "sha256": sha256,
            "uploaded_at": utc_now(),
            "uploaded_by_user_id": actor["user_id"],
            "uploaded_by": actor["display_name"],
            "url": f"/api/ops-core/{city}/evidence/{sha256}",
        }
        with connect(self.database_path) as con:
            init_db(con)
            with con:
                con.execute(
                    """
                    INSERT INTO evidence_files
                        (city_slug, sha256, file_name, mime_type, size_bytes, stored_path, uploaded_at, uploaded_by, payload)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(city_slug, sha256) DO NOTHING
                    """,
                    (city, sha256, file_name, mime, len(body), str(target), metadata["uploaded_at"], actor["user_id"], _payload(metadata)),
                )
        return metadata

    def _send_evidence(self, city: str, sha256: str) -> None:
        if not SHA256_RE.match(sha256):
            self.send_error(404)
            return
        with connect(self.database_path) as con:
            row = con.execute(
                "SELECT stored_path, file_name, mime_type, size_bytes FROM evidence_files WHERE city_slug = ? AND sha256 = ?",
                (city, sha256),
            ).fetchone()
        if row is None:
            self.send_error(404)
            return
        path = Path(row["stored_path"])
        try:
            path.relative_to(self.evidence_root)
        except ValueError:
            self.send_error(403)
            return
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != sha256:
            self._send_json(409, {"error": "evidence file missing or checksum mismatch"})
            return
        self.send_response(200)
        self.send_header("Content-Type", row["mime_type"] or "application/octet-stream")
        self.send_header("Content-Length", str(row["size_bytes"]))
        self.send_header("Content-Disposition", f'inline; filename="{safe_filename(row["file_name"])}"')
        self.send_header("Cache-Control", "private, no-store")
        self.end_headers()
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                self.wfile.write(chunk)


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(value).name).strip(".-")
    return (cleaned or "evidence.bin")[:160]


def load_or_create_signing_key(path: Path) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        key = path.read_bytes()
        if len(key) < 32:
            raise ValueError(f"attestation key is too short: {path}")
        return key
    key = secrets.token_bytes(32)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(key)
    return key


def load_users(path: Path) -> dict[str, dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load Ops user store {path}: {exc}") from exc
    users: dict[str, dict] = {}
    for row in payload.get("users", []):
        username = str(row.get("username", "")).strip().lower()
        roles = {str(role) for role in row.get("roles", [])}
        if not username or not roles or not roles <= set(ROLE_COLLECTIONS):
            raise ValueError(f"invalid Ops user record for {username or '<missing>'}")
        if username in users:
            raise ValueError(f"duplicate Ops username: {username}")
        users[username] = row
    if not users:
        raise ValueError("Ops user store has no users")
    return users


def verify_password(user: dict, password: str) -> bool:
    if not user.get("active", True):
        return False
    try:
        salt = bytes.fromhex(str(user["password"]["salt_hex"]))
        iterations = int(user["password"]["iterations"])
        expected = bytes.fromhex(str(user["password"]["hash_hex"]))
    except (KeyError, TypeError, ValueError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def actor_from_user(user: dict) -> dict:
    return {
        "user_id": str(user.get("user_id") or user["username"]),
        "username": str(user["username"]).lower(),
        "display_name": str(user.get("display_name") or user["username"]),
        "roles": sorted({str(role) for role in user.get("roles", [])}),
        "city_scopes": sorted({str(city) for city in user.get("city_scopes", ["*"])}),
    }


def trusted_actor() -> dict:
    return {
        "user_id": "local-admin",
        "username": "local-admin",
        "display_name": "Local administrator",
        "roles": ["admin"],
        "city_scopes": ["*"],
        "csrf": "local-trusted",
    }


def public_actor(actor: dict | None) -> dict | None:
    if actor is None:
        return None
    return {
        key: actor[key]
        for key in ("user_id", "username", "display_name", "roles", "city_scopes", "csrf")
        if key in actor
    }


def actor_has_role(actor: dict, roles: set[str]) -> bool:
    return bool(set(actor.get("roles", [])) & roles)


def actor_can_access_city(actor: dict, city: str) -> bool:
    scopes = set(actor.get("city_scopes", []))
    return "*" in scopes or city in scopes


def init_db(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS city_state (
            city_slug TEXT PRIMARY KEY,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS counters (
            city_slug TEXT NOT NULL,
            kind TEXT NOT NULL,
            value INTEGER NOT NULL,
            PRIMARY KEY (city_slug, kind)
        );

        CREATE TABLE IF NOT EXISTS work_orders (
            city_slug TEXT NOT NULL,
            id TEXT NOT NULL,
            position INTEGER NOT NULL,
            source_type TEXT,
            source_uid TEXT,
            asset_id TEXT,
            asset_name TEXT,
            asset_type TEXT,
            title TEXT,
            owner TEXT,
            priority TEXT,
            due_date TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            closed_at TEXT,
            payload TEXT NOT NULL,
            PRIMARY KEY (city_slug, id)
        );

        CREATE TABLE IF NOT EXISTS inspections (
            city_slug TEXT NOT NULL,
            id TEXT NOT NULL,
            position INTEGER NOT NULL,
            wo_id TEXT,
            asset_id TEXT,
            result TEXT,
            severity TEXT,
            evidence_ref TEXT,
            note TEXT,
            recorded_at TEXT,
            payload TEXT NOT NULL,
            PRIMARY KEY (city_slug, id)
        );

        CREATE TABLE IF NOT EXISTS defects (
            city_slug TEXT NOT NULL,
            id TEXT NOT NULL,
            position INTEGER NOT NULL,
            wo_id TEXT,
            inspection_id TEXT,
            asset_id TEXT,
            severity TEXT,
            finding TEXT,
            owner TEXT,
            due_date TEXT,
            status TEXT,
            created_at TEXT,
            resolved_at TEXT,
            payload TEXT NOT NULL,
            PRIMARY KEY (city_slug, id)
        );

        CREATE TABLE IF NOT EXISTS approvals (
            city_slug TEXT NOT NULL,
            id TEXT NOT NULL,
            position INTEGER NOT NULL,
            wo_id TEXT,
            inspection_id TEXT,
            decision TEXT,
            approved_by TEXT,
            approver_role TEXT,
            evidence_ref TEXT,
            recorded_at TEXT,
            payload TEXT NOT NULL,
            PRIMARY KEY (city_slug, id)
        );

        CREATE TABLE IF NOT EXISTS documents (
            city_slug TEXT NOT NULL,
            id TEXT NOT NULL,
            position INTEGER NOT NULL,
            document_id TEXT,
            revision TEXT,
            status TEXT,
            sha256 TEXT,
            uploaded_at TEXT,
            payload TEXT NOT NULL,
            PRIMARY KEY (city_slug, id),
            UNIQUE (city_slug, document_id, revision)
        );

        CREATE TABLE IF NOT EXISTS evidence_files (
            city_slug TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            file_name TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            stored_path TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            payload TEXT NOT NULL,
            PRIMARY KEY (city_slug, sha256)
        );

        CREATE TABLE IF NOT EXISTS audit_events (
            city_slug TEXT NOT NULL,
            id TEXT NOT NULL,
            position INTEGER NOT NULL,
            at TEXT,
            action TEXT,
            ref TEXT,
            detail TEXT,
            payload TEXT NOT NULL,
            PRIMARY KEY (city_slug, id)
        );

        CREATE TABLE IF NOT EXISTS project_records (
            city_slug TEXT NOT NULL,
            kind TEXT NOT NULL,
            id TEXT NOT NULL,
            position INTEGER NOT NULL,
            status TEXT,
            effective_at TEXT,
            payload TEXT NOT NULL,
            PRIMARY KEY (city_slug, kind, id)
        );

        CREATE INDEX IF NOT EXISTS idx_work_orders_city_status
            ON work_orders (city_slug, status, due_date);
        CREATE INDEX IF NOT EXISTS idx_work_orders_city_asset
            ON work_orders (city_slug, asset_id);
        CREATE INDEX IF NOT EXISTS idx_defects_city_status
            ON defects (city_slug, status, due_date);
        CREATE INDEX IF NOT EXISTS idx_inspections_city_work
            ON inspections (city_slug, wo_id);
        CREATE INDEX IF NOT EXISTS idx_approvals_city_work
            ON approvals (city_slug, wo_id, recorded_at);
        CREATE INDEX IF NOT EXISTS idx_documents_city_control
            ON documents (city_slug, document_id, revision, status);
        CREATE INDEX IF NOT EXISTS idx_project_records_city_kind_status
            ON project_records (city_slug, kind, status, effective_at);
        """
    )
    _ensure_column(con, "inspections", "evidence_ref", "TEXT")
    _ensure_column(con, "inspections", "note", "TEXT")
    _ensure_column(con, "defects", "finding", "TEXT")
    _ensure_column(con, "audit_events", "detail", "TEXT")


def _ensure_column(con: sqlite3.Connection, table: str, column: str, sql_type: str) -> None:
    columns = {
        row["name"]
        for row in con.execute(f"PRAGMA table_info({table})")
    }
    if column not in columns:
        con.execute(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")


def load_state(con: sqlite3.Connection, city: str) -> dict:
    counters = {
        row["kind"]: int(row["value"])
        for row in con.execute(
            "SELECT kind, value FROM counters WHERE city_slug = ? ORDER BY kind", (city,)
        )
    }
    state = empty_state()
    state["counters"].update(counters)
    for key, table in RECORD_TABLES.items():
        rows = con.execute(
            f"SELECT payload FROM {table} WHERE city_slug = ? ORDER BY position", (city,)
        )
        state[key] = [json.loads(row["payload"]) for row in rows]
    for key, kind in PROJECT_RECORD_KINDS.items():
        rows = con.execute(
            "SELECT payload FROM project_records WHERE city_slug = ? AND kind = ? ORDER BY position",
            (city, kind),
        )
        state[key] = [json.loads(row["payload"]) for row in rows]
    return state


def save_state(
    con: sqlite3.Connection,
    city: str,
    raw_state: dict,
    *,
    actor: dict | None = None,
    signing_key: bytes | None = None,
) -> dict:
    state = normalize_state(raw_state)
    if actor is not None:
        state = authorize_and_attest_state(
            con, city, load_state(con, city), state, actor, signing_key or b""
        )
    now = utc_now()
    with con:
        con.execute(
            """
            INSERT INTO city_state (city_slug, updated_at)
            VALUES (?, ?)
            ON CONFLICT(city_slug) DO UPDATE SET updated_at = excluded.updated_at
            """,
            (city, now),
        )
        con.execute("DELETE FROM counters WHERE city_slug = ?", (city,))
        con.executemany(
            "INSERT INTO counters (city_slug, kind, value) VALUES (?, ?, ?)",
            [(city, kind, int(value)) for kind, value in state["counters"].items()],
        )
        for table in RECORD_TABLES.values():
            con.execute(f"DELETE FROM {table} WHERE city_slug = ?", (city,))
        con.execute("DELETE FROM project_records WHERE city_slug = ?", (city,))
        _insert_work_orders(con, city, state["workOrders"])
        _insert_inspections(con, city, state["inspections"])
        _insert_approvals(con, city, state["approvals"])
        _insert_defects(con, city, state["defects"])
        _insert_documents(con, city, state["documents"])
        _insert_audit(con, city, state["audit"])
        _insert_project_records(con, city, state)
    return state


def empty_state() -> dict:
    return {
        "workOrders": [],
        "inspections": [],
        "approvals": [],
        "defects": [],
        "documents": [],
        "audit": [],
        "purchaseOrders": [],
        "deliveries": [],
        "invoices": [],
        "payments": [],
        "progressUpdates": [],
        "projectRevisions": [],
        "counters": {
            "workOrder": 1,
            "inspection": 1,
            "approval": 1,
            "defect": 1,
            "document": 1,
            "audit": 1,
            "purchaseOrder": 1,
            "delivery": 1,
            "invoice": 1,
            "payment": 1,
            "progressUpdate": 1,
            "projectRevision": 1,
        },
    }


def normalize_state(raw_state: dict) -> dict:
    if not isinstance(raw_state, dict):
        raise ValueError("state must be a JSON object")
    state = empty_state()
    for key in RECORD_TABLES:
        rows = raw_state.get(key, [])
        if not isinstance(rows, list):
            raise ValueError(f"{key} must be a list")
        state[key] = [row for row in rows if isinstance(row, dict)]
    for key in PROJECT_RECORD_KINDS:
        rows = raw_state.get(key, [])
        if not isinstance(rows, list):
            raise ValueError(f"{key} must be a list")
        state[key] = [row for row in rows if isinstance(row, dict)]
    counters = raw_state.get("counters", {})
    if isinstance(counters, dict):
        state["counters"].update({
            str(kind): int(value)
            for kind, value in counters.items()
            if str(kind) in state["counters"] and str(value).isdigit()
        })
    return state


def _payload(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True)


def _by_id(rows: list[dict]) -> dict[str, dict]:
    return {str(row.get("id")): row for row in rows if row.get("id")}


def _canonical_record(record: dict) -> bytes:
    unsigned = {key: value for key, value in record.items() if key != "signature"}
    return json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _attest(record: dict, record_type: str, actor: dict, signing_key: bytes) -> dict:
    result = dict(record)
    result["signed_by_user_id"] = actor["user_id"]
    result["signed_by"] = actor["display_name"]
    result["signed_at"] = utc_now()
    content_sha256 = hashlib.sha256(_canonical_record(result)).hexdigest()
    result["signature"] = {
        "scheme": "HMAC-SHA256/server-attestation-v1",
        "record_type": record_type,
        "content_sha256": content_sha256,
        "value": hmac.new(signing_key, content_sha256.encode("ascii"), hashlib.sha256).hexdigest(),
        "notice": "Authenticated server attestation; not a qualified electronic signature.",
    }
    return result


def _verify_attestation(record: dict, signing_key: bytes) -> bool:
    signature = record.get("signature")
    if not isinstance(signature, dict):
        return False
    content_sha256 = hashlib.sha256(_canonical_record(record)).hexdigest()
    expected = hmac.new(signing_key, content_sha256.encode("ascii"), hashlib.sha256).hexdigest()
    return (
        signature.get("scheme") == "HMAC-SHA256/server-attestation-v1"
        and hmac.compare_digest(str(signature.get("content_sha256", "")), content_sha256)
        and hmac.compare_digest(str(signature.get("value", "")), expected)
    )


def _allowed_collections(actor: dict) -> set[str]:
    allowed: set[str] = set()
    for role in actor.get("roles", []):
        allowed.update(ROLE_COLLECTIONS.get(role, set()))
    return allowed


def authorize_and_attest_state(
    con: sqlite3.Connection,
    city: str,
    current: dict,
    proposed: dict,
    actor: dict,
    signing_key: bytes,
) -> dict:
    if len(signing_key) < 32:
        raise ValueError("server attestation key unavailable")
    allowed = _allowed_collections(actor)
    immutable = {"inspections", "approvals", "documents", "audit"}
    changed: set[str] = set()
    for key in list(RECORD_TABLES) + list(PROJECT_RECORD_KINDS):
        before = _by_id(current[key])
        after = _by_id(proposed[key])
        if before != after:
            changed.add(key)
        if key in immutable:
            for record_id, row in before.items():
                if row.get("signature") and not _verify_attestation(row, signing_key):
                    raise ValueError(f"stored {key} record {record_id} failed attestation verification")
                if record_id not in after:
                    raise PermissionError(f"immutable {key} record {record_id} cannot be deleted")
                if after[record_id] != row:
                    raise PermissionError(f"immutable {key} record {record_id} cannot be changed")
    controlled_changes = changed - {"audit"}
    denied = sorted(controlled_changes - allowed)
    if denied:
        raise PermissionError(
            f"roles {', '.join(actor.get('roles', []))} cannot change: {', '.join(denied)}"
        )
    if changed and not controlled_changes and not actor_has_role(actor, {"admin", "planner", "maintainer", "inspector", "approver", "document_controller"}):
        raise PermissionError("read-only role cannot append audit records")

    result = normalize_state(proposed)
    for key in immutable:
        for index, row in enumerate(result[key]):
            if str(row.get("id")) in _by_id(current[key]) and not row.get("signature"):
                legacy_name = str(row.get("recorded_by") or row.get("approved_by") or row.get("uploaded_by") or "legacy-record")
                migration_actor = {
                    "user_id": f"legacy:{hashlib.sha256(legacy_name.encode('utf-8')).hexdigest()[:16]}",
                    "display_name": legacy_name,
                    "roles": ["legacy-migration"],
                }
                result[key][index] = _attest(row, f"legacy-{key}", migration_actor, signing_key)
    current_inspections = _by_id(current["inspections"])
    for index, row in enumerate(result["inspections"]):
        if str(row.get("id")) in current_inspections:
            continue
        if not actor_has_role(actor, {"admin", "inspector"}):
            raise PermissionError("inspection authority required")
        row = dict(row)
        row["recorded_by"] = actor["display_name"]
        row["recorded_role"] = ", ".join(actor.get("roles", []))
        result["inspections"][index] = _attest(row, "inspection", actor, signing_key)

    all_inspections = _by_id(result["inspections"])
    current_approvals = _by_id(current["approvals"])
    for index, row in enumerate(result["approvals"]):
        if str(row.get("id")) in current_approvals:
            continue
        if not actor_has_role(actor, {"admin", "approver"}):
            raise PermissionError("handback approval authority required")
        inspection = all_inspections.get(str(row.get("inspection_id", "")))
        if inspection is None or inspection.get("result") != "pass":
            raise ValueError("handback approval must reference a passing inspection")
        if str(inspection.get("signed_by_user_id", "")) == actor["user_id"]:
            raise PermissionError("inspector and handback approver must be different authenticated users")
        row = dict(row)
        row["approved_by"] = actor["display_name"]
        row["approver_role"] = ", ".join(actor.get("roles", []))
        result["approvals"][index] = _attest(row, "handback-approval", actor, signing_key)

    current_documents = _by_id(current["documents"])
    documents_by_control: dict[str, list[dict]] = {}
    document_revisions: set[tuple[str, str]] = set()
    for row in result["documents"]:
        control = str(row.get("document_id", ""))
        revision = str(row.get("revision", ""))
        if (control, revision) in document_revisions:
            raise ValueError(f"duplicate controlled document revision: {control} {revision}")
        document_revisions.add((control, revision))
        documents_by_control.setdefault(control, []).append(row)
    for index, row in enumerate(result["documents"]):
        if str(row.get("id")) in current_documents:
            continue
        if not actor_has_role(actor, {"admin", "document_controller"}):
            raise PermissionError("document-controller authority required")
        document_id = str(row.get("document_id", "")).strip()
        revision = str(row.get("revision", "")).strip()
        sha256 = str(row.get("sha256", ""))
        if not document_id or not revision or not SHA256_RE.match(sha256):
            raise ValueError("document id, revision and evidence SHA-256 are required")
        evidence = con.execute(
            "SELECT 1 FROM evidence_files WHERE city_slug = ? AND sha256 = ?",
            (city, sha256),
        ).fetchone()
        if evidence is None:
            raise ValueError(f"managed evidence {sha256} is not registered for {city}")
        prior = [item for item in documents_by_control[document_id] if item.get("id") != row.get("id")]
        if prior and str(row.get("supersedes", "")) not in {str(item.get("id")) for item in prior}:
            raise ValueError(f"new revision of {document_id} must identify the superseded record")
        row = dict(row)
        row["uploaded_by"] = actor["display_name"]
        row["uploaded_by_user_id"] = actor["user_id"]
        result["documents"][index] = _attest(row, "controlled-document", actor, signing_key)

    current_audit = _by_id(current["audit"])
    for index, row in enumerate(result["audit"]):
        if str(row.get("id")) not in current_audit:
            result["audit"][index] = _attest(row, "audit-event", actor, signing_key)
    validate_workflow(result)
    return result


def validate_workflow(state: dict) -> None:
    work_orders = _by_id(state["workOrders"])
    inspections = _by_id(state["inspections"])
    for inspection in inspections.values():
        if str(inspection.get("wo_id", "")) not in work_orders:
            raise ValueError(f"inspection {inspection.get('id')} references an unknown work order")
    for approval in state["approvals"]:
        inspection = inspections.get(str(approval.get("inspection_id", "")))
        if inspection is None or approval.get("wo_id") != inspection.get("wo_id"):
            raise ValueError(f"approval {approval.get('id')} does not match its inspection work order")
        if approval.get("decision") not in {"approved", "rejected"}:
            raise ValueError(f"approval {approval.get('id')} has an invalid decision")
    for work_order in work_orders.values():
        if work_order.get("status") != "closed":
            continue
        wo_id = work_order["id"]
        passing = next(
            (row for row in state["inspections"] if row.get("wo_id") == wo_id and row.get("result") == "pass"),
            None,
        )
        approval = next((row for row in state["approvals"] if row.get("wo_id") == wo_id), None)
        open_defect = next(
            (row for row in state["defects"] if row.get("wo_id") == wo_id and row.get("status") != "resolved"),
            None,
        )
        if passing is None or approval is None or approval.get("decision") != "approved":
            raise ValueError(f"closed work order {wo_id} lacks passing inspection and approval")
        if approval.get("inspection_id") != passing.get("id"):
            raise ValueError(f"closed work order {wo_id} approval is not for the latest passing inspection")
        if approval.get("signed_by_user_id") == passing.get("signed_by_user_id"):
            raise ValueError(f"closed work order {wo_id} violates segregation of duties")
        if open_defect is not None:
            raise ValueError(f"closed work order {wo_id} has open defect {open_defect.get('id')}")


def _insert_work_orders(con: sqlite3.Connection, city: str, rows: list[dict]) -> None:
    con.executemany(
        """
        INSERT INTO work_orders (
            city_slug, id, position, source_type, source_uid, asset_id,
            asset_name, asset_type, title, owner, priority, due_date, status,
            created_at, updated_at, closed_at, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                city,
                row.get("id", ""),
                idx,
                row.get("source_type", ""),
                row.get("source_uid", ""),
                row.get("asset_id", ""),
                row.get("asset_name", ""),
                row.get("asset_type", ""),
                row.get("title", ""),
                row.get("owner", ""),
                row.get("priority", ""),
                row.get("due_date", ""),
                row.get("status", ""),
                row.get("created_at", ""),
                row.get("updated_at", ""),
                row.get("closed_at", ""),
                _payload(row),
            )
            for idx, row in enumerate(rows)
            if row.get("id")
        ],
    )


def _insert_inspections(con: sqlite3.Connection, city: str, rows: list[dict]) -> None:
    con.executemany(
        """
        INSERT INTO inspections (
            city_slug, id, position, wo_id, asset_id, result, severity,
            evidence_ref, note, recorded_at, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                city,
                row.get("id", ""),
                idx,
                row.get("wo_id", ""),
                row.get("asset_id", ""),
                row.get("result", ""),
                row.get("severity", ""),
                row.get("evidence_ref", ""),
                row.get("note", ""),
                row.get("recorded_at", ""),
                _payload(row),
            )
            for idx, row in enumerate(rows)
            if row.get("id")
        ],
    )


def _insert_approvals(con: sqlite3.Connection, city: str, rows: list[dict]) -> None:
    con.executemany(
        """
        INSERT INTO approvals (
            city_slug, id, position, wo_id, inspection_id, decision,
            approved_by, approver_role, evidence_ref, recorded_at, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                city,
                row.get("id", ""),
                idx,
                row.get("wo_id", ""),
                row.get("inspection_id", ""),
                row.get("decision", ""),
                row.get("approved_by", ""),
                row.get("approver_role", ""),
                row.get("evidence_ref", ""),
                row.get("recorded_at", ""),
                _payload(row),
            )
            for idx, row in enumerate(rows)
            if row.get("id")
        ],
    )


def _insert_defects(con: sqlite3.Connection, city: str, rows: list[dict]) -> None:
    con.executemany(
        """
        INSERT INTO defects (
            city_slug, id, position, wo_id, inspection_id, asset_id,
            severity, finding, owner, due_date, status, created_at, resolved_at, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                city,
                row.get("id", ""),
                idx,
                row.get("wo_id", ""),
                row.get("inspection_id", ""),
                row.get("asset_id", ""),
                row.get("severity", ""),
                row.get("finding", ""),
                row.get("owner", ""),
                row.get("due_date", ""),
                row.get("status", ""),
                row.get("created_at", ""),
                row.get("resolved_at", ""),
                _payload(row),
            )
            for idx, row in enumerate(rows)
            if row.get("id")
        ],
    )


def _insert_documents(con: sqlite3.Connection, city: str, rows: list[dict]) -> None:
    con.executemany(
        """
        INSERT INTO documents (
            city_slug, id, position, document_id, revision, status,
            sha256, uploaded_at, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                city,
                row.get("id", ""),
                idx,
                row.get("document_id", ""),
                row.get("revision", ""),
                row.get("status", ""),
                row.get("sha256", ""),
                row.get("uploaded_at", ""),
                _payload(row),
            )
            for idx, row in enumerate(rows)
            if row.get("id")
        ],
    )


def _insert_audit(con: sqlite3.Connection, city: str, rows: list[dict]) -> None:
    con.executemany(
        """
        INSERT INTO audit_events (
            city_slug, id, position, at, action, ref, detail, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                city,
                row.get("id", ""),
                idx,
                row.get("at", ""),
                row.get("action", ""),
                row.get("ref", ""),
                row.get("detail", ""),
                _payload(row),
            )
            for idx, row in enumerate(rows)
            if row.get("id")
        ],
    )


def _insert_project_records(con: sqlite3.Connection, city: str, state: dict) -> None:
    values: list[tuple] = []
    for key, kind in PROJECT_RECORD_KINDS.items():
        for position, row in enumerate(state[key]):
            record_id = str(
                row.get("id")
                or row.get("purchase_order_id")
                or row.get("delivery_id")
                or row.get("invoice_id")
                or row.get("payment_id")
                or row.get("progress_update_id")
                or row.get("revision_id")
                or ""
            )
            if not record_id:
                continue
            values.append(
                (
                    city,
                    kind,
                    record_id,
                    position,
                    row.get("status", ""),
                    row.get("effective_at", row.get("at", "")),
                    _payload(row),
                )
            )
    con.executemany(
        """
        INSERT INTO project_records (
            city_slug, kind, id, position, status, effective_at, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        values,
    )


if __name__ == "__main__":
    raise SystemExit(main())
