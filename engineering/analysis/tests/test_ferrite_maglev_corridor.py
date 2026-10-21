"""Longer fixed-line profiles, genuine Rust circuit and clearance failures."""
from copy import deepcopy
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from engineering.ferrite_maglev import corridor


@pytest.fixture(scope='module')
def binary():return corridor.build_replay()[0]


@pytest.fixture(scope='module')
def suburban():return corridor.evaluate(distance_m=5000.,cars=6,mode='suburban',runtime_s=300.,battery_kwh=50.,charger_kw=600.)


@pytest.mark.parametrize('mode,distance,runtime',[('urban',2000.,140.),('suburban',5000.,300.)])
def test_exact_piecewise_profile_closes_and_preserves_transition_states(mode,distance,runtime):
    t=corridor.profile(distance_m=distance,runtime_s=runtime,cars=6,car_mass_kg=26400.,mode=mode)
    assert t['study_pass']
    end=corridor.trajectory_at(t,runtime)
    assert end['position_m']==pytest.approx(distance,abs=1e-5)
    assert end['speed_m_s']==pytest.approx(0.,abs=1e-6)
    for seg in t['phases'][:-1]:
        time=seg['start_time_s']+seg['duration_s'];left=corridor.trajectory_at(t,time-1e-7);right=corridor.trajectory_at(t,time+1e-7)
        assert abs(left['position_m']-right['position_m'])<1e-5
        assert abs(left['speed_m_s']-right['speed_m_s'])<1e-6
        assert abs(left['acceleration_m_s2']-right['acceleration_m_s2'])<1e-6
    assert all(corridor.trajectory_at(t,s['start_time_s']+s['duration_s']/2)['motor_force_n']==0. for s in t['phases'] if s['kind']=='coast')


def test_midway_booster_is_finite_nonpassenger_asset_and_not_a_stop(suburban):
    zone=next(z for z in suburban['installed_zones'] if z['kind']=='top-up')
    assert zone['passenger'] is False and zone['length_m']==300.
    assert zone['electrical_sections']==24
    assert zone['start_m']==2350. and zone['end_m']==2650.
    seg=next(s for s in suburban['longitudinal_profile']['phases'] if s['phase']=='booster')
    assert seg['start_speed_m_s']>10.


def test_legacy_voltage_rejection_and_two_explicit_rating_alternatives():
    cases=[corridor.evaluate(distance_m=5000.,cars=6,mode='suburban',battery_kwh=50.,charger_kw=600.,motor_option=name)
        for name in ('legacy','lower-force-constant','higher-voltage')]
    assert cases[0]['motion_screen_pass'] and not cases[0]['rating_screen_pass']
    assert cases[0]['peak_voltage_bound_v']>900.
    assert all(case['rating_screen_pass'] for case in cases[1:])
    assert all(case['physical_output_authorised'] is False for case in cases)


def test_pack_and_charge_alternatives_do_not_reduce_hotel_load_or_reserve():
    short=lambda pack,charger:corridor.evaluate(distance_m=5000.,cars=6,mode='suburban',battery_kwh=pack,charger_kw=charger,dwell_s=96.)
    assert not short(30.,600.)['service_energy_screen_pass']
    assert not short(50.,400.)['service_energy_screen_pass']
    assert short(50.,600.)['service_energy_screen_pass']
    long=corridor.evaluate(distance_m=5000.,cars=6,mode='suburban',battery_kwh=50.,charger_kw=240.,dwell_s=240.)
    assert long['service_energy_screen_pass']
    assert long['service_energy']['protected_reserve_kwh_per_car']==10.
    assert long['headway_lower_bound_s']>500.


def test_180_second_capacity_is_held_under_whole_leg_arrival_reservations(suburban):
    assert suburban['headway_lower_bound_s']>390.
    assert not suburban['capacity_screen_pass'] and not suburban['study_pass']


def test_actual_rust_nominal_handover_clearance_and_power_conservation(binary,suburban):
    replay=corridor.replay(binary,suburban,indexing_spread_m=.003)
    assert replay['expected_behavior_pass']
    raw=replay['raw_replay']
    assert raw['incoming_cleared'] and raw['outgoing_committed']
    assert raw['section_arming_events']>50
    assert raw['power_conservation_max_residual_w']<1e-6
    assert raw['physical_output_authorised'] is False


@pytest.mark.parametrize('load_case',['AW0','AW2','AW3'])
def test_common_suburban_duty_executes_each_load_with_same_installed_zones(binary,load_case):
    screen=corridor.evaluate(distance_m=5000.,cars=6,mode='suburban',runtime_s=375.,battery_kwh=50.,charger_kw=600.,dwell_s=96.,load_case=load_case)
    assert screen['motion_screen_pass'] and screen['rating_screen_pass'] and screen['service_energy_screen_pass']
    assert next(z for z in screen['installed_zones'] if z['id']=='booster')['length_m']==375.
    replay=corridor.replay(binary,screen,indexing_spread_m=.003)
    assert replay['expected_behavior_pass'],replay['raw_replay']['first_fault']


def test_rehashed_nominal_copy_cannot_replace_mandatory_bias_confirmation():
    from engineering.ferrite_maglev import moving_train
    profile=corridor.evaluate(distance_m=2000.,cars=6,battery_kwh=50.)['longitudinal_profile']
    assumptions=deepcopy(moving_train.load());assumptions.update(runtime_s=140.,car_mass_kg=profile['inputs']['car_mass_kg'],operational_profile_sha256=corridor.digest(corridor.encoded(profile)))
    forged=dict(assumptions=assumptions,candidate_sha256=corridor.digest(corridor.encoded(assumptions)))
    corridor.check_moving_identity('urban/nominal',forged,profile)
    with pytest.raises(ValueError,match='mandatory moving role'):
        corridor.check_moving_identity('urban/reduced-E-positive-bias',forged,profile)


def test_rehashed_replay_fault_metadata_cannot_relabel_a_nominal_execution(binary,suburban):
    nominal=corridor.replay(binary,suburban)
    corridor.check_replay_identity(nominal,suburban,None,0.)
    forged=deepcopy(nominal);forged['fault']='resistor-loss';forged['expected_behavior_pass']=True
    with pytest.raises(ValueError,match='exact corridor replay request'):
        corridor.check_replay_identity(forged,suburban,'resistor-loss',0.)


@pytest.mark.parametrize('fault',corridor.FAULTS)
def test_actual_rust_faults_hold_committed_resources_without_false_clearance(binary,suburban,fault):
    replay=corridor.replay(binary,suburban,fault=fault)
    assert replay['expected_behavior_pass'],replay['raw_replay']['first_fault']
    assert replay['raw_replay']['fault_held']
    assert not replay['raw_replay']['incoming_cleared']
    if fault=='uncommitted':
        assert replay['raw_replay']['first_fault']['sequence']==1
        assert not replay['raw_replay']['outgoing_committed']


def test_truncating_installed_zone_cannot_create_ideal_impulse_propulsion(binary):
    screen=deepcopy(corridor.evaluate(distance_m=2000.,cars=6,battery_kwh=50.,charger_kw=400.))
    screen['installed_zones'][0]['end_m']=0.
    replay=corridor.replay(binary,screen)
    assert not replay['expected_behavior_pass']
    assert replay['raw_replay']['fault_held'] and 'Overlap' in replay['raw_replay']['first_fault']['fault']
