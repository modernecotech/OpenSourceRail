"""Synthetic method maps below are not available physical motor evidence."""
from copy import deepcopy
from itertools import product
from math import sqrt
import pytest
from engineering.design_search import system_motion as m
from engineering.station_rail.common import identity


def bundle():
    ids=dict(candidate_id='1'*64,body_candidate_id='2'*64,support_component_id='3'*64,propulsion_component_id='4'*64)
    spec=dict(**ids,rotors=dict(radius_m=.335,equivalent_inertial_mass_kg_per_car=0.),pad_friction_coefficient_hypothesis=.35,
        maximum_pressure_Pa_hypothesis=.6e6,pressure_response_delay_s_hypothesis=1.,pressure_rise_time_s_hypothesis=.4,
        opposed_pistons_per_caliper_hypothesis=2,piston_diameter_m_hypothesis=.1,effective_friction_radius_m=.23)
    return dict(schema='osr-coupled-railway-bundle/1',bundle_id=ids['candidate_id'],**ids,requirement_revision='SYNTHETIC-METHOD-1',
        cars=1,mass=dict(accounted_tare_kg_per_car=900.,accounted_cap_loaded_kg_per_car=1000.,accounted_160_control_kg_per_car=1500.),
        rotating_equivalent_kg_per_car=0.,motor_definition={'motor_component_id':ids['propulsion_component_id']},brake_definition=spec,
        architecture_case=dict(commanded_power_windows_m=[[0.,100.]],requirements={}),source_sha256={'fixture':'5'*64})


def case(b,**changes):return m.scenario(b,dict(distance_m=100.,powered_windows=[[0.,100.]],speed_cap_m_s=100.,current_command_A=10.,initial_current_A=10.,rolling_coefficient=0.,bearing_N_per_car=0.,aero_N_s2_m2_per_car=0.,**changes))


def force_map(b,s,force=100.,loss=0.):
    axes=dict(position_m=[0.,s['distance_m']],speed_m_s=[0.,100.],current_A=[0.,10.],temperature_C=[20.,80.]);rows=[]
    for x,v,I,T in product(*(axes[a] for a in m.AXES)):
        F=force*I/10;P_loss=loss*I/10
        rows.append(dict(zip(m.AXES,(x,v,I,T)),thrust_N_train=F,electrical_input_W_train=F*v+P_loss,loss_W_train=P_loss,voltage_V=100.,vertical_force_N_train=0.))
    value=dict(schema='osr-station-available-force-map/1',candidate_id=b['candidate_id'],motor_component_id=b['propulsion_component_id'],scenario_id=s['scenario_id'],
        evidence_kind='synthetic-method-test',powered_windows=s['powered_windows'],axes=axes,samples=rows,
        thermal_model=dict(capacity_J_K=1e6,ambient_C=20.,initial_C=20.,maximum_C=80.,heat_rejection_W_K=0.),
        electrical_limits=dict(maximum_voltage_V=750.,maximum_current_A=20.,current_slew_A_s=1000000.))
    value['evaluation_id']=identity(value);return value


def seal(x):x=deepcopy(x);x.pop('evaluation_id',None);x['evaluation_id']=identity(x);return x


def test_missing_or_frozen_linear_or_generic_DC_map_never_becomes_available_force():
    b=bundle();s=case(b);r=m.evaluate(b,scenario_overrides={k:v for k,v in s.items() if k!='scenario_id'})
    assert r['forward_motion']['execution']=='not-run' and not r['physical_journey_completed']
    assert r['required_demand']['available_force'] is None and r['model_tasks']
    assert len(r['braking']['cases'])==9
    x=force_map(b,s);x.update(evidence_kind='verified-numerical-operating-map',model_family='linear-phasor-LIM')
    assert not m.admit_map(b,seal(x),s)['admitted']
    x['model_family']='generic-DC-MMF-benchmark'
    assert not m.admit_map(b,seal(x),s)['admitted']


def test_synthetic_map_requires_explicit_optin_and_cannot_claim_physical_journey():
    b=bundle();s=case(b);x=force_map(b,s)
    assert not m.admit_map(b,x,s)['admitted']
    r=m.forward(b,x,s,allow_synthetic=True)
    assert r['execution']=='completed-method-test' and r['test_only']
    assert r['available_motor_map_id'] is None and not r['physical_journey_completed']


def test_exact_constant_force_solution_and_energy_are_independent_of_demand_target():
    b=bundle();s=case(b);r=m.forward(b,force_map(b,s),s,allow_synthetic=True)
    assert r['state']=='destination-boundary' and r['final_position_m']==pytest.approx(100.,abs=1e-8)
    assert r['final_speed_m_s']==pytest.approx(sqrt(20.),abs=1e-8)
    assert r['elapsed_s']==pytest.approx(sqrt(2000.),abs=1e-8)
    assert abs(r['energy_residual_J'])<1e-6 and abs(r['electrical_work_residual_J'])<1e-6
    assert not r['predicted_stop_within_berth']


def test_partial_window_uses_actual_force_only_then_coasts_without_hidden_booster():
    b=bundle();s=case(b);s['powered_windows']=[[0.,10.]];s.pop('scenario_id');s['scenario_id']=identity(s)
    r=m.forward(b,force_map(b,s),s,allow_synthetic=True)
    assert r['final_position_m']==pytest.approx(100.,abs=1e-8)
    assert r['final_speed_m_s']==pytest.approx(sqrt(2.),abs=1e-7)
    assert r['mechanical_propulsion_work_J']==pytest.approx(1000.,abs=1e-5)
    assert all(t['thrust_N_train']==0 for t in r['trace'] if t['position_m']>10+1e-6)


def test_exact_candidate_motor_domain_and_cartesian_identity_are_required():
    b=bundle();s=case(b);x=force_map(b,s)
    for key,value in [('candidate_id','a'*64),('motor_component_id','b'*64),('scenario_id','c'*64),('powered_windows',[[0.,50.]])]:
        assert not m.admit_map(b,seal({**x,key:value}),s,allow_synthetic=True)['admitted']
    x['samples']=x['samples'][:-1]
    assert not m.admit_map(b,seal(x),s,allow_synthetic=True)['admitted']
    x=force_map(b,s)
    with pytest.raises(ValueError,match='outside sampled'):m.sample_map(x,position_m=101.,speed_m_s=0,current_A=0,temperature_C=20)


def test_no_centre_force_overlap_scaling_and_no_unbalanced_electrical_power():
    b=bundle();s=case(b);x=force_map(b,s)
    for row in x['samples']:
        row['thrust_N_train']*=row['position_m']/100;row['electrical_input_W_train']=row['thrust_N_train']*row['speed_m_s']
    x=seal(x);r=m.forward(b,x,s,allow_synthetic=True)
    assert r['state']=='stalled' and r['final_position_m']==0.
    x=force_map(b,s);x['samples'][0]['electrical_input_W_train']=500
    assert not m.admit_map(b,seal(x),s,allow_synthetic=True)['admitted']


def test_thermal_and_bus_limits_stop_method_instead_of_clipping():
    b=bundle();s=case(b);x=force_map(b,s,loss=100000.)
    x['thermal_model'].update(capacity_J_K=1000.,maximum_C=20.01)
    assert m.forward(b,seal(x),s,allow_synthetic=True)['state']=='thermal-limit'
    x=force_map(b,s);x['electrical_limits']['maximum_voltage_V']=50
    assert m.forward(b,seal(x),s,allow_synthetic=True)['state']=='electrical-limit'


def test_brake_mass_channel_loss_and_grade_failures_remain_hypothesis_screens():
    b=bundle();r=m.brake_screens(b,case(b));assert not r['qualified_braking_floor']
    for load in ('empty','normal','crowd'):
        rows={x['case']:x for x in r['cases'] if x['loading']==load}
        assert rows['insufficient-adhesion-control']['state']=='cannot-stop-in-declared-hypothesis'
        assert all(abs(x['energy_residual_J_per_car'])<1e-5 for x in rows.values())
    bad=deepcopy(b);bad['brake_definition']['candidate_id']='f'*64
    with pytest.raises(ValueError,match='differs'):m.brake_screens(bad,case(bad))
