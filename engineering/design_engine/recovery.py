"""Consistent private experiment/record checkpoints and fresh-target restoration."""

from __future__ import annotations
import json
from pathlib import Path
import shutil
import sqlite3

from .contracts import canonical
from .publication import digest, safe
from .store import Store


def checkpoint(store, destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("checkpoint output must be fresh")
    with store.connect() as con:
        con.execute("BEGIN IMMEDIATE")
        if con.execute(
            "SELECT count(*) FROM jobs WHERE status IN ('queued','running','resuming','cancelling')"
        ).fetchone()[0]:
            raise ValueError("checkpoint requires quiescent design jobs")
        destination.mkdir(parents=True, mode=0o700)
        # Use a separate read connection for SQLite backup; do not copy a WAL
        # database file while transactions can still be represented in the WAL.
        source = sqlite3.connect(store.database)
        target = sqlite3.connect(destination / "index.sqlite3")
        try:
            source.backup(target)
        finally:
            source.close()
            target.close()
        for name in (
            "runs",
            "exports",
            "downloads",
            "planning-drafts",
            "input-revisions",
        ):
            if (store.root / name).is_dir():
                shutil.copytree(store.root / name, destination / name)
    manifest = dict(
        schema="osr-design-checkpoint/1",
        files={
            p.relative_to(destination).as_posix(): digest(p)
            for p in sorted(destination.rglob("*"))
            if p.is_file()
        },
        database_integrity="checked on restore",
        private_data=True,
        physical_release=False,
    )
    (destination / "checkpoint.json").write_bytes(canonical(manifest) + b"\n")
    return manifest


def restore(checkpoint, destination):
    checkpoint = Path(checkpoint).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError(
            "restore only into a fresh target; existing records cannot be overwritten"
        )
    manifest = json.loads((checkpoint / "checkpoint.json").read_text())
    if (
        manifest.get("schema") != "osr-design-checkpoint/1"
        or manifest.get("physical_release") is not False
    ):
        raise ValueError("invalid design checkpoint")
    for name, expected in manifest["files"].items():
        path = safe(checkpoint, name)
        if path.is_symlink() or digest(path) != expected:
            raise ValueError("corrupt checkpoint payload")
    actual = {
        p.relative_to(checkpoint).as_posix()
        for p in checkpoint.rglob("*")
        if p.is_file() and p.name != "checkpoint.json"
    }
    if actual != set(manifest["files"]):
        raise ValueError("checkpoint file membership changed")
    shutil.copytree(checkpoint, destination)
    (destination / "checkpoint.json").unlink()
    store = Store(destination)
    with store.connect() as con:
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("restored design index failed integrity")
        ids = [r[0] for r in con.execute("SELECT id FROM jobs")]
        con.execute("DELETE FROM dispatches")
    for identifier in ids:
        job = store.verify_request(identifier)
        for attempt in job["attempts"]:
            if attempt["manifest"]:
                store.verify_attempt(identifier, attempt["number"])
        if job["request"].get("reviewed_inputs"):
            from .input_revisions import InputRevisions

            InputRevisions(store).validate_job(job["request"])
    return dict(
        schema="osr-design-restoration/1",
        restored_jobs=len(ids),
        all_sealed_artifacts_verified=True,
        target_fresh=True,
        active_jobs_started=False,
        physical_release=False,
    )
