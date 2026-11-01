"""Published native evidence is usable without dispatching local solvers."""
import json
import gzip
import shutil
import pytest
from engineering.station_rail import ROOT
from engineering.design_search import railway_publication as publication


def test_coordinated_publication_retains_execution_and_unknowns():
    result = publication.verify()
    assert result['body_count'] == 14
    assert result['evaluated_bundle_count'] == 112
    assert result['native_body_case_count'] == 9
    assert result['physical_journeys'] == result['complete_installed_masses'] == 0
    assert result['physical_accepted'] is False
    summary=json.loads((ROOT/publication.OUTPUT/'summary.json').read_bytes())
    completion=summary['completion_status']
    assert completion['simulation_complete']==112
    assert completion['integrated_force_driven_journey_complete']==0
    assert completion['engineering_validated']==0
    assert completion['approved_for_manufacture_or_operation']==0
    assert summary['current_source_refinement']['execution']=='completed'
    assert summary['current_source_refinement']['numerical_validity']=='equilibrium_energy_confirmed_only'
    assert summary['current_source_refinement']['physical_and_engineering_acceptance'] is False
    assert summary['current_source_fine_refinement']['mesh_m']==0.10625
    assert summary['current_source_fine_refinement']['reconciliation_state']=='reconciled-from-immutable-native-result'
    assert summary['current_source_fine_refinement']['physical_and_engineering_acceptance'] is False
    assert summary['frontier_tasks']==46
    frontier=json.loads(gzip.decompress((ROOT/publication.OUTPUT/'frontier.json.gz').read_bytes()))
    continuation=next(x for x in frontier if x['kind']=='unresolved-numerical-refinement'
        and x['body_candidate_id']=='8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b')
    assert continuation['proposed_next_mesh_m']==0.053125
    assert continuation['computational_cell_estimate']['solid_cells']==290660


def _declared_cost_row():
    candidate_id='c'*64
    scopes=set(publication.engine.model_cost.SCOPES)
    estimate=dict(candidate_id=candidate_id,model_cost_complete_for_declared_case=True,
        model_cost_missing_scopes=[],required_cost_scopes=sorted(scopes),
        scope_totals_iqd={scope:[1,2,3] for scope in scopes},assumption_id='a'*64,
        source_sha256={'rates.json':'b'*64},cost_line_items=[dict(candidate_id=candidate_id,
            scope=scope,source_ids=['a'*64],calculation_basis='explicit Class C assumption',
            scenario_iqd=dict(low=1,base=2,high=3)) for scope in sorted(scopes)])
    return dict(candidate_id=candidate_id,economics=dict(model_cost=estimate),physical_journey_completed=False)


def test_completion_levels_mark_assumption_based_cost_simulation_without_validation_or_release():
    status=publication.completion_summary([_declared_cost_row()])
    assert status['simulation_complete']==1
    assert status['integrated_force_driven_journey_complete']==0
    assert status['engineering_validated']==0
    assert status['approved_for_manufacture_or_operation']==0
    record=status['candidate_states'][0]
    assert record['assumption_id']=='a'*64
    assert 'cost scenario only' in status['simulation_scope']


def test_unattributed_cost_line_cannot_complete_the_simulation():
    row=_declared_cost_row()
    row['economics']['model_cost']['cost_line_items'][0]['source_ids']=[]
    status=publication.completion_summary([row])
    assert status['simulation_complete']==0
    assert status['engineering_validated']==0
    assert status['approved_for_manufacture_or_operation']==0


def test_publication_payload_cannot_promote_an_unqualified_winner(tmp_path):
    out = tmp_path / 'packet'
    shutil.copytree(ROOT / publication.OUTPUT, out)
    path = out / 'summary.json'
    summary = json.loads(path.read_bytes())
    summary['integrated_selection'] = 'invented-winner'
    path.write_text(json.dumps(summary))
    with pytest.raises(ValueError, match='payload changed'):
        publication.verify(output=out)


def test_publishing_current_evidence_does_not_rerun_campaign(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError('Publication refresh must not launch a campaign or solver')
    monkeypatch.setattr(publication.engine, 'run', refused)
    execution=json.loads((ROOT/publication.OUTPUT/'execution.json').read_bytes())
    current_result=dict(contract_id=execution['contract_id'],run_id=execution['run_id'],
                        campaign_id=execution['campaign_id'])
    # The immutable publication is present in a clean checkout, while its
    # ignored working-state cache is deliberately not. Supply the matching
    # execution receipt so this test exercises publication reuse without
    # depending on a developer's private build directory.
    monkeypatch.setattr(publication,'current',lambda root:(ROOT/'build/coupled-railway',current_result))
    assert publication.build()['verified']


def _refinement_frontier(candidate_id, mesh_m):
    return dict(kind='unresolved-numerical-refinement',body_candidate_id=candidate_id,
        proposed_next_mesh_m=mesh_m,state='implementation-or-resource-work-required')


def test_unrequested_current_refinement_is_ignored_and_stale_package_is_preserved(tmp_path, monkeypatch):
    from engineering.design_search import railway_refinement_current as current_refinement
    from engineering.design_search import railway_refinement_current_verifier as verifier
    stale=tmp_path/'build/coupled-railway/refinements'/current_refinement.CANDIDATE_ID/'old-request'
    stale.mkdir(parents=True)
    (stale/'request.json').write_text('{"stale":true}')
    monkeypatch.setattr(current_refinement,'_context',lambda *a,**k:pytest.fail('unrequested stale package must not be resolved'))
    monkeypatch.setattr(verifier,'verify',
        lambda *a,**k:pytest.fail('unrequested stale package must not be verified'))
    value=dict(contract_id='current-contract',frontier=[_refinement_frontier('d'*64,0.2125)])
    assert publication._current_refinement(tmp_path,value) is None
    assert (stale/'request.json').read_text()=='{"stale":true}'


def test_unrequested_fine_refinement_is_ignored_despite_stale_receipts(tmp_path, monkeypatch):
    from engineering.design_search import railway_refinement_current_fine_reconcile as reconciler
    stale=tmp_path/'build/coupled-railway/reconciliations'/reconciler.CANDIDATE_ID/'old-request'
    stale.mkdir(parents=True)
    (stale/'manifest.json').write_text('{}')
    (stale/'request.json').write_text('{"stale":true}')
    monkeypatch.setattr(reconciler,'verify',lambda *a,**k:pytest.fail('unrequested stale receipt must not be verified'))
    value=dict(contract_id='current-contract',campaign_id='campaign',run_id='run',frontier=[])
    assert publication._current_fine_refinement(tmp_path,value) is None
    assert (stale/'manifest.json').read_text()=='{}'


def test_exact_current_refinement_request_is_retained_only_after_verification(tmp_path, monkeypatch):
    from engineering.design_search import railway_refinement_current as current_refinement
    from engineering.design_search import railway_refinement_current_verifier as verifier
    candidate=current_refinement.CANDIDATE_ID
    task=_refinement_frontier(candidate,current_refinement.NEXT_MESH_M)
    value=dict(contract_id='current-contract',frontier=[task])
    parent=tmp_path/'build/coupled-railway/current-contract/result.json'
    package=tmp_path/'exact-current-refinement'
    package.mkdir(parents=True)
    payloads={'request.json':{'request_id':'request'},'native/result.json':{'evaluation_id':'evaluation'},
        'report.json':{'body_candidate_id':candidate},'manifest.json':{'manifest_id':'manifest'}}
    for name,payload in payloads.items():
        path=package/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(payload))
    context=(tmp_path,parent,{},dict(candidate_id=candidate),{},task,[], 'parent-sha')
    monkeypatch.setattr(current_refinement,'_context',lambda *a,**k:context)
    monkeypatch.setattr(current_refinement,'_request',lambda *a,**k:payloads['request.json'])
    monkeypatch.setattr(current_refinement,'_package',lambda *a,**k:package)
    checked=[]
    monkeypatch.setattr(verifier,'verify',lambda *a,**k:checked.append(k) or {'verified':True})
    result=publication._current_refinement(tmp_path,value)
    assert result['verified']=={'verified':True}
    assert result['request']==payloads['request.json']
    assert checked==[dict(parent_result=parent,candidate_id=candidate)]


def test_exact_fine_request_is_selected_and_verified_among_stale_receipts(tmp_path, monkeypatch):
    from engineering.design_search import railway_refinement_current_fine_reconcile as reconciler
    from engineering.station_rail.common import digest, identity
    candidate=reconciler.CANDIDATE_ID
    from engineering.design_search import railway_refinement_current as current_refinement
    task=_refinement_frontier(candidate,current_refinement.NEXT_MESH_M)
    parent=tmp_path/'build/coupled-railway/current-contract/result.json'
    parent.parent.mkdir(parents=True)
    parent.write_text(json.dumps({'source_bound_parent':'exact'}))
    value=dict(contract_id='current-contract',campaign_id='campaign',run_id='run',frontier=[task])
    stale=tmp_path/'build/coupled-railway/reconciliations'/candidate/'stale-request'
    stale.mkdir(parents=True)
    (stale/'manifest.json').write_text('{}')
    (stale/'request.json').write_text(json.dumps(dict(schema='old',body_candidate_id=candidate)))
    request=dict(schema='osr-current-source-fine-refinement-request/1',body_candidate_id=candidate,
        mesh_m=reconciler.MESH_M,parent_result_sha256=digest(parent),parent_contract_id=value['contract_id'],
        parent_campaign_id=value['campaign_id'],parent_run_id=value['run_id'],parent_frontier_item=task)
    request_id=identity(request)
    exact=stale.parent/request_id
    exact.mkdir()
    (exact/'request.json').write_text(json.dumps(request))
    payloads={'result.json':{'evaluation_id':'fine-evaluation'},'report.json':{'body_candidate_id':candidate},
        'manifest.json':{'manifest_id':'fine-manifest'}}
    for name,payload in payloads.items():(exact/name).write_text(json.dumps(payload))
    checked=[]
    monkeypatch.setattr(reconciler,'verify',lambda *a,**k:checked.append(k) or {'verified':True})
    result=publication._current_fine_refinement(tmp_path,value)
    assert result['folder']==exact
    assert result['request']==request
    assert result['verification']=={'verified':True}
    assert checked==[dict(parent_result=parent,candidate_id=candidate,request_id=request_id)]
    assert (stale/'manifest.json').read_text()=='{}'
