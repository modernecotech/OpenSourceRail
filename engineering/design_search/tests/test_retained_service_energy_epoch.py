import hashlib
import json
import os
from pathlib import Path

import pytest

from engineering.design_search import retained_service_energy_epoch as epoch
from engineering.design_search import retained_source_epoch as retained


def make_pins():
    pins=dict(schema='osr-service-energy-extra-external-pins/1',git_commit=epoch.GIT_COMMIT,
        manifest_ids={name:'a'*64 for name in epoch.CATALOG},
        manifest_sha256={name:'b'*64 for name in epoch.CATALOG},storage_id='c'*64,
        storage_sha256='d'*64,companion_manifest_id='e'*64,companion_manifest_sha256='f'*64)
    pins['pins_id']=retained._id(pins)
    return pins


@pytest.fixture
def isolated(tmp_path,monkeypatch):
    root=tmp_path/'root';root.mkdir();(root/'source.py').write_text('original source\n')
    sources={'source.py':hashlib.sha256((root/'source.py').read_bytes()).hexdigest()}
    data=dict(records={'record':{'id':'1'}},folders={'folder':{'files_sha256':{}}},
        sources=sources,sourced_transport={'test':True},physical_followup={'separate':True})
    monkeypatch.setattr(epoch,'_git_anchor',lambda root,pins:None)
    monkeypatch.setattr(epoch,'_records',lambda root,pins:data)
    return root,data,make_pins()


def test_external_pin_completeness_and_seal():
    pins=make_pins();assert epoch._pins(pins,pins['pins_id'])==pins
    wrong=dict(pins,git_commit='0'*40)
    with pytest.raises(ValueError,match='pinned'):
        epoch._pins(wrong,pins['pins_id'])
    with pytest.raises(ValueError,match='pinned'):
        epoch._pins(pins,'0'*64)
    missing=dict(pins,manifest_ids={})
    missing['pins_id']=retained._id({k:v for k,v in missing.items() if k!='pins_id'})
    with pytest.raises(ValueError,match='pinned'):
        epoch._pins(missing,missing['pins_id'])
    malformed=dict(pins,manifest_ids=None)
    malformed['pins_id']=retained._id({k:v for k,v in malformed.items() if k!='pins_id'})
    with pytest.raises(ValueError,match='pinned'):
        epoch._pins(malformed,malformed['pins_id'])


def test_historical_capture_and_verify_roundtrip(isolated,tmp_path):
    root,data,pins=isolated;out=tmp_path/'archive'
    meta=epoch.capture(root,out,pins=pins,expected_pins_id=pins['pins_id'])
    result=epoch.verify(root,out,pins=pins,expected_pins_id=pins['pins_id'],expected_archive_id=meta['archive_id'])
    assert result['verified'] and result['current_evaluator_admission'] is False
    assert result['physical_accepted'] is False and result['numerical_reexecuted'] is False
    helper_sha=hashlib.sha256(Path(retained.__file__).read_bytes()).hexdigest()
    assert result['capture_helper_sha256']==helper_sha
    assert result['verifier_helper_sha256']==helper_sha
    with pytest.raises(ValueError,match='destination'):
        epoch.capture(root,out,pins=pins,expected_pins_id=pins['pins_id'])


def test_archive_extra_member_and_trailing_data_fail_even_if_resealed(isolated,tmp_path):
    root,data,pins=isolated;out=tmp_path/'archive'
    meta=epoch.capture(root,out,pins=pins,expected_pins_id=pins['pins_id'])
    (root/'extra.py').write_text('unlisted\n')
    extra=dict(data['sources'],**{'extra.py':hashlib.sha256((root/'extra.py').read_bytes()).hexdigest()})
    raw=retained._make_archive(root,extra);(out/'sources.tar.gz').write_bytes(raw)
    meta['source_archive_sha256']=hashlib.sha256(raw).hexdigest()
    meta['archive_id']=retained._id({k:v for k,v in meta.items() if k!='archive_id'})
    (out/'manifest.json').write_bytes(retained._encoded(meta))
    with pytest.raises(ValueError,match='membership|source bytes'):
        epoch.verify(root,out,pins=pins,expected_pins_id=pins['pins_id'],expected_archive_id=meta['archive_id'])
    raw+=retained._make_archive(root,data['sources']);(out/'sources.tar.gz').write_bytes(raw)
    meta['source_archive_sha256']=hashlib.sha256(raw).hexdigest()
    meta['archive_id']=retained._id({k:v for k,v in meta.items() if k!='archive_id'})
    (out/'manifest.json').write_bytes(retained._encoded(meta))
    with pytest.raises(ValueError,match='gzip|trailing|archive'):
        epoch.verify(root,out,pins=pins,expected_pins_id=pins['pins_id'],expected_archive_id=meta['archive_id'])


def test_false_promotion_rejected_even_if_archive_is_resealed(isolated,tmp_path):
    root,data,pins=isolated;out=tmp_path/'archive';meta=epoch.capture(root,out,pins=pins,expected_pins_id=pins['pins_id'])
    meta['physical_accepted']=True;meta['archive_id']=retained._id({k:v for k,v in meta.items() if k!='archive_id'})
    (out/'manifest.json').write_bytes(retained._encoded(meta))
    with pytest.raises(ValueError,match='disposition'):
        epoch.verify(root,out,pins=pins,expected_pins_id=pins['pins_id'],expected_archive_id=meta['archive_id'])
    for key in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'):
        value={k:False for k in epoch.FLAGS};value[key]=True
        with pytest.raises(ValueError,match='release'):epoch._held(value)


def test_packet_inventory_rejects_links_and_special_files(tmp_path):
    folder=tmp_path/'folder';folder.mkdir();(folder/'ok').write_text('x')
    (folder/'link').symlink_to(folder/'ok')
    with pytest.raises(ValueError,match='ordinary'):epoch._inventory(folder)
    (folder/'link').unlink();os.link(folder/'ok',folder/'hardlink')
    with pytest.raises(ValueError,match='Hard-linked'):epoch._inventory(folder)
    (folder/'hardlink').unlink();os.mkfifo(folder/'fifo')
    with pytest.raises(ValueError,match='ordinary'):epoch._inventory(folder)


def test_capture_rejects_hardlinked_source(isolated,tmp_path):
    root,data,pins=isolated
    os.link(root/'source.py',root/'other-link.py')
    with pytest.raises(ValueError,match='Hard-linked'):
        epoch.capture(root,tmp_path/'archive',pins=pins,expected_pins_id=pins['pins_id'])


def test_source_epoch_conflicts_rejected_before_companion_processing(tmp_path,monkeypatch):
    cat={'a/manifest.json':('demo/1','manifest_id','source_sha256','files'),
         'b/manifest.json':('demo/1','manifest_id','source_sha256','files')}
    monkeypatch.setattr(epoch,'CATALOG',cat);root=tmp_path/'root';pins={'manifest_ids':{},'manifest_sha256':{}}
    for name,letter in [('a/manifest.json','a'),('b/manifest.json','b')]:
        value=dict(schema='demo/1',source_sha256={'source.py':letter*64},files_sha256={'payload':'f'*64},
            physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
        value['manifest_id']=retained._id(value);path=root/epoch.PREFIX/name;path.parent.mkdir(parents=True,exist_ok=True)
        raw=retained._encoded(value);path.write_bytes(raw);pins['manifest_ids'][name]=value['manifest_id'];pins['manifest_sha256'][name]=hashlib.sha256(raw).hexdigest()
    monkeypatch.setattr(epoch,'_inventory',lambda _:dict(files_sha256={'payload':'f'*64},directories=[],file_count=1,entry_count=1,bytes=1))
    with pytest.raises(ValueError,match='Conflicting current source epoch'):
        epoch._records(root,pins)


def test_source_path_traversal_rejected():
    with pytest.raises(ValueError,match='relative'):
        retained._checked_map({'../outside':'a'*64})


def test_missing_git_object_fails_without_fetch(tmp_path):
    with pytest.raises(ValueError,match='Git object'):
        epoch._git_bytes(tmp_path,'docs/design-engine/example.json')


def test_git_anchor_disables_lazy_fetch_and_environment_overrides(tmp_path,monkeypatch):
    monkeypatch.setenv('GIT_CONFIG_PARAMETERS',"'core.foo=malicious'")
    monkeypatch.setenv('GIT_NAMESPACE','other')
    calls=[]
    def run(cmd,**kwargs):
        env=kwargs['env'];calls.append(cmd)
        assert env['GIT_NO_LAZY_FETCH']=='1' and env['GIT_NO_REPLACE_OBJECTS']=='1'
        assert 'GIT_CONFIG_PARAMETERS' not in env and 'GIT_NAMESPACE' not in env
        return type('Result',(),{'returncode':0,'stdout':b'2\n' if 'cat-file' in cmd else b'{}'})()
    monkeypatch.setattr(epoch.subprocess,'run',run)
    assert epoch._git_bytes(tmp_path,'docs/design-engine/example.json')==b'{}'
    assert len(calls)==2


def test_capture_detects_changed_packet_before_handoff_and_keeps_stage(isolated,tmp_path,monkeypatch):
    root,data,pins=isolated;calls=0
    def records(*_):
        nonlocal calls
        calls+=1
        return data if calls<3 else dict(data,records={'changed':True})
    monkeypatch.setattr(epoch,'_records',records);out=tmp_path/'archive'
    with pytest.raises(ValueError,match='changed'):
        epoch.capture(root,out,pins=pins,expected_pins_id=pins['pins_id'])
    assert not out.exists() and list(tmp_path.glob('.service-energy-extra-*'))


def make_sourced(folder):
    payload=b'abcdefghijk';parts=[payload[:6],payload[6:]];chunk_rows=[]
    for i,part in enumerate(parts):
        name=f'sourced-cell.part-{i:03d}';(folder/name).write_bytes(part)
        chunk_rows.append(dict(path=name,bytes=len(part),sha256=hashlib.sha256(part).hexdigest()))
    (folder/'sourced-cell.tar.gz').write_bytes(payload);sha=hashlib.sha256(payload).hexdigest()
    manifest=dict(publication_id='a'*64,files_sha256={'sourced-cell.tar.gz':sha})
    value=dict(schema='osr-sourced-cell-chunk-storage/1',publication_id=manifest['publication_id'],
        publication_manifest_sha256='b'*64,chunk_bytes=6,
        archive_path='sourced-cell.tar.gz',archive_sha256=sha,total_bytes=len(payload),chunks=chunk_rows,
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
    value['storage_id']=retained._id(value);raw=retained._encoded(value);(folder/'storage.json').write_bytes(raw)
    return manifest,dict(storage_id=value['storage_id'],storage_sha256=hashlib.sha256(raw).hexdigest(),
        manifest_sha256={'sourced-case/manifest.json':'b'*64})


def test_sourced_archive_must_match_pinned_chunk_concatenation(tmp_path):
    manifest,pins=make_sourced(tmp_path);result=epoch._storage(tmp_path,manifest,pins)
    assert result['chunk_count']==2 and result['archive_git_tracking']=='not asserted by this verifier'
    (tmp_path/'sourced-cell.part-001').write_bytes(b'altered')
    with pytest.raises(ValueError,match='chunk'):
        epoch._storage(tmp_path,manifest,pins)


def test_sourced_archive_missing_does_not_infer_or_reassemble(tmp_path):
    manifest,pins=make_sourced(tmp_path);(tmp_path/'sourced-cell.tar.gz').unlink()
    with pytest.raises(ValueError,match='reassemble pinned chunks'):
        epoch._storage(tmp_path,manifest,pins)
    assert not (tmp_path/'sourced-cell.tar.gz').exists()


def test_sourced_storage_must_bind_the_original_manifest(tmp_path):
    manifest,pins=make_sourced(tmp_path)
    pins['manifest_sha256']['sourced-case/manifest.json']='c'*64
    with pytest.raises(ValueError,match='chunk storage'):
        epoch._storage(tmp_path,manifest,pins)
