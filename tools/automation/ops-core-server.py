#!/usr/bin/env python3
"""Serve the OSR operations portal with a small SQLite Ops Core API."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = REPO_ROOT / "var" / "ops-core.sqlite3"
CITY_RE = re.compile(r"^[A-Za-z0-9_.-]+$")

RECORD_TABLES = {
    "workOrders": "work_orders",
    "inspections": "inspections",
    "approvals": "approvals",
    "defects": "defects",
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Serve the operations portal and persist Ops Core records in SQLite."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8008)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
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

    class Handler(OpsCoreHandler):
        database_path = db_path

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"serving {REPO_ROOT} on http://{args.host}:{args.port}/")
    print(f"ops core sqlite: {db_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


class OpsCoreHandler(SimpleHTTPRequestHandler):
    database_path: Path

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

    def handle(self) -> None:
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            return

    def do_OPTIONS(self) -> None:
        try:
            city = self._api_city()
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        if city is None:
            self.send_error(404)
            return
        self.send_response(204)
        self._send_api_headers("application/json")
        self.end_headers()

    def do_GET(self) -> None:
        try:
            city = self._api_city()
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        if city is None:
            super().do_GET()
            return
        with connect(self.database_path) as con:
            init_db(con)
            payload = {
                "mode": "sqlite",
                "city_slug": city,
                "state": load_state(con, city),
            }
        self._send_json(200, payload)

    def do_PUT(self) -> None:
        try:
            city = self._api_city()
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        if city is None:
            self.send_error(404)
            return
        try:
            state = self._read_json()
            with connect(self.database_path) as con:
                init_db(con)
                saved = save_state(con, city, state)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(200, {"mode": "sqlite", "city_slug": city, "state": saved})

    def _api_city(self) -> str | None:
        path = urlparse(self.path).path
        prefix = "/api/ops-core/"
        if not path.startswith(prefix):
            return None
        city = unquote(path[len(prefix):]).strip("/")
        if not city or "/" in city or not CITY_RE.match(city):
            raise ValueError("invalid city slug")
        return city

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

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_api_headers("application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_api_headers(self, content_type: str) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


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


def save_state(con: sqlite3.Connection, city: str, raw_state: dict) -> dict:
    state = normalize_state(raw_state)
    now = datetime.now(timezone.utc).isoformat()
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
        _insert_audit(con, city, state["audit"])
        _insert_project_records(con, city, state)
    return state


def empty_state() -> dict:
    return {
        "workOrders": [],
        "inspections": [],
        "approvals": [],
        "defects": [],
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
