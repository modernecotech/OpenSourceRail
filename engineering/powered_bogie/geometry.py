"""Necessary-space checks with rigid frames and conservative swept boxes.

An overlap with an unverified equipment box is a space-allocation conflict,
not proof of contact between actual supplier housings. A non-overlap is useful
only within the declared box and movement domain, never supplier admission.
"""
from copy import deepcopy
from itertools import product
from math import sin, cos, sqrt, fsum, pi, prod

from engineering.station_rail.common import identity
from engineering.vehicle_installation import model
from . import FLAGS


def box(centre,size):
    return [[centre[i]-size[i]/2 for i in range(3)],
            [centre[i]+size[i]/2 for i in range(3)]]


def overlap(a,b,tolerance=0.):
    return [min(a[1][i],b[1][i])-max(a[0][i],b[0][i])+tolerance for i in range(3)]


def intersects(a,b,tolerance=0.):
    return all(x>1e-10 for x in overlap(a,b,tolerance))


def corners(b):
    return [[b[j][i] for i,j in enumerate(sign)] for sign in product((0,1),repeat=3)]


def envelope(points):
    return [[min(x[i] for x in points) for i in range(3)],
            [max(x[i] for x in points) for i in range(3)]]


def stock_boxes(pattern):
    """Hollow RHS is four occupied disjoint walls, never a filled outer box."""
    g=pattern['geometry'];stock=g['source_stock'];R=pattern['rotation']
    size=g['size_m'];pieces=[(size,[0.,0.,0.])]
    if stock and stock['kind']=='rhs':
        L,b,h=size;t=stock['wall_m'];pieces=[]
        for sign in (-1,1):
            pieces += [([L,t,h],[0.,sign*(b-t)/2,0.]),
                       ([L,b-2*t,t],[0.,0.,sign*(h-t)/2])]
    out=[]
    for n,c in enumerate(pattern['positions_m']):
        for w,(s,o) in enumerate(pieces):
            centre=[c[i]+fsum(R[i][j]*o[j] for j in range(3)) for i in range(3)]
            bounds=box(centre,model.transformed_size(s,R))
            out.append(dict(id=pattern['id']+f'/{n}/wall-{w}',part_id=pattern['part_id'],
                bounds_m=bounds,exact_stock=g['exact_stock'],
                basis=g['definition_basis'],finished_profile_cut_unapplied='finished_profile_xz_m' in g))
    return out


def transform_point(point,origin,yaw,roll,jounce):
    """T_track_bogie = translation(origin) Rz(yaw) Rx(roll), Z-up SI."""
    x,y,z=[point[i]-origin[i] for i in range(3)]
    y,z=cos(roll)*y-sin(roll)*z,sin(roll)*y+cos(roll)*z
    return [origin[0]+cos(yaw)*x-sin(yaw)*y,
            origin[1]+sin(yaw)*x+cos(yaw)*y,origin[2]+z+jounce]


def rigid_transform(origin,yaw,roll,jounce):
    cy,sy,cr,sr=cos(yaw),sin(yaw),cos(roll),sin(roll)
    R=[[cy,-sy*cr,sy*sr],[sy,cy*cr,-cy*sr],[0.,sr,cr]]
    t=[origin[i]-sum(R[i][j]*origin[j] for j in range(3)) for i in range(3)]
    t[2]+=jounce
    return [[*R[i],t[i]] for i in range(3)]+[[0.,0.,0.,1.]]


def continuous_bound(bounds,origin,movement,*,gear=False):
    """Lipschitz superset for every yaw/roll/jounce inside declared bounds.

    Rotation displacement <= radius*|angle|. Triangle inequality remains safe
    for composed yaw/roll. Enlarging an occupied wall can overpredict contact;
    overlap therefore stays unresolved instead of becoming a false failure.
    """
    pts=corners(bounds)
    r=max(sqrt(sum((v[i]-origin[i])**2 for i in range(3))) for v in pts)
    rr=max(sqrt((v[1]-origin[1])**2+(v[2]-origin[2])**2) for v in pts)
    theta=movement['roll_rad']+(movement['relative_gear_roll_rad'] if gear else 0.)
    yaw=movement['yaw_rad'];jounce=(movement['secondary_jounce_m']+
        (movement['primary_jounce_m'] if gear else 0.))
    delta=[r*(yaw+theta)+movement['lateral_m'],
           r*(yaw+theta)+movement['lateral_m'], rr*theta+jounce]
    return [[bounds[0][i]-delta[i] for i in range(3)],
            [bounds[1][i]+delta[i] for i in range(3)]]


def _category(pattern):
    name=pattern['part_id']
    if name.startswith('powered-bogie/'):
        return 'new-frame-or-mount' if pattern['geometry']['exact_stock'] else None
    if pattern['assembly_id']=='running/bogie-frame':
        return 'retained-frame' if pattern['geometry']['exact_stock'] else None
    if name in ('running/brake-disc','running/caliper-body','running/service-actuator',
                'running/parking-actuator','running/caliper-bracket','running/wheel'):
        return 'wheel-or-brake'
    if pattern['assembly_id']=='services/battery':return 'battery'
    if name.startswith('underframe/') or name in ('body/floor-crossmember','body/body-bolster'):
        return 'body-underframe'
    if name=='running/bolster-main-rhs':return 'retained-secondary-bolster'
    return None


def evaluate(result):
    if result['candidate_id']!=identity(result['physical_definition']):
        raise ValueError('Geometry must use the sealed candidate')
    p=result['physical_definition']['proposal'];m=p['movement'];origin=[2.1,0.,.53]
    # First left bogie/first car is sufficient only because all twelve use
    # identical counted transforms. Body extremes and fixed service pods are
    # copied from this actual counted car, not a free-space assumption.
    keepouts=[]
    for pattern in result['patterns']:
        if pattern['car_allocation']!=[[0,1.]]:continue
        if pattern['bogie_index'] not in (None,0):continue
        category=_category(pattern)
        if category is None:continue
        for row in stock_boxes(pattern):
            if row['bounds_m'][0][0]>4.0 or row['bounds_m'][1][0]<-.2:continue
            row['category']=category;keepouts.append(row)
    checked=[];poses=[]
    for sy,sr,sj in product((-1,0,1),(-1,1),(-1,1)):
        yaw,roll,jounce=sy*m['yaw_rad'],sr*m['roll_rad'],sj*m['secondary_jounce_m']
        poses.append(dict(yaw_rad=yaw,roll_rad=roll,jounce_m=jounce,
                          T_track_bogie=rigid_transform(origin,yaw,roll,jounce)))
    if len(poses)>p['limits']['maximum_poses_per_variant']:
        raise ValueError('Pose budget exceeded')
    for e in result['external_drive_placements'][:2]:
        nominal=box(e['centroid_m'],e['size_m'])
        swept=continuous_bound(nominal,origin,m,gear=e['hardware']!='motor')
        nominal_conflicts=[];sweep_holds=[];relative_holds=[]
        relative=dict(m,yaw_rad=0.,roll_rad=0.,secondary_jounce_m=0.)
        relative_swept=continuous_bound(nominal,origin,relative,gear=True) if e['hardware']!='motor' else nominal
        for other in keepouts:
            # Axle bore/coupling is intended and separately recorded. Brake,
            # bolster and frame intersections are never excluded as mating.
            if intersects(nominal,other['bounds_m'],p['clearance']['stock_tolerance_m']):
                nominal_conflicts.append(dict(**other,overlap_m=overlap(nominal,other['bounds_m']),
                    interpretation='Required-space conflict; actual housing/contact unknown'))
            if other['category'] in ('body-underframe','battery') and intersects(swept,other['bounds_m']):
                sweep_holds.append(dict(**other,interpretation='Continuous swept-box overlap; narrow-phase proof required'))
            if other['category'] in ('new-frame-or-mount','retained-frame','retained-secondary-bolster') and intersects(relative_swept,other['bounds_m']):
                relative_holds.append(dict(**other,interpretation='Gear/primary movement versus frame and mounts is not resolved'))
        # Every sample must lie inside the analytic superset. This is a bound
        # integrity test, not a sampled-only collision clearance assertion.
        sample_bounds=[]
        for pose in poses:
            sample=envelope([transform_point(v,origin,pose['yaw_rad'],pose['roll_rad'],pose['jounce_m']) for v in corners(nominal)])
            if any(sample[0][i]<swept[0][i]-1e-10 or sample[1][i]>swept[1][i]+1e-10 for i in range(3)):
                raise ValueError('Continuous bound does not enclose sample')
            sample_bounds.append(sample)
        checked.append(dict(hardware=e['hardware'],nominal_box_m=nominal,
            continuous_swept_outer_box_m=swept,poses_checked=len(poses),sample_boxes_m=sample_bounds,
            required_space_conflicts=nominal_conflicts,continuous_body_or_battery_holds=sweep_holds,
            relative_frame_swept_outer_box_m=relative_swept,relative_frame_swept_holds=relative_holds,
            minimum_ground_z_m=swept[0][2],
            ground_allocation_satisfied=swept[0][2]>=p['clearance']['bogie_ground_allocation_m'],
            actual_hardware_fit_status='HOLD-supplier-dimensions-and-mating-interfaces-unknown'))
    motor=checked[0]['nominal_box_m'];drop=deepcopy(motor);drop[0][2]-=p['clearance']['motor_downward_removal_m']
    tool=[]
    for pattern in result['patterns']:
        if pattern['bogie_index']!=0 or pattern['part_id']!='powered-bogie/M20-retained-bolt':continue
        for at in pattern['positions_m']:
            size=[2*p['clearance']['tool_socket_radius_m']]*2+[p['clearance']['tool_insertion_m']]
            centre=[at[0],at[1],at[2]+size[2]/2]
            bounds=box(centre,size)
            tool.append(dict(centre_m=centre,box_m=bounds,
                drive_envelope_conflict=any(intersects(bounds,r['nominal_box_m']) for r in checked),
                stock_or_body_conflict_ids=[k['id'] for k in keepouts if intersects(bounds,k['bounds_m'])],
                access_verified=False))
    services=[]
    for name,length,radius,body_at,moving_at in (
        ('power',p['services']['power_cable_length_m'],p['services']['power_cable_min_bend_radius_m'],[2.35,-.60,.82],[1.62,-.58,.48]),
        ('ventilation',p['services']['air_duct_length_m'],p['services']['air_duct_min_bend_radius_m'],[2.35,-.48,.82],[1.62,-.48,.58])):
        straight=sqrt(sum((body_at[i]-moving_at[i])**2 for i in range(3)))
        r=sqrt(sum((moving_at[i]-origin[i])**2 for i in range(3)))
        travel=r*(m['yaw_rad']+m['roll_rad'])+m['secondary_jounce_m']+m['lateral_m']
        necessary=straight+travel+pi*radius
        services.append(dict(service=name,fixed_body_anchor_m=body_at,bogie_anchor_m=moving_at,
            straight_separation_m=straight,continuous_endpoint_travel_bound_m=travel,
            minimum_bend_radius_m=radius,declared_cut_length_m=length,
            necessary_length_with_one180deg_loop_m=necessary,length_margin_m=length-necessary,
            necessary_length_screen=length>=necessary,
            route_and_terminal_clash_verified=False,thermal_or_ampacity_verified=False,
            scope='Conservative endpoint travel plus explicit half-circle loop only; routed finite hose/cable volume and connector rotation remain open'))
    clearances=dict(schema='osr-powered-bogie-geometry-evaluation/1',candidate_id=result['candidate_id'],
        body_evaluation_id=result['evaluation_id'],input_policy_id=identity(p),
        coordinate_frames=dict(track='x forward, y left, z up; railheadz0',
            bogie_origin_m=origin, T_track_bogie_nominal=rigid_transform(origin,0.,0.,0.),
            gear_relative_frame='Driven axle x=-1.05m; primary travel and gear roll enlarge the continuous bound',
            frame_supports='Existing primary spring/axlebox anchors and body secondary x=0 remain fixed'),
        samples=poses,continuous_domain=m,drives=checked,
        scope='First repeated bogie against actual counted car0 underframe/battery and retained wheel/brake stock/envelopes. Analytic bounding boxes can overpredict collision. Actual tread, housings, bearings, motion and contact are unverified.',
        intended_interfaces=[dict(name='gear-output-to-driven-axle',at_m=[1.05,.48,.38],
            status='Bore, keys/interference, axle fatigue and retention unknown;310kg parent owns output bearings'),
            dict(name='motor-to-toothed-coupling-to-gear',at_m=[1.62,.335,.40],
                 status='Coupling angular/radial/axial capacity and actual shafts unknown; mass inside310kg'),
            dict(name='motor-foot-to-removable-cradle',status='Eight M20 proposals counted; manufacturer hole pattern, foot loads and tool access unknown'),
            dict(name='gear-to-frame-torque-reaction',status='Two proposed bush/link plates, four M20 fasteners; manufacturer attachment unknown')],
        joins_and_services=dict(per_bogie=dict(motor_foot_M20_bolts=8,gear_torque_M20_bolts=4,
            M20_locknuts=12,M20_washers=24,retention_M12_sets=4,
            clamp_M6_sets=8,torque_bushes=2,retention_stops=2,
            toothed_couplings_in_310kg=1,gear_internal_bearings_in_310kg=2,
            retained_wheelset_bearings=4,slides=0,power_cables=3,power_cable_m=7.2,
            bonding_braids=2,bonding_m=2.4,ventilation_ducts=1,duct_m=1.4),
            flexibility=services,
            coupling_motion=dict(primary_vertical_travel_m=m['primary_jounce_m'],
                angular_misalignment_hypothesis_rad=m['relative_gear_roll_rad'],
                lateral_motion_hypothesis_m=m['lateral_m'],supplier_capability_known=False),
            count_basis='New revision only; retained original bogie fasteners/brakes/secondary suspension stay in original counted body. Retained control has no new mount hardware.'),
        maintenance=dict(motor_removal_swept_box_m=drop,removal_path_verified=False,
            requires_workshop_drop_table=True,tool_proposals=tool,
            nominal_body_lift_m=p['clearance']['body_lift_for_drop_m'],
            single_motor_static_mass_kg=486.,motor_lifting_design_load_kg=486.*1.30,
            declared_workshop_hoist_WLL_kg=1000.,hoist_and_lifting_eyes_verified=False,
            operations=['Isolate supply, discharge DC link, prove dead, secure body and both wheelsets',
                'Lift/support car by declared0.45m in controlled workshop; disconnect identified power/bond/air interfaces',
                'Lower bogie on rated drop table; remove retained guards and inspect access before releasing drive fasteners',
                'Support486kg motor and cradle independently; remove M20 joints and retention straps with counted nuts/washers',
                'Lower motor through0.60m finite stroke; check actual shaft disengagement and tool path before any physical lift',
                'Gear is axle mounted: remove driven wheelset as an assembly. Axle/gear separation requires controlled press/shaft tooling and supplier drawing',
                'Repair or replace accessible plates/retainers, inspect welds/bushes, restore torque/locking, insulation/bond and datum records'],
            repair_limits='No field cutting of loaded frame or unapproved drive lifting eyes; enclosure and path proposals remain held'),
        supplier_and_profile_gates=dict(OSR_new_worn_m=[.760,.680],catalogue_new_worn_m=[.840,.716],
            catalogue_matches_OSR_wear_domain=False,
            possible_research_maintenance_hypothesis_m=[.716,.760],
            stricter_research_wear_limit_selected=False,
            wear_rate_or_renewal_life_inferred=False,
            open=['Manufacturer dimensioned housing, foot/torque reaction and axle-interface drawings',
                  'Worn-wheel clearance, speed/ratio and actual motor cooling/thermal duty',
                  'Coupling misalignment, gear lubrication, bearing and shaft retention',
                  'Frame/mount strength, fatigue, weld access/NDT and damage tolerance',
                  'Primary/secondary suspension dynamics, brake interfaces and full body swept clearance']),
        geometry_screen_status='HOLD-required-space-conflicts-and-unverified-supplier-interfaces',
        source_sha256=result['source_sha256'],**FLAGS)
    clearances['evaluation_id']=identity(clearances)
    return clearances


def stock_case(result):
    """One regenerated crossmember/cradle subset; no supplier shape implied."""
    chosen={'powered-bogie/side-rhs','powered-bogie/transom-rhs',
            'powered-bogie/end-tie','powered-bogie/motor-cradle-plate',
            'powered-bogie/motor-vertical-cheek','powered-bogie/motor-outrigger-rhs',
            'powered-bogie/torque-arm-plate','powered-bogie/retention-strap'}
    entities=[];measures={}
    materials={r['id']:r for r in result['materials']}
    for pattern in result['patterns']:
        if pattern['bogie_index']!=0 or pattern['part_id'] not in chosen:continue
        for row in stock_boxes(pattern):
            bounds=row['bounds_m'];size=[bounds[1][i]-bounds[0][i] for i in range(3)]
            entity=dict(id=row['id'],shape='box',at_m=bounds[0],size_m=size,material=pattern['material_id'])
            entities.append(entity);measures[row['id']]=dict(volume_m3=prod(size),
                centroid_m=[(bounds[0][i]+bounds[1][i])/2 for i in range(3)],bounds_m=bounds)
    return dict(schema='osr-installation-stock-cad-case/1',case_id='powered-bogie-counted-stock',
        candidate_id=result['candidate_id'],component_geometry_id=identity(dict(entities=entities,units='m')),
        entities=entities,materials=materials,expected=dict(part_count=len(entities),part_measures=measures),
        scope='One powered-bogie gross-stock subset. RHS voids explicitly open; bolt holes, welds, real supplier housings and qualifying strength are outside this exact-volume check.',**FLAGS)
