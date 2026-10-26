"""Physical accounting and resource counterexamples for two-minute service."""
from copy import deepcopy
from pathlib import Path
import math
import os
import subprocess
import sys
import pytest
from scipy.integrate import solve_ivp

from engineering.comfort_design import service as s

MAIN=Path('/home/hayder/Documents/OpenSourceRail')
ROOT=MAIN if (MAIN/'docs/design-engine/ferrite-maglev/comfort-options/study.json.gz').is_file() else Path(__file__).resolve().parents[3]


@pytest.fixture(scope='module')
def vehicle():
    return dict(candidate_id='a'*64,body_candidate_id='b'*64,magnet_component_id='c'*64,
        mass=dict(accounted_tare_kg_per_car=17356.03179,accounted_cap_loaded_kg_per_car=20806.03179))


@pytest.fixture(scope='module')
def campaign(vehicle):return s.evaluate(vehicle,ROOT)


def test_actual_coast_does_not_hide_a_stop_short_of_station():
    p=s.motion_profile(2000,12,.4,.6,20806.03179,1000)
    assert p['runtime_s'] is None
    assert p['failure']=='coasts-to-rest-before-receiving-station'
    assert p['maximum_reachable_distance_before_stop_m']<1600
    assert p['coast_powered'] is False
    assert s.motion_profile(2000,12,.4,.6,20806.03179,500)['runtime_s'] is not None


def test_analytic_coast_matches_independent_ode_integrator():
    p=s.motion_profile(2000,15,.4,.6,20806.03179,1000)
    C,Q,m=1000,1.8,20806.03179
    def rhs(t,y):return [y[1],-(C+Q*y[1]**2)/m]
    r=solve_ivp(rhs,[0,p['coast_duration_s']],[0,15],rtol=1e-10,atol=1e-11)
    assert r.success
    assert r.y[0,-1]==pytest.approx(p['coast_distance_m'],abs=1e-6)
    assert r.y[1,-1]==pytest.approx(p['arrival_speed_before_braking_m_s'],abs=1e-7)
    assert abs(p['distance_residual_m'])<1e-8
    assert abs(p['energy_balance_residual_J_per_car'])<1e-8


def test_lower_mass_is_not_assumed_to_give_longer_unpowered_coast():
    light=s.motion_profile(2000,12,.4,.6,18000,1000)
    heavy=s.motion_profile(2000,12,.4,.6,30000,1000)
    assert light['maximum_unpowered_coast_distance_m']<heavy['maximum_unpowered_coast_distance_m']
    assert light['runtime_s'] is None and heavy['runtime_s'] is not None


def test_position_inverse_and_energy_residuals_across_phases():
    p=s.motion_profile(1500,15,.4,.6,20806.03179,1000)
    last=-1
    for j in range(101):
        t=p['runtime_s']*j/100;state=s.position_at(p,t)
        assert state['position_m']>=last and state['speed_m_s']>=0
        last=state['position_m']
        assert s.time_at_position(p,state['position_m'])==pytest.approx(t,abs=2e-6)
    assert s.position_at(p,p['runtime_s'])==dict(position_m=1500.,speed_m_s=0.)


def test_shared_motor_overlap_is_not_six_cars_always_engaged():
    p=s.motion_profile(2000,15,.4,.6,20806.03179,1000)
    narrow=s.motor_zone(p,350,104.5,35)
    fit=s.motor_zone(p,450,104.5,35)
    assert not narrow['geometry_full_engagement']
    assert fit['geometry_full_engagement']
    assert narrow['required_peak_force_per_fully_engaged_car_N']>fit['required_peak_force_per_fully_engaged_car_N']
    assert fit['actual_force_current_voltage_thermal_envelope'] is None
    assert fit['directions']==2 and fit['installed_direction_metres']==900


def test_primary_family_counts_and_same_candidate_identity(campaign,vehicle):
    assert len(campaign['scenarios'])==144
    assert len({r['scenario_id'] for r in campaign['scenarios']})==144
    assert campaign['candidate_id']==vehicle['candidate_id']
    assert campaign['body_candidate_id']==vehicle['body_candidate_id']
    assert campaign['magnet_component_id']==vehicle['magnet_component_id']
    assert sum(r['profile']['runtime_s'] is None for r in campaign['scenarios'])==16
    assert not campaign['operating_release'] and not campaign['selection']['integrated_operating_design_selected']


def test_section_addressing_keeps_dwell_counterexamples(campaign):
    records={(r['architecture'],r['delay_first_dwell_s']):r for r in campaign['station_resource_campaign']}
    assert records[('section-addressed',0.)]['screen']=='pass'
    assert records[('section-addressed',15.)]['screen']=='pass'
    assert records[('section-addressed',60.)]['screen']=='fail'
    assert records[('whole-zone-exclusive',15.)]['screen']=='fail'
    assert len(campaign['selected_station']['addressed_sections'])==36
    assert campaign['selected_station']['minimum_concurrent_train_phase_current_branches_per_direction']==2
    assert not campaign['selected_station']['independently_addressed_hardware_and_phase_routing_qualified']


def test_capacity_and_equal_service_cost_are_explicit(campaign):
    v=campaign['service']
    assert v['capacity_pphpd']==6*46*30==8280
    assert v['mean_regular_interval_wait_s']==60
    assert v['capacity_14400_at120s_minimum_cars']==11
    assert next(f for f in v['formation_alternatives'] if f['cars']==11)['capacity_pphpd']==15180
    assert campaign['equal_cycle_train_price_break_even']['relative_to180s_unit_price_ratio']==pytest.approx(2/3)
    assert v['actual_safe_headway_s'] is None


def test_city_fleet_retains_failed_leg_and_counted_added_stop_proposal(campaign):
    f=campaign['fleet']
    assert len(f['lines'])==14
    assert f['lines_with_unreachable_mainline_events']>0
    assert f['proposed_total_trainsets'] is None
    p=f['max2000m_spacing_alternative']
    assert p['total_trainsets']>451
    assert p['additional_passenger_station_sites']>0
    assert p['unit_trainset_price_ratio_for_equal_fleet_capex']==pytest.approx(451/p['total_trainsets'])
    assert p['actual_complete_CAPEX_USD'] is None and not p['physical_accepted']


def test_native_protocol_keeps_virtual_gap_separate_from_levitation(vehicle,campaign):
    request=s.native_request(vehicle,campaign,'nominal')
    assert len(request['model']['trains'])==3
    first={}
    for frame in request['frames']:
        for p in frame['positions']:first.setdefault(p['train'],frame['now_ns'])
    assert first[102]-first[101]==120_000_000_000
    assert first[103]-first[102]==120_000_000_000
    assert request['contract']['policy']['minimum_gap_um']==3000
    assert request['contract']['policy']['maximum_gap_um']==13000
    assert request['configuration']==list(bytes.fromhex(s.identity(dict(candidate_id=vehicle['candidate_id'],scenario_id=campaign['selected_scenario']['scenario_id']))))


def test_invalid_or_mixed_vehicle_cannot_enter_service(vehicle,campaign):
    bad=deepcopy(vehicle);bad['mass']['accounted_cap_loaded_kg_per_car']+=75
    with pytest.raises(ValueError,match='46-person'):s.evaluate(bad,ROOT)
    bad=deepcopy(campaign);bad['candidate_id']='f'*64
    with pytest.raises(ValueError,match='candidate mismatch'):s.native_request(vehicle,bad)
    edited=deepcopy(campaign);edited['service']['actual_safe_headway_s']=120
    with pytest.raises(ValueError,match='differs'):s.validate(edited,vehicle,ROOT)


def test_stopping_bound_never_credits_leader_motion():
    assert s.stopping_distance_m(15)>.5*15**2/.6
    assert s.stopping_distance_m(15,grade_permille=10)>s.stopping_distance_m(15)


def test_fresh_process_hash_seeds_preserve_complete_evaluation_identity():
    """Set iteration previously changed the order of retained conflict arrays."""
    module_root=Path(s.__file__).resolve().parents[2]
    code="""import json,sys
from pathlib import Path
from engineering.comfort_design import service
v={'candidate_id':'a'*64,'body_candidate_id':'b'*64,'magnet_component_id':'c'*64,
   'mass':{'accounted_tare_kg_per_car':17356.03179,'accounted_cap_loaded_kg_per_car':20806.03179}}
r=service.evaluate(v,root=Path(sys.argv[1]))
print(json.dumps({'evaluation_id':r['evaluation_id'],'campaign':r['station_resource_campaign']},sort_keys=True))
"""
    outputs=[]
    for seed in ('1','937'):
        env=dict(os.environ,PYTHONHASHSEED=seed,
                 PYTHONPATH=os.pathsep.join((str(module_root),str(ROOT))))
        run=subprocess.run([sys.executable,'-c',code,str(ROOT)],cwd=module_root,env=env,
                           capture_output=True,text=True,check=True,timeout=60)
        outputs.append(run.stdout)
    assert outputs[0]==outputs[1]
