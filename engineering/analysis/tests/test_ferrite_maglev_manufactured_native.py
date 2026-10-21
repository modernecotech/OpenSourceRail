"""Native material integrity controls; no assembled or physical acceptance."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import shutil
import sys
import zipfile

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from engineering.ferrite_maglev import manufactured_native as n, closure
from engineering.factory_examples import models


def test_definition_preserves_counted_frame_and_global_rod_bounds():
    value=n.definition();raw=closure.definition();frame=closure.primary_frame_definition()
    assert len(value['parts'])==len(raw['parts'])==113
    assert len(frame['parts'])==63
    byid={part['id']:part for part in value['parts']}
    assert len(byid)==len(value['parts'])
    assert {part['id'] for part in frame['parts']}<=set(byid)
    for index in (0,1):
        rod=byid[f'coupler/longitudinal-rod-{index}']
        assert rod['cylinder_axis']=='x'
        assert models.global_size(rod)==pytest.approx([2.8,.03,.03])
        assert models.volume(rod)==pytest.approx(3.141592653589793*.015**2*2.8)
    assert value['modelled_material_mass_kg']==pytest.approx(sum(part['modelled_mass_kg'] for part in value['parts']))
    assert value['interference_roles']==[]
    assert value['modelled_cg_m'] is None
    assert not value['complete_body_or_system_modelled']
    assert all(not value[flag] for flag in n.model.FLAGS)


def test_archive_expansion_is_bounded_before_crc_scan(tmp_path,monkeypatch):
    archive=tmp_path/'model.FCStd'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('Document.xml','x'*2048)
    monkeypatch.setattr(n,'MAX',1024)
    monkeypatch.setattr(zipfile.ZipFile,'testzip',lambda self:pytest.fail('oversized archive reached CRC expansion'))
    with pytest.raises(ValueError,match='bounded native document'):
        n._check_archive(archive)


@pytest.fixture
def retained_packet(tmp_path):
    if not (n.OUTPUT/'manifest.json').is_file():
        pytest.skip('Canonical manufactured-native packet required after the workflow publishes actual FreeCAD evidence')
    n.verify()
    target=tmp_path/'native';shutil.copytree(n.OUTPUT,target)
    return target


def rewrite(packet,name,value):
    raw=n.encoded(value)
    if name.endswith('.gz'):raw=gzip.compress(raw,mtime=0)
    (packet/name).write_bytes(raw)
    manifest=json.loads((packet/'manifest.json').read_text())
    manifest['files_sha256'][name]=sha256(raw).hexdigest()
    (packet/'manifest.json').write_bytes(n.encoded(manifest))


def test_actual_canonical_packet_reopens_and_binds_definition(retained_packet):
    manifest=n.verify(retained_packet)
    definition=json.loads((retained_packet/'definition.json').read_text())
    assert manifest['part_count']==len(definition['parts'])
    assert not manifest['release_authority']


@pytest.mark.parametrize('mutation',['volume','bounds','part-omission','exporter','geometry-helper','unsafe-nested-path'])
def test_rehashed_native_receipt_cannot_change_solid_or_identity(retained_packet,mutation):
    value=json.loads((retained_packet/'native-cad.json').read_text())
    if mutation=='volume':value['parts'][0]['volume_m3']*=2
    elif mutation=='bounds':value['parts'][0]['bounds_m'][0]+=.1
    elif mutation=='part-omission':value['parts'].pop()
    elif mutation=='exporter':value['exporter_sha256']='0'*64
    elif mutation=='geometry-helper':value['geometry_helpers_sha256']='0'*64
    else:value['files_sha256']['../foreign']='0'*64
    rewrite(retained_packet,'native-cad.json',value)
    with pytest.raises(ValueError):n.verify(retained_packet)


@pytest.mark.parametrize('mutation',['material','volume','vertex','triangle','part-identity'])
def test_rehashed_mesh_metadata_and_topology_cannot_detach_from_solids(retained_packet,mutation):
    value=json.loads(gzip.decompress((retained_packet/'native-mesh.json.gz').read_bytes()))
    if mutation=='material':value['parts'][0]['material']='steel'
    elif mutation=='volume':value['parts'][0]['volume_m3']*=2
    elif mutation=='vertex':value['parts'][0]['vertices_m'][0][0]+=1000
    elif mutation=='triangle':value['parts'][0]['triangles'][0][0]=len(value['parts'][0]['vertices_m'])
    else:value['parts'][0]['id']='foreign-part'
    rewrite(retained_packet,'native-mesh.json.gz',value)
    # Rebind nested hashes to reach metadata/topology checks instead of stopping
    # at an ordinary stale-hash failure.
    mesh_digest=sha256((retained_packet/'native-mesh.json.gz').read_bytes()).hexdigest()
    receipt=json.loads((retained_packet/'native-cad.json').read_text());receipt['files_sha256']['native-mesh.json.gz']=mesh_digest
    rewrite(retained_packet,'native-cad.json',receipt)
    visual=json.loads((retained_packet/'visual-receipt.json').read_text());visual['mesh_sha256']=mesh_digest
    rewrite(retained_packet,'visual-receipt.json',visual)
    with pytest.raises(ValueError):n.verify(retained_packet)


@pytest.mark.parametrize('mutation',['renderer','unsafe-nested-path'])
def test_rehashed_visual_receipt_cannot_change_renderer_or_inventory(retained_packet,mutation):
    value=json.loads((retained_packet/'visual-receipt.json').read_text())
    if mutation=='renderer':value['renderer_sha256']='0'*64
    else:value['files_sha256']['../foreign']='0'*64
    rewrite(retained_packet,'visual-receipt.json',value)
    with pytest.raises(ValueError):n.verify(retained_packet)


def test_rehashed_definition_cannot_silently_drop_a_frame_member(retained_packet):
    value=json.loads((retained_packet/'definition.json').read_text());value['parts'].pop()
    rewrite(retained_packet,'definition.json',value)
    with pytest.raises(ValueError,match='solid definition differs'):n.verify(retained_packet)
