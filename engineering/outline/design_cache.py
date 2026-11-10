"""Persistent source-bound reuse for shared design-price completion."""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import stat
import time

from engineering.design_search.storage import atomic_immutable
from engineering.station_rail.common import encoded, identity

SCHEMA = 'osr-design-pricing-cache-entry/1'
MAX_CACHE_ENTRY_BYTES = 64 * 1024 * 1024
MAX_CACHE_ENTRIES = 8
MAX_CACHE_BYTES = 256 * 1024 * 1024


def _directory(root: Path) -> Path:
    directory = root/'.cache'/'osr-engineering'/'design-completion'
    for parent in (root/'.cache', root/'.cache'/'osr-engineering', directory):
        if parent.is_symlink():
            raise ValueError('Design-price cache paths must not be symlinks')
    directory.mkdir(parents=True, exist_ok=True)
    if any(parent.is_symlink() for parent in (root/'.cache', root/'.cache'/'osr-engineering', directory)):
        raise ValueError('Design-price cache paths changed during initialization')
    return directory


def _key(source_sha256: dict, source_manifest_ids: dict, pricing_policy_id: str) -> str:
    return identity(dict(schema='osr-design-pricing-cache-key/1',
        source_sha256=source_sha256, source_manifest_ids=source_manifest_ids,
        pricing_policy_id=pricing_policy_id))


def _key_lock_path(directory: Path, key: str) -> Path:
    # Sixteen stable lock stripes bound metadata growth across source epochs.
    return directory/(key[0]+'.lock')


def _open_lock(path: Path, *, nonblocking=False):
    if path.is_symlink():
        raise ValueError('Design-price cache lock must not be a symlink')
    flags = (os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0)
        | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_CLOEXEC', 0))
    descriptor = os.open(path, flags, 0o600)
    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        os.close(descriptor)
        raise ValueError('Design-price cache lock must be a singly-linked regular file')
    lock = os.fdopen(descriptor, 'r+b')
    try:
        mode = fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0)
        fcntl.flock(lock.fileno(), mode)
    except Exception:
        lock.close()
        raise
    return lock


def _prune(directory: Path, keep_key: str) -> dict:
    """Keep this derived cache within a small budget; skip entries in use."""
    with _open_lock(directory/'.prune.lock'):
        return _prune_locked(directory, keep_key)


def _prune_locked(directory: Path, keep_key: str) -> dict:
    entries = []
    for path in directory.glob('*.json'):
        if len(path.stem) != 64 or any(c not in '0123456789abcdef' for c in path.stem):
            continue
        if path.is_symlink():
            raise ValueError('Design-price cache entry must not be a symlink')
        info = path.stat(follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('Design-price cache entry must be a singly-linked regular file')
        entries.append((info.st_mtime_ns, path.stem, path, info.st_size))
    entries.sort()
    total_bytes = sum(row[3] for row in entries)
    evicted = 0
    deferred = 0
    for _, key, path, size in entries:
        if len(entries)-evicted <= MAX_CACHE_ENTRIES and total_bytes <= MAX_CACHE_BYTES:
            break
        if key == keep_key:
            continue
        lock_path = _key_lock_path(directory, key)
        try:
            lock = _open_lock(lock_path, nonblocking=True)
        except BlockingIOError:
            deferred += 1
            continue
        try:
            if path.is_symlink():
                raise ValueError('Design-price cache entry changed to a symlink')
            if path.exists():
                current = path.stat(follow_symlinks=False)
                if not stat.S_ISREG(current.st_mode) or current.st_nlink != 1:
                    raise ValueError('Design-price cache entry must be a singly-linked regular file')
                path.unlink()
                evicted += 1
                total_bytes -= current.st_size
        finally:
            lock.close()
    return dict(cache_entries=len(entries)-evicted, cache_total_bytes=total_bytes,
        evicted_entries=evicted, prune_deferred_entries=deferred)


def _read(path: Path, key: str, root: Path, source_sha256: dict,
          source_manifest_ids: dict, pricing_policy_id: str, design_completion):
    flags = (os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
        | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_CLOEXEC', 0))
    descriptor = os.open(path, flags)
    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        os.close(descriptor)
        raise ValueError('Design-price cache entry must be a singly-linked regular file')
    if info.st_size > MAX_CACHE_ENTRY_BYTES:
        os.close(descriptor)
        raise ValueError('Design-price cache entry exceeds the bounded size')
    with os.fdopen(descriptor, 'rb') as handle:
        raw = handle.read(MAX_CACHE_ENTRY_BYTES+1)
    if len(raw) > MAX_CACHE_ENTRY_BYTES:
        raise ValueError('Design-price cache entry exceeds the bounded size')
    entry = json.loads(raw)
    if encoded(entry) != raw:
        raise ValueError('Design-price cache bytes are not canonical')
    entry_id = entry.get('entry_id')
    if (entry.get('schema') != SCHEMA or entry.get('cache_key') != key
            or entry_id != identity({k:v for k,v in entry.items() if k!='entry_id'})):
        raise ValueError('Design-price cache identity differs')
    value = entry.get('result')
    if (not isinstance(value, dict)
            or value.get('source_sha256') != source_sha256
            or value.get('source_manifest_ids') != source_manifest_ids
            or value.get('pricing_policy', {}).get('policy_id') != pricing_policy_id):
        raise ValueError('Design-price cache belongs to another source or policy epoch')
    design_completion.validate(value, root=root)
    return value, len(raw)


def evaluate_cached(root, *, design_completion_module=None):
    """Evaluate once per exact source and policy identity; validate every hit."""
    if design_completion_module is None:
        from . import design_completion as design_completion_module
    root = Path(root).resolve()
    started = time.perf_counter()
    pricing = design_completion_module.policy(root)
    source_sha256, source_manifest_ids = design_completion_module._source_inputs(root)
    pricing_policy_id = pricing['policy_id']
    key = _key(source_sha256, source_manifest_ids, pricing_policy_id)
    directory = _directory(root)
    path = directory/(key+'.json')
    lock_path = _key_lock_path(directory, key)
    if path.is_symlink():
        raise ValueError('Design-price cache paths must not be symlinks')
    with _open_lock(lock_path) as lock:
        lookup_elapsed_s = time.perf_counter()-started
        if path.exists():
            value, size = _read(path, key, root, source_sha256,
                source_manifest_ids, pricing_policy_id, design_completion_module)
            retention = _prune(directory, key)
            elapsed_s = time.perf_counter()-started
            return value, dict(elapsed_s=elapsed_s, cache_lookup_elapsed_s=lookup_elapsed_s,
                design_evaluation_elapsed_s=0.0, design_evaluation_performed=False,
                cache_hit=True, cache_key=key, cache_bytes=size, native_solver_jobs=0,
                CAD_jobs=0, streamed_railway_records=value['counts']['railway-bundle'],
                **retention)

        value, timing = design_completion_module.evaluate(root=root, policy=pricing)
        design_completion_module.validate(value, root=root)
        if (value.get('source_sha256') != source_sha256
                or value.get('source_manifest_ids') != source_manifest_ids
                or value.get('pricing_policy', {}).get('policy_id') != pricing_policy_id):
            raise ValueError('Design-price source or policy epoch changed during evaluation')
        entry = dict(schema=SCHEMA, cache_key=key, result=value)
        entry['entry_id'] = identity(entry)
        raw = encoded(entry)
        if len(raw) > MAX_CACHE_ENTRY_BYTES:
            raise ValueError('Design-price cache result exceeds the bounded size')
        atomic_immutable(path, raw)
        retention = _prune(directory, key)
        elapsed_s = time.perf_counter()-started
        return value, dict(elapsed_s=elapsed_s,
            cache_lookup_elapsed_s=lookup_elapsed_s,
            design_evaluation_elapsed_s=timing['elapsed_s'],
            design_evaluation_performed=True, cache_hit=False, cache_key=key,
            cache_bytes=len(raw), native_solver_jobs=timing.get('native_solver_jobs', 0),
            CAD_jobs=timing.get('CAD_jobs', 0),
            streamed_railway_records=timing.get('streamed_railway_records', 0),
            **retention)
