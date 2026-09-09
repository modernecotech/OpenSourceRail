import hashlib
import importlib.util
import json
from pathlib import Path
import tomllib

import pytest

from osr_scenario.generator import generate_scenario
from osr_scenario.stabling import distributed_candidate

ROOT = Path(__file__).resolve().parents[3]
SAMAWAH = ROOT / 'cities/catalogue/west-asia/Iraq/Samawah'


def test_candidate_preserves_every_non_fleet_input_and_counts():
    before = (SAMAWAH / 'samawah.toml').read_text()
    candidate, rows = distributed_candidate(before)
    original, changed = tomllib.loads(before), tomllib.loads(candidate)
    assert {k:v for k,v in original.items() if k != 'fleets'} == {k:v for k,v in changed.items() if k != 'fleets'}
    assert sum(row['trainset_count'] for row in rows) == 108
    assert len({row['station'] for row in rows}) == 20
    assert all(row['verified_track_slots'] is None for row in rows)
    for old, new in zip(original['fleets'], changed['fleets']):
        assert new['station_stabling'] is True
        for key in ('line', 'trainset_count', 'schedule', 'service_start', 'service_end'):
            assert old[key] == new[key]
    assert distributed_candidate(candidate)[0] == candidate


def test_sparse_fleet_covers_route_instead_of_filling_first_stations():
    text = (SAMAWAH / 'samawah.toml').read_text().replace('trainset_count = 53', 'trainset_count = 3')
    candidate, rows = distributed_candidate(text)
    first = [r for r in rows if r['line'] == 'line-1']
    assert len(first) == 3
    assert len({r['station'] for r in first}) == 3
    assert all(r['trainset_count'] == 1 for r in first)


def test_powered_points_and_terminal_directions_are_valid_for_every_city():
    for path in (ROOT / 'cities/catalogue').glob('*/*/*/design.toml'):
        slug = tomllib.loads(path.read_text())['city']['slug']
        candidate, rows = distributed_candidate(path.with_name(f'{slug}.toml').read_text())
        doc = tomllib.loads(candidate)
        stations = {s['id']:s for s in doc['stations']}
        sites = {s['station']:s for s in doc['sites']}
        lines = {line['id']:line for line in doc['lines']}
        for row in rows:
            assert stations[row['station']]['charging_power_kw'] > 0
            assert sites[row['station']]['storage_capacity_kwh'] > 0 or sites[row['station']]['grid_import_kw'] > 0
            line = lines[row['line']]
            if not line.get('is_ring'):
                assert not (row['station'] == line['stations'][0]['id'] and row['heading'] == 'reverse')
                assert not (row['station'] == line['stations'][-1]['id'] and row['heading'] == 'forward')


def test_no_powered_station_fails_instead_of_assigning_a_fictitious_depot():
    text = (SAMAWAH / 'samawah.toml').read_text()
    import re
    text = re.sub(r'(?m)^grid_import_kw = .*$', 'grid_import_kw = 0', text)
    candidate, _ = distributed_candidate(text)
    assert all(s['grid_import_kw'] == 0 for s in tomllib.loads(candidate)['sites'])
    text = re.sub(r'(?m)^storage_capacity_kwh = .*$', 'storage_capacity_kwh = 0', text)
    with pytest.raises(ValueError, match='no station with charging'):
        distributed_candidate(text)


def test_design_fleet_opt_in_is_serialized_for_native_loader():
    design = tomllib.loads((SAMAWAH / 'design.toml').read_text())
    design['fleets'][0]['station_stabling'] = True
    scenario = tomllib.loads(generate_scenario(design, SAMAWAH / 'design.toml', ROOT / 'lib/templates'))
    assert scenario['fleets'][0]['station_stabling'] is True
    assert 'station_stabling' not in scenario['fleets'][1]


def test_committed_candidates_and_source_records_are_current():
    spec = importlib.util.spec_from_file_location('stabling_plan', ROOT / 'tools/automation/generate-stabling-plan.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    paths = list((ROOT / 'cities/catalogue').glob('*/*/*/design.toml'))
    assert len(paths) == 266
    for path in paths:
        candidate, report = module.build(path)
        assert json.loads((path.parent / 'engineering/stabling/summary.json').read_text()) == report
        assert (path.parent / 'engineering/stabling/README.md').read_text() == module.markdown(report)
        assert hashlib.sha256(candidate.encode()).hexdigest() == report['candidate_sha256']
        assert report['passed'] is False
        hybrid = report['hybrid_allocation']
        assert not hybrid['depot_access_requirements']
        lines = {line['id']: {r['id'] for r in line['stations']} for line in tomllib.loads(candidate)['lines']}
        assert all(r['station'] in lines[r['line']] for r in hybrid['allocations'])
        assert hybrid['capacity']['passed']
        assert hybrid['station_trainsets'] + hybrid['depot_trainsets'] == report['fleet_trainsets']
        assert all(n <= 2 for n in hybrid['station_trainsets_by_location'].values())


def test_samawah_historical_operating_evidence_keeps_its_candidate_and_scope():
    folder = SAMAWAH / 'engineering/stabling'
    report = json.loads((folder / 'operating-screen.json').read_text())
    plan = json.loads((folder / 'summary.json').read_text())
    assert report['candidate_sha256'] == plan['candidate_sha256']
    assert report['passed'] is False
    assert report['operating_behavior_passed'] is True
    assert report['station_capacity_passed'] is False
    assert report['deployment_release_ready'] is False
    # Historical experiment provenance is retained; it need not match active code.
    retained = report['cases']['retained_endpoints']
    distributed = report['cases']['distributed_stations']
    assert retained['parked_station_count_at_0529'] == 6
    assert distributed['parked_station_count_at_0529'] == 20
    assert distributed['parked_trainsets_at_0529'] == 108
    assert distributed['largest_overnight_station_queue'] == 8
    assert distributed['departures_between_0230_and_0530'] == 0
    assert distributed['every_occupied_station_restarts_within_60s']
    assert distributed['invariant_violations'] == []
    assert plan['fleet_roles'] == {'revenue': 97, 'spare': 8, 'cold_reserve': 3}
    assert plan['trainsets_beyond_reference_platform_berths'] == 62
    assert plan['station_capacity']['available_station_positions'] == 40
    assert plan['station_capacity']['inventory_excess_trainsets'] == 68
    assert distributed['station_capacity']['passed'] is False
    directions = distributed['directional_service']
    assert directions['directions_restarting_within_tolerance'] == directions['planned_direction_count'] == 34
    assert directions['reserve_departures'] == []
    assert directions['snapshot_roles'] == plan['fleet_roles']


def test_lower_power_storage_station_remains_a_candidate():
    import re
    text = (SAMAWAH / 'samawah.toml').read_text()
    text = re.sub(r'(?m)^grid_import_kw = .*$', 'grid_import_kw = 0', text)
    text = re.sub(r'(?m)^charging_power_kw = .*$', 'charging_power_kw = 50', text)
    text = re.sub(r'(?m)^charger_max_kw = .*$', 'charger_max_kw = 50', text)
    candidate, rows = distributed_candidate(text)
    assert len({r['station'] for r in rows}) == 20
    selected = {r['station'] for r in rows}
    assert all(s['charging_power_kw'] == 50 for s in tomllib.loads(candidate)['stations'] if s['id'] in selected)
