"""Recovery must fail closed and must never reuse live volumes or connections."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('platform_recovery',ROOT/'tools/automation/platform-recovery.py')
recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)


@pytest.fixture
def bundle(tmp_path):
    root=tmp_path/'checkpoint';root.mkdir()
    for name in ['ops.zip','ops.signing-key','volume.tar']:(root/name).write_bytes(b'fixture')
    state=dict(services={'integration':dict(image='sha256:'+'a'*64,volumes=[dict(type='volume',source='live',target='/data')])},volumes={'live':dict(key='v0',archive='volume.tar')})
    (root/'state.json').write_text(json.dumps(state))
    manifest=dict(schema='osr-platform-checkpoint/1',complete=True,files={p.name:dict(bytes=p.stat().st_size,sha256=recovery.sha(p)) for p in root.iterdir()})
    (root/'manifest.json').write_text(json.dumps(manifest))
    return root


def test_exact_checkpoint_membership_and_hashes(bundle):
    recovery.verify(bundle)
    (bundle/'volume.tar').write_bytes(b'changed')
    with pytest.raises(ValueError,match='changed'):recovery.verify(bundle)


@pytest.mark.parametrize('mutation',['extra','missing','symlink','incomplete','unlisted-volume','unlisted-bind','mutable-image','missing-image-archive'])
def test_invalid_checkpoints_rejected(bundle,mutation):
    manifest=json.loads((bundle/'manifest.json').read_text());state=json.loads((bundle/'state.json').read_text())
    if mutation=='extra':(bundle/'extra').write_text('no')
    elif mutation=='missing':(bundle/'ops.signing-key').unlink()
    elif mutation=='symlink':(bundle/'link').symlink_to(bundle/'ops.zip')
    elif mutation=='incomplete':manifest['complete']=False
    elif mutation=='unlisted-volume':state['volumes']['live']['archive']='missing.tar'
    elif mutation=='unlisted-bind':state['services']['integration']['volumes']=[dict(type='bind',source='../secret',target='/run/config')]
    elif mutation=='missing-image-archive':state['images_archive']='missing.tar'
    elif mutation=='mutable-image':state['services']['integration']['image']='latest'
    (bundle/'state.json').write_text(json.dumps(state))
    manifest['files']['state.json']=dict(bytes=(bundle/'state.json').stat().st_size,sha256=recovery.sha(bundle/'state.json'))
    (bundle/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError):recovery.verify(bundle)


def test_clone_remaps_every_volume_and_disables_automatic_erp_delivery(tmp_path):
    source=tmp_path/'checkpoint';source.mkdir();private=tmp_path/'clone';private.mkdir()
    credentials=dict(erp=dict(url='http://live-erp',key='test-key',secret='test-secret'),principals=[])
    (source/'integration.json').write_text(json.dumps(credentials))
    state=dict(volumes={'source-volume':dict(key='v0')},services={'integration':dict(image='sha256:'+'a'*64,
        volumes=[dict(type='volume',source='source-volume',target='/data'),dict(type='bind',source='integration.json',target='/run/secrets/integration.json')])})
    before=copy.deepcopy(state)
    clone=recovery.clone_config(state,source,private,'unique-project',28880)
    assert clone['networks']=={'default':{'internal':True}}
    assert clone['volumes']=={'v0':{}}
    service=clone['services']['integration']
    assert service['volumes'][0]['source']=='v0'
    assert 'ports' not in service
    assert service['restart']=='no'
    assert service['pull_policy']=='never'
    assert 'erp' not in json.loads(Path(service['volumes'][1]['source']).read_text())
    assert json.loads((source/'integration.json').read_text())==credentials
    assert state==before


@pytest.mark.parametrize('name',['../x','/x','a/../b','a\\b','a//b',''])
def test_unsafe_members_rejected(name):
    with pytest.raises(ValueError):recovery.safe_relative(name)


def test_duplicate_manifest_keys_rejected(bundle):
    p=bundle/'manifest.json';p.write_text(p.read_text().replace('"complete": true','"complete": false, "complete": true'))
    with pytest.raises(ValueError,match='Duplicate'):recovery.verify(bundle)


@pytest.mark.parametrize('record',[{'bytes':True,'sha256':'a'*64},{'bytes':-1,'sha256':'a'*64},{'bytes':1,'sha256':'oops'}])
def test_malformed_integrity_entry_rejected(bundle,record):
    p=bundle/'manifest.json';m=json.loads(p.read_text());m['files']['ops.zip']=record;p.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='Invalid checksum'):recovery.verify(bundle)
