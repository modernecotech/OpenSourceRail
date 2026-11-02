"""Exact cut-plate geometry for a separate, unqualified 20m topology experiment.

Rows run upward from z=-1.38m. Fraction coordinates make physical identity
independent of an equivalent subdivision. Density, FE and cost assumptions
never enter the physical definition. Corner contact supplies no finite load path.
"""
from collections import deque,defaultdict
from fractions import Fraction as F
from math import fsum,isfinite,ceil
from pathlib import Path
from engineering.station_rail.common import identity,digest

PRODUCER='engineering/design_search/topology_geometry.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False)
DEFAULT_DENSITIES={'steel':7850.,'concrete':2500.}
DEFAULT_RESERVES={'deck_rebar':[500.,1000.,2000.],'connectors':[100.,250.,600.],'bearings':[100.,200.,400.],'bracing':[200.,500.,1000.],'protection_hardware':[50.,150.,400.]}
FIXED=dict(span_m=20.,deck_width_m=2.,deck_thickness_m=.18,web_height_m=1.2,web_thickness_m=.02,web_centres_y_m=(-.65,.65))


def _source():return {PRODUCER:digest(__file__)}
def _seal(v,key):v[key]=identity(v);return v
def _f(v):return str(F(str(v)))
def _float(v):return float(F(v))
def _positive(v):return type(v) in (int,float) and isfinite(v) and v>0


def _mask(mask):
    if hasattr(mask,'tolist'):mask=mask.tolist()
    if not isinstance(mask,(list,tuple)) or not mask or not isinstance(mask[0],(list,tuple)) or not mask[0]:raise ValueError('Nonempty rectangular binary mask required')
    nx=len(mask[0]);nz=len(mask)
    if max(nx,nz)>4096 or nx*nz>262144:raise ValueError('Bounded binary geometry mask required')
    if any(not isinstance(row,(list,tuple)) or len(row)!=nx or any(type(v) not in (bool,int) or v not in (0,1) for v in row) for row in mask):raise ValueError('Exact binary rectangular mask required')
    return [[bool(v) for v in row] for row in mask]


def _rectangles(mask,xs,zs):
    active={};done=[]
    for j,row in enumerate(mask):
        runs=[];i=0
        while i<len(row):
            if not row[i]:i+=1;continue
            start=i
            while i<len(row) and row[i]:i+=1
            runs.append((xs[start],xs[i]))
        new={}
        for run in runs:new[run]=(active[run][0],zs[j+1]) if run in active else (zs[j],zs[j+1])
        done.extend((a,b,c,d) for (a,b),(c,d) in active.items() if (a,b) not in new);active=new
    done.extend((a,b,c,d) for (a,b),(c,d) in active.items())
    return sorted(done)


def _grid(rects):
    xs=sorted({F(0),F(20),*(x for r in rects for x in r[:2])});zs=sorted({F('-1.38'),F('-.18'),*(z for r in rects for z in r[2:])})
    if len(rects)>262144 or (len(xs)-1)*(len(zs)-1)>262144:raise ValueError('Physical union grid budget exceeded')
    xi={x:i for i,x in enumerate(xs)};zi={z:i for i,z in enumerate(zs)};mask=[[False]*(len(xs)-1) for _ in range(len(zs)-1)]
    for a,b,c,d in rects:
        for j in range(zi[c],zi[d]):
            for i in range(xi[a],xi[b]):
                if mask[j][i]:raise ValueError('Overlapping physical rectangles')
                mask[j][i]=True
    return mask,xs,zs


def _components(mask,value):
    todo={(j,i) for j,row in enumerate(mask) for i,v in enumerate(row) if v==value};groups=[]
    while todo:
        seed=min(todo);todo.remove(seed);q=deque([seed]);group={seed}
        while q:
            j,i=q.popleft()
            for p in ((j-1,i),(j+1,i),(j,i-1),(j,i+1)):
                if p in todo:todo.remove(p);group.add(p);q.append(p)
        groups.append(group)
    return groups


def _geometry(rects):
    mask,xs,zs=_grid(rects);nz=len(mask);nx=len(mask[0]);edges=defaultdict(list)
    def occupied(j,i):return 0<=j<nz and 0<=i<nx and mask[j][i]
    for j,row in enumerate(mask):
        for i,v in enumerate(row):
            if not v:continue
            if not occupied(j-1,i):edges[('x',zs[j],1)].append((xs[i],xs[i+1]))
            if not occupied(j+1,i):edges[('x',zs[j+1],-1)].append((xs[i],xs[i+1]))
            if not occupied(j,i-1):edges[('z',xs[i],-1)].append((zs[j],zs[j+1]))
            if not occupied(j,i+1):edges[('z',xs[i+1],1)].append((zs[j],zs[j+1]))
    segments=[]
    for (axis,fixed,sign),intervals in sorted(edges.items()):
        merged=[]
        for a,b in sorted(intervals):
            if merged and merged[-1][1]==a:merged[-1]=(merged[-1][0],b)
            else:merged.append((a,b))
        for a,b in merged:
            start,end=([a,fixed],[b,fixed]) if axis=='x' else ([fixed,a],[fixed,b])
            if sign<0:start,end=end,start
            segments.append(dict(start_xz_m=list(map(float,start)),end_xz_m=list(map(float,end))))
    groups=_components(mask,True);void=_components(mask,False)
    holes=sum(not any(j in (0,nz-1) or i in (0,nx-1) for j,i in group) for group in void)
    corners=sum(occupied(j-1,i-1)==occupied(j,i) and occupied(j-1,i)==occupied(j,i-1) and occupied(j-1,i-1)!=occupied(j-1,i) for j in range(1,nz) for i in range(1,nx))
    area=sum((b-a)*(d-c) for a,b,c,d in rects)
    perimeter=fsum(abs(s['end_xz_m'][0]-s['start_xz_m'][0])+abs(s['end_xz_m'][1]-s['start_xz_m'][1]) for s in segments)
    centroid=None if not area else [float(sum((b-a)*(d-c)*(a+b)/2 for a,b,c,d in rects)/area),float(sum((b-a)*(d-c)*(c+d)/2 for a,b,c,d in rects)/area)]
    return dict(rectangles_xz_m=[[float(x) for x in r] for r in rects],area_m2=float(area),centroid_xz_m=centroid,boundary_segments_xz_m=segments,
        cut_perimeter_m=perimeter,hole_pierces=holes,finite_edge_components=len(groups),corner_only_contacts=corners,
        contour_starts_hypothesis=len(groups)+holes,one_finite_edge_component=len(groups)==1,manufacturability_proved=False,
        topology_screen='empty' if not groups else 'disconnected-or-corner-contact' if len(groups)!=1 or corners else 'connected-plane-geometry-only')


def realize(mask,*,span_m=20.,deck_width_m=2.,deck_thickness_m=.18,web_height_m=1.2,web_thickness_m=.02,web_centres_y_m=(-.65,.65)):
    args=dict(span_m=span_m,deck_width_m=deck_width_m,deck_thickness_m=deck_thickness_m,web_height_m=web_height_m,web_thickness_m=web_thickness_m,web_centres_y_m=tuple(web_centres_y_m))
    if args!=FIXED:raise ValueError('Fixed20m/2m retained-deck twin20mm-web research envelope required')
    mask=_mask(mask);nz=len(mask);nx=len(mask[0]);xs=[F(20)*i/nx for i in range(nx+1)];zs=[F('-1.38')+F('1.2')*j/nz for j in range(nz+1)];rects=_rectangles(mask,xs,zs)
    physical=dict(schema='osr-topology-physical-definition/1',deck=dict(dimensions_m=['20','2','9/50'],centre_m=['10','0','-9/100'],material_family='unqualified-research-concrete'),
        webs=dict(centres_y_m=['-13/20','13/20'],thickness_m='1/50',material_family='unqualified-structural-steel',rectangles_xz_m=[[str(x) for x in r] for r in rects]),
        interfaces=dict(span_m='20',deck_width_m='2',web_bottom_z_m='-69/50',web_top_z_m='-9/50'))
    value=dict(schema='osr-topology-realized-geometry/1',candidate_id=identity(physical),physical_definition=physical,web_geometry=_geometry(rects),nominal_parts=['retained-concrete-deck','cut-steel-web-left','cut-steel-web-right'],
        source_sha256=_source(),installed_mass_complete=False,minimum_feature_or_filter_proves_manufacturability=False,load_and_support_path_proved=False,**FLAGS)
    return _seal(value,'geometry_id')


def validate(candidate):
    if candidate.get('geometry_id')!=identity({k:v for k,v in candidate.items() if k!='geometry_id'}) or candidate.get('candidate_id')!=identity(candidate.get('physical_definition')):raise ValueError('Sealed physical geometry required')
    if candidate.get('source_sha256')!=_source() or any(candidate.get(k) is not False for k in FLAGS):raise ValueError('Current unqualified geometry source required')
    p=candidate['physical_definition'];rects=[tuple(F(x) for x in r) for r in p['webs']['rectangles_xz_m']]
    if any(not (0<=a<b<=20 and F('-1.38')<=c<d<=F('-.18')) for a,b,c,d in rects):raise ValueError('Physical rectangles outside fixed envelope')
    mask,xs,zs=_grid(rects)
    if _rectangles(mask,xs,zs)!=rects or candidate['web_geometry']!=_geometry(rects):raise ValueError('Canonical physical union differs')
    # Fixed fields cannot be tampered by resealing an otherwise valid record.
    expected=realize([[True]])['physical_definition'];expected['webs']['rectangles_xz_m']=p['webs']['rectangles_xz_m']
    if p!=expected:raise ValueError('Fixed physical interfaces differ')
    return rects


def _properties(boxes):
    masses=[a*b*c*rho for a,b,c,x,y,z,rho in boxes];mass=fsum(masses)
    if not mass:return dict(volume_m3=0.,mass_kg=0.,CG_m=None,inertia_tensor_kg_m2=None)
    cg=[fsum(m*p[3+i] for m,p in zip(masses,boxes))/mass for i in range(3)];inertia=[[0.]*3 for _ in range(3)]
    for m,p in zip(masses,boxes):
        var=[p[i]**2/12 for i in range(3)];offset=[p[3+i]-cg[i] for i in range(3)]
        for i in range(3):
            for j in range(3):inertia[i][j]+=m*((sum(var)+sum(x*x for x in offset)-var[i]-offset[i]**2) if i==j else -offset[i]*offset[j])
    return dict(volume_m3=fsum(p[0]*p[1]*p[2] for p in boxes),mass_kg=mass,CG_m=cg,inertia_tensor_kg_m2=inertia)


def quantities(candidate,densities=None,*,reserves_kg=None,module_length_m=5.):
    rects=validate(candidate);densities=dict(DEFAULT_DENSITIES if densities is None else densities);reserves={k:list(v) for k,v in (DEFAULT_RESERVES if reserves_kg is None else reserves_kg).items()}
    if set(densities)!=set(DEFAULT_DENSITIES) or any(not _positive(v) or not 1<=v<=1000000 for v in densities.values()):raise ValueError('Positive explicit steel/concrete density required')
    if set(reserves)!=set(DEFAULT_RESERVES) or any(len(v)!=3 or any(not _positive(x) for x in v) or not v[0]<=v[1]<=v[2] for v in reserves.values()):raise ValueError('Named positive low/base/high mass reserves required')
    if not _positive(module_length_m) or not 20/4096<=module_length_m<=20:raise ValueError('Positive bounded module length required')
    boxes=[(20.,2.,.18,10.,0.,-.09,densities['concrete'])]
    for y in (-.65,.65):
        boxes.extend((float(b-a),.02,float(d-c),float((a+b)/2),y,float((c+d)/2),densities['steel']) for a,b,c,d in rects)
    props=_properties(boxes);mass=props['mass_kg'];cg=props['CG_m'];inertia=props['inertia_tensor_kg_m2']
    n=len(rects);parts=[dict(part_id='retained-concrete-deck',**_properties(boxes[:1])),dict(part_id='cut-steel-web-left',**_properties(boxes[1:1+n])),dict(part_id='cut-steel-web-right',**_properties(boxes[1+n:]))]
    area=candidate['web_geometry']['area_m2'];perimeter=candidate['web_geometry']['cut_perimeter_m'];cuts=[];x=module_length_m
    while x<20-1e-12:
        position=F(str(x));left=[(c,d) for a,b,c,d in rects if a<position<=b];right=[(c,d) for a,b,c,d in rects if a<=position<b];length=sum(max(F(0),min(d,v)-max(c,u)) for c,d in left for u,v in right)
        cuts.append(dict(x_m=x,ligament_length_per_web_m=float(length),two_web_weld_seam_m=2*float(length)));x+=module_length_m
    nmodules=ceil(20/module_length_m);modules=[]
    for k in range(nmodules):
        lo=F(str(module_length_m))*k;hi=min(F(20),lo+F(str(module_length_m)))
        clipped=[(max(a,lo),min(b,hi),c,d) for a,b,c,d in rects if max(a,lo)<min(b,hi)]
        shape=_geometry(clipped)
        modules.append(dict(index=k,x_min_m=float(lo),x_max_m=float(hi),finite_edge_pieces_per_web=shape['finite_edge_components'],hole_pierces_per_web=shape['hole_pierces'],contour_starts_per_web_hypothesis=shape['contour_starts_hypothesis'],cut_perimeter_per_web_m=shape['cut_perimeter_m']))
    contact=2*.02*float(sum(b-a for a,b,c,d in rects if d==F('-.18')))
    steel_total=2*(2*area+.02*perimeter);steel_volume=2*area*.02;steel_mass=steel_volume*densities['steel'];deck_volume=7.2
    value=dict(schema='osr-topology-quantities/1',candidate_id=candidate['candidate_id'],geometry_id=candidate['geometry_id'],densities_kg_m3=densities,
        quantities=dict(deck_concrete_m3=deck_volume,steel_net_volume_m3=steel_volume,steel_net_mass_kg=steel_mass,deck_concrete_mass_kg=deck_volume*densities['concrete'],
            nominal_mass_kg=mass,nominal_CG_m=cg,nominal_inertia_tensor_kg_m2=inertia,nominal_part_quantities=parts,steel_total_surface_area_m2=steel_total,steel_exposed_area_m2=steel_total-contact,deck_exposed_area_m2=2*(20*2+20*.18+2*.18)-contact,steel_deck_contact_area_m2=contact,
            two_web_cut_perimeter_m=2*perimeter,two_web_hole_pierces=2*candidate['web_geometry']['hole_pierces'],two_web_contour_starts_hypothesis=2*candidate['web_geometry']['contour_starts_hypothesis'],
            steel_full_stock_envelope_kg=2*20*1.2*.02*densities['steel']),
        handling=dict(module_length_m=module_length_m,modules_per_web=nmodules,plate_handling_modules=2*nmodules,module_geometry=modules,actual_cut_pieces=2*sum(m['finite_edge_pieces_per_web'] for m in modules),two_web_module_hole_pierces=2*sum(m['hole_pierces_per_web'] for m in modules),two_web_module_contour_starts_hypothesis=2*sum(m['contour_starts_per_web_hypothesis'] for m in modules),splices=cuts,two_web_splice_ligament_m=fsum(c['two_web_weld_seam_m'] for c in cuts),two_web_module_cut_perimeter_m=2*perimeter+2*fsum(c['two_web_weld_seam_m'] for c in cuts),
            steel_surface_before_joining_m2=steel_total+2*.02*fsum(c['two_web_weld_seam_m'] for c in cuts),module_partition_is_manufacturing_hypothesis=True,splice_strength_and_detail_qualified=False),
        reserve_mass_kg=reserves,accounted_mass_kg_cases=[mass+fsum(v[i] for v in reserves.values()) for i in range(3)],reserve_CG_and_inertia_unknown=True,
        source_sha256=_source(),installed_mass_complete=False,complete_installed_mass_kg=None,**FLAGS)
    return _seal(value,'evaluation_id')
