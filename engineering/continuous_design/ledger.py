"""Transactional completion with a durable, idempotent follow-up outbox."""
from contextlib import contextmanager
import itertools
import json
from pathlib import Path
import time

from engineering.twin_workflow import core

_serial = itertools.count()


@contextmanager
def transaction(db):
    # SAVEPOINT composes with both an outer transaction and other ledger calls.
    name = "osr_" + str(next(_serial))
    db.execute("SAVEPOINT " + name)
    try:
        yield
    except BaseException:
        db.execute("ROLLBACK TO " + name)
        db.execute("RELEASE " + name)
        raise
    else:
        db.execute("RELEASE " + name)


def initialise(store):
    store.db.executescript("""
        CREATE TABLE IF NOT EXISTS outbox (
            origin TEXT PRIMARY KEY, baseline TEXT NOT NULL, lane TEXT NOT NULL,
            payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending',
            created REAL NOT NULL, delivered REAL, error TEXT);
    """)
    if "outboxed" not in {r[1] for r in store.db.execute("PRAGMA table_info(jobs)")}:
        store.db.execute("ALTER TABLE jobs ADD COLUMN outboxed INTEGER NOT NULL DEFAULT 0")
    store.db.commit()


def add(store, origin, baseline, lane, payload):
    store.db.execute("INSERT OR IGNORE INTO outbox(origin,baseline,lane,payload,created) VALUES(?,?,?,?,?)",
        (origin, baseline, lane, json.dumps(payload, sort_keys=True, allow_nan=False), time.time()))


def complete_job(store, key, receipt_sha, result, *, now=None):
    row = store.db.execute("SELECT * FROM jobs WHERE key=?", (key,)).fetchone()
    if row is None:
        raise ValueError("unknown completion")
    actions = dict(tasks=result.get("repairs", []), needs=result.get("needs", []), job=key)
    with transaction(store.db):
        store.db.execute("UPDATE jobs SET status='completed',receipt_sha=?,finished=?,error=NULL,outboxed=1 WHERE key=?",
            (receipt_sha, time.time() if now is None else now, key))
        add(store, "job:" + key, row["baseline"], row["lane"], actions)


def complete_provider(store, provider_id, values, needs, response_sha):
    row = store.db.execute("SELECT * FROM provider WHERE id=?", (provider_id,)).fetchone()
    if row is None:
        raise ValueError("unknown proposer completion")
    with transaction(store.db):
        store.db.execute("UPDATE provider SET status='import-pending',error=NULL WHERE id=?", (provider_id,))
        add(store, "provider:" + str(provider_id), row["baseline"], row["lane"],
            dict(tasks=values, needs=needs, provider_id=provider_id, response_sha256=response_sha))


def backfill(store):
    # Once-only migration also repairs the old completion/dispatch crash window.
    rows = list(store.db.execute("SELECT * FROM jobs WHERE status='completed' AND outboxed=0"))
    for row in rows:
        result = store.result(row)
        with transaction(store.db):
            add(store, "job:" + row["key"], row["baseline"], row["lane"],
                dict(tasks=result.get("repairs", []), needs=result.get("needs", []), job=row["key"]))
            store.db.execute("UPDATE jobs SET outboxed=1 WHERE key=?", (row["key"],))


def recover_outputs(store):
    for row in list(store.db.execute("SELECT * FROM jobs WHERE status='running' AND folder IS NOT NULL")):
        path=Path(row["folder"])/"receipt.json"
        if not path.is_file():continue
        try:
            receipt=core.read(path,maximum=10_000_000)
            if receipt.get("key")!=row["key"] or receipt.get("baseline_sha256")!=row["baseline"]:
                continue
            candidate=dict(row);candidate["receipt_sha"]=core.sha(path)
            result=store.result(candidate)
            if type(result.get("study_pass")) is not bool or any(result.get(k) is not False for k in core.FLAGS):
                continue
            complete_job(store,row["key"],candidate["receipt_sha"],result)
        except (ValueError,OSError,KeyError,TypeError):
            continue
    from .service import validated_proposals
    for row in list(store.db.execute("SELECT * FROM provider WHERE status IN ('running','interrupted')")):
        path=Path(row["folder"])/"response.json"
        if not path.is_file():continue
        try:
            values,needs=validated_proposals(store,row["baseline"],row["lane"],core.read(path))
            complete_provider(store,row["id"],values,needs,core.sha(path))
        except (ValueError,OSError,KeyError,TypeError):
            continue


def dispatch(store, *, limit=64):
    delivered = 0
    active=core.read(store.workspace/"active.json")["baseline_sha256"] if (store.workspace/"active.json").exists() else ""
    for row in list(store.db.execute("SELECT * FROM outbox WHERE state='pending' ORDER BY (baseline=?) DESC,created LIMIT ?", (active,limit))):
        payload = json.loads(row["payload"])
        try:
            with transaction(store.db):
                from . import research
                if "job" in payload:
                    research.observe(store, payload["job"])
                added = sum(store.enqueue(value, row["baseline"],priority=research.priority(store,value)) for value in payload["tasks"])
                store.record_needs(row["baseline"], row["lane"], payload["needs"])
                if "provider_id" in payload:
                    store.db.execute("UPDATE provider SET status=?,finished=?,error=NULL WHERE id=?",
                        ("added" if added else "no-progress", time.time(), payload["provider_id"]))
                store.db.execute("UPDATE outbox SET state='delivered',delivered=?,error=NULL WHERE origin=?",
                    (time.time(), row["origin"]))
            delivered += 1
        except (ValueError, OSError, TypeError, KeyError) as error:
            # The actions and parent remain durable and visible for repair.
            with transaction(store.db):
                store.db.execute("UPDATE outbox SET state='blocked',error=? WHERE origin=?", (str(error), row["origin"]))
    return delivered
