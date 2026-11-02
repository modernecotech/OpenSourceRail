from copy import deepcopy
import json
from pathlib import Path

import pytest

from engineering.design_search import design_grammar as grammar, railway_campaign as campaign
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity


def fixture(tmp_path):
    epoch={'engineering/example.py':'a'*64}
    bundle=dict(candidate_id='b'*64,body_candidate_id='c'*64,body_definition_id='d'*64,
        definition_id='e'*64,family_id='P1',propulsion_component_id='f'*64,
        mass={'mass_kg':100.0},unweighed_architecture_equipment=['pending'])
    context={'method_status':'not-run','body_candidate_id':bundle['body_candidate_id']}
    outputs={
        'installed_inventory':dict(schema='inventory',candidate_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],evaluation_id='1'*64,accounted_empty_mass_kg=100.0,**campaign.FLAGS),
        'interfaces':dict(candidate_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],value='declared',**campaign.FLAGS),
        'architecture':dict(candidate_id=bundle['candidate_id'],evaluation_id='2'*64,**campaign.FLAGS),
        'propulsion':dict(candidate_id=bundle['candidate_id'],evaluation_id='3'*64,**campaign.FLAGS),
        'motion_and_braking':dict(candidate_id=bundle['candidate_id'],trace=[{'v':-0.0},{'v':2.0}],**campaign.FLAGS),
        'civil':dict(candidate_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],value=5,**campaign.FLAGS),
        'manufacturing_and_economics':dict(candidate_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],value=6,**campaign.FLAGS),
    }
    base={'bundle_definition_id':bundle['definition_id']};body={'body_definition_id':bundle['body_definition_id'],**base}
    stages=[];upstream=[];(tmp_path/'stages').mkdir()
    for name in campaign.STAGES:
        if name in ('installed_inventory','interfaces'):inputs=body
        elif name=='architecture':inputs=base
        elif name=='propulsion':inputs={'architecture_evaluation_id':outputs['architecture']['evaluation_id'],**base}
        elif name=='motion_and_braking':inputs={'propulsion_evaluation_id':outputs['propulsion']['evaluation_id'],**base}
        elif name=='civil':inputs={'structure_context':context,**base}
        else:inputs={'upstream':list(upstream),**base}
        request=dict(stage=name,bundle_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],inputs=deepcopy(inputs),source_sha256=epoch)
        record=dict(schema='osr-coupled-stage-record/1',request=deepcopy(request),output=deepcopy(outputs[name]),**campaign.FLAGS)
        record['record_id']=identity(record)
        (tmp_path/'stages'/identity(request)).write_bytes(encoded(record))
        stages.append(dict(stage=name,request=request,record_id=record['record_id'],reused=False));upstream.append(record['record_id'])
    row=dict(candidate_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],bundle_definition_id=bundle['definition_id'],
        case_context_id=identity(dict(bundle_definition_id=bundle['definition_id'],structure_evidence=context)),structure_context=deepcopy(context),
        family_id=bundle['family_id'],motor_component_id=bundle['propulsion_component_id'],accounted_mass=deepcopy(bundle['mass']),
        architecture_added_mass_unknown=deepcopy(bundle['unweighed_architecture_equipment']),stages=stages,
        inventory_summary=campaign._inventory_summary(outputs['installed_inventory']),interfaces=deepcopy(outputs['interfaces']),
        architecture=deepcopy(outputs['architecture']),propulsion=deepcopy(outputs['propulsion']),motion=campaign._compact_motion(outputs['motion_and_braking']),
        civil=deepcopy(outputs['civil']),economics=deepcopy(outputs['manufacturing_and_economics']),installed_mass_kg=None,
        complete_body_qualified=False,physical_journey_completed=False,**campaign.FLAGS)
    row['row_id']=identity(row)
    return row,bundle,epoch,context


def check(folder,row,bundle,epoch,context):
    campaign._validate_cached_row(row,row['case_context_id'],bundle,epoch)
    campaign._verify_cached_stages(folder,row,bundle,epoch,context)


def stage_path(folder,row,index):
    return folder/'stages'/identity(row['stages'][index]['request'])


def reseal(row):row['row_id']=identity({k:v for k,v in row.items() if k!='row_id'})


def test_consistent_seven_stage_case_passes(tmp_path):
    row,bundle,epoch,context=fixture(tmp_path);check(tmp_path,row,bundle,epoch,context)


def test_missing_stage_file_fails(tmp_path):
    row,bundle,epoch,context=fixture(tmp_path);stage_path(tmp_path,row,2).unlink()
    with pytest.raises(ValueError,match='unavailable'):check(tmp_path,row,bundle,epoch,context)


def test_unresealed_stage_payload_tampering_fails(tmp_path):
    row,bundle,epoch,context=fixture(tmp_path);path=stage_path(tmp_path,row,2)
    record=json.loads(path.read_bytes());record['output']['evaluation_id']='8'*64;path.write_bytes(encoded(record))
    with pytest.raises(ValueError,match='stage record differs'):check(tmp_path,row,bundle,epoch,context)


@pytest.mark.parametrize('index',range(7))
def test_resealed_stage_output_that_disagrees_with_row_fails(tmp_path,index):
    row,bundle,epoch,context=fixture(tmp_path);path=stage_path(tmp_path,row,index)
    record=json.loads(path.read_bytes());out=record['output']
    if index==0:out['accounted_empty_mass_kg']=101.0
    elif index in (2,3):out['evaluation_id']='8'*64
    elif index==4:out['trace'][0]['v']=1.0
    else:out['value']='altered'
    record['record_id']=identity({k:v for k,v in record.items() if k!='record_id'});path.write_bytes(encoded(record))
    row['stages'][index]['record_id']=record['record_id'];reseal(row)
    with pytest.raises(ValueError,match='output differs from case projection'):check(tmp_path,row,bundle,epoch,context)


@pytest.mark.parametrize('mutation',['stage','candidate','body','source','dependency'])
def test_resealed_swapped_requests_do_not_match_candidate_dependencies(tmp_path,mutation):
    row,bundle,epoch,context=fixture(tmp_path);ref=row['stages'][3];request=ref['request']
    if mutation=='stage':request['stage']='interfaces'
    elif mutation=='candidate':request['bundle_id']='0'*64
    elif mutation=='body':request['body_candidate_id']='0'*64
    elif mutation=='source':request['source_sha256']={'wrong':'0'*64}
    else:request['inputs']['architecture_evaluation_id']='0'*64
    reseal(row)
    with pytest.raises(ValueError):check(tmp_path,row,bundle,epoch,context)


def test_swapped_stage_file_and_symlink_fail(tmp_path):
    row,bundle,epoch,context=fixture(tmp_path);a=stage_path(tmp_path,row,0);b=stage_path(tmp_path,row,1)
    a.write_bytes(b.read_bytes())
    with pytest.raises(ValueError,match='stage record differs'):check(tmp_path,row,bundle,epoch,context)
    a.unlink();a.symlink_to(b)
    with pytest.raises(ValueError,match='unavailable or unsafe'):check(tmp_path,row,bundle,epoch,context)


def test_output_types_and_compacted_trace_are_exact():
    assert not campaign._same_json(True,1)
    assert not campaign._same_json(-0.0,0.0)
    full={'trace':[{'v':-0.0}, {'v':2.0}], 'child':[{'trace':[1,2]}]}
    compact=campaign._compact_motion(full)
    assert campaign._same_compacted_motion(full,compact)
    compact['trace_index']['sha256']='0'*64
    assert not campaign._same_compacted_motion(full,compact)


def test_bounded_stage_reader_rejects_oversized_file(tmp_path,monkeypatch):
    row,bundle,epoch,context=fixture(tmp_path)
    monkeypatch.setattr(campaign,'_STAGE_RECORD_MAX_BYTES',16)
    with pytest.raises(ValueError,match='bounded ordinary-file domain'):check(tmp_path,row,bundle,epoch,context)


def test_duplicate_json_keys_are_rejected(tmp_path):
    row,bundle,epoch,context=fixture(tmp_path);path=stage_path(tmp_path,row,0)
    raw=path.read_bytes();path.write_bytes(raw.replace(b'{"configuration_adopted":false,',b'{"configuration_adopted":false,"configuration_adopted":false,',1))
    with pytest.raises(ValueError,match='stage JSON differs'):check(tmp_path,row,bundle,epoch,context)


def test_cached_validation_preserves_same_epoch_resume_bytes(tmp_path,monkeypatch):
    """Compare a bounded one-bundle replay with and without stage checks."""
    body=grammar.build(grammar.parameters());spec=campaign.specification();spec['families']=['P1']
    monkeypatch.setattr(campaign,'specification',lambda root=ROOT:deepcopy(spec))
    monkeypatch.setattr(campaign,'generate_bodies',lambda:([body],[]))
    context=dict(method_status='not-run',body_admission={},body_results=[],pending=[])
    monkeypatch.setattr(campaign,'_native_campaign',lambda *args,**kwargs:deepcopy(context))
    state=tmp_path/'state';campaign.run(state=state,maximum_new_bundles=1,native_jobs=0)
    validator=campaign._verify_cached_stages
    monkeypatch.setattr(campaign,'_verify_cached_stages',lambda *args:None)
    baseline=campaign.run(state=state,maximum_new_bundles=0,native_jobs=0)
    before=(state/'result.json').read_bytes()
    monkeypatch.setattr(campaign,'_verify_cached_stages',validator)
    checked=campaign.run(state=state,maximum_new_bundles=0,native_jobs=0)
    assert baseline==checked and before==(state/'result.json').read_bytes()
    assert checked['reused_bundles']==1 and checked['new_bundles']==0
    assert checked['integrated_selection'] is None and all(checked[k] is False for k in campaign.FLAGS)
