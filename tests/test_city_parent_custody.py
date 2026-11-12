"""Parent custody is content-bound, server-supplied and independent of store location."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from engineering.outline import city_workflow as flow,city_jobs as jobs
from engineering.station_rail.common import encoded,identity


def sealed(value,key):
    value[key]=identity({k:v for k,v in value.items() if k!=key});return value


@pytest.fixture
def parent(tmp_path,monkeypatch):
    root=tmp_path/'source';root.mkdir();(root/'producer.py').write_bytes(b'controlled source')
    store=tmp_path/'external';job='a'*32;folder=store/job/'artifacts';folder.mkdir(parents=True)
    planning={'city':'fixture','declared_reference':'not physical evidence'}
    raw=encoded(planning);(folder/'planning.json').write_bytes(raw)
    manifest=sealed(dict(schema='osr-mapped-city-workflow-publication/1',evaluation_id='b'*64,
        files_sha256={'planning.json':flow.identity_bytes(raw)},
        source_sha256={'producer.py':flow.digest(root/'producer.py')},**flow.FLAGS),'manifest_id')
    (folder/'manifest.json').write_bytes(encoded(manifest))
    verified=[]
    monkeypatch.setattr(flow,'verify',lambda path,**kw:verified.append(path) or deepcopy(manifest))
    from engineering.outline import planning_adapter
    def verify_base(base,root,*,trusted_base_sha256):
        assert flow.identity_bytes(encoded(base))==trusted_base_sha256
        return base
    monkeypatch.setattr(planning_adapter,'verify_base',verify_base)
    return root,store,job,folder,manifest,planning,verified


def test_external_capture_and_retained_offline_resolution(parent):
    root,store,job,folder,m,planning,verified=parent
    snapshot,base,trusted=flow.resolve_parent({'base_study_id':job},root=root,study_store=store)
    assert verified==[folder] and base==planning and trusted==m['files_sha256']['planning.json']
    assert json.loads(snapshot['manifest_json'])['manifest_id']==m['manifest_id']
    # Remove the original custody tree. The sealed result snapshot still replays
    # the exact parent planning input, without claiming full ancestor replay.
    import shutil
    shutil.rmtree(store)
    assert flow.resolve_parent({'base_study_id':job},root=root,parent=snapshot)==(snapshot,base,trusted)
    assert verified==[folder] and not (root/'build').exists()


@pytest.mark.parametrize('fault',['planning','manifest','planning-hash','manifest-seal','study-id','source'])
def test_resealed_snapshot_cannot_bypass_parent_custody(parent,fault):
    root,store,job,folder,m,planning,_=parent
    snapshot=flow.parent_snapshot(folder,job,root=root)
    if fault=='planning':snapshot['planning_json']='{}'
    elif fault=='manifest':snapshot['manifest_json']='{}'
    elif fault=='planning-hash':
        snapshot['planning_json']='{}';snapshot['planning_sha256']=flow.identity_bytes(b'{}')
    elif fault=='manifest-seal':
        manifest=json.loads(snapshot['manifest_json']);manifest['evaluation_id']='f'*64
        raw=encoded(manifest);snapshot['manifest_json']=raw.decode();snapshot['manifest_sha256']=flow.identity_bytes(raw)
    elif fault=='study-id':snapshot['study_id']='c'*32
    else:(root/'producer.py').write_bytes(b'changed source')
    sealed(snapshot,'snapshot_id')
    with pytest.raises(ValueError):flow.validate_parent_snapshot(snapshot,job,root=root)


def test_capture_rejects_changed_parent_after_server_verification(parent):
    root,_,job,folder,m,_,_=parent
    (folder/'manifest.json').write_bytes(b'{}')
    with pytest.raises(ValueError,match='changed during capture'):
        flow.parent_snapshot(folder,job,root=root,verified_manifest=m)


def test_client_cannot_specify_parent_snapshot_or_store_path():
    for key in ('parent','parent_snapshot','study_store','parent_directory'):
        with pytest.raises(ValueError,match='Typed'):
            flow.normalize({'city_slug':'samawah',key:'/arbitrary/client/path'})


def test_parent_snapshot_requires_exact_parent_request(parent):
    root,_,job,folder,_,_,_=parent;snapshot=flow.parent_snapshot(folder,job,root=root)
    with pytest.raises(ValueError,match='requires'):
        flow.resolve_parent({'city_slug':'fixture'},root=root,parent=snapshot)
    with pytest.raises(ValueError,match='exact'):
        flow.resolve_parent({'base_study_id':'d'*32},root=root,parent=snapshot)


def test_worker_receives_only_server_owned_snapshot_path(tmp_path,monkeypatch):
    from threading import RLock
    root=tmp_path/'source';root.mkdir();store=tmp_path/'external';store.mkdir()
    service=jobs.CityStudyService.__new__(jobs.CityStudyService)
    service.root=root;service.store=store;service.closed=False;service.lock=RLock()
    service.completed_by_key={};service.jobs={};service._poll=lambda jid:{'state':'completed'}
    service._verify=lambda path:{'manifest_id':'c'*64};service._usage=lambda:0
    service._write=lambda *a:None
    parent={'snapshot_id':'b'*64};seen=[]
    monkeypatch.setattr(jobs.publication_cache,'json_member',lambda *a,**k:{'evaluation_id':'d'*64,'planning_seed':{'seed_id':'e'*64}})
    monkeypatch.setattr(flow,'_sources',lambda root:{'producer.py':'f'*64})
    monkeypatch.setattr(flow,'parent_snapshot',lambda *a,**k:deepcopy(parent))
    monkeypatch.setattr(jobs,'disk_admission',lambda *a,**k:{'admitted':True})
    monkeypatch.setattr(jobs.subprocess,'Popen',lambda args,**kwargs:seen.append(args) or SimpleNamespace())
    request={'city_slug':'samawah','base_study_id':'a'*32,'edit_bundle':{}}
    a=service.submit(request)
    command=seen[0];path=Path(command[command.index('--parent-snapshot')+1])
    assert path==store/a['job_id']/'parent-study.json' and json.loads(path.read_bytes())==parent
    assert '--root' in command and command[command.index('--root')+1]==str(root)
    assert 'parent' not in json.loads((path.parent/'request.json').read_bytes())
    parent['snapshot_id']='0'*64
    b=service.submit(request)
    assert a['request_key']!=b['request_key'],'Cache identity must bind actual parent content'
    for record in service.jobs.values():record['log'].close()
