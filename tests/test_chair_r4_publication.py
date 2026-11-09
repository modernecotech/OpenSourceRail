"""Saved native chair evidence cannot be promoted by resealing the outer packet."""
from pathlib import Path
import gzip,hashlib,json,shutil,types
import pytest

PACKET=Path(__file__).resolve().parents[1]/'docs/assets/chair-installation-r4-v06'

def auditor(path):
    # A filesystem import loader can write verify.py's bytecode before its
    # read-only guard executes. Load the audit without mutating its packet.
    source=PACKET/'verify.py';module=types.ModuleType('chair_r4_packet_auditor')
    module.__file__=str(source)
    exec(compile(source.read_bytes(),str(source),'exec'),module.__dict__);module.P=path
    return module

def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def test_saved_native_geometry_and_point_evidence():
    before={p.relative_to(PACKET).as_posix() for p in PACKET.rglob('*') if p.is_file()}
    result=auditor(PACKET).verify()
    assert result['positive_closed_valid_solids']==275 and result['material_and_void_point_checks']==2427
    assert result['strict_import_identity']=='failed; retained separately' and result['physical_accepted'] is False
    assert {p.relative_to(PACKET).as_posix() for p in PACKET.rglob('*') if p.is_file()}==before

@pytest.mark.parametrize('fault',['measured-point','source-part','approval'])
def test_resealing_outer_manifest_cannot_replace_native_evidence_or_acceptance(tmp_path,fault):
    path=tmp_path/'packet';shutil.copytree(PACKET,path);manifest=json.loads((path/'manifest.json').read_bytes())
    if fault=='approval':manifest['physical_accepted']=True
    else:
        name='FreeCAD.json.gz' if fault=='measured-point' else 'source/coupon.json'
        raw=(path/name).read_bytes();value=json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
        if fault=='measured-point':
            value['point_probes']['results'][0]['actual_inside']=False
            value['point_probes']['results'][0]['passed']=True  # A self-declared pass is insufficient.
        else:value['entities'][0]['center_m'][0]+=.001
        (path/name).write_bytes(gzip.compress(encoded(value),mtime=0) if name.endswith('.gz') else encoded(value))
        manifest['files'][name]=dict(bytes=(path/name).stat().st_size,sha256=hashlib.sha256((path/name).read_bytes()).hexdigest())
    manifest.pop('manifest_id');manifest['manifest_id']=hashlib.sha256(encoded(manifest)).hexdigest();(path/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises(AssertionError):auditor(path).verify()
