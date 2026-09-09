from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from osr_scenario.stabling_cycles import inspect_cycles


def cycle_fixture():
    doc = {'scenario': {'start_time': '05:30'},
           'stations': [{'id': 'powered'}, {'id': 'unpowered'}],
           'fleets': [{'line': 'L', 'trainset_count': 2, 'service_start': '05:30', 'service_end': '02:00',
                       'dispatch_points': [{'station': 'powered', 'heading': 'forward'}]}]}
    rows = [{'train_id': f'T{i}', 'sim_time_s': '86340', 'service_role': 'revenue',
             'phase': 'dwelling', 'station_id': '1', 'departure_heading': 'forward', 'soc': '0.95'}
            for i in (1, 2)]
    result = {'sim_duration_s': 174601, 'invariant_violations': [],
              'per_train_final_soc': [['T1', 'L', .95, .4], ['T2', 'L', .95, .3]],
              'events': [{'train': 1, 'station': 1, 'kind': 'DepartStation', 'sim_time_s': 86400},
                         {'train': 1, 'station': 1, 'kind': 'DepartStation', 'sim_time_s': 172800}]}
    second = deepcopy(rows)
    for row in second:
        row['sim_time_s'] = '172740'
    return doc, result, {86340: rows, 172740: second}


def test_a_direction_restart_does_not_prove_all_trains_reached_stabling():
    doc, result, snapshots = cycle_fixture()
    assert inspect_cycles(doc, result, snapshots, 2)['passed']
    snapshots[172740][1]['station_id'] = '2'
    snapshots[172740][1]['soc'] = '0.21'
    report = inspect_cycles(doc, result, snapshots, 2)
    assert report['cycles'][0]['passed']
    cycle = report['cycles'][1]
    assert cycle['all_trainsets_parked']
    assert cycle['directional_service']['passed']
    assert cycle['trainsets_outside_selected_stabling_stations'][0]['train'] == 'T2'
    assert not report['passed']


def test_repeated_clock_time_cannot_substitute_for_a_missing_day():
    doc, result, snapshots = cycle_fixture()
    snapshots[172740] = deepcopy(snapshots[86340])
    with pytest.raises(ValueError, match='different elapsed time'):
        inspect_cycles(doc, result, snapshots, 2)
    del snapshots[172740]
    assert not inspect_cycles(doc, result, snapshots, 2)['passed']
    result['sim_duration_s'] = 86401
    with pytest.raises(ValueError, match='30 minutes'):
        inspect_cycles(doc, result, snapshots, 2)


def test_overnight_departure_and_depleted_battery_fail_independently():
    doc, result, snapshots = cycle_fixture()
    result['events'].insert(1, {'train': 2, 'station': 1, 'kind': 'DepartStation', 'sim_time_s': 170000})
    report = inspect_cycles(doc, result, snapshots, 2)
    assert report['cycles'][0]['passed']
    assert report['cycles'][1]['departures_between_0230_and_0530'] == 1
    assert not report['passed']
    result['events'].pop(1)
    result['per_train_final_soc'][1][3] = .19
    report = inspect_cycles(doc, result, snapshots, 2)
    assert all(c['passed'] for c in report['cycles'])
    assert not report['battery_reserve_preserved']
    assert not report['passed']


def test_invalid_service_window_and_nonfinite_soc_are_rejected():
    doc, result, snapshots = cycle_fixture()
    doc['scenario']['start_time'] = '01:30'
    with pytest.raises(ValueError, match='05:30'):
        inspect_cycles(doc, result, snapshots, 2)
    doc['scenario']['start_time'] = '05:30'
    snapshots[86340][0]['soc'] = 'nan'
    with pytest.raises(ValueError, match='nonfinite'):
        inspect_cycles(doc, result, snapshots, 2)


def test_samawah_continuous_evidence_is_current_after_charging_reachability_repair():
    root = Path(__file__).resolve().parents[3]
    folder = root / 'cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling'
    report = json.loads((folder / 'service-cycle-screen.json').read_text())
    plan = json.loads((folder / 'summary.json').read_text())
    assert report['candidate_sha256'] == report['scenario_sha256'] == plan['candidate_sha256']
    assert report['service_days'] == 2
    assert report['passed'] is False
    assert report['operating_behavior_passed'] is True
    assert report['station_capacity_passed'] is False
    assert report['deployment_release_ready'] is False
    for key, relative in report['source_paths'].items():
        assert report['source_sha256'][key] == hashlib.sha256((root / relative).read_bytes()).hexdigest()
    assert [len(c['trainsets_outside_selected_stabling_stations']) for c in report['cycles']] == [0, 0]
    assert all(c['parked_trainsets'] == 108 and c['parked_station_count'] == 20 for c in report['cycles'])
    assert all(c['operating_behavior_passed'] and not c['passed'] and c['departures_between_0230_and_0530'] == 0 for c in report['cycles'])
    assert all(c['station_capacity']['inventory_excess_trainsets'] == 68 for c in report['cycles'])
    assert all(not c['directional_service']['reserve_departures'] for c in report['cycles'])
    assert all(c['directional_service']['directions_restarting_within_tolerance'] == 34 for c in report['cycles'])
    manifest = json.loads((folder.parents[1] / 'package-manifest.json').read_text())
    assert 'engineering/stabling/service-cycle-screen.json' in manifest['failed_summaries']
    assert 'engineering/stabling/summary.json' in manifest['failed_summaries']
    assert manifest['passed'] is False
