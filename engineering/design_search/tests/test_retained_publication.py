"""Original producer pinning cannot relabel old research as current evidence."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import pytest
from engineering.design_search import retained_publication as r
from engineering.station_rail.common import encoded,identity,digest


def fixture(root):
    base=root/r.WHEEL_PACKET;base.mkdir(parents=True)
    (base/'result.json').write_text('{"result":"old"}\n')
    source=root/'engineering/original.py';source.parent.mkdir(exist_ok=True);source.write_text('new = True\n')
    producer=root/r.PRODUCER;producer.parent.mkdir(parents=True,exist_ok=True)
    producer.write_bytes(Path(r.__file__).read_bytes())
    original=b'old = True\n';wanted=sha256(original).hexdigest()
    m=dict(schema='osr-wheel-campaign-publication-manifest/1',source_sha256={'engineering/original.py':wanted},
        files_sha256={'result.json':digest(base/'result.json')},**r.FLAGS)
    m['manifest_id']=identity(m);(base/'manifest.json').write_bytes(encoded(m))
    return original,deepcopy(m)


def test_retention_preserves_original_receipt_and_verifies_original_source_bytes(tmp_path):
    original,m=fixture(tmp_path)
    result=r.retain(tmp_path,resolver=lambda root,name,wanted:original)
    assert result['verified'] and result['original_source_count']==1
    assert result['current_evaluator_admission'] is False and result['numerical_reexecuted'] is False
    assert json.loads((tmp_path/r.WHEEL_PACKET/'manifest.json').read_bytes())==m
    (tmp_path/'engineering/original.py').write_text('another current revision\n')
    assert r.verify(tmp_path)['retention_id']==result['retention_id']
    (tmp_path/r.WHEEL_EPOCH/'sources.tar.gz').write_bytes(b'tampered')
    with pytest.raises(ValueError,match='archive bytes differ'):r.verify(tmp_path)


def test_wrong_source_provider_cannot_create_a_historical_epoch(tmp_path):
    fixture(tmp_path)
    with pytest.raises(ValueError,match='Recovered original source bytes differ'):
        r.retain(tmp_path,resolver=lambda *_:b'wrong source')
    assert not (tmp_path/r.WHEEL_EPOCH).exists()


def test_retention_refuses_output_escape_and_conflicting_original_bindings(tmp_path):
    original,m=fixture(tmp_path)
    with pytest.raises(ValueError,match='inside the repository'):
        r.retain(tmp_path,output='../escape',resolver=lambda *_:original)
    with pytest.raises(ValueError,match='separate from the original packet'):
        r.retain(tmp_path,output=r.WHEEL_PACKET+'/sources',resolver=lambda *_:original)
    m['recovery_source_sha256']={'engineering/original.py':'0'*64}
    m['manifest_id']=identity({k:v for k,v in m.items() if k!='manifest_id'})
    (tmp_path/r.WHEEL_PACKET/'manifest.json').write_bytes(encoded(m))
    with pytest.raises(ValueError,match='Conflicting original source bindings'):
        r.retain(tmp_path,resolver=lambda *_:original)
