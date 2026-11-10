import hashlib
import json
from pathlib import Path

from engineering.outline import planning_geometry
from engineering.railway_project.city_recalculation import verify as verify_city
from engineering.station_rail.common import identity


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/design-engine/v06-design-closure/samawah-alignment-straightening-current-source-attempt-06'
RUNNER = ROOT / 'docs/design-engine/v06-design-closure/samawah-alignment-straightening-runner-01'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_samawah_alignment_screen_is_recursively_sealed_and_nonselecting():
    manifest = read_json(PACKET / 'manifest.json')
    assert manifest['schema'] == 'osr-samawah-stop-preserving-straightening-packet/1'
    assert manifest['packet_id'] == identity({k: v for k, v in manifest.items() if k != 'packet_id'})
    actual = {
        path.relative_to(PACKET).as_posix(): digest(path)
        for path in PACKET.rglob('*') if path.is_file() and path.name != 'manifest.json'
    }
    assert actual == manifest['files_sha256']
    assert manifest['file_count'] == len(actual) == 42
    assert all('/' in name for name in actual if name.startswith('attempt-history/'))

    request = read_json(PACKET / 'request.json')
    summary = read_json(PACKET / 'summary.json')
    execution = read_json(PACKET / 'execution.json')
    integrity = read_json(PACKET / 'source-integrity.json')
    assert request['request_id'] == identity({k: v for k, v in request.items() if k != 'request_id'})
    assert request['runner_sha256'] == digest(RUNNER / 'run.py')
    assert request['worker_sha256'] == digest(RUNNER / 'worker.py')
    assert request['source_commit'] == manifest['source_commit'] == execution['source_commit']
    assert integrity['before_after_source_bytes_unchanged'] is True
    assert execution['preserved_packets_unchanged'] is True
    assert execution['returncode'] == 0
    assert execution['execution_boundary']['os_sandbox_enforced'] is False
    assert len(summary['scenarios']) == 3
    assert [row['tolerance_m'] for row in summary['scenarios']] == [25.0, 50.0, 100.0]
    assert manifest['selected'] is False and manifest['physical_accepted'] is False and manifest['gate_closed'] is False

    baseline = read_json(PACKET / 'baseline.json')
    assert baseline['evaluation_id'] == summary['baseline_evaluation_id']
    assert verify_city(baseline)
    assert len(baseline['definition_failures']) == 1
    baseline_lines = {row['line_id']: row for row in baseline['physical_definition']['mapped_lines']}
    baseline_stops = {
        line_id: [(row['id'], row['lon'], row['lat']) for row in row['stops']]
        for line_id, row in baseline_lines.items()
    }
    assert summary['baseline']['station_markers'] == 26
    assert summary['baseline']['route_km'] == 57.873249527151515

    expected_fleets = ([41, 57, 85], [41, 57, 85], [41, 57, 85])
    expected_quantities = [
        {'standard_beams': 5458, 'standard_shared_bents': 2734, 'running_rail_m': 218073.22166319558, 'running_fastening_sets': 363458},
        {'standard_beams': 5426, 'standard_shared_bents': 2718, 'running_rail_m': 216810.706, 'running_fastening_sets': 361353},
        {'standard_beams': 5406, 'standard_shared_bents': 2708, 'running_rail_m': 215970.213, 'running_fastening_sets': 359952},
    ]
    for index, row in enumerate(summary['scenarios']):
        key = f"tolerance-{int(row['tolerance_m']):03d}m"
        city = read_json(PACKET / 'scenarios' / key / 'derived-city.json')
        result = read_json(PACKET / 'scenarios' / key / 'evaluation.json')
        details = read_json(PACKET / 'scenarios' / key / 'line-details.json')
        assert city['input_id'] == identity({k: v for k, v in city.items() if k != 'input_id'})
        assert result['candidate_id'] == row['candidate_id'] == manifest['scenario_candidate_ids'][str(row['tolerance_m'])]
        assert result['evaluation_id'] == row['evaluation_id'] == manifest['scenario_evaluation_ids'][str(row['tolerance_m'])]
        assert verify_city(result)
        assert result['quantities']['route_m'] / 1000 == row['route_km']
        assert row['station_markers'] == 26
        assert row['fleet_low_base_high'] == expected_fleets[index]
        assert row['definition_failure_count'] == 1
        failure = result['definition_failures'][0]
        assert failure['kind'] == 'overlapping-standard-platform-envelope'
        assert abs(failure['legs'][0]['distance_m'] - 56.55214440738746) < 1e-9
        assert max(row['max_deviation_m_by_line'].values()) <= row['tolerance_m'] + 0.05
        assert all(row['all_station_coordinates_fixed'] for row in [row])
        assert row['all_cost_scopes_unknown'] is True
        assert all(value is None for scope in result['scope_totals_usd'].values() for value in scope.values())
        for key, value in row['guideway_quantity_screen'].items():
            assert result['quantities'][key] == value
            assert value < baseline['quantities'][key]
            expected = expected_quantities[index][key]
            if isinstance(expected, float):
                assert abs(value - expected) < 0.001
            else:
                assert value == expected
        assert city['straightening_hypothesis']['selected'] is False
        alternative_lines = {item['line_id']: item for item in result['physical_definition']['mapped_lines']}
        for line_id, alternative in alternative_lines.items():
            source = baseline_lines[line_id]
            assert alternative['coordinates'][0] == source['coordinates'][0]
            assert alternative['coordinates'][-1] == source['coordinates'][-1]
            assert [(s['id'], s['lon'], s['lat']) for s in alternative['stops']] == baseline_stops[line_id]
            chain = planning_geometry.route(alternative['coordinates'], alternative['shape'])
            for stop in alternative['stops']:
                point = planning_geometry.point(alternative['coordinates'], chain, stop['chainage_m'])
                assert abs(point[0] - stop['lon']) <= 1e-10
                assert abs(point[1] - stop['lat']) <= 1e-10
        assert len(details) == 5

    for attempt in (1, 2, 3):
        record_dir = PACKET / 'attempt-history' / f'attempt-{attempt:02d}-'
        child = next(path for path in record_dir.parent.iterdir() if path.name.startswith(record_dir.name))
        assert read_json(child / 'execution.json')['returncode'] == 1
        assert read_json(child / 'failure.json')['physical_accepted'] is False
    review = (PACKET / 'independent-review.md').read_text(encoding='utf-8')
    assert 'No OS-level read-only sandbox was enforced' in review

