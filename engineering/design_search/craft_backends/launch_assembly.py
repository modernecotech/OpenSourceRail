"""Sized research launch shuttle: physical parts, interfaces and bounded CAD runs.

This is a separate component proposal, not the selected train or available thrust.
Nominal solids do not prove fits, fatigue, engagement, release or installed mass.
"""
from copy import deepcopy
from math import pi, sqrt, fsum
from pathlib import Path
import json
from . import native, solidcraft
from .cases import identity

ROOT=Path(__file__).resolve().parents[3]
SOURCE='engineering/design_search/craft_backends/launch_assembly.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,selected_reference_changed=False,movement_authority=False,
    installed_mass_complete=False)
STEEL='steel-proposed';BRONZE='bronze-bush-proposed'
MATERIALS={STEEL:dict(density_kg_m3=7850.,grade='S355-like candidate; certificate/thickness properties unverified'),
           BRONZE:dict(density_kg_m3=8800.,grade='CuSn bearing-bronze candidate; PV/wear properties unverified')}


def _box(name,at,size,group,*,holes=(),material=STEEL,stock=None):
    return dict(id=name,shape='box',at_m=list(at),size_m=list(size),holes=list(holes),material=material,
        subassembly=group,stock=stock or 'cut/machine plate',geometry_basis='Nominal dimensioned part; threads, fillets and weld beads separately unresolved')


def _cyl(name,at,radius,length,group,*,inner=0.,material=STEEL):
    return dict(id=name,shape='tube' if inner else 'cylinder',at_m=list(at),axis=[0,1,0],
        radius_m=radius,inner_radius_m=inner,length_m=length,material=material,subassembly=group,
        stock='turned/bored stock',geometry_basis='Nominal journal or annular part; fits and supplier qualification remain open')


def _rhs(name,at,size,axis,group):
    return dict(id=name,shape='hollow_box',at_m=list(at),size_m=list(size),wall_m=.006,
        hollow_axis=axis,material=STEEL,subassembly=group,stock='RHS100x60x6 candidate, cut to length',
        geometry_basis='Actual open-ended hollow section; corner radii and seam geometry not yet specified')


def dimensions():
    return dict(ear_length_m=.160,ear_thickness_m=.025,ear_height_m=.120,bore_diameter_m=.040,
        bore_center_local_xz_m=[.120,.060],ear_local_y_m=[-.055,.030],clear_gap_m=.060,
        ear_parent_translation_m=[.10,0,.24],pin_diameter_m=.040,pin_length_m=.200,
        root_support_local_x_m=0.,research_train_mass_kg=160000.,target_acceleration_m_s2=1.,
        total_longitudinal_requirement_N=160000.,force_per_ear_N=80000.)


def _parts():
    p=[]
    for i,y in enumerate((-.31,.25)):
        e=_rhs(f'frame/longitudinal/{i}',[-.60,y,.12],[1.20,.06,.10],'x','frame')
        e['holes']=[dict(axis='z',diameter_m=.018,x_m=x,y_m=.030) for x in (.44,.86)]
        p.append(e)
    for i,x in enumerate((-.53,-.03,.47)):
        p.append(_rhs(f'frame/crossmember/{i}',[x,-.25,.12],[.06,.50,.10],'y','frame'))
    mounting=[dict(axis='z',diameter_m=.018,x_m=x,y_m=y) for x in (.04,.46) for y in (.02,.58)]
    p.append(_box('frame/clevis-deck',[-.20,-.30,.22],[.50,.60,.020],'frame',holes=mounting))
    p.append(_box('clevis/backplate',[.075,-.055,.24],[.025,.110,.120],'clevis'))
    for i,y in enumerate((-.055,.030)):
        p.append(_box(f'clevis/ear/{i}',[.10,y,.24],[.160,.025,.120],'clevis',
            holes=[dict(axis='y',diameter_m=.040,x_m=.120,z_m=.060)]))
    pin=_cyl('clevis/pin',[.220,-.100,.300],.020,.200,'clevis')
    pin['blind_bores']=[dict(base_m=[.220,-.100,.300],axis=[0,1,0],radius_m=.005,length_m=.020),dict(base_m=[.220,.100,.300],axis=[0,-1,0],radius_m=.005,length_m=.020)]
    p.append(pin)
    for i,y in enumerate((-.061,.055)):
        p.append(_cyl(f'clevis/pin-washer/{i}',[.220,y,.300],.031,.006,'clevis',inner=.0202))
    for i,y in enumerate((-.100,.061)):
        p.append(_cyl(f'clevis/pin-spacer/{i}',[.220,y,.300],.029,.039,'clevis',inner=.0202))
    for i,y in enumerate((-.106,.100)):
        p.append(_cyl(f'clevis/pin-end-cap/{i}',[.220,y,.300],.032,.006,'clevis',inner=.0055))
        shaft_y=-.106 if i==0 else .080
        head_y=-.116 if i==0 else .106
        p.append(_cyl(f'clevis/retaining-screw-shank/{i}',[.220,shaft_y,.300],.005,.026,'clevis'))
        p.append(_cyl(f'clevis/retaining-screw-head/{i}',[.220,head_y,.300],.008,.010,'clevis'))
    for side in (-1,1):
        for i,x in enumerate((-.50,.50)):
            sy=.310 if side==1 else -.322
            holes=[dict(axis='y',diameter_m=.020,x_m=.04,z_m=z) for z in (.22,.06)]
            holes.append(dict(axis='y',diameter_m=.009,x_m=.04,z_m=.29))
            p.append(_box(f'guidance/drop-plate/{side}/{i}',[x-.04,sy,-.15],[.08,.012,.35],'guidance',holes=holes))
            for role,z,radius,width in [('running',.070,.070,.045),('capture',-.090,.050,.030)]:
                wy=.330 if side==1 else -.330-width
                key=f'guidance/{role}/{side}/{i}'
                p.append(_cyl(key+'/wheel',[x,wy,z],radius,width,'guidance',inner=.016))
                p.append(_cyl(key+'/bush',[x,wy,z],.016,width,'guidance',inner=.010,material=BRONZE))
                p.append(_cyl(key+'/axle',[x,.29 if side==1 else -.420,z],.010,.130,'guidance'))
                cy=.383 if side==1 else -.393
                p.append(_cyl(key+'/washer',[x,cy,z],.017,.003,'guidance',inner=.0102))
                p.append(_cyl(key+'/collar',[x,cy+.003 if side==1 else cy-.010,z],.015,.010,'guidance',inner=.0102))
                # A separately counted radial locking screw, represented at
                # major diameter. Its thread/drive removals remain bounded.
                e=dict(id=key+'/collar-lock-screw',shape='cylinder',at_m=[x,cy+.008,z+.009],axis=[0,0,1],
                    radius_m=.003,length_m=.012,material=STEEL,subassembly='guidance',stock='M6 locking screw candidate',
                    geometry_basis='Smooth major-diameter gross stock; thread and drive geometry excluded')
                p.append(e)
        gy=.440 if side==1 else -.443
        holes=[dict(axis='y',diameter_m=.009,x_m=x,z_m=.29) for x in (.15,1.15)]
        p.append(_box(f'guards/side/{side}',[-.65,gy,-.15],[1.30,.003,.34],'guards',holes=holes,stock='3mm sheet; laser cut/deburr, captive attachment required'))
        for i,x in enumerate((-.50,.50)):
            y=.322 if side==1 else -.440
            p.append(_cyl(f'guards/spacer/{side}/{i}',[x,y,.14],.008,.118,'guards',inner=.0045))
            y=.290 if side==1 else -.460
            p.append(_cyl(f'guards/stud/{side}/{i}',[x,y,.14],.004,.170,'guards'))
            stacks=[(.308,.302),(.443,.445)] if side==1 else [(-.310,-.308),(-.445,-.451)]
            for j,(washer_y,nut_y) in enumerate(stacks):
                p.append(_cyl(f'guards/washer/{side}/{i}/{j}',[x,washer_y,.14],.009,.002,'guards',inner=.0045))
                p.append(_cyl(f'guards/nut-blank/{side}/{i}/{j}',[x,nut_y,.14],.0075,.006,'guards',inner=.004))
    # Deck attachment: actual through-holes and separate fastener stock.
    for i,x in enumerate((-.16,.26)):
        for j,y in enumerate((-.28,.28)):
            at=[x,y,.085]
            e=dict(id=f'fasteners/deck-stud/{i}/{j}',shape='cylinder',at_m=at,axis=[0,0,1],radius_m=.008,
                length_m=.190,material=STEEL,subassembly='fasteners',stock='M16 stud candidate',
                geometry_basis='Gross major-diameter geometry; threads/preload/certification unresolved')
            p.append(e)
            for k,(z,nut_z) in enumerate(((.117,.107),(.240,.243))):
                p.append(dict(id=f'fasteners/deck-washer/{i}/{j}/{k}',shape='tube',at_m=[x,y,z],axis=[0,0,1],radius_m=.015,
                    inner_radius_m=.0085,length_m=.003,material=STEEL,subassembly='fasteners',stock='M16 washer candidate',geometry_basis='Nominal annular stock'))
                p.append(dict(id=f'fasteners/deck-nut-blank/{i}/{j}/{k}',shape='tube',at_m=[x,y,nut_z],axis=[0,0,1],radius_m=.014,
                    inner_radius_m=.008,length_m=.010,material=STEEL,subassembly='fasteners',stock='M16 threaded nut blank; wrench flats not yet modelled',geometry_basis='Gross turned blank, not catalog net mass'))
    for i,x in enumerate((-.16,.26)):
        for j,y in enumerate((-.28,.28)):
            p.append(dict(id=f'fasteners/deck-crush-sleeve/{i}/{j}',shape='tube',at_m=[x,y,.126],axis=[0,0,1],radius_m=.013,
                inner_radius_m=.009,length_m=.088,material=STEEL,subassembly='fasteners',stock='Machined internal crush sleeve before deck clamp',geometry_basis='Sleeve spans actual RHS inner faces; prevents an unsupported hollow-wall clamp hypothesis'))
    return p


def measures(part):
    """Analytical nominal material; subtract real bores, never solid RHS envelopes."""
    s=part['shape'];at=part['at_m']
    if s in ('box','hollow_box'):
        size=part['size_m'];v=size[0]*size[1]*size[2];mom=[v*(at[i]+size[i]/2) for i in range(3)]
        if s=='hollow_box':
            axis='xyz'.index(part['hollow_axis']);inner=[n if i==axis else n-2*part['wall_m'] for i,n in enumerate(size)]
            if min(inner)<=0:raise ValueError('RHS wall removes its section')
            iv=inner[0]*inner[1]*inner[2];v-=iv;mom=[v*(at[i]+size[i]/2) for i in range(3)]
        for hole in part.get('holes',[]):
            axis='xyz'.index(hole.get('axis','z'));r=hole['diameter_m']/2;length=hole.get('length_m',size[axis])
            center=[at[i]+(size[i]/2 if i==axis else hole.get(('x_m','y_m','z_m')[i],0.)) for i in range(3)]
            for i in range(3):
                if i!=axis and not r<=center[i]-at[i]<=size[i]-r:raise ValueError('Bore exceeds plate bounds')
            effective_length=2*part['wall_m'] if s=='hollow_box' and axis!='xyz'.index(part['hollow_axis']) else length
            hv=pi*r*r*effective_length;v-=hv;mom=[m-hv*c for m,c in zip(mom,center)]
        center=[m/v for m in mom];bounds=[at,[at[i]+size[i] for i in range(3)]]
    else:
        r=part['radius_m'];inner=part.get('inner_radius_m',0.);length=part['length_m'];axis=part['axis']
        if not 0<=inner<r:raise ValueError('Positive annular wall required')
        v=pi*(r*r-inner*inner)*length-sum(pi*b['radius_m']**2*b['length_m'] for b in part.get('blind_bores',[]));center=[at[i]+axis[i]*length/2 for i in range(3)]
        bounds=[[min(at[i],at[i]+axis[i]*length)-r*sqrt(1-axis[i]**2) for i in range(3)],
                [max(at[i],at[i]+axis[i]*length)+r*sqrt(1-axis[i]**2) for i in range(3)]]
    if v<=0:raise ValueError('Positive net nominal stock required')
    return dict(volume_m3=v,centroid_m=center,bounds_m=bounds,
        nominal_material_mass_kg=v*MATERIALS[part['material']]['density_kg_m3'])


def build():
    parts=_parts();ids={p['id'] for p in parts}
    if len(ids)!=len(parts):raise ValueError('Duplicate assembly occurrence')
    physical=dict(schema='osr-launch-shuttle-physical/1',frame='station-local right-handed: +x forward,+y left,+z up; rail top z=0',
        materials=MATERIALS,parts=parts,subassemblies=['frame','clevis','guidance','guards','fasteners'],
        parent_transforms={name:dict(rotation_matrix=[[1,0,0],[0,1,0],[0,0,1]],translation_m=[0,0,0])
                           for name in ['frame','clevis','guidance','guards','fasteners']})
    cid=identity(physical)
    ears=[p for p in parts if p['id'].startswith('clevis/ear/')]
    component=dict(schema='osr-launch-double-clevis-geometry/1',parts=ears,component_frame=dict(translation_to_station_m=[.10,0,.24],
        rotation_matrix=[[1,0,0],[0,1,0],[0,0,1]]))
    quantities={p['id']:measures(p) for p in parts};nominal=fsum(v['nominal_material_mass_kg'] for v in quantities.values())
    b=dict(schema='osr-launch-detail-assembly/1',case_id='launch-shuttle-detail',candidate_id=cid,
        component_geometry_id=identity(component),physical_definition=physical,dimensions=dimensions(),
        entities=parts,materials=MATERIALS,part_measures=quantities,component_geometry=component,
        nominal_located_material_mass_kg=nominal,
        installed_mass_bound_kg=[nominal*.98+.80,nominal+3.00],
        mass_scope='Nominal cut/bored material plus bounded thread/flats, weld filler, grease, sensors and flexible cable; not verified installed mass',
        unresolved_mass_accounts=[dict(id='weld-filler',low_kg=.30,high_kg=1.20),dict(id='grease-and-protection',low_kg=.10,high_kg=.30),
            dict(id='two-position-sensors',low_kg=.20,high_kg=.60),dict(id='flexible-cable-and-retention',low_kg=.20,high_kg=.90)],
        fastener_representation='Major-diameter studs, annular nut blanks and washers explicitly counted; threads, drive sockets and wrench flats remain to detail',
        requirements=dict(train_mass_kg=160000.,acceleration_m_s2=1.,longitudinal_force_N=160000.,available_thrust_N=None,
            force_basis='m*a research requirement only; excludes resistance/grade and does not establish an actuator map',launch_speed_m_s=None,powered_length_m=None),
        fem_interface=dict(schema='osr-launch-clevis-load-interface/1',candidate_id=cid,component_geometry_id=identity(component),
            component_body_ids=[p['id'] for p in ears],dimensions=dimensions(),units=dict(length='m',force='N',stress='Pa'),
            material_hypothesis=dict(young_Pa=210e9,poisson=.3,density_kg_m3=7850.,nominal_yield_Pa=355e6,
                status='Declared isotropic S355-like candidate, not certified or approved allowable'),
            total_force_N=160000.,force_per_ear_N=80000.,force_direction=[1,0,0],
            support=dict(local_plane='x=0',hypothesis='fully clamped root only; actual backplate/weld/deck flexibility unverified'),
            load=dict(region='positive-x half of bore',hypothesis='distributed bearing contact surrogate; no concentrated node force'),
            **FLAGS),
        joints=_joints(parts),access=_access(),manufacturing=_manufacturing(parts),
        engineering_holds=['Actual actuator/energy store and independent train braking absent from this component model',
            'Root weld, deck bolt preload/slip, guideway strength and rail retention load transfer unqualified',
            'Bearing PV/wear, fatigue, engagement/release, jerk and failure recovery require separate evidence',
            'Nominal solids omit threads, fillets, weld beads and certified supplier fits; no manufacturing release'],**FLAGS)
    b['assembly_definition_id']=identity(b);return b


def _joints(parts):
    return dict(clevis_ears=2,removable_coupling_pins=1,pin_spacers=2,pin_washers=2,pin_end_caps=2,pin_retaining_screws=2,
        running_wheels=4,capture_wheels=4,plain_bushes=8,wheel_axles=8,wheel_collars=8,wheel_collar_lock_screws=8,
        deck_studs=4,deck_crush_sleeves=4,deck_washers=8,deck_nut_blanks=8,guard_studs=4,guard_washers=8,guard_nut_blanks=8,guard_spacers=4,
        welded_interfaces=[dict(id='crossmember-ends',count=6),dict(id='drop-plate-to-frame',count=4),
            dict(id='ear-to-backplate',count=2),dict(id='backplate-to-deck',count=1)],
        root_weld_hypothesis='Continuous6mm fillet candidate; weld sizing, access, distortion and fatigue remain open',
        fits=[dict(interface='coupling pin/ears',nominal_diameter_m=.040,status='Fit/tolerance and replaceable bush design pending'),
              dict(interface='wheel/bush/axle',wheel_bore_m=.032,bush_bore_m=.020,status='Nominal contact; press/sliding fits require supplier/material sizing')],
        wiring=dict(position_sensors=2,flexible_cable_length_m=2.4,service_loop_travel_m=1.,mass_status='bounded allowance, not zero'),
        cooling=dict(active_hoses_count=0,basis='No hydraulic actuator or active cooler belongs to this component; their cooling and flexible connections remain external unknowns',
                     bearing_friction_heat_qualified=False))


def _access():
    return dict(travel=dict(direction=[1,0,0],range_m=[-.50,.50],
        swept_bounds_m=[[-1.15,-.46,-.15],[1.15,.46,.36]],finite_local_stroke_only=True,
        remaining_station_acceleration_distance_m=None),
        removal=[dict(component='clevis/pin',direction=[0,1,0],distance_m=.30,required_clearance_m=.30,
                     sequence=['Isolate and mechanically unload shuttle; park/lock independently','Remove upper guard/access obstruction and pin retaining screws and end caps','Support mating eye, withdraw pin along+y; never under stored load']),
                 dict(component='wheel-axle-bush',direction=[0,1,0],distance_m=.20,required_tool_envelope_m=[.25,.25,.25],
                     sequence=['Unload/capture assembly with jacking supports','Remove corresponding side guard','Release collar lock and withdraw axle before bush removal'])],
        installation=['Weld and inspect frame in jig before machining mating datums','Insert and inspect RHS crush sleeves before closing/joining frame; fit deck/backplate/ears with bore alignment fixture',
            'Fit wheel bushes, axles and both running/capture rollers','Install lock devices, sensors and cable service loops','Fit guards; verify swept/tool/removal envelopes on real guideway'],
        lifting=dict(points=4,method='Engineered removable lifting fixture; lug positions/capacity and proof test pending',rated_capacity_kg=None),
        retention=dict(required=True,capture_wheel_count=4,longitudinal_force_height_m=.30,wheelbase_m=1.,
            pitch_moment_requirement_Nm=48000.,pitch_reaction_delta_N=48000.,
            status='Necessary equilibrium requirement; roller/axle/guideway reaction capacity not qualified'),
        envelope_status='Finite dimensional envelopes defined, but collision/access validation on complete installation remains pending')


def _manufacturing(parts):
    return dict(bom=[dict(part_id=p['id'],subassembly=p['subassembly'],quantity=1,material=p['material'],stock=p['stock'],
        nominal_volume_m3=measures(p)['volume_m3'],nominal_mass_kg=measures(p)['nominal_material_mass_kg'],
        route=['cut/turn/form stock as declared','machine bores and mating datums','deburr/protect','dimensional and material inspection'],
        tolerances='Candidate bore/plate datums only; drawing-level tolerances and approved fits remain pending') for p in parts],
        process_plans=dict(frame=['Cut RHS stock, retain real hollow ends','Jig/tack, weld controlled sequence','Inspect welds and machine datums'],
            clevis=['Cut25mm plate and backplate','Bore paired ears in common fixture','Inspect bore coaxiality and ligament dimensions'],
            guidance=['Turn wheels/journals/bushes','Inspect bore/shaft fits and retention features','Grease and check free rotation'],
            guards=['Laser cut3mm sheet and holes','Deburr edges, coat and fit captive attachments']),
        costs=dict(estimated_factory_cost=None,basis='Part-level source quantities/routings are defined; price/labour/tooling/QA must be bound by the coordinator cost adapter, never zero'),
        transactions_performed=False,manufacturing_release=False)


def validate(value):
    if value.get('assembly_definition_id')!=identity({k:v for k,v in value.items() if k!='assembly_definition_id'}):raise ValueError('Assembly record identity differs')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Research assembly cannot grant release')
    expected=build()
    if value!=expected:raise ValueError('Assembly dimensions, quantities, ancestry or interfaces differ from canonical generator')
    return value


def cad_script(value):
    """One actual hollow body per RHS; named material bodies remain separate."""
    validate(value)
    ordinary=[p for p in value['entities'] if p['shape']!='hollow_box']
    case=dict(candidate_id=value['candidate_id'],component_geometry_id=identity(value['entities']),
        case_id=value['case_id'],entities=ordinary,materials=value['materials'],**FLAGS)
    commands=solidcraft.script_for(case)['commands'][:-1]
    for part in value['entities']:
        if part['shape']=='hollow_box':
            size=part['size_m'];at=part['at_m'];axis='xyz'.index(part['hollow_axis']);wall=part['wall_m']
            inner=[n if i==axis else n-2*wall for i,n in enumerate(size)]
            corner=[n if i==axis else n+wall for i,n in enumerate(at)]
            for dimensions,origin,operation in ((size,at,'new'),(inner,corner,'cut')):
                params=dict(zip(('length','width','height'),[x*1000 for x in dimensions]))
                params.update(corner=[x*1000 for x in origin],operation=operation)
                params.update(body_name=part['id']) if operation=='new' else params.update(targets=[part['id']])
                commands.append(dict(command='solid.box',params=params))
            commands.append(dict(command='material.assign',params=dict(bodies=[part['id']],material='OSR '+part['material'])))
            for h in part.get('holes',[]):
                index='xyz'.index(h['axis']);base=at[:];direction=[0,0,0];direction[index]=1
                for i,key in enumerate(('x_m','y_m','z_m')):
                    if i!=index:base[i]+=h.get(key,0.)
                commands.append(dict(command='solid.cylinder',params=dict(radius=h['diameter_m']*500,height=size[index]*1000,
                    base=[x*1000 for x in base],axis=direction,operation='cut',targets=[part['id']])))
        for bore in part.get('blind_bores',[]):
            commands.append(dict(command='solid.cylinder',params=dict(radius=bore['radius_m']*1000,height=bore['length_m']*1000,
                base=[x*1000 for x in bore['base_m']],axis=bore['axis'],operation='cut',targets=[part['id']])))
    commands.append(dict(command='inspect.measure',params={}))
    return dict(commands=commands)


def compare(value,measured,*,exact=False):
    """Unique exact geometric correspondence keeps importer label loss visible."""
    validate(value);expected=value['part_measures'];bodies=deepcopy(measured['bodies'])
    if len(bodies)!=len(expected):raise ValueError('CAD occurrence count differs')
    tolerance=1e-7 if exact else 1e-3
    position=1e-7 if exact else 1e-3
    unused=set(expected);checks=[]
    for body in bodies:
        candidates=[]
        for name in unused:
            e=expected[name]
            if (abs(body['volume_m3']-e['volume_m3'])<=e['volume_m3']*tolerance
                and max(abs(a-b) for a,b in zip(body['center_of_mass_m'],e['centroid_m']))<=position
                and max(abs(a-b) for a,b in zip(body['bbox_m']['min']+body['bbox_m']['max'],e['bounds_m'][0]+e['bounds_m'][1]))<=position):
                candidates.append(name)
        # Native source IDs are authoritative where retained; exact imported
        # generic product labels require a unique geometric correspondence.
        if body['id'] in candidates:candidates=[body['id']]
        if len(candidates)!=1:raise ValueError('CAD material does not uniquely match a physical occurrence: '+body['id'])
        name=candidates[0];unused.remove(name)
        if body.get('closed') is not True or exact and body.get('valid') is not True:raise ValueError('Closed valid material required')
        checks.append(dict(source_part_id=name,native_label=body['id'],
            relative_volume_error=abs(body['volume_m3']-expected[name]['volume_m3'])/expected[name]['volume_m3']))
    return dict(comparison_passed=not unused,occurrences=len(checks),exact_brep=exact,
        native_names_preserved=all(c['native_label']==c['source_part_id'] for c in checks),parts=checks,
        identity_basis='Source IDs where retained; otherwise unique volume/centroid/tight-bounds correspondence',**FLAGS)


def run(output,*,render_image=False):
    """Four bounded native executions, optionally one recorded CAD screenshot.

    Immutable output; no selected-reference, business-system or release writes.
    """
    from . import freecad_reference
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    value=build();source_before=native.digest(__file__)
    request=dict(assembly=value,source_sha256={SOURCE:source_before},toolchain=dict(solidcraft=native.pin('solidcraft')),
        maximum_native_processes=5 if render_image else 4,timeout_s=120,memory_mb=2048,**FLAGS)
    request['evaluation_request_id']=identity(request)
    native.write(output/'request.json',request);native.write(output/'commands.json',cad_script(value))
    gen=output/'generate'
    e=native.run('solidcraft',['run',output/'commands.json','--save',gen/'assembly.sc','--out',gen/'assembly.step',
        '--results','--json-out',gen/'results.json'],gen,read_roots=(output,),timeout_s=120,memory_mb=2048)
    if e['execution']!='executed':raise ValueError('CAD failed; immutable execution retained')
    check={}
    check['generated']=compare(value,solidcraft.parse_measurements(json.loads((gen/'results.json').read_bytes())))
    for extension in ('sc','step'):
        folder=output/('reopen-'+extension)
        e=native.run('solidcraft',['eval',gen/('assembly.'+extension),'--json-out',folder/'measure.json'],folder,
            read_roots=(output,),timeout_s=120,memory_mb=2048)
        if e['execution']!='executed':raise ValueError('CAD reopen failed; execution retained')
        check['reopen_'+extension]=compare(value,solidcraft.parse_measurements(json.loads((folder/'measure.json').read_bytes())))
    ref=freecad_reference.run(gen/'assembly.step',output/'freecad-reference',timeout_s=120,memory_mb=2048)
    if ref['execution']!='completed':raise ValueError('Independent exact STEP execution failed')
    check['independent_step']=compare(value,ref,exact=True)
    if render_image:
        e,replies=native.mcp('solidcraft',[('open',dict(path=str(gen/'assembly.sc'))),
            ('screenshot',dict(path=str(output/'presentation/assembly.png'),view='iso',width=1600,height=1000,grid=False,axes=False))],
            output/'presentation',read_root=output,timeout_s=120,memory_mb=2048)
        native.write(output/'presentation-scope.json',dict(execution=e['execution'],source='Actual generated CAD, no geometry offsets or synthetic product image',
            camera='native fitted isometric',guards_hidden=False,part_bodies=122,**FLAGS))
    if native.digest(__file__)!=source_before:raise ValueError('Assembly source changed during native execution')
    artifacts={str(p.relative_to(output)):native.digest(p) for p in sorted(output.rglob('*')) if p.is_file()}
    result=dict(schema='osr-launch-detail-native/1',candidate_id=value['candidate_id'],
        component_geometry_id=value['component_geometry_id'],assembly_geometry_id=identity(value['entities']),
        evaluation_request_id=request['evaluation_request_id'],checks=check,
        native_geometry_comparison_passed=all(c['comparison_passed'] for c in check.values()),
        located_nominal_material_mass_kg=value['nominal_located_material_mass_kg'],
        installed_mass_bound_kg=value['installed_mass_bound_kg'],artifact_sha256=artifacts,
        source_sha256={SOURCE:source_before},**FLAGS)
    result['evaluation_id']=identity(result);native.write(output/'result.json',result);return result


def verify(output):
    output=Path(output);r=json.loads((output/'result.json').read_bytes());request=json.loads((output/'request.json').read_bytes())
    if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Native result identity differs')
    if r['source_sha256']!={SOURCE:native.digest(__file__)}:raise ValueError('Current assembly source differs')
    validate(request['assembly'])
    if request['evaluation_request_id']!=identity({k:v for k,v in request.items() if k!='evaluation_request_id'}):raise ValueError('Native request identity differs')
    actual={str(p.relative_to(output)):native.digest(p) for p in output.rglob('*') if p.is_file() and p!=output/'result.json'}
    if actual!=r['artifact_sha256']:raise ValueError('Native artifact inventory differs')
    if any(r.get(k) is not False for k in FLAGS):raise ValueError('Research cannot grant acceptance')
    if r['candidate_id']!=request['assembly']['candidate_id'] or r['component_geometry_id']!=request['assembly']['component_geometry_id']:
        raise ValueError('Mixed physical identity')
    value=request['assembly'];checks={}
    checks['generated']=compare(value,solidcraft.parse_measurements(json.loads((output/'generate/results.json').read_bytes())))
    for extension in ('sc','step'):
        checks['reopen_'+extension]=compare(value,solidcraft.parse_measurements(json.loads((output/('reopen-'+extension)/'measure.json').read_bytes())))
    checks['independent_step']=compare(value,json.loads((output/'freecad-reference/result.json').read_bytes()),exact=True)
    if checks!=r['checks']:raise ValueError('Independently recomputed CAD readbacks differ')
    return dict(verified=True,fresh_solve=False,candidate_id=r['candidate_id'],evaluation_id=r['evaluation_id'],**FLAGS)
