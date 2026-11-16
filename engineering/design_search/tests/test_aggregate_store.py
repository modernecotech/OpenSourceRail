"""Bounded exact aggregate-v2 reconstruction and tamper controls."""
from hashlib import sha256
import io
import json
from pathlib import Path

import pytest

from engineering.design_search import aggregate_store, canonical_stream, case_node_store
from engineering.station_rail.common import encoded


@pytest.fixture(autouse=True)
def available_codec():
    try:
        case_node_store.codec_identity()
    except ValueError:
        pytest.skip('Rust Arrow case-node codec is not built')


def fixture(tmp_path):
    rows = [
        dict(case_context_id=str(i) * 64, row_id=str(i + 2) * 64,
             candidate_id=str(i + 4) * 64, value=-0.0 if i == 1 else None,
             nested={'unknown_mass_kg': None, 'labels': ['a', 'b']})
        for i in (0, 1)
    ]
    result = dict(schema='osr-coupled-railway-campaign/1', contract_id='c' * 64,
                  source_sha256={'source.py': 'd' * 64}, rows=rows,
                  integrated_selection=None, physical_accepted=False)
    result['campaign_id'] = canonical_stream.canonical_identity(result, semantic=True)
    result['run_id'] = canonical_stream.canonical_identity(result)
    cases = tmp_path / 'cases'
    source = tmp_path / 'case-json'
    cases.mkdir()
    source.mkdir()
    for row in rows:
        case_node_store.write(case_node_store.path_for(cases, row['case_context_id']), row, 'case')
        (source / (row['case_context_id'] + '.json')).write_bytes(encoded(row))
    return result, cases, source


def test_in_memory_and_source_file_roundtrip(tmp_path):
    result, cases, source = fixture(tmp_path)
    expected = encoded(result)
    in_memory = tmp_path / 'aggregate-v2'
    manifest = aggregate_store.write(in_memory, result, cases)
    assert manifest['row_count'] == 2
    assert manifest['run_id'] == result['run_id']
    stream = io.BytesIO()
    assert aggregate_store.read(in_memory, cases, stream)['aggregate_sha256'] == sha256(expected).hexdigest()
    assert stream.getvalue() == expected
    target = tmp_path / 'materialized.json'
    aggregate_store.materialize(in_memory, cases, target)
    assert target.read_bytes() == expected
    original = tmp_path / 'original.json'
    original.write_bytes(expected)
    migrated = tmp_path / 'migrated-v2'
    aggregate_store.write(migrated, original, cases, cases_source=source)
    replay = io.BytesIO()
    aggregate_store.read(migrated, cases, replay)
    assert replay.getvalue() == expected


def test_missing_or_corrupt_case_shard_is_rejected(tmp_path):
    result, cases, _ = fixture(tmp_path)
    store = tmp_path / 'aggregate-v2'
    aggregate_store.write(store, result, cases)
    first = case_node_store.path_for(cases, result['rows'][0]['case_context_id'])
    first.write_bytes(first.read_bytes() + b'x')
    with pytest.raises(ValueError, match='corrupt'):
        aggregate_store.read(store, cases, io.BytesIO())
    first.unlink()
    with pytest.raises((OSError, ValueError)):
        aggregate_store.read(store, cases, io.BytesIO())


def test_reordered_refs_fail_even_with_resealed_manifest(tmp_path):
    result, cases, _ = fixture(tmp_path)
    store = tmp_path / 'aggregate-v2'
    aggregate_store.write(store, result, cases)
    rows = store / 'rows.parquet'
    refs = json.loads(case_node_store._run(('decode', rows, '-')))
    refs.reverse()
    for ordinal, ref in enumerate(refs):
        ref['ordinal'] = ordinal
    rows.unlink()
    raw = encoded(refs)
    case_node_store._run(('encode', '-', rows), raw=raw)
    manifest_path = store / 'manifest.json'
    manifest = json.loads(manifest_path.read_bytes())
    manifest['rows_sha256'] = sha256(raw).hexdigest()
    manifest['rows_parquet_sha256'] = aggregate_store._hash_file(rows)
    manifest.pop('manifest_id')
    manifest['manifest_id'] = sha256(encoded(manifest)).hexdigest()
    manifest_path.write_bytes(encoded(manifest))
    with pytest.raises(ValueError, match='run_id|result differs'):
        aggregate_store.read(store, cases, io.BytesIO())


def test_zero_row_partial_frontier_roundtrip(tmp_path):
    cases = tmp_path / 'cases'
    cases.mkdir()
    result = dict(schema='osr-coupled-railway-campaign/1', contract_id='c' * 64,
                  source_sha256={'source.py': 'd' * 64}, rows=[],
                  integrated_selection=None, physical_accepted=False,
                  frontier=[{'state': 'pending'}])
    result['campaign_id'] = canonical_stream.canonical_identity(result, semantic=True)
    result['run_id'] = canonical_stream.canonical_identity(result)
    store = tmp_path / 'aggregate-v2'
    manifest = aggregate_store.write(store, result, cases)
    assert manifest['row_count'] == 0
    stream = io.BytesIO()
    aggregate_store.read(store, cases, stream)
    assert stream.getvalue() == encoded(result)


def test_interrupted_staging_is_retained_without_new_attempts(tmp_path):
    result, cases, _ = fixture(tmp_path)
    target = tmp_path / 'aggregate-v2'
    pending = tmp_path / '.aggregate-v2.pending'
    pending.mkdir()
    (pending / 'failure.log').write_text('interrupted')
    with pytest.raises(ValueError, match='staging retained'):
        aggregate_store.write(target, result, cases)
    assert (pending / 'failure.log').read_text() == 'interrupted'
    assert not target.exists()
