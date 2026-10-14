"""Indexed experiments alongside ERP, railway assurance and gateway databases.

Each attempt and sealed result is immutable. Resume appends a new attempt;
failed/cancelled attempts remain visible. No business or railway baseline lives
in this store.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
import sqlite3
import threading
import uuid

from .contracts import canonical, fingerprint, load, identity
from .publication import digest, safe

_LOCAL_PID = os.getpid()
_LOCAL_PROCESS_TOKEN = "local:" + uuid.uuid4().hex
_IDENTITY_LOCK = threading.Lock()


def now():
    return datetime.now(timezone.utc).isoformat()


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.database = self.root / "index.sqlite3"
        with self.connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS jobs(
                id TEXT PRIMARY KEY, created TEXT NOT NULL, updated TEXT NOT NULL,
                city TEXT NOT NULL, environment TEXT NOT NULL, status TEXT NOT NULL,
                phase TEXT NOT NULL, progress REAL NOT NULL, request TEXT NOT NULL,
                error TEXT, cancel_requested INTEGER NOT NULL DEFAULT 0,
                pid INTEGER, process_start TEXT, active_attempt INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS attempts(
                job TEXT NOT NULL, number INTEGER NOT NULL, started TEXT NOT NULL,
                ended TEXT, status TEXT NOT NULL, error TEXT, manifest TEXT,
                PRIMARY KEY(job,number), FOREIGN KEY(job) REFERENCES jobs(id)
            );
            CREATE TABLE IF NOT EXISTS events(
                sequence INTEGER PRIMARY KEY, job TEXT NOT NULL, time TEXT NOT NULL, payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dispatches(job TEXT PRIMARY KEY,pid INTEGER NOT NULL,process_start TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS job_submissions(key TEXT PRIMARY KEY,request_sha256 TEXT NOT NULL,job TEXT NOT NULL REFERENCES jobs(id));
            """)
        self.root.chmod(0o700)

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.database, timeout=30)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        try:
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    def create(self, request, *, idempotency_key=None):
        scope = identity(request["identity"])
        if idempotency_key is not None and (
            not isinstance(idempotency_key, str)
            or not re.fullmatch(r"[a-f0-9]{64}", idempotency_key)
        ):
            raise ValueError("exact scoped job submission digest required")
        identifier = "run-" + uuid.uuid4().hex[:16]
        instant = now()
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            if idempotency_key is not None:
                prior = con.execute(
                    "SELECT * FROM job_submissions WHERE key=?", (idempotency_key,)
                ).fetchone()
                if prior:
                    if prior["request_sha256"] != fingerprint(request):
                        raise ValueError("job submission key reused for altered inputs")
                    return self.get(prior["job"])
            write_new(self.root / "runs" / identifier / "request.json", request)
            con.execute(
                "INSERT INTO jobs(id,created,updated,city,environment,status,phase,progress,request) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    identifier,
                    instant,
                    instant,
                    scope["city"],
                    scope["environment"],
                    "queued",
                    "queued",
                    0,
                    canonical(request).decode(),
                ),
            )
            if idempotency_key is not None:
                con.execute(
                    "INSERT INTO job_submissions VALUES(?,?,?)",
                    (idempotency_key, fingerprint(request), identifier),
                )
        self.event(
            identifier, dict(kind="created", request_sha256=fingerprint(request))
        )
        return self.get(identifier)

    def get(self, identifier):
        with self.connect() as con:
            row = con.execute("SELECT * FROM jobs WHERE id=?", (identifier,)).fetchone()
            if row is None:
                raise ValueError("unknown design job")
            result = dict(row)
            result["request"] = json.loads(result["request"])
            result["attempts"] = [
                dict(a)
                for a in con.execute(
                    "SELECT * FROM attempts WHERE job=? ORDER BY number", (identifier,)
                )
            ]
        result["physical_release"] = False
        result["independently_accepted"] = False
        return result

    def list(self, city, environment):
        with self.connect() as con:
            ids = [
                r[0]
                for r in con.execute(
                    "SELECT id FROM jobs WHERE city=? AND environment=? ORDER BY created DESC LIMIT 100",
                    (city, environment),
                )
            ]
        return [self.get(i) for i in ids]

    def event(self, identifier, payload):
        with self.connect() as con:
            con.execute(
                "INSERT INTO events(job,time,payload) VALUES(?,?,?)",
                (identifier, now(), canonical(payload).decode()),
            )

    def begin(self, identifier, pid):
        started = process_start(pid)
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM jobs WHERE id=?", (identifier,)).fetchone()
            if row is None or row["status"] not in {"queued", "resuming"}:
                raise ValueError("job cannot start in this state")
            attempt = row["active_attempt"] + 1
            con.execute(
                "INSERT INTO attempts(job,number,started,status) VALUES(?,?,?,?)",
                (identifier, attempt, now(), "running"),
            )
            con.execute(
                "UPDATE jobs SET active_attempt=?,pid=?,process_start=?,status=?,phase=?,updated=? WHERE id=?",
                (attempt, pid, started, "running", "preflight", now(), identifier),
            )
        folder = self.root / "runs" / identifier / f"attempt-{attempt:04d}"
        folder.mkdir()
        return folder

    def update(self, identifier, phase, progress):
        with self.connect() as con:
            con.execute(
                "UPDATE jobs SET phase=?,progress=?,updated=? WHERE id=?",
                (phase, progress, now(), identifier),
            )

    def cancelled(self, identifier):
        with self.connect() as con:
            return bool(
                con.execute(
                    "SELECT cancel_requested FROM jobs WHERE id=?", (identifier,)
                ).fetchone()[0]
            )

    def cancel(self, identifier):
        row = self.get(identifier)
        if row["status"] not in {"queued", "running", "resuming", "cancelling"}:
            raise ValueError("only active jobs may be cancelled")
        with self.connect() as con:
            con.execute(
                "UPDATE jobs SET cancel_requested=1,updated=? WHERE id=?",
                (now(), identifier),
            )
        self.event(identifier, dict(kind="cancellation-requested"))
        return self.get(identifier)

    def finish(self, identifier, status, error=None, manifest=None):
        if status not in {
            "completed",
            "failed",
            "cancelled",
            "timeout",
            "budget-exceeded",
            "outside-domain",
            "unavailable",
            "interrupted",
        }:
            raise ValueError("explicit terminal job state required")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT active_attempt,status FROM jobs WHERE id=?", (identifier,)
            ).fetchone()
            if row is None or row["status"] not in {
                "queued",
                "running",
                "resuming",
                "cancelling",
            }:
                raise ValueError("terminal attempts cannot be rewritten")
            con.execute(
                "UPDATE attempts SET ended=?,status=?,error=?,manifest=? WHERE job=? AND number=? AND ended IS NULL",
                (
                    now(),
                    status,
                    error,
                    canonical(manifest).decode() if manifest else None,
                    identifier,
                    row[0],
                ),
            )
            con.execute(
                "UPDATE jobs SET status=?,phase=?,progress=100,error=?,updated=?,pid=NULL,process_start=NULL WHERE id=?",
                (status, status, error, now(), identifier),
            )
            con.execute("DELETE FROM dispatches WHERE job=?", (identifier,))
        self.event(
            identifier, dict(kind="attempt-finished", status=status, error=error)
        )

    def claim_dispatch(self, identifier):
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            job = con.execute(
                "SELECT status FROM jobs WHERE id=?", (identifier,)
            ).fetchone()
            if job is None or job[0] not in {"queued", "resuming"}:
                return False
            previous = con.execute(
                "SELECT * FROM dispatches WHERE job=?", (identifier,)
            ).fetchone()
            if (
                previous
                and process_ownership(previous["pid"], previous["process_start"])
                is not False
            ):
                return False
            con.execute(
                "INSERT OR REPLACE INTO dispatches VALUES(?,?,?)",
                (identifier, os.getpid(), process_start(os.getpid())),
            )
        return True

    def pending(self):
        with self.connect() as con:
            rows = [
                dict(r)
                for r in con.execute(
                    "SELECT j.id,d.pid,d.process_start FROM jobs j LEFT JOIN dispatches d ON d.job=j.id WHERE j.status IN ('queued','resuming')"
                )
            ]
        return [
            r["id"]
            for r in rows
            if r["pid"] is None
            or process_ownership(r["pid"], r["process_start"]) is False
        ]

    def resume(self, identifier, dependencies, toolchain):
        job = self.get(identifier)
        request = job["request"]
        if job["status"] not in {
            "failed",
            "cancelled",
            "timeout",
            "budget-exceeded",
            "interrupted",
            "unavailable",
        }:
            raise ValueError("job is not eligible for resume")
        if request["dependencies"] != dependencies or request["toolchain"] != toolchain:
            raise ValueError(
                "stale source/material/solver environment; create a new run"
            )
        self.verify_request(identifier)
        for attempt in job["attempts"]:
            if attempt["manifest"]:
                self.verify_attempt(identifier, attempt["number"])
        with self.connect() as con:
            con.execute(
                "UPDATE jobs SET status=?,phase=?,progress=0,error=NULL,updated=?,cancel_requested=0 WHERE id=?",
                ("resuming", "resuming", now(), identifier),
            )
        self.event(
            identifier,
            dict(kind="resume-requested", preserved_attempts=len(job["attempts"])),
        )
        return self.get(identifier)

    def verify_request(self, identifier):
        job = self.get(identifier)
        if load(self.root / "runs" / identifier / "request.json") != job["request"]:
            raise ValueError("changed sealed design request")
        return job

    def verify_attempt(self, identifier, number):
        job = self.verify_request(identifier)
        attempt = next((a for a in job["attempts"] if a["number"] == number), None)
        if not attempt or not attempt["manifest"]:
            raise ValueError("attempt has no sealed evidence")
        manifest = json.loads(attempt["manifest"])
        folder = self.root / "runs" / identifier / f"attempt-{number:04d}"
        if load(folder / "manifest.json") != manifest:
            raise ValueError("changed attempt manifest")
        if manifest["request_sha256"] != fingerprint(job["request"]):
            raise ValueError("attempt belongs to another request")
        for name, expected in manifest["artifacts"].items():
            target = safe(folder, name)
            if target.is_symlink() or digest(target) != expected:
                raise ValueError("corrupt attempt artifact: " + name)
        actual = {
            p.relative_to(folder).as_posix()
            for p in folder.rglob("*")
            if p.is_file() and p != folder / "manifest.json"
        }
        if actual != set(manifest["artifacts"]):
            raise ValueError("missing or extra attempt artifacts")
        return manifest

    def recover(self):
        """Mark dead workers interrupted without confusing reused process IDs."""
        with self.connect() as con:
            rows = [
                dict(r)
                for r in con.execute("SELECT * FROM jobs WHERE status=?", ("running",))
            ]
        for row in rows:
            if process_ownership(row["pid"], row["process_start"]) is False:
                self.finish(
                    row["id"],
                    "interrupted",
                    "worker exited before sealing; attempts retained",
                )


def _process_stat(pid):
    """Return Linux state/start ticks, or raise when procfs is unavailable."""
    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return fields[0], fields[19]


def process_start(pid):
    """Creation identity, with a same-process fallback when procfs is absent.

    The random fallback is only verifiable inside the owning interpreter. A
    different interpreter must treat a live owner with that token as unknown;
    it cannot infer that the PID was reused from an unavailable start time.
    """
    global _LOCAL_PID, _LOCAL_PROCESS_TOKEN
    try:
        pid = int(pid)
        if pid <= 0:
            return None
        state, started = _process_stat(pid)
        return started if state != "Z" else None
    except (OSError, ValueError, TypeError, IndexError):
        if pid == os.getpid():
            with _IDENTITY_LOCK:
                if _LOCAL_PID != os.getpid():
                    # A fork inherits globals but is a new process incarnation.
                    _LOCAL_PID = os.getpid()
                    _LOCAL_PROCESS_TOKEN = "local:" + uuid.uuid4().hex
                return _LOCAL_PROCESS_TOKEN
        return None


def process_ownership(pid, expected):
    """True: matching owner; False: dead/reused; None: identity unverifiable.

    Unknown ownership never authorizes dispatch takeover, recovery, or signals.
    This deliberately prefers retaining a possibly live job to executing it
    twice when the platform cannot expose process creation times.
    """
    try:
        if type(pid) is not int or pid <= 0:
            return False
        actual = process_start(pid)
        if actual is not None and expected is not None:
            if actual == expected:
                return True
            if (
                not str(actual).startswith("local:")
                and not str(expected).startswith("local:")
            ):
                return False
        try:
            state, _ = _process_stat(pid)
            if state == "Z":
                return False
        except (OSError, ValueError, TypeError, IndexError):
            pass
        if os.name != "posix":
            # A zero signal is a presence probe on POSIX. On other platforms
            # os.kill can have different semantics; never signal an unknown PID.
            return None
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (PermissionError, OSError):
        return None
    return None
