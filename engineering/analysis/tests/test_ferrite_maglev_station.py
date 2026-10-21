"""Independent station-motion, accounting and infeasible-route regressions."""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import station


@pytest.fixture(scope='module')
def reference():
    return station.evaluate()


def test_reference_reproduces_independent_jerk_limited_solution(reference):
    r=reference['trajectory']
    assert reference['study_pass']
    assert r['launch_speed_kmh']==pytest.approx(55.41680783,abs=1e-5)
    assert r['brake_entry_speed_kmh']==pytest.approx(45.69652571,abs=1e-5)
    assert r['phases']['launch']['distance_m']==pytest.approx(159.8096284,abs=1e-5)
    assert r['phases']['coast']['distance_m']==pytest.approx(732.0336560,abs=1e-5)
    assert r['phases']['braking']['distance_m']==pytest.approx(108.1567156,abs=1e-5)
    assert sum(v['duration_s'] for v in r['phases'].values())==pytest.approx(90.)
    assert r['peak_traction_input_kw']==pytest.approx(2345.608,abs=.1)
    assert r['launch_input_kwh']==pytest.approx(6.47159313,abs=1e-6)
    assert r['receiving_brake_mechanical_work_kwh']==pytest.approx(3.30976371,abs=1e-6)
    assert r['energy_balance']['passed'] and abs(r['energy_balance']['residual_j'])<1e-3
    assert not any(r[key] for key in station.FLAGS)


def test_trace_independently_closes_energy_and_has_zero_coast_thrust(reference):
    r=reference['trajectory'];trace=r['trace'];launch=[v for v in trace if v['phase']=='launch']
    mass=r['inputs']['train_mass_kg']
    time=np.array([v['time_s'] for v in launch]);speed=np.array([v['speed_m_s'] for v in launch])
    force=np.array([v['motor_force_n'] for v in launch])
    drag=6000+10.8*speed**2
    work=float(np.trapezoid(force*speed,time))
    drag_work=float(np.trapezoid(drag*speed,time))
    assert work==pytest.approx(.5*mass*speed[-1]**2+drag_work,abs=100.)
    coast=[v for v in trace if v['phase']=='coast']
    assert coast and all(v['motor_force_n']==v['mechanical_kw']==v['input_kw']==0 for v in coast)
    assert all(v['acceleration_m_s2']<0 for v in coast)
    assert speed[0]==0 and abs(trace[-1]['speed_m_s'])<1e-8


def test_grades_and_impossible_runtime_are_holds_without_extra_traction():
    for grade in (.05,-.05):
        r=station.evaluate(grade=grade)
        assert not r['study_pass']
        assert not r['trajectory']['study_pass']
        assert not r['traffic']['screen_pass']
        assert r['station_power'] is None
        assert not r['trajectory']['physical_output_authorised']
    assert not station.trajectory(runtime_s=20.)['study_pass']
    assert not station.trajectory(speed_limit_kmh=10.)['study_pass']


def test_grade_two_percent_cannot_reuse_flat_station_winding():
    r=station.evaluate(grade=.02)
    assert r['trajectory']['study_pass']
    assert not r['magnetic_overlap']['study_pass']
    assert not r['study_pass']
    assert r['magnetic_overlap']['minimum_winding_length_m']>200


def test_actual_bands_overlap_counts_and_headway(reference):
    r=reference['magnetic_overlap'];traffic=reference['traffic']
    assert len(r['magnetic_bands_relative_to_front_m'])==6
    assert sum(hi-lo for lo,hi in r['magnetic_bands_relative_to_front_m'])==72
    assert r['minimum_winding_length_m']==pytest.approx(185.66,abs=.2)
    assert r['full_engagement_winding_length_m']==pytest.approx(372.466344,abs=1e-5)
    assert r['minimum_force_reserve_fraction']['braking']==pytest.approx(.1783,abs=.0005)
    assert r['installed_direction_m_per_two_direction_station']==400
    assert r['installed_face_m_per_two_direction_station']==800
    assert r['individual_face_cassettes_per_two_direction_station']==320
    assert traffic['clearance_front_distance_m']==179.5
    assert traffic['planning_minimum_headway_s']==pytest.approx(176.95115,abs=1e-4)
    assert traffic['normal_passengers_per_hour_direction']==pytest.approx(720*3600/190)
    assert traffic['release_requires_positive_full_consist_evidence']
    assert not traffic['timer_is_clearance_proof']


def test_band_gaps_are_not_filled_by_a_continuous_envelope():
    bands=np.array([[-14.5-17.5*i,-2.5-17.5*i] for i in range(6)])
    assert station._overlap([0.],bands,-1000,1000)[0]==72
    # Window falls in the gap between the first and second active car bands.
    assert station._overlap([0.],bands,-20.,-14.5)[0]==0


def test_charging_includes_disconnected_dwell_and_retains_reserve(reference):
    r=reference['charging'];battery=reference['battery']
    assert r['battery_supplied_seconds_per_cycle']==105
    assert r['replacement_kwh_per_train']==10.5
    assert r['battery_charging_kw_per_train']==840
    assert r['connected_interface_kw_per_train']==1200
    assert r['battery_charge_c_rate']==pytest.approx(14/3)
    assert battery['eol_usable_soc_window_kwh_per_car']==pytest.approx(14.4)
    assert battery['remaining_before_recharge_kwh_per_car']==pytest.approx(12.65)
    assert battery['protected_services_reserve_kwh_per_car']==10
    assert battery['screen_pass'] and not battery['accepted']
    assert reference['station_power']['two_coincident_connected_services_kw']==2400
    assert reference['station_power']['one_launch_plus_opposite_connected_services_kw']==pytest.approx(3545.608,abs=.1)


def test_full_dwell_connection_avoids_only_the_disconnected_dwell_penalty(monkeypatch):
    a=station.load();a['station']['connected_charging_s']=60.
    monkeypatch.setattr(station,'load',lambda:deepcopy(a))
    r=station.evaluate()['charging']
    assert r['battery_supplied_seconds_per_cycle']==90
    assert r['replacement_kwh_per_train']==9
    assert r['connected_interface_kw_per_train']==900
    assert r['battery_charge_c_rate']==3


def test_reserve_shortfall_and_overaggressive_headway_block_selection(monkeypatch):
    a=station.load();a['station']['services_battery_kwh_per_car']=20
    monkeypatch.setattr(station,'load',lambda:deepcopy(a))
    r=station.evaluate(headway_s=170)
    assert not r['battery']['screen_pass']
    assert not r['traffic']['screen_pass']
    assert not r['study_pass']


def test_100_second_case_couples_smaller_motor_with_tighter_headway(reference):
    r=station.evaluate(runtime_s=100.)
    assert r['trajectory']['launch_input_kwh']<reference['trajectory']['launch_input_kwh']
    assert r['magnetic_overlap']['minimum_winding_length_m']==pytest.approx(120.5,abs=.2)
    assert r['traffic']['planning_headway_margin_s']<reference['traffic']['planning_headway_margin_s']
    assert r['charging']['connected_interface_kw_per_train']==1280


def test_cost_topologies_count_inactive_hardware_and_preserve_scope(reference):
    c=reference['costs'];middle=c['sensitivity_cases'][1]['topologies']
    assert middle['B-two-fixed-groups']['installed_bridges']==4
    assert middle['B-two-fixed-groups']['direct_subtotal_usd']==2460000
    assert middle['C-routed-8-banks']['direct_subtotal_usd']==2600000
    assert middle['D-independent-sections']['installed_bridges']==32
    assert middle['B-two-fixed-groups']['subtotal_with_reserve_usd']==2952000
    assert c['supplier_quote'] is c['complete_railway_price'] is False
    assert '45-second' in c['charging_rate_basis']
    assert all(not v['phase_current_kva_rating_qualified'] for v in middle.values())


def test_generic_consist_and_cache_are_not_hardwired_to_six_cars():
    one=station.evaluate(cars=1)
    assert one['trajectory']['inputs']['train_mass_kg']==26200
    assert len(one['magnetic_overlap']['magnetic_bands_relative_to_front_m'])==1
    assert one['magnetic_overlap']['train_length_assumption_m']==17
    r=station.trajectory(record_trace=False);r['phases']['launch']['duration_s']=-999
    assert station.trajectory(record_trace=False)['phases']['launch']['duration_s']>0


def test_efficiency_changes_electrical_energy_without_rewriting_motion():
    baseline=station.trajectory(record_trace=False)
    worse=station.trajectory(record_trace=False,motoring_efficiency=.7,generating_efficiency=.6)
    assert worse['phases']==baseline['phases']
    assert worse['launch_input_kwh']/baseline['launch_input_kwh']==pytest.approx(.85/.7)
    assert worse['receiving_brake_dc_kwh']/baseline['receiving_brake_dc_kwh']==pytest.approx(.6/.85)


@pytest.mark.parametrize('options',[dict(grade=math.nan),dict(cars=True),dict(car_mass_kg=-1),
                                  dict(runtime_s=math.inf),dict(record_trace=1)])
def test_invalid_inputs_are_rejected(options):
    with pytest.raises(ValueError):station.trajectory(**options)


def test_packet_is_bounded_source_bound_and_cannot_claim_release(tmp_path):
    manifest=station.publish(tmp_path)
    assert station.verify(tmp_path)==manifest
    result=json.loads(gzip.decompress((tmp_path/'result.json.gz').read_bytes()))
    assert result['engineering_accepted_count']==0
    assert len(result['cases'])==5
    result['physical_release']=True
    payload=gzip.compress(station._encoded(result),mtime=0)
    (tmp_path/'result.json.gz').write_bytes(payload)
    manifest['files_sha256']['result.json.gz']=sha256(payload).hexdigest()
    (tmp_path/'manifest.json').write_bytes(station._encoded(manifest))
    with pytest.raises(ValueError,match='release'):station.verify(tmp_path)
