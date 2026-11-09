"""Measurements are distinct from name identity and from physical acceptance."""
from math import isfinite
from geometry import FLAGS
TOLERANCES=dict(solidcraft=dict(volume_relative=1e-3,volume_absolute_m3=1e-12,position_absolute_m=1e-3),freecad=dict(volume_relative=1e-7,volume_absolute_m3=1e-13,position_absolute_m=1e-7))
def compatible(expected,actual,tol):
    v=actual.get('volume_m3');c=actual.get('center_of_mass_m');b=actual.get('bbox_m')
    if type(v) not in (int,float) or not isfinite(v) or v<=0 or not isinstance(c,list) or len(c)!=3 or not isinstance(b,dict):return False
    nums=c+b.get('min',[])+b.get('max',[])
    if len(nums)!=9 or any(type(x) not in (int,float) or not isfinite(x) for x in nums):return False
    return abs(v-expected['volume_m3'])<=max(tol['volume_absolute_m3'],tol['volume_relative']*expected['volume_m3']) and all(abs(x-y)<=tol['position_absolute_m'] for x,y in zip(c,expected['centroid_m'])) and all(abs(x-y)<=tol['position_absolute_m'] for a,z in zip((b['min'],b['max']),expected['bounds_m']) for x,y in zip(a,z))
def compare(spec,measurement,provider):
    tol=TOLERANCES[provider];bodies=measurement['bodies'];ps=spec['primitives'];matches=[];issues=[]
    if len(bodies)!=len(ps):issues.append('Body count differs')
    for p in ps:
        hits=[i for i,b in enumerate(bodies) if compatible(p['expected'],b,tol)]
        if len(hits)!=1:issues.append(dict(primitive=p['id'],geometric_matches=len(hits),reason='Absent or geometrically ambiguous; no name substitution'))
        else:matches.append(dict(primitive_id=p['id'],native_body_id=p['native_body_id'],measured_index=hits[0],measured_raw_id=bodies[hits[0]]['id']))
    if len({m['measured_index'] for m in matches})!=len(matches):issues.append('Bijection not injective')
    if any(b.get('closed') is not True for b in bodies):issues.append('Open or unknown closed status')
    return dict(provider=provider,tolerances=tol,geometric_bijection='passed' if not issues else 'held',issues=issues,mapping=matches,raw_labels_preserved=True,native_names_preserved=not issues and all(m['native_body_id']==m['measured_raw_id'] for m in matches),scope='Literal nominal individual material bodies only; no joint, thread, seal, installed mass or assembly qualification',**FLAGS)
