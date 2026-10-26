"""Failure-directed sill redistribution with actual stock and held acceptance.

This opt-in adapter broadens geometric variables beyond the frozen campaign's
discrete tuples. The25.6mm historical screen is advisory here. It is neither a
universal carbody requirement nor replaced by an invented strength criterion.
"""
from copy import deepcopy
from pathlib import Path
from math import isfinite
from engineering.station_rail import ROOT,FLAGS,body_frame,body_solid_frame
from engineering.station_rail.vehicle import tube
from engineering.station_rail.common import identity,digest,encoded
from engineering.design_search import joint_body,wheel_body

PRODUCER='engineering/design_search/body_revision.py'
LIMITS=dict(sill_width_m=[.18,.18],sill_depth_m=[.35,.65],sill_wall_m=[.004,.016],
    scope='Current counted tube/native adapter construction domain, not project-wide design requirements; extension needs explicit geometry/mesh/clearance verification')
MISSING=['Local/global thin-wall buckling and crippling','Supplier allowables, weld/HAZ, fatigue and joints','Hot/wet laminate/core/bond calibration and strength','Full-body stress, flexible modes, comfort and crashworthiness','Worn-wheel, bogie, rail and cassette swept clearance','Complete installed stock/mass/CG/inertia and manufacturing qualification']


def _reference(reference):
    if 'wheel_body' in reference or 'body_revision' in reference:raise ValueError('Supply the unchanged explicit base vehicle, not a revised child')
    if not reference.get('geometry_parts') or not reference.get('candidate_id'):raise ValueError('Explicit base vehicle and physical stock required')


def _parameters(p):
    wanted={'family','sill_width_m','sill_depth_m','sill_wall_m','material'}
    if set(p)!=wanted or p['family']!='finite_area_backed_sill_redistribution' or p['material']!='6082-T6-proposed':raise ValueError('Unsupported material/topology: create an evaluator-development task')
    for name in ('sill_width_m','sill_depth_m','sill_wall_m'):
        value=p[name];lo,hi=LIMITS[name]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not isfinite(value) or not lo<=value<=hi:raise ValueError('Outside explicit geometry adapter domain: '+name)
    if 2*p['sill_wall_m']>=min(p['sill_width_m'],p['sill_depth_m']):raise ValueError('Positive hollow section required')
    return deepcopy(p)


def _sills(vehicle):
    return [m for m in wheel_body._analysis_variant(vehicle)['members'] if m['id'].startswith('wheel-underframe/sill/')]


def _stock(sills,p):
    parts=[]
    for i,m in enumerate(sills):
        top=max(q['at_m'][2]+q['size_m'][2] for q in m['stock'])
        tube(parts,f'wheel-underframe/sill/redistribution/{i}',(m['start_m'][0],m['start_m'][1]-p['sill_width_m']/2,top-p['sill_depth_m']),m['length_m'],p['sill_width_m'],p['sill_depth_m'],p['sill_wall_m'])
    return parts


def _metrics(old,parts):
    new=body_frame.members_from_stock(parts);before=sum(m['mass_kg'] for m in old);after=sum(q['mass_kg'] for q in parts)
    return dict(sill_stock_mass_before_kg=before,sill_stock_mass_after_kg=after,sill_stock_delta_kg=after-before,
        vertical_I_ratio=sum(m['I_about_local_1_m4'] for m in new)/sum(m['I_about_local_1_m4'] for m in old),
        lateral_I_ratio=sum(m['I_about_local_2_m4'] for m in new)/sum(m['I_about_local_2_m4'] for m in old),
        vertical_I_per_mass_ratio=(sum(m['I_about_local_1_m4'] for m in new)/after)/(sum(m['I_about_local_1_m4'] for m in old)/before),
        minimum_nominal_sill_bottom_m=min(q['at_m'][2] for q in parts),
        sections=[{k:m[k] for k in ('id','area_m2','I_about_local_1_m4','I_about_local_2_m4','mass_kg','length_m','start_m','end_m','section')} for m in new],
        geometry_scope='Exact counted four-wall stock; I and mass are geometric quantities, not a whole-body stiffness, buckling or clearance pass')


def definitions(reference,root=ROOT):
    _reference(reference);baseline=joint_body.materialize_finite_body(reference,root=root);old=_sills(baseline);rows=[]
    for height,wall in ((.50,.006),(.60,.005),(.60,.008)):
        p=dict(family='finite_area_backed_sill_redistribution',sill_width_m=.18,sill_depth_m=height,sill_wall_m=wall,material='6082-T6-proposed');_parameters(p)
        row=dict(schema='osr-body-redistribution-definition/1',name=f'180x{height*1000:g}x{wall*1000:g}mm',parent_candidate_id=reference['candidate_id'],parameters=p,
            selection_purpose='next_experiment',model_limits=deepcopy(LIMITS),geometry_metrics=_metrics(old,_stock(old,p)),missing_gates=MISSING,
            advisory_policy=dict(historical_deflection_m=.0256,status='advisory',reason='Applicability and governing strength/gap/comfort limits need engineering policy; no historical evidence is changed'),**FLAGS)
        row['definition_id']=identity(row);rows.append(row)
    return rows


def _definition(reference,definition):
    value={k:v for k,v in definition.items() if k!='definition_id'}
    if identity(value)!=definition.get('definition_id') or definition.get('parent_candidate_id')!=reference['candidate_id']:raise ValueError('Mixed or mutated revision definition')
    return _parameters(definition['parameters'])


def materialize(reference,definition,root=ROOT):
    _reference(reference);p=_definition(reference,definition);v=joint_body.materialize_finite_body(reference,root=root);baseline_id=v['body_candidate_id'];old=_sills(v);oldids={q['id'] for m in old for q in m['stock']};new=_stock(old,p);metrics=_metrics(old,new);parts=[q for q in v['geometry_parts'] if q['id'] not in oldids]+new;delta=metrics['sill_stock_delta_kg']
    physical=dict(parent_candidate_id=reference['candidate_id'],parent_body_candidate_id=baseline_id,parameters=p,
        retained_joint_topology={k:x for k,x in joint_body.finite_parameters().items() if not k.startswith('sill_')},geometry_parts=wheel_body._physical_body_parts(parts),support_interface_id=v['support_component_id'])
    v['body_physical_definition']=physical;v['body_candidate_id']=identity(physical);v['candidate_id']=identity(dict(parent_candidate_id=reference['candidate_id'],body_candidate_id=v['body_candidate_id'],support_component_id=v['support_component_id'],propulsion_component_id=v['propulsion_component_id']));v['geometry_parts']=parts
    v['physical_definition']['body_revision']=dict(body_candidate_id=v['body_candidate_id'],parent_body_candidate_id=baseline_id,parameters=p);v['physical_definition']['geometry_definition_id']=identity(parts)
    for key in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car'):v['mass'][key]+=delta
    v['mass']['accounted_tare_kg_six_cars']=6*v['mass']['accounted_tare_kg_per_car'];v['mass']['located_material_kg']=sum(q['mass_kg'] for q in parts)
    v['axle_loads'].update(empty_kg_per_axle=v['mass']['accounted_tare_kg_per_car']/4,normal_kg_per_axle=v['mass']['accounted_cap_loaded_kg_per_car']/4,crowd_control_kg_per_axle=v['mass']['accounted_160_control_kg_per_car']/4)
    total_delta=sum(q['mass_kg'] for q in parts)-sum(q['mass_kg'] for q in reference['geometry_parts']);v['inventory']=[q for q in v['inventory'] if q['id']!='finite-backing-body-revision']+[dict(id='body-sill-redistribution',system='body',mass_kg=total_delta,evidence_class='exact-counted-stock-with-unqualified-strength-and-joints')]
    v['wheel_body']['parameters'].update(sill_depth_m=p['sill_depth_m'],sill_wall_m=p['sill_wall_m']);v['wheel_body']['stock_mass_delta_kg']=total_delta
    v['joint_body']['parameters']={**joint_body.finite_parameters(),'sill_depth_m':p['sill_depth_m'],'sill_wall_m':p['sill_wall_m']};v['joint_body']['net_body_stock_delta_kg']=total_delta
    v['wheel_body']['part_graph']=dict(parts=[dict(id=q['id'],source_part_id=q.get('source_part_id'),mass_kg=q['mass_kg'],material=q.get('material')) for q in parts],pad_connections=v['wheel_body']['pads'])
    v['body_revision']=dict(definition_id=definition['definition_id'],parameters=p,baseline_body_candidate_id=baseline_id,stock_mass_delta_kg=total_delta,sill_stock_delta_kg=delta,sill_sections=metrics['sections'],geometry_metrics=metrics,removed_sill_part_ids=sorted(oldids),missing_gates=MISSING,native_adapter=PRODUCER)
    v['source_sha256'][PRODUCER]=digest(__file__);v.update(FLAGS);v['evaluation_id']=identity(v);return v


def plan(reference,root=ROOT):
    rows=definitions(reference,root);ranked=sorted(rows,key=lambda r:(r['geometry_metrics']['sill_stock_delta_kg'],-r['geometry_metrics']['vertical_I_per_mass_ratio']));chosen=[ranked[0],max(rows,key=lambda r:r['geometry_metrics']['vertical_I_ratio'])]
    return dict(schema='osr-body-redistribution-plan/1',definitions=rows,selected_definition_ids=[r['definition_id'] for r in chosen],selection_purpose='next_experiment',ranking='Lowest counted sill mass then strongest vertical geometric inertia; no feasibility or whole-system optimum claim',
        maximum_native_jobs=6,jobs_per_candidate=3,case_labels=['normal','normal-fine','crowd'],mesh_override={'normal':.3,'normal-fine':.2,'crowd':.3},memory_mb=5120,worker_count=1,
        supported_variables=['Sill depth .35–.65m','Wall .004–.016m; width fixed .18m','Actual retained-frame/finite-backing stock and unchanged loading'],
        evaluator_development_tasks=['Different materials require constitutive/supplier/thermal/strength adapters','New panels/core/layups/topologies need independent coupons and native load-path adapters','Floor/roof/crossmember redistribution requires counted interfaces, aperture preservation and joint modelling'],**FLAGS)


def deck(candidate,definition,*,dx=.3,load='normal',asymmetric=False,braking=False,joint_factor=1.):
    p=_parameters(definition['parameters']);r=candidate.get('body_revision',{})
    if r.get('definition_id')!=definition.get('definition_id') or r.get('parameters')!=p or identity(candidate['body_physical_definition'])!=candidate['body_candidate_id']:raise ValueError('Mixed revision/body physical identity')
    if wheel_body._physical_body_parts(candidate['geometry_parts'])!=candidate['body_physical_definition']['geometry_parts']:raise ValueError('Actual body stock differs from candidate identity')
    for m in _sills(candidate):
        dim=m['section']['dimensions']
        if max(abs(a-b) for a,b in zip(dim,[p['sill_width_m'],p['sill_depth_m'],p['sill_wall_m'],p['sill_wall_m'],p['sill_wall_m'],p['sill_wall_m']]))>1e-8:raise ValueError('Declared sill section differs from actual stock')
    keys=dict(empty='accounted_tare_kg_per_car',normal='accounted_cap_loaded_kg_per_car',crowd='accounted_160_control_kg_per_car')
    if load not in keys:raise ValueError('Explicit unchanged body load required')
    variant=wheel_body._analysis_variant(candidate);mass=candidate['mass'][keys[load]]-6730.;raw,mesh=body_solid_frame.deck(variant,mass,dx,asymmetric=asymmetric,braking=braking,joint_factor=joint_factor)
    original=wheel_body._parse_nodes(raw);copy=deepcopy(candidate);copy['wheel_body']['pads']=[];raw,extra=wheel_body._sandwich(raw,variant,copy,dx);nodes=wheel_body._parse_nodes(raw);new_nodes={n:xyz for n,xyz in nodes.items() if n not in original};frame=body_frame._mesh(variant,dx);nbase=max(frame['nodes']);equations=[];records=[];used=set()
    for patch in candidate['joint_body']['finite_backing']['patches']:
        m=next(m for m in variant['members'] if m['id']==patch['post_id']);z=m['start_m'][2] if patch['end']==0 else m['end_m'][2];master=min(n for n,xyz in frame['nodes'].items() if abs(xyz[0]-m['start_m'][0])<1e-8 and abs(xyz[1]-m['start_m'][1])<1e-8 and abs(xyz[2]-z)<1e-8);origin=frame['nodes'][master];rot=nbase+master;x0,x1,z0,z1=patch['footprint_xz_m'];contacts=[]
        for n,xyz in new_nodes.items():
            if abs(xyz[1]-patch['post_face_y_m'])>1e-8 or not x0-1e-9<=xyz[0]<=x1+1e-9 or not z0-1e-9<=xyz[2]<=z1+1e-9:continue
            if n in used:raise ValueError('Overlapping finite backing transfer footprints')
            used.add(n);contacts.append(n);r=[xyz[j]-origin[j] for j in range(3)];cross={0:[(2,-r[2]),(3,r[1])],1:[(3,-r[0]),(1,r[2])],2:[(1,-r[1]),(2,r[0])]}
            for j in range(3):equations.append([(n,j+1,1.),(master,j+1,-1.)]+[(rot,d,c) for d,c in cross[j] if abs(c)>1e-12])
        if len(contacts)<8 or joint_body.joint_models.rank_and_work_checks(dict(transfer_points_m=[nodes[n] for n in contacts]))['rank']!=6:raise ValueError('Finite backing area is not represented')
        records.append(dict(pad_index=patch['pad_index'],contact_nodes=len(contacts),contact_area_m2=patch['contact_area_m2']))
    inserts=[]
    for eq in equations:inserts += ['*EQUATION',str(len(eq)),','.join(f'{n},{d},{c:.12g}' for n,d,c in eq)]
    ids=wheel_body._solid_element_ids(raw);inserts+=['*ELSET,ELSET=J_BODY_ALL']+[','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)];raw=raw.replace('*STEP','\n'.join(inserts)+'\n*STEP',1).replace('*END STEP','*EL PRINT,ELSET=J_BODY_ALL,TOTALS=ONLY\nELSE\n*END STEP')
    return raw,dict(**mesh,**extra,sprung_mass_kg=mass,load=load,body_candidate_id=candidate['body_candidate_id'],finite_area_transfer=records,finite_area_equations=len(equations),no_additional_global_supports=True,joint_hypothesis=candidate['joint_body']['joint_hypothesis'],mesh_target_dx_m=dx)


def _sources(candidate,root):
    sources={**candidate['source_sha256'],PRODUCER:digest(__file__)};joint_body._verify_sources(sources,root);joint_body._verify_loaded_sources(sources)
    if digest(joint_body.__file__)!=sources[joint_body.PRODUCER]:raise ValueError('Imported joint adapter differs from declared source')
    return sources


def run(candidate,definition,output,*,root=ROOT,case_labels=None,mesh_override=None,memory_mb=5120):
    if identity({k:v for k,v in definition.items() if k!='definition_id'})!=definition.get('definition_id'):raise ValueError('Mutated revision definition')
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh immutable body revision run required')
    override={'normal':.3,'normal-fine':.2,'crowd':.3} if mesh_override is None else mesh_override
    if mesh_override is None and case_labels is not None:override={k:v for k,v in override.items() if k in case_labels}
    modes=joint_body._evaluation_cases(False,case_labels,override)
    if len(modes)>3:raise ValueError('Maximum three native jobs per candidate')
    sources=_sources(candidate,root);source=digest(__file__);tool=dict(ccx_path='/usr/bin/ccx',ccx_sha256=digest('/usr/bin/ccx'),OMP_threads=1,RLIMIT_AS_bytes=joint_body._native_memory_limit(memory_mb),requested_memory_mb=memory_mb,timeout_s=150);output.mkdir(parents=True);(output/'candidate.json').write_bytes(encoded(candidate));(output/'definition.json').write_bytes(encoded(definition));cases=[]
    for name,load,dx,asym,brake,jf in modes:
        raw,meta=deck(candidate,definition,dx=dx,load=load,asymmetric=asym,braking=brake,joint_factor=jf);case=dict(case=name,mesh=meta,**joint_body._native_body(raw,output/name,tool));(output/name/'definition.json').write_bytes(encoded(meta))
        if case['execution']=='completed':
            case['force_balance_relative_error']=abs(case['support_reaction_z_N']+meta['applied_vertical_force_N'])/abs(meta['applied_vertical_force_N']);case.update(joint_body._energy_balance(raw,output/name/'body.dat'));case['historical_deflection_advisory']=dict(limit_m=.0256,actual_m=case['maximum_vertical_displacement_m'],comparison='below' if case['maximum_vertical_displacement_m']<=.0256 else 'above',disposition='advisory pending governing design policy')
        cases.append(case)
    refinement=wheel_body._displacement_refinement(cases);balanced=all(joint_body._case_valid(c) for c in cases);validity='mesh_confirmed' if balanced and refinement['status']=='pass' else 'nonconverged' if balanced and refinement['status']=='fail' else 'unconfirmed' if balanced else 'unknown'
    _sources(candidate,root)
    if digest(__file__)!=source or digest(tool['ccx_path'])!=tool['ccx_sha256']:raise ValueError('Revision producer or solver changed during execution')
    value=dict(schema='osr-body-redistribution-evaluation/1',candidate_id=candidate['candidate_id'],body_candidate_id=candidate['body_candidate_id'],definition_id=definition['definition_id'],parameters=definition['parameters'],execution='completed' if all(c['execution']=='completed' for c in cases) else 'completed_with_errors',numerical_validity=validity,engineering_screen='unknown',selection_purpose='next_experiment',advisory_policy=definition['advisory_policy'],displacement_refinement=refinement,cases=cases,native_jobs_used=len(cases),tool=tool,source_sha256=sources,missing_gates=MISSING,joint_hypothesis=candidate['joint_body']['joint_hypothesis'],**FLAGS)
    value['evaluation_id']=identity(value);(output/'result.json').write_bytes(encoded(value));manifest=dict(evaluation_id=value['evaluation_id'],candidate_id=candidate['candidate_id'],source_sha256=sources,tool=tool,files_sha256={q.relative_to(output).as_posix():digest(q) for q in output.rglob('*') if q.is_file()},**FLAGS);manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return value
