"""Exact canonical case/stage records in the Rust Arrow node-table format.

Only active coupled state uses this store. Historical JSON archives have their
own source-bound readers and are never admitted as an active cache entry.
"""
from hashlib import sha256
from functools import lru_cache
import json
import os
from pathlib import Path
import stat
import subprocess

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded

SCHEMA = 'osr-coupled-case-node-store/2'
MAX_CANONICAL_BYTES = 64 * 1024 * 1024
TIMEOUT_SECONDS = 180


def path_for(folder, key):
    return Path(folder) / (key + '.parquet')


def _codec(root=ROOT):
    explicit = os.environ.get('OSR_CASE_NODE_CODEC')
    paths = ([Path(explicit)] if explicit else [Path(root) / 'target' / profile / 'osr-campaign-case-nodes'
              for profile in ('release', 'debug')])
    for path in paths:
        try:
            info = path.stat(follow_symlinks=False)
        except OSError:
            continue
        if stat.S_ISREG(info.st_mode) and info.st_mode & stat.S_IXUSR:
            return path
    raise ValueError('Rust case-node codec unavailable; build osr-campaign-case-nodes with the columnar feature')


@lru_cache(maxsize=8)
def _binary_digest(path, device, inode, size, mtime_ns, ctime_ns):
    digest = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def codec_identity(root=ROOT):
    """Bind an active state to the exact executable bytes."""
    binary = _codec(root)
    info = binary.stat(follow_symlinks=False)
    return {'osr-campaign-case-nodes': _binary_digest(str(binary), info.st_dev, info.st_ino,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)}


def codec_source_identity(root=ROOT):
    """Bind source epochs to the Rust implementation and dependency graph."""
    result = {}
    for name in ('crates/osr-design-search/src/case_nodes.rs',
                 'crates/osr-design-search/src/canonical.rs',
                 'crates/osr-design-search/src/bin/osr-campaign-case-nodes.rs',
                 'crates/osr-design-search/Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml'):
        source = Path(root) / name
        if not source.is_file():
            raise ValueError('Rust case-node codec source unavailable: ' + name)
        result[name] = sha256(source.read_bytes()).hexdigest()
    return result


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate canonical object key')
        result[key] = value
    return result


def _ordinary(path, maximum=None):
    path = Path(path)
    try:
        info = path.stat(follow_symlinks=False)
    except OSError as error:
        raise ValueError('Coupled cached node file unavailable or unsafe') from error
    if stat.S_ISLNK(info.st_mode):
        raise ValueError('Coupled cached node file unavailable or unsafe')
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or (maximum is not None and info.st_size > maximum):
        raise ValueError('Coupled cached node file exceeds the bounded ordinary-file domain')
    return info


def _run(arguments, *, raw=None, root=ROOT):
    command = [str(_codec(root)), *map(str, arguments)]
    result = subprocess.run(command, input=raw, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=TIMEOUT_SECONDS, check=False)
    if result.returncode:
        reason = result.stderr.decode('utf-8', errors='replace').strip()[:1000]
        raise ValueError('Rust case-node codec rejected record: ' + reason)
    return result.stdout


def _envelope(value, kind):
    if kind not in ('case', 'stage'):
        raise ValueError('Unknown coupled node kind')
    payload = encoded(value)
    if len(payload) > MAX_CANONICAL_BYTES:
        raise ValueError('Coupled node exceeds canonical byte domain')
    return dict(schema=SCHEMA, kind=kind, payload_sha256=sha256(payload).hexdigest(), payload=value)


def write(path, value, kind, *, root=ROOT):
    """Publish one fresh node document. An interrupted .pending remains visible."""
    path = Path(path)
    if path.suffix != '.parquet' or path.exists() or path.is_symlink():
        raise ValueError('Fresh .parquet coupled node target required')
    raw = encoded(_envelope(value, kind))
    if len(raw) > MAX_CANONICAL_BYTES:
        raise ValueError('Coupled node envelope exceeds canonical byte domain')
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix('.parquet.pending')
    if pending.exists() or pending.is_symlink():
        if _run(('decode', pending, '-'), root=root) != raw:
            raise ValueError('Interrupted coupled node differs from requested record')
        _publish_pending(path)
        return path
    _run(('encode', '-', path), raw=raw, root=root)
    if _run(('decode', path, '-'), root=root) != raw:
        raise ValueError('Rust case-node readback differs from exact canonical source')
    return path


def _publish_pending(path):
    path = Path(path)
    pending = path.with_suffix('.parquet.pending')
    before = _ordinary(pending)
    if path.exists() or path.is_symlink():
        raise ValueError('Coupled node final path already exists')
    os.link(pending, path, follow_symlinks=False)
    after = path.stat(follow_symlinks=False)
    if (not stat.S_ISREG(after.st_mode) or after.st_nlink != 2 or
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)):
        raise ValueError('Interrupted coupled node changed before publication')
    pending.unlink()
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def recover(path, kind, validate, *, root=ROOT, maximum=MAX_CANONICAL_BYTES):
    """Admit a completed interrupted write only after caller checks identities."""
    path = Path(path)
    pending = path.with_suffix('.parquet.pending')
    if not pending.exists() and not pending.is_symlink():
        return None
    payload = read(pending, kind, root=root, maximum=maximum)
    validate(payload)
    _publish_pending(path)
    return payload


def read(path, kind, *, root=ROOT, maximum=MAX_CANONICAL_BYTES):
    """Decode, check canonical bytes, and preserve nulls and signed-zero values."""
    path = Path(path)
    before = _ordinary(path)
    raw = _run(('decode', path, '-'), root=root)
    if len(raw) > maximum:
        raise ValueError('Coupled cached node file exceeds the bounded ordinary-file domain')
    after = _ordinary(path)
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    if any(getattr(before, field) != getattr(after, field) for field in fields):
        raise ValueError('Coupled cached node changed while reading')
    try:
        envelope = json.loads(raw, object_pairs_hook=_unique_pairs)
    except (ValueError, UnicodeError) as error:
        raise ValueError('Coupled cached node canonical JSON differs') from error
    if encoded(envelope) != raw or not isinstance(envelope, dict) or set(envelope) != {'schema', 'kind', 'payload_sha256', 'payload'}:
        raise ValueError('Coupled cached node canonical envelope differs')
    payload = envelope['payload']
    if (envelope['schema'] != SCHEMA or envelope['kind'] != kind
            or envelope['payload_sha256'] != sha256(encoded(payload)).hexdigest()):
        raise ValueError('Coupled cached node kind or payload digest differs')
    return payload
