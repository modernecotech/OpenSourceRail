"""Read-only audit of saved native fabrication CAD and finite B-rep evidence.

No CAD generator, geometry repair, solver or business service is started.
"""
from pathlib import Path
from math import fsum, isclose, pi
import gzip, hashlib, json, sys
sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
PINNED = {
    'case.json': '7e124222e6745049cc2b4160ee6757ec5458b2dbb2269493ec1cba8e6997fc18',
    'commands.json': 'd81c38455c9532d4e6193c456bf8ad886399efefe607f3cb492f9bdb1af090e7',
    'expected.json': 'f14f8631daa906fb6c9fd3e9fab448ff03f42ab22ebfa70f53b2bf5f7c97d50c',
    'FreeCAD.json': '112019b8d593ac4cb2270d2251e7337a9f43ed56f292d860d6e0e30f1d7153ac',
    'frame.step': 'f62c43a82c72521892d02d7aad7c9cfbdef590f8798109acb231c28186337bb5',
    'frame.sc': '59790ebf21da8f2216f58044504c896b24f82fb76c0653f07bae338301665c82',
}
FLAGS = ('physical_accepted','engineering_accepted','manufacturing_release',
         'operating_release','selected_reference_changed','movement_authority')

def encoded(v):
    return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def identity(v):return hashlib.sha256(encoded(v)).hexdigest()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):
    p=P/n;b=p.read_bytes();return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)

def checkseal(v,key='evaluation_id'):
    assert v[key]==identity({k:x for k,x in v.items() if k!=key})

def dot(a,b):return fsum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def close(a,b):return isclose(a,b,rel_tol=1e-10,abs_tol=1e-14)

def oracle(e):
    """Independent polygon integration or disjoint circular subtraction, SI."""
    if e['kind']=='profile-prism':
        ps=e['points_m'];pairs=list(zip(ps,ps[1:]+ps[:1]))
        signed=[a[0]*b[1]-a[1]*b[0] for a,b in pairs];A=fsum(signed)/2
        assert A>0
        C=[fsum((a[k]+b[k])*s for (a,b),s in zip(pairs,signed))/(6*A) for k in range(2)]
        a=e['plane_x_dir'];b=e['plane_y_dir'];n=cross(a,b);o=e['origin_m'];L=e['distance_m']
        assert close(dot(a,a),1) and close(dot(b,b),1) and close(dot(a,b),0) and L>0
        V=A*L;center=[o[i]+a[i]*C[0]+b[i]*C[1]+n[i]*L/2 for i in range(3)]
        vertices=[[o[i]+a[i]*p[0]+b[i]*p[1]+n[i]*t for i in range(3)] for p in ps for t in [0,L]]
    else:
        assert e['kind']=='box-minus-disjoint-cylinders';size=e['size_m'];c=e['centre_m'];V=size[0]*size[1]*size[2];M=[V*x for x in c]
        for h in e['holes']:
            assert h['axis']==[1.,0.,0.];v=pi*h['radius_m']**2*h['length_m'];V-=v
            center=[h['base_m'][i]+h['axis'][i]*h['length_m']/2 for i in range(3)];M=[M[i]-v*center[i] for i in range(3)]
        center=[m/V for m in M]
        vertices=[[c[i]+size[i]*s[i]/2 for i in range(3)] for s in __import__('itertools').product([-1,1],repeat=3)]
    return V,center,{s:[f(v[i] for v in vertices) for i in range(3)] for s,f in [('min',min),('max',max)]}

def inside(e,p):
    """Strict analytic membership; published probes stay away from boundaries."""
    if e['kind']=='profile-prism':
        a=e['plane_x_dir'];b=e['plane_y_dir'];n=cross(a,b);d=[p[i]-e['origin_m'][i] for i in range(3)]
        x,y,t=dot(d,a),dot(d,b),dot(d,n)
        if not 0<t<e['distance_m']:return False
        ps=e['points_m']
        return all((q[0]-r[0])*(y-r[1])-(q[1]-r[1])*(x-r[0])>0 for r,q in zip(ps,ps[1:]+ps[:1]))
    if not all(abs(p[i]-e['centre_m'][i])<e['size_m'][i]/2 for i in range(3)):return False
    for h in e['holes']:
        d=[p[i]-h['base_m'][i] for i in range(3)];t=dot(d,h['axis']);r2=fsum((d[i]-h['axis'][i]*t)**2 for i in range(3))
        if 0<t<h['length_m'] and r2<h['radius_m']**2:return False
    return True

def verify():
    m=read('manifest.json');checkseal(m,'manifest_id')
    actual={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and p.name!='manifest.json'}
    assert actual==set(m['files'])
    for name,row in m['files'].items():
        p=P/name;assert not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
    assert all(m[k] is False for k in FLAGS)
    for n,h in PINNED.items():assert sha(P/n)==h,n
    case=read('case.json');checkseal(case);assert case['case_geometry_id']==identity(case['physical_definition'])==m['case_geometry_id']
    assert [{k:v for k,v in e.items() if k not in ('volume_m3','centroid_m')} for e in case['entities']]==case['physical_definition']['entities']
    es={e['id']:e for e in case['entities']};assert len(es)==26 and len({e['stock_owner'] for e in es.values()})==6
    assert len([e for e in es if e.startswith('plate/')])==12 and len([e for e in es if e.startswith('deposit/')])==12
    expected=read('expected.json');checkseal(expected);assert expected['extra_plate_purchase_count']==0 and expected['source_physical_plate_count']==6
    values={}
    for e in es.values():
        V,C,B=oracle(e);assert close(V,e['volume_m3']) and all(close(x,y) for x,y in zip(C,e['centroid_m']));values[e['id']]=(V,C,B)
    assert close(fsum(v[0] for v in values.values()),expected['total_volume_m3'])
    cmds=read('commands.json');assert cmds['units']=='mm' and len(cmds['commands'])==132
    assert cmds['commands'][0]==dict(command='document.units',params=dict(units='mm'))
    measurement=read('FreeCAD.json');bodies=measurement['bodies'];native=measurement['point_probes'];plan=read('probe-plan.json');checkseal(plan)
    assert measurement['execution']=='completed' and measurement['body_count']==len(bodies)==len(es)==len(native['mapping'])==26
    assert native['plan_id']==plan['evaluation_id'] and native['mapping_issues']==native['mismatches']==[]
    assert all(b['valid'] and b['closed'] and b['all_solids_closed_valid'] and b['solid_count']==1 and b['volume_m3']>0 for b in bodies)
    assert len({b['native_name'] for b in bodies})==26
    for eid,(V,C,B) in values.items():
        matches=[b for b in bodies if isclose(b['volume_m3'],V,rel_tol=1e-7,abs_tol=1e-13) and all(abs(b['center_of_mass_m'][i]-C[i])<=1e-7 for i in range(3)) and all(abs(b['bbox_m'][s][i]-B[s][i])<=1e-7 for s in ['min','max'] for i in range(3))]
        assert len(matches)==1 and matches[0]['native_name']==native['mapping'][eid]['native_name']
    planned={(r['id'],q['id']):q for r in plan['records'] for q in r['probes']};seen=set()
    for q in native['results']:
        key=(q['source_id'],q['probe_id']);assert key not in seen;seen.add(key);p=planned[key]
        assert q['point_m']==p['point_m'] and inside(es[key[0]],q['point_m']) is p['expected_inside'] is q['expected_inside'] is q['actual_inside'] and q['passed']
    assert seen==set(planned) and len(seen)==native['executed_probe_count']==416
    assert native['strict_native_name_identity']=='failed' and native['strict_name_failure']
    assert all(measurement[k] is False for k in FLAGS)
    prefix=read('native-execution.json');assert prefix['execution']=='completed' and prefix['native_calls']==3 and prefix['source_inputs_tool_unchanged']
    for view in ['fabrication','end-joint']:
        render=read('renders/'+view+'/result.json');recipe=read('renders/'+view+'/recipe.json')
        assert render['execution']=='completed' and render['source_unchanged'] and render['width']==3000 and render['height']==1900
        assert recipe['candidate_id']==case['case_geometry_id'] and all(recipe[k] is False for k in FLAGS if k in recipe)
        assert {x.split(':color=')[0] for x in recipe['body_styles']}==set(es)
    return dict(independent_closed_solids=26,source_physical_plates=6,CAD_regions=26,stock_owners=6,finite_point_checks=416,strict_import_identity='failed; retained separately',geometry_metrics_and_finite_probes='passed',physical_accepted=False,engineering_accepted=False)

if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
