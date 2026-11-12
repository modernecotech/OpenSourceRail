"""Retain authenticated historical ledger inputs without relabelling execution.

Dry-run by default. This migration does not run engineering or change any gate.
The original ledger and authenticated source bytes remain content-addressed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

from .release_gate import STATUS

ARCHIVE = 'docs/archives/v06-closure-source-context'
MAX_FILE = 64 * 1024 * 1024
MAX_ROWS = 4096


def _path(value: str) -> str:
    if (not isinstance(value, str) or not value or '\\' in value
            or PurePosixPath(value).is_absolute() or '..' in PurePosixPath(value).parts
            or PurePosixPath(value).as_posix() != value):
        raise ValueError('unsafe retained source path')
    return value


def _git(root: Path, revision: str, path: str) -> bytes:
    spec = f'{revision}:{_path(path)}'
    environment = dict(os.environ, GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1')
    size = int(subprocess.check_output(['git', '-C', str(root), 'cat-file', '-s', spec], env=environment))
    if size > MAX_FILE:
        raise ValueError('ledger artifact exceeds retention file bound')
    return subprocess.check_output(['git', '-C', str(root), 'show', spec], env=environment)


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def _ordinary_bytes(root: Path, path: Path) -> bytes:
    if (not path.is_relative_to(root) or path == root
            or any(p.is_symlink() for p in (path, *path.parents) if p != root)):
        raise ValueError('ordinary in-tree status/evidence required')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE:
            raise ValueError('ordinary bounded status/evidence required')
        raw = stream.read(MAX_FILE + 1)
    if len(raw) > MAX_FILE:
        raise ValueError('status/evidence exceeds retention file bound')
    return raw


def retain(root: str | Path, source_revision: str, *, status_path: str = STATUS,
           write: bool = False) -> dict:
    root = Path(root).resolve()
    if not re.fullmatch(r'[0-9a-f]{40}', source_revision):
        raise ValueError('full immutable source revision required')
    status_file = root / _path(status_path)
    original = _ordinary_bytes(root, status_file)
    status_mode = stat.S_IMODE(status_file.stat(follow_symlinks=False).st_mode)
    status = json.loads(original)
    if status.get('source_retention'):
        # Idempotence must still verify retained bytes and identity metadata.
        from .release_gate import _retained_context
        _retained_context(root, status)
        manifest = json.loads((root / status['source_retention']['path']).read_text())
        if manifest['source_revision'] != source_revision:
            raise ValueError('existing retention uses a different source revision')
        return {'changed': False, 'retained': [], 'already_retained': True}
    proposed = copy.deepcopy(status)
    rows = [(gate, index, item) for gate, record in status['gates'].items()
            for index, item in enumerate(record['evidence'])]
    if len(rows) > MAX_ROWS:
        raise ValueError('too many ledger evidence rows')
    inventory = []
    payloads = {}
    retained = []
    # Authenticate every mismatch before creating any files. Current ordinary
    # worktree bytes take precedence over HEAD so local changes are not ignored.
    for gate, index, row in rows:
        path = _path(row['path'])
        current_file = root / path
        if current_file.exists() or current_file.is_symlink():
            if (current_file.is_symlink() or not current_file.is_file()
                    or not current_file.resolve().is_relative_to(root)
                    or any(p.is_symlink() for p in current_file.parents if p != root)):
                raise ValueError('ordinary in-tree evidence required')
            if current_file.stat().st_size > MAX_FILE:
                raise ValueError('ledger artifact exceeds retention file bound')
            current = _ordinary_bytes(root, current_file)
        else:
            current = _git(root, 'HEAD', path)
        observed = _hash(current)
        inventory.append({'gate': gate, 'path': path, 'expected_sha256': row['sha256'],
                          'current_sha256': observed, 'current_bytes': len(current)})
        if observed == row['sha256']:
            continue
        historical = _git(root, source_revision, path)
        if _hash(historical) != row['sha256']:
            raise ValueError(f'original evidence hash not authenticated: {path}')
        destination = f'{ARCHIVE}/source/{path}.source'
        payloads[destination] = historical
        if sum(map(len, payloads.values())) > 16 * 1024 * 1024:
            raise ValueError('retained source aggregate exceeds 16 MiB migration bound')
        new_row = proposed['gates'][gate]['evidence'][index]
        new_row.update(path=destination, original_path=path, source_revision=source_revision)
        retained.append({'gate': gate, 'original_path': path, 'path': destination,
                         'source_revision': source_revision, 'sha256': row['sha256'],
                         'bytes': len(historical)})
    if not retained:
        return {'changed': False, 'retained': [], 'inventory': inventory}
    original_path = f'{ARCHIVE}/status-before-retention.json'
    manifest_path = f'{ARCHIVE}/manifest.json'
    manifest = {'schema': 'osr-v06-retained-closure-source-context/1',
                'source_revision': source_revision,
                'scope': 'Historical implementation context only; no new execution or gate closure.',
                'original_ledger': {'path': original_path, 'sha256': _hash(original)},
                'inventory': inventory, 'retained_sources': retained}
    payloads[original_path] = original
    manifest_raw = _json(manifest)
    payloads[manifest_path] = manifest_raw
    proposed['source_retention'] = {'path': manifest_path, 'sha256': _hash(manifest_raw)}
    # Refuse symlink traversal and nonidentical existing archives before writes.
    for path, raw in payloads.items():
        destination = root / path
        if any(p.is_symlink() for p in [destination, *destination.parents] if p != root):
            raise ValueError('symlink in archive destination')
        if destination.exists() and destination.read_bytes() != raw:
            raise ValueError(f'immutable archive differs: {path}')
    if write:
        if _ordinary_bytes(root, status_file) != original:
            raise ValueError('status changed during source retention')
        for path, raw in payloads.items():
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        # Replacing a same-directory temporary file never follows a final
        # status-file symlink. Recheck ordinary parents and concurrent edits.
        if _ordinary_bytes(root, status_file) != original:
            raise ValueError('status changed during source retention')
        import tempfile
        descriptor, temporary = tempfile.mkstemp(prefix='.retained-status-', dir=status_file.parent)
        try:
            os.fchmod(descriptor, status_mode)
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(_json(proposed))
            os.replace(temporary, status_file)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return {'changed': True, 'written': write, 'retained': retained, 'inventory': inventory}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--source-revision', required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = retain(args.root, args.source_revision, write=args.write)
    print(json.dumps({key: value for key, value in result.items() if key != 'inventory'}, indent=2))


if __name__ == '__main__':
    main()
