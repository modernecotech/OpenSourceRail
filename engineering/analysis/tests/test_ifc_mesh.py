"""Native meshes preserve source identity and finite placed geometry."""
import hashlib
import json
from pathlib import Path
import pytest
from engineering.interchange import ifc_mesh

ROOT=Path(__file__).resolve().parents[3]
IFC=ROOT/'engineering/models/bim/reference/civil-coordination.ifc'
INDEX=IFC.with_suffix('.index.json')

def test_native_ifc_meshes_are_bounded_repeatable_and_indexed(tmp_path,monkeypatch):
    monkeypatch.setattr(ifc_mesh,'MAX_CHUNK_BYTES',250_000)
    a=ifc_mesh.tessellate(IFC,INDEX,tmp_path/'a')
    b=ifc_mesh.tessellate(IFC,INDEX,tmp_path/'b')
    assert a==b
    assert a['object_count']>100 and a['triangle_count']>a['object_count']*12
    assert len(a['chunks'])>1 and not a['deployment_release_ready']
    meshes=[]
    for chunk in a['chunks']:
        data=(tmp_path/'a'/chunk['file']).read_bytes()
        assert data==(tmp_path/'b'/chunk['file']).read_bytes()
        assert len(data)<=250_001
        assert hashlib.sha256(data).hexdigest()==chunk['sha256']
        meshes.extend(json.loads(data)['objects'])
    index=json.loads(INDEX.read_text());ids={o['asset_id']:o for o in index['objects']}
    assert len({o['asset_id'] for o in meshes})==a['object_count']
    assert set(ids)=={o['asset_id'] for o in meshes}|{o['asset_id'] for o in a['non_geometric_objects']}
    assert any(len(m['vertices'])>24 for m in meshes), 'curved and profiled solids must not become boxes'
    for m in meshes:
        assert m['ifc_guid']==ids[m['asset_id']]['ifc_guid']
        # World placements must lie inside the independently generated envelope.
        box=ids[m['asset_id']]['bbox_m']
        for axis in range(3):
            values=m['vertices'][axis::3]
            assert min(values)>=box[axis]-0.02
            assert max(values)<=box[axis+3]+0.02

def test_drift_and_oversized_meshes_fail_closed(tmp_path,monkeypatch):
    index=json.loads(INDEX.read_text());index['ifc_sha256']='0'*64
    bad=tmp_path/'bad.json';bad.write_text(json.dumps(index))
    with pytest.raises(ValueError,match='hash'):ifc_mesh.tessellate(IFC,bad,tmp_path/'bad')
    monkeypatch.setattr(ifc_mesh,'MAX_CHUNK_BYTES',50)
    with pytest.raises(ValueError,match='bounded'):ifc_mesh.tessellate(IFC,INDEX,tmp_path/'tiny')
