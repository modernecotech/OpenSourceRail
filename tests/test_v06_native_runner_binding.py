"""Offline binding/receipt controls, not native ERP or resource-execution proof."""
from copy import deepcopy
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import json
import os
import signal
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/automation/native-v06'))
import runner_binding as b


def runner():
    spec=spec_from_file_location('bound_native_runner',ROOT/'tools/automation/v06-platform-native.py');value=module_from_spec(spec);spec.loader.exec_module(value);return value


@pytest.fixture()
def bound(tmp_path,monkeypatch):
    control=tmp_path/'control';control.mkdir(mode=0o700);owner='osr-v06-123456789abc'
    request=dict(owner=owner,private_dir=str(control),limits=dict(cpu_seconds=2700,elapsed_seconds=1800,rss_bytes=1024**3,disk_bytes=1024**3,host_reserve_bytes=100),token='UNIT-NOT-A-CREDENTIAL',**b.FLAGS)
    command=dict(argv=['python','tools/automation/v06-platform-native.py','run','--proposal','unit-only-source'],**b.FLAGS)
    b.supervisor.write(control/'supervisor-binding.json',request);b.supervisor.write(control/'command.json',command)
    for key,value in dict(OSR_NATIVE_OWNER=owner,OSR_NATIVE_PRIVATE_DIR=str(control),OSR_NATIVE_BINDING=request['token']).items():monkeypatch.setenv(key,value)
    value=dict(schema='osr-v06-platform-fixture/2',input_id='a'*64,identities=dict(candidate_id='b'*64),component_id='unit/source-component',
        proposal_file_sha256='c'*64,review_pack=dict(sha256='d'*64),**b.FLAGS)
    source={b.SUPERVISOR_PATH:b.sha256((ROOT/b.SUPERVISOR_PATH).read_bytes()).hexdigest(),'runner.py':'e'*64}
    return control,owner,request,command,value,source


def receipts(bound,monkeypatch):
    control,owner,request,command,value,source=bound;binding=b.bind_run(value,source)
    evidence=control/'fixture/evidence';evidence.mkdir(parents=True)
    native=dict(schema='osr-v06-native-platform-result/2',execution='executed',namespace=owner,input_id=value['input_id'],
        run_binding=binding,acceptance_state='awaiting-resource-supervision',
        cleanup=dict(namespace=owner,verified=True,errors=[],remaining_containers=[],remaining_volumes=[],remaining_networks=[]),**b.FLAGS)
    adoption=dict(schema='osr-native-child-reaper/1',owner=owner,source_sha256=source[b.SUPERVISOR_PATH],verified=True,
        native_exit=0,native_wait_status=0,native_reaped=True,remaining_direct_children=[],
        capabilities=dict(subreaper=True,pidfd_verified=True,parent_death_signal=int(signal.SIGTERM),verified_before_launch=True,
            waitability=dict(verified=True,worker_reset=True,probe_exit=73,probe_wait_status=73<<8)),**b.FLAGS)
    resource=dict(schema='osr-native-resource-supervision/1',execution='completed',owner=owner,child_exit=0,reaper_exit=0,failure=None,
        supervisor_source_sha256=source[b.SUPERVISOR_PATH],binding_sha256=b.digest(request),command_sha256=b.digest(command['argv']),limits=request['limits'],
        final_accounting=dict(cpu_charged_s=1.,host_free_bytes=100000,violations=[]),elapsed_s=2.,observed_peak_rss_bytes=10000,observed_peak_disk_bytes=10000,
        cleanup=dict(owner=owner,verified=True,errors=[],remaining=dict(container=[],volume=[],network=[]),unaccounted_volume_mounts=[]),
        host_process_cleanup=dict(verified=True,worker_reaped=True,worker_wait_status=0,adoption=adoption),**b.FLAGS)
    b.supervisor.write(evidence/'result.json',native);b.supervisor.write(control/'supervisor-result.json',resource)
    calls=[]
    # Other tests cover the real lifecycle contract; these isolate the joint
    # binding boundary and explicitly prove that its upstream verifier is called.
    monkeypatch.setattr(b.candidate_contracts,'verify_result',lambda result,input_value,sources:calls.append((result,input_value,sources)))
    return evidence,native,resource,calls


def test_exact_owner_candidate_source_and_private_fixture_binding(bound):
    control,owner,request,command,value,source=bound;binding=b.bind_run(value,source)
    assert binding['owner']==owner and binding['fixture_dir']==str(control/'fixture')
    assert binding['input_id']==value['input_id'] and binding['source_sha256']==source
    assert b.load(control/'runner-binding.json')==dict(owner=owner,private_dir=str(control),binding_sha256=b.digest(request))
    assert b.bind_run(value,source)==binding and not(control/'fixture').exists()
    assert all(binding[key] is False for key in b.FLAGS)


def test_missing_or_partial_supervisor_context_refuses_v2_before_native_calls(bound,monkeypatch):
    control,owner,request,command,value,source=bound;r=runner()
    monkeypatch.setattr(r,'campaign_input',lambda *a:value);monkeypatch.setattr(r,'sources',lambda:source)
    monkeypatch.setattr(r,'preflight',lambda *a:(_ for _ in ()).throw(AssertionError('Native preflight reached without binding')))
    for key in b.ENV_KEYS:monkeypatch.delenv(key,raising=False)
    with pytest.raises(ValueError,match='reviewed resource supervisor'):r.run()
    assert not(control/'fixture').exists()


def test_conflicting_owner_output_or_candidate_cannot_escape_bound_directory(bound,monkeypatch):
    control,owner,request,command,value,source=bound
    with pytest.raises(ValueError,match='exactly bound'):b.bind_run(value,source,control.parent/'escaped')
    monkeypatch.setenv('OSR_NATIVE_OWNER','osr-v06-fedcba987654')
    with pytest.raises(b.supervisor.Hold):b.bind_run(value,source)
    monkeypatch.setenv('OSR_NATIVE_OWNER',owner);b.bind_run(value,source)
    with pytest.raises(ValueError,match='cannot be overwritten'):b.bind_run(dict(value,input_id='f'*64),source)
    assert not(control.parent/'escaped').exists()


def test_bound_preflight_hold_never_creates_fixture_or_starts_native_services(bound,monkeypatch):
    control,owner,request,command,value,source=bound;r=runner()
    monkeypatch.setattr(r,'campaign_input',lambda *a:value);monkeypatch.setattr(r,'sources',lambda:source)
    monkeypatch.setattr(r,'preflight',lambda *a:dict(ready=False))
    monkeypatch.setattr(r,'invoke',lambda *a,**kw:(_ for _ in ()).throw(AssertionError('No Docker/process call allowed')))
    with pytest.raises(RuntimeError,match='preflight hold'):r.run()
    assert b.load(control/'candidate-run-binding.json')['owner']==owner and not(control/'fixture').exists()


def test_legacy_v1_cannot_substitute_for_an_actual_candidate(bound,monkeypatch):
    *_,value,source=bound
    with pytest.raises(ValueError,match='legacy kit'):b.bind_run(dict(schema='osr-v06-platform-fixture/1'),source)
    for key in b.ENV_KEYS:monkeypatch.delenv(key,raising=False)
    assert b.bind_run(dict(schema='osr-v06-platform-fixture/1'),source) is None


def test_joint_acceptance_requires_lifecycle_and_resource_records(bound,monkeypatch):
    control,owner,request,command,value,source=bound;evidence,native,resource,calls=receipts(bound,monkeypatch)
    result=b.verify_supervision(evidence,value,source,native)
    assert len(calls)==1 and result['owner']==owner and result['input_id']==value['input_id']
    assert result['schema']=='osr-v06-native-candidate-acceptance/1' and result['docker_cleanup_verified'] and result['host_cleanup_verified']
    assert all(result[k] is False for k in b.FLAGS)


@pytest.mark.parametrize('fault',['held','owner','source','command','request','input','host','native-wait','worker-wait','unreaped','volume','docker','erp-owner','physical','missing','budget','cpu','reserve','reset','boolean-exit'])
def test_joint_gate_rejects_mixed_stale_unfinished_or_promoted_receipts(bound,monkeypatch,fault):
    control,owner,request,command,value,source=bound;evidence,native,resource,calls=receipts(bound,monkeypatch)
    if fault=='held':resource['execution']='held'
    elif fault=='owner':resource['owner']='osr-v06-fedcba987654'
    elif fault=='source':resource['supervisor_source_sha256']='0'*64
    elif fault=='command':resource['command_sha256']='0'*64
    elif fault=='request':b.supervisor.write(control/'supervisor-binding.json',dict(request,token='changed'))
    elif fault=='input':value=dict(value,input_id='0'*64)
    elif fault=='host':resource['host_process_cleanup']['verified']=False
    elif fault=='native-wait':resource['host_process_cleanup']['adoption']['native_wait_status']=7<<8
    elif fault=='worker-wait':resource['host_process_cleanup']['worker_wait_status']=7<<8
    elif fault=='unreaped':resource['host_process_cleanup']['worker_reaped']=False
    elif fault=='volume':resource['cleanup']['unaccounted_volume_mounts']=['unknown-volume']
    elif fault=='docker':resource['cleanup']['remaining']['container']=['remaining']
    elif fault=='erp-owner':native['cleanup']['namespace']='osr-v06-fedcba987654';b.supervisor.write(evidence/'result.json',native)
    elif fault=='physical':resource['physical_accepted']=True
    elif fault=='budget':resource['final_accounting']['violations']=['rss']
    elif fault=='cpu':resource['final_accounting']['cpu_charged_s']=3000
    elif fault=='reserve':resource['final_accounting']['host_free_bytes']=1
    elif fault=='reset':resource['host_process_cleanup']['adoption']['capabilities']['waitability']['worker_reset']=False
    elif fault=='boolean-exit':resource['child_exit']=False
    if fault=='missing':(control/'supervisor-result.json').unlink()
    else:b.supervisor.write(control/'supervisor-result.json',resource)
    with pytest.raises(ValueError):b.verify_supervision(evidence,value,source,native)


def test_lifecycle_rejection_and_actual_result_byte_drift_cannot_be_bypassed(bound,monkeypatch):
    control,owner,request,command,value,source=bound;evidence,native,resource,calls=receipts(bound,monkeypatch)
    monkeypatch.setattr(b.candidate_contracts,'verify_result',lambda *a:(_ for _ in ()).throw(ValueError('Actual lifecycle failed')))
    with pytest.raises(ValueError,match='Actual lifecycle'):b.verify_supervision(evidence,value,source,native)
    monkeypatch.setattr(b.candidate_contracts,'verify_result',lambda *a:None)
    b.supervisor.write(evidence/'result.json',dict(native,uncovered=['changed']))
    with pytest.raises(ValueError,match='ERP lifecycle bytes'):b.verify_supervision(evidence,value,source,native)


def test_public_verifier_keeps_legacy_path_and_requires_joint_gate_for_v2(bound,monkeypatch):
    control,owner,request,command,value,source=bound;r=runner();evidence,native,resource,calls=receipts(bound,monkeypatch)
    legacy=dict(schema='osr-v06-native-platform-result/1',legacy='retained')
    monkeypatch.setattr(r,'verify_lifecycle',lambda *a:legacy)
    assert r.verify(evidence)==legacy
    monkeypatch.setattr(r,'verify_lifecycle',lambda *a:native);monkeypatch.setattr(r,'campaign_input',lambda *a:value);monkeypatch.setattr(r,'sources',lambda:source)
    assert r.verify(evidence)['schema']=='osr-v06-native-candidate-acceptance/1'
    (control/'supervisor-result.json').unlink()
    with pytest.raises(ValueError):r.verify(evidence)


def test_disposable_candidate_overlay_names_and_labels_redis_cache_without_changing_v1():
    import yaml
    owner='osr-v06-123456789abc';v1=b.compose_overlay(owner,ROOT,False);v2=b.compose_overlay(owner,ROOT,False,candidate=True)
    base=yaml.safe_load((ROOT/'deployment/erpnext/compose.yaml').read_text());overlay=yaml.safe_load(v2)
    assert 'redis-cache-data' not in v1 and overlay['services']['redis-cache']['volumes']==['redis-cache-data:/data']
    assert overlay['volumes']['redis-cache-data']['labels']=={b.supervisor.LABEL:owner}
    assert overlay['networks']['default']['labels']=={b.supervisor.LABEL:owner}
    for service in (*b.APP_SERVICES,'db','redis-cache','redis-queue'):
        assert overlay['services'][service]['labels'][b.supervisor.LABEL]==owner
    # The Redis /data mount is declared in both service variants after merge.
    assert base['services']['redis-queue']['volumes']==['redis-data:/data']
    assert set(overlay['volumes'])=={'sites','logs','db-data','redis-data','redis-cache-data'}


@pytest.mark.parametrize('quota,expected',[(False,'935cde091c4a9bf5b0d444a2614d55bc88eb0c5b5906037596c87e4180380727'),(True,'d7ee97de21c53bdd6ac6ae3bd67c550becf15a0df835ee561b6e5edb95dbbe12')])
def test_legacy_overlay_bytes_match_the_retained_renderer(quota,expected):
    value=b.compose_overlay('osr-v06-123456789abc',Path('/REPO'),quota)
    assert b.sha256(value.encode()).hexdigest()==expected
