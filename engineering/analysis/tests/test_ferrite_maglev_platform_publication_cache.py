"""Fresh-byte memoization never trusts retained publication checksums as truth."""
from hashlib import sha256
import json

import pytest

from engineering.ferrite_maglev import platform_publication as publication


@pytest.fixture
def planning(tmp_path,monkeypatch):
    source=tmp_path/'input.txt';source.write_text('source-A')
    calls=[]
    def sources():return {'input.txt':sha256(source.read_bytes()).hexdigest()}
    def generate():
        calls.append(source.read_text())
        return {'index.json':json.dumps({'value':source.read_text()},sort_keys=True).encode(),
                'cities/test.json.gz':b'declared immutable fresh bytes','README.md':b'Unaccepted planning study\n'}
    monkeypatch.setattr(publication,'sources',sources)
    monkeypatch.setattr(publication,'folders',lambda:[tmp_path])
    monkeypatch.setattr(publication,'_generate_payload',generate)
    monkeypatch.setattr(publication,'_PAYLOAD_CACHE',None)
    return source,calls,tmp_path/'publication'


def test_publish_then_verify_generates_once_and_checks_retained_bytes(planning):
    _,calls,output=planning
    publication.publish(output)
    assert publication.verify(output)['verified']
    assert calls==['source-A']


def test_coherently_resealed_retained_tamper_is_rejected_with_warm_cache(planning):
    _,calls,output=planning
    publication.publish(output)
    altered=b'{"value":"fabricated-retained-result"}'
    (output/'index.json').write_bytes(altered)
    path=output/'manifest.json';manifest=json.loads(path.read_bytes())
    manifest['files_sha256']['index.json']=sha256(altered).hexdigest()
    path.write_bytes(publication.platform.encoded(manifest))
    with pytest.raises(ValueError,match='derived data differs'):publication.verify(output)
    assert calls==['source-A']


def test_input_source_change_invalidates_cached_snapshot(planning):
    source,calls,output=planning
    first=publication.payload();publication.publish(output)
    source.write_text('source-B')
    with pytest.raises(ValueError,match='stale'):publication.verify(output)
    second=publication.payload()
    assert second['index.json']!=first['index.json']
    assert calls==['source-A','source-B']
    publication.publish(output)
    assert publication.verify(output)['verified']
    assert calls==['source-A','source-B']


def test_caller_mapping_mutation_cannot_poison_cached_bytes(planning):
    _,calls,_=planning
    first=publication.payload();expected=dict(first)
    first['index.json']=b'poison';first.pop('README.md');first['extra']=b'poison'
    assert publication.payload()==expected
    assert calls==['source-A']


def test_mid_generation_source_drift_does_not_populate_cache(planning,monkeypatch):
    source,calls,_=planning
    original=publication._generate_payload
    def drifting():
        result=original();source.write_text('source-B');return result
    monkeypatch.setattr(publication,'_generate_payload',drifting)
    with pytest.raises(ValueError,match='source changed during generation'):publication.payload()
    assert publication._PAYLOAD_CACHE is None
    monkeypatch.setattr(publication,'_generate_payload',original)
    result=publication.payload()
    assert json.loads(result['index.json'])['value']=='source-B'
    assert calls==['source-A','source-B']


def test_mid_generation_drift_does_not_replace_prior_valid_snapshot(planning,monkeypatch):
    source,calls,_=planning
    publication.payload();prior=publication._PAYLOAD_CACHE
    source.write_text('source-B');original=publication._generate_payload
    def drifting():
        result=original();source.write_text('source-C');return result
    monkeypatch.setattr(publication,'_generate_payload',drifting)
    with pytest.raises(ValueError,match='source changed during generation'):publication.payload()
    assert publication._PAYLOAD_CACHE==prior
    assert calls==['source-A','source-B']


def test_complete_source_mapping_is_keyed_including_names(planning,monkeypatch):
    _,calls,_=planning
    snapshot={'a.txt':'a'*64};monkeypatch.setattr(publication,'sources',lambda:dict(snapshot))
    publication.payload();snapshot.clear();snapshot['b.txt']='a'*64
    publication.payload()
    assert calls==['source-A','source-A']


def test_snapshot_cache_retains_only_last_source_key(planning):
    source,calls,_=planning
    publication.payload();source.write_text('source-B');publication.payload()
    source.write_text('source-A');publication.payload()
    assert calls==['source-A','source-B','source-A']


def test_mutable_generated_byte_buffers_are_not_cached(planning,monkeypatch):
    monkeypatch.setattr(publication,'_generate_payload',lambda:{'index.json':bytearray(b'not immutable')})
    with pytest.raises(ValueError,match='immutable planning payload bytes'):publication.payload()
    assert publication._PAYLOAD_CACHE is None
