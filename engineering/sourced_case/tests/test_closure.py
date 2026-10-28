"""Recorded evidence coverage cannot be self-signed into engineering completion."""
from copy import deepcopy
import pytest
from engineering.sourced_case import closure as x,coordinator as c,identity,FLAGS
from engineering.sourced_case.tests.test_coordinator import campaign,state


def test_actual_saved_case_produces_all_phases_and_WPs_without_completion(state):
    r=x.build(state)
    assert r['counts']['saved_cases']==1 and r['counts']['conditional_journeys']==1
    assert r['counts']['conditional_arrivals']==1
    assert {p['phase_id'] for p in r['phases']}=={'P'+str(n) for n in range(10)}
    assert {p['work_package'] for p in r['work_packages']}=={'WP'+str(n) for n in range(1,7)}
    assert all(p['completion'] is None and not p['physical_qualification'] for p in r['phases'])
    assert r['design_complete_percentage'] is None
    assert r['counts']['external_physical_record_availability'] is None
    assert r['counts']['provided_authenticated_physical_records']==0
    assert r['counts']['complete_whole_life_cost_USD'] is None
    assert r['vehicles'][0]['bounded_purchased_occurrences']>0
    assert r['vehicles'][0]['installed_mass_kg'] is None
    assert r['journeys'][0]['numerical_validity'].startswith('arithmetic-checked')
    assert all(r[k] is False for k in FLAGS)
    assert r['evaluation_id']==identity({k:v for k,v in r.items() if k!='evaluation_id'})


def test_real_component_change_invalidates_all_connected_domains(state):
    r=x.build(state);g=r['dependency_graph'];n=next(n for n in g['nodes'] if n['kind']=='component')
    change=dict(node_id=n['node_id'],old_revision_id=n['revision_id'],new_revision_id='f'*64,change_kind='physical')
    out=x.invalidate(g,[change])
    assert {'geometry','mass-CG-inertia','structure','drive-electrothermal','civil-loads','civil-geometry','BOM','manufacturing','procurement','cost','control','service','city','publication'}<=set(out['invalidated_kinds'])
    assert out['physical_candidate_revision_required'] and not out['cached_outputs_reusable']
    assert not out['automatic_selection_allowed']


def test_evaluator_change_invalidates_dependents_without_new_physical_candidate(state):
    g=x.build(state)['dependency_graph'];n=next(n for n in g['nodes'] if n['kind']=='structure')
    out=x.invalidate(g,[dict(node_id=n['node_id'],old_revision_id=n['revision_id'],new_revision_id='f'*64,change_kind='evaluator')])
    assert not out['physical_candidate_revision_required'] and out['evaluations_must_be_recomputed']
    assert {'civil-loads','civil-geometry','cost','city','publication'}<=set(out['invalidated_kinds'])


def test_unknown_cached_revision_and_graph_forgery_cannot_hide_invalidation(state):
    g=x.build(state)['dependency_graph'];n=g['nodes'][0]
    with pytest.raises(ValueError):x.invalidate(g,[dict(node_id=n['node_id'],old_revision_id='f'*64,new_revision_id='e'*64,change_kind='physical')])
    g['edges']=[]
    with pytest.raises(ValueError):x.invalidate(g,[])


def test_manufacturing_exports_are_disabled_drafts_not_production(state):
    r=x.build(state);m=r['manufacturing_exports'][0]
    assert m['research_draft_export_allowed'] and m['export_status']=='disabled-review-drafts-only'
    assert not m['ERPNext_submission_allowed'] and not m['production_release']
    assert m['qualified_cycles'] is None and m['complete_installed_cost_USD'] is None
    latest=c.read(state/'latest.json');case=c.read(state/latest['cases'][0]['path'])
    case['manufacturing']['ERPNext_drafts']['submission_allowed']=True
    p=case['manufacturing'];p['evaluation_id']=identity({k:v for k,v in p.items() if k!='evaluation_id'})
    result=x.manufacturing_status(case)
    assert not result['research_draft_export_allowed'] and result['export_status'].startswith('held')


def test_modified_or_mixed_saved_case_is_not_a_dashboard_input(state):
    latest=c.read(state/'latest.json');row=latest['cases'][0];case=c.read(state/row['path'])
    case['body_candidate_id']='f'*64;case['evaluation_id']=identity({k:v for k,v in case.items() if k!='evaluation_id'})
    row['evaluation_id']=case['evaluation_id'];latest['run_id']=identity({k:v for k,v in latest.items() if k!='run_id'})
    c.write(state/row['path'],case);c.write(state/'latest.json',latest)
    with pytest.raises(ValueError):x.build(state)


def test_native_boolean_is_not_an_authenticated_native_package(state):
    with pytest.raises(ValueError):x.build(state,native=[dict(kind='whole-body',path='missing',verified=True)])


def test_unknown_files_links_and_source_archive_tamper_are_refused(state):
    (state/'unexpected.json').write_text('{}')
    with pytest.raises(ValueError):x.build(state)
    (state/'unexpected.json').unlink();p=state/'input-sources.tar.gz';p.write_bytes(b'not-an-archive')
    with pytest.raises(Exception):x.build(state)


def test_charging_proposal_stays_separate_from_integrated_candidate_completion(state):
    latest=c.read(state/'latest.json');row=latest['cases'][0];value=c.read(state/row['path']);cid=value['candidate_id']
    value['charging_proposal']=dict(proposal_id='f'*64,physical_accepted=False,existing_converters=3,required_converters=8,hot_supply_derating=None)
    value['evaluation_id']=identity({k:v for k,v in value.items() if k!='evaluation_id'});row['evaluation_id']=value['evaluation_id']
    latest['run_id']=identity({k:v for k,v in latest.items() if k!='run_id'});c.write(state/row['path'],value);c.write(state/'latest.json',latest)
    r=x.build(state);proposal=r['unintegrated_research_proposals'][0]
    assert proposal['integrated_case_candidate_id']==cid and not proposal['included_in_integrated_candidate']
    assert proposal['proposal']['existing_converters']==3 and proposal['proposal']['required_converters']==8
    assert r['counts']['complete_installed_cost_USD'] is None and all(r[k] is False for k in FLAGS)


def test_foreign_declared_producer_bytes_cannot_identify_executing_dashboard(state,tmp_path):
    root=tmp_path/'foreign';p=root/x.CODE;p.parent.mkdir(parents=True);p.write_text('different producer')
    with pytest.raises(ValueError):x.build(state,root=root)
