"""Small publication contracts; typed costing/attempt stubs are not evidence."""
from copy import deepcopy
import gzip
import importlib.util
import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import pytest

ROOT=Path(__file__).resolve().parents[3]
SOURCE_ROOT=Path(os.environ.get('OSR_TOPOLOGY_ORCHESTRATOR_ROOT',ROOT)).resolve()


@pytest.fixture(scope='module')
def p():
    import engineering
    import engineering.design_search
    packages=[engineering,engineering.design_search];saved=[q.__path__ for q in packages];old=list(sys.path)
    try:
        sys.path.insert(0,str(SOURCE_ROOT))
        for package,relative in zip(packages,('engineering','engineering/design_search')):package.__path__=[str(SOURCE_ROOT/relative),*package.__path__]
        spec=importlib.util.spec_from_file_location('engineering.design_search._civil_topology_publication_contract',SOURCE_ROOT/'engineering/design_search/civil_topology_publication.py');module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        yield module
    finally:
        sys.path[:]=old
        for package,path in zip(packages,saved):package.__path__=path
        sys.modules.pop('engineering.design_search._civil_topology_publication_contract',None)


@pytest.fixture(autouse=True)
def no_actual_campaign_or_baseline(p,monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('Publication unit control invoked an actual campaign or baseline')
    for name in ('plan','run','_state','_worker','make_baseline','_baseline'):
        if hasattr(p.experiment,name):monkeypatch.setattr(p.experiment,name,forbidden)
    monkeypatch.setattr(p.topology_system_cost,'validate_baseline',forbidden);monkeypatch.setattr(p.topology_system_cost,'compare',forbidden)


def sealed(p,value,key):
    value=deepcopy(value);value[key]=p.identity(value);return value


def system_record(candidate='composition',tools='recorded-host'):
    rows={name:dict(factory_gate_cost_iqd=[100.,110.,120.],delivered_cost_iqd=[120.,130.,140.],model_based_installed_CAPEX_iqd=[140.,150.,160.],model_based_whole_life_NPV_iqd=[200.,210.,220.],scope_totals_iqd={'guideway':[10.,20.,30.]},production_plan=dict(production_shifts_per_day=2,civil_shifts_per_day=2,hours_per_shift=8)) for name in ('low','base','high')}
    return dict(candidate_id=candidate,evaluation_id='system-'+tools,replay_context=dict(host=tools),comparison_to_corrected_canonical_baseline=dict(same_service=True),cases=rows)


def result_record(p,mask=None,*,valid=True):
    c=p.geometry.realize([[1]] if mask is None else mask);spec=p.topology_cost.default_spec();q=p.geometry.quantities(c,reserves_kg=spec['reserve_mass_kg'],module_length_m=spec['module_length_m'])
    replay=dict(execution='completed',declared_residual_request_met=valid,cases=[dict(load_case='crowd_control',vehicle_mass_case='high',span_mass_case='high',maximum_vertical_displacement_m=.004)])
    return dict(execution='completed',evaluation_id='evaluation-'+c['candidate_id'],physical_geometry=c,quantities=q,
        system_cost=system_record('composition-'+c['candidate_id']),coarse_replay=deepcopy(replay),fine_replay=deepcopy(replay),span_cost=dict(cases=[dict(case=n,scoped_installed_iqd=100.,total_factory_person_hours=10.) for n in ('low','base','high')]),support_demands=dict(status='typed-provisional'),
        baseline_id='typed-baseline',numerical_refinement_status='mesh-unresolved',compliance_relative_changes=[.1],trial=dict(kind='typed'),optimization=None,**p.FLAGS)


def attempt(name,index=0,execution='worker-completed'):
    return dict(trial_id=name,request_id='request-'+name,attempt_id='attempt-'+name,execution=execution,runtime_seconds=float(index+1))


def baseline():return dict(baseline_id='typed-baseline',load_context_id='typed-load',selected=dict(selection_id='selection',candidate_id='selected-vehicle',vehicle_evaluation_id='typed-vehicle-evaluation'))


def manifest_folder(p,tmp_path):
    folder=tmp_path/'publication';folder.mkdir();(folder/'nested').mkdir();(folder/'nested/payload.json').write_text('typed payload\n')
    value=dict(schema='osr-civil-topology-publication/1',portfolio_id='typed',source_sha256={},files_sha256=p._payload(folder),**p.FLAGS);value=sealed(p,value,'manifest_id');(folder/'manifest.json').write_bytes(p.encoded(value));return folder,value


def test_inventory_is_recursive_and_nested_manifest_is_not_excluded(p,tmp_path):
    folder,record=manifest_folder(p,tmp_path);(folder/'nested/manifest.json').write_text('nested data')
    assert 'nested/payload.json' in p._payload(folder) and 'nested/manifest.json' in p._payload(folder)
    with pytest.raises(ValueError,match='inventory'):p._check(folder)


@pytest.mark.parametrize('kind',['file','directory','root','ancestor'])
def test_linked_publication_payload_and_root_are_rejected(p,tmp_path,kind):
    folder,record=manifest_folder(p,tmp_path)
    if kind=='root':
        alias=tmp_path/'alias';alias.symlink_to(folder,target_is_directory=True);target=alias
    elif kind=='ancestor':
        alias=tmp_path/'parent-alias';alias.symlink_to(tmp_path,target_is_directory=True);target=alias/'publication'
    else:
        target=folder;(folder/'linked').symlink_to(folder/'nested/payload.json' if kind=='file' else folder/'nested',target_is_directory=kind=='directory')
    with pytest.raises(ValueError,match='[Ll]ink|[Oo]rdinary|[Uu]nlinked'):p._check(target)


def test_matching_inventory_cannot_promote_physical_acceptance(p,tmp_path):
    folder,record=manifest_folder(p,tmp_path);record.pop('manifest_id');record['physical_accepted']=True;record=sealed(p,record,'manifest_id');(folder/'manifest.json').write_bytes(p.encoded(record))
    with pytest.raises(ValueError):p._check(folder)


def test_system_semantics_ignores_execution_metadata_but_preserves_every_cost_field(p):
    old=system_record();fresh=system_record(tools='different-replay-host')
    assert p._system_semantics(old)==p._system_semantics(fresh)
    for mutation in ('changed','missing'):
        value=deepcopy(fresh)
        if mutation=='changed':value['cases']['base']['scope_totals_iqd']['guideway'][1]+=1
        else:del value['cases']['base']['production_plan']
        assert p._system_semantics(old)!=p._system_semantics(value)
    # Removing an entire cost axis must not be confused with tool provenance.
    value=deepcopy(fresh);del value['cases']['high'];assert p._system_semantics(old)!=p._system_semantics(value)


@pytest.fixture
def inputs(p,tmp_path,monkeypatch):
    result=result_record(p);spec=p.experiment.specification(SOURCE_ROOT);cost_spec=p.topology_cost.default_spec();trial=dict(trial_id='typed-trial')
    recorded_tools=sealed(p,dict(host='/preserved/old-python',binary_sha256='a'*64),'tool_context_id');new_tools=sealed(p,dict(host='/current/ci-python',binary_sha256='b'*64),'tool_context_id')
    configured=sealed(p,dict(specification=spec,load_context=dict(context_id='typed-load',vehicle_candidate_id='selected-vehicle'),cost_specification=cost_spec,source_sha256={'producer':'c'*64},tool_context=recorded_tools,trials=[trial]),'campaign_id')
    current=deepcopy(configured);current['tool_context']=new_tools;current.pop('campaign_id');current=sealed(p,current,'campaign_id')
    original_baseline=dict(baseline(),load_context=configured['load_context'],assumptions=dict(assumption_id='typed-assumptions'))
    payload=gzip.compress(p.encoded(original_baseline),mtime=0);(tmp_path/'baseline.json.gz').write_bytes(payload)
    state=dict(schema='osr-civil-topology-state/1',plan=configured,baseline=dict(baseline_id='typed-baseline',file_sha256=p.digest(tmp_path/'baseline.json.gz')),completed=[attempt('typed-trial')],pending_trial_ids=[]);(tmp_path/'state.json').write_bytes(p.encoded(state))
    calls=[]
    monkeypatch.setattr(p.experiment,'plan',lambda root:current)
    def validate(value,root,*,require_current_tools):calls.append(require_current_tools);assert value==original_baseline
    monkeypatch.setattr(p.topology_system_cost,'validate_baseline',validate)
    monkeypatch.setattr(p.experiment,'_read_attempt',lambda *args:result)
    monkeypatch.setattr(p.topology_cost,'estimate',lambda *args:result['span_cost'])
    monkeypatch.setattr(p.experiment,'support_demands',lambda *args:result['support_demands'])
    recomputed=system_record(result['system_cost']['candidate_id'],tools='current-replay-host')
    def compare(*args,**kwargs):assert kwargs['require_current_tools'] is False;return recomputed
    monkeypatch.setattr(p.topology_system_cost,'compare',compare)
    return dict(folder=tmp_path,state=state,current=current,result=result,recomputed=recomputed,calls=calls)


def test_preserved_tool_context_does_not_require_current_host_equality(p,inputs):
    state,base,attempts=p._inputs(inputs['folder'],SOURCE_ROOT)
    assert state['plan']['tool_context']!=inputs['current']['tool_context']
    assert inputs['calls']==[False] and len(attempts)==1


@pytest.mark.parametrize('field',['source_sha256','load_context','specification'])
def test_preserved_tools_do_not_relax_current_source_candidate_or_spec_identity(p,inputs,field):
    inputs['current'][field]=dict(inputs['current'][field],unexpected='different')
    with pytest.raises(ValueError,match='inputs differ'):p._inputs(inputs['folder'],SOURCE_ROOT)


@pytest.mark.parametrize('mode',['changed-cost','missing-cost','changed-geometry'])
def test_algebraic_replay_rejects_changed_cost_or_candidate_despite_tool_metadata_tolerance(p,inputs,mode):
    if mode=='changed-cost':inputs['recomputed']['cases']['base']['model_based_whole_life_NPV_iqd'][1]+=1
    elif mode=='missing-cost':del inputs['recomputed']['cases']['low']['production_plan']
    else:inputs['result']['physical_geometry']=p.geometry.realize([[1,0]])
    with pytest.raises(ValueError):p._inputs(inputs['folder'],SOURCE_ROOT)


def test_duplicate_physical_results_keep_every_attempt_but_enter_archive_once(p):
    result=result_record(p);other=deepcopy(result);other['evaluation_id']='another-evaluation'
    attempts=[(attempt('trial-a'),result),(attempt('trial-b',1),other),(attempt('failed',2,'wall-timeout'),None)]
    value=p.summarize(dict(plan=dict(campaign_id='campaign')),baseline(),attempts)
    assert value['trial_count']==3 and len(value['attempts'])==3
    assert value['unique_realized_candidate_count']==value['numerically_replayed_candidate_count']==1
    assert value['attempts'][0]['evaluation_id']!=value['attempts'][1]['evaluation_id']
    failed=value['attempts'][2];assert failed['execution']=='wall-timeout' and failed['candidate_id'] is None and failed['system_cost'] is None
    assert value['integrated_selection'] is None and all(value[k] is False for k in p.FLAGS)


@pytest.mark.parametrize('mode',['coarse-failed','fine-failed','coarse-residual','fine-residual'])
def test_failed_binary_or_declared_residual_gate_never_enters_archive(p,mode):
    result=result_record(p)
    if mode.endswith('failed'):result['coarse_replay' if mode.startswith('coarse') else 'fine_replay']['execution']='not-run'
    else:result['coarse_replay' if mode.startswith('coarse') else 'fine_replay']['declared_residual_request_met']=False
    value=p.summarize(dict(plan=dict(campaign_id='campaign')),baseline(),[(attempt('held'),result)])
    assert value['unique_realized_candidate_count']==1 and value['numerically_replayed_candidate_count']==0
    assert value['attempts'][0]['candidate_id']==result['physical_geometry']['candidate_id']


def test_svg_and_readme_keep_failed_attempts_and_draw_actual_cut_rectangles(p):
    result=result_record(p,[[1,0],[0,1]]);attempts=[(attempt('trial<&"'),result),(attempt('failed',1,'worker-failed<&'),None)]
    drawing=p._svg(attempts);tree=ET.fromstring(drawing);texts=[''.join(e.itertext()) for e in tree.iter('{http://www.w3.org/2000/svg}text')]
    assert 'trial<&"' in texts and 'worker-failed<&' in texts
    assert len(list(tree.iter('{http://www.w3.org/2000/svg}rect')))==2+len(result['physical_geometry']['web_geometry']['rectangles_xz_m'])
    value=p.summarize(dict(plan=dict(campaign_id='campaign')),baseline(),attempts);readme=p._readme(value)
    assert '2 terminal attempts' in readme and 'worker-failed<&' in readme
    assert 'do not change the selected v0.6 railway' in readme and 'No candidate is accepted' in readme


@pytest.mark.parametrize('target',['README.md','topologies.svg','result.json'])
def test_verify_rebuilds_cross_records_even_when_inventory_is_consistently_resealed(p,tmp_path,monkeypatch,target):
    result=result_record(p);attempts=[(attempt('trial'),result)];state=dict(plan=dict(campaign_id='campaign'));base=baseline();portfolio=p.summarize(state,base,attempts)
    (tmp_path/'result.json').write_bytes(p.encoded(portfolio));(tmp_path/'README.md').write_text(p._readme(portfolio));(tmp_path/'topologies.svg').write_text(p._svg(attempts))
    monkeypatch.setattr(p,'sources',lambda root:{'typed':'a'*64});monkeypatch.setattr(p,'_inputs',lambda *a:(state,base,attempts))
    def manifest():
        value=sealed(p,dict(schema='osr-civil-topology-publication/1',portfolio_id=portfolio['portfolio_id'],source_sha256=p.sources(SOURCE_ROOT),files_sha256=p._payload(tmp_path),**p.FLAGS),'manifest_id');(tmp_path/'manifest.json').write_bytes(p.encoded(value))
    manifest();assert p.verify(root=SOURCE_ROOT,output=tmp_path)['verified']
    if target=='result.json':
        changed=deepcopy(portfolio);changed['trial_count']=99;(tmp_path/target).write_bytes(p.encoded(changed))
    else:(tmp_path/target).write_text((tmp_path/target).read_text()+'\nchanged')
    manifest()
    with pytest.raises(ValueError,match='does not reproduce'):p.verify(root=SOURCE_ROOT,output=tmp_path)


@pytest.mark.skipif(not hasattr(os,'mkfifo'),reason='POSIX ordinary-payload control')
def test_uninventoried_nonregular_payload_is_rejected_without_opening_fifo(p,tmp_path):
    folder,record=manifest_folder(p,tmp_path);os.mkfifo(folder/'untracked-fifo')
    with pytest.raises(ValueError,match='[Oo]rdinary|[Rr]egular|[Pp]ayload|[Ii]nventory'):p._check(folder)


def test_preserved_tool_metadata_still_requires_its_original_identity_seal(p,inputs):
    state=inputs['state'];state['plan']['tool_context']['host']='/tampered/recorded-host'
    state['plan'].pop('campaign_id');state['plan']=sealed(p,state['plan'],'campaign_id');(inputs['folder']/'state.json').write_bytes(p.encoded(state))
    with pytest.raises(ValueError,match='identity'):p._inputs(inputs['folder'],SOURCE_ROOT)


@pytest.mark.parametrize('mask',[[[1,0],[0,1]],[[0]]])
def test_explicit_invalid_physical_topology_cannot_be_archived_by_resealed_success_flags(p,mask):
    # Impossible kernel success flags are deliberately supplied: a publication
    # must retain this result while rejecting its independently known topology.
    result=result_record(p,mask);value=p.summarize(dict(plan=dict(campaign_id='campaign')),baseline(),[(attempt('invalid-physical'),result)])
    assert value['unique_realized_candidate_count']==1
    assert value['numerically_replayed_candidate_count']==0
    assert value['attempts'][0]['candidate_id']==result['physical_geometry']['candidate_id']
