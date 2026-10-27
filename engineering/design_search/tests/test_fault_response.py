from copy import deepcopy
from math import exp, pi
import pytest
from engineering.design_search import design_grammar, railway_bundle, fault_response as f


@pytest.fixture(scope='module')
def bundle():
    return railway_bundle.materialize(design_grammar.build(design_grammar.parameters()))


def test_flat_failed_launch_never_becomes_reverse_brake_propulsion(bundle):
    case=f.request(bundle,name='flat-stiction-control',initial_position_m=0.,initial_speed_m_s=0.,horizon_s=5.)
    result=f.solve(bundle,case)
    assert result['final_position_m']==0. and result['maximum_abs_speed_m_s']==0.
    assert result['disc_heat_J_train']==0. and result['stationary_holding_hypothesis']
    assert all(row['static_hold'] and row['acceleration_m_s2']==0. for row in result['trace'])
    assert not result['actual_protected_stop'] and result['safety_braking_floor_m_s2'] is None


def test_delay_exponential_pressure_stop_matches_independent_closed_form(bundle):
    case=f.request(bundle,name='closed-form-pressure-rise',initial_position_m=0.,initial_speed_m_s=3.,
                   horizon_s=20.,adhesion=1.,dt_s=.02)
    r=f.solve(bundle,case);spec=bundle['brake_definition']
    m=bundle['mass']['accounted_cap_loaded_kg_per_car']+bundle['rotating_equivalent_kg_per_car']
    piston=spec['opposed_pistons_per_caliper_hypothesis']*spec['maximum_pressure_Pa_hypothesis']*pi*spec['piston_diameter_m_hypothesis']**2/4
    force=spec['discs_per_car']*spec['pad_friction_coefficient_hypothesis']*piston*spec['effective_friction_radius_m']/spec['rotors']['radius_m']
    a=force/m;tau=spec['pressure_rise_time_s_hypothesis'];delay=case['detection_command_latency_s']+spec['pressure_response_delay_s_hypothesis']
    lo=0.;hi=20.
    for _ in range(70):
        q=(lo+hi)/2
        if a*(q-tau*(1-exp(-q/tau)))<3.:lo=q
        else:hi=q
    q=(lo+hi)/2;expected_time=delay+q
    expected_distance=3*expected_time-a*(q*q/2-tau*q+tau*tau*(1-exp(-q/tau)))
    assert r['stopping_events'][0]['time_s']==pytest.approx(expected_time,abs=1e-4)
    assert r['stopping_events'][0]['position_m']==pytest.approx(expected_distance,abs=3e-4)
    assert abs(r['energy_residual_J_train'])<1e-6
    assert r['disc_heat_J_train']==pytest.approx(r['initial_kinetic_energy_J_train'],abs=1e-6)


def test_station_grade_rolls_back_before_brake_then_holds_without_invented_rescue(bundle):
    case=f.request(bundle,name='rollback-control',initial_position_m=0.,initial_speed_m_s=0.,
                   grade_up_fraction=.01,horizon_s=15.,dt_s=.02)
    r=f.solve(bundle,case)
    assert r['minimum_position_m']<-.1 and r['maximum_reverse_displacement_m']>.1
    assert r['stationary_at_horizon'] and r['stationary_holding_hypothesis']
    assert r['final_signed_speed_m_s']==0.
    assert abs(r['energy_residual_J_train'])<1e-6
    assert all(row['acceleration_m_s2']==0. for row in r['trace'] if row['static_hold'])


def test_zero_pressure_downhill_follows_gravity_and_retains_moving_failure(bundle):
    case=f.request(bundle,name='pressure-loss-control',initial_speed_m_s=20.,grade_up_fraction=-.02,
                   pressure_available_fraction=0.,horizon_s=10.)
    r=f.solve(bundle,case)
    assert r['final_signed_speed_m_s']>20. and not r['stationary_at_horizon']
    assert r['disc_heat_J_train']==0. and r['lumped_active_disc_temperature_C_hypothesis']==bundle['brake_definition']['ambient_C_hypothesis']
    assert abs(r['energy_residual_J_train'])<1e-5 and not r['actual_protected_stop']


def test_resealed_wrong_bundle_or_model_claim_is_rejected(bundle):
    case=f.request(bundle,name='scope-control')
    for key,value in [('bundle_id','a'*64),('actual_isolation_transient_verified',True),
                      ('post_isolation_motor_force_N_per_car_hypothesis',1000.),('physical_accepted',True)]:
        bad=deepcopy(case);bad[key]=value;bad.pop('request_id');bad['request_id']=f.identity(bad)
        with pytest.raises(ValueError,match='exact bundle'):f.solve(bundle,bad)


def test_last_budgeted_step_at_observation_horizon_is_complete(bundle):
    case=f.request(bundle,name='exact-step-budget-boundary',initial_speed_m_s=0.,horizon_s=120.,dt_s=.005)
    r=f.solve(bundle,case)
    assert r['elapsed_s']==pytest.approx(120.,abs=1e-10)
    assert r['state']=='observation-horizon' and r['execution']=='completed-conditional-method'


def test_other_source_tree_cannot_attest_executing_brake_code(bundle,tmp_path):
    files={f.PRODUCER:open(f.__file__,'rb').read(),'engineering/station_rail/braking.py':b'# other brake code\n',
           'engineering/design_search/railway_bundle.py':b'# other bundle code\n'}
    for name,data in files.items():
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    with pytest.raises(ValueError,match='Executing'):f.evaluate(bundle,root=tmp_path)


def test_reverse_travel_from_later_forward_peak_is_distinct_from_fault_position(bundle):
    case=f.request(bundle,name='reversal-control',initial_speed_m_s=1.,grade_up_fraction=.02,
                   pressure_available_fraction=0.,horizon_s=10.)
    r=f.solve(bundle,case)
    assert r['maximum_position_m']>case['initial_position_m']
    assert r['maximum_rollback_from_reached_position_m']>r['maximum_reverse_displacement_m']
    assert r['cumulative_reverse_travel_m']==pytest.approx(r['maximum_rollback_from_reached_position_m'],abs=1e-8)
