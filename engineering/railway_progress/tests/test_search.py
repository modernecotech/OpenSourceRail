"""Actual bounded hardware revisions select experiments, never a railway."""
from copy import deepcopy
import pytest

from engineering.reference_cell import vehicles,bundle
from engineering.railway_progress import search,alternatives,FLAGS,identity


@pytest.fixture(scope='module')
def inputs():
    vehicle=vehicles.evaluate('V1');base=bundle.materialize(vehicle,2000.)
    return vehicle,base


@pytest.fixture(scope='module')
def result(inputs):
    return search.run(*inputs)


def test_twelve_actual_counts_locations_and_hardware_identities_are_distinct(inputs,result):
    vehicle,base=inputs;rows=result['trials']
    assert len(rows)==result['trial_budget']==12
    assert {(r['banks'],r['roller_pairs_per_bank']) for r in rows}=={(n,p) for n in (3,5,7) for p in (1,2,3,4)}
    assert len({r['candidate_id'] for r in rows})==12
    assert len({r['evaluation_id'] for r in rows})==12
    assert result['body_candidate_id']==vehicle['candidate_id']
    assert all(r['installed_motors']==r['banks']*2*r['roller_pairs_per_bank'] for r in rows)
    assert all(r['source_published_motor_mass_kg']==r['installed_motors']*2010. for r in rows)
    assert all(r['parent_candidate_id']==result['parent_candidate_id'] for r in rows)


def test_baseline_is_reused_instead_of_becoming_a_fictitious_noop_revision(inputs,result):
    parent=alternatives.evaluate(*inputs,kind='station-pinch-rollers',distance_m=2000.)
    baseline=next(r for r in result['trials'] if (r['banks'],r['roller_pairs_per_bank'])==(5,4))
    assert baseline['candidate_id']==parent['candidate_id']==result['parent_candidate_id']
    assert baseline['evaluation_id']==parent['evaluation_id']
    with pytest.raises(ValueError,match='actually change'):alternatives.revise(inputs[0],parent,dict(roller_pairs_per_bank=4),inputs[1])


def test_frontier_only_contains_supported_necessary_bound_experiments(result):
    supported={r['candidate_id'] for r in result['trials'] if r['necessary_force_screen_passed']}
    assert set(result['next_experiment_frontier'])<=supported
    assert result['qualified_integrated_frontier']==[] and result['integrated_winner'] is None
    assert result['native_solves']==0
    assert all(r['complete_installed_cost_usd'] is None and r['unknown_mass_items'] for r in result['trials'])
    assert all(result[k] is False for k in FLAGS)
    assert result['evaluation_id']==identity({k:v for k,v in result.items() if k!='evaluation_id'})
    for row in result['trials']:
        if row['minimum_active_pairs']==0 or row['exact_geometric_contact_m']<500.-1e-8:
            assert not row['necessary_force_screen_passed']
        assert row['necessary_force_screen_passed']==(row['sampled_force_lower_cap_at20_N']>=row['normal_required_force_at20_N'])


@pytest.mark.parametrize('changes',[
    dict(roller_pairs_per_bank=-1),dict(motor_count=7),dict(roller_wall_m=.25),
    dict(bank_starts_m=[0.,0.]),dict(clamp_design_pressure_Pa=-1.),dict(not_a_hardware_variable=1),
])
def test_invalid_hardware_is_not_an_automatic_redesign(inputs,changes):
    vehicle,base=inputs;parent=alternatives.evaluate(vehicle,base)
    with pytest.raises(ValueError):alternatives.revise(vehicle,parent,changes,base)


def test_resealed_wrong_body_cannot_inherit_the_previous_physical_design(inputs):
    vehicle,base=inputs;parent=alternatives.evaluate(vehicle,base)
    other=deepcopy(parent);other['body_candidate_id']='f'*64
    other['evaluation_id']=identity({k:v for k,v in other.items() if k!='evaluation_id'})
    with pytest.raises(ValueError):alternatives.revise(vehicle,other,dict(motor_count=10,roller_pairs_per_bank=5),base)
