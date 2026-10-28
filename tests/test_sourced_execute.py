"""Orchestrator contract fixtures are disposable, never engineering evidence."""
import importlib.util
from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
import pytest

PATH=Path(__file__).resolve().parents[1]/'tools/automation/sourced-execute.py'
spec=importlib.util.spec_from_file_location('osr_sourced_execute',PATH);x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)


def signed(v,key='evaluation_id'):
    v[key]=x.ident(v);return v


def req():return dict(vehicle_id='V1',distance_m=2000.,variant='unit-test-only',distributed=False,ambient_C=55.)


def fake_case():
    physical=dict(vehicle='body',wayside_drive='drive');cid=x.ident(physical)
    b=signed(dict(candidate_id=cid,body_candidate_id='body',propulsion_component_id='drive',brake_definition=dict(candidate_id=cid),architecture_case=dict(physical_definition=dict(composition=physical)),**x.FLAGS),'definition_id')
    a=signed(dict(candidate_id='drive',body_candidate_id='body',**x.FLAGS))
    r=dict(**req(),candidate_id=cid,body_candidate_id='body',bundle=b,drive=a,source_sha256={'source.py':'a'*64},qualified_journeys=0,operating_map_admitted=False,journeys=[],**x.FLAGS)
    for k in ('civil','manufacturing','partial_public_price'):r[k]=dict(candidate_id=cid)
    return signed(r)


def test_case_rejects_wrong_source_body_or_unsealed_cache(monkeypatch):
    c=SimpleNamespace(identity=x.ident);e={'vehicle':{'candidate_id':'body'}}
    monkeypatch.setattr(x,'vehicle',lambda c,e:e['vehicle']);r=fake_case()
    assert x.case(c,r,req(),e,{'source.py':'a'*64}) is r
    with pytest.raises(ValueError):x.case(c,r,req(),e,{'source.py':'b'*64})
    bad=deepcopy(r);bad['qualified_journeys']=1
    with pytest.raises(ValueError):x.case(c,bad,req(),e,r['source_sha256'])
    bad=deepcopy(r);bad['body_candidate_id']='other';bad=signed({k:v for k,v in bad.items() if k!='evaluation_id'})
    with pytest.raises(ValueError):x.case(c,bad,req(),e,r['source_sha256'])


@pytest.mark.parametrize('result',[dict(failures=[{'body':'V2','reason':'definition failure'}],semantic_replay_executed=False),dict(failures=[],semantic_replay_executed=False)])
def test_failed_or_incomplete_replay_never_publishes(monkeypatch,tmp_path,result):
    output=tmp_path/'published';output.mkdir();marker=output/'keep';marker.write_text('old publication')
    monkeypatch.setattr(x,'modules',lambda root:SimpleNamespace())
    monkeypatch.setattr(x,'execute',lambda *args,**kwargs:(result,tmp_path/'audit'))
    with pytest.raises(ValueError):x.publish(tmp_path/'state',output=output,audit=tmp_path/'audit')
    assert list(output.iterdir())==[marker] and marker.read_text()=='old publication'


def test_worker_receipt_wrong_epoch_cannot_supply_canonical_outputs(tmp_path):
    request=dict(executor_sha256=x.sha(PATH),source_sha256={'a':'a'},input_files_sha256={},request_id='request')
    report=dict(request_id='request',source_sha256={'other':'b'},executor_sha256=x.sha(PATH),output_files_sha256={},**x.FLAGS)
    report['execution_id']=x.ident(report);x.write(tmp_path/'worker-result.json',report)
    with pytest.raises(ValueError):x.validate_outputs(None,tmp_path,request,{'a':'a'})


def test_changed_worker_input_is_not_accepted_after_execution(tmp_path):
    p=tmp_path/'cached-vehicle.json.gz';p.write_bytes(b'initial');digest=x.sha(p)
    r=dict(executor_sha256=x.sha(PATH),source_sha256={},input_files_sha256={p.name:digest})
    p.write_bytes(b'modified')
    with pytest.raises(ValueError):x.validate_outputs(None,tmp_path,r,{})


def test_conflicting_canonical_files_are_never_overwritten(tmp_path):
    source=tmp_path/'source';target=tmp_path/'target';source.write_bytes(b'new');target.write_bytes(b'old')
    with pytest.raises(ValueError):x.install(source,target)
    assert target.read_bytes()==b'old'


def test_audit_must_not_pollute_closed_state_and_lock_is_shared(tmp_path):
    state=tmp_path/'state'
    with pytest.raises(ValueError):x.outside(state/'audit',state)
    with x.lock(state):
        with pytest.raises(ValueError):
            with x.lock(state):pass


def test_worker_actual_replay_detects_resealed_numerical_forgery(monkeypatch,tmp_path):
    folder=tmp_path/'worker';folder.mkdir();archive=tmp_path/'source.tar.gz';archive.write_bytes(b'disposable-source-fixture')
    cached=dict(vehicle={'candidate_id':'body'});x.write(folder/'cached-vehicle.json.gz',cached)
    request=req();epoch={'source.py':'a'*64};key=x.ident(dict(request=request,source=epoch))
    old=dict(value='forged',**x.FLAGS);x.write(folder/('expected-'+key+'.json.gz'),old)
    inputs={p.name:x.sha(p) for p in folder.iterdir()}
    r=dict(operation='replay',root=str(tmp_path),requests=[request],missing_request_keys=[],source_sha256=epoch,
        executor_sha256=x.sha(PATH),input_files_sha256=inputs,source_archive_sha256=x.sha(archive),source_archive=str(archive),**x.FLAGS)
    r['request_id']=x.ident(r);x.write(folder/'input.json',r)
    c=SimpleNamespace(plan=lambda:[request],sources=lambda root:epoch,write=x.write,identity=x.ident,encoded=x.encoded,evaluate=lambda e,**kw:dict(value='actual',**x.FLAGS))
    monkeypatch.setattr(x,'modules',lambda root:c);monkeypatch.setattr(x,'vehicle',lambda c,e:e['vehicle']);monkeypatch.setattr(x,'case',lambda c,v,*args:v)
    assert x.worker(folder)==2
    result=x.load(folder/'worker-result.json')
    assert result['execution']=='failed' and 'semantic replay differs' in result['failure']['reason']
    assert result['completed']==[] and result['operating_release'] is False


def test_fresh_attempts_preserve_previous_failure_packages(tmp_path):
    a=x.fresh(tmp_path,'gen');(a/'failure.json').write_text('preserve')
    b=x.fresh(tmp_path,'gen');assert a!=b and (a/'failure.json').read_text()=='preserve'


def test_completed_case_survives_later_definition_failure(monkeypatch,tmp_path):
    c=SimpleNamespace(identity=x.ident);monkeypatch.setattr(x,'vehicle',lambda c,e:e['vehicle'])
    e={'vehicle':{'candidate_id':'body'}};x.write(tmp_path/'vehicle.json.gz',e)
    r=fake_case();epoch=r['source_sha256'];key=x.ident(dict(request=req(),source=epoch));name='case-'+key+'.json.gz';x.write(tmp_path/name,r)
    request=dict(executor_sha256=x.sha(PATH),source_sha256=epoch,input_files_sha256={},request_id='request',requests=[req()])
    report=dict(request_id='request',source_sha256=epoch,executor_sha256=x.sha(PATH),output_files_sha256={p.name:x.sha(p) for p in tmp_path.iterdir()},execution='failed',failure={'reason':'later definition failure'},**x.FLAGS)
    report['execution_id']=x.ident(report);x.write(tmp_path/'worker-result.json',report)
    done,receipt=x.validate_outputs(c,tmp_path,request,epoch)
    assert len(done)==1 and done[0][2]['evaluation_id']==r['evaluation_id']
    assert receipt['execution']=='failed' and receipt['failure']['reason']=='later definition failure'


def test_publication_binds_original_gzip_while_accepting_portable_recompression(tmp_path):
    import gzip
    c=SimpleNamespace(identity=x.ident);epoch={'source.py':'a'*64};request=req();key=x.ident(dict(request=request,source=epoch))
    state=tmp_path/'state';(state/'cases').mkdir(parents=True);folder=tmp_path/'worker';folder.mkdir()
    payload=x.encoded({'values':list(range(200)),**x.FLAGS})
    original=gzip.compress(payload,compresslevel=1,mtime=0);regenerated=gzip.compress(payload,compresslevel=9,mtime=0)
    assert original!=regenerated and gzip.decompress(original)==gzip.decompress(regenerated)
    name='expected-'+key+'.json.gz';(folder/name).write_bytes(original);(folder/('case-'+key+'.json.gz')).write_bytes(regenerated)
    canonical=state/'cases'/(key+'.json.gz');canonical.write_bytes(original)
    r=dict(requests=[request],input_files_sha256={name:x.sha(folder/name)})
    x.bind_replayed_canonical(c,state,folder,r,epoch)
    canonical.write_bytes(regenerated)
    with pytest.raises(ValueError):x.bind_replayed_canonical(c,state,folder,r,epoch)


def test_resource_budget_is_explicit_address_space_not_an_RSS_claim():
    assert x.MEMORY==2*1024**3 and x.RSS_TARGET==700*1024**2


def snapshot_fixture(state):
    state.mkdir();(state/'latest.json').write_bytes(b'frontier');(state/'vehicles').mkdir();(state/'vehicles/V1.json.gz').write_bytes(b'actual-sealed-registry-fixture')
    snapshot=x.canonical_inventory(state);epoch={'source':'epoch'}
    replay=dict(initial_verification=dict(verified=True,pending=0,cases=30,semantic_replay_executed=False,**x.FLAGS),canonical_input_inventory=snapshot,canonical_input_inventory_id=x.ident(snapshot),source_sha256=epoch)
    return SimpleNamespace(sources=lambda root:epoch),replay


def test_postlock_reuses_first_report_only_for_exact_all_canonical_bytes(tmp_path):
    state=tmp_path/'state';c,replay=snapshot_fixture(state)
    check=x.bind_verified_snapshot(c,state,replay,tmp_path)
    assert check==replay['initial_verification'] and check is not replay['initial_verification']
    (state/'.coordinator.lock').write_text('cooperative lock changes are not engineering payload')
    assert x.bind_verified_snapshot(c,state,replay,tmp_path)==check
    (state/'vehicles/V1.json.gz').write_bytes(b'changed-registry')
    with pytest.raises(ValueError,match='inventory or source changed'):x.bind_verified_snapshot(c,state,replay,tmp_path)


def test_postlock_rejects_added_file_or_source_epoch(tmp_path):
    state=tmp_path/'state';c,replay=snapshot_fixture(state)
    (state/'unexpected.json').write_text('extra payload')
    with pytest.raises(ValueError,match='inventory or source changed'):x.bind_verified_snapshot(c,state,replay,tmp_path)
    (state/'unexpected.json').unlink();c.sources=lambda root:{'source':'changed'}
    with pytest.raises(ValueError,match='inventory or source changed'):x.bind_verified_snapshot(c,state,replay,tmp_path)


def test_postlock_rejects_forged_snapshot_and_incomplete_initial_verification(tmp_path):
    state=tmp_path/'state';c,replay=snapshot_fixture(state);replay['canonical_input_inventory_id']='forged'
    with pytest.raises(ValueError):x.bind_verified_snapshot(c,state,replay,tmp_path)
    replay['canonical_input_inventory_id']=x.ident(replay['canonical_input_inventory']);replay['initial_verification']['pending']=1
    with pytest.raises(ValueError,match='complete first verification'):x.bind_verified_snapshot(c,state,replay,tmp_path)
