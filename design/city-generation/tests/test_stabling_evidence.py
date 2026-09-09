from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

from osr_scenario.stabling import distributed_candidate
from osr_scenario.stabling_evidence import inspect_morning_service

ROOT = Path(__file__).resolve().parents[3]


def fixture():
    doc = {'stations': [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}],
           'fleets': [{'line': 'L', 'trainset_count': 2, 'dispatch_points': [
               {'station': 'b', 'heading': 'forward'}, {'station': 'b', 'heading': 'reverse'}]}]}
    rows = [{'train_id': f'T{i}', 'service_role': 'revenue', 'phase': 'awaiting',
             'station_id': '2', 'departure_heading': heading}
            for i, heading in ((1, 'forward'), (2, 'reverse'))]
    events = [{'train': 1, 'station': 2, 'kind': 'Dispatched', 'sim_time_s': 14400}]
    return doc, rows, events


def test_one_departure_at_a_station_does_not_prove_both_directions():
    doc, rows, events = fixture()
    report = inspect_morning_service(doc, events, rows)
    assert report['snapshot_covers_fleet']
    assert report['planned_direction_count'] == 2
    assert report['directions_restarting_within_tolerance'] == 1
    assert not report['passed']
    events.append({'train': 2, 'station': 2, 'kind': 'Dispatched', 'sim_time_s': 14500})
    assert not inspect_morning_service(doc, events, rows)['passed']
    events[-1]['sim_time_s'] = 14400
    assert inspect_morning_service(doc, events, rows)['passed']


def test_reserve_departure_cannot_satisfy_revenue_direction_coverage():
    doc, rows, events = fixture()
    doc['fleets'][0]['spare_count'] = 1
    rows[1]['service_role'] = 'spare'
    events.append({'train': 2, 'station': 2, 'kind': 'Dispatched', 'sim_time_s': 14400})
    report = inspect_morning_service(doc, events, rows)
    assert report['reserve_departures'] == [{'train': 2, 'role': 'spare', 'sim_time_s': 14400}]
    assert report['directions_restarting_within_tolerance'] == 1
    assert not report['passed']


def test_turnarounds_change_event_departure_direction_and_missing_snapshot_fails():
    doc, rows, events = fixture()
    # Reversing only train 1 leaves both trains departing in reverse.
    events[:0] = [{'train': 1, 'station': 3, 'kind': 'Turnaround', 'sim_time_s': 100}]
    rows[0]['departure_heading'] = 'reverse'
    events.append({'train': 2, 'station': 2, 'kind': 'Dispatched', 'sim_time_s': 14400})
    assert not inspect_morning_service(doc, events, rows)['passed']
    events.insert(1, {'train': 2, 'station': 1, 'kind': 'Turnaround', 'sim_time_s': 300})
    rows[1]['departure_heading'] = 'forward'
    assert inspect_morning_service(doc, events, rows)['passed']
    assert not inspect_morning_service(doc, events, rows[:1])['passed']
    with pytest.raises(ValueError, match='duplicate train'):
        inspect_morning_service(doc, events, rows + rows[:1])


def test_platform_comparison_does_not_double_count_a_shared_station_or_credit_sidings():
    spec = importlib.util.spec_from_file_location('stabling_plan_capacity', ROOT / 'tools/automation/generate-stabling-plan.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    station = {'id': 'S', 'archetype': 'standard', 'platform_length_m': 59.5}
    design = {'stations': [station, deepcopy(station)], 'lines': [{'name': 'L', 'rolling_stock': 'test'}]}
    allocations = [{'line': 'L', 'station': 'S', 'trainset_count': 7, 'service_role': 'revenue'},
                   {'line': 'L', 'station': 'S', 'trainset_count': 1, 'service_role': 'spare'}]
    rows = module.capacity_requirements(design, allocations, {'test': {'length_m': 49.5}}, {'standard': {'platform_count': 2}})
    assert len(rows) == 1
    row = rows[0]
    assert row['reference_platform_berths'] == 2
    assert row['trainsets_beyond_reference_platform_berths'] == 6
    assert row['additional_usable_stabling_length_m'] == 357
    assert row['verified_stabling_slots'] is None
    design['stations'][1]['platform_length_m'] = 119
    with pytest.raises(ValueError, match='inconsistent physical'):
        module.capacity_requirements(design, allocations, {'test': {'length_m': 49.5}}, {'standard': {'platform_count': 2}})


def test_candidate_reconciles_declared_roles_and_rejects_conflicting_inventory():
    import tomllib
    city = ROOT / 'cities/catalogue/west-asia/Iraq/Samawah'
    design = tomllib.loads((city / 'design.toml').read_text())
    text = (city / 'samawah.toml').read_text()
    candidate, rows = distributed_candidate(text, design['fleets'])
    assert sum(row['trainset_count'] for row in rows if row['service_role'] == 'revenue') == 97
    assert sum(row['trainset_count'] for row in rows if row['service_role'] == 'spare') == 8
    assert sum(row['trainset_count'] for row in rows if row['service_role'] == 'cold_reserve') == 3
    assert distributed_candidate(candidate)[0] == candidate
    design['fleets'][0]['spare_count'] += 1
    with pytest.raises(ValueError, match='role counts do not reconcile'):
        distributed_candidate(text, design['fleets'])
