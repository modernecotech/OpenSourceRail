from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from osr_scenario.stabling_redistribution import balance_snapshot, route_to_point


def fixture():
    line = {'id': 'L', 'stations': [{'id': 'a', 'distance_from_prev_m': 0},
                                  {'id': 'b', 'distance_from_prev_m': 1000},
                                  {'id': 'c', 'distance_from_prev_m': 2000}]}
    doc = {'stations': [{'id': s} for s in ('a', 'b', 'c')], 'lines': [line],
           'fleets': [{'line': 'L', 'trainset_count': 8, 'spare_count': 1, 'dispatch_points': [
               {'station': 'a', 'heading': 'forward'}, {'station': 'b', 'heading': 'forward'},
               {'station': 'b', 'heading': 'reverse'}, {'station': 'c', 'heading': 'reverse'}]}]}
    rows = [{'train_id': f'T{i}', 'service_role': 'revenue' if i < 8 else 'spare',
             'phase': 'dwelling', 'station_id': str(station), 'departure_heading': heading, 'soc': '.95'}
            for i, station, heading in [(1, 1, 'forward'), (2, 2, 'forward'), (3, 2, 'reverse'),
                                       (4, 3, 'reverse'), (5, 3, 'reverse'), (6, 3, 'reverse'),
                                       (7, 3, 'reverse'), (8, 3, 'reverse')]]
    return doc, rows


def solve(doc, rows, battery=100):
    return balance_snapshot(doc, rows, kwh_per_km=8, battery_kwh=battery, max_speed_kmh=60)


def test_balance_preserves_inventory_reserves_and_every_revenue_direction():
    doc, rows = fixture()
    before = deepcopy(rows)
    r = solve(doc, rows)
    assert rows == before  # evidence is never mutated into the target
    assert r['observed_maximum_queue'] == 5
    assert r['target_maximum_queue'] == r['queue_lower_bound'] == 3
    assert r['trainsets_to_move'] == 2
    assert r['reserve_trainsets_moved'] == 0
    assert all(m['train'] != 8 for m in r['moves'])
    assert sum(x['trainset_count'] for x in r['target_allocations']) == 8
    assert r['planned_revenue_directions_preserved'] == 4
    for point in doc['fleets'][0]['dispatch_points']:
        assert any(x['service_role'] == 'revenue' and x['station'] == point['station']
                   and x['heading'] == point['heading'] for x in r['target_allocations'])


def test_routes_require_real_terminal_turns_and_respect_ring_direction():
    doc, _ = fixture()
    line = doc['lines'][0]
    r = route_to_point(line, 'b', 'forward', 'b', 'reverse')
    assert r == {'distance_m': 4000, 'stations': ['b', 'c', 'b'], 'terminal_reversals': 1}
    assert route_to_point(line, 'b', 'forward', 'a', 'forward')['distance_m'] == 5000
    assert route_to_point(line, 'a', 'reverse', 'b', 'forward') is None
    line.update(is_ring=True, ring_wrap_length_m=3000)
    assert route_to_point(line, 'a', 'reverse', 'c', 'reverse')['distance_m'] == 3000
    assert route_to_point(line, 'a', 'reverse', 'c', 'forward') is None


def test_insufficient_energy_does_not_invent_intermediate_charging():
    doc, rows = fixture()
    r = solve(doc, rows, battery=1)
    assert r['target_maximum_queue'] == 5
    assert not r['queue_lower_bound_attained']
    assert r['moves'] == []
    for row in rows[3:7]:
        row['soc'] = '.21'
    r = solve(doc, rows)
    assert r['precharge_required_kwh'] > 0
    assert all(m['nominal_energy_kwh'] <= 75 for m in r['moves'])


def test_missing_duplicate_and_wrong_role_snapshots_fail():
    doc, rows = fixture()
    with pytest.raises(ValueError, match='cover the fleet'):
        solve(doc, rows[:-1])
    with pytest.raises(ValueError, match='duplicate'):
        solve(doc, rows + rows[:1])
    rows[-1]['service_role'] = 'revenue'
    with pytest.raises(ValueError, match='declared roles'):
        solve(doc, rows)


def test_committed_study_is_source_bound_and_cannot_close_physical_gates():
    root = Path(__file__).resolve().parents[3]
    folder = root / 'cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling'
    r = json.loads((folder / 'redistribution-study.json').read_text())
    assert r['generation_passed'] is True and r['passed'] is False
    assert r['deployment_release_ready'] is False
    assert (r['fleet_trainsets'], r['reference_platform_berths']) == (108, 46)
    assert r['unavoidable_positions_beyond_selected_platform_envelope'] == 62
    assert r['two_trainsets_per_station_reference'] == {
        'station_count': 20, 'trainset_positions': 40, 'fleet_positions_elsewhere_or_to_resolve': 68,
    }
    for key, relative in r['source_paths'].items():
        assert r['source_sha256'][key] == hashlib.sha256((root / relative).read_bytes()).hexdigest()
    for cycle in r['cycles']:
        assert cycle['target_maximum_queue'] == cycle['queue_lower_bound'] == 7
        assert cycle['planned_revenue_directions_preserved'] == 34
        assert cycle['reserve_trainsets_moved'] == 0
        assert cycle['trainsets_beyond_reference_platform_berths'] == 62
    manifest = json.loads((folder.parents[1] / 'package-manifest.json').read_text())
    assert 'engineering/stabling/redistribution-study.json' in manifest['failed_summaries']
