"""Independent scope/admission controls, including the retained28.018mm case."""
from copy import deepcopy
import pytest
from engineering.design_search import requirement_policy as p

CID='1'*64
REQ='REQUIREMENTS-EXAMPLE-1'


def basis(limit=.003):
    return dict(candidate_id=CID,basis_kind='approved-interface-limit',
        observable='maximum_interface_displacement_m',unit='m',operator='max',limit=limit,
        review_disposition='supported-for-declared-scope',source_sha256='2'*64,
        review_record_id='3'*64,source_uri='repo:example-supported-interface',source_locator='test fixture section1')


def observation(value,observable='maximum_interface_displacement_m',unit='m'):
    # Declared evidence envelope for contract testing; not railway evidence.
    return dict(value=value,unit=unit,observable=observable,candidate_id=CID,requirement_revision=REQ,
        execution='completed',numerical_validity='converged',model_domain='supported',evidence_kind='verified-simulation',
        evidence_id='4'*64,evaluation_id='5'*64,independent_review_id='6'*64,source_sha256={'fixture-model':'7'*64})


def physical_criterion(limit=.003):
    r=deepcopy(p.catalogue()['criteria']['physical.clearance']);r['limit']=limit;r['provenance']=basis(limit)
    return {'physical.clearance':r}


def finding(result,uid):return next(r for r in result['findings'] if r['criterion_id']==uid)


def test_catalogue_separates_obligations_preferences_assumptions_and_model_domains():
    c=p.catalogue();assert {r['category'] for r in c['criteria'].values()}==set(p.CATEGORIES)
    assert c['criteria']['target.global_deflection']['category']=='project_preference'
    assert c['criteria']['physical.clearance']['limit'] is None
    assert c['criteria']['physical.temperature']['limit'] is None
    assert c['criteria']['model.linear_steel']['limit']==1.3
    assert not c['unknown_is_zero'] and c['historical_evaluations_are_immutable']
    assert c['policy_id']==p.identity({k:v for k,v in c.items() if k!='policy_id'})
    assert len(c['source_sha256'][p.PRODUCER])==64
    assert c['example_references'][0]['applicability'].startswith('unassessed')


def test_retained_28mm_result_exceeds_advisory_target_without_universal_failure():
    r=p.assess({'body_vertical_displacement_m':.02801798},candidate_id=CID,requirement_revision=REQ)
    f=finding(r,'target.global_deflection')
    assert f['status']=='target_exceeded' and f['value']==.02801798 and f['limit']==.0256
    assert f['hard_screen_failed'] is False
    assert r['declared_hard_screen']=='unknown' and r['integrated_suitability']=='unknown'
    assert r['complete_installed_mass_kg'] is None and r['complete_installed_cost_USD'] is None


def test_relaxing_project_target_cannot_create_physical_acceptance_or_new_hardware():
    old=p.catalogue()['criteria'];new=deepcopy(old);new['target.global_deflection']['limit']=.04
    report=p.review_proposal(old,new,candidate_id=CID,rationale='Investigate actual clearance and ride consequences')
    assert report['disposition']=='requires-new-evaluation-and-review'
    assert report['previous_requirement_revision']!=report['proposed_requirement_revision']
    assert report['physical_candidate_id_unchanged'] and report['candidate_id']==CID
    r=p.assess({'body_vertical_displacement_m':.02801798},new,candidate_id=CID)
    assert finding(r,'target.global_deflection')['status']=='target_met'
    assert r['integrated_suitability']=='unknown' and not r['physical_accepted']
    assert not report['automatic_acceptance'] and not report['historical_results_mutated']


def test_supported_hard_interface_violation_remains_a_real_declared_failure():
    a=p.assess({'maximum_interface_displacement_m':observation(.004)},physical_criterion(),candidate_id=CID,requirement_revision=REQ)
    f=finding(a,'physical.clearance')
    assert f['status']=='supported_limit_violated' and f['hard_screen_failed']
    assert a['declared_hard_screen']=='fail'
    assert a['integrated_suitability']=='incompatible_with_declared_supported_limit'
    b=p.assess({'maximum_interface_displacement_m':observation(.002)},physical_criterion(),candidate_id=CID,requirement_revision=REQ)
    assert finding(b,'physical.clearance')['status']=='supported_screen_satisfied'
    assert b['integrated_suitability']=='unknown'  # one screen is not a railway


def test_missing_typical_or_unreviewed_basis_does_not_become_a_physical_limit():
    for change in ({'provenance':None},{'provenance':{**basis(),'basis_kind':'supplier-typical-data'}},
                   {'provenance':{**basis(),'review_record_id':None}}, {'limit':None}):
        criteria=physical_criterion();criteria['physical.clearance'].update(change)
        r=p.assess({'maximum_interface_displacement_m':observation(.004)},criteria,candidate_id=CID,requirement_revision=REQ)
        assert finding(r,'physical.clearance')['status']=='unknown'
        assert r['declared_hard_screen']=='unknown'
    criteria=physical_criterion()
    assert finding(p.assess({'maximum_interface_displacement_m':.002},criteria,candidate_id=CID),'physical.clearance')['status']=='unknown'


def test_nonconverged_tool_error_and_out_of_domain_evidence_cannot_pass_hard_screens():
    for change in ({'numerical_validity':'nonconverged'},{'execution':'tool_error'},{'model_domain':'outside'},
                   {'independent_review_id':None},{'source_sha256':{}},{'observable':'another quantity'}):
        row={**observation(.002),**change}
        r=p.assess({'physical.clearance':row},physical_criterion(),candidate_id=CID,requirement_revision=REQ)
        assert finding(r,'physical.clearance')['status']=='unknown'
        assert r['integrated_suitability']=='unknown'


def test_units_and_unknown_quantities_are_never_silently_converted_to_zero():
    r=p.assess({'physical.clearance':{**observation(2),'unit':'mm'}},physical_criterion(),candidate_id=CID,requirement_revision=REQ)
    assert finding(r,'physical.clearance')['status']=='unknown'
    assert finding(r,'physical.clearance')['value']==2
    missing=p.assess({})
    assert all(f['status']=='unknown' and f['value'] is None for f in missing['findings'])
    with pytest.raises(ValueError):p.assess({'body_vertical_displacement_m':float('nan')})
    with pytest.raises(ValueError):p.assess({'physical.clearance':observation(float('inf'))})


def test_numerical_domain_violation_does_not_become_physical_material_failure():
    r=p.assess({'maximum_linear_model_steel_B_T':2.24},candidate_id=CID)
    f=finding(r,'model.linear_steel')
    assert f['status']=='outside_model_domain' and not f['hard_screen_failed']
    assert r['integrated_suitability']=='unknown' and not r['numerical_model_admitted']
    old=p.catalogue()['criteria'];bad=deepcopy(old);bad['model.linear_steel']['limit']=2.3
    review=p.review_proposal(old,bad,candidate_id=CID,rationale='Higher force wanted')
    assert review['disposition']=='blocked-unsupported-revision'
    with pytest.raises(ValueError,match='cannot be enlarged'):p.assess({},bad)
    new=deepcopy(bad);new['model.linear_steel']['model_id']='new-nonlinear-moving-model/1'
    review=p.review_proposal(old,new,candidate_id=CID,rationale='Develop and benchmark a different model')
    assert review['disposition']=='requires-new-evaluation-and-review'
    assert any(t['kind']=='new-model-validation' for t in review['next_tasks'])
    assert not review['physical_generation_performed']


def test_safety_obligations_cannot_be_removed_demoted_or_arbitrarily_relaxed():
    old=p.catalogue()['criteria']
    new=deepcopy(old);new.pop('safety.independent_stop')
    assert p.review_proposal(old,new,candidate_id=CID,rationale='Simplify')['disposition']=='blocked-unsupported-revision'
    old=physical_criterion();new=deepcopy(old);new['physical.clearance'].update(limit=.01,provenance=None)
    assert p.review_proposal(old,new,candidate_id=CID,rationale='Need a lighter body')['disposition']=='blocked-unsupported-revision'
    new=deepcopy(old);new['physical.clearance']['limit']=.01
    assert p.review_proposal(old,new,candidate_id=CID,rationale='Reuse original approval')['disposition']=='blocked-unsupported-revision'
    new=deepcopy(old);new['physical.clearance']['category']='project_preference'
    assert p.review_proposal(old,new,candidate_id=CID,rationale='Change role')['disposition']=='blocked-unsupported-revision'
    old=p.catalogue()['criteria'];new=deepcopy(old);new['physical.clearance']['limit']=.0256
    assert p.review_proposal(old,new,candidate_id=CID,rationale='Reuse old target')['disposition']=='blocked-unsupported-revision'
    new=deepcopy(old);new['target.global_deflection']['category']='mandatory_obligation'
    assert p.review_proposal(old,new,candidate_id=CID,rationale='Promote target to hard rule')['disposition']=='blocked-unsupported-revision'


def test_mixed_identities_are_rejected_and_policy_evaluation_does_not_rewrite_inputs():
    values={'physical.clearance':observation(.002)};criteria=physical_criterion();saved=deepcopy((values,criteria))
    a=p.assess(values,criteria,candidate_id=CID,requirement_revision=REQ)
    assert (values,criteria)==saved and a['candidate_id']==CID
    assert a['evaluation_id']!=CID and a['selection_id'] is None
    with pytest.raises(ValueError,match='Mixed'):p.assess(values,criteria,candidate_id='a'*64,requirement_revision=REQ)
    with pytest.raises(ValueError,match='Mixed'):p.assess(values,criteria,candidate_id=CID,requirement_revision='OTHER')
    for result in (a,p.review_proposal(criteria,criteria,candidate_id=CID)):
        assert all(result[k] is False for k in p.FLAGS)
        assert result['historical_results_mutated'] is False
