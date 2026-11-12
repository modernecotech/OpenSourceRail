"""Typed historical driver fixtures do not qualify physical twin/motor models."""
import hashlib,io,json,subprocess,tarfile
from pathlib import Path
from types import SimpleNamespace
import pytest
from engineering.railway_twin import retained as r


def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args]).decode().strip()


@pytest.fixture(params=['twin','motor','cell'])
def packet(request,tmp_path,monkeypatch):
    domain=request.param;root=tmp_path/'repo';root.mkdir()
    git(root,'init','-q');git(root,'config','user.name','Test');git(root,'config','user.email','test@example.invalid')
    cfg=r.CATALOG[domain];method=root/cfg['producer'];method.parent.mkdir(parents=True)
    method.write_text('def verify_publication(*args,**kwargs):\n    return {"verified":True,"physical_accepted":False}\n')
    folder=root/cfg['folder'];folder.mkdir(parents=True);payload=folder/'payload.tar.gz'
    with tarfile.open(payload,'w:gz') as archive:
        raw=b'{"fixture":true}\n';member=tarfile.TarInfo('fixture.json');member.size=len(raw);archive.addfile(member,io.BytesIO(raw))
    manifest=dict(schema=cfg['schema'],source_sha256={cfg['producer']:hashlib.sha256(method.read_bytes()).hexdigest()})
    sha=hashlib.sha256(payload.read_bytes()).hexdigest()
    if domain in ('twin','cell'):manifest['files_sha256']={payload.name:sha}
    else:manifest.update(archive=payload.name,archive_sha256=sha)
    (folder/cfg['manifest']).write_text(json.dumps(manifest))
    git(root,'add','.');git(root,'commit','-qm','original fixture')
    revision=git(root,'rev-parse','HEAD');monkeypatch.setattr(r,'REVISION',revision)
    monkeypatch.setattr(r.shutil,'disk_usage',lambda _:SimpleNamespace(free=r.MAX_TEMP+r.epoch.MIN_FREE_BYTES+1))
    return root,domain,revision,tmp_path/'state',method,payload


def check(packet):
    root,domain,revision,state,*_=packet
    return r.verify(root,domain,state,source_revision=revision)


def test_two_original_typed_domains_are_explicitly_historical(packet):
    root,domain,rev,state,*_=packet;before=git(root,'status','--porcelain')
    result=check(packet)
    assert result['retained_verified'] and result['method_replay_completed']
    assert result['current_source_valid'] is False and 'verified' not in result
    assert result['native_processes']==result['native_solver_executions']==0
    assert all(result[key] is False for key in r.FLAGS)
    assert not (state/'epoch').exists()
    assert git(root,'status','--porcelain')==before


def test_wrong_epoch_is_refused(packet):
    root,domain,rev,state,*_=packet
    with pytest.raises(ValueError,match='Exact pinned'):
        r.verify(root,domain,state,source_revision='0'*40)


def test_artifact_tampering_fails_before_method(packet):
    root,domain,rev,state,method,payload=packet;payload.write_bytes(b'changed')
    with pytest.raises(ValueError,match='artifact size'):check(packet)
    assert not (state/'epoch').exists()


def test_source_bindings_must_cooccur_at_one_epoch(packet,monkeypatch):
    root,domain,rev,state,method,payload=packet;method.write_text(method.read_text()+'\n# changed producer\n')
    git(root,'add','.');git(root,'commit','-qm','changed source only');new=git(root,'rev-parse','HEAD')
    monkeypatch.setattr(r,'REVISION',new)
    with pytest.raises(ValueError,match='do not co-occur'):
        r.verify(root,domain,state,source_revision=new)


def test_oversized_live_manifest_refused_before_read(packet,monkeypatch):
    root,domain,rev,state,*_=packet
    with (root/r.CATALOG[domain]['folder']/r.CATALOG[domain]['manifest']).open('r+b') as stream:stream.truncate(1024**4)
    with pytest.raises(ValueError,match='artifact size'):check(packet)


def test_unexpected_native_process_is_refused_and_inputs_preserved(packet,monkeypatch):
    root,domain,rev,state,method,payload=packet
    method.write_text('def verify_publication(*args,**kwargs):\n    import subprocess\n    subprocess.run(["true"],check=True)\n')
    p=root/r.CATALOG[domain]['folder']/r.CATALOG[domain]['manifest'];m=json.loads(p.read_bytes());m['source_sha256'][r.CATALOG[domain]['producer']]=hashlib.sha256(method.read_bytes()).hexdigest();p.write_text(json.dumps(m))
    git(root,'add','.');git(root,'commit','-qm','native fixture method');new=git(root,'rev-parse','HEAD');monkeypatch.setattr(r,'REVISION',new)
    with pytest.raises(ValueError,match='Original checker failed'):r.verify(root,domain,state,source_revision=new)
    assert 'cannot launch native' in (state/'stderr.txt').read_text()
    assert (state/'epoch'/r.CATALOG[domain]['producer']).is_file()
    assert json.loads((state/'receipt.json').read_bytes())['retained_verified'] is False


def test_foreign_import_is_refused(packet,monkeypatch):
    poison="import types\nforeign=types.ModuleType('engineering.foreign')\nforeign.__file__='/current/engineering/foreign.py'\nsys.modules['engineering.foreign']=foreign\n"
    monkeypatch.setattr(r,'CHILD',r.CHILD.replace("if sys.argv[3]=='twin':",poison+"if sys.argv[3]=='twin':"))
    with pytest.raises(ValueError,match='Original checker failed'):check(packet)
    assert 'import escaped historical epoch' in (packet[3]/'stderr.txt').read_text()
