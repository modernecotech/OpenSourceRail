"""Mass/energy ownership, controller bounds and strict candidate propagation."""
from copy import deepcopy
from math import copysign
import pytest

from engineering.railway_project import bundle,drive,motion
from engineering.station_rail.common import identity
from test_railway_project_bundle import inputs,station,civil_control
from test_railway_project_drive import body_fixture,declared
from test_railway_project_civil import seal


def project():
    b,a=inputs();other=body_fixture()
    b['parts']=other['parts'];b['patterns']=other['patterns'];b['source_sha256']=other['source_sha256']
    b['physical_definition']['hardware']=other['physical_definition']['hardware']
    b['compact_drive_contract'].update(geartrain=other['compact_drive_contract']['geartrain'])
    b['candidate_id']=identity(b['physical_definition'])
    b['compact_drive_contract']['candidate_id']=b['candidate_id']
    b['compact_drive_contract']['mass_ownership'].update(zero_is_exact_no_external_addition_not_unknown_equipment=True,
        remaining_unknown_mass_positive=True)
    b['compact_drive_contract'].pop('contract_id',None)
    b['compact_drive_contract']['contract_id']=identity(b['compact_drive_contract'])
    seal(b)
    s=station(b,a);c=civil_control(b,a);p=bundle.combine(b,a,c,s)
    return p,b,a,drive.evaluate(b,declared())


def scenario():
    return dict(load_state='normal',mass_case='base',grade_fraction=.02,grade_observation_fraction=.02,
        headwind_m_s=0.,speed_cap_m_s=55/3.6,rolling_coefficient=.003,air_density_kg_m3=1.2,cd_a_m2=10.,
        acceleration_request_m_s2=.8,comfort_jerk_m_s3=.5,non_motor_rotating_mass_fraction=.04,
        brake_force_cap_n=180000.,brake_lower_fraction=.9,adhesion_fraction=.15,adhesion_lower_fraction=.06,
        brake_latency_s=.3,brake_rise_s=1.,berth_tolerance_m=1.,dt_s=.05,max_time_s=1800.,dwell_s=35.,headway_s=200.,
        hotel_power_w_per_car=50000.,train_total_supply_limit_w=3.3e6,
        assumption_reference='synthetic-unit-control-not-installed-hardware',
        brake_independence_hypothesis='independent-stored-brake-energy-hypothesis',
        power_loss_at_s=None,failed_drive_fraction=0.,emergency_at_m=None)


def test_exact_route_mass_and_copper_cooling_partition_reach_rust_input():
    p,b,a,d=project();q,manifest=motion.compile_case(p,b,a,d,0,scenario())
    assert q['candidate_id']==p['candidate_id'] and q['distance_m']==a['legs'][0]['distance_m']
    assert q['mass_kg']==140700.
    assert q['drive']['external_mass_kg']==0.
    assert q['rotating_equivalent_mass_kg']==pytest.approx(140700*.04+d['model']['rotor_reflected_equivalent_mass_kg'])
    assert q['auxiliary_power_w']==pytest.approx(300000.+drive.mandatory_auxiliary_power_w(d))
    assert q['drive']['grid_power_w']+q['auxiliary_power_w']<=scenario()['train_total_supply_limit_w']
    assert manifest['old_pilot_force_mass_or_distance_imported'] is False
    assert manifest['physical_accepted'] is False and q['thermal'] is None


def test_reverse_travel_uses_other_station_and_grade_sign_without_reflecting_body():
    args=project();a,m=motion.compile_case(*args,0,scenario())
    b,n=motion.compile_case(*args,0,scenario(),direction=-1)
    assert a['mass_kg']==b['mass_kg'] and a['drive']==b['drive']
    assert a['grade_fraction']==-b['grade_fraction']==.02
    assert m['from_stop']==n['to_stop'] and m['to_stop']==n['from_stop']
    assert a['control']['policy_id']==b['control']['policy_id']


def test_unknown_supply_mixed_mass_and_brake_obligations_cannot_export():
    args=project();s=scenario();s['train_total_supply_limit_w']=3e6
    with pytest.raises(ValueError,match='Total supply'):
        motion.compile_case(*args,0,s)
    s=scenario();s['brake_force_cap_n']=None
    with pytest.raises(ValueError,match='physical input'):
        motion.compile_case(*args,0,s)
    s=scenario();s['brake_latency_s']=1.
    with pytest.raises(ValueError,match='latency'):
        motion.compile_case(*args,0,s)
    p,b,a,d=args;changed=deepcopy(d);changed['body_evaluation_id']='a'*64;seal(changed)
    with pytest.raises(ValueError,match='Mixed'):
        motion.compile_case(p,b,a,changed,0,scenario())


def test_fault_at_departure_is_explicit_and_keeps_independent_brake_bounds():
    s=scenario();s['power_loss_at_s']=0.
    q,m=motion.compile_case(*project(),0,s)
    assert q['fault']['power_loss_at_s']==0.
    assert q['control']['brake_force_lower_bound_n']>0
    assert q['control']['end_of_authority_m']==q['distance_m']


def test_resealed_wrong_drive_contract_or_invented_available_curve_refuses():
    p,b,a,d=project();changed=deepcopy(d);changed['body_contract_id']='f'*64;seal(changed)
    with pytest.raises(ValueError,match='body/drive contract'):
        motion.compile_case(p,b,a,changed,0,scenario())
    changed=deepcopy(d);changed['model']['rotor_reflected_equivalent_mass_kg']*=.5;seal(changed)
    with pytest.raises(ValueError,match='drive producer contract'):
        motion.compile_case(p,b,a,changed,0,scenario())


def test_native_numeric_types_are_explicit_before_policy_and_case_hashes():
    s=scenario();s.update(grade_fraction=0,grade_observation_fraction=0,cd_a_m2=10,dwell_s=35)
    q,m=motion.compile_case(*project(),0,s)
    assert type(q['grade_fraction']) is type(q['cd_a_m2']) is type(q['dwell_s']) is float
    assert type(q['control']['grade_estimate_fraction']) is float
    assert type(q['control']['initial_hold_applied']) is bool
    assert q['id']==identity({k:v for k,v in q.items() if k!='id'})
    assert m['native_input_id']==identity(q)
    assert type(m['scenario']['cd_a_m2']) is int  # original assumption retained
    original=dict(a=2**53,b=-0.0,c=True,d=None)
    out=motion.native_numbers(original)
    assert out==original and type(out['a']) is float and out['c'] is True and out['d'] is None
    assert copysign(1.,out['b'])==-1.
    with pytest.raises(ValueError,match='exactly as binary64'):
        motion.native_numbers(2**53+1)
    with pytest.raises(ValueError,match='Finite binary64'):
        motion.native_numbers(float('inf'))
