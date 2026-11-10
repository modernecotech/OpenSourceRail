import hashlib
import json
from pathlib import Path

from engineering.station_rail.common import identity


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/design-engine/v06-design-closure/samawah-station-consolidation-current-source-attempt-03'
RUNNER = ROOT / 'docs/design-engine/v06-design-closure/samawah-station-consolidation-current-source-runner-01'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_current_source_station_consolidation_packet_is_recursively_sealed():
    manifest = read_json(PACKET / 'manifest.json')
    assert manifest['schema'] == 'osr-samawah-current-source-station-consolidation-packet/2'
    assert manifest['packet_id'] == identity({k: v for k, v in manifest.items() if k != 'packet_id'})

    actual = {
        path.relative_to(PACKET).as_posix(): digest(path)
        for path in PACKET.rglob('*')
        if path.is_file() and path.name != 'manifest.json'
    }
    assert manifest['files_sha256'] == actual
    assert manifest['file_count'] == len(actual)
    assert 'inputs/body.json.gz' in actual
    assert 'inputs/city.json' in actual
    assert 'inputs/policy.json' in actual

    request = read_json(PACKET / 'request.json')
    result = read_json(PACKET / 'result.json')
    comparison = read_json(PACKET / 'comparison.json')
    execution = read_json(PACKET / 'execution.json')
    source_integrity = read_json(PACKET / 'source-integrity.json')
    assert request['request_id'] == identity({k: v for k, v in request.items() if k != 'request_id'})
    assert result['evaluation_id'] == identity({k: v for k, v in result.items() if k != 'evaluation_id'})
    assert request['runner_sha256'] == digest(RUNNER / 'run.py')
    assert request['worker_sha256'] == digest(RUNNER / 'worker.py')
    assert manifest['source_commit'] == execution['source_commit'] == request['source_commit']
    assert manifest['candidate_id'] == result['candidate_id'] == comparison['midpoint_scenario']['candidate_id']
    assert manifest['evaluation_id'] == result['evaluation_id'] == comparison['midpoint_scenario']['evaluation_id']
    assert source_integrity['unchanged'] is True
    assert execution['retained_packets_unchanged'] is True
    assert execution['returncode'] == 0
    assert execution['execution_boundary']['os_sandbox_enforced'] is False

    baseline = comparison['baseline']
    revised = comparison['midpoint_scenario']
    assert comparison['control_reproduced'] is True
    assert comparison['source_polyline_unchanged'] is True
    assert comparison['all_other_lines_unchanged'] is True
    assert revised['route_m'] == baseline['route_m']
    assert revised['station_markers'] == baseline['station_markers'] - 1
    assert len(baseline['definition_failures']) == 1
    assert revised['definition_failures'] == []
    assert revised['line1_runtime_s'] < baseline['line1_runtime_s']
    assert revised['fleet_request_cases']['base']['total_trainsets'] == baseline['fleet_request_cases']['base']['total_trainsets']
    assert revised['fleet_request_cases']['high']['total_trainsets'] == baseline['fleet_request_cases']['high']['total_trainsets'] - 1
    assert revised['known_counted_BOM_process_subtotal_usd']['base'] == baseline['known_counted_BOM_process_subtotal_usd']['base']
    assert all(value is None for scope in revised['scope_totals_usd'].values() for value in scope.values())
    assert comparison['physical_accepted'] is False
    assert comparison['engineering_accepted'] is False
    assert comparison['gate_closed'] is False

    failed_launch = read_json(PACKET / 'attempt-01-launcher-preflight-failure.json')
    assert failed_launch['worker_started'] is False
    assert failed_launch['candidate_evaluation_started'] is False
    review = (PACKET / 'independent-review.md').read_text(encoding='utf-8')
    assert 'no OS read-only sandbox was enforced' in review
    assert '22-file packet' in review

    superseded = ROOT / 'docs/design-engine/v06-design-closure/samawah-station-consolidation-current-source-attempt-02-incomplete-manifest'
    old_manifest = read_json(superseded / 'manifest.json')
    assert old_manifest['schema'].endswith('superseded')
    assert 'nested inputs/ omitted' in old_manifest['integrity_scope']

