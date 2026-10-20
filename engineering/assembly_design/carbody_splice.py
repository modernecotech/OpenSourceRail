"""Exact carbody butt-splice demands and unqualified weld-gap coupons.

Element restoring end forces are retained per simultaneous load case and side.
They are not a uniquely recovered weld traction: endpoint lumped loads and
rigid joint transfers are not separately retained by the source frame solver.
Partial penetration is a deliberate defect sensitivity, never a rail option.
"""
from copy import deepcopy
import json
import math
from pathlib import Path

import numpy as np
from engineering.twin_workflow import core
from engineering.design_consistency import contracts as geometry,demonstrators
from . import baseline,carbody_assembly as body,carbody_frame as frame

RECIPES=[dict(penetration_fraction=v,root_gap_m=.003,offcut_length_m=.35) for v in (.5,.75,1.)]
KINDS={.5:'carbody-splice-half',.75:'carbody-splice-three-quarter',1.:'carbody-splice-full'}
HOLDS=[
 'Source frame uses ideal rigid joint offsets, synthetic planning loads and an unadopted body fixture; no railway joint demand adoption',
 'Member-end restoring forces include endpoint lumped load and rigid-joint transfer ambiguity; a resolved free-body weld traction is not established',
 'Issued bevel/root face/backing and corner transitions, access, fit tolerances and distortion control are absent',
 'Selected steel heat/corner radii and filler classification, metallurgy, process and WPS/PQR/welder qualification are absent',
 'Local weld/HAZ/parent stress, shear/torsion/warping, residual stress, imperfections, buckling, fracture and railway fatigue resistance are unverified',
 'Inspection/NDT method, access, acceptance criteria, repair disposition and authenticated serial evidence require adoption',
 'Coupon is not installed in the carbody; no body stiffness, mass, load path or accepted completion is changed',
]
SOURCES=[dict(url='https://www.twi-global.com/technical-knowledge/job-knowledge/design-part-3-092',
    scope='Butt-joint preparation, access and weld design guidance; no adopted railway criterion or selected WPS',retrieved='2026-10-20'),
    dict(url='https://www.twi-global.com/technical-knowledge/job-knowledge/design-part-4-093',
    scope='Fatigue-sensitive weld detail guidance; incomplete penetration coupons are defects, not accepted alternatives',retrieved='2026-10-20')]


def _canonical(value):return json.loads(core.encoded(value))


def _finite(values,label):
    if not isinstance(values,(list,tuple)) or any(type(v) not in (int,float) or not math.isfinite(v) for v in values):
        raise ValueError('finite numeric '+label+' required')


def sources():
    paths=[Path(__file__),Path(body.__file__),Path(frame.__file__),baseline.DATA,
        core.ROOT/'engineering/civil_exploration/spatial_structure.py',
        core.ROOT/'engineering/civil_exploration/train_bridge.py',
        core.ROOT/'design/component-catalogue/src/osr_mech/section_contract.py',
        core.ROOT/'engineering/design_consistency/contracts.py']
    return {p.relative_to(core.ROOT).as_posix():core.sha(p) for p in paths}


def candidates(policy):
    baseline.validate(policy)
    return deepcopy(RECIPES)


def _source(policy,carbody):
    baseline.validate(policy)
    if carbody is None:carbody=body.build(policy,list(body.candidates(policy))[4])
    if _canonical(carbody)!=_canonical(body.build(policy,carbody['variables'])):
        raise ValueError('exact controlled source carbody required')
    return carbody


def demand_register(carbody,frame_report=None,*,policy=None):
    """Every declared primary sill/roof splice, exact endpoint, case and side.

    No interpolation, componentwise envelope or averaging of the two sides is
    used. The source's local element axes and end-force ordering are preserved.
    """
    policy=core.read(baseline.DATA) if policy is None else policy
    carbody=_source(policy,carbody);expected=frame.report(carbody)
    if frame_report is not None and _canonical(frame_report)!=_canonical(expected):
        raise ValueError('exact retained source frame report required')
    result=expected;parts={p['id']:p for p in carbody['contract']['parts']}
    joints=[j for j in carbody['contract']['assembly_joints'] if j['id'].endswith('-butt-splice')]
    if len(joints)!=4:raise ValueError('four controlled primary sill/roof butt splices required')
    records=[]
    case_sha256={identity:core.digest(case) for identity,case in result['cases'].items()}
    for joint in joints:
        if len(joint['endpoints'])!=2 or any(not parts[i]['analysis']['section'] for i in joint['endpoints']):
            raise ValueError('two owned RHS endpoints required at declared splice')
        ends={pid:frame._line(parts[pid]) for pid in joint['endpoints']}
        possibilities=[]
        left,right=joint['endpoints']
        for a in (0,1):
            for b in (0,1):possibilities.append((float(np.linalg.norm(ends[left][a]-ends[right][b])),a,b))
        distance,a,b=min(possibilities)
        if distance>1e-10:raise ValueError('declared butt splice endpoints do not coincide')
        endpoint_indices={left:a,right:b};point=ends[left][a]
        if not np.allclose(parts[left]['placement']['rotation'],parts[right]['placement']['rotation'],rtol=0,atol=1e-12):
            raise ValueError('common RHS cut axes required; no implicit wrench rotation')
        axes=parts[left]['placement']['rotation'];case_records=[]
        for case_id,case in result['cases'].items():
            if case['candidate_revision']!=carbody['revision']:raise ValueError('frame case source differs')
            force_map={}
            for force in case['member_forces']:
                key=(force['part_id'],tuple(force['nodes']))
                if key in force_map:raise ValueError('duplicate frame element force identity')
                _finite(force['local_end_forces_n_nm'],'twelve-axis member force')
                if len(force['local_end_forces_n_nm'])!=12:raise ValueError('twelve element end-force components required')
                force_map[key]=force
            sides=[]
            for pid in joint['endpoints']:
                matches=[]
                for element in case['elements']:
                    if element['part_id']!=pid:continue
                    if element['part_revision']!=parts[pid]['revision']:raise ValueError('stale frame member revision')
                    for end,node in enumerate(element['nodes']):
                        position=np.asarray(case['nodes_m'][node])
                        if np.linalg.norm(position-point)<=1e-10:matches.append((element,end,node,position))
                if len(matches)!=1:raise ValueError('unique exact member-end cut required; no nearest-section substitution')
                element,element_end,node,position=matches[0];force=force_map[(pid,tuple(element['nodes']))]
                raw=list(force['local_end_forces_n_nm'][6*element_end:6*element_end+6])
                # A positive-local-x cut convention requires reversing all six
                # components at a negative-x physical member endpoint.
                sign=1. if endpoint_indices[pid]==1 else -1.
                common=[sign*v for v in raw];rotation=np.asarray(parts[pid]['placement']['rotation'])
                world=np.r_[rotation@np.asarray(raw[:3]),rotation@np.asarray(raw[3:])].tolist()
                sides.append(dict(part_id=pid,part_revision=parts[pid]['revision'],geometry_sha256=parts[pid]['analysis']['geometry_sha256'],
                    physical_member_endpoint=endpoint_indices[pid],physical_side='negative-local-x member' if endpoint_indices[pid]==1 else 'positive-local-x member',
                    element_nodes=element['nodes'],element_endpoint_index=element_end,cut_node=node,
                    exact_source_endpoint_m=ends[pid][endpoint_indices[pid]].tolist(),retained_frame_node_m=position.tolist(),
                    raw_local_end_wrench_n_nm=raw,raw_world_end_wrench_n_nm=world,
                    common_positive_local_x_section_wrench_n_nm=common,common_convention_multiplier=sign,
                    section=deepcopy(parts[pid]['analysis']['section'])))
            residual=[sum(side['raw_local_end_wrench_n_nm'][i] for side in sides) for i in range(6)]
            case_records.append(dict(case_id=case_id,source_case_sha256=case_sha256[case_id],input=deepcopy(case['input']),
                sides=sides,raw_endpoint_wrench_sum_n_nm=residual,
                endpoint_load_interpretation='Unresolved endpoint nodal/lumped/rigid-link force transfer; residual is not a weld equilibrium failure or permission to average',
                resolved_joint_free_body=False))
        records.append(dict(joint_id=joint['id'],source_joint_sha256=core.digest(joint),part_ids=joint['endpoints'],
            cut_point_world_m=point.tolist(),local_to_world_rotation=axes,
            global_datum='Source car centre x=0, centreplane y=0 and rail z=0; coupon later uses its own local datum',
            component_order=['N_x_N','V_y_N','V_z_N','T_x_Nm','M_y_Nm','M_z_Nm'],
            source_mechanism=joint['mechanism'],cases=case_records))
    value=dict(schema='osr-carbody-splice-demands/1',carbody_revision=carbody['revision'],source_frame_revision=result['revision'],
        source_frame_sha256=core.digest(result),source_sha256=sources(),joint_count=len(records),case_count=len(result['cases']),splices=records,
        exact_cut_method='Physical RHS endpoint matched to exactly one source element endpoint per member, within retained node rounding1e-10m; no interpolation or maxima mixing',
        componentwise_envelope_used=False,side_average_used=False,adopted_joint_demands=False,
        source_frame_failed_checks=result['failed_checks'],source_frame_held_checks=result['held_checks'],
        scope='Simultaneous element restoring wrench vectors at each exact declared sill/roof splice endpoint; endpoint applied loads/rigid transfers and physical weld traction remain unresolved',**core.FLAGS)
    value['revision']=core.digest(value);return value


def section_index(section,wrench):
    """Linear plane-section index only; deliberately no weld resistance/allowable.

    Normal force and the two bending moments stay in one simultaneous vector.
    V/A entries are signed nominal averages, not local shear distributions.
    Torsion/warping and combined fracture/fatigue stress are not evaluated.
    """
    _finite(wrench,'simultaneous six-axis wrench')
    if len(wrench)!=6:raise ValueError('simultaneous six-axis wrench required')
    for key in ('area_m2','iy_m4','iz_m4','width_m','height_m'):
        if type(section.get(key)) not in (int,float) or not math.isfinite(section[key]) or section[key]<=0:
            raise ValueError('positive finite section geometry required')
    N,Vy,Vz,T,My,Mz=wrench;A=section['area_m2'];Iy=section['iy_m4'];Iz=section['iz_m4']
    corners=[dict(y_m=sy*section['width_m']/2,z_m=sz*section['height_m']/2,
        sigma_x_pa=N/A+My*sz*section['height_m']/2/Iy-Mz*sy*section['width_m']/2/Iz)
        for sy in (-1,1) for sz in (-1,1)]
    return dict(simultaneous_wrench_n_nm=list(wrench),normal_corner_indices=corners,
        maximum_absolute_normal_index_pa=max(abs(r['sigma_x_pa']) for r in corners),
        nominal_shear_average_y_pa=Vy/A,nominal_shear_average_z_pa=Vz/A,torsion_demand_nm=T,
        torsional_stress_pa=None,combined_equivalent_stress_pa=None,adopted_allowable_pa=None,resistance_n_nm=None,
        scope='Gross linear kinematic plane-section comparison only; discontinuous/partial filler shear, warping, weld/HAZ/root/toe stress and material response are unqualified')


def _filler_section(primitives):
    # Cross-sectional properties recovered from the actual disjoint box solids,
    # not a full-RHS area multiplied by an invented weld efficiency factor.
    rows=[]
    for primitive in primitives:
        _,w,h=primitive['dimensions_m'];_,y,z=primitive['centre_m'];rows.append((w*h,y,z,w,h))
    A=sum(a for a,_,_,_,_ in rows);yc=sum(a*y for a,y,_,_,_ in rows)/A;zc=sum(a*z for a,_,z,_,_ in rows)/A
    Iy=sum(w*h**3/12+a*(z-zc)**2 for a,_,z,w,h in rows);Iz=sum(h*w**3/12+a*(y-yc)**2 for a,y,_,w,h in rows)
    return dict(area_m2=A,iy_m4=Iy,iz_m4=Iz,centroid_y_m=yc,centroid_z_m=zc,
        width_m=max(y+w/2 for _,y,_,w,_ in rows)-min(y-w/2 for _,y,_,w,_ in rows),
        height_m=max(z+h/2 for _,_,z,_,h in rows)-min(z-h/2 for _,_,z,_,h in rows),
        basis='Actual four disjoint nominal weld-gap strips; not effective weld design geometry or material qualification')


def build(policy,variables=None,*,carbody=None,frame_report=None,splice_id='sill--1-butt-splice'):
    variables=deepcopy(RECIPES[-1] if variables is None else variables)
    if variables not in candidates(policy) or any(type(v) is not float or not math.isfinite(v) for v in variables.values()):
        raise ValueError('controlled finite coupon recipe required')
    carbody=_source(policy,carbody);register=demand_register(carbody,frame_report,policy=policy)
    source=next((s for s in register['splices'] if s['joint_id']==splice_id),None)
    if source is None or not splice_id.startswith('sill-'):raise ValueError('declared primary sill splice required for coupon')
    source_parts={p['id']:p for p in carbody['contract']['parts']};first=source_parts[source['part_ids'][0]]
    section=first['analysis']['section'];w,h,t=(section[k] for k in ('width_m','height_m','wall_m'))
    if any(source_parts[pid]['analysis']['section']!=section for pid in source['part_ids']):raise ValueError('matching selected stock cross-sections required')
    gap=variables['root_gap_m'];length=variables['offcut_length_m'];depth=t*variables['penetration_fraction']
    materials=deepcopy(carbody['contract']['materials']);materials['weld-metal-hypothesis']=dict(density_kg_m3=materials['steel']['density_kg_m3'],
        basis='Nominal parent-steel density for measured coupon mass bookkeeping only; filler classification, properties and WPS are unselected')
    parts=[];offcuts=[];filler=[]
    for i,sign in enumerate((-1,1)):
        pid='rhs-offcut-'+str(i);part=geometry.member(pid,length,w,h,t,'steel',materials,
            placement=dict(translation_m=[sign*(length+gap)/2,0.,0.],rotation=body.IDENTITY),
            limits=dict(tolerance_m=None,tolerance_status='fit and machining tolerances unissued'),
            inspections=['selected heat and section/corner radii','cut length/squareness','gap and coaxiality','unissued edge-prep/HAZ requirements'])
        part.update(manufacturing_unit_id=pid,geometric_role='source-stock-offcut',procurement=None,
            process_route='Saw selected RHS stock, deburr and fixture; square-ended research blank, issued weld edge preparation absent',
            source_part_id=source['part_ids'][i],source_part_revision=source_parts[source['part_ids'][i]]['revision'],
            source_geometry_sha256=source_parts[source['part_ids'][i]]['analysis']['geometry_sha256'])
        parts.append(part);offcuts.append(pid)
    # Four explicitly owned nominal strips in the root gap; base-metal ends
    # touch their x faces, with no duplicate parent/filler material volume.
    # Partial penetration leaves inner/root/corner regions intentionally empty.
    specs=[('top',[gap,w,depth],[0.,0.,(h-depth)/2]),('bottom',[gap,w,depth],[0.,0.,-(h-depth)/2]),
        ('side-negative',[gap,depth,h-2*t],[0.,-(w-depth)/2,0.]),('side-positive',[gap,depth,h-2*t],[0.,(w-depth)/2,0.])]
    for name,dimensions,centre in specs:
        pid='nominal-weld-'+name;primitive=geometry.box(pid,*dimensions,centre)
        part=geometry.part(pid,'weld-metal-hypothesis',dict(role='Nominal gap ownership; not issued groove, bevel, reinforcement or bead surface',primitives=[primitive]),materials,
            limits=dict(tolerance_m=None,tolerance_status='penetration/prep/face criteria unissued'),
            inspections=['filler/process trace','root/side fusion and penetration','corner transitions','NDT and independent disposition'])
        part.update(manufacturing_unit_id='coupon-welded-assembly',geometric_role='unqualified-weld-metal-region',procurement=None,
            process_route='Nominal solid ownership for deposition study; actual joint prep, access, passes, backing and inspection unissued')
        parts.append(part);filler.append(pid)
    joints=[dict(id='coupon-butt-connection',endpoints=offcuts+filler,mechanism='Three-mm square-gap bookkeeping coupon; unissued preparation, backing and weld procedure',
        fastener_ids=[],tolerance_m=None,load_case_ids=[c['case_id'] for c in source['cases']],inspection=['fit-up','root/face fusion','NDT and disposition'],capacity_evidence=None,qualified=False)]
    revision=core.digest(dict(kind=KINDS[variables['penetration_fraction']],variables=variables,source_carbody_revision=carbody['revision'],
        source_register_revision=register['revision'],source_joint=source,parts=parts,joints=joints))
    for p in parts:p.update(revision=revision,joints=['coupon-butt-connection'])
    contract=demonstrators.contract('Separate selected-sill offcut/weld-gap research coupon; not installed',parts,materials)
    contract.update(revision=revision,assembly_joints=joints,mandatory_evidence=HOLDS,
        unresolved_part_allocations=['No issued edge-preparation groove/backing/reinforcement/profile; fixture, consumable loss and actual process allowances unknown'])
    geometry.validate(contract)
    filler_section=_filler_section([p['manufacturing']['primitives'][0] for p in parts if p['id'] in filler])
    sequence=[dict(id='fit-source-stock',title='Cut and fixture selected RHS offcuts at3mm gap; issued edge prep absent',part_ids=offcuts,requires=[]),
        dict(id='nominal-face-strips',title='Show nominal top/bottom gap ownership; actual passes unissued',part_ids=filler[:2],requires=['fit-source-stock']),
        dict(id='nominal-side-strips',title='Show nominal sidewall gap ownership; corner/root fusion and NDT held',part_ids=filler[2:],requires=['nominal-face-strips'])]
    process=[dict(id='material',instruction='Verify selected parent heat, actual corner radii, weldability and unselected filler before cutting',hold=['heat/product certificate','filler/WPS/PQR adoption'],executed=False),
        dict(id='cut-and-prep',instruction='Cut350mm research offcuts; establish an issued bevel/root face/backing/access detail before any manufacturing release',hold=['qualified edge prep and root access','dimensional tolerances'],executed=False),
        dict(id='fit',instruction='Fixture with accessible datum targets; record3mm nominal gap, alignment and restraint assumptions',hold=['actual calibrated measurements','fixture access and shrinkage plan'],executed=False),
        dict(id='weld',instruction='The4gap solids define nominal material ownership only; establish real process, pass direction, heat input, corner closure and inspection access',hold=['qualified WPS/PQR/welder','root and corner fusion'],executed=False),
        dict(id='inspect',instruction='Record actual dimensional, visual and adopted NDT results and any destructive coupon observations; no simulated pass',hold=['adopted acceptance/NDT criteria','authenticated serial data and independent review'],executed=False)]
    metadata=dict(source_carbody_revision=carbody['revision'],source_body_variables=deepcopy(carbody['variables']),source_frame_revision=register['source_frame_revision'],
        source_demand_register_revision=register['revision'],source_joint_id=splice_id,source_joint_demand=source,source_sha256=sources(),
        selected_source_sections={pid:deepcopy(source_parts[pid]['analysis']['section']) for pid in source['part_ids']},
        selected_source_geometry_sha256={pid:source_parts[pid]['analysis']['geometry_sha256'] for pid in source['part_ids']},
        architecture='baghdad-six-car-research-coupon',installed_in_source_carbody=False,source_body_stiffness_modified=False,
        datum=dict(origin='Coupon root-gap centre',local_x='Selected source RHS axial direction',local_y='RHS width',local_z='RHS height',world_cut_point_m=source['cut_point_world_m'],source_local_to_world=source['local_to_world_rotation']),
        original_body_nominal_gap_m=0.,coupon_root_gap_m=gap,offcut_length_each_m=length,penetration_depth_m=depth,
        penetration_class='full nominal gap ownership; actual complete fusion unproven' if variables['penetration_fraction']==1. else 'deliberate incomplete-penetration defect sensitivity; not an accepted railway option',
        filler_section=filler_section,parent_section=deepcopy(section),offcut_ids=offcuts,weld_metal_part_ids=filler,
        weld_mass_kg=sum(p['properties']['mass_kg'] for p in parts if p['id'] in filler),
        assembly_sequence=sequence,process_plan=process,issued_manufacturing_detail=False,full_pilot_scope=False,
        complete_installed_mass_kg=None,source_frame_failed_checks=register['source_frame_failed_checks'])
    value=dict(schema='osr-carbody-splice-coupon/1',kind=KINDS[variables['penetration_fraction']],variables=variables,revision=revision,contract=contract,
        requirement_ids=['baghdad:ME-01'],metadata=metadata,assembly_steps=[p['instruction'] for p in process],
        qa_plan=[dict(unit_id=p['id'],unit_revision=revision,serial=None,required=p['inspection_characteristics'],records=[],accepted=False) for p in parts],
        source_scope='Separate selected-RHS offcut coupon with nominal weld-gap material ownership and exact simultaneous source endpoint demands; no installed weld preparation, connection stiffness, resistance or railway acceptance',
        open_requirements=HOLDS,sources=SOURCES,**core.FLAGS)
    value['definition_sha256']=core.digest(value);return value


def evaluate(policy,candidate):
    meta=candidate['metadata'];source=body.build(policy,meta['source_body_variables'])
    expected=build(policy,candidate['variables'],carbody=source,splice_id=meta['source_joint_id'])
    if _canonical(candidate)!=_canonical(expected):raise ValueError('coupon differs from exact source/geometry/demand reconstruction')
    parts={p['id']:p for p in candidate['contract']['parts']};m=candidate['metadata'];section=m['filler_section'];cases=[]
    for case in m['source_joint_demand']['cases']:
        sides=[]
        for side in case['sides']:
            wrench=side['common_positive_local_x_section_wrench_n_nm']
            sides.append(dict(part_id=side['part_id'],physical_side=side['physical_side'],source_element_nodes=side['element_nodes'],
                simultaneous_wrench_n_nm=wrench,parent_section_index=section_index(m['parent_section'],wrench),
                nominal_gap_region_index=section_index(section,wrench)))
        cases.append(dict(case_id=case['case_id'],source_case_sha256=case['source_case_sha256'],sides=sides,
            raw_endpoint_wrench_sum_n_nm=case['raw_endpoint_wrench_sum_n_nm'],resolved_joint_free_body=False))
    mass=sum(p['properties']['mass_kg'] for p in parts.values());weld_mass=sum(parts[i]['properties']['mass_kg'] for i in m['weld_metal_part_ids'])
    rho=candidate['contract']['materials']['weld-metal-hypothesis']['density_kg_m3']
    checks=dict(exact_source_binding=True,source_frame_implemented_screens=not m['source_frame_failed_checks'],
        nominal_complete_penetration=candidate['variables']['penetration_fraction']==1.,
        weld_gap_mass_follows_actual_owned_geometry=math.isclose(weld_mass,section['area_m2']*candidate['variables']['root_gap_m']*rho,rel_tol=1e-10),
        stock_sections_preserved=all(parts[i]['analysis']['section']==m['parent_section'] for i in m['offcut_ids']),
        separate_coupon_does_not_change_body=not m['installed_in_source_carbody'] and not m['source_body_stiffness_modified'])
    checks.update({reason:None for reason in HOLDS})
    result=dict(schema='osr-carbody-splice-coupon-assessment/1',candidate_revision=candidate['revision'],checks=checks,
        failed_checks=[k for k,v in checks.items() if v is False],held_checks=[k for k,v in checks.items() if v is None],
        measurements=dict(represented_coupon_mass_kg=mass,weld_metal_mass_kg=weld_mass,parent_section=m['parent_section'],
            actual_nominal_gap_section=section,simultaneous_case_indices=cases),
        design_resistance_n_nm=None,adopted_allowable_pa=None,eligible_as_rail_connection=False,
        scope='Demand-to-geometry manufacturing research handoff; normal/shear-average section indices are not weld strength, multiaxial acceptance, fatigue qualification or installed-frame validation',**core.FLAGS)
    result['revision']=core.digest(result);return result


def section_svg(candidate):
    """Actual parent/gap-strip yz sections; no issued groove or weld face claim."""
    from html import escape
    geometry.validate(candidate['contract'])
    m=candidate['metadata'];parts={p['id']:p for p in candidate['contract']['parts']}
    parent=parts[m['offcut_ids'][0]]['manufacturing']['primitives']
    filler=[p for pid in m['weld_metal_part_ids'] for p in parts[pid]['manufacturing']['primitives']]
    if any(p['kind']!='box' for p in parent+filler):raise ValueError('controlled box-region coupon section required')
    for p in parent+filler:_finite(p['dimensions_m']+p['centre_m'],'section drawing dimensions')
    width=m['parent_section']['width_m'];height=m['parent_section']['height_m']
    _finite([width,height,m['penetration_depth_m'],m['coupon_root_gap_m']],'section drawing dimensions')
    if min(width,height)<=0:raise ValueError('positive section drawing envelope required')
    scale=435/max(width,height);centre_z=344
    def regions(primitives,cx,fill,stroke):
        output=[]
        for p in primitives:
            _,w,h=p['dimensions_m'];_,y,z=p['centre_m']
            output.append(f'<rect x="{cx+(y-w/2)*scale:.6f}" y="{centre_z-(z+h/2)*scale:.6f}" width="{w*scale:.6f}" height="{h*scale:.6f}" fill="{fill}" stroke="{stroke}" stroke-width=".6"/>')
        return output
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="720" viewBox="0 0 1000 720">',
        '<defs><pattern id="unfilled" patternUnits="userSpaceOnUse" width="5" height="5"><rect width="5" height="5" fill="#edf0f4"/><path d="M-1 1L1-1M0 5L5 0M4 6L6 4" stroke="#728397" stroke-width=".7"/></pattern></defs>',
        '<rect width="1000" height="720" fill="#fafbfd"/>',
        '<g font-family="sans-serif" fill="#20344a">',
        '<text x="35" y="35" font-size="21">Selected sill splice: nominal material ownership</text>',
        '<text x="35" y="60" font-size="14">UNISSUED coupon research; no groove/preparation, weld resistance or railway acceptance</text>',
        '<text x="120" y="100" font-size="16">Selected parent RHS stock / yz</text>',
        '<text x="610" y="100" font-size="16">Nominal root-gap midplane / yz</text>']
    lines+=regions(parent,250,'#5e778d','#31495d')
    lines+=regions(parent,750,'url(#unfilled)','#728397')
    lines+=regions(filler,750,'#e89935','#965914')
    lines+=[f'<text x="80" y="600" font-size="15">{width*1000:.1f} × {height*1000:.1f} mm; parent wall {m["parent_section"]["wall_m"]*1000:.1f} mm</text>',
        f'<text x="575" y="600" font-size="15">Nominal fill depth {m["penetration_depth_m"]*1000:.1f} mm; axial gap {m["coupon_root_gap_m"]*1000:.1f} mm</text>',
        '<rect x="35" y="625" width="17" height="13" fill="#e89935"/><text x="60" y="636" font-size="13">Owned nominal filler strips</text>',
        '<rect x="320" y="625" width="17" height="13" fill="url(#unfilled)"/><text x="345" y="636" font-size="13">Unfilled source-wall region</text>',
        '<text x="35" y="661" font-size="13">White centre is the RHS void. Partial penetration is a defect sensitivity; full nominal fill does not prove fusion.</text>',
        f'<text x="35" y="685" font-size="12">Source {escape(m["source_carbody_revision"][:16])}; cut {escape(m["source_joint_id"])}; demand {escape(m["source_demand_register_revision"][:16])}</text>',
        '</g></svg>']
    return '\n'.join(lines)+'\n'
