"""Publication-contract tests use fake cheap executions, never claim physics."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import io,json,tarfile
from pathlib import Path
from types import SimpleNamespace
import pytest

P=Path(__file__).resolve().parents[1]/'sourced-verify.py';spec=importlib.util.spec_from_file_location('sourced_full_verify',P);s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def ident(v):return sha256(encoded(v)).hexdigest()

def archive(path,entries):
    with tarfile.open(path,'w:gz') as a:
        for name,raw,kind in entries:
            info=tarfile.TarInfo(name);info.size=len(raw);info.type=kind
            if kind==tarfile.SYMTYPE:info.linkname='../escape'
            a.addfile(info,io.BytesIO(raw) if kind==tarfile.REGTYPE else None)

@pytest.fixture
def fixture(tmp_path,monkeypatch):
    root=tmp_path/'root';pub=tmp_path/'pub';audit=tmp_path/'private';root.mkdir();pub.mkdir();(root/'tools/automation').mkdir(parents=True)
    helper=root/s.HELPER;helper.write_bytes(b'frozen-executor-fixture');monkeypatch.setattr(s,'HELPER_SHA256',s._sha(helper))
    epoch={'source.py':'a'*64};check=dict(verified=True,run_id='b'*64,cases=30,pending=0,semantic_replay_executed=True,qualified_journeys=0,**s.FLAGS)
    index=dict(run_id='b'*64,cases=[dict(name=i) for i in range(30)],pending=[])
    summary=dict(schema='osr-sourced-cell-summary/1',**index,**s.FLAGS)
    archive(pub/'sourced-cell.tar.gz',[('latest.json',encoded(index),tarfile.REGTYPE)])
    (pub/'summary.json').write_bytes(encoded(summary))
    def publish(validation=None):
        m=dict(schema='osr-sourced-cell-publication/1',source_sha256=epoch,validation=deepcopy(check if validation is None else validation),
          files_sha256={n:s._sha(pub/n) for n in ('sourced-cell.tar.gz','summary.json')},**s.FLAGS)
        m['publication_id']=ident(m);(pub/'manifest.json').write_bytes(encoded(m));return m
    publish();calls=[]
    c=SimpleNamespace(identity=ident,encoded=encoded,sources=lambda root:epoch,plan=lambda:[dict(vehicle_id='V'+str(v),context=n) for v in range(1,6) for n in range(6)],read=lambda p:json.loads(Path(p).read_bytes()))
    def unreleased(value):
        if isinstance(value,dict):
            if any(k in s.FLAGS and v is not False for k,v in value.items()):raise ValueError('release')
            for v in value.values():unreleased(v)
        elif isinstance(value,list):
            for v in value:unreleased(v)
    def fresh(folder,name):
        p=Path(folder)/(name+'-0000');p.mkdir(parents=True);return p
    def execute(operation,state,**kwargs):
        calls.append(('execute',operation));where=Path(kwargs['audit']);where.mkdir(parents=True)
        rows=[]
        for v in range(1,6):
            worker=where/('V'+str(v));worker.mkdir();(worker/'input.json').write_text('{}')
            rows.append(dict(folder='V'+str(v),validated_cases=6,execution=dict(returncode=0,interrupted=False),worker_receipt_id=str(v)*64))
        initial=deepcopy(check);initial['semantic_replay_executed']=False
        report=dict(operation='replay',failures=[],semantic_replay_executed=True,source_sha256=epoch,executor_sha256=s.HELPER_SHA256,workers=rows,initial_verification=initial,source_archive_sha256='f'*64,**s.FLAGS)
        report['orchestration_id']=ident(report);return report,where
    ex=SimpleNamespace(modules=lambda root:c,unreleased=unreleased,fresh=fresh,execute=execute,ident=ident,
      bind_verified_snapshot=lambda c,state,r,root:dict(r['initial_verification']),load=lambda p:json.loads(p.read_bytes()),
      bind_replayed_canonical=lambda c,state,folder,request,epoch:calls.append(('canonical-bind',folder.name)),
      write=lambda p,v:p.write_bytes(encoded(v)))
    monkeypatch.setattr(s,'_executor',lambda root:ex)
    return SimpleNamespace(root=root,pub=pub,audit=audit,check=check,publish=publish,calls=calls,executor=ex,index=index)


def test_full_replay_and_original_validation_preserved(fixture):
    f=fixture;r=s.verify(f.pub,audit=f.audit,root=f.root)
    assert f.calls[0]==('execute','replay')
    assert {x[1] for x in f.calls if x[0]=='canonical-bind'}=={'V1','V2','V3','V4','V5'}
    assert r['actual_replayed_cases']==30 and r['actual_body_workers']==5
    assert r['original_validation']==f.check
    assert r['verification_id']==ident({k:v for k,v in r.items() if k!='verification_id'})
    assert all(r[k] is False for k in s.FLAGS)
    assert (Path(r['private_audit'])/'verification.json').exists()


@pytest.mark.parametrize('attack',['seal','epoch','flags','extra-file','file-sha','summary'])
def test_original_publication_contract_attacks(fixture,attack):
    f=fixture;m=json.loads((f.pub/'manifest.json').read_bytes())
    if attack=='seal':m['publication_id']='0'*64
    elif attack=='epoch':m['source_sha256']={};m.pop('publication_id');m['publication_id']=ident(m)
    elif attack=='flags':m['operating_release']=True;m.pop('publication_id');m['publication_id']=ident(m)
    elif attack=='extra-file':m['files_sha256']['extra']='a'*64;m.pop('publication_id');m['publication_id']=ident(m)
    elif attack=='file-sha':(f.pub/'summary.json').write_bytes(b'changed')
    elif attack=='summary':
        (f.pub/'summary.json').write_bytes(encoded({'schema':'wrong'}));m=f.publish()
    (f.pub/'manifest.json').write_bytes(encoded(m))
    with pytest.raises(ValueError):s.verify(f.pub,audit=f.audit,root=f.root)
    if attack!='summary':assert f.calls==[]


@pytest.mark.parametrize('name,kind',[('../escape',tarfile.REGTYPE),('/absolute',tarfile.REGTYPE),('x\\escape',tarfile.REGTYPE),('./noncanonical',tarfile.REGTYPE),('C:/portable-escape',tarfile.REGTYPE),('link',tarfile.SYMTYPE),('directory',tarfile.DIRTYPE)])
def test_unsafe_archive_refused_before_execution(fixture,name,kind):
    f=fixture;archive(f.pub/'sourced-cell.tar.gz',[(name,b'',kind)]);f.publish()
    with pytest.raises(ValueError):s.verify(f.pub,audit=f.audit,root=f.root)
    assert f.calls==[] and not (f.pub.parent/'escape').exists()


def test_duplicate_and_too_many_members_refused(fixture):
    f=fixture;archive(f.pub/'sourced-cell.tar.gz',[('same',b'x',tarfile.REGTYPE)]*2);f.publish()
    with pytest.raises(ValueError):s.verify(f.pub,audit=f.audit,root=f.root)
    archive(f.pub/'sourced-cell.tar.gz',[(str(i),b'x',tarfile.REGTYPE) for i in range(41)]);f.publish()
    # Fresh verification folders may remain: failed input packages are retained.
    with pytest.raises((ValueError,OSError)):s.verify(f.pub,audit=f.audit/'second',root=f.root)
    assert f.calls==[]


@pytest.mark.parametrize('attack',['failures','integrity-only','missingbody','fewcases','badworker','orchestration-seal','firstcheck','originalvalidation'])
def test_incomplete_or_forged_replay_never_passes(fixture,attack):
    f=fixture;original=f.executor.execute
    def execute(*args,**kwargs):
        r,where=original(*args,**kwargs)
        if attack=='failures':r['failures']=[{'why':'failed'}]
        elif attack=='integrity-only':r['semantic_replay_executed']=False
        elif attack=='missingbody':r['workers'].pop()
        elif attack=='fewcases':r['workers'][0]['validated_cases']=5
        elif attack=='badworker':r['workers'][0]['execution']['returncode']=2
        elif attack=='firstcheck':r['initial_verification']['pending']=1
        elif attack=='originalvalidation':r['initial_verification']['qualified_journeys']=1
        r.pop('orchestration_id');r['orchestration_id']='0'*64 if attack=='orchestration-seal' else ident(r)
        return r,where
    f.executor.execute=execute
    with pytest.raises(ValueError):s.verify(f.pub,audit=f.audit,root=f.root)


def test_private_paths_and_source_helper_tamper(fixture,monkeypatch):
    f=fixture
    with pytest.raises(ValueError):s.verify(f.pub,audit=f.pub/'inside',root=f.root)
    alias=f.pub.parent/'alias';alias.symlink_to(f.pub,target_is_directory=True)
    with pytest.raises(ValueError):s.verify(alias,audit=f.audit,root=f.root)
    assert f.calls==[]
    # Test real helperloader separately; fixture itself uses only mockexecutions.
    real=importlib.util.module_from_spec(spec);spec.loader.exec_module(real)
    with pytest.raises(ValueError,match='executor'):real._executor(f.root)


def test_source_changed_after_actual_replay_refused(fixture):
    f=fixture;original=f.executor.execute
    def execute(*args,**kwargs):
        r,w=original(*args,**kwargs);(f.root/s.HELPER).write_bytes(b'changed afterexecution');return r,w
    f.executor.execute=execute
    with pytest.raises(ValueError,match='changed'):s.verify(f.pub,audit=f.audit,root=f.root)


@pytest.mark.parametrize('name',['manifest.json','sourced-cell.tar.gz','summary.json'])
def test_symlink_publication_inputs_refused(fixture,name):
    f=fixture;outside=f.pub.parent/('outside-'+name);(f.pub/name).rename(outside);(f.pub/name).symlink_to(outside)
    with pytest.raises(ValueError):s.verify(f.pub,audit=f.audit,root=f.root)
    assert f.calls==[]


def test_expanded_archive_budget_before_execution(fixture,monkeypatch):
    f=fixture;monkeypatch.setattr(s,'MAX_EXPANDED',1)
    with pytest.raises(ValueError):s.verify(f.pub,audit=f.audit,root=f.root)
    assert f.calls==[]


def test_publication_became_linked_after_replay_refused(fixture):
    f=fixture;original=f.executor.execute
    def execute(*args,**kwargs):
        r,w=original(*args,**kwargs);a=f.pub/'sourced-cell.tar.gz';other=f.pub.parent/'same-bytes.tar.gz';a.rename(other);a.symlink_to(other);return r,w
    f.executor.execute=execute
    with pytest.raises(ValueError,match='ordinary'):s.verify(f.pub,audit=f.audit,root=f.root)
