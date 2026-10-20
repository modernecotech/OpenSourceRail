"""Provisional manufactured carbody shell on the six-car planning architecture.

A whole repeated car module, with real voids and traceable manufacturing units,
replaces the isolated dummy-loaded floor exhibit for packaging studies. This is
not an adopted low-floor layout or a verified vehicle structure. Connection
capacity, supplier doors, bogies, crash/fatigue and physical acceptance stay open.
"""
from copy import deepcopy
import ast
import math

from engineering.twin_workflow import core
from engineering.design_consistency import contracts as geometry
from engineering.continuous_design import beam_confirmation
from . import baseline, contracts as configuration, installed_equipment

IDENTITY = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
# Local member x becomes global y or z, with right-handed section rotations.
ALONG_Y = [[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]]
ALONG_Z = [[0., 0., 1.], [0., 1., 0.], [-1., 0., 0.]]
STOCK = (
    dict(frame_wall_m=.004, floor_m=.006, portal_profile='slender'),
    dict(frame_wall_m=.005, floor_m=.008, portal_profile='slender'),
    dict(frame_wall_m=.006, floor_m=.010, portal_profile='slender'),
    dict(frame_wall_m=.006, floor_m=.010, portal_profile='strengthened-medium'),
    dict(frame_wall_m=.008, floor_m=.010, portal_profile='strengthened-heavy'),
    dict(frame_wall_m=.010, floor_m=.012, portal_profile='strengthened-deep'),
)
PROFILES={
    'slender':dict(post_x=.06,post_y=.08,sill_w=.12,sill_h=.24,roof_h=.12,door_header_h=.08,window_h=.06),
    'strengthened-medium':dict(post_x=.16,post_y=.12,sill_w=.18,sill_h=.30,roof_h=.18,door_header_h=.24,window_h=.10),
    'strengthened-heavy':dict(post_x=.22,post_y=.16,sill_w=.20,sill_h=.36,roof_h=.20,door_header_h=.24,window_h=.12),
    'strengthened-deep':dict(post_x=.28,post_y=.20,sill_w=.24,sill_h=.40,roof_h=.20,door_header_h=.24,window_h=.14),
}

HOLDS = [
    'Adopt the six-car transverse profile, floor/door/platform map, accessible circulation and emergency egress',
    'Reconcile complete tare/passenger/battery/equipment/axle/CG maps; these shell masses are gross represented quantities only',
    'Bogie bolster, suspension, coupler, jacking/lifting, crash, global torsion, shell buckling, modal and railway fatigue load cases',
    'Issued weld geometries, throat/lengths, procedures, distortion sequence, inspection and qualified local connection resistance',
    'Panel fasteners, clips, seals, insulation, drainage, galvanic isolation and full installed fire/temperature/acoustic/weather qualification',
    'Supplier-configured doors, actual opening/closing tracks, obstruction detection, locks, seals and emergency release',
    'Window safety glazing build-up, retention/bond frame and impact qualification; represented glass uses a provisional density',
    'Floor local wheel/foot loads and stiffening, equipment anchors, interiors, services, floor transitions and vehicle-to-platform tolerances',
    'Bogie/door/gangway/cowl swept clearances, complete service access and installed cassette/HVAC interference resolution',
    'Frame section corner radii, cut/bend tooling, tolerances, welding shrinkage and independent prototype/production acceptance',
]


def _envelope():
    """Read existing historical transverse values without importing CAD engines."""
    path = core.ROOT/'design/component-catalogue/src/osr_mech/rolling_stock/baseline.py'
    names = {'PROMOTED_LIGHT_METRO_CAR_WIDTH_MM', 'PROMOTED_LIGHT_METRO_CAR_HEIGHT_MM'}
    values = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    values[target.id] = float(ast.literal_eval(node.value))/1000
    if set(values) != names:
        raise ValueError('historical car transverse reference missing')
    return values['PROMOTED_LIGHT_METRO_CAR_WIDTH_MM'], values['PROMOTED_LIGHT_METRO_CAR_HEIGHT_MM'], path


def candidates(policy):
    """Six complete shells with the same function, openings and load inputs."""
    if policy['architecture'] != 'baghdad-six-car':
        raise ValueError('six-car planning architecture required')
    yield from deepcopy(STOCK)


def _validate(policy, variables):
    if policy['architecture'] != 'baghdad-six-car' or variables not in STOCK:
        raise ValueError('registered carbody stock alternative required')
    if any(type(v) is not float or not math.isfinite(v) for k,v in variables.items() if k!='portal_profile'):
        raise ValueError('finite controlled stock dimensions required')
    facts = baseline.facts(policy)
    prototype = configuration.prototype_configuration()
    if not math.isclose(facts['train.car_length'], prototype['values']['car_length']['value'], rel_tol=0, abs_tol=1e-12):
        raise ValueError('prototype and policy car length differ')
    return prototype


def _subtract(rectangles, hole):
    """Disjoint rectangular material cells after one rectangular cutting void."""
    result = []
    hx0, hx1, hz0, hz1 = hole
    for x0, x1, z0, z1 in rectangles:
        a, b, c, d = max(x0, hx0), min(x1, hx1), max(z0, hz0), min(z1, hz1)
        if a >= b or c >= d:
            result.append((x0, x1, z0, z1)); continue
        for item in ((x0,a,z0,z1), (b,x1,z0,z1), (a,b,z0,c), (a,b,d,z1)):
            if item[1]-item[0] > 1e-10 and item[3]-item[2] > 1e-10:
                result.append(item)
    return result


def _connected(rectangles):
    """Separate disconnected sheet remnants into independent physical parts."""
    pending = list(rectangles); groups = []
    def touching(a,b):
        x_overlap = min(a[1],b[1])-max(a[0],b[0])
        z_overlap = min(a[3],b[3])-max(a[2],b[2])
        return (x_overlap > 1e-9 and z_overlap >= -1e-10) or (z_overlap > 1e-9 and x_overlap >= -1e-10)
    while pending:
        group = [pending.pop(0)]; changed = True
        while changed:
            changed = False
            for rect in list(pending):
                if any(touching(rect,item) for item in group):
                    group.append(rect); pending.remove(rect); changed = True
        groups.append(group)
    return groups


def bounds(part):
    """Exact axis-aligned bounds for the box-only owned carbody contract."""
    import numpy as np
    rotation = np.asarray(part['placement']['rotation']); translation = np.asarray(part['placement']['translation_m'])
    points=[]
    for primitive in part['manufacturing']['primitives']:
        if primitive['kind'] != 'box': raise ValueError('carbody bounds require controlled box primitives')
        centre=np.asarray(primitive['centre_m']); extent=np.asarray(primitive['dimensions_m'])/2
        for x in (-1,1):
            for y in (-1,1):
                for z in (-1,1): points.append(rotation@(centre+extent*[x,y,z])+translation)
    points=np.asarray(points)
    return [points.min(axis=0).tolist(),points.max(axis=0).tolist()]


def build(policy, variables=None):
    variables=deepcopy(STOCK[0] if variables is None else variables)
    prototype=_validate(policy,variables); facts=baseline.facts(policy)
    width,height,transverse_source=_envelope()
    length=facts['train.car_length']; half=length/2; wall=variables['frame_wall_m']; floor=variables['floor_m']
    # New explicit packaging hypothesis, not the old LM3 350/760 mm floor.
    floor_z=1.0; sill_top=floor_z-floor; roof_inner=height-.003
    profile=PROFILES[variables['portal_profile']];post_x=profile['post_x'];post_y=profile['post_y'];sill_w=profile['sill_w'];sill_h=profile['sill_h'];roof_h=profile['roof_h']
    side_y=width/2-.002-post_y/2; rail_y=width/2-.002-sill_w/2
    frame_end=half-.002-post_x/2; sill_length=length-.004
    materials=dict(
        steel=dict(density_kg_m3=facts['steel.density'],young_pa=facts['steel.elastic_modulus'],poisson=.3,
            basis='Repository nominal steel reference; exact heat/grade/temperature/weld properties require adoption'),
        aluminium=dict(density_kg_m3=2700.,young_pa=69e9,poisson=.33,
            basis='Nominal study aluminium; exact alloy/temper and forming/joint allowables unissued'),
        glass=dict(density_kg_m3=2500.,basis='Provisional homogeneous glazing density; laminated build-up/retention not selected'))
    parts=[]; joints=[]; groups={}
    def add(identity,material,primitives,group,process,section=None,placement=None):
        p=geometry.part(identity,material,dict(role=identity,primitives=primitives),materials,section=section,placement=placement,
            limits=dict(tolerance_m=None,tolerance_status='unissued',minimum_wall_m=None),
            inspections=['material and process identity','cut/formed dimensions and datums','joint fit and accessibility','damage/corrosion protection'])
        p.update(geometric_role='owned-manufactured-solid',procurement=None,process_route=process,
            manufacturing_unit_id=identity,datum_scheme={'A':'rail z=0; provisional floor z=1.0m','B':'body centre plane y=0','C':'car centre x=0'})
        parts.append(p);groups[identity]=group;return p
    def box(identity,material,dimensions,centre,group,process='Cut/drill/deburr; issued manufacturing tolerances and process qualification open'):
        return add(identity,material,[geometry.box(identity,*dimensions,centre)],group,process)
    def member(identity,member_length,w,h,centre,group,rotation=IDENTITY):
        p=geometry.member(identity,member_length,w,h,wall,'steel',materials,
            placement={'translation_m':list(centre),'rotation':rotation},inspections=['section/wall and cut dimensions','end contact and weld access'])
        p.update(geometric_role='owned-manufactured-solid',procurement=None,
            process_route='Cut sharp-corner RHS reference; actual stock radii/end preparations and weld sequence to qualify',
            manufacturing_unit_id=identity,datum_scheme={'A':'rail z=0','B':'car centre y=0','C':'car centre x=0'})
        parts.append(p);groups[identity]=group;return p
    def joint(identity,endpoints,mechanism,stage):
        if len(endpoints)<2:raise ValueError('joint requires at least two physical parts')
        joints.append(dict(id=identity,endpoints=endpoints,mechanism=mechanism,fastener_ids=[],
            tolerance_m=None,load_case_ids=['represented-shell-gravity','planning-tare-plus-crush-sensitivity'],
            inspection=['fit and datum','connection identity','qualified connection inspection remains open'],
            capacity_evidence=None,qualified=False,assembly_stage=stage))
    def longitudinal(identity,w,h,y,z,group):
        # Two stock lengths below12.2m, not an unavailable one-piece18.5m RHS.
        ids=[]
        for i in range(2):
            name=identity+'-'+str(i);ids.append(name)
            member(name,sill_length/2,w,h,((2*i-1)*sill_length/4,y,z),group)
        joint(identity+'-butt-splice',ids,
            'Direct butt contact between stock sections; complete-penetration weld prep/backing/access, distortion, NDT and fatigue design unissued',group)
        return ids
    def rail_at(ids,x):return ids[0 if x<0 else 1]
    sill_ids={}
    for sign in (-1,1):
        sill_ids[sign]=longitudinal('sill-'+str(sign),sill_w,sill_h,sign*rail_y,sill_top-sill_h/2,'underframe')
    # Floor modules end on crossmember centre lines; bogie bolsters retain the
    # exact reference 2.1 m inset used by the six-car family definition.
    from osr_mech.family_definition import family_definition
    family=family_definition('metro-6car')
    first=family['cars'][0]; bogie_x=[b['pivot_x_m']-first['centre_x_m'] for b in family['bogies'] if b['parent']==first['id']]
    end_cross=min(frame_end,half-.002-.04)
    stations=sorted(set([-end_cross,end_cross,*[length*(i/10-.5) for i in range(1,10)],*bogie_x]))
    for i,x in enumerate(stations):
        is_bolster=any(abs(x-v)<1e-9 for v in bogie_x)
        member('cross-'+str(i).zfill(2),2*(rail_y-sill_w/2),.12 if is_bolster else .08,sill_h if is_bolster else .16,
            (x,0,sill_top-(sill_h/2 if is_bolster else .08)),'underframe',ALONG_Y)
        for sign in (-1,1):joint(f'cross-{i:02d}-sill-{sign}',[f'cross-{i:02d}',rail_at(sill_ids[sign],x)],
            'Touching square-cut RHS end; weld geometry, throat/access, distortion and fatigue qualification required','underframe')
    # Assembly floor modules are deliberately real repeated physical units,
    # unlike the earlier bay exhibit (its test mass/feet are not tiled here).
    floor_end=min(end_cross-.04,frame_end-post_x/2)
    floor_boundaries=[-floor_end,*[length*(i/10-.5) for i in range(1,10)],floor_end]
    for i,(left,right) in enumerate(zip(floor_boundaries,floor_boundaries[1:])):
        identity=f'floor-{i:02d}'; gap=.001
        box(identity,'aluminium',(right-left-gap,2*(rail_y-sill_w/2),floor),((left+right)/2,0,floor_z-floor/2),'floor')
        supports=[f'cross-{min(range(len(stations)),key=lambda j:abs(stations[j]-v)):02d}' for v in (left,right)]
        joint(identity+'-supports',[identity,*dict.fromkeys(supports)],
            'Seated floor sheet on crossmember top; isolated clips/fasteners, sealing, local foot/wheel loads and galvanic barriers unissued','floor')
    door_centres=[-4.4,4.4]; door_width=1.4; door_top=floor_z+2.0
    windows=[(-7.1,2.2),(0.,1.8),(7.1,2.2)]; window_bottom=1.65;window_top=2.55
    jambs=[-frame_end,frame_end,-2.2,2.2]
    jambs += [x+sign*(door_width/2+post_x/2) for x in door_centres for sign in (-1,1)]
    jambs += [x+sign*(w/2+post_x/2) for x,w in windows for sign in (-1,1)]
    jambs=sorted(set(jambs)); side_post_top=roof_inner-roof_h
    openings=[];roof_ids={}
    for sign in (-1,1):
        side='left' if sign==1 else 'right'
        for j,x in enumerate(jambs):
            identity=f'{side}-post-{j:02d}'
            member(identity,side_post_top-sill_top,post_y,post_x,(x,sign*side_y,(side_post_top+sill_top)/2),'side-frame',ALONG_Z)
            joint(identity+'-sill',[identity,rail_at(sill_ids[sign],x)],'RHS post end directly seats on steel sill; end/weld capacity and continuity unqualified','side-frame')
        roof_id='roof-rail-'+side
        roof_ids[sign]=longitudinal(roof_id,post_y,roof_h,sign*side_y,roof_inner-roof_h/2,'roof-frame')
        for j in range(len(jambs)):joint(roof_id+f'-post-{j:02d}',[rail_at(roof_ids[sign],jambs[j]),f'{side}-post-{j:02d}'],
            'Direct touching post/roof-rail ends; weld detail and transfer stiffness require qualification','roof-frame')
        for i,x in enumerate(door_centres):
            opening=dict(id=f'{side}-door-{i}',type='door',side_sign=sign,x_bounds_m=[x-door_width/2,x+door_width/2],
                z_bounds_m=[floor_z,door_top],clear_width_m=door_width,clear_height_m=2.,adopted=False,
                supplier_configuration=None,platform_match=None,door_track_and_emergency_release=None)
            openings.append(opening)
            header=f'{side}-door-header-{i}'
            member(header,door_width,post_y,profile['door_header_h'],(x,sign*side_y,door_top+profile['door_header_h']/2),'side-frame')
            nearest=[f'{side}-post-{jambs.index(x+s*(door_width/2+post_x/2)):02d}' for s in (-1,1)]
            joint(header+'-jambs',[header,*nearest],'Touching door lintel ends; local frame/door distortion and weld stiffness remain unqualified','side-frame')
        for i,(x,w) in enumerate(windows):
            openings.append(dict(id=f'{side}-window-{i}',type='window',side_sign=sign,x_bounds_m=[x-w/2,x+w/2],
                z_bounds_m=[window_bottom,window_top],clear_width_m=w,clear_height_m=window_top-window_bottom,adopted=False))
            for level,name in ((window_bottom-profile['window_h']/2,'sill'),(window_top+profile['window_h']/2,'header')):
                identity=f'{side}-window-{name}-{i}'
                member(identity,w,post_y,profile['window_h'],(x,sign*side_y,level),'side-frame')
                nearest=[f'{side}-post-{jambs.index(x+s*(w/2+post_x/2)):02d}' for s in (-1,1)]
                joint(identity+'-jambs',[identity,*nearest],'Touching window frame; glazing retention/bond/thermal and weld details unqualified','side-frame')
            glass=f'{side}-window-glass-{i}'
            box(glass,'glass',(w-.012,.012,window_top-window_bottom-.012),(x,sign*(width/2-.012), (window_top+window_bottom)/2),'glazing',
                'Supplier laminated safety glazing and retention system required; homogeneous study glass shape only')
            joint(glass+'-retention',[glass,f'{side}-window-sill-{i}',f'{side}-window-header-{i}'],
                'Proposed captured/bonded glazing with 6mm perimeter clearance; gasket, bond, setting blocks and mechanical fail-safe retention absent','glazing')
        # Exterior sheets: <=1.85m along car, with cutting rectangles physically
        # removing door/window material. Disconnected remnants become new units.
        relevant=[o for o in openings if o['side_sign']==sign]
        for module in range(10):
            left=-half+.002+module*sill_length/10;right=left+sill_length/10
            rectangles=[(left,right,sill_top-sill_h,roof_inner)]
            for opening in relevant:
                rectangles=_subtract(rectangles,(*opening['x_bounds_m'],*opening['z_bounds_m']))
            for sub,rects in enumerate(_connected(rectangles)):
                identity=f'{side}-skin-{module:02d}-{sub}'
                primitives=[geometry.box(f'cell-{k}',b-a,.002,d-c,[(a+b)/2,sign*(width/2-.001),(c+d)/2]) for k,(a,b,c,d) in enumerate(rects)]
                add(identity,'aluminium',primitives,'side-skin','Laser/waterjet cut connected 2mm sheet; window/door voids retained; edge hems, clips, seals and finishes unissued')
                nearby=[f'{side}-post-{j:02d}' for j,x in enumerate(jambs) if left-.04<=x<=right+.04]
                joint(identity+'-retention',[identity,rail_at(roof_ids[sign],(left+right)/2),*nearby],
                    'Removable nonstructural cladding; actual holes, clips/fasteners, dielectric layers and seal compression must be designed','cladding')
        # Floor edge strips fill the zone above side sills without material
        # passing through post feet. The steel post has a direct steel seat.
        edge_cuts=[-half+.002,*[edge for x in jambs for edge in (x-post_x/2,x+post_x/2)],half-.002]
        for i,(left,right) in enumerate(zip(sorted(set(edge_cuts)),sorted(set(edge_cuts))[1:])):
            if any(left+1e-9<x<right-1e-9 for x in jambs) or right-left<1e-8:continue
            identity=f'{side}-floor-edge-{i:02d}'
            box(identity,'aluminium',(right-left,sill_w,floor),((left+right)/2,sign*rail_y,floor_z-floor/2),'floor')
            joint(identity+'-seat',[identity,*sill_ids[sign]],'Seated sheet strip between primary post feet; isolated fixing and weather sealing unissued','floor')
        # Two independent sliding leaves per door. Frame and glass are separate
        # physical materials; the hollow window is not an opaque solid block.
        for i,x in enumerate(door_centres):
            for leaf in (0,1):
                centre=x+(2*leaf-1)*door_width/4;leaf_w=door_width/2-.008;bottom=floor_z+.008;top=door_top-.008
                z0,z1=1.7,2.65;innerw=leaf_w-.10;y=sign*(width/2-.025)
                pieces=[geometry.box('left-rail',.05,.03,top-bottom,[centre-(leaf_w-.05)/2,y,(bottom+top)/2]),
                    geometry.box('right-rail',.05,.03,top-bottom,[centre+(leaf_w-.05)/2,y,(bottom+top)/2]),
                    geometry.box('lower-panel',innerw,.03,z0-bottom,[centre,y,(bottom+z0)/2]),
                    geometry.box('upper-panel',innerw,.03,top-z1,[centre,y,(z1+top)/2])]
                identity=f'{side}-door-{i}-leaf-{leaf}'
                add(identity,'aluminium',pieces,'door-leaves','Provisional hollow leaf/frame coordination solid; internal extrusion cavities, hardware, seals and qualified operator absent')
                glass=identity+'-glass'
                box(glass,'glass',(innerw-.008,.012,z1-z0-.008),(centre,y,(z0+z1)/2),'door-leaves')
                joint(identity+'-glass-retention',[identity,glass],'4mm glazing fit clearance; supplier gasket and mechanical retention qualification required','doors')
                joint(identity+'-operator',[identity,f'{side}-door-header-{i}'],'Declared hanging/sliding leaf; track, bearings, lock and actual sweeps unimplemented','doors')
    # Roof bows align to actual side frame posts; end beams and end posts frame
    # a genuine gangway opening rather than an end wall passing through it.
    for i,x in enumerate(jambs):
        identity=f'roof-bow-{i:02d}'
        member(identity,2*(side_y-post_y/2),post_x,roof_h,(x,0,roof_inner-roof_h/2),'roof-frame',ALONG_Y)
        joint(identity+'-rails',[identity,rail_at(roof_ids[1],x),rail_at(roof_ids[-1],x)],'Touching transverse roof bow; weld and global lateral/torsional transfer not qualified','roof-frame')
    for i in range(10):
        left=-half+.002+i*sill_length/10;right=left+sill_length/10
        identity=f'roof-sheet-{i:02d}'
        box(identity,'aluminium',(right-left-.001,width-.004,.003),((left+right)/2,0,height-.0015),'roof-skin',
            'Flat segmented sheet study roof; drainage slopes, formed corners, weld/bond/seal and equipment penetrations unissued')
        joint(identity+'-retention',[identity,rail_at(roof_ids[1],(left+right)/2),rail_at(roof_ids[-1],(left+right)/2)],'Proposed removable weather roof; complete clip/seal/thermal break and suction design required','cladding')
    for sign in (-1,1):
        side='front' if sign==1 else 'rear';x=sign*frame_end
        for s in (-1,1):
            identity=f'{side}-gangway-post-{s}'
            member(identity,side_post_top-sill_top,.06,post_x,(x,s*.58,(sill_top+side_post_top)/2),'end-frame',ALONG_Z)
            # Local end crossmember sits directly below the post.
            cross=f'cross-{len(stations)-1:02d}' if sign==1 else 'cross-00'
            joint(identity+'-underframe',[identity,cross],'End-post foot seats on end crossmember; qualified gangway/crash/coupling interface absent','end-frame')
            joint(identity+'-roof',[identity,f'roof-bow-{jambs.index(sign*frame_end):02d}'],'End-post top contacts roof-bow underside; centroid offset and weld capacity remain unqualified','roof-frame')
        identity=side+'-gangway-header'
        member(identity,1.1,post_x,.08,(x,0,3.09),'end-frame',ALONG_Y)
        joint(identity+'-posts',[identity,f'{side}-gangway-post--1',f'{side}-gangway-post-1'],'Gangway top frame; seal/kinematic interface to next car unselected','end-frame')
        rectangles=_subtract([(-width/2+.002,width/2-.002,sill_top-sill_h,roof_inner)],(-.55,.55,floor_z,3.05))
        for j,rects in enumerate(_connected(rectangles)):
            name=f'{side}-end-skin-{j}'
            primitives=[geometry.box(f'cell-{k}',.002,b-a,d-c,[sign*(half-.001),(a+b)/2,(c+d)/2]) for k,(a,b,c,d) in enumerate(rects)]
            add(name,'aluminium',primitives,'end-skin','Cut bulkhead skin with gangway opening; pressure/fire/seal/attachment qualification open')
            joint(name+'-frame',[name,identity,f'{side}-gangway-post--1',f'{side}-gangway-post-1'],
                'Nonstructural end sheet to framed opening; attachment hardware and fire/weather seals unissued','cladding')
        threshold=side+'-gangway-threshold'
        threshold_length=half-.002-floor_end
        box(threshold,'aluminium',(threshold_length,1.1,floor),(sign*(half-.002-threshold_length/2),0,floor_z-floor/2),'floor')
        joint(threshold+'-seat',[threshold,'cross-00' if sign==-1 else f'cross-{len(stations)-1:02d}'],
            'Gangway approach floor; intercar bridge, movement/seal, trip protection and supplier support remain open','floor')
    # Stage plans are physical group inventories with prerequisites, not a
    # fabricated animation/proof of a viable weld/erection process.
    stage_groups=[('underframe',['underframe'],[]),('side-frame',['side-frame'],['underframe']),
        ('end-frame',['end-frame'],['underframe']),('roof-frame',['roof-frame'],['side-frame','end-frame']),
        ('floor',['floor'],['underframe','side-frame','end-frame']),('cladding',['side-skin','roof-skin','end-skin'],['roof-frame','floor']),
        ('glazing',['glazing'],['cladding']),('doors',['door-leaves'],['side-frame','floor'])]
    stages=[dict(id=name,parts=[p['id'] for p in parts if groups[p['id']] in values],requires=requires,
        supports=['external carbody assembly fixture; reactions and release sequence unqualified'],
        loads=[dict(id='represented-self-weight',gravity_m_s2=9.80665)],
        mandatory_hold='Qualified temporary support, lifting, joining and dimensional acceptance before advancing') for name,values,requires in stage_groups]
    source_map={str(transverse_source.relative_to(core.ROOT)):core.sha(transverse_source),
        str(baseline.DATA.relative_to(core.ROOT)):core.sha(baseline.DATA),**family['source_sha256']}
    definition=dict(schema='osr-engineering-representations/1',name='carbody-assembly',parts=parts,materials=materials,
        assembly_joints=joints,construction_stages=stages,mandatory_evidence=HOLDS,
        physical_validation=False,production_released=False)
    metadata=dict(architecture=policy['architecture'],prototype_revision=prototype['revision'],source_sha256=source_map,
        dimensions_m=dict(length=length,width=width,height=height,floor_above_rail=floor_z),
        transverse_basis='Historical LM3 transverse envelope read as an UNADOPTED six-car packaging hypothesis; no floor layout transferred',
        floor_basis='New constant 1.0m floor study assumption; not an adopted accessible/low-floor/platform solution',
        car_count=prototype['values']['car_count']['value'],represented_car_id='repeated-car-module; cab/cowl/intercar differences unrepresented',
        bogie_reference_positions_m=bogie_x,bogie_configuration=None,part_groups=groups,openings=openings,
        module_limit_m=dict(side_sheet_longitudinal=sill_length/10,roof_sheet_longitudinal=sill_length/10,primary_rail_stock=sill_length/2),
        manufactured_frame_wall_m=wall,portal_profile=deepcopy(profile),floor_thickness_m=floor,assembly_stage_ids=[s['id'] for s in stages],
        primary_sill_ids=[name for ids in sill_ids.values() for name in ids],complete_carbody_accepted=False,
        assembly_sequence=[dict(id=s['id'],title=s['id'].replace('-',' ').title(),part_ids=s['parts'],requires=s['requires']) for s in stages],
        missing_physical_units=['weld metal','panel and floor attachment hardware','insulation and liners','seals and glazing retention',
            'selected door operators/locks','bogie interface hardware','coupling/gangway bridge','interiors and complete service equipment'],
        no_removal_credit=True,complete_installed_vehicle_mass_kg=None)
    revision=core.digest(dict(variables=variables,contract=definition,metadata=metadata))
    definition['revision']=revision
    for p in parts:
        p['revision']=revision;p['joints']=[j['id'] for j in joints if p['id'] in j['endpoints']]
    geometry.validate(definition)
    return dict(schema='osr-assembly-design-candidate/1',kind='carbody-assembly',variables=variables,revision=revision,
        requirement_ids=['baghdad:ME-01'],contract=definition,metadata=metadata,
        assembly_steps=[s['id']+': fixture, join, inspect and obtain independent stage acceptance; proposed sequence only' for s in stages],
        qa_plan=[dict(unit_id=p['id'],unit_revision=revision,serial=None,required=p['inspection_characteristics'],records=[],accepted=False) for p in parts],
        source_scope='One complete repeated primary frame and segmented skin/opening/leaf geometry study; incomplete installed/qualified six-car vehicle',
        open_requirements=HOLDS,**core.FLAGS)


def stage_plan(candidate):
    """Public source for native assembly sequence media/UI (not motion proof)."""
    return deepcopy(candidate['contract']['construction_stages'])


def _intersection(a,b):
    extents=[min(a[1][i],b[1][i])-max(a[0][i],b[0][i]) for i in range(3)]
    return max(0.,extents[0])*max(0.,extents[1])*max(0.,extents[2])


def opening_interferences(candidate):
    """Actual geometry intruding in clear door/window apertures; infills excluded."""
    results=[];width=candidate['metadata']['dimensions_m']['width'];groups=candidate['metadata']['part_groups']
    for opening in candidate['metadata']['openings']:
        x0,x1=opening['x_bounds_m'];z0,z1=opening['z_bounds_m'];sign=opening['side_sign']
        aperture=[[x0,sign*(width/2-.15),z0],[x1,sign*(width/2+.05),z1]]
        aperture[0][1],aperture[1][1]=sorted([aperture[0][1],aperture[1][1]])
        for p in candidate['contract']['parts']:
            if groups[p['id']] in {'glazing','door-leaves'}:continue
            # Individual material cells, not a holed sheet's outer bounding box.
            for primitive in p['manufacturing']['primitives']:
                shadow=deepcopy(p);shadow['manufacturing']['primitives']=[primitive]
                volume=_intersection(bounds(shadow),aperture)
                if volume>1e-12:results.append(dict(opening_id=opening['id'],part_id=p['id'],intersection_m3=volume))
    return results


def equipment_conflicts(candidate, equipment=None):
    """Packaging warnings against current shared service locations, never adoption.

    When provided, the exact installed-equipment revision binds instance
    identities and mounting datums. Supplier solids and maintenance envelopes
    are not reconstructed here and remain a hold.
    """
    layout=installed_equipment.layout();issues=[]
    if equipment is not None:
        if equipment['architecture'] != candidate['metadata']['architecture']:raise ValueError('equipment architecture mismatch')
        if equipment.get('revision')!=core.digest({k:v for k,v in equipment.items() if k!='revision'}) or equipment.get('layout_sha256')!=core.sha(installed_equipment.DATA):
            raise ValueError('stale equipment revision or layout')
        if not equipment.get('instances'):raise ValueError('equipment instances required')
        locations=[i for i in equipment['instances'] if i['body_id']==equipment['instances'][0]['body_id']]
    else:
        locations=[dict(id=f'cassette-{i+1:02d}',local_position_m=p,function='lv-ventilation-cassette') for i,p in enumerate(layout['cassette_local_positions_m'])]
    cassette_count=len(locations)
    if equipment is not None:
        locations += [i for i in equipment['purchased_boundaries'] if i['body_id']==equipment['instances'][0]['body_id']]
    else:
        locations += [dict(id=f'cooling-module-{i+1:02d}',local_position_m=p,function='refrigeration-boundary') for i,p in enumerate(layout['cooling_module_local_positions_m'])]
    width=candidate['metadata']['dimensions_m']['width'];floor=candidate['metadata']['dimensions_m']['floor_above_rail']
    for location in locations:
        x,y,z=location['local_position_m']
        for opening in candidate['metadata']['openings']:
            if opening['type']!='door':continue
            # A clear transverse passage prism joins both paired door openings.
            a,b=opening['x_bounds_m']
            if a<x<b and abs(y)<width/2 and floor<z<opening['z_bounds_m'][1]:
                issues.append(dict(instance_id=location['id'],opening_id=opening['id'],state='datum-in-declared-door-circulation-prism',
                    scope='Datum overlap only; full supplier service envelope, passenger circulation and adoption require resolution'))
    return dict(layout_sha256=core.sha(installed_equipment.DATA),cassette_count=cassette_count,cooling_boundary_count=len(locations)-cassette_count,issues=issues,
        complete_solid_interference_checked=False,provided_exact_equipment_revision=equipment.get('revision') if equipment else None,
        geometry_and_maintenance_envelope='hold',scope='Controlled service mount datums versus proposed door circulation; no positive installed fit claim')


def _beam_closed_form(length,supports,q,ei,xs):
    """Independent integrated Macaulay beam solution including both overhangs."""
    a,b=supports;total=q*length;rb=(total*(length/2-a))/(b-a);ra=total-rb
    def raw(x):return -q*x**4/24+ra*max(x-a,0)**3/6+rb*max(x-b,0)**3/6
    c1=(raw(a)-raw(b))/(b-a);c2=-raw(a)-c1*a
    return [(raw(x)+c1*x+c2)/ei for x in xs], [ra,rb]


def beam_diagnostic(candidate, *, load_scale=1.0, passenger_mass_kg=75., planning_crush_passengers=None, mass_basis="planning-tare-plus-crush"):
    """Sill-only elastic diagnostic with explicit unreconciled planning loads.

    Sidewall/roof sharing is NOT assumed; this does not verify the carbody or
    predict its real deflection. No invented displacement/resistance allowable.
    """
    for value in (load_scale,passenger_mass_kg):
        if type(value) not in (int,float) or not math.isfinite(value) or value<=0:raise ValueError('positive finite diagnostic input required')
    prototype=configuration.prototype_configuration()
    if planning_crush_passengers is None:
        planning_crush_passengers=prototype['values']['crush_passengers']['value']/prototype['values']['car_count']['value']
    if mass_basis not in {'planning-tare-plus-crush','represented-shell'}:raise ValueError('unknown diagnostic mass basis')
    if type(planning_crush_passengers) not in (int,float) or not math.isfinite(planning_crush_passengers) or planning_crush_passengers<0:
        raise ValueError('nonnegative finite planning occupancy required')
    summary=geometry.summary(candidate['contract']);sills=[p for p in candidate['contract']['parts'] if p['id'] in candidate['metadata']['primary_sill_ids']]
    length=max(bounds(p)[1][0] for p in sills)-min(bounds(p)[0][0] for p in sills)
    # Butt-joined serial lengths never count as parallel section stiffness.
    cross_sections={p['placement']['translation_m'][1]:p['analysis']['section'] for p in sills}
    young=candidate['contract']['materials']['steel']['young_pa'];ei=sum(section['iy_m4']*young for section in cross_sections.values())
    x0=-length/2;supports=[x-x0 for x in candidate['metadata']['bogie_reference_positions_m']]
    planning_tare=prototype['values']['tare_mass']['value']/prototype['values']['car_count']['value']
    mass=(planning_tare+planning_crush_passengers*passenger_mass_kg) if mass_basis=='planning-tare-plus-crush' else summary['mass_kg']
    q=mass*9.80665*load_scale/length
    solutions=[beam_confirmation.solve(length,supports,ei,uniform=q,divisions=n) for n in (16,32)]
    fine=solutions[-1];closed,reactions=_beam_closed_form(length,supports,q,ei,fine['nodes_m'])
    scale=max(max(abs(v) for v in closed),1e-12)
    agreement=max(abs(v-fine['displacement_rotation'][2*i]) for i,v in enumerate(closed))/scale
    # Physical y-section ordinate of each sill; sharing uses only the two RHS.
    section_inertia=sum(section['iy_m4'] for section in cross_sections.values())
    xs=[length*i/400 for i in range(401)]
    moment=lambda x:-q*x*x/2+sum(r*max(x-s,0) for r,s in zip(reactions,supports))
    peak=max(abs(moment(x)) for x in xs)
    return dict(scope='Sill-only linear elastic overhang sensitivity; planning tare plus synthetic passenger mass or represented shell self-weight; full sidewall/roof sharing and actual vehicle loads unresolved',
        assumptions=dict(passenger_mass_kg=passenger_mass_kg,planning_crush_passengers=planning_crush_passengers,
            mass_basis=mass_basis,planning_tare_reference_kg=planning_tare,represented_shell_mass_kg=summary['mass_kg'],
            actual_vehicle_tare_reconciled=False,prototype_revision=prototype['revision'],gravity_m_s2=9.80665,load_scale=load_scale),
        mass_kg=mass,uniform_load_n_m=q,ei_nm2=ei,supports_m=supports,solutions=solutions,
        closed_form_relative_error=agreement,independent_support_reactions_n=reactions,
        maximum_nodal_deflection_m=fine['maximum_nodal_deflection_m'],maximum_sampled_moment_nm=peak,
        maximum_sill_fibre_stress_pa=peak*next(iter(cross_sections.values()))['height_m']/2/section_inertia,
        adopted_stress_allowable_pa=None,adopted_deflection_limit_m=None,whole_carbody_qualified=False)


def evaluate(policy,candidate):
    _validate(policy,candidate['variables'])
    if core.digest(candidate)!=core.digest(build(policy,candidate['variables'])):raise ValueError('carbody differs from controlled generator')
    summary=geometry.summary(candidate['contract']);groups=candidate['metadata']['part_groups'];dims=candidate['metadata']['dimensions_m']
    conflicts=opening_interferences(candidate);parts=candidate['contract']['parts'];part_bounds={p['id']:bounds(p) for p in parts}
    inside=all(b[0][0]>=-dims['length']/2-1e-9 and b[1][0]<=dims['length']/2+1e-9 and
        b[0][1]>=-dims['width']/2-1e-9 and b[1][1]<=dims['width']/2+1e-9 and b[0][2]>=0 and b[1][2]<=dims['height']+1e-9 for b in part_bounds.values())
    stages=stage_plan(candidate);seen=set();stage_ok=True
    for stage in stages:
        stage_ok &= set(stage['requires'])<=seen;seen.add(stage['id'])
    all_members=[identity for stage in stages for identity in stage['parts']]
    staged_once=len(all_members)==len(set(all_members)) and set(all_members)=={p['id'] for p in parts}
    byid={p['id']:p for p in parts};joint_refs=all(set(j['endpoints'])<=set(byid) for j in candidate['contract']['assembly_joints'])
    diagnostic=beam_diagnostic(candidate);adverse=beam_diagnostic(candidate,load_scale=2.);self_weight=beam_diagnostic(candidate,mass_basis='represented-shell')
    checks=dict(physical_unit_identity_unique=len(byid)==len(parts),all_defined_parts_staged_once=staged_once,
        assembly_dependency_acyclic=stage_ok,connection_endpoints_exist=joint_refs,
        actual_door_window_voids_clear=not conflicts,owned_shell_within_provisional_outer_envelope=inside,
        expected_door_count=sum(o['type']=='door' for o in candidate['metadata']['openings'])==4,
        expected_window_count=sum(o['type']=='window' for o in candidate['metadata']['openings'])==6,
        independent_sill_beam_agreement=diagnostic['closed_form_relative_error']<1e-7,
        diagnostic_force_balance=diagnostic['solutions'][-1]['force_balance_relative_error']<1e-8,
        adverse_double_load_control=math.isclose(adverse['maximum_nodal_deflection_m'],2*diagnostic['maximum_nodal_deflection_m'],rel_tol=1e-10))
    checks.update({key:None for key in ('adopted-door-platform-and-floor-map','whole-carbody-stress-deflection-and-fatigue',
        'qualified-primary-joints','local-floor-wheel-loads','door-moving-and-fail-safe-tests','complete-panel-retention-and-weather-fire',
        'bogie-coupler-crash-and-lifting','installed-equipment-interference','physical-independent-acceptance')})
    from . import carbody_frame
    frame=carbody_frame.report(candidate)
    checks.update({'frame/'+name:value for name,value in frame['checks'].items()})
    failed=[name for name,value in checks.items() if value is False];held=[name for name,value in checks.items() if value is None]
    group_mass={group:sum(p['properties']['mass_kg'] for p in parts if groups[p['id']]==group) for group in sorted(set(groups.values()))}
    return dict(schema='osr-assembly-screening/1',kind=candidate['kind'],candidate_revision=candidate['revision'],checks=checks,
        failed_checks=failed,held_checks=held,state='failed' if failed else 'hold',implemented_checks_pass=not failed,screen_pass=False,
        measurements=dict(part_count=len(parts),joint_count=len(candidate['contract']['assembly_joints']),mass_kg=summary['mass_kg'],cg_m=summary['cg_m'],
            inertia_tensor_kg_m2=summary['inertia_tensor_kg_m2'],group_mass_kg=group_mass,
            represented_six_car_gross_mass_kg=summary['mass_kg']*candidate['metadata']['car_count'],
            complete_installed_vehicle_mass_kg=None,mass_scope='All represented shell solids only; no credit against planning tare and omitted units remain listed',
            dimensions_m=dims,opening_interferences=conflicts,equipment_packaging=equipment_conflicts(candidate),
            maximum_sheet_module_length_m=max(b[1][0]-b[0][0] for identity,b in part_bounds.items() if groups[identity] in {'side-skin','roof-skin','floor'}),
            sill_only_diagnostic=diagnostic,adverse_double_load_diagnostic=adverse,represented_shell_self_weight=self_weight),
        digital_specification_complete=False,connection_resistance_qualified=False,open_requirements=HOLDS,supplemental_evidence={'carbody-frame':frame},
        scope=candidate['source_scope']+'; geometry/identity/fit controls, retained sill-only diagnostics and connected actual-RHS3Dframe sensitivities; no whole-carbody acceptance',**core.FLAGS)
