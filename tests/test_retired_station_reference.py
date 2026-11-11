"""Synthetic Git fixtures do not admit railway evidence; the real pin is separate."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

FILE=Path(__file__).resolve().parents[1]/'engineering/station_rail/retired_station_reference.py'
spec=importlib.util.spec_from_file_location('retired_station_under_test',FILE)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def write(root,name,value):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(r.encoded(value) if isinstance(value,dict) else value)


def sealed(value,key):value[key]=r.identity(value);return value


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    root=tmp_path
    subprocess.run(['git','init','-q','--initial-branch=fixture'],cwd=root,check=True)
    subprocess.run(['git','config','user.name','Fixture'],cwd=root,check=True)
    subprocess.run(['git','config','user.email','fixture@example.invalid'],cwd=root,check=True)
    write(root,r.PRODUCER,FILE.read_bytes());write(root,'source.py',b'old-source=1\n')
    write(root,'engineering/development-baseline.toml',b'schema="fixture"\n')
    write(root,'docs/workbench/current/app.js',b'old interface\n')
    write(root,'OpenSourceRail-Book.pdf',b'opaque old book fixture\n')
    prefix='docs/design-engine/research/'
    value=sealed(dict(source='fixture',**{k:False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release')}),'portfolio_id')
    write(root,prefix+'result.json',value);write(root,prefix+'extra.txt',b'committed unmanifested diagnostic\n')
    m=sealed(dict(schema='fixture-research/1',source_sha256={'source.py':r._hash(root/'source.py')},files_sha256={'result.json':r._hash(root/prefix/'result.json')}),'manifest_id');write(root,prefix+'manifest.json',m)
    dossier='docs/design-engine/current/'
    write(root,dossier+'native-drive.tar.gz',b'opaque old native fixture\n')
    write(root,dossier+'summary.json',dict(schema='osr-current-design/1',selection_id=r.identity(dict(schema='fixture'))))
    selector=dict(schema='fixture')
    current=sealed(dict(schema='osr-current-publication/1',selection_id=r.identity(selector),evaluation_id='a'*64,
        candidate_id='b'*64,body_candidate_id='c'*64,support_component_id='d'*64,propulsion_component_id='e'*64,
        source_sha256={'source.py':r._hash(root/'source.py')},
        files_sha256={'native-drive.tar.gz':r._hash(root/dossier/'native-drive.tar.gz'),'summary.json':r._hash(root/dossier/'summary.json')},
        linked_artifacts_sha256={'OpenSourceRail-Book.pdf':r._hash(root/'OpenSourceRail-Book.pdf')},
        workbench_files_sha256={'app.js':r._hash(root/'docs/workbench/current/app.js')},
        **{k:False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release')}),'manifest_id')
    write(root,dossier+'manifest.json',current)
    subprocess.run(['git','add','.'],cwd=root,check=True);subprocess.run(['git','commit','-q','-m','Fixture'],cwd=root,check=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    monkeypatch.setattr(r,'COMMIT',commit);monkeypatch.setattr(r,'PACKETS',{'research':('source_sha256','files_sha256','manifest_id',('result.json','portfolio_id'))})
    v=r._snapshot(root);monkeypatch.setattr(r,'EXPECTED_RECEIPT_ID',v['retention_id']);write(root,r.OUTPUT+'/manifest.json',v);r._cache.clear()
    yield root,v
    r._cache.clear()


def test_git_archive_and_retired_paths_are_bound_without_old_source_dependencies(fixture):
    root,m=fixture;v=r.verify(root)
    assert v['verified'] and v['reference_selection_id']==m['reference_selection_id']
    assert all(v[k] is False for k in r.FLAGS)
    assert 'source.py' not in v['dependency_sha256']
    assert 'docs/design-engine/current/native-drive.tar.gz' not in v['dependency_sha256']
    assert 'docs/design-engine/research/extra.txt' in v['dependency_sha256']
    assert r.PRODUCER in v['dependency_sha256']
    assert 'docs/design-engine/current/native-drive.tar.gz' in m['git_files']
    assert 'OpenSourceRail-Book.pdf' in m['git_files']


def test_new_active_source_and_current_dossier_do_not_rewrite_old_evidence(fixture):
    root,_=fixture;r.verify(root)
    write(root,'source.py',b'new active source\n')
    write(root,'docs/design-engine/current/native-drive.tar.gz',b'new active native output\n')
    write(root,'engineering/development-baseline.toml',b'new active policy\n')
    assert r.verify(root)['verified']


def test_evolved_coupled_packet_is_checked_separately_from_retired_git_bytes(fixture,monkeypatch):
    root,_=fixture
    folder=root/'docs/design-engine/coupled-railway'
    write(root,'docs/design-engine/coupled-railway/README.md',b'original coupled packet\n')
    old_packet=sealed(dict(schema='fixture-coupled/1',source_sha256={},
        files_sha256={'README.md':r._hash(folder/'README.md')},
        **{k:False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release')}),'manifest_id')
    write(root,'docs/design-engine/coupled-railway/manifest.json',old_packet)
    subprocess.run(['git','add','.'],cwd=root,check=True)
    subprocess.run(['git','commit','-q','-m','Pinned coupled packet'],cwd=root,check=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    monkeypatch.setattr(r,'COMMIT',commit)
    monkeypatch.setattr(r,'PACKETS',{
        'research':('source_sha256','files_sha256','manifest_id',('result.json','portfolio_id')),
        'coupled-railway':('source_sha256','files_sha256','manifest_id',None),
    })
    retired=r._snapshot(root)
    monkeypatch.setattr(r,'EXPECTED_RECEIPT_ID',retired['retention_id'])
    write(root,r.OUTPUT+'/manifest.json',retired)

    # The live packet advances, while the exact old bytes remain in COMMIT.
    addition=folder/'native/current.tar.gz';addition.parent.mkdir(parents=True,exist_ok=True);addition.write_bytes(b'new source-bound packet\n')
    current=json.loads((folder/'manifest.json').read_bytes())
    current['files_sha256']['native/current.tar.gz']=r._hash(addition)
    current.pop('manifest_id');current['manifest_id']=r.identity(current)
    write(root,'docs/design-engine/coupled-railway/manifest.json',current)
    def verify_current(root_arg):
        manifest=json.loads((Path(root_arg)/'docs/design-engine/coupled-railway/manifest.json').read_bytes())
        assert manifest['manifest_id']==r.identity({k:v for k,v in manifest.items() if k!='manifest_id'})
        assert r._hash(Path(root_arg)/'docs/design-engine/coupled-railway/native/current.tar.gz')==manifest['files_sha256']['native/current.tar.gz']
        return dict(verified=True,manifest_id=manifest['manifest_id']),list((Path(root_arg)/'docs/design-engine/coupled-railway').rglob('*'))
    monkeypatch.setattr(r,'_verify_current_coupled_packet',verify_current)
    r._cache.clear()
    result=r.verify(root)
    assert result['verified'] and result['historical_payloads_verified_from_pinned_git'] is True
    assert result['active_packet_manifest_ids']=={'coupled-railway':current['manifest_id']}
    assert 'docs/design-engine/coupled-railway/README.md' not in result['dependency_sha256']


def test_retired_packet_payload_tampering_is_not_accepted(fixture):
    root,_=fixture;r.verify(root);write(root,'docs/design-engine/research/result.json',b'changed\n')
    with pytest.raises(ValueError,match='payload changed'):r.verify(root)


def test_resealed_replacement_receipt_cannot_change_pins(fixture):
    root,v=fixture;v=deepcopy(v);v['git_files']['source.py']['sha256']='0'*64;v.pop('retention_id');sealed(v,'retention_id');write(root,r.OUTPUT+'/manifest.json',v)
    with pytest.raises(ValueError,match='fixed pin'):r.verify(root)


def test_missing_exact_history_holds_without_using_current_head(fixture,monkeypatch):
    root,_=fixture;monkeypatch.setattr(r,'COMMIT','0'*40)
    with pytest.raises(ValueError,match='fetch exact commit'):r.verify(root)


def test_symlinked_retired_payload_is_rejected(fixture):
    root,_=fixture;p=root/'docs/design-engine/research/extra.txt';p.unlink();p.symlink_to(root/'source.py')
    with pytest.raises(ValueError,match='Linked retired'):r.verify(root)


def test_external_git_alternates_are_not_silently_used(fixture):
    root,_=fixture;write(root,'.git/objects/info/alternates',b'/outside/object-store\n')
    with pytest.raises(ValueError,match='alternates'):r.verify(root)


def test_changed_pinned_object_storage_invalidates_cached_byte_verification(fixture):
    root,v=fixture;r.verify(root);oid=v['git_files']['source.py']['git_blob'];obj=root/'.git/objects'/oid[:2]/oid[2:]
    obj.chmod(0o644);obj.write_bytes(b'corrupt Git object')
    with pytest.raises(ValueError,match='blob missing|history is unavailable'):r.verify(root)


def test_unexpected_extra_comparison_file_is_rejected(fixture):
    root,_=fixture;write(root,'docs/design-engine/research/new.txt',b'not pinned')
    with pytest.raises(ValueError,match='inventory changed'):r.verify(root)


def test_loaded_verifier_cannot_publish_a_different_root_source_hash(fixture):
    root,_=fixture;write(root,r.PRODUCER,b'changed verifier source')
    with pytest.raises(ValueError,match='verifier source differs'):r.verify(root)


def test_reference_artifact_helpers_return_old_bytes_and_explicit_nonadmission(fixture):
    root,v=fixture;write(root,'docs/design-engine/current/native-drive.tar.gz',b'new active output')
    raw,meta=r.reference_archive('drive',root)
    assert raw==b'opaque old native fixture\n' and meta['sha256']==v['git_files']['docs/design-engine/current/native-drive.tar.gz']['sha256']
    assert all(meta[k] is False for k in r.FLAGS)
    summary,manifest=r.reference_current(root)
    assert summary['selection_id']==manifest['selection_id']==v['reference_selection_id']
    with pytest.raises(ValueError,match='Named retired'):r.reference_archive('../drive',root)
    with pytest.raises(ValueError,match='Known pinned'):r.reference_bytes('/outside',root)
