#!/usr/bin/env python3
"""Create and verify self-checking Ops Core data/evidence backups."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import re
import shutil
import stat
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


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
        if any(path.is_symlink() for path, _ in files):
            raise SystemExit('evidence symlinks must not be included in backups')
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


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate manifest key: {key}')
        result[key] = value
    return result


def _archive_path(name):
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError('invalid archive path')
    path = PurePosixPath(name)
    if path.is_absolute() or str(path) != name or any(p in ('.', '..') for p in path.parts):
        raise ValueError('unsafe archive path')
    if name != 'data/ops-core.sqlite3' and not name.startswith('data/evidence/'):
        raise ValueError('unexpected archive path')
    return path


def _verify_into(path, destination):
    """Verify exact membership and stream validated payloads to a private staging area."""
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)):
            raise ValueError('duplicate archive entry')
        if 'manifest.json' not in names or archive.getinfo('manifest.json').file_size > 4_000_000:
            raise ValueError('missing or oversized manifest')
        if any(entry.is_dir() or stat.S_IFMT(entry.external_attr >> 16) not in (0, stat.S_IFREG) for entry in entries):
            raise ValueError('archive must contain only regular payload files')
        manifest = json.loads(archive.read('manifest.json'), object_pairs_hook=_unique_object)
        if not isinstance(manifest, dict) or manifest.get('schema_version') != '1.0':
            raise ValueError('unsupported manifest schema')
        created = datetime.fromisoformat(manifest.get('created_at', ''))
        if created.tzinfo is None:
            raise ValueError('manifest creation time requires timezone')
        rows = manifest.get('files')
        if not isinstance(rows, list) or not rows:
            raise ValueError('manifest requires checksummed payload files')
        declared = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != {'path', 'size_bytes', 'sha256'}:
                raise ValueError('invalid manifest file entry')
            name = row['path']; _archive_path(name)
            if name in declared:
                raise ValueError('duplicate manifest file entry')
            declared.add(name)
            if type(row['size_bytes']) is not int or row['size_bytes'] < 0:
                raise ValueError('invalid manifest file size')
            if not isinstance(row['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', row['sha256']):
                raise ValueError('invalid manifest checksum')
        if 'data/ops-core.sqlite3' not in declared:
            raise ValueError('SQLite snapshot must appear in checksummed manifest')
        if set(names) != declared | {'manifest.json'}:
            raise ValueError('archive membership differs from manifest')
        for row in rows:
            name = row['path']
            if archive.getinfo(name).file_size != row['size_bytes']:
                raise ValueError(f'backup size mismatch: {name}')
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            checksum = hashlib.sha256(); size = 0
            with archive.open(name) as source, target.open('xb') as output:
                while block := source.read(1024 * 1024):
                    size += len(block); checksum.update(block); output.write(block)
            if size != row['size_bytes'] or checksum.hexdigest() != row['sha256']:
                raise ValueError(f'backup checksum mismatch: {name}')
        database = destination / 'data/ops-core.sqlite3'
        with database.open('rb') as handle:
            if handle.read(16) != b'SQLite format 3\x00':
                raise ValueError('invalid SQLite database header')
        with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as db:
            if db.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                raise ValueError('SQLite integrity check failed')
            if db.execute('PRAGMA foreign_key_check').fetchone() is not None:
                raise ValueError('SQLite foreign-key check failed')
            # Evidence path reconstruction follows the application's content-addressed layout.
            # Never trust an archived absolute stored_path as a destination.
            tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if 'evidence_files' in tables:
                for city, digest, filename, size in db.execute('SELECT city_slug,sha256,file_name,size_bytes FROM evidence_files'):
                    if not re.fullmatch('[a-z0-9-]+', city) or not re.fullmatch('[0-9a-f]{64}', digest):
                        raise ValueError('invalid application evidence identity')
                    name = f'data/evidence/{city}/{digest[:2]}/{digest}-{filename}'
                    _archive_path(name)
                    target = destination / name
                    if name not in declared or target.stat().st_size != size or sha256(target) != digest:
                        raise ValueError('missing or changed application evidence file')
                for table in ('inspections', 'approvals'):
                    if table not in tables:
                        continue
                    for city, reference in db.execute(f'SELECT city_slug,evidence_ref FROM {table} WHERE evidence_ref IS NOT NULL'):
                        if not reference.startswith('/api/ops-core/'):
                            continue  # External/document references are not locally uploaded files.
                        match = re.fullmatch(r'/api/ops-core/([a-z0-9-]+)/evidence/([0-9a-f]{64})', reference)
                        if not match or match[1] != city or not db.execute(
                                'SELECT 1 FROM evidence_files WHERE city_slug=? AND sha256=?', (city, match[2])).fetchone():
                            raise ValueError('dangling or cross-city application evidence reference')
        return manifest


def verify_backup(path: Path) -> None:
    try:
        with tempfile.TemporaryDirectory(prefix='osr-ops-verify-') as directory:
            manifest = _verify_into(path, Path(directory))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error, zipfile.BadZipFile) as exc:
        raise SystemExit(f'backup verification failed: {exc}') from exc
    print(f"verified {path} ({len(manifest['files'])} files; SQLite integrity checked)")


def restore_backup(path: Path, output: Path) -> None:
    """Restore into a new offline directory; existing deployments are never overwritten."""
    output = output.resolve()
    if output.exists():
        raise SystemExit('restore destination must not exist')
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='osr-ops-restore-', dir=output.parent) as directory:
            stage = Path(directory)
            manifest = _verify_into(path, stage)
            database = stage / 'data/ops-core.sqlite3'
            with sqlite3.connect(database) as db:
                tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if not {'city_state', 'work_orders', 'inspections', 'approvals', 'evidence_files'} <= tables:
                    raise ValueError('snapshot is not an initialized Ops Core application database')
                for city, digest, filename in db.execute('SELECT city_slug,sha256,file_name FROM evidence_files').fetchall():
                    target = output / 'data/evidence' / city / digest[:2] / f'{digest}-{filename}'
                    db.execute('UPDATE evidence_files SET stored_path=? WHERE city_slug=? AND sha256=?', (str(target), city, digest))
            # Exclusive creation avoids replacing another restore or a live deployment.
            output.mkdir()
            try:
                shutil.move(str(stage / 'data'), str(output / 'data'))
                (output / 'restore.json').write_text(json.dumps(dict(schema='osr-ops-restore/1',
                    source_sha256=sha256(path), source_manifest=manifest,
                    evidence_paths_rebased=True, independently_accepted=False,
                    notice='Offline Ops Core restore only. Provision user store and signing key from the secret vault; reconcile other services separately.'), indent=2) + '\n')
            except Exception:
                shutil.rmtree(output)
                raise
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error, zipfile.BadZipFile) as exc:
        raise SystemExit(f'backup restore failed: {exc}') from exc
    print(f'restored verified Ops Core data to {output}')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("output", type=Path)
    create.add_argument("--db", type=Path, default=Path("var/ops-core.sqlite3"))
    create.add_argument("--evidence-dir", type=Path, default=Path("var/ops-evidence"))
    verify = subparsers.add_parser("verify")
    verify.add_argument("backup", type=Path)
    restore = subparsers.add_parser('restore')
    restore.add_argument('backup', type=Path)
    restore.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.command == "create":
        create_backup(args.db.resolve(), args.evidence_dir.resolve(), args.output.resolve())
    elif args.command == 'verify':
        verify_backup(args.backup.resolve())
    else:
        restore_backup(args.backup.resolve(), args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
