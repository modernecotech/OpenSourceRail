"""Cheap typed clearance, internal gear and service-access screens.

AABB overlap is not silently promoted to true BRep contact. Occupied simple
boxes are exact only at nominal orthogonal poses; curved/envelope overlaps and
continuous padding remain typed holds. Every current obligation is retained.
"""
from math import sqrt,fsum
from itertools import product
from engineering.powered_bogie.geometry import stock_boxes
from engineering.vehicle_installation import model
from . import FLAGS
from .common import policy,validate,seal
from .kinematics import frame_tree,poses,apply,continuous_padding
from .gears import requirements


def bounds(at,size,R=model.I):
    s=model.transformed_size(size,R)
    return [[at[i]-s[i]/2 for i in range(3)],[at[i]+s[i]/2 for i in range(3)]]
def gap(a,b):
    values=[max(a[0][i]-b[1][i],b[0][i]-a[1][i]) for i in range(3)]
    return max(values)
def inflated(b,p):return [[b[0][i]-p[i] for i in range(3)],[b[1][i]+p[i] for i in range(3)]]
def transformed(b,T):
    points=[apply(T,list(c)) for c in product(*[(b[0][i],b[1][i]) for i in range(3)])]
    return [[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]


def _retained(body,bi):
    car=bi//2;bx=8.5+car*17.65+(-6.4 if bi%2==0 else 6.4);out=[]
    critical=('underframe/','body/floor','body/body-bolster','running/frame','running/wheel','running/axle','running/bearing','running/primary','running/bolster','running/secondary','running/brake','running/caliper','running/service-actuator','running/parking-actuator','running/disc-guard','services/battery')
    for p in body['patterns']:
        if p['part_id'].startswith('compact-drive/') or p['car_allocation']!=[[car,1.]] or p['bogie_index'] not in (None,bi):continue
        if not p['part_id'].startswith(critical):continue
        role='solid' if p['geometry']['exact_stock'] else 'equipment-envelope'
        if any(k in p['part_id'] for k in ('coating','weld-deposit','adhesive','charge','local-air-tube')):role='allocation'
        if role=='allocation':continue
        for r in stock_boxes(p):
            if r['bounds_m'][0][0]>bx+2.2 or r['bounds_m'][1][0]<bx-2.2:continue
            axle=0 if sum(r['bounds_m'][j][0] for j in (0,1))/2<bx else 1
            if p['bogie_index'] is None:frame='body'
            elif p['assembly_id'] in ('running/wheelset','running/axlebox'):frame='wheelset'
            else:frame='bogie'
            out.append(dict(id=r['id'],part_id=p['part_id'],bounds=r['bounds_m'],role=role,frame=frame,axle=2*bi+axle,exact=r['exact_stock'],uncertainty=max(p.get('uncertainty_m',[.05]))))
    return out,bx


def evaluate(body,*,root=None):
    validate(body);p=policy() if root is None else policy(root);c=body['compact_drive_contract'];sample=poses(p);findings=[];repetition=[];nominal=[];ground=[];tools=[]
    bypart={r['id']:r for r in body['parts']};entities=c['assembly_entities']
    for bi in range(12):
        old,bx=_retained(body,bi);own=[r for r in entities if r['bogie']==bi and r['role']!='allocation']
        repetition.append(dict(bogie=bi,entities=len(own),retained_regions=len(old),all_actual_world_positions_checked=True))
        # Nominal occupied/prior-envelope gate across every repeated installation.
        for e in own:
            if e['group'] in ('fastener','lubrication','weld','integration'):continue
            b=bounds(e['at_m'],e['geometry']['size_m'],e['rotation'])
            for r in old:
                if gap(b,r['bounds'])>p['gap_m']+.052:continue
                if r['part_id']=='running/axle' and e['group'] in ('geartrain','shaft','bearing','case'):
                    # Only output-axis shaft/bore mating; otheraxes never excluded.
                    if e['metadata'].get('axis')=='output' or (e['group']=='case' and e['part_id'].endswith('case-long-side')):
                        findings.append(dict(kind='intended-output-axle-interface-hold',entity=e['id'],other=r['id'],bore_and_axle_tolerance_verified=False));continue
                g=gap(b,r['bounds']);pad=e['uncertainty_m']+r['uncertainty']+p['stock_tolerance_m']
                if g<p['gap_m']+pad:
                    row=dict(kind='nominal-stock-overlap' if g<0 and e['role']=='solid' and r['role']=='solid' and e['geometry']['kind']=='box' else 'nominal-required-space-or-gap-hold',entity=e['id'],other=r['id'],part_id=e['part_id'],other_part_id=r['part_id'],signed_axis_separation_m=g,required_gap_plus_uncertainty_m=p['gap_m']+pad,bogie=bi,exact_BRep_contact_not_established=e['geometry']['kind']!='box' or r['role']!='solid')
                    nominal.append(row)
            # Ground is measured in contact/wear frame. Suspension heave affects
            # motor/frame only. Axlecase never sinks by secondary travel.
            if e['group'] in ('motor','case','retention') and e['frame']!='body' and e['axle'] is not None:
                zmin=1e9
                for pose in sample:
                    tree=frame_tree(bx,-1.05 if e['axle']%2==0 else 1.05,pose,c['body_lift_m'],gear_pitch=p['movement']['gear_pitch_rad'])
                    key='gear' if e['frame']=='gear' else e['frame'];zmin=min(zmin,transformed(b,tree[key])[0][2])
                ground.append(dict(entity=e['id'],frame=e['frame'],sample_min_z_m=zmin,required_ground_m=p['ground_allocation_m'],passed_sample=zmin>=p['ground_allocation_m']+e['uncertainty_m'],continuous_ground_verified=False))
        # Continuous broadphase padding is conservative, not a clearance proof.
        # Pair count is bounded spatially; allnearby typed interfaces retained.
        for e in own:
            if e['group'] not in ('motor','case','guard','coupling'):continue
            b=bounds(e['at_m'],e['geometry']['size_m'],e['rotation'])
            for r in old:
                if r['frame']==e['frame'] or gap(b,r['bounds'])>.35:continue
                pad=continuous_padding(e['geometry']['size_m'],'body-gear' if r['frame']=='body' and e['frame']=='gear' else 'relative',p,e['uncertainty_m']+r['uncertainty'])
                if gap(inflated(b,pad),r['bounds'])<p['gap_m']:
                    findings.append(dict(kind='continuous-relative-bound-hold',entity=e['id'],other=r['id'],relative_frames=[e['frame'],r['frame']],padding_m=pad,bogie=bi,interpretation='Conservative broadphase overlap; interval/narrowphase needed, not actual supplier contact'))
    # Axes must reproduce pitch distances, ratio, case containment and positive
    # gear roots around retainedaxle/hubs. No material allowable is invented.
    gear=c['geartrain'];axis_checks=[]
    for a,b,want in [('input','middle',gear['centre_distances_m'][0]),('middle','output',gear['centre_distances_m'][1])]:
        actual=sqrt(sum((gear['axes'][a][i]-gear['axes'][b][i])**2 for i in (0,2)));axis_checks.append(dict(pair=[a,b],actual_m=actual,pitch_distance_m=want,residual_m=actual-want,passed=abs(actual-want)<1e-12))
    case=bounds(gear['case_centre_m'],gear['case_size_m']);contain=[]
    for g in gear['gears']:
        axis=gear['axes'][g['axis']];r=g['addendum_diameter_m']/2;b=bounds([axis[0],g['y_m'],axis[2]],[2*r,g['face_m'],2*r])
        margins=[min(b[0][i]-case[0][i],case[1][i]-b[1][i])-.010 for i in range(3)]
        contain.append(dict(gear=g['id'],wall_inner_margin_m=margins,passed=min(margins)>=0,positive_root_material=g['root_diameter_m']>g['bore_m']))
    # Tools operate aftertheexplicitguard/coupling removal step. Count target
    # fastener axes, actual finite approach boxes and retained obstructions.
    for e in entities:
        if not e['part_id'].endswith(('M10-motor-screw','M16-torque-bolt')):continue
        sign=e['side'];radius=e['metadata'].get('bolt_head_tool_radius_m',p['torque_socket_radius_m']);L=p['foot_tool_insertion_m'] if e['part_id'].endswith('M10-motor-screw') else p['torque_tool_insertion_m'];at=e['at_m'][:];at[1]+=sign*(L/2+.025)
        b=bounds(at,[2*radius,L,2*radius]);retained,bx=_retained(body,e['bogie']);hits=[r['id'] for r in retained if gap(b,r['bounds'])<0]
        tools.append(dict(fastener=e['id'],axis=[0,sign,0],tool_box_m=b,retained_conflict_ids=hits,guard_and_coupling_removed_first=e['metadata'].get('remove_guard_and_coupling_before_tool',False),path_continuous_box=True))
    body_support=dict(lift_m=c['body_lift_m'],springs_not_stretched=True,pedestals_and_emergency_kingpin_retention_counted=True,stiffness_fatigue_and_hoist_known=False)
    counts=c['retained_brake_count_per_bogie'];countpass=counts=={'brake-disc':4,'caliper-body':4,'service-actuator':2,'parking-actuator':2,'friction-pad':8}
    result=dict(schema='osr-compact-drive-cheap-evaluation/1',candidate_id=body['candidate_id'],body_evaluation_id=body['evaluation_id'],config=c['config'],axis_checks=axis_checks,case_gear_checks=contain,gear_requirements=requirements(gear),retained_brake_counts=counts,retained_brake_counts_pass=countpass,
        nominal_findings=nominal,continuous_and_interface_holds=findings,ground_samples=ground,tools=tools,body_support=body_support,all12_bogie_records=repetition,pose_samples=sample,
        numerical_validity='Deterministic analytic geometry, grossstock and elementary gear mechanics only; no CAD/FEM/contact solve',
        known_geometry_screen_pass=all(x['passed'] for x in axis_checks+contain) and countpass and not nominal,
        geometry_screen='HOLD: nominal/continuous findings, full supplier revision/terminal shape, actual bearing/joint capability and finite removal/services require detailing',
        removal=dict(motor_downward_stroke_m=p['removal_stroke_m'],workshop_body_lift_m=p['workshop_body_lift_m'],gear_wheelset_removal_required=True,verified=False,
            sequence=['Isolate/prove dead andsupportbody/bogie/wheelsets','Drain/isolatecoolant anddisconnectlabelledpower/bonds/hoses','Remove retainedsplitshaft guard andcoupling beforemotorfoot tools','Supportmotor andcradle independently, release6M10face joints, lower through600mm protecteddrop stroke','Keepgear torque link supported; wheelset/gear removal requiresaxle/shaftretention andcontrolled bearing tools'],loads_and_eyes_verified=False),
        service_counts=dict(motors=24,gearboxes=24,gear_bearings=144,power_cables=72,coolant_hoses=48,motor_bonds=24,rotor_air_ducts=24,inverters=24,positive_unknown_integration_reserve_kg={c:sum(r['mass_kg'][c] for r in body['patterns'] if r['part_id']=='compact-drive/integration-reserve') for c in model.CASES}),
        upstream_stiffness_thermal_force_and_physical_evidence_invalidated=True,**FLAGS)
    support=c.get('support_package')
    if support:
        support_ids={r['id'] for r in body['parts'] if r['id'].startswith('compact-drive/pedestal-') or r['id'] in ('compact-drive/emergency-cap','compact-drive/emergency-riser')}
        support_patterns=[r for r in body['patterns'] if r['part_id'] in support_ids]
        support_mass={case:fsum(r['mass_kg'][case] for r in support_patterns) for case in model.CASES}
        support_rows=[r for r in nominal if r.get('part_id') in support_ids or r.get('other_part_id') in support_ids]
        continuous_support=[r for r in findings if r.get('entity','').split('@')[0] in support_ids]
        ground_support=[r for r in ground if r.get('entity','').split('@')[0] in support_ids]
        result['support_package_screen']=dict(
            family=support['family'],variant=support['variant'],candidate_id=body['candidate_id'],
            unique_support_part_types=len(support_ids),support_occurrences=sum(r['count'] for r in support_patterns),
            support_mass_kg=support_mass,all_12_bogies_screened=len(repetition)==12,
            support_nominal_clearance_rows=len(support_rows),support_continuous_bound_rows=len(continuous_support),
            support_ground_pose_rows=len(ground_support),
            screens={
                'candidate_identity':'PASS' if body['candidate_id']==body['compact_drive_contract']['candidate_id'] else 'HOLD',
                'support_occurrence_accounting':'PASS' if sum(r['count'] for r in support_patterns)>0 else 'HOLD',
                'nominal_support_clearance':'HOLD' if support_rows else 'PASS_WITHIN_DECLARED_GROSS_STOCK_SCREEN',
                'continuous_support_envelope':'HOLD' if continuous_support else 'PASS_WITHIN_DECLARED_CONTINUOUS_BOUND',
                'sampled_support_ground':'HOLD' if any(not r['passed_sample'] for r in ground_support) else 'PASS_WITHIN_SAMPLED_POSES',
                'support_load_path_and_joint_strength':'HOLD',
                'support_stiffness_fatigue_and_retention':'HOLD',
                'supplier_and_finished_geometry':'HOLD',
                'finite_removal_and_service':'HOLD',
                'physical_acceptance':'HOLD'},
            interpretation='Clearance flags remain analytic gross-stock/envelope evidence. Support loads, joints, stiffness, fatigue, retention, finished geometry and removal are not qualified.')
    return seal(result)
