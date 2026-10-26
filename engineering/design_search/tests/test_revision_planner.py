from copy import deepcopy
import pytest
from engineering.design_search import revision_planner as p

CID='1'*64;EID='2'*64


def diagnosis(**kw):
    return dict(candidate_id=CID,evaluation_id=EID,requirement_revision='BROAD-FUNCTION-1',execution='completed',
        numerical_validity='mesh_confirmed',failure_class='functional',domain='body',diagnosis='body-deflection',
        metric='maximum_vertical_displacement_m',**kw)


def test_provisional_target_generates_review_and_diverse_physical_experiments():
    e=diagnosis(criterion_kind='provisional-target',criterion_value_m=.0256,observed_m=.02801798)
    r=p.plan(CID,e)
    assert r['failure_class']=='advisory-target' and r['integrated_suitability']=='unknown'
    assert r['proposals'][0]['kind']=='criterion-review'
    assert r['proposals'][0]['actions'][0]['selected_value'] is None
    assert {'close-shell-loadpath','sandwich-and-oriented-faces','support-and-length-architecture'}<={x['strategy_id'] for x in r['proposals']}
    assert all(not x['hard_requirement_relaxation_allowed'] and not x['physical_improvement_claimed'] for x in r['proposals'])
    assert not r['convergence_to_working_solution_guaranteed']


def test_invalid_model_cannot_drive_physical_design_ranking_or_current_increase():
    e=diagnosis();e.update(domain='propulsion',diagnosis='steel model beyond declared field domain',failure_class='model-domain',numerical_validity='out-of-domain')
    r=p.plan(CID,e)
    assert len(r['proposals'])==1 and r['proposals'][0]['kind']=='evaluator-development'
    assert all(a['variable'].startswith('model.') for a in r['proposals'][0]['actions'])
    e.update(failure_class='functional',numerical_validity='nonconverged',diagnosis='unresolved lateral mechanism')
    r=p.plan(CID,e)
    assert r['failure_class']=='numerical' and r['proposals'][0]['strategy_id']=='repair-numerical-model'


def test_missing_evidence_requests_measurement_even_when_no_calculation_exists():
    e=diagnosis();e.update(failure_class='evidence-gap',execution='not-executed',numerical_validity='unknown')
    r=p.plan(CID,e)
    assert r['failure_class']=='evidence-gap'
    assert r['proposals'][0]['kind']=='measurement-and-data' and r['selected_candidate_id'] is None


def test_repeated_failed_local_mutations_escalate_to_loadpath_and_architecture():
    e=diagnosis();first=p.plan(CID,e);signature=first['failure_signature']
    history=[dict(candidate_id=str(i)*64,evaluation_id=str(i+1)*64,failure_signature=signature,
        strategy_id='redistribute-section-stock',improved=False) for i in (3,4)]
    r=p.plan(CID,e,history=history,maximum_proposals=8)
    ids={x['strategy_id'] for x in r['proposals']}
    assert r['stagnation_detected'] and 'redistribute-section-stock' not in ids
    assert 'close-shell-loadpath' in ids and 'route-power-and-formation' in ids
    assert any(a['variable']=='material.core_family' for x in r['proposals'] for a in x['actions'])


def test_materialization_source_and_coupled_recalculation_are_explicit():
    r=p.plan(CID,diagnosis());s=r['proposals'][0]
    assert s['parent_candidate_id']==CID and s['trigger_evaluation_id']==EID
    assert s['physical_candidate_id'] is None and s['materialization_status']=='not-generated'
    assert s['complete_installed_mass_kg'] is None and s['complete_cost_USD'] is None
    assert not s['native_dispatch_allowed'] and not r['physical_accepted']
    assert 'motor-thrust-and-braking' in s['required_re_evaluations'] and 'civil' in s['required_re_evaluations']
    assert r['plan_id']==p.variables.identity({n:v for n,v in r.items() if n!='plan_id'})
    e=diagnosis();e['observed_m']=.03
    assert p.plan(CID,e)['plan_id']!=r['plan_id']


def test_required_limits_cannot_be_relabelled_as_advisory_to_manufacture_a_pass():
    e=diagnosis(hard_requirement=True,criterion_kind='provisional-target')
    with pytest.raises(ValueError,match='mandatory requirement'):p.plan(CID,e)
    e=diagnosis();e['candidate_id']='3'*64
    with pytest.raises(ValueError,match='ancestry'):p.plan(CID,e)
    with pytest.raises(ValueError,match='bounded|twelve'):p.plan(CID,diagnosis(),maximum_proposals=0)
    with pytest.raises(ValueError,match='explicit progress'):p.plan(CID,diagnosis(),history=[dict(candidate_id=CID,evaluation_id=EID)])


def test_diagnostics_choose_coupled_domain_alternatives_without_acceptance():
    cases=[('propulsion','valid force shortfall','primary-secondary-topology'),('services','hot HVAC capacity','reduce-thermal-demand'),
        ('braking','wet rail stopping','brake-distribution'),('fitout','glazing and seat mass','body-stock-and-core'),
        ('civil','foundation erection','civil-system'),('operations','coast stall','route-power-and-formation'),
        ('accessibility','boarding interface unclear','resolve-coupled-interface-question')]
    for domain,reason,strategy in cases:
        e=diagnosis();e.update(domain=domain,diagnosis=reason,metric='declared-domain-response')
        r=p.plan(CID,e,maximum_proposals=3)
        assert strategy in {x['strategy_id'] for x in r['proposals']},domain
        assert all(x['expected_performance'] is None for x in r['proposals'])


def test_new_registered_variable_participates_without_rewriting_fixed_strategy_table():
    from engineering.design_search import design_variables as v
    d=v.descriptor('body.tapered_rib_geometry','body','record','mixed-record',effects=['geometry','buckling','assembly'],
        compatibility=['local buckling and joining'],dependencies=['material.primary_grade'],note='New taper requires a generator and independent model')
    registry=v.register(d);e=diagnosis(exploration_variable_ids=[d['id']])
    r=p.plan(CID,e,registry=registry,maximum_proposals=2)
    s=r['proposals'][0]
    assert s['kind']=='new-family-investigation' and s['actions'][0]['variable']==d['id']
    assert s['adapter_requirements'][0]['status']=='new-adapter-required' and not s['native_dispatch_allowed']
    assert 'buckling' in s['required_re_evaluations']
    e=diagnosis(exploration_variable_ids=['unregistered.physical.variable'])
    with pytest.raises(ValueError,match='registered exploration'):p.plan(CID,e)
