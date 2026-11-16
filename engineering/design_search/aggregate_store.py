"""Source-bound v2 aggregate assembled from one Arrow core and ordered case shards.

A full coupled result duplicates its case records. This store keeps the canonical
result with rows=[] in core.parquet and ordered case references in rows.parquet.
The existing case_node_store owns each typed Arrow case document. Reconstruction
streams exact canonical bytes, validates the original aggregate SHA and recomputes
run_id without loading or writing the 721 MB result as one object.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded
from . import canonical_stream, case_node_store

SCHEMA = 'osr-coupled-aggregate-store/2'
MAX_CORE_BYTES = 64 * 1024 * 1024
MAX_AGGREGATE_BYTES = 1024 * 1024 * 1024
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_ROWS = 128
ID = re.compile(r'[0-9a-f]{64}\Z')
ROW_ID = re.compile(rb'"row_id":"([0-9a-f]{64})"')


def _ordinary(path, maximum=None):
    path = Path(path)
    info = path.stat(follow_symlinks=False)
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
            or (maximum is not None and info.st_size > maximum)):
        raise ValueError('Aggregate source or shard is not a bounded ordinary single-link file')
    return info


def _hash_file(path):
    digest = sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _loads(raw):
    value = json.loads(raw, object_pairs_hook=case_node_store._unique_pairs)
    if encoded(value) != raw:
        raise ValueError('Aggregate component differs from Python canonical bytes')
    return value


def _core_offset(core):
    marker = b'"rows":[]'
    if core.count(marker) != 1:
        raise ValueError('Exactly one empty canonical rows field required')
    offset = core.index(marker) + len(b'"rows":')
    if core[offset:offset + 2] != b'[]':
        raise ValueError('Canonical rows placeholder differs')
    return offset


def _core_value(core):
    value = _loads(core)
    if not isinstance(value, dict) or value.get('rows') != []:
        raise ValueError('Aggregate core must have an empty top-level rows array')
    for key in ('contract_id', 'campaign_id', 'run_id'):
        if not isinstance(value.get(key), str) or not ID.fullmatch(value[key]):
            raise ValueError('Aggregate identity field differs')
    if not isinstance(value.get('source_sha256'), dict):
        raise ValueError('Aggregate source epochs differ')
    return value


def _source_rows(source, cases_source):
    """Yield exact aggregate rows from the original canonical file, bounded per row."""
    source = Path(source)
    _ordinary(source, MAX_AGGREGATE_BYTES)
    cases_source = Path(cases_source)
    if cases_source.is_symlink() or not cases_source.is_dir():
        raise ValueError('Ordinary source case directory required')
    paths = sorted(cases_source.glob('*.json'))
    if not paths or len(paths) > MAX_ROWS:
        raise ValueError('Source case count exceeds aggregate bound')
    candidates = []
    for path in paths:
        info = _ordinary(path, case_node_store.MAX_CANONICAL_BYTES)
        if not ID.fullmatch(path.stem):
            raise ValueError('Source case identity filename differs')
        with path.open('rb') as stream:
            prefix = stream.read(min(64, info.st_size - 1))
        candidates.append((path, prefix, info.st_size))

    def same_span(file, start, path, length):
        file.seek(start)
        digest = sha256()
        remaining = length - 1
        with path.open('rb') as case:
            while remaining:
                chunk = case.read(min(1024 * 1024, remaining))
                if not chunk or file.read(len(chunk)) != chunk:
                    return None
                digest.update(chunk)
                remaining -= len(chunk)
            if case.read(1) != b'\n' or case.read(1):
                return None
        digest.update(b'\n')
        return digest.hexdigest()

    with source.open('rb') as file:
        marker = b',"rows":['
        prefix = bytearray()
        start = -1
        while len(prefix) < MAX_CORE_BYTES:
            block = file.read(min(1024 * 1024, MAX_CORE_BYTES - len(prefix)))
            if not block:
                break
            prefix.extend(block)
            start = prefix.find(marker)
            if start >= 0:
                break
        if start < 0:
            raise ValueError('Exactly one aggregate rows field required')
        content_start = start + len(marker)
        file.seek(content_start)
        rows = []
        while file.read(1) != b']':
            pos = file.tell() - 1
            file.seek(pos)
            probe = file.read(64)
            matches = []
            for path, candidate_prefix, length in candidates:
                if probe[:len(candidate_prefix)] != candidate_prefix:
                    continue
                digest = same_span(file, pos, path, length)
                if digest is not None:
                    matches.append((path, length, digest))
            if len(matches) != 1:
                raise ValueError('Aggregate row does not match exactly one source case')
            path, length, digest = matches[0]
            rows.append((path.stem, path, length, digest))
            if len(rows) > MAX_ROWS:
                raise ValueError('Aggregate row count exceeds bound')
            file.seek(pos + length - 1)
            separator = file.read(1)
            if separator != b',' and separator != b']':
                raise ValueError('Aggregate row separator differs')
            if separator == b']':
                break
        if len(rows) != len(paths):
            raise ValueError('Aggregate rows or source case inventory differ')
        suffix = file.read()
        core = bytes(prefix[:content_start]) + b']' + suffix
        if len(core) > MAX_CORE_BYTES:
            raise ValueError('Aggregate core exceeds one Arrow document')
    yield core
    for context, path, length, digest in rows:
        raw = path.read_bytes()
        if len(raw) != length or sha256(raw).hexdigest() != digest:
            raise ValueError('Source case changed after aggregate row matching')
        yield context, raw


class _Composer:
    def __init__(self, core, sink=None):
        self.core = core
        self.value = _core_value(core)
        self.offset = _core_offset(core)
        self.sink = sink
        self.full = sha256()
        self.no_run = sha256()
        self.bytes = 0
        self.rows = 0
        self._emit(core[:self.offset + 1])

    def _emit(self, data, *, no_run=True):
        if self.sink is not None:
            remaining = memoryview(data)
            while remaining:
                count = self.sink.write(remaining)
                if type(count) is not int or not 0 < count <= len(remaining):
                    raise OSError('Aggregate stream sink made no progress')
                remaining = remaining[count:]
        self.full.update(data)
        if no_run:
            self.no_run.update(data)
        self.bytes += len(data)
        if self.bytes > MAX_AGGREGATE_BYTES:
            raise ValueError('Aggregate reconstruction exceeds 1 GiB bound')

    def row(self, raw):
        if not raw.endswith(b'\n') or self.rows >= MAX_ROWS:
            raise ValueError('Bounded canonical case row required')
        if self.rows:
            self._emit(b',')
        self._emit(raw[:-1])
        self.rows += 1

    def finish(self):
        tail = self.core[self.offset + 1:]
        marker = b',"run_id":"' + self.value['run_id'].encode('ascii') + b'"'
        if tail.count(marker) != 1:
            raise ValueError('Root run_id field differs or is not after rows')
        before, after = tail.split(marker, 1)
        self._emit(before)
        self._emit(marker, no_run=False)
        self._emit(after)
        full = self.full.hexdigest()
        run_id = self.no_run.hexdigest()
        if run_id != self.value['run_id']:
            raise ValueError('Aggregate run_id differs from canonical stream')
        return dict(aggregate_sha256=full, aggregate_bytes=self.bytes,
                    run_id=run_id, row_count=self.rows)


def _case_bytes(cases_folder, context, *, root):
    if not ID.fullmatch(context):
        raise ValueError('Case context identity differs')
    path = case_node_store.path_for(cases_folder, context)
    _ordinary(path, 16 * 1024 * 1024)
    row = case_node_store.read(path, 'case', root=root)
    if not isinstance(row, dict) or row.get('case_context_id') != context:
        raise ValueError('Case shard belongs to another context')
    raw = encoded(row)
    if len(raw) > case_node_store.MAX_CANONICAL_BYTES:
        raise ValueError('Case shard exceeds canonical bound')
    return path, row, raw


def _ref(context, raw, row, path, ordinal):
    if not ID.fullmatch(row.get('row_id', '')):
        raise ValueError('Case row identity differs')
    return dict(ordinal=ordinal, case_context_id=context, row_id=row['row_id'],
                case_sha256=sha256(raw).hexdigest(), case_bytes=len(raw),
                parquet_name=path.name, parquet_sha256=_hash_file(path))


def _write_component(stage, name, raw, *, root):
    path = stage / name
    case_node_store._run(('encode', '-', path), raw=raw, root=root)
    if case_node_store._run(('decode', path, '-'), root=root) != raw:
        raise ValueError('Arrow aggregate component round-trip differs')
    _ordinary(path, 16 * 1024 * 1024)
    return _hash_file(path)


def write(folder, result_or_source, cases_folder, *, root=ROOT, cases_source=None):
    """Atomically publish a fresh aggregate store from a dict or canonical JSON.

    The Path form is solely for source-bound migration and needs cases_source.
    Active campaign calls pass its in-memory result dict and existing case shards.
    Failed staging directories are retained for diagnosis.
    """
    folder = Path(folder)
    if folder.exists() or folder.is_symlink():
        raise ValueError('Fresh aggregate-v2 output required')
    folder.parent.mkdir(parents=True, exist_ok=True)
    stage = folder.with_name('.' + folder.name + '.pending')
    if stage.exists() or stage.is_symlink():
        raise ValueError('Interrupted aggregate-v2 staging retained')
    stage.mkdir()
    if isinstance(result_or_source, (str, Path)):
        if cases_source is None:
            raise ValueError('Migration source case directory required')
        entries = _source_rows(result_or_source, cases_source)
        core = next(entries)
        expected_aggregate = _hash_file(result_or_source)
    elif isinstance(result_or_source, dict):
        rows = result_or_source.get('rows')
        if not isinstance(rows, list) or len(rows) > MAX_ROWS:
            raise ValueError('Bounded in-memory aggregate rows required')
        core_value = dict(result_or_source)
        core_value['rows'] = []
        core = encoded(core_value)
        entries = ((row['case_context_id'], encoded(row)) for row in rows)
        expected_aggregate = None
        if result_or_source.get('campaign_id') != canonical_stream.canonical_identity(result_or_source, semantic=True):
            raise ValueError('Aggregate semantic campaign_id differs')
    else:
        raise TypeError('Aggregate source must be an in-memory dict or canonical file')
    if len(core) > MAX_CORE_BYTES:
        raise ValueError('Aggregate core exceeds Arrow document bound')
    value = _core_value(core)
    composer = _Composer(core)
    refs = []
    for context, source_raw in entries:
        path, row, raw = _case_bytes(cases_folder, context, root=root)
        if raw != source_raw:
            raise ValueError('Aggregate row and case shard bytes differ')
        ids = ROW_ID.findall(raw)
        if len(ids) != 1 or ids[0].decode() != row['row_id']:
            raise ValueError('Case row_id field differs')
        refs.append(_ref(context, raw, row, path, len(refs)))
        composer.row(raw)
    composed = composer.finish()
    if expected_aggregate is not None and composed['aggregate_sha256'] != expected_aggregate:
        raise ValueError('Reconstructed aggregate differs from source file')
    core_hash = _write_component(stage, 'core.parquet', core, root=root)
    refs_raw = encoded(refs)
    rows_hash = _write_component(stage, 'rows.parquet', refs_raw, root=root)
    manifest = dict(schema=SCHEMA, aggregate_sha256=composed['aggregate_sha256'],
                    aggregate_bytes=composed['aggregate_bytes'], row_count=len(refs),
                    core_sha256=sha256(core).hexdigest(), rows_sha256=sha256(refs_raw).hexdigest(),
                    core_parquet_sha256=core_hash, rows_parquet_sha256=rows_hash,
                    rows_open_offset=composer.offset, contract_id=value['contract_id'],
                    campaign_id=value['campaign_id'], run_id=value['run_id'],
                    source_epochs_sha256=sha256(encoded(value['source_sha256'])).hexdigest(),
                    codec_source_identity=case_node_store.codec_source_identity(root))
    manifest['manifest_id'] = sha256(encoded(manifest)).hexdigest()
    with (stage / 'manifest.json').open('xb') as target:
        target.write(encoded(manifest))
        target.flush()
        os.fsync(target.fileno())
    _ordinary(stage / 'manifest.json', MAX_MANIFEST_BYTES)
    directory = os.open(stage, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    if folder.exists() or folder.is_symlink():
        raise ValueError('Aggregate output appeared during staging')
    os.rename(stage, folder)
    directory = os.open(folder.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return manifest


def _load_store(folder, *, root):
    folder = Path(folder)
    if folder.is_symlink() or not folder.is_dir() or {p.name for p in folder.iterdir()} != {'core.parquet', 'rows.parquet', 'manifest.json'}:
        raise ValueError('Aggregate-v2 file inventory differs')
    path = folder / 'manifest.json'
    _ordinary(path, MAX_MANIFEST_BYTES)
    manifest = _loads(path.read_bytes())
    if not isinstance(manifest, dict) or manifest.get('schema') != SCHEMA:
        raise ValueError('Aggregate-v2 manifest schema differs')
    manifest_id = manifest.get('manifest_id')
    if not isinstance(manifest_id, str) or not ID.fullmatch(manifest_id):
        raise ValueError('Aggregate-v2 manifest identity differs')
    if sha256(encoded({k: v for k, v in manifest.items() if k != 'manifest_id'})).hexdigest() != manifest_id:
        raise ValueError('Aggregate-v2 manifest hash differs')
    if manifest.get('codec_source_identity') != case_node_store.codec_source_identity(root):
        raise ValueError('Aggregate-v2 codec source identity differs')
    for name, key in (('core.parquet', 'core_parquet_sha256'), ('rows.parquet', 'rows_parquet_sha256')):
        part = folder / name
        _ordinary(part, 16 * 1024 * 1024)
        if _hash_file(part) != manifest[key]:
            raise ValueError('Aggregate-v2 Parquet part hash differs')
    core = case_node_store._run(('decode', folder / 'core.parquet', '-'), root=root)
    refs_raw = case_node_store._run(('decode', folder / 'rows.parquet', '-'), root=root)
    if sha256(core).hexdigest() != manifest['core_sha256'] or sha256(refs_raw).hexdigest() != manifest['rows_sha256']:
        raise ValueError('Aggregate-v2 decoded part hash differs')
    value = _core_value(core)
    refs = _loads(refs_raw)
    if (not isinstance(refs, list) or len(refs) > MAX_ROWS
            or len(refs) != manifest['row_count'] or _core_offset(core) != manifest['rows_open_offset']):
        raise ValueError('Aggregate-v2 row references differ')
    for key in ('contract_id', 'campaign_id', 'run_id'):
        if value[key] != manifest[key]:
            raise ValueError('Aggregate-v2 core identity differs')
    if sha256(encoded(value['source_sha256'])).hexdigest() != manifest['source_epochs_sha256']:
        raise ValueError('Aggregate-v2 source epochs differ')
    return manifest, core, refs


def read(folder, cases_folder, sink, *, root=ROOT):
    """Stream verified canonical bytes to sink; caller stages external output."""
    manifest, core, refs = _load_store(folder, root=root)
    composer = _Composer(core, sink)
    seen = set()
    for ordinal, ref in enumerate(refs):
        if (not isinstance(ref, dict) or set(ref) != {'ordinal', 'case_context_id', 'row_id', 'case_sha256', 'case_bytes', 'parquet_name', 'parquet_sha256'}
                or ref['ordinal'] != ordinal or ref['case_context_id'] in seen):
            raise ValueError('Aggregate-v2 ordered case reference differs')
        context = ref['case_context_id']
        seen.add(context)
        path = case_node_store.path_for(cases_folder, context)
        _ordinary(path, 16 * 1024 * 1024)
        if ref['parquet_name'] != path.name or _hash_file(path) != ref['parquet_sha256']:
            raise ValueError('Aggregate-v2 case shard missing, swapped or corrupt')
        _, row, raw = _case_bytes(cases_folder, context, root=root)
        if (len(raw) != ref['case_bytes'] or sha256(raw).hexdigest() != ref['case_sha256']
                or row.get('row_id') != ref['row_id']):
            raise ValueError('Aggregate-v2 case row bytes or identity differ')
        composer.row(raw)
    result = composer.finish()
    if result['aggregate_sha256'] != manifest['aggregate_sha256'] or result['aggregate_bytes'] != manifest['aggregate_bytes']:
        raise ValueError('Aggregate-v2 canonical result differs')
    return manifest


def materialize(folder, cases_folder, target, *, root=ROOT):
    """Publish one fresh exact temporary JSON for current refinement consumers."""
    target = Path(target)
    if target.exists() or target.is_symlink():
        raise ValueError('Fresh aggregate materialization target required')
    target.parent.mkdir(parents=True, exist_ok=True)
    pending = target.with_name('.' + target.name + '.pending')
    if pending.exists() or pending.is_symlink():
        raise ValueError('Interrupted aggregate materialization retained')
    descriptor = os.open(pending, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, 'w+b', buffering=0) as stream:
        receipt = read(folder, cases_folder, stream, root=root)
        stream.flush()
        os.fsync(stream.fileno())
    if _hash_file(pending) != receipt['aggregate_sha256']:
        raise ValueError('Aggregate materialization changed after writing')
    os.link(pending, target, follow_symlinks=False)
    pending.unlink()
    directory = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return receipt
