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

from .contracts import canonical, fingerprint, identity as validate_identity
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

APPLICABILITY_SCHEMA = "osr-evidence-applicability/1"
APPLICABILITY_FIELDS = {
    "schema",
    "project",
    "configuration_revision",
    "baseline_sha256",
    "candidate_id",
    "physical_part_id",
    "material_batch",
    "definition_sha256",
}


def normalize_record_scope(identity, applicability=None):
    """Validate the retained design identity and exact evidence applicability.

    Absent optional fields are explicit nulls. They never match a named candidate,
    part, batch or definition. The full navigation identity is retained separately
    so a caller cannot accidentally discard project/revision/baseline or run IDs.
    """
    scoped_identity = dict(validate_identity(identity))
    expected = {
        "schema": APPLICABILITY_SCHEMA,
        "project": scoped_identity["project"],
        "configuration_revision": scoped_identity["configuration_revision"],
        "baseline_sha256": scoped_identity["baseline_sha256"],
        "candidate_id": None,
        "physical_part_id": scoped_identity["part_id"],
        "material_batch": None,
        "definition_sha256": None,
    }
    if applicability is not None:
        if (
            not isinstance(applicability, dict)
            or set(applicability) - APPLICABILITY_FIELDS
        ):
            raise ValueError("controlled evidence applicability fields required")
        expected.update(applicability)
    if expected["schema"] != APPLICABILITY_SCHEMA:
        raise ValueError("versioned evidence applicability required")
    for key in ("project", "configuration_revision", "baseline_sha256"):
        if expected[key] != scoped_identity[key]:
            raise ValueError("evidence applicability differs from its identity: " + key)
    for key in ("candidate_id", "physical_part_id", "material_batch"):
        value = expected[key]
        if value is not None and (
            not isinstance(value, str) or not 0 < len(value) <= 160
        ):
            raise ValueError("bounded evidence applicability required: " + key)
    if (
        scoped_identity["part_id"] is not None
        and expected["physical_part_id"] != scoped_identity["part_id"]
    ):
        raise ValueError("evidence physical part differs from its identity")
    digest = expected["definition_sha256"]
    if digest is not None and (
        not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest)
    ):
        raise ValueError("exact definition digest required")
    canonical(expected)
    return scoped_identity, expected


def record_applicability(row, identity, applicability=None, *, require_verified=True):
    """Return exact-scope eligibility, never an engineering acceptance.

    Legacy city/environment-only records remain available for audit but cannot
    contribute to candidate assessment. Reissue them as new scoped records.
    """
    target_identity, target_applicability = normalize_record_scope(
        identity, applicability
    )
    reasons = []
    if row.get("identity") is None or row.get("applicability") is None:
        return dict(
            eligible=False,
            state="unknown",
            reasons=[
                "legacy or unscoped evidence; reissue with explicit applicability"
            ],
        )
    try:
        record_identity, record_scope = normalize_record_scope(
            row["identity"], row["applicability"]
        )
    except (ValueError, TypeError, KeyError):
        return dict(
            eligible=False, state="unknown", reasons=["invalid retained evidence scope"]
        )
    if record_identity != target_identity:
        reasons.append("different canonical design identity")
    if record_scope != target_applicability:
        reasons.append(
            "different explicit evidence applicability; null is not a wildcard"
        )
    if (
        record_identity["baseline_sha256"] is None
        or record_identity["configuration_revision"] == "unselected"
    ):
        reasons.append("unknown baseline or configuration revision")
    if (
        row.get("city") != record_identity["city"]
        or row.get("environment") != record_identity["environment"]
    ):
        reasons.append("record location differs from its retained identity")
    content = dict(
        kind=row.get("kind"),
        city=row.get("city"),
        environment=row.get("environment"),
        payload=row.get("payload"),
        identity=record_identity,
        applicability=record_scope,
    )
    if row.get("revision") != fingerprint(content):
        reasons.append("record content no longer matches its scoped revision")
    if require_verified:
        verification = row.get("verification") or {}
        if row.get("state") != "verified-record" or verification.get(
            "revision"
        ) != row.get("revision"):
            reasons.append(
                "record lacks independent completeness and integrity verification"
            )
        if (
            verification.get("identity") != record_identity
            or verification.get("applicability") != record_scope
        ):
            reasons.append(
                "independent verification does not cover this exact evidence scope"
            )
    return dict(
        eligible=not reasons,
        state="eligible" if not reasons else "unknown",
        reasons=reasons,
    )


def _decoded_record(row):
    result = dict(row)
    for key in ("payload", "verification", "identity", "applicability"):
        result[key] = json.loads(result[key]) if result.get(key) is not None else None
    result.update(physical_release=False, independent_acceptance=False)
    return result


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
            con.execute("BEGIN IMMEDIATE")
            # Additive migration only: the omitted identity of an old record
            # cannot be reconstructed from today's selected project or revision.
            columns = {
                row[1] for row in con.execute("PRAGMA table_info(review_records)")
            }
            for name, declaration in (
                ("identity", "TEXT"),
                ("applicability", "TEXT"),
                ("scope_state", "TEXT NOT NULL DEFAULT 'legacy-unscoped'"),
            ):
                if name not in columns:
                    con.execute(
                        "ALTER TABLE review_records ADD COLUMN "
                        + name
                        + " "
                        + declaration
                    )

    def list(self, city, environment):
        with self.store.connect() as con:
            rows = [
                dict(r)
                for r in con.execute(
                    "SELECT * FROM review_records WHERE city=? AND environment=? ORDER BY created DESC LIMIT 200",
                    (city, environment),
                )
            ]
        return [_decoded_record(row) for row in rows]

    def submit(
        self,
        city,
        environment,
        kind,
        payload,
        actor,
        key,
        *,
        identity=None,
        applicability=None,
    ):
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
        if identity is None:
            if applicability is not None:
                raise ValueError(
                    "evidence applicability needs its full canonical identity"
                )
            scoped_identity, scope = None, None
            scope_state = "legacy-unscoped"
        else:
            scoped_identity, scope = normalize_record_scope(identity, applicability)
            if (
                scoped_identity["city"] != city
                or scoped_identity["environment"] != environment
            ):
                raise ValueError("record is outside its canonical identity")
            for payload_key, scope_key in (
                ("batch", "material_batch"),
                ("candidate", "candidate_id"),
            ):
                if (
                    scope[scope_key] is not None
                    and payload_key in payload
                    and payload[payload_key] != scope[scope_key]
                ):
                    raise ValueError(
                        "record payload differs from its declared " + scope_key
                    )
            scope_state = (
                "scoped"
                if scoped_identity["baseline_sha256"] is not None
                else "incomplete-scope"
            )
        revision_content = dict(
            kind=kind, city=city, environment=environment, payload=payload
        )
        if scoped_identity is not None:
            revision_content.update(identity=scoped_identity, applicability=scope)
        revision = fingerprint(revision_content)
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
                    "INSERT INTO review_records(id,city,environment,kind,creator,created,revision,payload,state,verifier,verification,identity,applicability,scope_state) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
                        (
                            canonical(scoped_identity).decode()
                            if scoped_identity is not None
                            else None
                        ),
                        canonical(scope).decode() if scope is not None else None,
                        scope_state,
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
                        canonical(
                            dict(
                                revision=revision,
                                identity=scoped_identity,
                                applicability=scope,
                                scope_state=scope_state,
                            )
                        ).decode(),
                    ),
                )
        with self.store.connect() as con:
            row = dict(
                con.execute(
                    "SELECT * FROM review_records WHERE id=?", (identifier,)
                ).fetchone()
            )
        return _decoded_record(row)

    def verify(
        self,
        identifier,
        expected_revision,
        actor,
        *,
        city,
        environment,
        evidence_root,
        identity=None,
        applicability=None,
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
            retained = _decoded_record(row)
            if retained["identity"] is not None:
                if identity is None:
                    raise ValueError(
                        "independent review requires the exact retained design identity and applicability"
                    )
                eligible = record_applicability(
                    retained, identity, applicability, require_verified=False
                )
                if not eligible["eligible"]:
                    raise ValueError(
                        "record is outside the selected evidence scope: "
                        + "; ".join(eligible["reasons"])
                    )
            elif identity is not None or applicability is not None:
                raise ValueError(
                    "legacy record has unknown project/revision applicability; reissue it explicitly"
                )
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
                schema="osr-record-verification/2",
                record=identifier,
                revision=expected_revision,
                reviewer=actor_id,
                verified_at=now(),
                scope=dict(city=city, environment=environment),
                identity=retained["identity"],
                applicability=retained["applicability"],
                scope_state=retained["scope_state"],
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
