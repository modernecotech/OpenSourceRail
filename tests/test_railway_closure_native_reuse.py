import gzip
import json

import pytest

from engineering.station_pair.native_reuse import seed_exact_batch
from engineering.station_rail.common import digest, encoded, identity


def sealed(value):
    value['receipt_id'] = identity(value)
    return value


def fixture_cache(tmp_path):
    source_runs = tmp_path / 'source' / 'native-runs'
    source_runs.mkdir(parents=True)
    source = source_runs / 'old-key'
    source.mkdir()
    request = {'schema': 'osr-test-request/1', 'cases': [{'id': 'case-1'}]}
    raw = encoded(request)
    input_path = source / 'input.json.gz'
    input_path.write_bytes(gzip.compress(raw, mtime=0))
    output_path = source / 'output.json.gz'
    output_path.write_bytes(gzip.compress(encoded({'result': 7}), mtime=0))
    execution = {'exit_code': 0, 'failure': None, 'wall_s': 0.125}
    (source / 'execution.json').write_bytes(encoded(execution))
    (source / 'stderr.log').write_bytes(b'')

    previous_build = sealed({
        'schema': 'osr-test-build/1', 'source_sha256': {'source.rs': 'a' * 64},
        'tools': {'rustc': 'rustc test'}, 'product': 'test', 'protocol': 'test/1',
        'binary_sha256': 'b' * 64, 'build_location': '/old/run',
    })
    current_build = sealed({
        'schema': 'osr-test-build/1', 'source_sha256': {'source.rs': 'a' * 64},
        'tools': {'rustc': 'rustc test'}, 'product': 'test', 'protocol': 'test/1',
        'binary_sha256': 'b' * 64, 'build_location': '/new/run',
    })
    context = {
        'bridge_sha256': 'c' * 64,
        'resources': {'cpu_s': 10, 'memory_bytes': 1024},
        'platform': 'test-platform', 'machine': 'test-machine',
    }
    receipt = sealed({
        'schema': 'osr-test-execution/1', 'request_sha256': identity(request),
        'build_receipt_id': previous_build['receipt_id'],
        'output_sha256': digest(output_path), 'input_gzip_sha256': digest(input_path),
        'resources': context['resources'], 'context': context, **execution,
    })
    receipt_path = source / 'receipt.json'
    receipt_path.write_bytes(encoded(receipt))
    manifest_files = {
        f'native/serial/native-runs/old-key/{path.name}': digest(path)
        for path in source.iterdir()
    }
    return source_runs, request, raw, previous_build, current_build, context, receipt, manifest_files


def test_exact_native_batch_rebinds_build_receipt_and_preserves_origin(tmp_path):
    (source_runs, request, raw, previous_build, current_build, context,
     old_receipt, manifest_files) = fixture_cache(tmp_path)
    target = tmp_path / 'new' / 'native-runs' / 'new-key'
    target.parent.mkdir(parents=True)
    origin_bytes = (source_runs / 'old-key' / 'receipt.json').read_bytes()

    rebound = seed_exact_batch(
        source_runs=source_runs, target=target, request=request, raw_request=raw,
        previous_build=previous_build, current_build=current_build,
        current_context=context, input_hash_field='input_gzip_sha256',
        manifest_files=manifest_files, manifest_prefix='native/serial',
        run_name='native-runs', origin_manifest_id='d' * 64,
    )

    assert rebound['build_receipt_id'] == current_build['receipt_id']
    assert rebound['receipt_id'] != old_receipt['receipt_id']
    assert rebound['cache_reuse']['origin_receipt_id'] == old_receipt['receipt_id']
    assert rebound['cache_reuse']['origin_manifest_id'] == 'd' * 64
    assert (source_runs / 'old-key' / 'receipt.json').read_bytes() == origin_bytes
    assert json.loads((target / 'receipt.json').read_bytes()) == rebound
    assert gzip.decompress((target / 'input.json.gz').read_bytes()) == raw
    assert digest(target / 'output.json.gz') == old_receipt['output_sha256']


@pytest.mark.parametrize('change', ['request', 'runtime', 'binary'])
def test_native_cache_rejects_incompatible_requests_and_context(tmp_path, change):
    (source_runs, request, raw, previous_build, current_build, context,
     _, manifest_files) = fixture_cache(tmp_path)
    if change == 'request':
        request = {'schema': 'osr-test-request/1', 'cases': [{'id': 'different'}]}
        raw = encoded(request)
    elif change == 'runtime':
        context = {**context, 'resources': {'cpu_s': 11, 'memory_bytes': 1024}}
    else:
        current_build = sealed({**{k: v for k, v in current_build.items() if k != 'receipt_id'},
                                'binary_sha256': 'e' * 64})
    target = tmp_path / 'new' / 'native-runs' / 'new-key'
    target.parent.mkdir(parents=True)

    assert seed_exact_batch(
        source_runs=source_runs, target=target, request=request, raw_request=raw,
        previous_build=previous_build, current_build=current_build,
        current_context=context, input_hash_field='input_gzip_sha256',
        manifest_files=manifest_files, manifest_prefix='native/serial',
        run_name='native-runs',
    ) is None
    assert not target.exists()


def test_native_cache_fails_closed_when_manifest_disagrees(tmp_path):
    (source_runs, request, raw, previous_build, current_build, context,
     _, manifest_files) = fixture_cache(tmp_path)
    manifest_files['native/serial/native-runs/old-key/output.json.gz'] = 'f' * 64
    target = tmp_path / 'new' / 'native-runs' / 'new-key'
    target.parent.mkdir(parents=True)

    with pytest.raises(ValueError, match='source publication manifest'):
        seed_exact_batch(
            source_runs=source_runs, target=target, request=request, raw_request=raw,
            previous_build=previous_build, current_build=current_build,
            current_context=context, input_hash_field='input_gzip_sha256',
            manifest_files=manifest_files, manifest_prefix='native/serial',
            run_name='native-runs',
        )
    assert not target.exists()


def test_exact_batch_can_cross_bridge_revision_and_records_both_hashes(tmp_path):
    (source_runs, request, raw, previous_build, current_build, context,
     _, manifest_files) = fixture_cache(tmp_path)
    context = {**context, 'bridge_sha256': 'e' * 64}
    target = tmp_path / 'new' / 'native-runs' / 'new-key'
    target.parent.mkdir(parents=True)

    rebound = seed_exact_batch(
        source_runs=source_runs, target=target, request=request, raw_request=raw,
        previous_build=previous_build, current_build=current_build,
        current_context=context, input_hash_field='input_gzip_sha256',
        manifest_files=manifest_files, manifest_prefix='native/serial',
        run_name='native-runs',
    )

    assert rebound['cache_reuse']['origin_bridge_sha256'] == 'c' * 64
    assert rebound['cache_reuse']['current_bridge_sha256'] == 'e' * 64


def test_fleet_receipt_uses_context_as_resource_binding(tmp_path):
    (source_runs, request, raw, previous_build, current_build, context,
     old_receipt, manifest_files) = fixture_cache(tmp_path)
    path = source_runs / 'old-key' / 'receipt.json'
    fleet_receipt = {key: value for key, value in old_receipt.items()
                     if key not in ('receipt_id', 'resources', 'input_gzip_sha256')}
    fleet_receipt['input_sha256'] = digest(source_runs / 'old-key' / 'input.json.gz')
    fleet_receipt = sealed(fleet_receipt)
    path.write_bytes(encoded(fleet_receipt))
    manifest_files['native/serial/native-runs/old-key/receipt.json'] = digest(path)
    target = tmp_path / 'new' / 'fleet-runs' / 'new-key'
    target.parent.mkdir(parents=True)

    rebound = seed_exact_batch(
        source_runs=source_runs, target=target, request=request, raw_request=raw,
        previous_build=previous_build, current_build=current_build,
        current_context=context, input_hash_field='input_sha256',
        manifest_files=manifest_files, manifest_prefix='native/serial',
        run_name='native-runs',
    )

    assert rebound is not None
    assert rebound['input_sha256'] == fleet_receipt['input_sha256']
