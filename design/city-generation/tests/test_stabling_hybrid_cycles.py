from copy import deepcopy

import pytest

from osr_scenario.stabling_hybrid_cycles import inspect_hybrid_cycles


def fixture():
    home = {'station': 'a', 'heading': 'forward', 'location_type': 'station', 'service_role': 'revenue', 'trainset_count': 2}
    depot = {**home, 'location_type': 'depot', 'trainset_count': 1}
    doc = {'scenario': {'start_time': '05:30'}, 'stations': [{'id': 'a', 'depot_stabling_positions': 2}],
           'fleets': [{'line': 'L', 'trainset_count': 4, 'service_start': '05:30', 'service_end': '02:00',
                       'dispatch_points': [{'station': 'a', 'heading': 'forward'}],
                       'overnight_allocations': [home, {**depot, 'service_role': 'spare'}, depot]}]}
    rows = [{'train_id': f'T{i}', 'sim_time_s': '86340', 'service_role': 'spare' if i == 3 else 'revenue',
             'phase': 'awaiting', 'station_id': '1', 'heading': 'forward', 'departure_heading': 'forward',
             'stabling_location': 'station' if i <= 2 else 'depot', 'soc': '0.95'} for i in range(1, 5)]
    result = {'sim_duration_s': 174601, 'invariant_violations': [],
              'per_train_final_soc': [[f'T{i}', 'L', .95, .4] for i in range(1, 5)],
              'events': [{'train': train, 'station': 1, 'kind': 'Dispatched', 'sim_time_s': opening}
                         for opening in (86400, 172800) for train in (1, 4)]}
    second = deepcopy(rows)
    for r in second:
        r['sim_time_s'] = '172740'
    return doc, result, {86340: rows, 172740: second}


def test_explicit_roles_and_depot_capacity_are_distinct_from_station_berths():
    doc, result, snapshots = fixture()
    report = inspect_hybrid_cycles(doc, result, snapshots, 2)
    assert report['passed']
    assert all(c['station_trainsets'] == c['depot_trainsets'] == 2 for c in report['cycles'])
    assert all(c['depot_revenue_departures_first_30_minutes'] == 1 for c in report['cycles'])
    snapshots[172740][3]['stabling_location'] = 'station'
    report = inspect_hybrid_cycles(doc, result, snapshots, 2)
    assert not report['passed']
    assert not report['cycles'][1]['capacity']['passed']
    assert report['cycles'][1]['misplaced_trainsets'][0]['train'] == 'T4'


def test_depot_departure_cannot_mask_missing_station_launch_stock():
    doc, result, snapshots = fixture()
    result['events'] = [e for e in result['events'] if e['train'] == 4]
    report = inspect_hybrid_cycles(doc, result, snapshots, 2)
    assert not report['passed']
    assert all(c['home_placement_passed'] and not c['morning_launch_passed'] for c in report['cycles'])


def test_missing_or_duplicate_snapshot_and_mistimed_night_are_detected():
    doc, result, snapshots = fixture()
    snapshots[172740].pop()
    assert not inspect_hybrid_cycles(doc, result, snapshots, 2)['passed']
    snapshots[172740].append(snapshots[172740][0])
    with pytest.raises(ValueError, match='duplicate'):
        inspect_hybrid_cycles(doc, result, snapshots, 2)
    snapshots[172740] = snapshots[86340]
    with pytest.raises(ValueError, match='mistimed'):
        inspect_hybrid_cycles(doc, result, snapshots, 2)


def test_reserve_departure_low_soc_and_late_run_in_fail():
    doc, result, snapshots = fixture()
    result['events'].append({'train': 3, 'station': 1, 'kind': 'Dispatched', 'sim_time_s': 172801})
    assert not inspect_hybrid_cycles(doc, result, snapshots, 2)['passed']
    result['events'].pop()
    result['per_train_final_soc'][0][3] = .19
    assert not inspect_hybrid_cycles(doc, result, snapshots, 2)['battery_reserve_preserved']
    result['per_train_final_soc'][0][3] = .4
    result['events'].insert(0, {'train': 4, 'station': 1, 'kind': 'DepartStation', 'sim_time_s': 80000})
    report = inspect_hybrid_cycles(doc, result, snapshots, 2)
    assert not report['passed']
    assert report['cycles'][0]['departures_between_0230_and_0530'] == 1


def test_snapshot_role_phase_and_finite_soc_are_checked():
    for field, value, error in [('service_role', 'revenue', 'role'), ('phase', 'traveling', 'phase'), ('soc', 'nan', 'nonfinite')]:
        doc, result, snapshots = fixture()
        snapshots[86340][2][field] = value
        with pytest.raises(ValueError, match=error):
            inspect_hybrid_cycles(doc, result, snapshots, 2)


def test_empty_home_returns_are_reported_separately_from_passenger_service():
    doc, result, snapshots = fixture()
    result['events'].insert(0, {'train': 4, 'station': 1, 'kind': 'ReturnToStabling', 'sim_time_s': 80000})
    report = inspect_hybrid_cycles(doc, result, snapshots, 2)
    assert report['passed']
    assert report['cycles'][0]['empty_returns_between_0230_and_0530'] == 1
    assert report['cycles'][0]['passenger_departures_after_closing'] == 0
    assert not report['cycles'][0]['quiet_period_passed']


def test_reserve_precision_matches_city_validator_without_hiding_real_depletion():
    doc, result, snapshots = fixture()
    result['per_train_final_soc'][0][3] = 0.2 - 5e-6
    report = inspect_hybrid_cycles(doc, result, snapshots, 2)
    assert report['passed']
    assert report['minimum_train_soc_during_run'] == 0.2 - 5e-6
    assert report['battery_reserve_tolerance_fraction'] == 1e-5
    result['per_train_final_soc'][0][3] = 0.2 - 2e-5
    assert not inspect_hybrid_cycles(doc, result, snapshots, 2)['passed']


def test_city_hybrid_screens_are_current_and_keep_physical_release_open():
    import hashlib
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    reports = list(root.glob('cities/catalogue/*/*/*/engineering/stabling/hybrid-cycle-screen.json'))
    assert len(reports) == 4
    assert {json.loads(p.read_text())['city'] for p in reports} == {'samawah', 'uige', 'quelimane', 'edea'}
    for path in reports:
        report = json.loads(path.read_text())
        plan = json.loads(path.with_name('summary.json').read_text())
        assert report['passed'] and report['service_days'] == 2
        assert not report['deployment_release_ready']
        assert report['candidate_sha256'] == plan['native_hybrid_candidate']['sha256']
        for key, relative in report['source_paths'].items():
            assert report['source_sha256'][key] == hashlib.sha256((root / relative).read_bytes()).hexdigest()
        assert not report['reserve_departures'] and not report['invariant_violations']
        for cycle in report['cycles']:
            assert cycle['home_placement_passed'] and cycle['capacity']['passed'] and cycle['morning_launch_passed']
            assert cycle['passenger_departures_after_closing'] == 0
            assert cycle['station_trainsets'] == plan['hybrid_allocation']['station_trainsets']
            assert cycle['depot_trainsets'] == plan['hybrid_allocation']['depot_trainsets']
        manifest = json.loads((path.parents[2] / 'package-manifest.json').read_text())
        assert not [s for s in manifest['stale_analysis_sources'] if s['artifact'].endswith('hybrid-cycle-screen.json')]
