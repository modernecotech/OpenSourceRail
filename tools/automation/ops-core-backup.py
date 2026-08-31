#!/usr/bin/env python3
"""Create and verify self-checking Ops Core data/evidence backups."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_backup(database: Path, evidence: Path, output: Path) -> None:
    if not database.is_file():
        raise SystemExit(f"database does not exist: {database}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osr-ops-backup-") as temp_name:
        snapshot = Path(temp_name) / "ops-core.sqlite3"
        with sqlite3.connect(database) as source, sqlite3.connect(snapshot) as target:
            source.backup(target)
        files = [(snapshot, "data/ops-core.sqlite3")]
        if evidence.is_dir():
            files.extend(
                (path, f"data/evidence/{path.relative_to(evidence).as_posix()}")
                for path in sorted(evidence.rglob("*"))
                if path.is_file()
            )
        manifest = {
            "schema_version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "notice": "The server signing key and user store are secrets and are intentionally excluded; back them up in the deployment secret vault.",
            "files": [
                {"path": archive_name, "size_bytes": path.stat().st_size, "sha256": sha256(path)}
                for path, archive_name in files
            ],
        }
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
            for path, archive_name in files:
                archive.write(path, archive_name)
    verify_backup(output)
    print(f"created verified backup {output} ({output.stat().st_size} bytes)")


def verify_backup(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        names = set(archive.namelist())
        for row in manifest.get("files", []):
            name = row["path"]
            if name not in names:
                raise SystemExit(f"backup missing {name}")
            body = archive.read(name)
            if len(body) != int(row["size_bytes"]):
                raise SystemExit(f"backup size mismatch: {name}")
            if hashlib.sha256(body).hexdigest() != row["sha256"]:
                raise SystemExit(f"backup checksum mismatch: {name}")
        if "data/ops-core.sqlite3" not in names:
            raise SystemExit("backup has no SQLite snapshot")
    print(f"verified {path} ({len(manifest['files'])} files)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("output", type=Path)
    create.add_argument("--db", type=Path, default=Path("var/ops-core.sqlite3"))
    create.add_argument("--evidence-dir", type=Path, default=Path("var/ops-evidence"))
    verify = subparsers.add_parser("verify")
    verify.add_argument("backup", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        create_backup(args.db.resolve(), args.evidence_dir.resolve(), args.output.resolve())
    else:
        verify_backup(args.backup.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
