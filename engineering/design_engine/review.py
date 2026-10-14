"""Future appointments and evidence intake with separate authenticated review.

Record verification checks identity, completeness and retained evidence hashes.
It does not issue a material, engineering, construction or railway acceptance.
"""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import uuid
from datetime import date

from .contracts import canonical, fingerprint
from .store import now

KINDS = {
    "appointment",
    "material",
    "quotation",
    "measurement",
    "calibration",
    "site",
    "inspection",
    "decision",
}
REQUIRED = {
    "appointment": {
        "person_name",
        "organization",
        "role",
        "appointment_scope",
        "identity_reference",
        "valid_until",
    },
    "material": {
        "supplier",
        "grade",
        "batch",
        "conditions",
        "properties",
        "source_reference",
    },
    "quotation": {
        "supplier",
        "place",
        "date",
        "currency",
        "scope",
        "line_items",
        "source_reference",
    },
    "measurement": {
        "specimen",
        "candidate",
        "test_method",
        "instrument",
        "uncertainty",
        "observations",
        "source_reference",
    },
    "calibration": {
        "model",
        "training_specimens",
        "holdout_specimens",
        "parameters",
        "uncertainty",
        "source_reference",
    },
    "site": {
        "site",
        "crs",
        "survey_date",
        "ground_water_utilities",
        "calibration",
        "source_reference",
    },
    "inspection": {
        "asset",
        "revision",
        "method",
        "observations",
        "inspector",
        "source_reference",
    },
    "decision": {
        "candidate",
        "revision",
        "scope",
        "authority",
        "rationale",
        "source_reference",
    },
}


class ReviewStore:
    def __init__(self, store):
        self.store = store
        with store.connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS review_records(
                id TEXT PRIMARY KEY,city TEXT NOT NULL,environment TEXT NOT NULL,kind TEXT NOT NULL,
                creator TEXT NOT NULL,created TEXT NOT NULL,revision TEXT NOT NULL,payload TEXT NOT NULL,
                state TEXT NOT NULL,verifier TEXT,verification TEXT
            );
            CREATE TABLE IF NOT EXISTS review_events(
                sequence INTEGER PRIMARY KEY,record TEXT NOT NULL,time TEXT NOT NULL,
                actor TEXT NOT NULL,event TEXT NOT NULL,payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS review_submissions(
                city TEXT NOT NULL,environment TEXT NOT NULL,actor TEXT NOT NULL,idempotency_key TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,record TEXT NOT NULL,
                PRIMARY KEY(city,environment,actor,idempotency_key)
            );
        """)

    def list(self, city, environment):
        with self.store.connect() as con:
            rows = [
                dict(r)
                for r in con.execute(
                    "SELECT * FROM review_records WHERE city=? AND environment=? ORDER BY created DESC LIMIT 200",
                    (city, environment),
                )
            ]
        for row in rows:
            row["payload"] = json.loads(row["payload"])
            row["verification"] = (
                json.loads(row["verification"]) if row["verification"] else None
            )
            row["physical_release"] = False
            row["independent_acceptance"] = False
        return rows

    def submit(self, city, environment, kind, payload, actor, key):
        if kind not in KINDS:
            raise ValueError("controlled evidence or appointment type required")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", city) or environment not in {
            "simulation",
            "physical",
            "training",
        }:
            raise ValueError("explicit record scope required")
        if not actor or not re.fullmatch(r"[A-Za-z0-9_-]{8,80}", key):
            raise ValueError("actor and idempotency key required")
        if not isinstance(payload, dict) or len(canonical(payload)) > 128 * 1024:
            raise ValueError("bounded structured record required")
        if set(payload) - REQUIRED[kind]:
            raise ValueError(
                "record contains unknown fields or attempted approval properties"
            )
        revision = fingerprint(
            dict(kind=kind, city=city, environment=environment, payload=payload)
        )
        with self.store.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            prior = con.execute(
                "SELECT * FROM review_submissions WHERE city=? AND environment=? AND actor=? AND idempotency_key=?",
                (city, environment, actor, key),
            ).fetchone()
            if prior:
                if prior["payload_sha256"] != revision:
                    raise ValueError(
                        "idempotency key was reused with different record content"
                    )
                identifier = prior["record"]
            else:
                identifier = "record-" + uuid.uuid4().hex[:16]
                con.execute(
                    "INSERT INTO review_records VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        identifier,
                        city,
                        environment,
                        kind,
                        actor,
                        now(),
                        revision,
                        canonical(payload).decode(),
                        "draft",
                        None,
                        None,
                    ),
                )
                con.execute(
                    "INSERT INTO review_submissions VALUES(?,?,?,?,?,?)",
                    (city, environment, actor, key, revision, identifier),
                )
                con.execute(
                    "INSERT INTO review_events(record,time,actor,event,payload) VALUES(?,?,?,?,?)",
                    (
                        identifier,
                        now(),
                        actor,
                        "submitted",
                        canonical(dict(revision=revision)).decode(),
                    ),
                )
        with self.store.connect() as con:
            row = dict(
                con.execute(
                    "SELECT * FROM review_records WHERE id=?", (identifier,)
                ).fetchone()
            )
        row["payload"] = json.loads(row["payload"])
        row["verification"] = (
            json.loads(row["verification"]) if row["verification"] else None
        )
        row.update(physical_release=False, independent_acceptance=False)
        return row

    def verify(
        self, identifier, expected_revision, actor, *, city, environment, evidence_root
    ):
        # Actor must come from the existing authenticated account/session path;
        # an actor or role supplied in navigation or request JSON is insufficient.
        if (
            not isinstance(actor, dict)
            or not actor.get("username")
            or not set(actor.get("roles", [])) & {"approver", "admin"}
        ):
            raise PermissionError("authenticated record reviewer required")
        actor_id = actor["username"]
        allowed = actor.get("city_scopes", [])
        if "*" not in allowed and city not in allowed:
            raise PermissionError("review account is outside this city")
        with self.store.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT * FROM review_records WHERE id=?", (identifier,)
            ).fetchone()
            if row is None or row["city"] != city or row["environment"] != environment:
                raise ValueError("record is outside the selected scope")
            if row["revision"] != expected_revision:
                raise ValueError("review refers to an altered record revision")
            if row["creator"] == actor_id:
                raise PermissionError(
                    "record author cannot verify their own submission"
                )
            if row["state"] != "draft":
                raise ValueError(
                    "verified record cannot be silently re-reviewed or overwritten"
                )
            payload = json.loads(row["payload"])
            missing = sorted(
                k
                for k in REQUIRED[row["kind"]]
                if k not in payload or payload[k] in (None, "", [], {})
            )
            if missing:
                raise ValueError("missing required record data: " + ", ".join(missing))
            if (
                row["kind"] == "appointment"
                and date.fromisoformat(payload["valid_until"]) < date.today()
            ):
                raise ValueError("appointment has expired")
            if row["kind"] == "quotation":
                if payload["currency"] not in {
                    "USD",
                    "IQD",
                    "EUR",
                    "GBP",
                } or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", payload["date"]):
                    raise ValueError("dated currency-qualified quotation required")
                for line in payload["line_items"]:
                    if (
                        set(line) != {"description", "quantity", "unit", "unit_price"}
                        or type(line["quantity"]) not in (int, float)
                        or type(line["unit_price"]) not in (int, float)
                        or line["quantity"] <= 0
                        or line["unit_price"] < 0
                    ):
                        raise ValueError(
                            "complete nonnegative priced scope lines required"
                        )
            if row["kind"] == "calibration":
                if not isinstance(
                    payload["training_specimens"], list
                ) or not isinstance(payload["holdout_specimens"], list):
                    raise ValueError(
                        "named training and holdout specimen lists required"
                    )
                if set(payload["training_specimens"]) & set(
                    payload["holdout_specimens"]
                ):
                    raise ValueError("independent holdout specimens required")
            reference = payload.get("source_reference") or payload.get(
                "identity_reference"
            )
            if not isinstance(reference, dict) or set(reference) != {"path", "sha256"}:
                raise ValueError("retained evidence path and exact checksum required")
            base = Path(evidence_root).resolve()
            name = Path(reference["path"])
            path = base / name
            if (
                name.is_absolute()
                or ".." in name.parts
                or path.is_symlink()
                or not path.resolve().is_relative_to(base)
                or not path.is_file()
            ):
                raise ValueError(
                    "evidence must remain inside the controlled private evidence store"
                )
            if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
                raise ValueError("evidence hash changed or does not match the record")
            result = dict(
                schema="osr-record-verification/1",
                record=identifier,
                revision=expected_revision,
                reviewer=actor_id,
                verified_at=now(),
                scope=dict(city=city, environment=environment),
                evidence_sha256=reference["sha256"],
                verification="authenticated independent record-completeness and byte-integrity review",
                technical_applicability_accepted=False,
                physical_correlation=False,
                independent_acceptance=False,
                physical_release=False,
            )
            con.execute(
                "UPDATE review_records SET state=?,verifier=?,verification=? WHERE id=?",
                ("verified-record", actor_id, canonical(result).decode(), identifier),
            )
            con.execute(
                "INSERT INTO review_events(record,time,actor,event,payload) VALUES(?,?,?,?,?)",
                (
                    identifier,
                    now(),
                    actor_id,
                    "verified-record",
                    canonical(result).decode(),
                ),
            )
        return result
