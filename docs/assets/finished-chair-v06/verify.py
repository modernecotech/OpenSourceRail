"""Read-only audit of this retained local CAD packet; executes no CAD or solver."""
import hashlib,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def read(n):return json.loads((ROOT/n).read_bytes())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    m=read('manifest.json')
    assert m['evaluation_id']==hashlib.sha256(encoded({k:v for k,v in m.items() if k!='evaluation_id'})).hexdigest()
    actual={p.name for p in ROOT.iterdir() if p.is_file() and p.name!='manifest.json'}
    assert actual==set(m['files'])
    for n,r in m['files'].items():
        p=ROOT/n;assert p.is_file() and not p.is_symlink() and p.stat().st_size==r['bytes'] and digest(p)==r['sha256'],n
    for flag in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','selected_reference_changed'):
        assert m[flag] is False
    case=read('case.json');measure=read('FreeCAD-measurement.json');old=read('FreeCAD-execution.json')
    assert case['candidate_id']==m['candidate_id'] and case['component_geometry_id']==m['component_geometry_id']
    assert old['execution']=='failed' and old['returncode']==0 and old['error']['message']=='STEP source occurrence identity/count differs'
    assert measure['execution']=='completed' and len(measure['bodies'])==len(case['entities'])==66
    seen=set();total=0.
    for e in case['entities']:
        at=e['at_m']
        if e['shape']=='box':
            size=e['size_m'];volume=math.prod(size)
            for h in e.get('holes',[]):volume-=math.pi*(h['diameter_m']/2)**2*size['xyz'.index(h['axis'])]
            box={'min':at,'max':[x+s for x,s in zip(at,size)]}
        else:
            assert e['shape']=='tube'
            volume=math.pi*(e['radius_m']**2-e['inner_radius_m']**2)*e['length_m']
            end=[x+a*e['length_m'] for x,a in zip(at,e['axis'])]
            w=[e['radius_m']*math.sqrt(max(0.,1-a*a)) for a in e['axis']]
            box={'min':[min(x,y)-r for x,y,r in zip(at,end,w)],'max':[max(x,y)+r for x,y,r in zip(at,end,w)]}
        matches=[b for b in measure['bodies'] if abs(b['volume_m3']-volume)<=volume*1e-7+1e-12 and
                 max(abs(b['bbox_m'][k][i]-box[k][i]) for k in ('min','max') for i in range(3))<=1e-7]
        assert len(matches)==1,e['id']
        b=matches[0];assert b['native_name'] not in seen and b['closed'] and b['valid'] and b['all_solids_closed_valid'] and b['solid_count']==1
        seen.add(b['native_name']);total+=volume
    assert abs(total-m['total_material_volume_m3'])<=1e-12
    return dict(files=len(m['files']),unique_closed_solids=len(seen),geometry_correspondence=True,
                strict_import_identity='failed; retained unchanged',physical_accepted=False)

if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
