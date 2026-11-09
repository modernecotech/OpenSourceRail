"""SOURCE-only chair/P6 counterpart and new drilling-family proposals.

Nothing invokes the frozen P1 chair producer, P6 adaptation, a body composer or
native tools. These pure records are not an installed candidate. Actual use
requires exact authenticated inputs and a separately reviewed definition trial.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from math import fsum, isfinite, pi, prod, sqrt

P1 = dict(physical_id='5a3a6cd74fd33ab6d85e0a264afc899a5fff319e16e7fd94189637a6bfba44f3',
          evaluation_id='d1339473c06dd9dc5a6187b9aed70aa025b4a0c0d2caa33ccd430a939f28f9ea',
          raw_sha256='f639405395242bd5987651a1e61a8a7fd4264cf23f2a5494825ca495381c4b23')
P6 = dict(physical_id='ce1b8b222b06a6479f7738d9409d74a5333514b79b7baf5dffc7c8510b73e044',
          evaluation_id='8fffa3254dab9b737e8785de7d781325dde3cec028a89b14a3e8371b04cc6289',
          raw_sha256='3984b2a7ad9966b8d74fec2da9d0530cea66d3557071e964816f55fefebb9df5')
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
REAR=[[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.]]
HEADER_R=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,selected_reference_changed=False,movement_authority=False,
           native_evaluator_admitted=False,installed_mass_complete=False)
OLD_PARTS=tuple('body/chair-'+n for n in ('base','frame','pan','back','cushion','upholstery','armrest',
    'anchor-track','anchor-bolt','anchor-nut','anchor-washer','shell-bolt','shell-nut','shell-washer'))


def encoded(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(x):return sha256(encoded(x)).hexdigest()


def _number(x,positive=False):
    if type(x) not in (int,float) or not isfinite(x) or (positive and x<=0):raise ValueError('Finite nonboolean SI scalar required')
    return float(x)


def _vector(x):
    if not isinstance(x,(list,tuple)) or len(x)!=3:raise ValueError('Three SI coordinates required')
    return [_number(v) for v in x]


def _digest(x):
    if not isinstance(x,str) or len(x)!=64 or any(c not in '0123456789abcdef' for c in x):raise ValueError('Exact source identity required')


def _near(a,b):return len(a)==len(b) and all(abs(_number(x)-_number(y))<=1e-9 for x,y in zip(a,b))


def _rotation(R):
    if not isinstance(R,list) or len(R)!=3:raise ValueError('Proper rotation required')
    for row in R:_vector(row)
    if any(abs(sum(R[k][i]*R[k][j] for k in range(3))-float(i==j))>1e-10 for i in range(3) for j in range(3)):raise ValueError('Proper rotation required')
    a=R;det=a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
    if abs(det-1)>1e-10:raise ValueError('Reflection is not rear-bogie rotation')
    return R


def transform(p,T,R):
    p=_vector(p);T=_vector(T);_rotation(R)
    return [T[i]+sum(R[i][j]*p[j] for j in range(3)) for i in range(3)]


def authenticated_record(raw,pin,*,physical_key='candidate_id',evaluation_key='evaluation_id'):
    if not isinstance(raw,bytes) or set(pin)!={'physical_id','evaluation_id','raw_sha256'}:raise ValueError('Exact immutable raw input/pin required')
    for v in pin.values():_digest(v)
    if sha256(raw).hexdigest()!=pin['raw_sha256']:raise ValueError('Raw input differs')
    value=json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
    if value.get(physical_key)!=pin['physical_id'] or value.get(evaluation_key)!=pin['evaluation_id']:raise ValueError('Physical/evaluation identity differs; same CID is insufficient')
    if 'physical_definition' in value and identity(value['physical_definition'])!=pin['physical_id']:raise ValueError('Physical definition differs')
    return value


def placements(layout):
    cars=layout.get('cars')
    if type(cars) is not int or not 1<=cars<=6:raise ValueError('Explicit bounded car count required')
    if not _near([layout['car_length_m'],layout['intercar_gap_m']],[17.,.65]) or not _near(layout['bogie_centres_local_x_m'],[-6.4,6.4]):raise ValueError('Unreviewed formation/placement domain')
    return [dict(car=car,bogie=label,translation_m=[car*17.65+8.5+x,0.,0.],rotation=deepcopy(R),extra_body_lift_m=0.)
            for car in range(cars) for label,x,R in [('front',-6.4,I),('rear',6.4,REAR)]]


def component_physical(c):
    return {k:deepcopy(c[k]) for k in ('id','geometry','at_m','rotation','frame','material_id')}


def header_templates(components):
    """Exact local header/cap/weld/cleat/central-diaphragm references, no adapter."""
    by={c['id']:c for c in components}
    if len(by)!=len(components):raise ValueError('Duplicate source component')
    headers=[c for c in components if c['id'].startswith('header/')]
    expected={f'header/{side}/{hx}' for side in (-1,1) for hx in (-.4,.5)}
    if {h['id'] for h in headers}!=expected:raise ValueError('Exactly four canonical source headers required')
    out=[]
    for h in sorted(headers,key=lambda h:h['id']):
        _,side,hx=h['id'].split('/');side=int(side);hx=float(hx);g=h['geometry']
        _rotation(h['rotation'])
        if (h['frame']!='body' or h['material_id']!='body/al5083' or set(g)!={'kind','size_m','wall_m'} or g['kind']!='rhs' or
            not _near(g['size_m'],[.7285,.120,.180]) or abs(_number(g['wall_m'])-.008)>1e-10 or h['rotation']!=HEADER_R or
            not _near(h['at_m'],[hx,side*.72575,1.0195])):raise ValueError('Changed/unreviewed actual header geometry or datum')
        welds=[c for c in components if c['id'].startswith('p6/endcap-weld/') and h['id'] in c.get('metadata',{}).get('declared_parent_ids',[])]
        if len(welds)!=1:raise ValueError('Exact actual endcap weld ownership required')
        w=welds[0];caps=[by[x] for x in w['metadata']['declared_parent_ids'] if x!=h['id'] and x in by]
        if len(caps)!=1:raise ValueError('One actual endcap required')
        c=caps[0]
        _rotation(c['rotation']);_rotation(w['rotation'])
        if c['frame']!='body' or c['rotation']!=I or not _near(c['at_m'],[hx,side*1.094,1.0195]) or c['geometry']!={'kind':'box','size_m':[.12,.008,.18]}:raise ValueError('Unreviewed endcap')
        path=[[hx-.06,side*1.09,.9295],[hx+.06,side*1.09,.9295],[hx+.06,side*1.09,1.1095],[hx-.06,side*1.09,1.1095],[hx-.06,side*1.09,.9295]]
        if w['frame']!='body' or w['rotation']!=I or not _near(w['at_m'],[0.,0.,0.]) or w['geometry'].get('kind')!='route' or abs(_number(w['geometry'].get('radius_m'))-.004)>1e-10 or len(w['geometry'].get('path_m',[]))!=5 or any(not _near(a,b) for a,b in zip(w['geometry']['path_m'],path)):raise ValueError('Actual cap/weld geometry changed')
        cleats=[x for x in components if x['id'].startswith('retained/underframe/crossmember-joint-cleat') and abs(x['at_m'][0]-hx)<1e-8 and x['at_m'][1]*side>0]
        diaphragms=[x for x in components if x['id'].startswith('retained/underframe/internal-diaphragm') and abs(x['at_m'][0]-hx)<1e-8]
        if len(cleats)!=1 or len(diaphragms)!=1:raise ValueError('Explicit retained cleat and separate central diaphragm required')
        cleat,diaphragm=cleats[0],diaphragms[0]
        _rotation(cleat['rotation']);_rotation(diaphragm['rotation'])
        if not _near(cleat['geometry']['size_m'],[.2,.01,.18]) or not _near(cleat['at_m'],[hx,side*.33,1.0195]) or cleat['rotation']!=I or cleat['frame']!='body':raise ValueError('Changed source cleat')
        if not _near(diaphragm['geometry']['size_m'],[.008,.63,.32]) or not _near(diaphragm['at_m'],[hx,0.,.9395]) or diaphragm['rotation']!=I or diaphragm['frame']!='body':raise ValueError('Changed central diaphragm')
        gap=abs(h['at_m'][1])-g['size_m'][0]/2-(abs(cleat['at_m'][1])+.005)
        out.append(dict(header=deepcopy(h),endcap=deepcopy(c),endcap_weld=deepcopy(w),cleat=deepcopy(cleat),central_diaphragm=deepcopy(diaphragm),
            header_to_cleat_gap_m=gap,source_record_ids={x['id']:identity(x) for x in (h,c,w,cleat,diaphragm)},
            physical_template_id=identity([component_physical(x) for x in (h,c,w,cleat,diaphragm)])))
    return out


def map_headers(templates,layout,stub_patterns,*,p1_physical_id,p6_pin):
    _digest(p1_physical_id)
    if p1_physical_id!=P1['physical_id']:raise ValueError('Exact P1 physical source required')
    if p6_pin!=P6:raise ValueError('Exact8fff/3984 P6 evaluation required; no3202/b863 substitution')
    if len(templates)!=4:raise ValueError('All source header templates required')
    members={}
    for t in templates:
        for key in ('header','endcap','endcap_weld','cleat','central_diaphragm'):
            c=t[key]
            if t['source_record_ids'].get(c['id'])!=identity(c) or (c['id'] in members and identity(members[c['id']])!=identity(c)):raise ValueError('Mixed/stale source mate epoch')
            members[c['id']]=c
        if t['physical_template_id']!=identity([component_physical(t[k]) for k in ('header','endcap','endcap_weld','cleat','central_diaphragm')]):raise ValueError('Source template physical identity differs')
    header_templates(list(members.values()))
    out=[];retired=set()
    for placement in placements(layout):
        patterns=[p for p in stub_patterns if p['car_allocation']==[[placement['car'],1.]]]
        if len(patterns)!=1:raise ValueError('One exact source stub pattern per car required')
        pattern=patterns[0]
        if (pattern.get('part_id')!='underframe/floor-crossmember-stub' or pattern.get('material_id')!='body/al6005a' or
            pattern.get('count')!=len(pattern['positions_m']) or pattern.get('rotation')!=HEADER_R or
            pattern.get('geometry',{}).get('kind')!='rhs' or not _near(pattern['geometry']['size_m'],[.7835,.100,.180]) or
            abs(_number(pattern['geometry'].get('source_stock',{}).get('wall_m'))-.006)>1e-10):raise ValueError('Exact original100mm stub ownership/geometry required')
        _rotation(pattern['rotation'])
        if any(abs(abs(_vector(p)[1])-.75325)>1e-8 or abs(p[2]-1.0195)>1e-8 for p in pattern['positions_m']):raise ValueError('Changed P1 stub pose')
        for t in templates:
            h=t['header'];at=transform(h['at_m'],placement['translation_m'],placement['rotation'])
            matches=[(i,p) for i,p in enumerate(pattern['positions_m']) if abs(p[0]-at[0])<1e-8 and p[1]*at[1]>0]
            if len(matches)!=1:raise ValueError('Unique exact old100mm source stub required')
            index,old=matches[0];key='source/'+identity([p1_physical_id,pattern['id'],index])
            if key in retired:raise ValueError('Source stub retired twice')
            retired.add(key)
            out.append(dict(instance_id=f'P6/car{placement["car"]}/{placement["bogie"]}',placement=deepcopy(placement),template=deepcopy(t),
                world_header_center_m=at,old_stub=dict(source_key=key,pattern_id=pattern['id'],index=index,pattern_record_id=identity(pattern),position_m=deepcopy(old)),
                source_p6=deepcopy(p6_pin),additional_lift_m=0.,old_stub_retirement_owner='Canonical P6 replacement map only; chair must not credit this stock again'))
    if len(out)!=8*layout['cars']:raise ValueError('Incomplete counterpart mapping')
    return out


def necessary_anchor_gap(depth,distance):
    depth=_number(depth,True);distance=_number(distance,True)
    if depth not in (.100,.120):raise ValueError('Explicit100/120mm counterpart only')
    gap=distance-.010-depth/2-.010-.003
    return dict(gap_m=gap,required_m=.005,residual_m=gap-.005,necessary_passed=gap>=.005-1e-10,
        hypothesis='Plan gap floor10mm halfbacker, actual counterpart halfdepth,10mm plate,3mm own weld halo; no clearance waiver',qualified=False)


def node_hardware(depth):
    depth=_number(depth,True)
    if depth not in (.100,.120):raise ValueError('Explicit100/120mm hardware domain required')
    grip=depth+.021;bolt=depth+.040;projection=bolt-2*.0016-grip-.0065
    if abs(projection-.0093)>1e-10:raise ValueError('Incomplete node stack')
    return dict(sleeve_length_m=depth,M8_underhead_length_m=bolt,grip_m=grip,nominal_thread_projection_m=projection,
        head_washer_m=.0016,nut_washer_m=.0016,nut_m=.0065,cap_wall_length_m=.016,
        sleeve_count=2,bolt_count=2,nut_count=2,washer_count=4,qualified=False)


def node_proposal(mapped,lane_y,anchor_distance,*,connected_sides,reviewed_joint_id,unresolved_interfaces):
    """Local120mm drilling/hardware proposal; never inherits P1 installation."""
    if unresolved_interfaces:raise ValueError('Unresolved source mating interfaces must be revised first')
    _digest(reviewed_joint_id)
    if mapped.get('source_p6')!=P6:raise ValueError('Wrong actual P6 source epoch')
    if not connected_sides or set(connected_sides)-{'left','right'} or len(set(connected_sides))!=len(connected_sides):raise ValueError('Explicit node joint sides required')
    bound=necessary_anchor_gap(.120,anchor_distance)
    if not bound['necessary_passed']:raise ValueError('120mm necessary weld/backer gap below unchanged5mm; new row/joint definition required')
    lane_y=_number(lane_y);center=mapped['world_header_center_m'];side=1 if center[1]>0 else -1
    if not any(abs(lane_y-side*v)<1e-8 for v in (.8075,1.0725)):raise ValueError('Unsupported actual bridge lane')
    x=center[0];column=lane_y-side*.040;t=mapped['template'];h=t['header'];placement=mapped['placement']
    R=placement['rotation'];T=placement['translation_m'];H=h['rotation']
    total=[[sum(R[i][k]*H[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    _rotation(total)
    world_header=transform(h['at_m'],T,R)
    if mapped.get('additional_lift_m')!=0. or placement.get('extra_body_lift_m')!=0. or T[2]!=0. or not _near(center,world_header):raise ValueError('Stale/mixed pose or second body lift')
    bores=[]
    for z in (1.0535,1.0855):
        p=[x,column,z];local=[sum(total[k][j]*(p[k]-world_header[k]) for k in range(3)) for j in range(3)]
        if abs(local[0])+.0071>h['geometry']['size_m'][0]/2+1e-10 or abs(local[2])+.0071>.09+1e-10:raise ValueError('Bore outside actual120mm RHS material walls')
        bores.append(dict(header_id=h['id'],source_header_record_id=t['source_record_ids'][h['id']],world_axis=0,world_center_m=p,
            header_local_axis=1,header_local_center_m=local,header_local_wall_planes_m=[-.060,.060],diameter_m=.0142,wall_thickness_m=.008,
            removed_wall_volume_m3=2*.008*pi*.0071**2,existing_bores_must_be_unioned_once=True,source_paid_blank_retained=True))
    relief=abs(lane_y)+.030>1.080
    inner=lane_y-side*.070;outer=side*1.080 if relief else lane_y+side*.030
    width=abs(outer-inner)
    value=dict(schema='osr-chair-P6-local-node-proposal/1',source_p6=deepcopy(P6),source_stub=deepcopy(mapped['old_stub']),
        header_template_id=t['physical_template_id'],joint_review_id=reviewed_joint_id,frame='body/world without extra lift',
        bores=bores,sleeves=dict(quantity=2,material='al6005a',axis=0,length_m=.120,outer_radius_m=.007,inner_radius_m=.0045,
            net_volume_each_m3=pi*(.007**2-.0045**2)*.120,gross_cut_length_m=.124),
        hardware_dimensions=node_hardware(.120),M8=dict(quantity=2,material='steel',underhead_length_m=.160,grip_m=.141,head_washer_m=.0016,nut_washer_m=.0016,nut_m=.0065,thread_projection_m=.0093,
            layers_m=[['left-isolation',.0005],['left-plate',.010],['actual-header',.120],['right-plate',.010],['right-isolation',.0005]],qualified=False),
        plates=dict(material='al5083',quantity=2,attached=len(connected_sides),opposite_backers=2-len(connected_sides),size_m=[.010,width,.080],center_y_m=(inner+outer)/2,
            gross_blank_each_m=[.010,.104,.084],notch_width_m=.100-width,cap_weld_nominal_y_gap_m=.006 if relief else None,
            internal_12mm_bridge_diaphragms=len(connected_sides) if relief else 0,
            diaphragm_size_m=[.012,.034,.054],diaphragm_gross_blank_m=[.012,.038,.058],
            actual_station_and_weld_route_require_new_anchor_clearance_check=True,existing_central_8mm_diaphragm_is_not_this_part=True),
        relative_to100mm=dict(sleeve_extra_length_each_m=.020,M8_extra_length_each_m=.020,
            additional_sleeve_net_volume_m3=2*pi*(.007**2-.0045**2)*.020,
            additional_M8_shank_volume_m3=2*pi*.004**2*.020),
        necessary_bound=bound,positive_process_person_hours=dict(sleeve_pair=.070,wall_drill_pair=.080,plate_pair=.360 if relief else .200,QA=.110 if relief else .060),
        apply_automatically=False,actual_source_machining_applied=False,complete_installed=False,**FLAGS)
    physical=dict(header_template_id=t['physical_template_id'],world_header_center_m=world_header,
        bores=[{k:b[k] for k in ('world_axis','world_center_m','header_local_axis','header_local_center_m','header_local_wall_planes_m','diameter_m','wall_thickness_m')} for b in bores],
        sleeve={k:value['sleeves'][k] for k in ('quantity','material','axis','length_m','outer_radius_m','inner_radius_m')},
        hardware={k:v for k,v in node_hardware(.120).items() if k!='qualified'},
        plates={k:v for k,v in value['plates'].items() if k not in ('actual_station_and_weld_route_require_new_anchor_clearance_check','existing_central_8mm_diaphragm_is_not_this_part')})
    value['physical_definition_id']=identity(physical);value['evaluation_id']=identity(value)
    return value


def spacer_shoe_proposal(template):
    gap=_number(template['header_to_cleat_gap_m'],True)
    if abs(gap-.0265)>1e-9:raise ValueError('Changed joint gap needs a new shoe source family')
    for key in ('header','endcap','endcap_weld','cleat','central_diaphragm'):
        c=template[key]
        if template['source_record_ids'].get(c['id'])!=identity(c):raise ValueError('Stale shoe mate source record')
    h=template['header'];side=1 if h['at_m'][1]>0 else -1;hx=h['at_m'][0]
    value=dict(schema='osr-chair-P6-header-shoe-outline/1',ownership_key='shoe/'+h['id'],quantity_per_header=1,
        frame='Existing P6 body-local; instantiate once per header, not per chair node',
        geometry=dict(shape='box',center_m=[hx,side*.34825,1.0195],size_m=[.120,.0265,.180],material='al5083'),
        source_mates={k:template[k]['id'] for k in ('header','cleat','central_diaphragm')},source_mate_record_ids=deepcopy(template['source_record_ids']),
        gross_blank_size_m=[.124,.0305,.184],net_volume_m3=.120*.0265*.180,gross_volume_m3=.124*.0305*.184,
        nominal_density_kg_m3=2660.,nominal_mass_kg=.120*.0265*.180*2660,
        joint_welds=dict(quantity=2,material='al5356-hypothesis',leg_m=.004,each_U_length_m=.460,
            nominal_deposit_volume_m3=2*.460*.004**2/2,gross_filler_reserve_factor=1.20,
            top_weld_omitted=True,side_weld_top_m=1.0995,floor_lower_face_m=1.1095,nominal_floor_gap_after_4mm_halo_m=.006,
            meaning='Two proposed bottom-and-side U seams;10mm top truncation avoids depositing a top weld into the floor. New joint load/HAZ/fatigue/model review required'),
        positive_person_hours=dict(cut_and_face=.25,fit_and_weld=.60,QA=.15),shared_jig_tooling_usd=None,
        main_girder_and_cleat_joint_qualification=False,actual_mating_and_tool_evaluation=False,apply_automatically=False,**FLAGS)
    value['physical_definition_id']=identity(dict(geometry=value['geometry'],quantity_per_header=1,
        source_mates_physical=[component_physical(template[k]) for k in ('header','cleat','central_diaphragm')],
        weld_geometry={k:value['joint_welds'][k] for k in ('quantity','material','leg_m','each_U_length_m','top_weld_omitted','side_weld_top_m')}))
    value['evaluation_id']=identity(value);return value


def coupon_projection(c):
    cons=c['consumables']
    return dict(entities=c['entities'],bounded_welds=[{k:w[k] for k in ('fillet_m','net_length_m','centroid_m')} for w in cons['welds']],
        bounded_consumables={n:{k:cons[n][k] for k in ('net_mass_kg','centroid_hypothesis_m')} for n in ('powder_coating','cover_seams','anchor_sealant','r3_added_foot_finish') if n in cons})


def _legacy_volume(e):
    if e['shape']=='box':return prod(e['size_m'])-fsum(pi*(b['diameter_m']/2)**2*b.get('depth_m',e['size_m'][b['axis']]) for b in e['bores'])
    if e['shape']=='cylinder':return pi*(e['radius_m']**2-e['inner_radius_m']**2)*e['length_m']
    raise ValueError('Unsupported coupon material')


def revised_coupon_rows(coupon,recipe,new_rows,*,expected_physical_id,manufacturing_state):
    """New unfabricated drill-pattern family; never redrill an existing part."""
    if manufacturing_state!='new-design-unfabricated':raise ValueError('Adjacent old/new9mm holes5mm apart are not an approved retrofit')
    _digest(expected_physical_id)
    if identity(coupon_projection(coupon))!=expected_physical_id or coupon.get('recipe_id')!=identity(recipe):raise ValueError('Exact frozen coupon/recipe required')
    if not coupon.get('status') or any(v is not False for v in coupon['status'].values()):raise ValueError('Unqualified frozen research coupon required')
    if coupon.get('row_revision'):raise ValueError('No cumulative row perturbation')
    if not _near(recipe['geometry']['foot_size_m'],[.110,.170,.020]) or abs(_number(recipe['geometry']['leg_length_m'])-.3775)>1e-10:raise ValueError('Unchanged20mm foot/377.5mm leg domain required')
    for key in ('occupant_kg','provisional_chair_kg','gravity_m_s2','vertical_factor','longitudinal_factor','lateral_factor','overturning_height_above_floor_m'):_number(recipe['preliminary_loads'][key],True)
    old=[_number(v) for v in coupon['row_v_m']];new=[_number(v) for v in new_rows]
    if len(old)!=2 or len(new)!=2 or any(not any(abs(v-x)<1e-9 for x in choices) for v,choices in zip(old,[(-.19,-.05),(.05,.19)])):raise ValueError('Exact two R4 parent rows required')
    deltas=[b-a for a,b in zip(old,new)]
    if not any(abs(d)>1e-10 for d in deltas) or any(min(abs(d),abs(abs(d)-.005))>1e-9 for d in deltas):raise ValueError('New family permits one discrete5mm drill-pattern move per row')
    value=deepcopy(coupon);value.pop('evaluation_id',None);by={e['id']:e for e in value['entities']}
    if len(by)!=len(value['entities']):raise ValueError('Duplicate source chair entity')
    changed=set();moved=set()
    for row,delta in enumerate(deltas):
        if abs(delta)<1e-10:continue
        for foot in (row,row+2):
            e=by.get(f'foot-{foot}')
            if not e or e['shape']!='box' or len(e['bores'])!=1 or abs(e['bores'][0]['center_m'][1]-old[row])>1e-9:raise ValueError('Unresolved exact foot bore owner')
            b=e['bores'][0]
            if b['axis']!=2 or abs(b['diameter_m']-.009)>1e-10:raise ValueError('Changed floor fixing geometry')
            b['center_m'][1]=new[row]
            if any(abs(b['center_m'][k]-e['center_m'][k])+b['diameter_m']/2+.005>e['size_m'][k]/2+1e-10 for k in (0,1)):raise ValueError('New foot bore lacks5mm nominal edge ligament')
            changed.add(e['id'])
        strip=by.get(f'anchor-strip-{row}')
        if not strip or strip['shape']!='box' or len(strip['bores'])!=2:raise ValueError('Exact strip bore owners required')
        for b in strip['bores']:
            if b['axis']!=2 or abs(b['center_m'][1]-old[row])>1e-9:raise ValueError('Unresolved source strip axis')
            b['center_m'][1]=new[row]
            if abs(new[row]-strip['center_m'][1])+b['diameter_m']/2+.005>strip['size_m'][1]/2+1e-10:raise ValueError('New strip bore edge failure')
        changed.add(strip['id'])
        for col in (0,1):
            prefixes=[f'floor-M8-{row}-{col}',f'floor-sleeve-{row}-{col}',f'head-isolation-{row}-{col}',f'dielectric-liner-{row}-{col}',f'isolation-{row}-{col}',f'backing-{row}-{col}',f'nut-cage-{row}-{col}',f'tip-cap-{row}-{col}']
            for prefix in prefixes:
                es=[e for e in value['entities'] if e['id']==prefix or e['id'].startswith(prefix+'/')]
                if not es:raise ValueError('Missing row-dependent fixing/liner/cage/cap '+prefix)
                for e in es:
                    key='center_m' if e['shape']=='box' else 'start_m' if e['shape']=='cylinder' else None
                    if key is None:raise ValueError('Unresolved row-dependent material solid')
                    e[key][1]+=delta
                    for b in e.get('bores',[]):b['center_m'][1]+=delta
                    moved.add(e['id'])
            stacks=[s for s in value['fastener_stacks'] if s['id']==f'floor-M8-{row}-{col}']
            if len(stacks)!=1:raise ValueError('Exact floor fastener stack required')
            st=stacks[0];st['head_bearing_face_m'][1]+=delta
            for e in st['entities']:
                if e['id'] not in by:raise ValueError('Stack and material occurrences differ')
                e.update(deepcopy(by[e['id']]))
    owners=[i for s in value['stock'] for i in s['entity_ids']]
    if len(set(owners))!=len(owners) or set(owners)!=set(by):raise ValueError('Coupon stock ownership incomplete/duplicate')
    process_delta=0.;QA_delta=0.
    for stock in value['stock']:
        net=fsum(_legacy_volume(by[k]) for k in stock['entity_ids'])
        if net<=0 or abs(net-stock['net_volume_m3'])>1e-12 or stock['gross_volume_m3']<net-1e-12:raise ValueError('Changed stock net/gross domain')
        if changed.intersection(stock['entity_ids']):stock['process_hours']+=.015;stock['qa_hours']+=.005;process_delta+=.015;QA_delta+=.005
    loads=recipe['preliminary_loads'];mass=loads['occupant_kg']+loads['provisional_chair_kg'];gravity=loads['gravity_m_s2']
    compression=mass*gravity*loads['vertical_factor']/4
    uplift=mass*gravity*max(loads['longitudinal_factor'],loads['lateral_factor'])*loads['overturning_height_above_floor_m']/(2*min(.265,abs(new[1]-new[0])))
    eccentricity=sqrt(.055**2+max(abs(v-s*.12) for v,s in zip(new,(-1,1)))**2)
    stress=6*max(compression,uplift)*eccentricity/(.110*.020**2)
    if stress>60e6:raise ValueError('Revised row fails unchanged60MPa necessary foot-band hypothesis')
    if 'anchor_sealant' in value['consumables']:
        value['consumables']['anchor_sealant']['centroid_hypothesis_m'][1]+=sum(deltas)/2
        value['consumables']['anchor_sealant']['centroid_basis']='Retained bounded point proxy shifted by equal2-of4-anchor share; not measured bead geometry'
    value['row_v_m']=new;value['status']=deepcopy(FLAGS)
    value['support_bounds']=dict(foot_band_stress_Pa=stress,allowable_hypothesis_Pa=60e6,fixture_band_screen_passed=True,qualified=False,
        model_domain='Same unchanged-load20mm-foot elastic band hypothesis; attachment/contact/HAZ/fatigue and actual load envelopes remain open')
    value['row_revision']=dict(family='R5-P6-new-drill-jig-5mm',parent_physical_id=expected_physical_id,parent_recipe_id=coupon['recipe_id'],old_rows_m=old,new_rows_m=new,
        replaced_bores_not_added=True,new_parts_before_fabrication_only=True,moved_entity_ids=sorted(moved),changed_bore_owner_ids=sorted(changed),
        extra_process_person_hours=process_delta,extra_QA_person_hours=QA_delta,gross_blanks_unchanged=True,prior_moments_and_native_and_body_results_inherited=False)
    new_recipe=deepcopy(recipe)
    new_recipe['family']='research/direct-floor-chair-r5-P6-counterpart'
    new_recipe['anchor_row_revision']=dict(parent_recipe_id=coupon['recipe_id'],old_rows_m=old,new_rows_m=new,step_m=.005,
        unfabricated_new_parts_only=True,legacy_four_drilling_alternatives_superseded_only_in_this_family=True)
    new_recipe['geometry']['drilling_row_v_m']=new
    value['definition_recipe']=new_recipe
    value['recipe_id']=identity(new_recipe)
    value['definition_id']=identity(coupon_projection(value));value['evaluation_id']=identity(value)
    return value


def floor_and_credit_guard(source_credit_rows,floor_wear,*,expected_credit_record_ids,expected_wear_record_id,already_applied_credit_ids,wear_translation_already_applied):
    ids=[r['source_part_id'] for r in source_credit_rows]
    if len(ids)!=14 or set(ids)!=set(OLD_PARTS):raise ValueError('Exact14once-only old chair allowance leaves required')
    if expected_credit_record_ids!=[identity(r) for r in source_credit_rows] or expected_wear_record_id!=identity(floor_wear):raise ValueError('Stale/mixed exact source credit/wear records')
    if type(wear_translation_already_applied) is not bool:raise ValueError('Explicit prior-application state required')
    if set(ids)&set(already_applied_credit_ids) or wear_translation_already_applied:raise ValueError('Source allowances/wear may not be credited or lifted twice')
    if abs(_number(floor_wear['translate_z_m'])-.0185)>1e-10 or floor_wear.get('source_pieces')!=108 or floor_wear.get('gross_stock_and_cost_retained') is not True:raise ValueError('Exact global108piece wear correction required')
    return dict(source_credit_ids=ids,source_credit_scope='Whole train exactly once, not per bogie/node; original source gross procurement is retained unless separately retired',
        wear_global_delta_z_m=.0185,wear_target_center_m=1.1485,geometry_seat_lift_m=0.,new_floor_strip_cutouts_reused_if_unchanged=True,
        remaining_tile_clip_union_and_source_hash_verification_required=True,body_axle_civil_propulsion_cost_results_inherited=False,apply_automatically=False,**FLAGS)
