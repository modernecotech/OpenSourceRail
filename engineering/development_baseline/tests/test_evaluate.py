"""Regression coverage for the selected physical car and revised service."""
from copy import deepcopy
from pathlib import Path
import json
import os
import subprocess
import sys

import pytest

from engineering.comfort_design import service as method
from engineering.development_baseline import ROOT, FLAGS, evaluate


@pytest.fixture(scope='module')
def root():
    return Path(os.environ.get('OSR_EVIDENCE_ROOT', str(ROOT)))


@pytest.fixture(scope='module')
def current(root):
    return evaluate.build(root)


def test_current_service_replaces_earlier_station_prototype(current):
    s = current['service']
    p, z = s['selected_scenario']['profile'], s['selected_station']
    assert p['speed_cap_m_s'] == 20.
    assert p['distance_m'] == 2000.
    assert p['runtime_s'] == pytest.approx(151.9296321678084)
    assert z['length_m'] == 800.
    assert z['station_id'] == 'ba09b80f337c964c9dc987ebcfb7e6409cbd528783d78086dbad1961eeb422cd'
    assert z['minimum_nominal_resource_interval_s'] == pytest.approx(79.50369108813798)
    assert z['nominal_resource_screen'] == 'pass'
    assert s['assumptions']['station_winding_library_m'] == [350., 450., 600., 800., 900., 1000.]
    assert s['budget']['maximum_motor_options_per_reaching_scenario'] == 6
    assert s['named_comparisons']['archived_54kmh_450m_prototype']['launch_speed_m_s'] == 15.
    assert s['named_comparisons']['archived_54kmh_450m_prototype']['shared_winding_m'] == 450.


def test_retained_city_fleet_and_windings_use_same_72kmh_choice(current):
    f = current['service']['fleet']
    assert len(f['lines']) == 14
    assert f['proposed_total_trainsets'] == 906
    assert sum(r['proposed_total_trainsets'] for r in f['lines']) == 906
    assert f['additional_passenger_station_sites'] == 0
    assert f['total_direction_winding_m'] == 390500.
    assert f['motor_overlap_count'] == 4
    assert sum(float(k) * v for k, v in f['station_library_counts'].items()) == 390500.
    assert f['overlapping_motor_hardware_or_phase_handoff_qualified'] is False
    assert 'max2000m_spacing_alternative' not in f
    assert f['station_winding_library_m'] == [350., 450., 600., 800., 900., 1000.]


def test_interfaces_follow_current_station_ids(current):
    s = current['service']
    pairs = {(r['scenario_id'], z['station_id']) for r in s['scenarios'] for z in r['motor_zone_options']}
    assert all((r['scenario_id'], r['station_id']) in pairs for r in s['selection']['shortlist'])
    assert current['interfaces']['service_evaluation_id'] == s['evaluation_id']
    assert current['interfaces']['station']['cases'][0]['station_id'] == s['selected_station']['station_id']
    assert s['selected_station']['sections_per_direction'] == 64
    assert s['selected_station']['minimum_concurrent_train_phase_current_branches_per_direction'] == 2


def test_same_physical_car_and_unknown_installed_mass(current):
    assert current['candidate_id'] == '957f7e4e2e0e98b575810fb0c568554968fc1eb0715fb673827a16bcf63d400b'
    assert current['body_candidate_id'] == '1eca1897b983bf62ec315cdc39aca2e2387f93ad6ab0c195bc278e14c8fb120b'
    assert current['magnet_component_id'] == '397ddf033ab98afaea053acaa3047249a3329f542f1f5e52a6eb1b466b9662e0'
    assert current['vehicle']['mass']['accounted_tare_kg_per_car'] == pytest.approx(17356.683728076856)
    assert current['vehicle']['mass']['accounted_cap_loaded_kg_per_car'] == pytest.approx(20806.683728076856)
    assert current['vehicle']['mass']['installed_tare_kg_per_car'] is None
    assert current['vehicle']['mass']['CG_m'] is None
    assert current['vehicle']['mass']['inertia_kg_m2'] is None
    assert current['service']['service']['capacity_pphpd'] == 8280.
    assert current['development_default'] is True
    assert current['configuration_adopted_for_development'] is True
    assert all(current[k] is v for k, v in FLAGS.items())
    failed = {r['gate'] for r in current['gates'] if r['state'] == 'fail'}
    assert failed == {'capture-energy', 'roof-hot-core'}


def test_native_requests_use_current_profile_and_candidate(current):
    request = method.native_request(current['vehicle'], current['service'])
    assert max(p['velocity_mmps'] for frame in request['frames'] for p in frame['positions']) == 20000
    sid = current['service']['selected_scenario']['scenario_id']
    assert request['configuration'] == list(bytes.fromhex(evaluate.identity(dict(candidate_id=current['candidate_id'], scenario_id=sid))))
    assert request['contract']['control'] == 'contract-180'
    assert current['service']['protection']['safe_operation_permitted'] is False


def test_mixed_selection_rejected(current, root):
    mixed = deepcopy(current)
    mixed['service']['selected_station']['length_m'] = 450.
    with pytest.raises(ValueError, match='differs'):
        evaluate.validate(mixed, root)


def test_fresh_process_and_hash_seed_reproduce_current_identity(current, root):
    script = "from engineering.development_baseline import evaluate; import json; r=evaluate.build(" + repr(str(root)) + "); print(json.dumps([r['evaluation_id'],r['service']['evaluation_id'],evaluate.identity(r['service']['station_resource_campaign'])]))"
    env = dict(os.environ, PYTHONHASHSEED='937')
    run = subprocess.run([sys.executable, '-c', script], cwd=root, env=env,
        check=True, capture_output=True, text=True, timeout=120)
    assert json.loads(run.stdout) == [current['evaluation_id'], current['service']['evaluation_id'],
        evaluate.identity(current['service']['station_resource_campaign'])]
