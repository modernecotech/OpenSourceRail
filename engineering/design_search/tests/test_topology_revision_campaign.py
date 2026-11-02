"""Bounded protocol controls; no campaign, optimisation or finite-element solve."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import signal
import subprocess
import sys

import numpy as np
import pytest

from engineering.design_search import topology_geometry as geometry
from engineering.station_rail.common import digest,identity

_spec=importlib.util.spec_from_file_location('engineering.design_search.topology_revision_campaign',
    Path(__file__).resolve().parents[1]/'topology_revision_campaign.py')
c=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=c;_spec.loader.exec_module(c)


@pytest.fixture(autouse=True)
def bounded_control():
    previous=signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('30-second control budget')))
    signal.alarm(30)
    yield
    signal.alarm(0);signal.signal(signal.SIGALRM,previous)


def data():
    mask=np.zeros((6,6),dtype=bool);mask[[0,-1],:]=True;mask[:,[0,-1]]=True;mask[2,2]=True
    passive=mask.copy();passive[2,2]=False;rho=np.full(mask.shape,.2);rho[mask]=.8
    physical=geometry.realize(mask)
    binding=c.revisions.make_parent_input(physical,mask,rho,passive,parent_evaluation_id='a'*64,
        parent_request_id='b'*64,arrays_package_sha256='c'*64,required_passive_cell_ids=np.flatnonzero(passive).tolist())
    child=dict(parent_trial_id='d'*64,parent_attempt_id='e'*64,parent_request_id='b'*64,
        parent_evaluation_id='a'*64,parent_candidate_id=physical['candidate_id'],parent_input=binding,
        parent_files_sha256={},strategy=c.revisions.STRATEGIES[0]);c._seal(child,'trial_id')
    spec=dict(geometry=deepcopy(geometry.FIXED),elastic_hypotheses=dict(steel_density_kg_m3=7850.,concrete_density_kg_m3=2400.),
        search=dict(nx=6,nz=6,passive_edge_band_m=.2,passive_end_block_m=3.34),
        replay=dict(two_mesh_compliance_change_target=.1))
    configured=dict(parent_plan=dict(specification=spec,cost_specification=dict(reserve_mass_kg=geometry.DEFAULT_RESERVES,module_length_m=5.)),
        parent_campaign_id='f'*64,proposal_policy=dict(c.PROPOSAL_POLICY),campaign_id='1'*64,
        source_sha256={'source.py':'2'*64},tool_context=dict(worker_environment={'OPENBLAS_NUM_THREADS':'1'}),
        baseline={'baseline_id':'3'*64,'file_sha256':'4'*64},resources=dict(c.RESOURCES),children=[child])
    original=dict(physical_geometry=physical,representative_poses=[dict(name=x) for x in ('quarter','middle','three-quarter')])
    baseline=dict(baseline_id='3'*64,load_context_id='5'*64,load_context={'id':'6'*64},assumptions={'declared':True})
    return configured,child,original,mask,rho,passive,baseline


def analyses(compliance=10.,gate=True,n=81):
    rows=[dict(load_case='load'+str(i//27),vehicle_mass_case=('low','base','high')[(i//9)%3],
        span_mass_case=('low','base','high')[(i//3)%3],pose=str(i%3),compliance_J=compliance) for i in range(n)]
    return dict(execution='completed',declared_residual_request_met=gate,cases=rows)


def stubs(monkeypatch,coarse=None,fine=None):
    calls=[]
    monkeypatch.setattr(c.parent,'mesh',lambda spec,factor=1:dict(factor=factor))
    def replay(mesh,mask,spec,context,quantity,poses):
        calls.append((mesh['factor'],mask.copy(),deepcopy(quantity),deepcopy(context),deepcopy(poses)))
        analysis=coarse if mesh['factor']==1 else fine
        return {'displacements':np.zeros((2,81))},deepcopy(analyses() if analysis is None else analysis)
    monkeypatch.setattr(c.parent,'replay',replay)
    monkeypatch.setattr(c.topology_cost,'estimate',lambda candidate,q,spec,assumptions:dict(candidate_id=candidate['candidate_id'],quantity_evaluation_id=q['evaluation_id'],assumptions=assumptions))
    monkeypatch.setattr(c.parent,'support_demands',lambda candidate,q,b,spec:dict(candidate_id=candidate['candidate_id'],baseline_id=b['baseline_id']))
    def compare(candidate,q,cost,baseline,supports,*,root):
        assert cost['candidate_id']==supports['candidate_id']==candidate['candidate_id']
        assert cost['quantity_evaluation_id']==q['evaluation_id']
        return dict(candidate_id='7'*64,baseline_id=baseline['baseline_id'],cases={mass:dict(scope_totals_iqd={str(i):[1.,2.,3.] for i in range(14)}) for mass in ('low','base','high')})
    monkeypatch.setattr(c.topology_system_cost,'compare',compare)
    monkeypatch.setattr(c.parent.kernel,'optimise',lambda *_a,**_k:pytest.fail('SIMP must never run'))
    return calls


def test_binary_child_preserves_ancestry_all81_rhs_exact_refined_geometry_and_fourteen_scopes(monkeypatch):
    configured,child,original,mask,rho,passive,baseline=data();calls=stubs(monkeypatch)
    saved=[];request=c._request(configured,child)
    result,raw=c._evaluate(request,configured,original,mask,rho,passive,baseline,checkpoint=lambda *args:saved.append(args))
    assert result['execution']=='completed' and result['parent_evaluation_id']=='a'*64
    assert result['candidate_id']!=original['physical_geometry']['candidate_id']
    assert result['composition_candidate_id']!=result['candidate_id']
    assert result['proposal']['removed_cell_ids']==[14]
    assert [row[0] for row in calls]==[1,2]
    assert calls[1][1].shape==(12,12) and np.array_equal(calls[1][1],np.repeat(np.repeat(calls[0][1],2,0),2,1))
    assert len(result['coarse_replay']['cases'])==len(result['fine_replay']['cases'])==81
    assert len(result['compliance_relative_changes'])==81
    assert all(len(v['scope_totals_iqd'])==14 for v in result['system_cost']['cases'].values())
    assert [x[0] for x in saved]==['proposal','quantities-and-cost','coarse','fine','whole-system-cost']
    np.testing.assert_array_equal(raw['original_density_field'],rho)
    assert result['SIMP_reexecuted'] is result['void_stiffness_credited'] is False
    assert all(result[k] is False for k in c.FLAGS)


def test_residual_gate_prevents_two_mesh_claim_even_when_compliance_equal(monkeypatch):
    values=data();stubs(monkeypatch,fine=analyses(gate=False))
    result,_=c._evaluate(c._request(values[0],values[1]),values[0],*values[2:])
    assert result['compliance_relative_changes'] is None and result['numerical_refinement_status']=='mesh-unresolved'


@pytest.mark.parametrize('bad',('missing','order'))
def test_missing_rhs_or_mixed_fine_cases_fail_without_truncation_and_keep_checkpoints(monkeypatch,bad):
    values=data();fine=analyses(n=80 if bad=='missing' else 81)
    if bad=='order':fine['cases'].reverse()
    stubs(monkeypatch,fine=fine);saved=[]
    with pytest.raises(ValueError,match='81-case|order'):
        c._evaluate(c._request(values[0],values[1]),values[0],*values[2:],checkpoint=lambda *args:saved.append(args))
    assert [x[0] for x in saved][-1]=='fine'


def test_rejected_nochange_is_terminal_without_fe_or_cost(monkeypatch):
    values=data();configured,child,original,mask,rho,passive,baseline=values
    def rejected(*args,**kwargs):
        out=dict(execution='proposal-rejected',failure_reason='physically-identical-no-change',occupancy=mask.tolist(),revision_id='8'*64,evaluation_id='9'*64)
        return out
    monkeypatch.setattr(c.revisions,'propose',rejected)
    monkeypatch.setattr(c.parent,'mesh',lambda *_a,**_k:pytest.fail('Rejected proposal cannot dispatch FE'))
    monkeypatch.setattr(c.topology_cost,'estimate',lambda *_a,**_k:pytest.fail('Rejected proposal cannot dispatch cost'))
    out,_=c._evaluate(c._request(configured,child),configured,original,mask,rho,passive,baseline)
    assert out['execution']=='proposal-rejected' and out['system_cost'] is None


def planned(tmp_path,monkeypatch):
    original=tmp_path/'ordinary-original';original.mkdir();(original/'state.json').write_text('{}');(original/'baseline.json.gz').write_bytes(b'original');(original/'trials').mkdir()
    configured,child,*_=data();parent_plan=dict(load_context={},source_sha256={'old.py':'a'*64},tool_context=configured['tool_context']);c._seal(parent_plan,'campaign_id')
    state=dict(plan=parent_plan,baseline=dict(file_sha256=digest(original/'baseline.json.gz'),baseline_id='b'*64))
    records=[]
    for i in range(6):
        record={k:v for k,v in deepcopy(child).items() if k not in ('strategy','trial_id')};record['parent_trial_id']=str(i)*64;records.append(record)
    monkeypatch.setattr(c,'_verified_parents',lambda folder,root:(state,records))
    monkeypatch.setattr(c,'_source_epoch',lambda root,plan:{'old.py':'a'*64,c.PRODUCER:'b'*64,c.revisions.PRODUCER:'c'*64})
    monkeypatch.setattr(c.parent,'tool_context',lambda:deepcopy(configured['tool_context']))
    return c.plan(tmp_path,parent_state=original),original


def test_plan_twelve_explicit_strategy_pairs_arbitrary_existing_parent_path_no_execution(tmp_path,monkeypatch):
    configured,original=planned(tmp_path,monkeypatch)
    assert configured['parent_state_path']==str(original)
    assert len(configured['children'])==len({v['trial_id'] for v in configured['children']})==12
    assert {v['strategy'] for v in configured['children']}==set(c.revisions.STRATEGIES)
    assert configured['SIMP_reexecuted'] is False and c.PRODUCER in configured['source_sha256']
    assert c._check_plan(configured,tmp_path)==configured


def test_missing_parent_rejected_before_parent_state_can_autocreate(tmp_path,monkeypatch):
    monkeypatch.setattr(c.parent,'_state',lambda *_:pytest.fail('Missing original state must not be created'))
    with pytest.raises(ValueError,match='Existing complete parent'):c._verified_parents(tmp_path/'missing',tmp_path)
    assert not (tmp_path/'missing').exists()


@pytest.mark.parametrize('damage',('source','tools','parent-bytes','duplicate','promotion'))
def test_sealed_but_stale_or_mixed_plan_is_rejected(tmp_path,monkeypatch,damage):
    configured,original=planned(tmp_path,monkeypatch)
    if damage=='source':configured['source_sha256'][c.PRODUCER]='0'*64
    elif damage=='tools':configured['tool_context']={'foreign':True}
    elif damage=='parent-bytes':(original/'state.json').write_text('{"changed":true}')
    elif damage=='duplicate':configured['children'][1]=deepcopy(configured['children'][0])
    else:configured['physical_accepted']=True
    configured.pop('campaign_id');c._seal(configured,'campaign_id')
    with pytest.raises(ValueError):c._check_plan(configured,tmp_path)


def childstate(tmp_path,monkeypatch):
    configured,original=planned(tmp_path,monkeypatch);folder=tmp_path/'separate-children';folder.mkdir()
    (folder/'baseline.json.gz').write_bytes((original/'baseline.json.gz').read_bytes())
    state=dict(schema='osr-topology-revision-state/1',plan=configured,baseline=configured['baseline'],
        pending_trial_ids=[v['trial_id'] for v in configured['children']],completed=[])
    c._write(folder/'state.json',state)
    return folder,configured,state,original


def test_timeout_is_preserved_as_terminal_and_next_run_does_not_retry(tmp_path,monkeypatch):
    folder,configured,state,original=childstate(tmp_path,monkeypatch);calls=[]
    class Child:
        pid=123456
        def __init__(self,args,**kwargs):calls.append((args,kwargs));self.n=0
        def wait(self,timeout=None):
            self.n+=1
            if timeout is not None:raise subprocess.TimeoutExpired('child',timeout)
            return -9
        def poll(self):return -9
    monkeypatch.setattr(c.subprocess,'Popen',Child);kills=[];monkeypatch.setattr(c.os,'killpg',lambda *args:kills.append(args))
    out=c.run(folder,root=tmp_path,max_trials=1,parent_state=original)
    assert out['completed']==1 and out['failed']==1 and out['pending']==11 and len(kills)==1
    updated=c._state(folder,tmp_path);row=updated['completed'][0]
    assert row['execution']=='wall-timeout' and row['physical_failure_inferred'] is False
    attempt=folder/'trials'/row['trial_id'];before={p.name:digest(p) for p in attempt.iterdir()}
    assert {'request.json','attempt.json','stdout.log','stderr.log','process.json'}<=set(before)
    c.run(folder,root=tmp_path,max_trials=0,parent_state=original)
    assert len(calls)==1 and before=={p.name:digest(p) for p in attempt.iterdir()}
    assert calls[0][1]['env']['OPENBLAS_NUM_THREADS']=='1' and calls[0][1]['start_new_session'] is True


def test_spawn_failure_is_indexed_not_silently_retried(tmp_path,monkeypatch):
    folder,_,_,original=childstate(tmp_path,monkeypatch)
    monkeypatch.setattr(c.subprocess,'Popen',lambda *_a,**_k:(_ for _ in ()).throw(OSError('controlled spawn failure')))
    result=c.run(folder,root=tmp_path,max_trials=1,parent_state=original)
    state=c._state(folder,tmp_path)
    assert result['failed']==1 and state['completed'][0]['execution']=='spawn-failed'
    stderr=folder/'trials'/state['completed'][0]['trial_id']/'stderr.log'
    assert b'controlled spawn failure' in stderr.read_bytes()


def test_nested_parent_child_and_unindexed_interrupted_directory_rejected(tmp_path,monkeypatch):
    folder,_,state,original=childstate(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match='disjoint'):c.run(original/'child',root=tmp_path,max_trials=0,parent_state=original)
    interrupted=folder/'trials'/state['pending_trial_ids'][0];interrupted.mkdir(parents=True);(interrupted/'partial.log').write_text('keep')
    with pytest.raises(ValueError,match='Unfinished child'):c.run(folder,root=tmp_path,max_trials=1,parent_state=original)
    assert (interrupted/'partial.log').read_text()=='keep'


def test_symlink_and_invalid_invocation_budget_rejected(tmp_path):
    (tmp_path/'real').mkdir();(tmp_path/'link').symlink_to(tmp_path/'real',target_is_directory=True)
    with pytest.raises(ValueError,match='unlinked'):c.run(tmp_path/'link',root=tmp_path,max_trials=0)
    for value in (True,-1,13,1.5):
        with pytest.raises(ValueError,match='Zero to twelve'):c.run(tmp_path/'safe',root=tmp_path,max_trials=value)


def successful_attempt(tmp_path,monkeypatch):
    configured,child,original,mask,rho,passive,baseline=data();stubs(monkeypatch)
    request=c._request(configured,child);result,raw=c._evaluate(request,configured,original,mask,rho,passive,baseline)
    output=tmp_path/'trials'/child['trial_id'];output.mkdir(parents=True)
    c._write(output/'request.json',request);c._write(output/'result.json.gz',result);np.savez_compressed(output/'arrays.npz',**raw)
    receipt=dict(request_id=request['request_id'],trial_id=child['trial_id'],campaign_id=configured['campaign_id'],
        source_sha256=configured['source_sha256'],tool_context=configured['tool_context'],
        observed_worker_environment=configured['tool_context']['worker_environment'],native_jobs_dispatched=0,SIMP_reexecuted=False,
        limits=dict(RLIMIT_AS_bytes=[c.RESOURCES['maximum_address_space_bytes']]*2,RLIMIT_CPU_seconds=[c.RESOURCES['maximum_cpu_seconds']]*2),
        **c.FLAGS)
    row=dict(trial_id=child['trial_id'],request_id=request['request_id'],execution='worker-completed',returncode=0)
    reseal_attempt(output,row,receipt)
    return configured,output,row,receipt,result


def reseal_attempt(output,row,receipt):
    receipt.pop('receipt_id',None)
    receipt['files_sha256']={n:digest(output/n) for n in ('arrays.npz','result.json.gz')}
    c._seal(receipt,'receipt_id');c._write(output/'worker.json',receipt)
    row.pop('attempt_id',None);row['worker_receipt_id']=receipt['receipt_id']
    row['files_sha256']={p.name:digest(p) for p in output.iterdir() if p.name!='attempt.json'}
    c._seal(row,'attempt_id');c._write(output/'attempt.json',row)


def test_successful_attempt_verifies_complete_worker_result_and_array_bindings(tmp_path,monkeypatch):
    configured,_,row,_,result=successful_attempt(tmp_path,monkeypatch)
    assert c._read_attempt(tmp_path,row,configured)==result


@pytest.mark.parametrize('damage',('raw-payload','density','promotion','ancestry','receipt-source','coverage'))
def test_tampered_attempt_rejected_even_after_consistent_outer_resealing(tmp_path,monkeypatch,damage):
    configured,output,row,receipt,result=successful_attempt(tmp_path,monkeypatch)
    if damage=='raw-payload':
        with (output/'arrays.npz').open('ab') as stream:stream.write(b'changed')
    else:
        if damage=='density':
            with np.load(output/'arrays.npz',allow_pickle=False) as stored:values={k:stored[k].copy() for k in stored.files}
            values['original_density_field'][0,0]=.7;np.savez_compressed(output/'arrays.npz',**values)
        elif damage in ('promotion','ancestry'):
            result['physical_accepted']=True if damage=='promotion' else False
            if damage=='ancestry':result['parent_evaluation_id']='0'*64
            result.pop('evaluation_id');c._seal(result,'evaluation_id');c._write(output/'result.json.gz',result)
        elif damage=='receipt-source':receipt['source_sha256']={'foreign.py':'0'*64}
        reseal_attempt(output,row,receipt)
        if damage=='coverage':
            receipt['files_sha256'].pop('arrays.npz');receipt.pop('receipt_id');c._seal(receipt,'receipt_id');c._write(output/'worker.json',receipt)
            row.pop('attempt_id');row['worker_receipt_id']=receipt['receipt_id'];row['files_sha256']['worker.json']=digest(output/'worker.json')
            c._seal(row,'attempt_id');c._write(output/'attempt.json',row)
    with pytest.raises(ValueError):c._read_attempt(tmp_path,row,configured)


def test_worker_applies_requested_limits_then_refuses_wrong_environment_before_parent_or_fe(tmp_path,monkeypatch):
    configured,child,*_=data();output=tmp_path/'trials'/child['trial_id'];output.mkdir(parents=True)
    request=c._request(configured,child);c._write(output/'request.json',request);c._write(tmp_path/'state.json',dict(plan=configured))
    limits=[];monkeypatch.setattr(c.resource,'setrlimit',lambda kind,value:limits.append((kind,value)))
    monkeypatch.setattr(c,'_check_plan',lambda value,root:value)
    monkeypatch.setattr(c,'_own_parent',lambda *_:pytest.fail('Wrong environment must fail before parent/FE'))
    monkeypatch.setenv('OPENBLAS_NUM_THREADS','2')
    with pytest.raises(ValueError,match='environment'):c._worker(output/'request.json',output)
    assert limits==[(c.resource.RLIMIT_AS,(1024**3,1024**3)),(c.resource.RLIMIT_CPU,(140,140))]
