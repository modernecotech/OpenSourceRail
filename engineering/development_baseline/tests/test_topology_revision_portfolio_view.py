"""Authenticated small revision projections; no publication or numerical work."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
from pathlib import Path
import subprocess

import pytest

from engineering.development_baseline import portfolio_view as view
from engineering.station_rail.common import encoded,identity

spec=importlib.util.spec_from_file_location('topology_parent_fixture',Path(__file__).with_name('test_topology_portfolio_view.py'))
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
seal=fixture.seal


def records(baseline=None):
    baseline=fixture.synthetic_baseline() if baseline is None else baseline
    parent=fixture.topology_record(baseline);parent['campaign_id']='f'*64
    for i,a in enumerate(parent['attempts']):a.update(trial_id=str(i)*64,request_id=str(i+5)*64)
    seal(parent,'portfolio_id')
    files={'state.json':'e'*64,'result.json':sha256(encoded(parent)).hexdigest()}
    for a in parent['attempts']:files['trials/'+a['trial_id']+'/arrays.npz']='b'*64
    manifest=seal(dict(schema='osr-civil-topology-publication/1',portfolio_id=parent['portfolio_id'],files_sha256=files,**view.FLAGS),'manifest_id')
    binding=dict(path='docs/design-engine/civil-topology',manifest_id=manifest['manifest_id'],manifest_sha256=sha256(encoded(manifest)).hexdigest(),state_sha256=files['state.json'],campaign_id=parent['campaign_id'])
    old=parent['attempts'][0]
    def replay(valid=True):return dict(execution='completed',residual_request_met=valid,case_count=81,maximum_vertical_displacement_m=17.65)
    child=dict(trial_id='1'*64,request_id='2'*64,attempt_id='3'*64,parent_trial_id=old['trial_id'],parent_request_id=old['request_id'],parent_evaluation_id=old['evaluation_id'],parent_candidate_id=old['candidate_id'],parent_arrays_package_sha256='b'*64,
        candidate_id='c'*64,evaluation_id='4'*64,quantity_evaluation_id='5'*64,composition_candidate_id='6'*64,revision_id='7'*64,
        strategy='retain-mandatory-component',execution='worker-completed',proposal_execution='proposal-generated',refinement_status='mesh-unresolved',
        binary_replay_admitted_to_archive=True,nominal_stock_mass_kg=23000.,span_installed_cost_iqd=dict(low=10.,base=20.,high=40.),factory_person_hours=dict(low=15.,base=20.,high=30.),
        system_cost=deepcopy(old['system_cost']),coarse_replay=replay(),fine_replay=replay(),compliance_relative_changes=[.23]*81,
        physical_model_or_material_strength_qualified=False,current_evaluator_admission=False,**view.FLAGS)
    invalid=deepcopy(child);invalid.update(trial_id='8'*64,candidate_id='d'*64,evaluation_id='9'*64,composition_candidate_id='a'*64,
        fine_replay=replay(False),binary_replay_admitted_to_archive=False,compliance_relative_changes=None)
    duplicate=deepcopy(child);duplicate.update(trial_id='a'*64,evaluation_id='b'*64,strategy='connect-all-stock')
    failed=deepcopy(child);failed.update(trial_id='b'*64,candidate_id=None,evaluation_id=None,system_cost=None,
        execution='wall-timeout',proposal_execution=None,coarse_replay=None,fine_replay=None,refinement_status=None,binary_replay_admitted_to_archive=False)
    archive=deepcopy(parent['archive']);archive['cells'][0].update(candidate_ids=['c'*64],retained_pareto_candidate_ids=['c'*64]);archive['retained_candidate_ids']=['c'*64];archive['cross_cell_partial_quantity_pareto_candidate_ids']=['c'*64];seal(archive,'archive_id')
    record=seal(dict(schema='osr-topology-revision-portfolio/1',parent_publication=binding,baseline_id=parent['baseline_id'],load_context_id=parent['load_context_id'],
        selection_id=baseline['selection_id'],selected_vehicle_candidate_id=baseline['vehicle']['candidate_id'],vehicle_evaluation_id=baseline['vehicle']['evaluation_id'],
        physical_model_or_material_strength_qualified=False,current_evaluator_admission=False,trial_count=4,unique_realized_candidate_count=2,
        archive_eligible_candidate_count=1,archive_eligible_attempt_count=2,residual_gate_failed_attempt_count=1,mesh_unresolved_attempt_count=3,
        attempts=[child,invalid,duplicate,failed],archive=archive,ranking_scope='Next experiment only',integrated_selection=None,**view.FLAGS),'portfolio_id')
    return record,parent,dict(binding,files_sha256=files),manifest


def test_revision_projection_deduplicates_physics_retains_every_attempt_and_publishes_hours():
    record,parent,binding,_=records();before=deepcopy(record)
    out=view._topology_revisions(record,parent,fixture.synthetic_baseline(),binding)
    assert len(out['rows'])==2 and out['mechanics_retained_count']==1
    assert out['quantity_retained_count'] is out['quantity_archive_id'] is None
    assert all(r['process_hours']==dict(low=15.,base=20.,high=30.) and r['quantity_retained'] is None for r in out['rows'])
    assert len(out['assumptions']['attempts'])==4 and out['assumptions']['archive_eligible_attempt_count']==2
    assert out['assumptions']['attempts'][-1]['execution']=='wall-timeout'
    assert out['evidence_path'].endswith('/result.json') and out['geometry_path'].endswith('/revisions.svg')
    assert record==before


def test_valid_evaluation_preferred_for_duplicate_geometry_and_scopes_stay_distinct():
    record,parent,binding,_=records();first=record['attempts'][0];first['fine_replay']['residual_request_met']=False;first['binary_replay_admitted_to_archive']=False
    record['archive_eligible_attempt_count']=1;record['residual_gate_failed_attempt_count']=2;seal(record,'portfolio_id')
    out=view._topology_revisions(record,parent,fixture.synthetic_baseline(),binding);row=next(r for r in out['rows'] if r['candidate_id']=='c'*64)
    assert row['mechanics_evaluation_id']=='b'*64 and row['mechanics_retained'] is True
    assert row['model_deflection_upper_m']==17.65 and 'mesh-unresolved' in row['structural_status']
    assert row['cost_iqd']['base']==20. and len(row['assumptions']['whole_system_cost']['cases']['base']['scope_totals_iqd'])==14
    assert 'unqualified' in row['structural_status'] and row['complete_installed_mass_kg'] is None


@pytest.mark.parametrize('damage',('parent','selection','vehicle','evaluation','arrays','ancestry','archive','cost','hours','missing-hours','scope','promotion','gate'))
def test_mixed_or_stale_revision_evidence_rejected_after_resealing(damage):
    record,parent,binding,_=records();a=record['attempts'][0]
    if damage=='parent':record['parent_publication']['manifest_id']='0'*64
    elif damage=='selection':record['selection_id']='0'*64
    elif damage=='vehicle':record['selected_vehicle_candidate_id']='0'*64
    elif damage=='evaluation':record['vehicle_evaluation_id']='0'*64
    elif damage=='arrays':a['parent_arrays_package_sha256']='0'*64
    elif damage=='ancestry':a['parent_candidate_id']='0'*64
    elif damage=='archive':record['archive']['cells'][0]['candidate_ids'].append('0'*64);seal(record['archive'],'archive_id')
    elif damage=='cost':a['span_installed_cost_iqd']['base']=10**500
    elif damage=='hours':a['factory_person_hours']['base']=-1
    elif damage=='missing-hours':del a['factory_person_hours']
    elif damage=='scope':a['system_cost']['cases']['base']['scope_totals_iqd'].pop('guideway')
    elif damage=='promotion':a['physical_accepted']=True
    else:a['fine_replay']['residual_request_met']=False
    seal(record,'portfolio_id')
    with pytest.raises(view.CurrentUnavailable):view._topology_revisions(record,parent,fixture.synthetic_baseline(),binding)


def test_exact_payload_binding_and_no_dispatch(tmp_path,monkeypatch):
    record,parent,binding,_=records();raw=encoded(record);relative='docs/design-engine/civil-topology-revisions/result.json';path=tmp_path/relative;path.parent.mkdir(parents=True);path.write_bytes(raw)
    publication=dict(source_sha256={relative:sha256(raw).hexdigest()})
    monkeypatch.setattr(subprocess,'Popen',lambda *_a,**_k:pytest.fail('Read-only view cannot dispatch'))
    assert view._read(tmp_path,publication,'civil-topology-revisions','result.json',record['schema'],'portfolio_id')==record
    view._topology_revisions(record,parent,fixture.synthetic_baseline(),binding)
    path.write_bytes(raw+b' ')
    with pytest.raises(view.CurrentUnavailable,match='binding'):view._read(tmp_path,publication,'civil-topology-revisions','result.json',record['schema'],'portfolio_id')
