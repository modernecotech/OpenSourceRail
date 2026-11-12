import hashlib,importlib.util,json,subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest
spec=importlib.util.spec_from_file_location('retained',Path(__file__).parents[1]/'engineering/railway_closure/retained.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args]).decode().strip()

@pytest.fixture
def packet(tmp_path,monkeypatch):
    root=tmp_path/'repo';root.mkdir();git(root,'init','-q');git(root,'config','user.name','Test');git(root,'config','user.email','test@example.invalid')
    method=root/'engineering/railway_closure/publication.py';method.parent.mkdir(parents=True)
    method.write_text('def verify(**kwargs):\n    return {"verified":True,"physical_accepted":False}\n')
    data=root/'input.json';data.write_text('original data')
    sources={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (method,data)}
    out=root/'docs/packet';out.mkdir(parents=True);(out/'manifest.json').write_text(json.dumps(dict(source_sha256=sources)));(out/'payload').write_text('original evidence')
    git(root,'add','.');git(root,'commit','-qm','original')
    monkeypatch.setattr(r.shutil,'disk_usage',lambda _:SimpleNamespace(free=r.MIN_FREE_BYTES+r.MAX_SOURCE_BYTES))
    return root,out,git(root,'rev-parse','HEAD')

def test_same_epoch_ignores_live_source_and_is_explicitly_historical(packet):
    root,out,rev=packet;(root/'engineering/railway_closure/publication.py').write_text('raise RuntimeError("live must not run")')
    (root/'input.json').write_text('live changed')
    result=r.verify(root=root,output=out,source_revision=rev)
    assert result['retained_verified'] and result['source_epoch_verified']
    assert result['source_status']=='historical' and result['current_source_valid'] is False
    assert 'verified' not in result and result['physical_accepted'] is False

def test_artifact_tamper(packet):
    root,out,rev=packet;(out/'payload').write_text('tampered')
    with pytest.raises(ValueError,match='artifact bytes'):r.verify(root=root,output=out,source_revision=rev)

def test_mixed_source_epoch(packet):
    root,out,_=packet;(root/'input.json').write_text('new epoch');git(root,'add','.');git(root,'commit','-qm','different source')
    with pytest.raises(ValueError,match='do not co-occur'):r.verify(root=root,output=out,source_revision=git(root,'rev-parse','HEAD'))

def test_native_child_process_refused(packet):
    root,out,_=packet;method=root/'engineering/railway_closure/publication.py'
    method.write_text('def verify(**kwargs):\n    import subprocess\n    subprocess.run(["true"],check=True)\n')
    m=json.loads((out/'manifest.json').read_bytes());m['source_sha256'][method.relative_to(root).as_posix()]=hashlib.sha256(method.read_bytes()).hexdigest();(out/'manifest.json').write_text(json.dumps(m))
    git(root,'add','.');git(root,'commit','-qm','native fixture')
    with pytest.raises(subprocess.CalledProcessError) as e:r.verify(root=root,output=out,source_revision=git(root,'rev-parse','HEAD'))
    assert 'cannot launch native' in e.value.stderr

@pytest.mark.parametrize('name',['../input','/input','a//b','a\\b','a/./b','a\nb'])
def test_unsafe_names(name):
    with pytest.raises(ValueError,match='Unsafe'):r.safe_name(name)

def test_disk_refusal(packet,monkeypatch):
    root,out,rev=packet;monkeypatch.setattr(r.shutil,'disk_usage',lambda _:SimpleNamespace(free=r.MIN_FREE_BYTES))
    with pytest.raises(ValueError,match='disk reserve'):r.verify(root=root,output=out,source_revision=rev)


def test_workflow_uses_same_full_pins_for_fetch_prefetch_and_verify():
    import re
    workflow=(Path(__file__).parents[1]/'.github/workflows/reconciled-pilot.yml').read_text()
    pins=re.findall(r"[0-9a-f]{35,40}",workflow)
    assert len(pins)==9 and len(set(pins))==3
    assert all(len(pin)==40 and pins.count(pin)==3 for pin in pins)


@pytest.mark.parametrize('filename',['manifest.json','payload'])
def test_sparse_oversized_tamper_refused_before_payload_reads(packet,monkeypatch,filename):
    root,out,rev=packet
    with (out/filename).open('r+b') as stream:
        stream.truncate(1024**4)
    def forbidden(*args,**kwargs):raise AssertionError('Unbounded payload read')
    monkeypatch.setattr(Path,'read_bytes',forbidden)
    with pytest.raises(ValueError,match='bytes/size'):
        r.verify(root=root,output=out,source_revision=rev)


@pytest.mark.parametrize('position',['pre','post'])
def test_foreign_project_module_import_origin_is_rejected(packet,monkeypatch,position):
    root,out,rev=packet
    poison="import types\nforeign=types.ModuleType('engineering.foreign')\nforeign.__file__='/foreign/current/engineering/foreign.py'\nsys.modules['engineering.foreign']=foreign\n"
    if position=='pre':
        child=r.CHILD.replace('require_project_origins()\nfrom engineering',poison+'require_project_origins()\nfrom engineering')
    else:
        child=r.CHILD.replace('print(json.dumps(dict(original_checker_result=',poison+'print(json.dumps(dict(original_checker_result=')
    monkeypatch.setattr(r,'CHILD',child)
    with pytest.raises(subprocess.CalledProcessError) as exc:
        r.verify(root=root,output=out,source_revision=rev)
    assert 'import escaped historical epoch' in exc.value.stderr
