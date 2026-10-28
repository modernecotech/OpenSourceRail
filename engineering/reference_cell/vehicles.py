"""Five equipped, located research assemblies; geometry is not qualification.

Dimensions and mass intervals below are explicit design hypotheses. Purchased
envelopes are not detailed internals, delivered weights or supplier drawings.
No current reference, retained source-bound packet or production order is edited.
"""
from copy import deepcopy
from math import pi
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity, digest
from engineering.component_registry import make_part, make_occurrence, make_registry, validate_registry, summary
from engineering.component_registry.materials import catalogue

PRODUCER = 'engineering/reference_cell/vehicles.py'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False, physical_journey_completed=False,
             selected_reference_changed=False)
FUNCTIONS = ('primary-body','bogie-interfaces','running-gear','doors','glazing',
             'seating','HVAC','solar-roof','auxiliary-power','LIM-interface',
             'control-safety','coupling-articulation')
FAMILIES = {
    'V1': ('GFRP semi-monocoque with metallic hardpoints', 'GFRP-EGLASS-HYPOTHESIS-1', .0032, .045, 'ring-and-sandwich', .85),
    'V2': ('GFRP sandwich monocoque with participating roof and floor', 'GFRP-EGLASS-HYPOTHESIS-1', .0040, .060, 'participating-sandwich', 1.05),
    'V3': ('Aluminium extrusion frame with modular GFRP cladding', 'AL-6082-T6-EXTRUSION', .0022, .035, 'extruded-frame', .85),
    'V4': ('Aluminium stressed-skin body', 'AL-6082-T651-SHEET', .0024, .030, 'stressed-skin', .70),
    'V5': ('Aluminium underframe and GFRP integrated cabin', 'GFRP-EGLASS-HYPOTHESIS-1', .0035, .050, 'hybrid-underframe', 1.00),
}
REQUIREMENTS = dict(cars=6, car_length_m=17., car_width_m=2.8,
    fixed_seats_per_car=44, wheelchair_places_per_car=2,
    passenger_door_sets_per_car=2, doors_on_one_side=True,
    passenger_normal_per_car=46, crowd_structural_control_people_per_car=160,
    people_mass_kg_hypothesis=75., powered_bogies=0, traction_batteries=0,
    independent_braking_required=True, service_battery_required=True,
    target_headway_s=120., speed_cap_m_s=20., axle_count_per_car=4,
    wheel_count_per_car=8, bogies_per_car=2)


def variants():
    return list(FAMILIES)


def pose(x=0., y=0., z=0., axis='z'):
    """Part origin is its centroid; cylinders are locally along z."""
    rotation = {'z': [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]],
                'x': [[0.,0.,1.],[0.,1.,0.],[-1.,0.,0.]],
                'y': [[1.,0.,0.],[0.,0.,1.],[0.,-1.,0.]]}[axis]
    return [rotation[i]+[float((x,y,z)[i])] for i in range(3)]+[[0.,0.,0.,1.]]


def _geometry(kind, dims):
    if kind in ('box','envelope'):
        volume = None if kind == 'envelope' else dims[0]*dims[1]*dims[2]
    elif kind == 'cylinder': volume = pi*dims['radius']**2*dims['length']
    else: volume = pi*(dims['outer_radius']**2-dims['inner_radius']**2)*dims['length']
    return dict(kind=kind, dimensions_m=dims, net_volume_m3=volume)


def _mass_properties(rows):
    """Conservative envelope bounds plus an exact uniform known-stock subset.

    Bounds are conditional on supplied mass/size intervals, not confidence
    intervals or weighed acceptance. Origin inertia is not inertia about CG.
    """
    low=high=nominal=0.;moment=[0.,0.,0.];qlo=[0.,0.,0.];qhi=[0.,0.,0.]
    ilo=[0.,0.,0.];ihi=[0.,0.,0.];known=[]
    for row in rows:
        part=row['part'];m=part['mass'];a=m['lower_bound_kg'];b=m['upper_bound_kg']
        low+=a;high+=b;g=part['geometry'];d=g['dimensions_m'];pos=row['xyz']
        if g['kind'] in ('box','envelope'):extent=list(d)
        else:
            radius=d.get('outer_radius',d.get('radius'));extent=[2*radius,2*radius,d['length']]
            if row['axis']=='x':extent=[extent[2],extent[1],extent[0]]
            elif row['axis']=='y':extent=[extent[0],extent[2],extent[1]]
        spatial=[(pos[i]-extent[i]/2,pos[i]+extent[i]/2) for i in range(3)]
        square=[]
        for i,(u,w) in enumerate(spatial):
            choices=[a*u,a*w,b*u,b*w];qlo[i]+=min(choices);qhi[i]+=max(choices)
            square.append((0. if u<=0<=w else min(u*u,w*w),max(u*u,w*w)))
        for i in range(3):
            axes=[j for j in range(3) if j!=i]
            ilo[i]+=a*sum(square[j][0] for j in axes)
            ihi[i]+=b*sum(square[j][1] for j in axes)
        mass=m['calculated_kg']
        if mass is not None:
            nominal+=mass
            for i in range(3):moment[i]+=mass*pos[i]
            known.append((row,mass,extent))
    cg=[x/nominal for x in moment];I=[[0.,0.,0.] for _ in range(3)]
    for row,mass,extent in known:
        g=row['part']['geometry'];d=g['dimensions_m'];delta=[row['xyz'][i]-cg[i] for i in range(3)]
        if g['kind']=='box':local=[mass*sum(d[j]**2 for j in range(3) if j!=i)/12 for i in range(3)]
        else:
            radii=d['radius']**2 if g['kind']=='cylinder' else d['outer_radius']**2+d['inner_radius']**2
            local=[mass*(3*radii+d['length']**2)/12]*2+[mass*radii/2]
            if row['axis']=='x':local=[local[2],local[1],local[0]]
            elif row['axis']=='y':local=[local[0],local[2],local[1]]
        for i in range(3):
            for j in range(3):
                I[i][j]+=(local[i]+mass*sum(delta[k]**2 for k in range(3) if k!=i)) if i==j else -mass*delta[i]*delta[j]
    return dict(calculated_net_stock_mass_kg=nominal,calculated_subset_CG_m=cg,
        calculated_subset_uniform_inertia_about_its_CG_kg_m2=I,mass_lower_bound_kg=low,mass_upper_bound_kg=high,
        all_item_CG_bounds_m=[[min(qlo[i]/low,qlo[i]/high,qhi[i]/low,qhi[i]/high),
                              max(qlo[i]/low,qlo[i]/high,qhi[i]/low,qhi[i]/high)] for i in range(3)],
        all_item_diagonal_inertia_about_registry_origin_bounds_kg_m2=[[ilo[i],ihi[i]] for i in range(3)],
        installed_CG_m=None,installed_inertia_about_CG_kg_m2=None,
        scope='Uniform nominal stock subset and conservative finite-envelope/mass bounds; purchased internals and authenticated installed properties remain unknown')


def evaluate(vehicle_id='V1', root=ROOT):
    if vehicle_id not in FAMILIES:
        raise ValueError('Explicit V1, V2, V3, V4 or V5 vehicle required')
    root=Path(root)
    if digest(root/PRODUCER)!=digest(__file__):
        raise ValueError('Executing vehicle generator differs from declared source root')
    title, shell_grade, skin, core, load_path, spacing = FAMILIES[vehicle_id]
    materials = {m['grade_id']:m for m in catalogue()['materials']}
    parts={}; local=[]; assembly_access=[]; joints=[]

    def add(name, function, dims, xyz, grade=shell_grade, *, kind='box', axis='z',
            bounds=None, process=None, parent=None, details=None):
        geometry=_geometry('envelope' if bounds else kind, dims)
        material=materials[grade]
        volume=geometry['net_volume_m3']; density=material['density_kg_m3']
        mass=(dict(calculated_kg=None,lower_bound_kg=bounds[0],upper_bound_kg=bounds[1],evidence_state='bounded-estimate')
              if bounds else dict(calculated_kg=volume*density['nominal'],
                  lower_bound_kg=volume*density['lower'],upper_bound_kg=volume*density['upper'],evidence_state='calculated'))
        process=process or ('purchased-assembly' if bounds else 'cut-form-machine-and-inspect')
        material_id=None if bounds else material['material_id']
        code='OSR-'+vehicle_id+'-'+name.upper().replace('/','-')+'-'+identity(dict(geometry=geometry,material_id=material_id))[:8]
        metadata=dict(process=process,method=process,
            blank_volume_m3=None if bounds else volume/.85,
            gross_to_net_yield_hypothesis=None if bounds else .85,
            cycle_hours=None,cycle_hours_bounds=None,
            tooling_id=None if bounds else vehicle_id+'-'+process,
            labour_estimate_evidence=None,manufacturing_qualified=False)
        mating=dict(interface_status='sized-hypothesis-needs-load-and-fitup-verification',
            attachment=deepcopy(details or {}),fasteners_are_separate_counted_parts=True,
            tolerance_m=None,approved_installation_sequence=None)
        part=make_part(code,'A',[function],geometry,material_id,mass,metadata,
            assembly=mating,
            electrical_thermal=dict(power_W=None,heat_W=None,cooling_verified=False,
                flexible_services_included_as_separate_parts=True),
            cost=dict(source_class='C',currency='USD',lower_usd=None,upper_usd=None,source_id=None,source_date=None,location=None,quantity_basis='one-part',confidence='unresolved',material_usd=None,fabrication_usd=None,assembly_usd=None,
                inspection_usd=None,transport_usd=None,installation_usd=None,supplier_quote_id=None),
            procurement=dict(supplier=None,country_of_origin=None,quote_id=None,MOQ=None,lead_days=None),
            evidence=dict(state='design-hypothesis',source=PRODUCER,physical_test_ids=[],
                supplier_configuration_id=None,material_composition_known=False if bounds else True,installed_geometry_qualified=False),
            lifecycle=dict(inspection_interval_hours=None,replacement_procedure=None,
                repairability_review='pending',recycling_route=None))
        if code in parts and parts[code] != part:
            raise ValueError('One part ID cannot define different dimensions/materials')
        parts[code]=part
        local.append(dict(name=name+'/'+str(len(local)),part=part,xyz=xyz,axis=axis,
            function=function,parent=parent or function))
        return part

    def box(name, f, dims, xyz, grade=shell_grade, **kw):
        return add(name,f,list(dims),xyz,grade,**kw)

    def purchased(name, f, dims, xyz, mass_bounds, grade='STEEL-S355-HYPOTHESIS', **kw):
        return box(name,f,dims,xyz,grade,bounds=mass_bounds,**kw)

    def bolt_group(prefix, f, xyz, count, pitch=.025):
        # Every shaft, head, nut and washer contributes separately to geometry,
        # mass and assembly; hole/counterbore/tolerance qualification stays open.
        for n in range(count):
            q=(xyz[0]+(n%4)*pitch,xyz[1]+(n//4)*pitch,xyz[2])
            add(prefix+'-shaft',f,dict(length=.050,radius=.004),q,'STEEL-FASTENER-HYPOTHESIS',kind='cylinder',process='formed-threaded-fastener')
            add(prefix+'-head',f,dict(length=.005,radius=.0065),(q[0],q[1],q[2]+.0275),'STEEL-FASTENER-HYPOTHESIS',kind='cylinder',process='formed-fastener-head')
            add(prefix+'-nut',f,dict(length=.007,outer_radius=.007,inner_radius=.0045),(q[0],q[1],q[2]-.0265),'STEEL-FASTENER-HYPOTHESIS',kind='tube',process='formed-threaded-nut')
            add(prefix+'-washer',f,dict(length=.0015,outer_radius=.009,inner_radius=.0045),(q[0],q[1],q[2]-.02225),'STEEL-FASTENER-HYPOTHESIS',kind='tube',process='punched-washer')

    def access(name, f, envelope, start, end, *, lift, tools, flex=0., method='remove-replaceable-module'):
        assembly_access.append(dict(id=name,function=f,envelope_dimensions_m=list(envelope),
            start_transform=pose(*start),end_transform=pose(*end),
            motion=dict(kind='linear-translation',sample_count=9,translation_m=[end[i]-start[i] for i in range(3)]),
            swept_AABB_m=dict(min=[min(start[i],end[i])-envelope[i]/2 for i in range(3)],
                max=[max(start[i],end[i])+envelope[i]/2 for i in range(3)]),
            tool_access_radius_m=.15,required_tools=tools,lifting_device=lift,
            flexible_service_reserve_m=flex,sequence=['isolate-and-protect','support-and-disconnect',
                'release-counted-retention','translate-through-swept-envelope','replace-and-inspect'],
            method=method,clearance_and_lifting_verified=False,interference_resolution='pending-site-and-installed-interfaces'))

    # Four floor and roof cassettes have actual skins, foam, edges and seams.
    for n in range(4):
        x=2.2+4.2*n
        floor_grade='AL-6082-T651-SHEET' if vehicle_id in ('V3','V4','V5') else shell_grade
        floor_skin=.003 if floor_grade.startswith('AL') else skin
        for sign in (-1,1):
            box('floor-face','primary-body',(4.18,2.65,floor_skin),(x,0,1.0+sign*(core+floor_skin)/2),floor_grade,process='panel-cut-and-bond')
            box('roof-face','primary-body',(4.18,2.65,skin),(x,0,3.5+sign*(core+skin)/2),shell_grade,process='moulded-skin' if shell_grade.startswith('GFRP') else 'sheet-form-and-rivet')
        box('floor-core','primary-body',(4.18,2.65,core),(x,0,1.0),'PET-KERDYN-80',process='cut-core-and-bond')
        box('roof-core','primary-body',(4.18,2.65,core),(x,0,3.5),'PET-KERDYN-80',process='cut-core-and-bond')
        for y in (-1.31,1.31):
            box('cassette-edge-closeout','primary-body',(4.18,.035,core),(x,y,1.0),shell_grade,process='closeout-and-bond')
            box('roof-edge-closeout','primary-body',(4.18,.035,core),(x,y,3.5),shell_grade,process='closeout-and-bond')
        box('floor-bondline','primary-body',(4.18,2.65,.0006),(x,0,1.0+core/2+.0003),'ADHESIVE-EPOXY-HYPOTHESIS',process='meter-mix-bond-cure-inspect')
        box('roof-bondline','primary-body',(4.18,2.65,.0006),(x,0,3.5-core/2-.0003),'ADHESIVE-EPOXY-HYPOTHESIS',process='meter-mix-bond-cure-inspect')
    rail_grade='AL-6082-T6-EXTRUSION' if vehicle_id in ('V1','V3','V5') else shell_grade
    rail_depth=.16 if vehicle_id=='V5' else .12
    for y in (-1.15,1.15):
        box('underframe-web','primary-body',(16.8,.008,rail_depth),(8.5,y,.87),rail_grade,process='extrude-cut-drill' if rail_grade.startswith('AL') else 'moulded-stringer')
        for z in (.87-rail_depth/2-.004,.87+rail_depth/2+.004):
            box('underframe-flange','primary-body',(16.8,.10,.008),(8.5,y,z),rail_grade,process='extrude-cut-drill' if rail_grade.startswith('AL') else 'moulded-stringer')
    count=int(16.8/spacing)+1
    frame_grade='AL-6082-T6-EXTRUSION' if vehicle_id in ('V3','V4') else shell_grade
    for n in range(count):
        x=.1+16.8*n/(count-1)
        for y in (-1.36,1.36):
            if y<0 and any(abs(x-door)<.70 for door in (6.3,10.7)): continue
            box('ring-upright','primary-body',(.045,.035,2.38),(x,y,2.23),frame_grade,process='moulded-rib' if frame_grade.startswith('GFRP') else 'extrusion-cut-and-join')
        box('transverse-floor-member','primary-body',(.06,2.65,.075),(x,0,.91),rail_grade)
        box('roof-transverse-rib','primary-body',(.045,2.65,.035),(x,0,3.45),frame_grade)
    # Side sill/header strips and solid jambs leave actual door/window openings.
    for y in (-1.38,1.38):
        for z in (1.13,3.20):
            for i,(a,b) in enumerate(((.1,5.60),(7.,10.0),(11.4,16.9)) if y<0 else ((.1,16.9),)):
                box('side-belt-'+str(i),'primary-body',(b-a,skin,.26),((a+b)/2,y,z),shell_grade,process='moulded-integrated-belt' if shell_grade.startswith('GFRP') else 'sheet-cut-form-join')
        for x in (.15,2.85,5.55,7.,8.5,10.,11.45,14.15,16.85):
            box('window-door-jamb','primary-body',(.085,.060,2.05),(x,y,2.12),frame_grade)
    for x in (.08,16.92):
        for y in (-1.2,1.2): box('end-post','primary-body',(.06,.12,2.4),(x,y,2.23),rail_grade)
        box('end-crossmember','primary-body',(.06,2.65,.12),(x,0,.88),rail_grade)
        for y in (-.95,.95):
            purchased('end-escape-glazing','glazing',(.025,.65,1.40),(x,y,2.40),(37.5,52.5),'GLASS-LAMINATED-HYPOTHESIS',process='purchased-retained-glazing')
    for seam in (4.3,8.5,12.7):
        box('cassette-lap-strap','primary-body',(.10,2.6,.004),(seam,0,1.035),rail_grade)
        box('cassette-seam-adhesive','primary-body',(.10,2.6,.001),(seam,0,1.032),'ADHESIVE-EPOXY-HYPOTHESIS')
        bolt_group('cassette-joint','primary-body',(seam,-1.2,1.02),16)
        joints.append(dict(kind='cassette-lap',x_m=seam,adhesive_and_fasteners_counted=True,
            load_transfer_verified=False,fatigue_and_fire_qualified=False))

    # Bogie centres 2.9 and 14.1 m; four secondary support hardpoints/car.
    for centre in (2.9,14.1):
        for y in (-.95,.95):
            box('body-bogie-hardpoint','bogie-interfaces',(.32,.24,.030),(centre,y,.78),'AL-6082-T6-EXTRUSION',process='machined-insert')
            box('hardpoint-local-doubler','bogie-interfaces',(.55,.38,.012),(centre,y,.81),shell_grade)
            purchased('secondary-air-spring','running-gear',(.28,.28,.20),(centre,y,.64),(12.,20.),'ELASTOMER-EPDM-HYPOTHESIS')
            purchased('secondary-damper','running-gear',(.12,.12,.26),(centre+.22,y,.60),(6.,10.))
            bolt_group('hardpoint-bolt','bogie-interfaces',(centre-.08,y-.04,.77),8)
        for y in (-.8,.8):
            box('bogie-longitudinal-member','running-gear',(2.10,.12,.12),(centre,y,.46),'STEEL-S355-HYPOTHESIS',process='fabricate-and-inspect-bogie-frame')
        for x in (centre-.75,centre+.75):
            box('bogie-crossmember','running-gear',(.12,1.65,.10),(x,0,.46),'STEEL-S355-HYPOTHESIS')
            add('axle','running-gear',dict(length=1.75,radius=.065),(x,0,.32),'STEEL-S355-HYPOTHESIS',kind='cylinder',axis='y',process='forge-machine-heat-treat-and-inspect')
            for y in (-.7175,.7175):
                add('wheel-rim','running-gear',dict(length=.080,outer_radius=.320,inner_radius=.240),(x,y,.32),'STEEL-S355-HYPOTHESIS',kind='tube',axis='y',process='forged-and-profile-machined-wheel')
                add('wheel-web','running-gear',dict(length=.022,outer_radius=.240,inner_radius=.065),(x,y,.32),'STEEL-S355-HYPOTHESIS',kind='tube',axis='y')
                purchased('axle-bearing','running-gear',(.16,.10,.16),(x,y*1.21,.32),(6.,10.))
                purchased('primary-spring-damper','running-gear',(.15,.15,.18),(x,y,.48),(10.,17.))
                add('friction-brake-disc','running-gear',dict(length=.018,outer_radius=.210,inner_radius=.080),(x,y*.65,.32),'STEEL-S355-HYPOTHESIS',kind='tube',axis='y')
                purchased('independent-brake-caliper','running-gear',(.30,.16,.25),(x+.16,y*.65,.40),(13.,21.))
                purchased('brake-pad-pair','running-gear',(.16,.05,.10),(x+.16,y*.65,.40),(1.5,3.))
            bolt_group('bogie-frame-bolt','running-gear',(x,-.8,.49),12)
        purchased('antiroll-bar-link-set','running-gear',(.12,1.7,.16),(centre,0,.58),(15.,25.))
        purchased('bogie-lateral-stops','running-gear',(.18,.50,.12),(centre,0,.64),(7.,12.))
        access('bogie-removal-'+str(centre),'running-gear',(2.35,2.,.80),(centre,0,.45),(centre,3.,.45),lift='car-body-lift-and-bogie-drop-table',tools=['torque-tool','spring-restraint'],flex=.5)
    # Passive fin is split into removable 3 m plates; all excitation stays wayside.
    for x in (4.,7.,10.):
        box('passive-aluminium-fin','LIM-interface',(2.98,.012,.30),(x,0,.51),'AL-6082-T651-SHEET',process='plate-cut-drill-and-deburr')
        for dx in (-1.0,1.0):
            box('secondary-hanger','LIM-interface',(.07,.10,.24),(x+dx,0,.75),'AL-6082-T6-EXTRUSION')
            bolt_group('secondary-retention','LIM-interface',(x+dx-.025,-.025,.80),4)
        access('secondary-replacement-'+str(x),'LIM-interface',(3.,.25,.40),(x,0,.51),(x,0,.10),lift='supported-lifting-cradle',tools=['torque-tool','air-gap-gauge'])

    # 40 four-abreast seats plus four fixed wall-bench places =44/car.
    for x in (1.1,2.,2.9,3.8,4.7,12.3,13.2,14.1,15.,15.9):
        for y in (-1.02,-.53,.53,1.02):
            box('seat-pan','seating',(.44,.44,.007),(x,y,1.43),'GFRP-EGLASS-HYPOTHESIS-1',process='moulded-seat-shell')
            box('seat-back','seating',(.004,.44,.65),(x+.20,y,1.77),'GFRP-EGLASS-HYPOTHESIS-1')
            box('seat-leg','seating',(.035,.035,.40),(x,y,1.215),'AL-6082-T6-EXTRUSION')
            purchased('seat-cushion-and-cover','seating',(.42,.42,.05),(x,y,1.47),(1.2,2.0),'ELASTOMER-EPDM-HYPOTHESIS')
            bolt_group('seat-anchor','seating',(x-.04,y-.04,1.02),4)
    for y in (-1.12,1.12):
        box('two-place-wall-bench','seating',(.95,.44,.028),(8.9,y,1.43),'GFRP-EGLASS-HYPOTHESIS-1',process='moulded-integrated-bench')
        box('bench-bracket','seating',(.85,.045,.32),(8.9,y,1.25),'AL-6082-T6-EXTRUSION')
        purchased('bench-cushion-two-place','seating',(.95,.42,.045),(8.9,y,1.47),(3.,5.),'ELASTOMER-EPDM-HYPOTHESIS')
        bolt_group('bench-anchor','seating',(8.6,y-.025,1.02),8)
    for y in (-.90,.90):
        purchased('wheelchair-restraint-and-call','seating',(.10,.25,.12),(7.7,y,1.1),(4.,8.))
    for y in (-1.39,1.39):
        for x in (1.6,4.1,7.7,9.15,12.8,15.35):
            # Purchased laminate envelope: ply/PVB internal detail stays pending.
            purchased('side-window-module','glazing',(1.10,.022,.92),(x,y,2.24),(58.,72.),'GLASS-LAMINATED-HYPOTHESIS',process='purchased-laminated-window')
            box('window-gasket-upper','glazing',(1.10,.018,.014),(x,y,2.71),'ELASTOMER-EPDM-HYPOTHESIS')
            box('window-gasket-lower','glazing',(1.10,.018,.014),(x,y,1.77),'ELASTOMER-EPDM-HYPOTHESIS')
            for sign in (-1,1): box('window-gasket-side','glazing',(.014,.018,.92),(x+sign*.557,y,2.24),'ELASTOMER-EPDM-HYPOTHESIS')
            bolt_group('window-retainer','glazing',(x-.50,y,1.78),8)
            access('window-'+str(x)+'-'+str(y),'glazing',(1.16,.07,.98),(x,y,2.24),(x,3. if y>0 else -3.,2.24),lift='suction-lift-with-rated-restraint',tools=['glazing-tool','torque-tool'])
    for x in (6.3,10.7):
        for dx in (-.285,.285):
            box('door-leaf-core','doors',(.55,.035,2.02),(x+dx,-1.41,2.04),'PET-KERDYN-80',process='bonded-door-leaf')
            for dy in (-.020,.020): box('door-leaf-face','doors',(.55,.003,2.02),(x+dx,-1.41+dy,2.04),'AL-6082-T651-SHEET')
            purchased('door-roller-bearing','doors',(.065,.055,.065),(x+dx,-1.40,3.09),(1.,2.))
            purchased('door-bottom-guide','doors',(.12,.08,.06),(x+dx,-1.40,1.02),(1.,2.))
            access('door-leaf-motion-'+str(x+dx),'doors',(.56,.055,2.03),(x+dx,-1.41,2.04),(x+dx+(-.55 if dx<0 else .55),-1.48,2.04),lift='none-in-service',tools=['retained-roller-and-mechanical-stop'],method='plug-slide-service-sweep')
        purchased('door-drive-lock-emergency-set','doors',(.95,.16,.18),(x,-1.32,3.13),(30.,48.))
        box('door-running-track','doors',(2.30,.045,.040),(x,-1.35,3.20),'AL-6082-T6-EXTRUSION')
        for dx in (-.59,.59):
            box('door-jamb-reinforcement','doors',(.07,.09,2.20),(x+dx,-1.35,2.09),'AL-6082-T6-EXTRUSION')
            box('door-vertical-seal','doors',(.018,.020,2.08),(x+dx,-1.44,2.04),'ELASTOMER-EPDM-HYPOTHESIS')
            purchased('door-travel-stop','doors',(.055,.055,.055),(x+dx,-1.39,3.17),(1.,2.))
        purchased('door-step-gap-bridge','doors',(1.1,.22,.06),(x,-1.47,1.0),(10.,18.))
        bolt_group('door-module-retainer','doors',(x-.5,-1.34,3.2),16)
        access('door-mechanism-replacement-'+str(x),'doors',(1.05,.25,.25),(x,-1.32,3.13),(x,0.,2.8),lift='portable-module-cradle',tools=['door-isolation','torque-tool'],flex=1.0)

    for x in (4.25,12.75):
        purchased('HVAC-roof-unit','HVAC',(1.70,1.10,.30),(x,0,3.73),(180.,260.))
        for y in (-.45,.45):
            box('HVAC-support-rail','HVAC',(1.85,.06,.06),(x,y,3.56),'AL-6082-T6-EXTRUSION')
            bolt_group('HVAC-mount','HVAC',(x-.75,y,3.55),8)
        purchased('HVAC-flexible-duct-and-vibration-set','HVAC',(.35,.70,.20),(x,0,3.40),(8.,15.),'ELASTOMER-EPDM-HYPOTHESIS')
        access('HVAC-replacement-'+str(x),'HVAC',(1.85,1.25,.45),(x,0,3.73),(x,0,5.),lift='crane-and-spreader',tools=['refrigerant-recovery','torque-tool'],flex=.5)
    for y in (-.60,.60):
        box('HVAC-duct-top','HVAC',(15.8,.35,.001),(8.5,y,3.31),'AL-6082-T651-SHEET')
        box('HVAC-duct-bottom','HVAC',(15.8,.35,.001),(8.5,y,3.17),'AL-6082-T651-SHEET')
        for dy in (-.175,.175): box('HVAC-duct-side','HVAC',(15.8,.001,.14),(8.5,y+dy,3.24),'AL-6082-T651-SHEET')
        purchased('HVAC-insulation-and-diffusers','HVAC',(15.8,.40,.18),(8.5,y,3.24),(18.,32.),'PET-KERDYN-80')
    purchased('condensate-drain-hose','HVAC',(.04,.04,2.5),(11.9,1.30,2.3),(2.,4.),'ELASTOMER-EPDM-HYPOTHESIS')
    for x in (1.2,2.9,6.4,8.1,9.8,11.5,15.,16.2):
        purchased('flush-solar-module','solar-roof',(1.55,1.05,.025),(x,.68,3.555),(14.,20.),'GLASS-LAMINATED-HYPOTHESIS')
        for y in (.20,1.16):
            box('solar-removable-clamp','solar-roof',(.08,.035,.025),(x,y,3.54),'AL-6082-T6-EXTRUSION')
            bolt_group('solar-retainer','solar-roof',(x,y,3.54),2)
    purchased('solar-isolator-and-MPPT','solar-roof',(.35,.25,.12),(9.6,.85,.72),(5.,10.))
    purchased('auxiliary-battery-with-BMS','auxiliary-power',(1.1,.75,.38),(8.5,1.0,.60),(220.,350.))
    purchased('auxiliary-DC-converter','auxiliary-power',(.5,.38,.22),(9.35,.95,.64),(22.,38.))
    purchased('LV-distribution-protection','auxiliary-power',(.7,.22,.7),(11.8,1.18,1.53),(24.,42.))
    for x in (8.15,8.85):
        box('battery-slide-rail','auxiliary-power',(.08,.90,.04),(x,.95,.40),'AL-6082-T6-EXTRUSION')
        bolt_group('battery-cradle-anchor','auxiliary-power',(x,.75,.43),8)
    purchased('battery-stop-lock-and-restraint','auxiliary-power',(1.0,.08,.12),(8.5,.62,.48),(7.,12.))
    access('battery-removal','auxiliary-power',(1.20,.85,.45),(8.5,1.,.60),(8.5,3.,.60),lift='rated-battery-trolley-and-restraint',tools=['electrical-isolation','insulated-tool'],flex=.6)
    for name,dims,xyz,bounds in (
        ('ATP-TCMS-enclosure',(.60,.30,.55),(11.8,1.12,2.25),(28.,45.)),
        ('brake-control-and-energy-store',(.75,.50,.45),(7.,1.,.60),(55.,85.)),
        ('fire-emergency-equipment',(.40,.30,.50),(5.2,1.15,1.50),(15.,25.)),
        ('localisation-and-speed-sensor',(.12,.12,.12),(2.9,.80,.52),(2.,4.)),
        ('localisation-and-speed-sensor',(.12,.12,.12),(14.1,.80,.52),(2.,4.)),
        ('passenger-call-radio-and-CCTV',(.70,.20,.20),(8.5,0.,3.18),(8.,16.))):
        purchased(name,'control-safety',dims,xyz,bounds)
    for x,gangway_x in ((.35,-.125),(16.65,17.125)):
        purchased('coupler-drawgear','coupling-articulation',(1.20,.50,.40),(x,0,.75),(120.,180.))
        purchased('gangway-bellows-and-retention','coupling-articulation',(.25,1.2,2.15),(gangway_x,0,2.10),(70.,110.),'ELASTOMER-EPDM-HYPOTHESIS')
        bolt_group('coupler-anchor','coupling-articulation',(x-.05,-.20,.90),16)
    # Flexible circuits, conduits and every retained cable clip are counted.
    for name,area,length,y,z in (('LV-power-conductor',25e-6,30.,1.0,1.12),
        ('door-HVAC-conductor',6e-6,120.,1.10,3.12),('control-data-conductor',1.5e-6,240.,-1.10,3.12)):
        for circuit in range(round(length/15.)):
            add(name,'auxiliary-power',dict(length=15.,radius=(area/pi)**.5),(8.5,y+(.006*circuit),z),'COPPER-CU-ETP-HYPOTHESIS',kind='cylinder',axis='x',process='cut-terminate-inspect-cable',details=dict(straight_routed_segment=True,circuit_length_m=15.,termination_and_flex_routing_pending=True))
        purchased(name+'-insulation-flex-loop','auxiliary-power',(15.0,.06,.04),(8.5,y,z),(3.,7.),'ELASTOMER-EPDM-HYPOTHESIS')
    for n in range(64):
        x=.4+16.2*n/63
        box('service-cable-clip','auxiliary-power',(.025,.025,.015),(x,1.15,3.12),'AL-6082-T6-EXTRUSION')
        bolt_group('cable-clip-fastener','auxiliary-power',(x,1.15,3.12),1)
    purchased('flexible-service-connectors-and-hose-set','auxiliary-power',(1.,.20,.12),(8.5,1.0,1.18),(12.,22.),'ELASTOMER-EPDM-HYPOTHESIS')
    purchased('small-equipment-retention-consumables','control-safety',(.50,.20,.15),(11.8,1.10,.80),(15.,30.))
    # Replaceable interior service panels preserve access; no bonded machine.
    for x in (2.2,6.4,10.6,14.8):
        for y in (-1.30,1.30):
            box('removable-interior-service-panel','primary-body',(4.10,.004,.65),(x,y,1.47),'GFRP-EGLASS-HYPOTHESIS-1',process='moulded-replaceable-panel')
            bolt_group('service-panel-captive-retainer','primary-body',(x-.50,y,1.17),8)

    assemblies=[dict(id='train',parent_id=None)]
    occurrences=[]
    for car in range(6):
        parent='car-'+str(car+1)
        assemblies.append(dict(id=parent,parent_id='train'))
        assemblies.extend(dict(id=parent+'/'+f,parent_id=parent) for f in FUNCTIONS)
        for n,row in enumerate(local):
            x,y,z=row['xyz']; transform=pose(x+17.5*car,y,z,row['axis'])
            occurrences.append(make_occurrence(parent+'/'+row['name'],row['part'],
                parent_id=parent+'/'+row['parent'],transform=transform,scope='vehicle/'+row['function']))
    # Conservative finite-sample broad phase, not a claim of collision-free
    # installation. Retention within the serviced function is removed first;
    # every other function remains an explicit obstacle.
    obstacles=[]
    for row in local:
        geometry=row['part']['geometry'];d=geometry['dimensions_m']
        if geometry['kind'] in ('box','envelope'): extent=list(d)
        else:
            radius=d.get('outer_radius',d.get('radius'));extent=[2*radius,2*radius,d['length']]
            if row['axis']=='x':extent=[extent[2],extent[1],extent[0]]
            elif row['axis']=='y':extent=[extent[0],extent[2],extent[1]]
        obstacles.append((row['name'],row['function'],row['xyz'],extent))
    for access_record in assembly_access:
        collision=set();d=access_record['envelope_dimensions_m']
        a=[access_record['start_transform'][i][3] for i in range(3)]
        delta=access_record['motion']['translation_m']
        for sample in range(access_record['motion']['sample_count']):
            centre=[a[i]+delta[i]*sample/(access_record['motion']['sample_count']-1) for i in range(3)]
            for name,function,location,extent in obstacles:
                if function==access_record['function']:continue
                if all(abs(centre[i]-location[i])<(d[i]+extent[i])/2-1e-9 for i in range(3)):
                    collision.add(name)
        access_record['sampled_broad_phase_intersections']=sorted(collision)
        access_record['sampled_clearance_state']='potential-interference' if collision else 'no-sampled-AABB-intersection'
        access_record['continuous_clearance_proved']=False
    registry=make_registry(vehicle_id+' '+title,list(parts.values()),occurrences,list(FUNCTIONS),assemblies=assemblies)
    validate_registry(registry)
    totals=summary(registry)
    per_car_properties=_mass_properties(local)
    train_properties=_mass_properties([dict(row,xyz=(row['xyz'][0]+17.5*car,row['xyz'][1],row['xyz'][2])) for car in range(6) for row in local])
    source={PRODUCER:digest(root/PRODUCER)}
    for path in sorted((root/'engineering/component_registry').rglob('*')):
        if path.is_file() and path.suffix in ('.py','.json') and 'tests' not in path.parts and '__pycache__' not in path.parts:
            source[path.relative_to(root).as_posix()]=digest(path)
    function_counts={f:sum(row['function']==f for row in local) for f in FUNCTIONS}
    value=dict(schema='osr-equipped-reference-cell-vehicle/1',vehicle_id=vehicle_id,label=title,
        candidate_id=registry['candidate_id'],registry=registry,summary=totals,
        requirements=deepcopy(REQUIREMENTS),functional_requirements=list(FUNCTIONS),
        per_car_mass_properties=per_car_properties,train_mass_properties=train_properties,
        per_car_occurrences=len(local),per_car_functional_occurrences=function_counts,
        per_car_part_definitions=len(parts),geometry_scope='Sized net stock primitives plus bounded purchased envelopes; interface cuts, routing and supplier internals remain unqualified',
        architecture=dict(load_path_hypothesis=load_path,shell_grade=shell_grade,skin_thickness_m=skin,
            sandwich_core_m=core,ring_spacing_m_hypothesis=spacing,physical_structure_validated=False),
        interfaces=dict(bogie_centres_per_car_m=[2.9,14.1],axle_longitudinal_positions_m=[2.15,3.65,13.35,14.85],
            body_secondary_hardpoint_positions_m=[[x,y,.78] for x in (2.9,14.1) for y in (-.95,.95)],body_secondary_hardpoints_per_car=4,
            door_centres_per_car_m=[6.3,10.7],door_side_y_m=-1.41,
            wheelchair_spaces_per_car=[dict(center_m=[7.7,y,1.05],envelope_m=[1.25,.75,1.4]) for y in (-.9,.9)],
            nominal_cabin_aisle_m=.60,passive_secondary_segments_per_car=3,
            longitudinal_car_pitch_m=17.5,frame_origin='x=car first end; y=cross-track; z=running-rail top'),
        manufacturing_plan=[dict(part_definition_id=p['physical_definition_id'],part_revision_id=p['revision_id'],
            part_id=p['part_id'],process=p['manufacturing'],required_inspections=['dimensional','material-lot','joint-or-retention'],
            approved_work_instruction=None,qualified_tooling=None) for p in parts.values()],
        assembly_access=assembly_access,body_joints=joints,
        mass_complete=False,complete_installed_vehicle_mass_kg=None,
        installed_functional_categories_represented=all(function_counts.values()),
        unresolved=['Supplier internals, actual routed wiring, mounting holes/copes and tolerances',
            'Calibrated masses, installed CG/inertia and delivered material/lot records',
            'Laminate schedules/allowables, joints, body/door/glazing/HVAC/solar/brake load paths and fire/crash qualification',
            'Service sweeps, passenger clearances, structural supports, tool/lifting access and replacement fitup',
            'Brake energy/fade/adhesion, thermal cooling duty and sealed electrical protection',
            'Actual blank/cut layouts, moulds, process yields/cycle/labour and sourced lifecycle costs'],
        source_sha256=source,**FLAGS)
    value['evaluation_id']=identity(value)
    return value
