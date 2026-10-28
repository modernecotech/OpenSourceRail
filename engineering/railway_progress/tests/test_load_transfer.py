"""Independent sampled journey-to-24-axle civil load transfer checks."""
from copy import deepcopy
from math import fsum
import pytest
from engineering.reference_cell import vehicles
from engineering.reference_cell import bundle as vehicle_adapter
from engineering.railway_progress import alternatives,coordinator,journey,identity
from engineering.railway_progress import load_transfer as l


@pytest.fixture(scope='module')
def actual():
    v=vehicles.evaluate('V1');base=vehicle_adapter.materialize(v,1500.)
    alt=alternatives.evaluate(v,base,distance_m=1500.)
    b,c=coordinator.compose(v,1500.,alt)
    j=journey.evaluate(b,alt,context=journey.scenario(distance_m=1500.,dt_s=.25))
    assert j['trajectory']
    return v,b,c,alt,j


def seal(v,key='evaluation_id'):
    v[key]=identity({k:x for k,x in v.items() if k!=key});return v


def sample(actual):
    j=deepcopy(actual[4]);j['trajectory']=[next(s for s in j['trajectory'] if s['front_m']>50. and s['traction_N']>0)]
    return seal(j)


def test_actual_vehicle_journey_supplies24_axles_and_work_energy_remains_explicit(actual):
    v,b,c,a,j=actual
    assert len(b['route_axle_offsets_from_leading_nose_m'])==24
    assert abs(j['discrete_work_kinetic_residual_J'])<1e-4*max(1.,j['energy_J']['traction'])
    r=l.evaluate(b,c,a,[dict(name='actual-normal',result=j)])
    assert r['candidate_id']==b['candidate_id'] and r['alternative_candidate_id']==a['candidate_id']
    assert r['sampled_states']>0 and r['maximum_vertical_balance_residual_N']<1e-6
    assert not r['actual_wheel_rail_dynamics_validated'] and r['qualified_span_capacity_Nm'] is None
    assert r['qualified_foundation_pressure_Pa'] is None and not r['physical_accepted']


def test_single_sample_global_force_and_first_moment_match_actual_wheel_positions(actual):
    v,b,c,a,_=actual;j=sample(actual);r=l.evaluate(b,c,a,[dict(name='one-state',result=j)],dynamic_factor=1.)
    weight=j['translating_train_mass_kg']*9.80665;front=j['trajectory'][0]['front_m']
    assert fsum(r['sampled_live_support_envelope_N'])==pytest.approx(weight)
    expected=fsum(weight/24*(front-o['offset_behind_leading_nose_m']) for o in b['route_axle_offsets_from_leading_nose_m'])
    assert fsum(F*x for F,x in zip(r['sampled_live_support_envelope_N'],r['support_positions_m']))==pytest.approx(expected)
    assert r['sampled_known_dead_plus_live_envelope_N']==pytest.approx([d+F for d,F in zip(c['guideway_known_support_reactions_N'],r['sampled_live_support_envelope_N'])])


def test_counted_rotational_equivalent_is_not_added_to_gravitational_axle_weight(actual):
    v,b,c,a,_=actual;j=sample(actual);larger=deepcopy(j);larger['effective_mass_kg']*=10;larger['counted_rotor_equivalent_mass_kg']*=10;seal(larger)
    one=l.evaluate(b,c,a,[dict(name='normal',result=j)],dynamic_factor=1.)
    two=l.evaluate(b,c,a,[dict(name='rotor-field-perturbation',result=larger)],dynamic_factor=1.)
    assert one['sampled_live_support_envelope_N']==two['sampled_live_support_envelope_N']
    assert fsum(two['sampled_live_support_envelope_N'])==pytest.approx(j['translating_train_mass_kg']*9.80665)


def test_traction_longitudinal_reactions_follow_engaged_station_contacts_not_nose_or_all_beams(actual):
    v,b,c,a,_=actual;j=sample(actual);s=j['trajectory'][0]
    r=l.evaluate(b,c,a,[dict(name='powered',result=j)],dynamic_factor=1.)
    assert s['brake_N']==0 and s['traction_N']>0
    assert fsum(r['sampled_longitudinal_force_envelope_N'])==pytest.approx(s['traction_N'])
    loaded=[x for x,F in zip(r['support_positions_m'],r['sampled_longitudinal_force_envelope_N']) if F>0]
    assert loaded and max(loaded)<500.
    assert any(x!=pytest.approx(s['front_m']) for x in loaded)


def test_actual_failed_initial_bank_is_retained_as_empty_trajectory_failure(actual):
    v,b,c,a,_=actual
    failed=journey.evaluate(b,a,context=journey.scenario(distance_m=1500.,failed_banks=[0],dt_s=.25))
    assert failed['execution']=='stalled' and not failed['trajectory']
    r=l.evaluate(b,c,a,[dict(name='bank0-failed',result=failed)])
    assert len(r['scenarios'])==1
    assert r['scenarios'][0]['journey_evaluation_id']==failed['evaluation_id']
    assert not r['scenarios'][0]['complete_trajectory_load_coverage']
    assert r['sampled_states']==0


def test_out_of_generated_guideway_sample_is_retained_as_domain_failure_not_crash_or_clamp(actual):
    v,b,c,a,_=actual;j=sample(actual);j['trajectory'][0]['front_m']=-1000.;seal(j)
    r=l.evaluate(b,c,a,[dict(name='outside-model-domain',result=j)])
    assert r['out_of_generated_guideway_states']==1 and r['sampled_states']==0
    assert len(r['scenarios'])==1 and not r['scenarios'][0]['complete_trajectory_load_coverage']
    assert r['scenarios'][0]['out_of_generated_guideway_states']==1


@pytest.mark.parametrize('target',['bundle','civil','alternative','journey'])
def test_resealed_mixed_configuration_is_rejected_before_load_transfer(actual,target):
    v,b,c,a,_=actual;b,c,a=deepcopy(b),deepcopy(c),deepcopy(a);j=sample(actual)
    if target=='bundle':b['candidate_id']='f'*64;seal(b,'definition_id')
    elif target=='civil':c['candidate_id']='f'*64;seal(c)
    elif target=='alternative':a['candidate_id']='f'*64;seal(a)
    else:j['candidate_id']='f'*64;seal(j)
    with pytest.raises(ValueError):l.evaluate(b,c,a,[dict(name='mixed',result=j)])


def test_source_epoch_and_sampled_not_continuous_scope_are_visible(actual):
    v,b,c,a,j=actual;r=l.evaluate(b,c,a,[dict(name='normal',result=j)])
    assert len(r['source_sha256']['engineering/railway_progress/load_transfer.py'])==64
    assert 'sampled' in ' '.join(r['limitations']).lower()
    for bad in (0.,2.1,float('nan'),True):
        with pytest.raises(ValueError):l.evaluate(b,c,a,[],dynamic_factor=bad)
