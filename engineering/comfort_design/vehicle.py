"""One explicit comfort-car proposal, with stock/geometry/unknowns kept distinct.

This generator replaces exact counted stock. It never spreads the retained
equipment allowance into fictitious solids, nor treats reference HVAC internals
or an analytical seat fixture as a released installed assembly.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np

from engineering.comfort_options import envelope, glazing, layout, seats_doors, systems
from engineering.equipped_vehicle import inventory as equipped
from engineering.ferrite_maglev import candidate_magnetics
from engineering.halbach_scaling import candidates, vehicles
from . import ROOT, PARENT_REVISION, FLAGS

SCHEMA='osr-matched-comfort-vehicle/1'
G=9.80665


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def _stock(name,volume,density,quantity=1,**extra):
    return dict(id=name,volume_m3_each=volume,density_kg_m3=density,quantity=quantity,
                total_mass_kg=volume*density*quantity,**extra)


def _component_mass(parts):return math.fsum(p['total_mass_kg'] for p in parts)


def _roof_stock(t,c):
    rows=deepcopy(envelope._new_stock('roof','aluminium',t,60))
    for p in rows:
        ratio=1.
        if p['id'] in ('core/trimmed-foam','edge/GFRP-vertical-ring'):ratio=c/.04
        elif p['id']=='attachment/aluminium-sleeve':ratio=(c+2*t)/(.04+2*t)
        elif p['id']=='attachment/M6-shank':ratio=(c+2*t+.012)/(.04+2*t+.012)
        p['volume_m3_each']*=ratio
        p['total_mass_kg']=p['volume_m3_each']*p['density_kg_m3']*p['quantity']
        if 'core_thickness_m' in p:p['core_thickness_m']=c
        if 'length_m' in p:p['length_m']=c+2*t+(.012 if p['id']=='attachment/M6-shank' else 0.)
        for name in ('displaced_edge_wall_volume_m3_each','displaced_insert_volume_m3_each'):
            if name in p:p[name]*=c/.04
    # A2mm perimeter bearing rises above the old panel datum. Four strips meet
    # without overlapping corners; this is new material, not a free datum shift.
    w=.0447
    area=17*2.65-(17-2*w)*(2.65-2*w)
    rows.append(_stock('datum/GFRP-perimeter-bearing',area*.002,1900.,
                       width_m=w,thickness_m=.002,outer_size_m=[17.,2.65]))
    return rows


def roof_revision(root=ROOT):
    """Four bounded revisions after the added-rib/global-frame interference."""
    variants=[]
    for t,c in ((.0012,.040),(.0013,.040),(.0012,.045),(.0013,.045)):
        stock=_roof_stock(t,c);mass=_component_mass(stock)
        fixtures=[]
        for pressure in (750.,1500.):
            f=envelope.sandwich_strip(t-.00004,c-.0005,69e9,16e6,2.125,
                                      pressure+mass*G/(17*2.65))
            f.update(imposed_pressure_Pa=pressure,nominal_skin_m=t,minimum_skin_m=t-.00004,
                     nominal_core_m=c,minimum_core_m=c-.0005,
                     shear_necessary_screen='pass' if f['core_peak_shear_Pa']<=.63e6/2 else 'fail',
                     face_necessary_screen='pass' if f['face_peak_bending_stress_Pa']<=260e6*.5/1.5 else 'fail')
            fixtures.append(f)
        physical=dict(component='roof-panel-on-retained-ribs',skin_each_m=t,core_m=c,
            core_grade='Divinycell-H60-proposal',skin_grade='6082-T6-sheet-proposal',
            nominal_support_span_m=2.125,extra_crossrails=0,stock_parts=stock,
            bottom_skin_datum_m=2.7573,bearing_rise_m=.002,
            body_outer_roof_top_m=2.7573+c+2*t+.0007,
            face_lap_growth_m=.0015,lap_bond_growth_m=.0002,
            source_parent_id='roof/aluminium/0.9mm/core-60')
        checks=[f[k] for f in fixtures for k in ('deflection_necessary_screen','shear_necessary_screen','face_necessary_screen')]
        variants.append(dict(physical_definition=physical,physical_definition_id=identity(physical),
            counted_mass_kg=mass,stock_parts=stock,fixtures=fixtures,
            necessary_screen='pass' if all(x=='pass' for x in checks) else 'fail',
            installed_mass_kg=None,global_body_qualified=False))
    passing=sorted((v for v in variants if v['necessary_screen']=='pass'),key=lambda v:v['counted_mass_kg'])
    if not passing:raise ValueError('no necessary-screen roof revision; refuse integrated design')
    chosen=passing[0]
    frame=vehicles._frame('6082-six-cell-deep-40kn',Path(root))
    longitudinal=[p for p in frame['stock_parts'] if 'roof-longitudinal' in p['id'] and 'at_m' in p]
    top=max(p['at_m'][2]+p['size_m'][2]-.3 for p in longitudinal)
    low=chosen['physical_definition']['bottom_skin_datum_m']-.0017
    if low<=top:raise ValueError('revised roof laps still overlap primary roof rails')
    # Actual material-prism intersections of the rejected150mm crossrail option.
    failed=next(r for r in envelope.options(root) if r['id'].endswith('crossrail-150x60x3mm'))
    overlaps=[]
    for i in range(8):
        cx=-8.5+(i+.5)*2.125
        for wall in _tube_boxes(f'crossrail/{i}',[.06,2.65,.15],[cx-.03,-1.325,2.7553-.152],1,.003,2710.):
            for p in longitudinal:
                at=[p['at_m'][0],p['at_m'][1],p['at_m'][2]-.3]
                dims=[max(0.,min(wall['at_m'][j]+wall['size_m'][j],at[j]+p['size_m'][j])-max(wall['at_m'][j],at[j])) for j in range(3)]
                vol=math.prod(dims)
                if vol>1e-14:overlaps.append(dict(crossrail_part_id=wall['id'],frame_part_id=p['id'],common_volume_m3=vol))
    if not overlaps:raise ValueError('retained crossrail/global-frame collision control must fail')
    return dict(selected=chosen,variants=variants,
        revision_reason='The150mm crossrail proposal interferes with retained primary roof longitudinal material. Thicker skins and45mm core retain the original ribs, with a counted2mm bearing rise.',
        selected_minimum_rail_clearance_m=low-top,
        rejected_crossrail=dict(component_id=failed['physical_definition_id'],necessary_local_fixture='pass',
            matched_assembly_screen='fail',collisions=overlaps,total_common_volume_m3=math.fsum(p['common_volume_m3'] for p in overlaps),
            physical_rejection='No free notch or silently deleted primary rail; original evidence retained'),
        global_stiffness_joints_fire_and_hvac='unknown')


def _primitive(name,size,at,density,*,kind='box',holes=None,**extra):
    value=dict(id=name,kind=kind,size_m=list(size),at_m=list(at),density_kg_m3=density,**extra)
    volume=math.prod(size) if kind=='box' else math.pi*(size[0]/2)**2*size[2]
    if holes:
        value['holes']=deepcopy(holes)
        for h in holes:
            axis='xyz'.index(h.get('axis','z'))
            volume-=math.pi*(h['diameter_m']/2)**2*h.get('length_m',size[axis])
    value['volume_m3']=volume
    source={**value,'density_assumption_kg_m3':density}
    mass,cg,inertia=candidate_magnetics._region_mass_properties(source)
    value.update(mass_kg=float(mass),cg_m=cg.tolist(),inertia_kg_m2=inertia.tolist())
    return value


def _tube_boxes(name,size,at,axis,wall,density):
    u,v=[i for i in range(3) if i!=axis];parts=[]
    for coordinate,label in ((u,'u'),(v,'v')):
        for sign in (-1,1):
            sz=list(size);p=list(at);sz[coordinate]=wall
            if sign>0:p[coordinate]+=size[coordinate]-wall
            if coordinate==v:sz[u]-=2*wall;p[u]+=wall
            parts.append(_primitive(f'{name}/{label}/{sign}',sz,p,density))
    return parts


def _ring_boxes(name,L,W,h,at,wall,density):
    x,y,z=at
    return [_primitive(name+'/left',[L,wall,h],[x,y,z],density),
            _primitive(name+'/right',[L,wall,h],[x,y+W-wall,z],density),
            _primitive(name+'/front',[wall,W-2*wall,h],[x,y+wall,z],density),
            _primitive(name+'/back',[wall,W-2*wall,h],[x+L-wall,y+wall,z],density)]


def _occurrence(name,mass,system,source,*,geometries=(),evidence='unlocated-counted-material',role=''):
    return dict(id=name,source_part_id=source,system=system,mass_kg=mass,evidence_class=evidence,
        role=role,geometry_parts=list(geometries),global_installation_location_known=bool(geometries),
        installed_location_qualified=False,structural_participation=dict(intended=system in ('body','frame-joints','seating','magnetics','hardpoints'),demonstrated=None),
        assembly_function=dict(insertion='Install using identified datum and retained access envelope; detailed swept paths unqualified',
            inspection='Stock identity, measured mass/dimensions, fastener/bond and functional checks required',
            removal='Isolate stored energy; secure adjoining loads; prove lifting and removal access',
            assembly_swept_path_verified=False))


def _seat_units(cabin):
    groups=defaultdict(list)
    for p in cabin['geometry']['seats']:
        if p['kind']=='wall-bench-seat':key=('wall',-1 if (p['x0_m']+p['x1_m'])<0 else 1)
        else:key=('transverse',round(p['x0_m'],8),-1 if p['y0_m']<0 else 1)
        groups[key].append(p)
    units=[]
    for key,places in sorted(groups.items(),key=lambda item:str(item[0])):
        n=len(places)
        if n not in (1,2):raise ValueError('one/two adjacent seat places per unit required')
        bounds=[min(p['x0_m'] for p in places),min(p['y0_m'] for p in places),
                max(p['x1_m'] for p in places),max(p['y1_m'] for p in places)]
        units.append(dict(id='seat-unit/'+str(len(units)),kind=key[0],places=n,
                          place_ids=[p['id'] for p in places],bounds_xy_m=bounds,
                          rotation_z_deg=90 if key[0]=='wall' else 0, gross_leg_stock_m=.42,proposed_installed_leg_cut_m=.40))
    if sum(u['places'] for u in units)!=44:raise ValueError('seat unit map must contain44 places')
    return units


def _single_fixture(pair):
    """Keep four legs/back supports; halve pan width and rail span only."""
    value=deepcopy(pair);width=.47;parts=[]
    for p in pair['stock_parts']:
        p=deepcopy(p);name=p['id'];volume=p['volume_m3_each']
        if name in ('pan/skins','back/skins','pan-back/H80-core','panel/bond','pan/foam-pad'):volume*=.5
        elif name=='panel/GFRP-edge-closure':volume=(2*(width+.48)+2*(width+.60))*(.03+2*.0008)*.001
        elif name=='support/Al-RHS-rails':volume*=.5
        p['volume_m3_each']=volume;p['mass_kg']=volume*p['density_kg_m3']*p['quantity'];parts.append(p)
    pan=seats_doors.pan_fixture(width=.47,span=.48,face=.0008,core=.03,load=1500.,young=pair['materials']['gfrp_E_Pa'])
    rail=seats_doors.beam_fixture(width=.03,depth=.05,wall=.002,span=.47,total_load=1500.)
    total=pan['total_deflection_m']+rail['deflection_m']
    physical=dict(parent_component_id=pair['component_id'],places=1,width_m=width,stock_parts=parts,
                  retained_legs=4,retained_uprights=2,retained_fasteners=16)
    return dict(physical_definition=physical,component_id=identity(physical),stock_parts=parts,
        counted_mass_kg=math.fsum(p['mass_kg'] for p in parts),fixtures=dict(pan=pan,rail=rail,total_deflection_m=total),
        necessary_screen='pass' if total<=.005 and pan['small_deflection_domain'] and pan['face_stress_Pa']<=pair['materials']['gfrp_strength_Pa']/1.5 else 'fail',
        installed_mass_kg=None,physical_accepted=False)


def _seat_geometry(unit,fixture):
    """Located skin/core/support material; joints/fasteners remain unlocated."""
    width=.47*unit['places'];x0,y0,x1,y1=unit['bounds_xy_m'];p=[]
    def box(name,size,at,rho):p.append(_primitive(unit['id']+'/'+name,size,at,rho))
    # Local seating coordinates: x along the two-place pan, y fore/aft.
    local=[]
    for label,depth,height in (('pan',.48,.03),('back',.60,.03)):
        if label=='pan':
            for k,z in enumerate((.45,.45+.0308)):local.append(_primitive(label+f'/skin/{k}',[width,depth,.0008],[0,.0316,z],1900.))
            local.append(_primitive(label+'/core',[width,depth,.03],[0,.0316,.4508],80.))
            local.append(_primitive('pan/foam',[width,depth,.03],[0,.0316,.4816],50.))
        else:
            for k,y in enumerate((0.,.0308)):local.append(_primitive(label+f'/skin/{k}',[width,.0008,.60],[0,y,.4816],1900.))
            local.append(_primitive(label+'/core',[width,.03,.60],[0,.0008,.4816],80.))
    area=seats_doors.rhs(.03,.05,.002)['area_m2']
    for j,y in enumerate((.06,.45)):
        local.extend(_tube_boxes(f'rail/{j}',[width,.03,.05],[0,y,.40],0,.002,2700.))
    for j,(x,y) in enumerate(((.03,.06),(width-.06,.06),(.03,.45),(width-.06,.45))):
        local.extend(_tube_boxes(f'leg/{j}',[.03,.05,.40],[x,y,0.],2,.002,2700.))
    # Exact stock geometry of the pan/legs is a proposed placement. Some
    # physical joints meet/overlap until cuts and weld/bond design are completed.
    for q in local:
        size=q['size_m'];a=q['at_m']
        if unit['kind']=='wall':sz=[size[0],size[1],size[2]];at=[x0+a[0],y0+a[1],a[2]]
        else:sz=[size[1],size[0],size[2]];at=[x0+.16+a[1],y0+a[0],a[2]]
        p.append(_primitive(unit['id']+'/'+q['id'],sz,at,q['density_kg_m3']))
    return p


def _panel_geometry(option,role):
    definition=option['physical_definition'];t=definition.get('skin_each_m',option.get('face_m',.0009))
    c=definition.get('core_m',.06 if role=='floor' else .045)
    if role=='floor':t=.0009;c=.06;bottom=-(c+2*t+.001)
    else:bottom=definition['bottom_skin_datum_m']
    bond=.001 if role=='floor' else .0007
    top_core=bottom+t+bond/2+c;core_z=bottom+t+bond/2
    parts=[]
    for i in range(8):
        for j in range(3):
            name=f'{role}/panel/{i}/{j}';x=-8.5+i*2.125;y=-1.325+j*(2.65/3);L=2.125;W=2.65/3
            for label,z in (('bottom',bottom),('top',top_core+bond/2)):
                parts.append(_primitive(name+'/skin/'+label,[L,W,t],[x,y,z],2710.))
            holes=[dict(axis='z',diameter_m=.020,x_m=xx,y_m=yy) for xx in (.020,L-.020) for yy in (.020,W-.020)]
            # The core edge walls displace actual foam; insert holes are cut.
            parts.append(_primitive(name+'/core',[L-.003,W-.003,c],[x+.0015,y+.0015,core_z],80. if role=='floor' else 60.,holes=[dict(h,x_m=h['x_m']-.0015,y_m=h['y_m']-.0015) for h in holes]))
            parts.extend(_ring_boxes(name+'/edge',L,W,c,[x,y,core_z],.0015,1900.))
            for label,z in (('bottom',bottom-.0015),('top',top_core+bond/2+t)):
                parts.extend(_ring_boxes(name+'/lap/'+label,L,W,.0015,[x,y,z],.020,1900.))
    if role=='roof':
        parts.extend(_ring_boxes('roof/datum-bearing',17,2.65,.002,[-8.5,-1.325,2.7553],.0447,1900.))
    return parts


@lru_cache(maxsize=2)
def _parent(root_name):
    root=Path(root_name)
    body=next(b for b in vehicles.variants(root) if b['candidate_id']==systems.BODY_ID)
    magnet=next(m for m in candidates.candidates(root) if m['physical_id']==systems.MAGNET_ID)
    return body,magnet,equipped.build_inventory(body,magnet,root=root)


def _source(root,records):
    sources={}
    for value in records:
        for name,digest in value.get('source_sha256',{}).items():
            if name in sources and sources[name]!=digest:raise ValueError('mixed vehicle source '+name)
            sources[name]=digest
    for name in ('engineering/comfort_design/brief.json','engineering/comfort_design/__init__.py','engineering/comfort_design/vehicle.py','engineering/comfort_design/native_vehicle.py'):
        path=Path(__file__).with_name('__init__.py') if name.endswith('/__init__.py') else Path(__file__) if name.endswith('/vehicle.py') else Path(__file__).with_name('native_vehicle.py') if name.endswith('/native_vehicle.py') else root/name
        if path.is_file():sources[name]=sha256(path.read_bytes()).hexdigest()
    return dict(sorted(sources.items()))


def build(root=ROOT):
    root=Path(root).resolve();brief=json.loads((root/'engineering/comfort_design/brief.json').read_bytes())
    cabin=layout.primary_options(root=root)['bench_default'];window=glazing.options(2)[0]
    comparison=systems.evaluate(cabin,window,root=root)
    panels=envelope.options(root)
    floor=min((p for p in panels if p['component']=='floor' and p['necessary_screen']=='pass'),key=lambda p:p['counted_mass_kg'])
    roof=roof_revision(root);selected_roof=roof['selected']
    furnishings=seats_doors.options(root=root)
    pair=next(p for p in furnishings if p['component']=='bench' and p['necessary_screen']=='pass')
    single=_single_fixture(pair)
    if single['necessary_screen']!='pass':raise ValueError('single-seat derivative must pass necessary fixture')
    door=min((p for p in furnishings if p['component']=='door' and p['necessary_screen']=='pass'),key=lambda p:p['counted_mass_kg'])
    units=_seat_units(cabin);seat_mass=math.fsum((pair if u['places']==2 else single)['counted_mass_kg'] for u in units)
    if seat_mass>800:raise ValueError('seat proposal exceeds retained interior budget')
    old_body,magnet,parent=_parent(str(root));rows=[];geometry=[];removed=[]
    for row in deepcopy(parent['occurrences']):
        if row['id'].startswith(('retained/panel/floor/','retained/panel/roof/')) or row['system'] in ('doors','glazing'):
            removed.append(dict(id=row['id'],mass_kg=row['mass_kg']));continue
        if row['id']=='retained/unlocated-equipment-residual':
            row['mass_kg']-=800.;row['role']='Residual allocation excluding explicitly resolved800kg interior account; not a physical equipment inventory'
        rows.append(row)
        old_geometry=row.get('geometry')
        if old_geometry:
            p=old_geometry.get('primitive_source')
            if p:
                p=deepcopy(p);p['id']=row['id'];offset=old_geometry.get('source_coordinate_translation_m',[0,0,0])
                p['at_m']=[a+b for a,b in zip(p['at_m'],offset)]
                rho=p.get('density_assumption_kg_m3',p.get('density_kg_m3'))
                if rho is None:rho=row['mass_kg']/p['volume_m3']
                # Parent primitives carry exact cut volumes and signed moments.
                q=deepcopy(p);q['density_kg_m3']=rho
                q['mass_kg']=old_geometry['mass_kg'];q['cg_m']=old_geometry['cg_m'];q['inertia_kg_m2']=old_geometry['inertia_kg_m2']
                geometry.append(q)
            elif 'size_m' in old_geometry:
                q=deepcopy(old_geometry);q['density_kg_m3']=q.get('density_kg_m3',row['mass_kg']/math.prod(q['size_m']));q['volume_m3']=math.prod(q['size_m']);geometry.append(q)
    # All new bodies inherit the same exact local PM material bundle, with
    # explicit proposed bank transforms. This is geometry, not accepted mount fit.
    mounts=[dict(id=f'module/{i:02d}',translation_m=[float(x),float(y),-1.16],rotation_xyz_deg=[0.,0.,0.],
                 facing_normal=[0.,0.,1.],reference_gap_m=.012,carrier_interface_qualified=False)
            for i,(y,x) in enumerate((y,x) for y in (-.88,.88) for x in np.arange(-5.5,6.,1.))]
    for row in rows:
        if row['id'].startswith('module/'):
            module=int(row['id'].split('/')[1]);local=row['local_geometry'];at=[a+b for a,b in zip(local['at_m'],mounts[module]['translation_m'])]
            p=_primitive(row['id'],local['size_m'],at,local['density_kg_m3'])
            row['geometry_parts']=[p];row['global_installation_location_known']=True
            row['pose_basis']='Proposed inherited bank datum; new carrier/retention/clearance qualification required'
            geometry.append(p)
    for kind,option in (('floor',floor),('roof',selected_roof)):
        parts=_panel_geometry(option,kind);geometry.extend(parts)
        rows.append(_occurrence('new-'+kind,option['counted_mass_kg'],'body',option['physical_definition_id'],
            geometries=parts,evidence='counted-component-with-partial-proposed-geometry',role='Panel stock plus explicitly counted edges/bonds/fasteners; not all hardware located'))
    for unit in units:
        fixture=pair if unit['places']==2 else single;parts=_seat_geometry(unit,fixture);geometry.extend(parts)
        rows.append(_occurrence(unit['id'],fixture['counted_mass_kg'],'seating',fixture['component_id'],geometries=parts,
            evidence='counted-fixture-with-proposed-material-placement',role='Fixture stock; back supports, edge closures, bonds and all fixings not fully located'))
    rows.append(_occurrence('interior/retained-unlocated-remainder',800-seat_mass,'seating','ancestor/interior800',
        evidence='unlocated-allocation',role='Unlocated rest of retained800kg account; not a saving or measured other interior'))
    for i,x in enumerate(cabin['door_centres_x_m']):
        door_parts=[]
        for leaf in (0,1):
            start=x-.7+leaf*.7
            # Four disjoint rectangles around the exact0.5x1m window void.
            rectangles=[(0.,0.,.1,2.1),(.6,0.,.1,2.1),(.1,0.,.5,.55),(.1,1.55,.5,.55)]
            for layer,y,t,rho in (('inner',1.264,.0005,2700.),('core',1.2645,.060,80.),('outer',1.3245,.0005,2700.)):
                for k,(dx,z,w,h) in enumerate(rectangles):
                    door_parts.append(_primitive(f'door/{i}/leaf/{leaf}/{layer}/{k}',[w,t,h],[start+dx,y,z],rho))
        geometry.extend(door_parts)
        rows.append(_occurrence(f'door/{i}/leaf-stock',door['counted_mass_kg'],'doors',door['component_id'],geometries=door_parts,
            evidence='counted-component-with-partial-proposed-geometry',role='Two61mm-deep proposed leaves; panevoids and opaque panels located; edges, seals and fixings require matched joint geometry'))
        rows.append(_occurrence(f'door/{i}/operator-reference',41.,'doors','Wabtec-ES2-1300mm-reference',evidence='supplier-reference',role='1400mm actual mechanism and deeper-leaf integration unqualified'))
    for p in window['stock_parts']:
        rows.append(_occurrence('glazing/'+p['id'],p['total_mass_kg'],'glazing',window['physical_definition_id']))
    # Actual glass/PVB planes, without inventing equipment internals or treating
    # the body surface as an uncut continuous pane.
    windows=[]
    for side in (-1,1):
        for i,x in enumerate((-6.5,-1.5,1.5,6.5)):
            windows.append(dict(id=f'fixed-window/{side}/{i}',size_m=[2.,.00676,1.5],at_m=[x-1.,side*1.321-.00338,.9]))
    for i,x in enumerate(cabin['door_centres_x_m']):
        for j in (0,1):windows.append(dict(id=f'door-window/{i}/{j}',size_m=[.5,.00676,1.],at_m=[x-.7+j*.7+.1,1.317,.55]))
    for pane in windows:
        x,y,z=pane['at_m'];sx,_,sz=pane['size_m']
        for label,thick,rho,off in (('glass-outer',.003,2500.,0.),('PVB',.00076,1070.,.003),('glass-inner',.003,2500.,.00376)):
            geometry.append(_primitive(pane['id']+'/'+label,[sx,thick,sz],[x,y+off,z],rho))
    # Two deleted opposite-side openings receive the same counted opaque infill.
    for i,x in enumerate((-4.5,4.5)):
        y=-1.325
        for label,t,rho in (('outer',.002,1900.),('core',.04,80.),('inner',.002,1900.),('bond',.0007,1000.)):
            geometry.append(_primitive(f'infill/{i}/{label}',[1.4,t,2.1],[x-.7,y,0.],rho));y+=t
    rows.append(_occurrence('infill/blanked-door-stock',cabin['infill_stock']['total_mass_kg'],'body','comfort-layout/infill',role='Original aperture frames retained; opaque skins/core/bond counted'))
    # Door leaf stock is located as panel/edge assembly envelopes only, never as
    # a solid block with the operator-reference mass smeared into it.
    door_envelopes=[dict(id=f'door/{i}',opening_centre_x_m=x,closed_leaf_depth_m=.061,
        opening_size_m=[1.4,2.1],closed_bounds_m=[x-.7,1.264,0.,x+.7,1.325,2.1],
        proposed_open_sweep_bounds_m=[x-1.4,1.327,0.,x+1.4,1.388,2.1],
        geometry_is_material=False,installed_mechanism_qualified=False) for i,x in enumerate((-4.5,4.5))]
    top=selected_roof['physical_definition']['body_outer_roof_top_m']
    packages=[dict(id=f'HVAC/{i}',centre_m=[x,0.,top+.02+.357/2],size_m=[2.655,2.083,.357],
        geometry_is_material=False,mass_reference_kg=192.,actual_50C_performance_known=False)
        for i,x in enumerate((-5.91,-2.955,0.,2.955,5.91))]
    # The old located material is not a globally solved flexible body, and new
    # stock placements can overlap at unresolved joints. Keep those holds visible.
    for p in geometry:
        p.setdefault('volume_m3',p['mass_kg']/p['density_kg_m3'])
    geometry_ids=[p['id'] for p in geometry]
    if len(geometry_ids)!=len(set(geometry_ids)):raise ValueError('duplicate geometry identity')
    accounted=math.fsum(p['mass_kg'] for p in rows)
    expected=comparison['mass']['accounted_tare_kg_per_car']+floor['counted_mass_kg']-700.5275+selected_roof['counted_mass_kg']-518.075+2*door['counted_mass_kg']-comparison['mass']['added']['door_leaf_stock_kg']
    if not math.isclose(accounted,expected,abs_tol=1e-6):raise ValueError('exact stock replacements do not close '+str((accounted,expected)))
    located=equipped.combine([dict(id=p['id'],mass_kg=p['mass_kg'],cg_m=p['cg_m'],inertia_kg_m2=p['inertia_kg_m2']) for p in geometry])
    if located['mass_kg']>accounted:raise ValueError('partial located material exceeds accounted stock')
    body_physical=dict(parent_body_candidate_id=systems.BODY_ID,layout_id=cabin['physical_geometry_id'],
        floor_component_id=floor['physical_definition_id'],roof_component=selected_roof['physical_definition'],
        door_component_id=door['component_id'],glazing_component_id=window['physical_definition_id'],
        paired_seat_component_id=pair['component_id'],single_seat_component=single['physical_definition'],seat_units=units,
        door_interfaces=door_envelopes,HVAC_reference_layout=packages,
        geometry_definition_id=identity([{k:p[k] for k in ('id','kind','size_m','at_m','density_kg_m3','holes') if k in p} for p in geometry if not p['id'].startswith('module/')]),
        retained_unlocated_account_treatment='Subtract800 interior, identify counted seat stock, retain all remaining allowance unlocated')
    body_id=identity(body_physical)
    physical=dict(body_candidate_id=body_id,body=body_physical,magnet_component_id=magnet['physical_id'],
        module_mounts=mounts,cars=6,fixed_seats_per_car=44,wheelchair_places_per_car=2,planned_standing_per_car=0)
    cid=identity(physical)
    sources=_source(root,[parent,comparison,floor,pair,door,cabin])
    unknown=deepcopy(parent['missing_inventory'])
    for item in unknown:
        if item['system']=='seating':item['reason']='44 seats are dimensioned and counted, including four single-seat derivatives; back/leg/anchor strength, fire and swept installation remain open'
        if item['system']=='magnetics':item['reason']='24 explicit proposed mounting transforms now exist; actual carrier fit, retention and multiaxis operating maps remain unqualified'
    unknown += [dict(id='roof/global-joints-and-material-correlation',system='body',mass_kg=None,
                    reason='New45mm-core roof retains ribs; complete stiffness, lap/bearing joints, fire, hot properties and actual support reactions need verification'),
                dict(id='doors/deeper-opening-track-interlocks',system='doors',mass_kg=None,
                    reason='61mm leaf plug/sliding proposal changes closed intrusion and external sweep; actual track, emergency egress and frame reinforcement unclosed')]
    value=dict(schema=SCHEMA,candidate_id=cid,body_candidate_id=body_id,magnet_component_id=magnet['physical_id'],
        parent_revision=PARENT_REVISION,parent_composition_id=systems.PARENT_COMPOSITION_ID,
        physical_definition=physical,service_basis=deepcopy(brief['user_authorized_basis']),
        mass=dict(accounted_tare_kg_per_car=accounted,accounted_cap_loaded_kg_per_car=accounted+46*75.,
            accounted_160_control_kg_per_car=accounted+12000.,accounted_tare_kg_six_cars=6*accounted,
            installed_tare_kg_per_car=None,installed_loaded_kg_per_car=None,
            inherited_unlocated_account_kg=5578.253763406856,remaining_noninterior_allocation_kg=5578.253763406856-800.,
            interior_account_retained_kg=800.,counted_seat_stock_kg=seat_mass,unlocated_interior_remainder_kg=800.-seat_mass,
            parent_tare_kg=systems.PARENT_TARE_KG,net_accounted_change_kg=accounted-systems.PARENT_TARE_KG,
            component_replacements=[dict(domain='floor',removed_kg=700.5275,added_kg=floor['counted_mass_kg']),
                dict(domain='roof',removed_kg=518.075,added_kg=selected_roof['counted_mass_kg']),
                dict(domain='doors-glazing-infill',removed_kg=711.66944,added_kg=2*door['counted_mass_kg']+82+431.6248+67.62)],
            replacement_residual_kg=accounted-expected,CG_m=None,inertia_kg_m2=None),
        inventory=rows,missing_inventory=unknown,seating_layout=cabin,geometry_parts=geometry,located_material_properties=located,
        source_parent_removed_occurrences=removed,
        components=dict(floor=floor,roof_revision=roof,door=door,glazing=window,paired_seat=pair,single_seat=single),
        interfaces=dict(coordinate_frame='x longitudinal,y left,z up; retained floor topz0; metres',
            magnetic_mounts=mounts,door_openings=door_envelopes,HVAC_packages=packages,
            floor_surface_nominal_z_m=0.,roof_bottom_skin_z_m=2.7573,roof_top_z_m=top,
            car_body_length_m=17.,car_body_width_m=2.65,retained_arm_width_m=2.96,
            roof_component_global_fit='analytic-material-datum-pass; tolerance/joint/dynamic qualification unknown',
            floor_perimeter_lap_step_m=.0015,floor_flush_wear_surface_qualified=False,
            one_side_platform_compatibility_qualified=False),
        assembly_plan=[dict(sequence=i+1,operation=name,release_evidence=proof) for i,(name,proof) in enumerate([
            ('Build retained lower/roof extrusion fixture and magnetic hardpoints','Material certificates, datum survey, joint/structural review'),
            ('Fit new floor panels, edge/insert details and flush wear finish','Panel inspection, point loads and wheelchair floor transitions'),
            ('Install opaque infill,61mm doors and actual1300-to1400mm mechanism adaptation','Opening/track clearance, seals, interlocks, evacuation and measured mass'),
            ('Install20 pair benches and4 single-seat derivatives','Anchor/backrest/crash/fire qualification; actual assembly access'),
            ('Fit45mm-core roof panels on retained ribs with counted bearings','Skin/core/bond inspection, structural modes and global load tests'),
            ('Install glazing and fiveHVAC reference packages with ducts/services','Actual50C thermal/electrical performance and known mounting/clearance'),
            ('Install24 restrained magnetic cassettes and retained propulsion band','Native mounting fit, polarity/retention, converged force/current maps'),
            ('Install and weigh all remaining services, protection, couplers and capture','Close unknowninventory, CG/inertia, faults and prototype evidence')])],
        coverage=[dict(system=s,known_occurrences=sum(p['system']==s for p in rows),
            accounted_mass_kg=math.fsum(p['mass_kg'] for p in rows if p['system']==s),
            complete_installed_inventory=False) for s in equipped.SYSTEMS],
        readiness=dict(material_accounting='reconciled',necessary_panel_seat_door_fixtures='pass-with-declared-research-limits',
            native_equipped_model='proposed-defined-material-geometry-only',complete_installed_mass='unknown',
            complete_CG_and_inertia='unknown',structure='unknown',suspension='unknown',physical_acceptance='hold'),
        source_sha256=sources,source_component_ids=dict(layout=cabin['layout_id'],floor=floor['physical_definition_id'],roof=selected_roof['physical_definition_id'],
            door=door['component_id'],glazing=window['physical_definition_id'],pair_seat=pair['component_id'],single_seat=single['component_id']),
        scope='Matched research proposal with disjoint stock accounts and explicit proposed material placements. Whole equipped mass, joined-body modes, global contact/clearance and physical operation remain unqualified.',**FLAGS)
    value['evaluation_id']=identity(value)
    return value


def validate(value,root=ROOT):
    if value!=build(root):raise ValueError('vehicle physical definition, source, mass or scope differs from deterministic rebuild')
    return True
