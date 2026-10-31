"""Execution/cache contracts; no synthetic native result qualifies a vehicle."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from engineering.design_search import railway_campaign as c,railway_native as native,grammar_shell as shell,design_grammar as grammar
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity


def test_stage_requires_exact_dependency_request_and_stable_source_epoch(tmp_path,monkeypatch):
    epoch={'fixture':'a'*64};monkeypatch.setattr(c,'source_epoch',lambda root:epoch)
    bundle=dict(candidate_id='1'*64,body_candidate_id='2'*64);calls=[]
    def calculate():calls.append(True);return dict(candidate_id=bundle['candidate_id'],value=3)
    a,reuse=c._stage(tmp_path,'fixture',bundle,{'mass':100},epoch,calculate)
    b,reuse=c._stage(tmp_path,'fixture',bundle,{'mass':100},epoch,calculate)
    assert reuse and len(calls)==1 and a==b
    different,reuse=c._stage(tmp_path,'fixture',bundle,{'mass':101},epoch,calculate)
    assert not reuse and different['record_id']!=a['record_id']
    monkeypatch.setattr(c,'source_epoch',lambda root:{'fixture':'b'*64})
    with pytest.raises(ValueError,match='epoch changed'):c._stage(tmp_path,'fixture',bundle,{'mass':100},epoch,calculate)


def test_stable_comparison_identity_excludes_invocation_counters_only():
    a=dict(rows=[{'mass':100}],new_bundles=1,reused_bundles=0,native={'new_native_jobs':2,'reused_native_jobs':0,'body_results':[{'evaluation_id':'a'*64}]})
    b=deepcopy(a);b.update(new_bundles=0,reused_bundles=1);b['native'].update(new_native_jobs=0,reused_native_jobs=2)
    assert c.semantic_id(a)==c.semantic_id(b)
    b['native']['body_results'][0]['evaluation_id']='b'*64
    assert c.semantic_id(a)!=c.semantic_id(b)


def test_native_request_cannot_be_rebound_to_another_fixture_or_resource_limit(tmp_path):
    case=shell.benchmark_plan()['cases'][0];(tmp_path/'model.inp').write_text(case['raw']);(tmp_path/'definition.json').write_bytes(encoded(case['definition']))
    request=dict(kind='independent-solid-method',case_id=case['id'],input_id=identity(json.loads(encoded(case))),memory_mb=3072,timeout_s=90)
    result=dict(benchmark_id=case['id'],tool=dict(requested_memory_mb=3072,timeout_s=90))
    assert native._requested(tmp_path,result,request)==result
    with pytest.raises(ValueError,match='fixture input'):native._requested(tmp_path,{**result,'benchmark_id':'different'},request)
    with pytest.raises(ValueError,match='resource'):native._requested(tmp_path,result,{**request,'memory_mb':5120})


def test_resume_and_new_structural_evidence_trigger_dependent_case_evaluation(tmp_path,monkeypatch):
    body=grammar.build(grammar.parameters());spec=c.specification();spec['families']=['P1','P2']
    monkeypatch.setattr(c,'specification',lambda root=ROOT:deepcopy(spec));monkeypatch.setattr(c,'generate_bodies',lambda:([body],[]))
    context=dict(method_status='not-run',body_admission={},body_results=[],pending=[])
    monkeypatch.setattr(c,'_native_campaign',lambda *args,**kwargs:deepcopy(context))
    a=c.run(state=tmp_path,maximum_new_bundles=1);assert len(a['rows'])==1 and a['new_bundles']==1
    estimate=a['rows'][0]['economics']['model_cost']
    assert estimate['model_cost_complete_for_declared_case'] is True
    assert estimate['procurement_ready'] is False and estimate['physical_or_safety_accepted'] is False
    assert a['rows'][0]['economics']['model_based_whole_life_NPV_IQD']==estimate['model_based_whole_life_NPV_iqd']
    assert len(a['model_cost_comparisons'])==1 and a['model_cost_comparisons'][0]['comparison']['integrated_winner'] is None
    b=c.run(state=tmp_path,maximum_new_bundles=0);assert b['campaign_id']==a['campaign_id'] and b['reused_bundles']==1
    context['body_results']=[dict(body_candidate_id=body['candidate_id'],evaluation_id='c'*64,case='normal',mesh_m=1.,raw={'numerical_validity':'unknown'})]
    d=c.run(state=tmp_path,maximum_new_bundles=1)
    assert d['new_bundles']==1 and d['rows'][0]['case_context_id']!=a['rows'][0]['case_context_id']
    old=next(s for s in a['rows'][0]['stages'] if s['stage']=='civil');new=next(s for s in d['rows'][0]['stages'] if s['stage']=='civil')
    assert old['record_id']!=new['record_id']
    assert len(list((tmp_path/'cases').iterdir()))==2
