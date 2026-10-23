"""One fresh connected-pilot qualification per primary publication operation."""
from hashlib import sha256
import json

import pytest

from engineering.ferrite_maglev import delivery, pilot_release


@pytest.fixture
def connected(monkeypatch, tmp_path):
    """A real semantic parent receipt with a separately mutable child receipt.

    Only the unrelated expensive engineering studies are replaced. The parent
    publisher/verifier, source binding and retained-byte checks remain real.
    """
    output=tmp_path/'pilot';output.mkdir()
    child=tmp_path/'child-manifest.json';child.write_bytes(b'original child receipt')
    monkeypatch.setattr(pilot_release,'OUTPUT',output)
    value=dict(schema=pilot_release.SCHEMA,components=[],digital_profiles_executed=False,
               source_sha256=pilot_release.sources(),**delivery.model.FLAGS)
    monkeypatch.setattr(pilot_release,'study',lambda:value)
    monkeypatch.setattr(pilot_release,'readme',lambda value,output:'Fixture; physical acceptance open.')
    pilot_release.publish(output)
    counts=[]
    original=pilot_release.verify
    def counted(*args,**kwargs):
        counts.append(1)
        return original(*args,**kwargs)
    monkeypatch.setattr(pilot_release,'verify',counted)
    original_summary=pilot_release.read_summary
    monkeypatch.setattr(pilot_release,'read_summary',lambda:original_summary(output))
    monkeypatch.setattr(delivery,'_connected_pilot_manifests',lambda:{
        'pilot/manifest.json':sha256((output/'manifest.json').read_bytes()).hexdigest(),
        'child/manifest.json':sha256(child.read_bytes()).hexdigest()})
    return output,child,counts,value


def primary_math(monkeypatch):
    sources={'stable.py':'a'*64}
    monkeypatch.setattr(delivery.model,'sources',lambda:sources)
    monkeypatch.setattr(delivery.model,'build',lambda:{'family':'ferrite-pm-maglev-study',**delivery.model.FLAGS})
    monkeypatch.setattr(delivery,'runtime',lambda:{'fixture':True})
    monkeypatch.setattr(delivery,'render',lambda result:b'fixed fixture presentation')
    for name in ('section_svg','energy_svg'):
        monkeypatch.setattr(delivery,name,lambda result:b'<svg/>')
    for module,name in ((delivery.field,'study'),(delivery.transition,'build'),
                        (delivery.geometry,'interface'),(delivery.geometry,'civil_bay'),
                        (delivery.optimisation,'study'),(delivery.evacuation,'study')):
        monkeypatch.setattr(module,name,lambda:{'fixture':True})
    monkeypatch.setattr(delivery.evacuation,'envelope_svg',lambda study:b'<svg/>')
    monkeypatch.setattr(delivery.media,'field_image',lambda study:b'fixture image')
    def retained(*, _pilot=None):
        # Both consumers must receive the same freshly qualified context. They
        # retain its manifest checks rather than accepting a raw summary dict.
        delivery._check_connected_pilot(_pilot)
        return dict(_pilot.manifest_sha256)
    def studies(*, _pilot=None):
        return dict(connected_pilot=delivery._check_connected_pilot(_pilot))
    monkeypatch.setattr(delivery,'external_evidence',retained)
    monkeypatch.setattr(delivery,'closure_studies',studies)
    return sources


def test_payload_qualifies_once_without_cross_operation_cache(monkeypatch,connected):
    _,_,counts,value=connected
    primary_math(monkeypatch)
    first=delivery.payload()
    assert len(counts)==1
    assert json.loads(first['result.json'])['closure_studies']['connected_pilot']=={
        k:v for k,v in value.items() if k!='components'}
    second=delivery.payload()
    assert len(counts)==2
    assert first==second


def test_verify_qualifies_once_with_exact_retained_result(monkeypatch,tmp_path,connected):
    _,_,counts,_=connected
    sources=primary_math(monkeypatch)
    files=delivery.payload()
    manifest=dict(schema='osr-primary-infrastructure-publication/1',family='ferrite-pm-maglev-study',
                  source_sha256=sources,files_sha256={n:sha256(v).hexdigest() for n,v in files.items()},
                  **delivery.model.FLAGS)
    output=tmp_path/'primary';output.mkdir()
    for name,data in files.items():(output/name).write_bytes(data)
    (output/'manifest.json').write_bytes(delivery.encoded(manifest))
    counts.clear()
    assert delivery.verify(output)==manifest
    assert len(counts)==1
    changed=iter((sources,{'stable.py':'b'*64}))
    monkeypatch.setattr(delivery.model,'sources',lambda:next(changed))
    with pytest.raises(ValueError,match='sources changed while verifying'):
        delivery.verify(output)


def test_context_refuses_changed_child_and_parent_receipts(connected):
    output,child,counts,_=connected
    context=delivery._verify_connected_pilot()
    assert len(counts)==1
    original=child.read_bytes();child.write_bytes(b'changed child receipt')
    with pytest.raises(ValueError,match='changed after verification'):
        delivery._check_connected_pilot(context)
    child.write_bytes(original)
    (output/'manifest.json').write_bytes(b'changed parent receipt')
    with pytest.raises(ValueError,match='changed after verification'):
        delivery._check_connected_pilot(context)


@pytest.mark.parametrize('consumer',[delivery.external_evidence,delivery.closure_studies])
def test_default_consumers_reject_forged_or_stale_parent(connected,consumer):
    output,_,counts,_=connected
    manifest=json.loads((output/'manifest.json').read_bytes())
    manifest['source_sha256']={'forged-child-input':'b'*64}
    (output/'manifest.json').write_bytes(delivery.encoded(manifest))
    with pytest.raises(ValueError,match='altered connected pilot'):
        consumer()
    assert len(counts)==1


def test_receipt_mutation_during_qualification_is_rejected(monkeypatch,connected):
    _,child,_,_=connected
    original=pilot_release.read_summary
    def racing():
        summary=original()
        child.write_bytes(b'new child generation')
        return summary
    monkeypatch.setattr(pilot_release,'read_summary',racing)
    with pytest.raises(ValueError,match='changed while verifying'):
        delivery._verify_connected_pilot()
