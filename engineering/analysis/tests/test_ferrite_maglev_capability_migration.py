import json
import pytest
from engineering.ferrite_maglev import capability_migration as m


def test_actual_baseline_features_have_owned_dispositions():
    value=m.load()
    assert len(value['capabilities'])==14
    assert value['baseline']['tag']=='v0.4.0'
    assert len(value['products'])==3
    assert all(r['acceptance_test'] and r['owner'] for r in value['capabilities'])


def test_source_presence_does_not_mark_tested(monkeypatch):
    monkeypatch.setattr(m.pilot_assurance,'study',lambda:dict(profiles=[]))
    value=m.study()
    assert not any(r['state']=='retained-and-tested' for r in value['capabilities'])
    assert all(r['executed_current'] is False and r['execution_receipt'] is None
               and r['engineering_accepted'] is False for r in value['capabilities'])
    retained={r['id'] for r in m.load()['capabilities'] if r['state']=='retained-and-tested'}
    assert retained
    assert all(r['state']=='retained-but-unconnected' for r in value['capabilities'] if r['id'] in retained)
    assert value['physical_release'] is False


def test_migration_payload_tamper_rejected(tmp_path):
    m.publish(tmp_path);m.verify(tmp_path)
    value=json.loads((tmp_path/'study.json').read_bytes())
    value['capabilities'][0]['owner']='forged'
    (tmp_path/'study.json').write_text(json.dumps(value))
    with pytest.raises(ValueError,match='altered'):
        m.verify(tmp_path)


def test_migration_source_claim_tamper_rejected(tmp_path):
    m.publish(tmp_path);m.verify(tmp_path)
    receipt=json.loads((tmp_path/'manifest.json').read_bytes())
    receipt['source_sha256']={'forged':'a'*64}
    (tmp_path/'manifest.json').write_bytes(m.encoded(receipt))
    with pytest.raises(ValueError,match='altered'):
        m.verify(tmp_path)


def test_rehashed_false_acceptance_readme_is_rejected(tmp_path):
    from hashlib import sha256
    m.publish(tmp_path);m.verify(tmp_path)
    (tmp_path/'README.md').write_text('All hardware accepted and released for passengers.')
    receipt=json.loads((tmp_path/'manifest.json').read_bytes())
    receipt['files_sha256']['README.md']=sha256((tmp_path/'README.md').read_bytes()).hexdigest()
    (tmp_path/'manifest.json').write_bytes(m.encoded(receipt))
    with pytest.raises(ValueError,match='altered'):
        m.verify(tmp_path)


def test_pinned_historical_product_reference_has_no_active_retired_identity(tmp_path,monkeypatch):
    from engineering.ferrite_maglev import architecture_audit
    value=m.load();baseline=value['baseline']
    assert baseline==dict(commit='205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e',
                          feature_rows=14,path='README.md',tag='v0.4.0',
                          sha256='c4160b9ba9aefde225d9bcd7ea8b34c8db7565294f10c56a603276b01b5de444')
    historical='https://github.com/modernecotech/OpenSourceRail/blob/'+baseline['commit']+'/'+baseline['path']
    trainset=next(row for row in value['capabilities'] if row['id']=='trainset')
    assert historical in trainset['decision']
    monkeypatch.setattr(m.pilot_assurance,'study',lambda:dict(profiles=[]))
    summary=m.study()
    payloads={'input.json':m.encoded(value),'README.md':m.readme(summary).encode(),
              'study.json':m.encoded(summary),
              'pilot-study.json':m.encoded(dict(components=[dict(summary=summary)]))}
    paths=[]
    for name,raw in payloads.items():
        path=tmp_path/name;path.write_bytes(raw);paths.append(path)
    assert architecture_audit.scan(paths)==[]
    # Historical evidence must not exempt the surrounding file from the audit.
    paths[1].write_bytes(paths[1].read_bytes()+b'\nconfiguration='+architecture_audit.TOKENS[4].encode())
    assert architecture_audit.scan(paths)==[str(paths[1])]
