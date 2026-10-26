"""Cross-domain physical identity, accounting and automatic revision controls."""
from copy import deepcopy
import pytest
from engineering.design_search import wheel_families as f,contracts as k,wheel_brakes

@pytest.fixture(scope='module')
def candidates():return f.initial_families('V06-INTEGRATION-TEST')

def test_stock_identity_mass_fin_neck_and_static_axles(candidates):
    for c in candidates:
        v=f.materialize(c);assert v['candidate_id']==c['candidate_id']
        assert k.mass_properties(c)['known_mass_subtotal_kg']==pytest.approx(v['mass']['accounted_tare_kg_per_car'])
        parts={p['id']:p for p in v['geometry_parts']};fin=parts['station-secondary/active-fin'];neck=parts['station-secondary/upper-neck']
        assert fin['at_m'][2]+fin['size_m'][2]==pytest.approx(neck['at_m'][2])
        assert neck['at_m'][2]+neck['size_m'][2]==pytest.approx(.34)
        assert v['propulsion']['active_fin_aluminium_mass_kg']==pytest.approx(fin['mass_kg'])
        assert v['axle_loads']['normal_kg_per_axle']==pytest.approx(v['mass']['accounted_cap_loaded_kg_per_car']/4)
        assert not k.inventory_summary(c)['complete_installed_distribution']


def test_failure_generates_counted_child_and_display_name_is_not_physics(candidates):
    parent=candidates[0]
    request=k.make_evaluation_request(parent,evaluator_id='wheel-body',evaluator_sources={'test.py':'a'*64})
    result=k.make_result(request,execution_status='executed',numerical_status='converged',screen_status='fail',
        diagnostics=[dict(native=dict(metrics=dict(normal_deflection_m=.11)))])
    child=f.propose_revision(parent,[result],trial_index=0)
    assert child['candidate_id']!=parent['candidate_id'] and child['lineage']['parent_candidate_ids']==[parent['candidate_id']]
    assert child['architecture']['wheel_parameters']['body']['sill_depth_m']>.35
    v=f.materialize(child)
    assert sum(r['mass_kg'] for r in v['inventory'])==pytest.approx(v['mass']['accounted_tare_kg_per_car'])
    p=f._parameters(parent);p['motor']['physical']['name']='cosmetic rename'
    renamed=f.make(p,requirement_revision=parent['requirement_revision'],label='Different display label')
    assert renamed['candidate_id']==parent['candidate_id']


def test_altered_physical_part_cannot_use_unchanged_materialization(candidates):
    changed=deepcopy(candidates[0]);g=next(x for x in changed['geometry'] if x.get('kind')=='box')
    g['native_part']['size_m'][0]*=1.01
    with pytest.raises(ValueError):f.materialize(changed)


def test_invalid_body_displacement_requests_model_work_without_a_physical_mutation(candidates):
    parent=candidates[0]
    request=k.make_evaluation_request(parent,evaluator_id='wheel-body',evaluator_sources={'test.py':'a'*64})
    invalid=k.make_result(request,execution_status='executed',numerical_status='invalid',screen_status='fail',diagnostics=[dict(native=dict(metrics=dict(normal_deflection_m=1e9)))])
    assert f.propose_revision(parent,[invalid],trial_index=0) is None
