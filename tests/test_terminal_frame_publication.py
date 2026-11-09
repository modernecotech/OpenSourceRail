"""Saved fabrication evidence remains bounded and authentic after outer resealing."""
from pathlib import Path
import hashlib,json,shutil,types
import pytest

PACKET=Path(__file__).resolve().parents[1]/'docs/assets/terminal-frame-v06'

def audit(path):
    source=PACKET/'verify.py';m=types.ModuleType('terminal_frame_audit');m.__file__=str(source)
    exec(compile(source.read_bytes(),str(source),'exec'),m.__dict__);m.P=path
    return m.verify()

def encoded(v):return(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def test_saved_real_regions_and_independent_material_void_evidence():
    before={p.relative_to(PACKET).as_posix() for p in PACKET.rglob('*') if p.is_file()}
    r=audit(PACKET)
    assert r['independent_closed_solids']==26 and r['source_physical_plates']==6 and r['finite_point_checks']==416
    assert r['strict_import_identity']=='failed; retained separately' and r['physical_accepted'] is False
    assert before=={p.relative_to(PACKET).as_posix() for p in PACKET.rglob('*') if p.is_file()}

@pytest.mark.parametrize('fault',['extra-solid','void-point','source-plate','approval'])
def test_outer_reseal_does_not_replace_source_native_evidence_or_release(tmp_path,fault):
    folder=tmp_path/'packet';shutil.copytree(PACKET,folder);m=json.loads((folder/'manifest.json').read_bytes())
    if fault=='approval':m['physical_accepted']=True
    else:
        name='case.json' if fault=='source-plate' else 'FreeCAD.json';v=json.loads((folder/name).read_bytes())
        if fault=='source-plate':v['entities'][0]['distance_m']+=.001
        elif fault=='extra-solid':v['bodies'].append(v['bodies'][0]);v['body_count']+=1
        else:
            q=next(q for q in v['point_probes']['results'] if q['expected_inside'] is False)
            q['actual_inside']=True;q['passed']=True
        (folder/name).write_bytes(encoded(v));m['files'][name]=dict(bytes=(folder/name).stat().st_size,sha256=hashlib.sha256((folder/name).read_bytes()).hexdigest())
    m.pop('manifest_id');m['manifest_id']=hashlib.sha256(encoded(m)).hexdigest();(folder/'manifest.json').write_bytes(encoded(m))
    with pytest.raises(AssertionError):audit(folder)
