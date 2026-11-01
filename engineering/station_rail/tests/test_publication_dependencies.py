"""A root receipt cannot make a stale linked source or changed payload current."""
import json
from pathlib import Path
import pytest
from engineering.station_rail import publication as p
from engineering.station_rail.common import encoded,identity,digest

CONTRACT=('fixture-current-research/1','sources','files','publication_id')


def packet(root):
    source=root/'engineering/input.py';source.parent.mkdir();source.write_text('value = 1\n')
    base=root/'docs/design-engine/fixture';base.mkdir(parents=True)
    payload=base/'result.json';payload.write_text('{"value":1}\n')
    m=dict(schema=CONTRACT[0],sources={'engineering/input.py':digest(source)},
        files={'result.json':digest(payload)},physical_accepted=False,engineering_accepted=False,
        manufacturing_release=False,operating_release=False)
    m['publication_id']=identity(m);(base/'manifest.json').write_bytes(encoded(m))
    return base,m


def test_linked_source_change_is_rejected_even_when_packet_bytes_are_intact(tmp_path):
    base,m=packet(tmp_path)
    bound=p._linked_packet_sources(tmp_path,'fixture',CONTRACT)
    assert bound['engineering/input.py']==m['sources']['engineering/input.py']
    assert bound['docs/design-engine/fixture/result.json']==m['files']['result.json']
    (tmp_path/'engineering/input.py').write_text('value = 2\n')
    with pytest.raises(ValueError,match='stale source engineering/input.py'):
        p._linked_packet_sources(tmp_path,'fixture',CONTRACT)
    assert json.loads((base/'manifest.json').read_bytes())==m


def test_payload_change_resealed_acceptance_and_unsafe_source_are_rejected(tmp_path):
    base,m=packet(tmp_path)
    (base/'result.json').write_text('{"value":2}\n')
    with pytest.raises(ValueError,match='payload differs'):
        p._linked_packet_sources(tmp_path,'fixture',CONTRACT)
    (base/'result.json').write_text('{"value":1}\n')
    m['physical_accepted']=True;m['publication_id']=identity({k:v for k,v in m.items() if k!='publication_id'})
    (base/'manifest.json').write_bytes(encoded(m))
    with pytest.raises(ValueError,match='cannot grant physical_accepted'):
        p._linked_packet_sources(tmp_path,'fixture',CONTRACT)
    m['physical_accepted']=False;m['sources']={'../outside.py':'0'*64}
    m['publication_id']=identity({k:v for k,v in m.items() if k!='publication_id'})
    (base/'manifest.json').write_bytes(encoded(m))
    with pytest.raises(ValueError,match='repository-relative'):
        p._linked_packet_sources(tmp_path,'fixture',CONTRACT)


def test_publish_checks_linked_packets_before_calculation_or_replacement(tmp_path,monkeypatch):
    out=tmp_path/'existing';out.mkdir();marker=out/'manifest.json';marker.write_text('original')
    def fail(_root):raise ValueError('stale linked source')
    monkeypatch.setattr(p,'linked_publication_sources',fail)
    monkeypatch.setattr(p.evaluation,'build',lambda *_:pytest.fail('must not calculate before source preflight'))
    with pytest.raises(ValueError,match='stale linked source'):p.publish(root=tmp_path,output=out)
    assert marker.read_text()=='original'


def test_schema_can_bind_dispositions_in_a_sealed_result_instead_of_manifest(tmp_path):
    base,m=packet(tmp_path)
    result=dict(schema='fixture-result/1',physical_accepted=False,engineering_accepted=False,
        manufacturing_release=False,operating_release=False)
    result['result_id']=identity(result);(base/'result.json').write_bytes(encoded(result))
    for flag in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'):
        m.pop(flag,None)
    m['files']['result.json']=digest(base/'result.json')
    m['publication_id']=identity({k:v for k,v in m.items() if k!='publication_id'})
    (base/'manifest.json').write_bytes(encoded(m))
    contract=(*CONTRACT,('result.json','fixture-result/1','result_id'))
    p._linked_packet_sources(tmp_path,'fixture',contract)
    with pytest.raises(ValueError,match='cannot grant physical_accepted'):
        p._linked_packet_sources(tmp_path,'fixture',CONTRACT)
    result['physical_accepted']=True;result['result_id']=identity({k:v for k,v in result.items() if k!='result_id'})
    (base/'result.json').write_bytes(encoded(result));m['files']['result.json']=digest(base/'result.json')
    m['publication_id']=identity({k:v for k,v in m.items() if k!='publication_id'});(base/'manifest.json').write_bytes(encoded(m))
    with pytest.raises(ValueError,match='cannot grant physical_accepted'):
        p._linked_packet_sources(tmp_path,'fixture',contract)
