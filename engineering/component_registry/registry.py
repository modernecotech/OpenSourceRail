"""Part/revision/occurrence contracts; quantities never grant hardware acceptance.

The transform maps each centred local part frame to the registry frame in metres.
Parent links express ownership, not an implicit second transformation. Mass from a
purchased envelope is bounded independently of its geometric volume/density.
"""
from copy import deepcopy
from hashlib import sha256
from math import pi,isfinite,fsum,sqrt
import json
import re

FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False,physical_journey_completed=False)
SCHEMA='osr-component-registry/1'
PHYSICAL_FIELDS=('part_id','functions','geometry','material_id','assembly','electrical_thermal')

def _part_physical(p):
    result={k:p[k] for k in PHYSICAL_FIELDS}
    result['manufacturing_definition']={k:p['manufacturing'][k] for k in ('method','blank_dimensions_m','joining_method','mould_id','tool_definition_id') if k in p['manufacturing']}
    return result


def identity(value):
    return sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()


def _number(x,name,positive=False,nonnegative=False):
    if type(x) not in (int,float) or not isfinite(x) or positive and x<=0 or nonnegative and x<0:
        raise ValueError('Finite '+name+' required')
    return float(x)


def _id(value):return isinstance(value,str) and re.fullmatch('[a-f0-9]{64}',value) is not None

def _text(value,name):
    if not isinstance(value,str) or not value.strip():raise ValueError('Nonempty '+name+' required')
    return value


def _strings(value,name,allow_empty=False):
    if not isinstance(value,list) or not allow_empty and not value or len(value)!=len(set(value)):
        raise ValueError('Distinct '+name+' required')
    for x in value:_text(x,name)


def _unaccepted(value):
    if isinstance(value,dict):
        if any(k in FLAGS and v is not False for k,v in value.items()):raise ValueError('Registry cannot issue physical acceptance or release')
        for v in value.values():_unaccepted(v)
    elif isinstance(value,list):
        for v in value:_unaccepted(v)


def _bounds(value,name,keys=('lower_bound_kg','upper_bound_kg')):
    a,b=[value.get(k) for k in keys]
    if (a is None)!=(b is None):raise ValueError('Both '+name+' bounds or neither required')
    if a is not None:
        _number(a,name,nonnegative=True);_number(b,name,nonnegative=True)
        if a>b:raise ValueError('Ordered '+name+' bounds required')
    return a,b


def _pose(t):
    if not isinstance(t,list) or len(t)!=4 or any(not isinstance(r,list) or len(r)!=4 for r in t):
        raise ValueError('Rigid 4x4 installed transform required')
    for r in t:
        for v in r:_number(v,'transform entry')
    if any(abs(t[3][j]-(1. if j==3 else 0.))>1e-10 for j in range(4)):
        raise ValueError('Homogeneous rigid transform required')
    R=[r[:3] for r in t[:3]]
    if any(abs(sum(R[k][i]*R[k][j] for k in range(3))-(1. if i==j else 0.))>1e-9 for i in range(3) for j in range(3)):
        raise ValueError('Orthonormal installed rotation required')
    det=R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1])-R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0])+R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0])
    if abs(det-1)>1e-9:raise ValueError('Proper installed rotation required')
    return t


def geometry_properties(g,mass_kg=None):
    if not isinstance(g,dict):raise ValueError('Explicit geometry record required')
    kind=g.get('kind');d=g.get('dimensions_m');volume=None;factors=None
    if kind in ('box','envelope'):
        if not isinstance(d,list) or len(d)!=3:raise ValueError('Box/envelope needs three dimensions')
        x,y,z=[_number(v,'geometry dimension',positive=True) for v in d]
        dims=[x,y,z]
        if kind=='box':volume=x*y*z;factors=[(y*y+z*z)/12,(x*x+z*z)/12,(x*x+y*y)/12]
    elif kind in ('cylinder','tube'):
        if not isinstance(d,dict):raise ValueError('Cylinder/tube dimensions required')
        L=_number(d.get('length'),'length',positive=True)
        R=_number(d.get('radius') if kind=='cylinder' else d.get('outer_radius'),'outer radius',positive=True)
        r=0. if kind=='cylinder' else _number(d.get('inner_radius'),'inner radius',nonnegative=True)
        if r>=R:raise ValueError('Inner radius must be below outer radius')
        volume=pi*(R*R-r*r)*L;dims=[2*R,2*R,L]
        factors=[(3*(R*R+r*r)+L*L)/12]*2+[(R*R+r*r)/2]
    elif kind=='rhs':
        if not isinstance(d,dict):raise ValueError('RHS dimensions required')
        x,y,z,t=[_number(d.get(k),k,positive=True) for k in ('length','width','height','wall')]
        if 2*t>=min(y,z):raise ValueError('Hollow section wall closes the cavity')
        outer=x*y*z;inner=x*(y-2*t)*(z-2*t);volume=outer-inner;dims=[x,y,z]
        fo=[(y*y+z*z)/12,(x*x+z*z)/12,(x*x+y*y)/12]
        fi=[((y-2*t)**2+(z-2*t)**2)/12,(x*x+(z-2*t)**2)/12,(x*x+(y-2*t)**2)/12]
        factors=[(outer*a-inner*b)/volume for a,b in zip(fo,fi)]
    else:raise ValueError('Supported net primitive or purchased envelope required')
    declared=g.get('net_volume_m3')
    if declared is not None:
        _number(declared,'net volume',positive=True)
        if volume is None or abs(declared-volume)>1e-9*max(1.,volume):raise ValueError('Declared net geometry volume differs')
    inertia=None
    if mass_kg is not None:
        _number(mass_kg,'mass',nonnegative=True)
        if factors is not None:inertia=[[mass_kg*factors[i] if i==j else 0. for j in range(3)] for i in range(3)]
    return dict(volume_m3=volume,centroid_m=[0.,0.,0.],inertia_kg_m2=inertia,envelope_dimensions_m=dims,
        inertia_basis='uniform net primitive' if inertia is not None else 'unknown purchased distribution' if kind=='envelope' else 'mass unresolved')


def make_part(part_id,revision,functions,geometry,material_id,mass,manufacturing,assembly=None,
              electrical_thermal=None,cost=None,procurement=None,evidence=None,lifecycle=None,material_evaluation_id=None):
    if material_evaluation_id is None and material_id is not None:
        from .materials import catalogue
        matched=next((m for m in catalogue()['materials'] if m['material_id']==material_id),None)
        if matched is None:raise ValueError('Custom physical material needs its explicit material evaluation identity')
        material_evaluation_id=matched['material_evaluation_id']
    g=deepcopy(geometry);properties=geometry_properties(g)
    g.setdefault('net_volume_m3',properties['volume_m3'])
    result=dict(part_id=part_id,revision=revision,functions=list(functions),geometry=g,material_id=material_id,material_evaluation_id=material_evaluation_id,
        mass=deepcopy(mass),manufacturing=deepcopy(manufacturing),assembly=deepcopy(assembly or {}),
        electrical_thermal=deepcopy(electrical_thermal or {}),cost=deepcopy(cost) if cost is not None else
        dict(source_class='C',currency='USD',lower_usd=None,upper_usd=None,source_id=None,source_date=None,location=None,quantity_basis='one-part',confidence='unresolved'),
        procurement=deepcopy(procurement or dict(supplier=None,country_of_origin=None,quote_id=None,MOQ=None,lead_days=None)),
        evidence=deepcopy(evidence or dict(calculations=[],tests=[],reviewer=None,status='unqualified-research-definition')),
        lifecycle=deepcopy(lifecycle or dict(inspection_interval=None,replacement=None,repair_method=None,recycling=None)),**FLAGS)
    result['physical_definition_id']=identity(_part_physical(result))
    result['revision_id']=identity(result)
    _part(result)
    return result


def _part(p):
    for k in ('part_id','revision'):_text(p.get(k),k)
    _strings(p.get('functions'),'functions');geometry_properties(p.get('geometry'))
    if p.get('material_id') is not None and (not _id(p['material_id']) or not _id(p.get('material_evaluation_id'))):raise ValueError('Immutable material identity required')
    if p.get('physical_definition_id')!=identity(_part_physical(p)):raise ValueError('Part physical definition identity differs')
    if p.get('revision_id')!=identity({k:v for k,v in p.items() if k!='revision_id'}):raise ValueError('Part revision identity differs')
    m=p.get('mass')
    if not isinstance(m,dict):raise ValueError('Mass record required')
    lo,hi=_bounds(m,'mass');v=m.get('calculated_kg')
    if v is not None:
        _number(v,'calculated mass',positive=True)
        if lo is not None and not lo<=v<=hi:raise ValueError('Calculated mass outside its bounds')
    if m.get('evidence_state') not in ('calculated','bounded-estimate','unresolved','supplier-typical'):
        raise ValueError('Explicit mass evidence state required')
    if m.get('evidence_state')=='unresolved' and (v is not None or lo is not None):raise ValueError('Unresolved mass cannot invent quantity')
    if m.get('evidence_state')=='bounded-estimate' and lo is None:raise ValueError('Bounded mass requires actual finite bounds')
    if p['geometry']['kind']=='envelope' and v is not None and m.get('evidence_state')=='calculated':
        raise ValueError('Purchased envelope volume is not a calculated installed mass')
    if not isinstance(p['manufacturing'],dict) or not p['manufacturing'].get('method'):
        raise ValueError('Explicit manufacturing method or unresolved route required')
    for k in ('cycle_hours','scrap_fraction'):
        if p['manufacturing'].get(k) is not None:
            x=_number(p['manufacturing'][k],k,nonnegative=True)
            if k=='scrap_fraction' and x>=1:raise ValueError('Scrap fraction must be below one')
    cost=p['cost']
    if not isinstance(cost,dict):raise ValueError('Cost provenance record required')
    if cost.get('source_class',cost.get('class','C')) not in ('A','B','C'):raise ValueError('Cost class A/B/C required')
    a,b=_bounds(cost,'cost',('lower_usd','upper_usd'))
    if a is not None:
        for k in ('currency','source_id','source_date','location','quantity_basis'):_text(cost.get(k),'cost '+k)
        if cost['currency']!='USD':raise ValueError('Converted USD cost record required with source currency retained separately')
    _unaccepted(p)
    return True


def make_occurrence(occurrence_id,part,parent_id=None,transform=None,scope='vehicle'):
    _part(part)
    pose=deepcopy(transform if transform is not None else [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
    _pose(pose)
    return dict(occurrence_id=occurrence_id,part_definition_id=part['physical_definition_id'],part_revision_id=part['revision_id'],
        parent_id=parent_id,transform=pose,scope=scope,pose_frame='registry',candidate_id=None,**FLAGS)


def _physical(r):
    return dict(parent_candidate_id=r.get('parent_candidate_id'),
        part_definitions=sorted(p['physical_definition_id'] for p in r['parts']),
        assemblies=deepcopy(r['assemblies']),required_functions=r['required_functions'],
        occurrences=[{k:o[k] for k in ('occurrence_id','part_definition_id','parent_id','transform','scope','pose_frame')} for o in r['occurrences']])


def make_registry(label,parts,occurrences,required_functions,parent_candidate_id=None,assemblies=(),materials=None):
    if materials is None:
        from .materials import catalogue
        materials=catalogue()['materials']
    r=dict(schema=SCHEMA,label=label,parent_candidate_id=parent_candidate_id,parts=deepcopy(list(parts)),
        occurrences=deepcopy(list(occurrences)),assemblies=deepcopy(list(assemblies)),materials=deepcopy(list(materials)),
        required_functions=list(required_functions),coordinate_frame=dict(name='registry',length_unit='m',mass_unit='kg',inertia_unit='kg*m2'),
        complete_installed_design=False,unknown_is_zero=False,**FLAGS)
    r['candidate_id']=identity(_physical(r))
    for o in r['occurrences']:o['candidate_id']=r['candidate_id']
    r['registry_id']=identity(r)
    validate_registry(r);return r


def validate_registry(r):
    if r.get('schema')!=SCHEMA or r.get('registry_id')!=identity({k:v for k,v in r.items() if k!='registry_id'}):raise ValueError('Registry schema/revision identity differs')
    if r.get('candidate_id')!=identity(_physical(r)):raise ValueError('Registry physical candidate identity differs')
    if r.get('complete_installed_design') is not False or r.get('unknown_is_zero') is not False:raise ValueError('Registry is not installed physical acceptance')
    _unaccepted(r);_strings(r['required_functions'],'required functions')
    if r.get('coordinate_frame')!=dict(name='registry',length_unit='m',mass_unit='kg',inertia_unit='kg*m2'):
        raise ValueError('Exact metre/kilogram registry coordinate frame required')
    if r.get('parent_candidate_id') is not None and not _id(r['parent_candidate_id']):raise ValueError('Physical ancestry identity required')
    if not isinstance(r.get('parts'),list) or not 1<=len(r['parts'])<=10000 or not isinstance(r.get('occurrences'),list) or not 1<=len(r['occurrences'])<=200000:
        raise ValueError('Bounded nonempty part and physical occurrence inventories required')
    if not isinstance(r.get('assemblies'),list) or len(r['assemblies'])>10000:
        raise ValueError('Bounded assembly inventory required')
    materials={}
    from .materials import validate_material
    for m in r['materials']:
        validate_material(m)
        if m['material_id'] in materials:raise ValueError('Duplicate material definition')
        materials[m['material_id']]=m
    parts={};revisions=set();logical=set()
    for p in r['parts']:
        _part(p);pid=p['physical_definition_id'];key=(p['part_id'],p['revision'])
        if pid in parts or p['revision_id'] in revisions or key in logical:raise ValueError('Duplicate or ambiguous part definition')
        parts[pid]=p;revisions.add(p['revision_id']);logical.add(key)
        if p['material_id'] is not None and p['material_id'] not in materials:raise ValueError('Part material definition absent')
        material=materials.get(p['material_id']);props=geometry_properties(p['geometry'])
        if material is not None and p.get('material_evaluation_id')!=material['material_evaluation_id']:
            raise ValueError('Part binds a stale/different material evaluation')
        mass=p['mass'].get('calculated_kg')
        if material is not None and props['volume_m3'] is not None and mass is not None and p['mass']['evidence_state']=='calculated':
            density=material['density_kg_m3']['nominal'];expected=props['volume_m3']*density
            if abs(expected-mass)>1e-7*max(1.,expected):raise ValueError('Net material geometry/calculated mass disagree')
    nodes={};used=set()
    for a in r['assemblies']:
        _text(a.get('id'),'assembly ID')
        if a['id'] in nodes:raise ValueError('Duplicate assembly ID')
        nodes[a['id']]=a.get('parent_id')
    for o in r['occurrences']:
        _text(o.get('occurrence_id'),'occurrence ID');oid=o['occurrence_id']
        if oid in nodes:raise ValueError('Duplicate physical occurrence or assembly ID')
        nodes[oid]=o.get('parent_id');_pose(o['transform'])
        if o.get('candidate_id')!=r['candidate_id'] or o.get('pose_frame')!='registry':raise ValueError('Mixed candidate or coordinate frame')
        part=parts.get(o['part_definition_id'])
        if part is None or o['part_revision_id']!=part['revision_id']:raise ValueError('Occurrence refers to missing/stale part revision')
        _text(o.get('scope'),'occurrence scope');used.add(o['part_definition_id'])
    if used!=set(parts):raise ValueError('Unused definitions cannot inflate registry coverage')
    for n,parent in nodes.items():
        seen={n}
        while parent is not None:
            if parent not in nodes:raise ValueError('Assembly/occurrence parent absent')
            if parent in seen:raise ValueError('Assembly graph has a cycle')
            seen.add(parent)
            if len(seen)>64:raise ValueError('Assembly hierarchy depth exceeds bounded contract')
            parent=nodes[parent]
    # One occurrence is one physical item: aggregated quantity and residual-account
    # rows cannot be inserted into the solid occurrence ledger a second time.
    if any(o.get('quantity',1)!=1 or o.get('accounted_mass_kg') is not None for o in r['occurrences']):
        raise ValueError('Explicit individual installations, not duplicate residual accounts, required')
    return True


def _rotate(I,R):
    return [[fsum(R[i][a]*I[a][b]*R[j][b] for a in range(3) for b in range(3)) for j in range(3)] for i in range(3)]


def summary(r):
    validate_registry(r);parts={p['physical_definition_id']:p for p in r['parts']}
    masses=[];lows=[];highs=[];known=[];all_exact=True;functions={f:[] for f in r['required_functions']};prices=[];per_scope={}
    gross=[];unresolved=[]
    for o in r['occurrences']:
        p=parts[o['part_definition_id']];m=p['mass'];v=m.get('calculated_kg');lo,hi=_bounds(m,'mass')
        if lo is None and v is not None:lo=hi=v
        lows.append(lo);highs.append(hi);masses.append(v)
        props=geometry_properties(p['geometry'],v);all_exact &= v is not None and props['inertia_kg_m2'] is not None
        if v is not None:known.append((o,p,v,props))
        if v is None:unresolved.append(o['occurrence_id'])
        for f in p['functions']:
            if f in functions:functions[f].append(o['occurrence_id'])
        price=_bounds(p['cost'],'cost',('lower_usd','upper_usd'));prices.append(price)
        scope=per_scope.setdefault(o['scope'],dict(occurrences=0,calculated_mass_kg=0.,lower_mass_kg=0.,upper_mass_kg=0.,unresolved_bounds=0))
        scope['occurrences']+=1;scope['calculated_mass_kg']+=v if v is not None else 0.
        if lo is None:scope['unresolved_bounds']+=1;scope['lower_mass_kg']=scope['upper_mass_kg']=None
        elif scope['lower_mass_kg'] is not None:scope['lower_mass_kg']+=lo;scope['upper_mass_kg']+=hi
        scrap=p['manufacturing'].get('scrap_fraction');volume=props['volume_m3']
        gross.append(None if volume is None or scrap is None else volume/(1-scrap))
    count=len(masses);total=fsum(v for v in masses if v is not None);cg=None;inertia=None
    if all_exact and total>0:
        cg=[fsum(v*o['transform'][j][3] for o,p,v,g in known)/total for j in range(3)]
        inertia=[[0.]*3 for _ in range(3)]
        for o,p,v,g in known:
            R=[line[:3] for line in o['transform'][:3]];rot=_rotate(g['inertia_kg_m2'],R);d=[o['transform'][j][3]-cg[j] for j in range(3)];norm=sum(x*x for x in d)
            for i in range(3):
                for j in range(3):inertia[i][j]+=rot[i][j]+v*((norm if i==j else 0.)-d[i]*d[j])
    result=dict(schema='osr-component-coverage/1',candidate_id=r['candidate_id'],registry_id=r['registry_id'],
        unique_part_definitions=len(parts),physical_occurrences=count,
        known_calculated_mass_kg=total,complete_nominal_mass_kg=total if len(known)==count else None,
        mass_lower_bound_kg=None if any(x is None for x in lows) else fsum(lows),
        mass_upper_bound_kg=None if any(x is None for x in highs) else fsum(highs),
        primitive_uniform_mass_CG_m=cg,primitive_uniform_mass_inertia_kg_m2=inertia,
        installed_CG_m=None,installed_inertia_kg_m2=None,
        mass_occurrence_coverage=0. if not count else len(known)/count,
        mass_bound_occurrence_coverage=0. if not count else sum(v is not None for v in lows)/count,
        price_occurrence_coverage=0. if not count else sum(a is not None for a,b in prices)/count,
        price_lower_bound_usd=None if any(a is None for a,b in prices) else fsum(a for a,b in prices),
        price_upper_bound_usd=None if any(b is None for a,b in prices) else fsum(b for a,b in prices),
        total_gross_blank_volume_m3=None if any(x is None for x in gross) else fsum(gross),
        functional_coverage={f:dict(occurrences=len(ids),present=bool(ids),qualified=False) for f,ids in functions.items()},
        missing_functions=[f for f,ids in functions.items() if not ids],unresolved_nominal_mass_occurrences=unresolved,
        scopes=per_scope,validation_coverage=0.,complete_installed_design=False,**FLAGS)
    result['evaluation_id']=identity(result);return result


def affected_dependencies(before,after):
    """A changed material/part invalidates physical downstream work, never release."""
    validate_registry(before);validate_registry(after)
    physical=before['candidate_id']!=after['candidate_id']
    property_revision=sorted(p.get('material_evaluation_id') for p in before['parts'] if p.get('material_evaluation_id'))!=sorted(p.get('material_evaluation_id') for p in after['parts'] if p.get('material_evaluation_id'))
    changed_mass=sorted(identity(p['mass']) for p in before['parts'])!=sorted(identity(p['mass']) for p in after['parts'])
    return dict(material_evaluation_revision=property_revision,mass_evaluation_revision=changed_mass,physical_revision=physical,from_candidate_id=before['candidate_id'],to_candidate_id=after['candidate_id'],
        invalidated_stages=['geometry','mass','structure','thermal','electrical','propulsion','braking','civil','manufacturing','cost','controls'] if physical else ['mass','structure','thermal','electrical','propulsion','braking','civil','manufacturing','cost','controls'] if property_revision or changed_mass else ['commercial-and-evidence-review'] if before['registry_id']!=after['registry_id'] else [],**FLAGS)


def screen_sweep(r,moving_occurrence_id,end_transform,*,tool_radius_m=0.,removed_before_motion=()):
    """Conservative finite removal/tool envelope against located stock.

    Constant-rotation translation uses an exact swept AABB of the part envelope.
    A rotation change uses the enclosing sphere swept between its two centres;
    no unsampled intermediate rotational clearance is claimed. Every other solid
    remains an obstacle unless explicitly declared removed before the motion.
    This reports potential interference, never an installed-access acceptance.
    """
    validate_registry(r);_pose(end_transform);radius=_number(tool_radius_m,'tool radius',nonnegative=True)
    parts={p['physical_definition_id']:p for p in r['parts']};occ={o['occurrence_id']:o for o in r['occurrences']}
    if moving_occurrence_id not in occ:raise ValueError('Moving occurrence absent')
    removed=list(removed_before_motion)
    if len(removed)!=len(set(removed)) or any(x not in occ or x==moving_occurrence_id for x in removed):raise ValueError('Explicit distinct pre-removed actual occurrences required')
    moving=occ[moving_occurrence_id];start=moving['transform'];g=geometry_properties(parts[moving['part_definition_id']]['geometry'])
    dims=g['envelope_dimensions_m'];same_rotation=all(abs(start[i][j]-end_transform[i][j])<1e-12 for i in range(3) for j in range(3))
    def halfwidth(o):
        d=geometry_properties(parts[o['part_definition_id']]['geometry'])['envelope_dimensions_m']
        return [sum(abs(o['transform'][i][j])*d[j]/2 for j in range(3)) for i in range(3)]
    h=halfwidth(moving) if same_rotation else [sqrt(sum(x*x for x in dims))/2]*3
    lower=[min(start[i][3],end_transform[i][3])-h[i]-radius for i in range(3)]
    upper=[max(start[i][3],end_transform[i][3])+h[i]+radius for i in range(3)]
    collisions=[]
    for oid,o in occ.items():
        if oid==moving_occurrence_id or oid in removed:continue
        other=halfwidth(o);lo=[o['transform'][i][3]-other[i] for i in range(3)];hi=[o['transform'][i][3]+other[i] for i in range(3)]
        if all(min(upper[i],hi[i])-max(lower[i],lo[i])>1e-10 for i in range(3)):collisions.append(oid)
    result=dict(candidate_id=r['candidate_id'],registry_id=r['registry_id'],moving_occurrence_id=moving_occurrence_id,
        start_transform=start,end_transform=deepcopy(end_transform),tool_radius_m=radius,
        removed_before_motion=removed,swept_AABB_m=dict(min=lower,max=upper),potential_interference_occurrence_ids=collisions,
        method='constant-rotation-envelope-translation' if same_rotation else 'conservative-enclosing-sphere-translation-and-rotation',
        state='potential-interference' if collisions else 'no-AABB-interference-for-declared-path',
        finite_path_checked=True,exact_contact_geometry_checked=False,lifting_retention_and_flexible_services_verified=False,
        complete_installed_geometry_verified=False,**FLAGS)
    result['evaluation_id']=identity(result);return result
