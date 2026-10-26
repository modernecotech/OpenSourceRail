"""Opt-in, physically counted four-bolt body transfer alternative.

The existing two-bolt model remains an immutable control. Four actual fastener
axes per pad make a rank-six transfer geometry; native stiffness still assumes
intact rigid shanks and no slip. This does not establish real joint stiffness,
fatigue, laminate bearing, safe modes or a complete equipped vehicle.
"""
from copy import deepcopy
from pathlib import Path
import re
import numpy as np
from math import isfinite
from engineering.station_rail import ROOT,FLAGS,body_frame,body_solid_frame
from engineering.station_rail.common import digest,identity,encoded
from engineering.station_rail.vehicle import box,cylinder
from engineering.design_search import wheel_body,joint_models

PRODUCER='engineering/design_search/joint_body.py'


def default_parameters():
    return dict(sill_depth_m=.35,sill_wall_m=.008,clamp_plate_thickness_m=.003,joint='four_bolt_rectangle',bolt_row_spacing_m=.04)


def _parameters(parameters):
    p=deepcopy(parameters)
    if set(p)!=set(default_parameters()) or p['joint']!='four_bolt_rectangle' or p['bolt_row_spacing_m']!=.04:raise ValueError('Explicit four-bolt physical family required')
    wheel_body._parameters(dict(family='participating_sandwich',**{k:p[k] for k in ('sill_depth_m','sill_wall_m','clamp_plate_thickness_m')}))
    return p


def _hardware(parts,thickness,row_spacing):
    posts=[m for m in body_frame.members_from_stock(parts) if m['axis']==2 and m['id'].startswith('comfort-shell/replacement-frame/') and '-post-' in m['id']]
    extras=[];holes=[];pads=[]
    for i,m in enumerate(posts):
        side=1 if m['start_m'][1]>0 else -1;outer=side*1.325;x=m['start_m'][0]
        w=min(.08,max(q['at_m'][0]+q['size_m'][0] for q in m['stock'])-min(q['at_m'][0] for q in m['stock']))
        for end,z in enumerate((m['start_m'][2]+.04,m['end_m'][2]-.04)):
            at=(x-w/2,outer if side>0 else outer-thickness,z-.04);prefix=f'wheel-shell-clamp/{i}/{end}'
            plate=box(prefix+'/plate',at,(w,thickness,.08),system='body-panel-connections');extras.append(plate)
            low=min(min(q['at_m'][1] for q in m['stock']),at[1]);high=max(max(q['at_m'][1]+q['size_m'][1] for q in m['stock']),at[1]+thickness)
            pad=dict(post_id=m['id'],end=end,side=side,x_m=x,z_m=z,reference_z_m=m['start_m'][2] if end==0 else m['end_m'][2],plate_id=plate['id'],bolt_axes=[],joint='four_bolt_rectangle')
            for bolt,(xx,zz) in enumerate((xx,zz) for xx in (x-w/4,x+w/4) for zz in (z-row_spacing/2,z+row_spacing/2)):
                name=prefix+f'/bolt/{bolt}';lowrod=low-.0075;highrod=high+.0015
                kwargs=dict(system='body-panel-connections')
                extras += [cylinder(name+'/shank',(xx,lowrod,zz),.004,highrod-lowrod,**kwargs),cylinder(name+'/head',(xx,highrod,zz),.007,.005,**kwargs),
                    cylinder(name+'/nut',(xx,low-.0075,zz),.007,.006,inner=.004,**kwargs),cylinder(name+'/washer-low',(xx,low-.0015,zz),.009,.0015,inner=.0045,**kwargs),cylinder(name+'/washer-high',(xx,high,zz),.009,.0015,inner=.0045,**kwargs)]
                holes.append(dict(x_m=xx,z_m=zz,y_low_m=low,y_high_m=high,radius_m=.0045));pad['bolt_axes'].append([xx,zz])
            pad['transfer_rank']=joint_models.rank_and_work_checks(dict(transfer_points_m=[[xx,side*(1.325+thickness),zz] for xx,zz in pad['bolt_axes']]))['rank'];pads.append(pad)
    return extras,holes,pads


def materialize_body(base_vehicle,parameters,root=ROOT):
    """Count fresh frame/floor fit plus new four-bolt pads; no inherited solve."""
    p=_parameters(parameters);frame_parameters=dict(family='frame_only',**{k:p[k] for k in ('sill_depth_m','sill_wall_m','clamp_plate_thickness_m')})
    v=wheel_body.materialize(base_vehicle,frame_parameters,root);hardware,holes,pads=_hardware(v['geometry_parts'],p['clamp_plate_thickness_m'],p['bolt_row_spacing_m'])
    parts,removed=wheel_body._drill(v['geometry_parts']+hardware,holes)
    for q in parts:
        if q.get('role')=='panel-side' and q.get('density_kg_m3')==1900:
            q['source_part_id']=q.get('source_part_id',q['id']);q['id']+='-balanced-crossply';q['material']='proposed-E-glass-epoxy-balanced-crossply';q['laminate_specification']=dict(angles_deg=[0,90,90,0],total_thickness_m=.002)
    delta=sum(q['mass_kg'] for q in parts)-sum(q['mass_kg'] for q in base_vehicle['geometry_parts']);extra=sum(q['mass_kg'] for q in parts)-sum(q['mass_kg'] for q in v['geometry_parts'])
    physical=dict(parent_candidate_id=base_vehicle['candidate_id'],parent_body_candidate_id=base_vehicle['body_candidate_id'],parameters=p,
        geometry_parts=wheel_body._physical_body_parts(parts),support_interface_id=v['support_component_id'])
    bodyid=identity(physical);v['body_candidate_id']=bodyid;v['candidate_id']=identity(dict(parent_candidate_id=base_vehicle['candidate_id'],body_candidate_id=bodyid,support_component_id=v['support_component_id'],propulsion_component_id=v['propulsion_component_id']))
    v['body_physical_definition']=physical;v['geometry_parts']=parts;v['physical_definition']['body_revision']=dict(body_candidate_id=bodyid,parent_body_candidate_id=base_vehicle['body_candidate_id'],parameters=p);v['physical_definition']['geometry_definition_id']=identity(parts)
    for key in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car'):v['mass'][key]+=extra
    v['mass']['accounted_tare_kg_six_cars']=6*v['mass']['accounted_tare_kg_per_car'];v['mass']['located_material_kg']=sum(q['mass_kg'] for q in parts)
    v['axle_loads'].update(empty_kg_per_axle=v['mass']['accounted_tare_kg_per_car']/4,normal_kg_per_axle=v['mass']['accounted_cap_loaded_kg_per_car']/4,crowd_control_kg_per_axle=v['mass']['accounted_160_control_kg_per_car']/4)
    v['inventory']=[q for q in v['inventory'] if q['id']!='wheel-body-revision']+[dict(id='four-bolt-body-revision',system='body',evidence_class='exact-counted-material-with-ideal-unqualified-joints',mass_kg=delta)]
    v['wheel_body'].update(parameters={**frame_parameters,'family':'participating_sandwich'},stock_mass_delta_kg=delta,shell_hardware_mass_kg=sum(q['mass_kg'] for q in hardware),drilled_material_removed_kg=removed,pads=pads,
        part_graph=dict(parts=[dict(id=q['id'],source_part_id=q.get('source_part_id'),mass_kg=q['mass_kg'],material=q.get('material')) for q in parts],pad_connections=pads),lineage='Fresh counted floor-fit/frame plus four-bolt clamp alternative; no two-bolt results inherited')
    v['joint_body']=dict(parameters=p,clamp_pads=len(pads),bolt_stacks=4*len(pads),hardware_stock_mass_kg=sum(q['mass_kg'] for q in hardware),drilled_material_removed_kg=removed,net_body_stock_delta_kg=delta,
        frame_floor_fit_stock_delta_kg=delta-extra,transfer_rank_histogram={str(r):sum(q['transfer_rank']==r for q in pads) for r in sorted({q['transfer_rank'] for q in pads})},
        joint_hypothesis='Four counted rigid intact bolt axes/pad; no slip/preload/bearing/contact calibration. Global hole stiffness omitted; exact physical material removed. Rank alone cannot establish global stability.',unknown_fitted_hardware_mass_kg=None)
    v['source_sha256'].update({PRODUCER:digest(__file__),joint_models.PRODUCER:digest(Path(__file__).with_name('joint_models.py'))});v.update(FLAGS);v['evaluation_id']=identity(v);return v


def body_deck(vehicle,parameters,*,dx=.6,load='normal',asymmetric=False,braking=False,joint_factor=1.):
    if parameters.get('joint')=='bonded_backing_insert_four_bolt':return _finite_body_deck(vehicle,parameters,dx=dx,load=load,asymmetric=asymmetric,braking=braking,joint_factor=joint_factor)
    p=_parameters(parameters)
    if p!=vehicle.get('joint_body',{}).get('parameters') or identity(vehicle['body_physical_definition'])!=vehicle['body_candidate_id']:raise ValueError('Mixed four-bolt physical identity/parameters')
    if wheel_body._physical_body_parts(vehicle['geometry_parts'])!=vehicle['body_physical_definition']['geometry_parts']:raise ValueError('Physical geometry differs from body definition')
    keys=dict(empty='accounted_tare_kg_per_car',normal='accounted_cap_loaded_kg_per_car',crowd='accounted_160_control_kg_per_car')
    if load not in keys:raise ValueError('Explicit actual body loading required')
    variant=wheel_body._analysis_variant(vehicle);mass=vehicle['mass'][keys[load]]-6730.
    raw,mesh=body_solid_frame.deck(variant,mass,dx,asymmetric=asymmetric,braking=braking,joint_factor=joint_factor)
    raw,extra=wheel_body._sandwich(raw,variant,vehicle,dx);mesh.update(extra);ids=wheel_body._solid_element_ids(raw)
    inserts=['*ELSET,ELSET=J_BODY_ALL']+[','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)]
    raw=raw.replace('*STEP','\n'.join(inserts)+'\n*STEP',1).replace('*END STEP','*EL PRINT,ELSET=J_BODY_ALL,TOTALS=ONLY\nELSE\n*END STEP')
    return raw,dict(**mesh,sprung_mass_kg=mass,load=load,body_candidate_id=vehicle['body_candidate_id'],joint=vehicle['joint_body'],modes='not requested; detailed full-body mass/model verification remains required',stress='not qualified; holes, bearing and actual joint stiffness unresolved')


def _energy_balance(raw,path):
    nodes=wheel_body._parse_nodes(raw);loads=[];reading=False
    for line in raw.splitlines():
        if line.startswith('*'):reading=line.upper().startswith('*CLOAD');continue
        if reading:
            f=line.split(',')
            if len(f)==3:loads.append((int(f[0]),int(f[1]),float(f[2])))
    u={};rf={};reading=None;text=Path(path).read_text()
    for line in text.splitlines():
        if 'displacements' in line.lower():reading=u
        elif 'forces' in line.lower():reading=rf
        f=line.split()
        if reading is not None and len(f)==4 and f[0].isdigit():reading[int(f[0])]=list(map(float,f[1:]))
    work=.5*sum(f*u[n][d-1] for n,d,f in loads);external=np.zeros(6);reaction=np.zeros(6)
    for n,d,f in loads:
        vector=np.zeros(3);vector[d-1]=f;external[:3]+=vector;external[3:]+=np.cross(nodes[n],vector)
    for n,vector in rf.items():reaction[:3]+=vector;reaction[3:]+=np.cross(nodes[n],vector)
    found=re.search(r'total internal energy[^\n]*\n\s*([\d.Ee+\-]+)',text,re.I);energy=float(found[1]) if found else None
    force_scale=max(float(np.linalg.norm(external[:3])),1e-12);force_error=float(max(abs((external+reaction)[:3])))/force_scale;moment_error=float(max(abs((external+reaction)[3:])))/(17*force_scale)
    return dict(external_work_J=work,solid_internal_energy_J=energy,energy_relative_residual=abs(work-energy)/abs(work) if energy is not None and work else None,
        applied_generalized_force=external.tolist(),support_generalized_reaction=reaction.tolist(),force_residual_N=(external+reaction)[:3].tolist(),moment_residual_Nm=(external+reaction)[3:].tolist(),
        force_balance_relative_error_all_axes=force_error,moment_balance_relative_error_all_axes=moment_error,moment_residual_normalisation_m=17.)


def _case_valid(case):
    if case.get('execution')!='completed':return False
    for key in ('force_balance_relative_error','force_balance_relative_error_all_axes','moment_balance_relative_error_all_axes','energy_relative_residual'):
        value=case.get(key)
        if not isinstance(value,(float,int)) or not isfinite(value) or value>=1e-4:return False
    return True


def _verify_sources(sources,root):
    for name,expected in sources.items():
        path=Path(root)/name
        if not path.is_file() or digest(path)!=expected:raise ValueError('Declared source differs from executed source root: '+name)


def _evaluation_cases(confirmation=False,case_labels=None,mesh_override=None):
    modes=[('normal','normal',.6,False,False,1.),('normal-fine','normal',.3,False,False,1.),('crowd','crowd',.6,False,False,1.)]
    if confirmation:modes += [('asymmetric-braking','normal',.6,True,True,1.),('joint-sensitivity','normal',.6,False,False,.1)]
    if case_labels is not None:
        selected=list(case_labels)
        if not selected or len(selected)!=len(set(selected)) or set(selected)-{m[0] for m in modes}:raise ValueError('Explicit unique available body cases required')
        modes=[m for m in modes if m[0] in selected]
    override={} if mesh_override is None else mesh_override
    if not isinstance(override,dict) or set(override)-{m[0] for m in modes}:raise ValueError('Mesh overrides must name selected body cases only')
    if any(isinstance(dx,bool) or not isinstance(dx,(int,float)) or dx not in (.6,.3,.2) for dx in override.values()):raise ValueError('Bounded body mesh targets are0.6,0.3,0.2m only')
    cases=[(name,load,override.get(name,dx),asym,brake,jf) for name,load,dx,asym,brake,jf in modes];targets={m[0]:m[2] for m in cases}
    if 'normal' in targets and 'normal-fine' in targets and targets['normal-fine']>=targets['normal']:raise ValueError('Normal-fine must be strictly finer than normal; duplicate meshes cannot confirm refinement')
    return cases


def evaluate_body(vehicle,parameters,output,*,root=ROOT,confirmation=False,case_labels=None,mesh_override=None):
    """Explicit opt-in native run. Coordinator freezes source before dispatch."""
    p=_finite_parameters(parameters) if parameters.get('joint')=='bonded_backing_insert_four_bolt' else _parameters(parameters);output=Path(output).resolve()
    modes=_evaluation_cases(confirmation,case_labels,mesh_override)
    if output.exists():raise ValueError('Fresh immutable native body directory required')
    sources={**vehicle['source_sha256'],PRODUCER:digest(__file__)};_verify_sources(sources,root)
    # Helpers are imported from this worktree. Their bytes must also equal the
    # declared root; isolated checkouts are not an OS-enforced sandbox.
    for module in (wheel_body,body_frame,body_solid_frame,joint_models):
        if digest(module.__file__)!=sources[module.PRODUCER]:raise ValueError('Imported helper differs from declared source: '+module.PRODUCER)
    output.mkdir(parents=True);(output/'candidate.json').write_bytes(encoded(vehicle));cases=[]
    tool=dict(ccx_path='/usr/bin/ccx',ccx_sha256=digest('/usr/bin/ccx'),OMP_threads=1,RLIMIT_AS_bytes=wheel_body._address_space_bound(),timeout_s=150)
    for name,load,dx,asym,brake,jf in modes:
        raw,definition=body_deck(vehicle,p,dx=dx,load=load,asymmetric=asym,braking=brake,joint_factor=jf)
        definition.update(mesh_target_dx_m=dx,asymmetric_load=asym,braking_load=brake,joint_modulus_factor=jf)
        r=dict(case=name,mesh=definition,**wheel_body._native(raw,output/name));(output/name/'definition.json').write_bytes(encoded(definition))
        if r['execution']=='completed':
            residual=abs(r['support_reaction_z_N']+definition['applied_vertical_force_N'])/abs(definition['applied_vertical_force_N']);r['force_balance_relative_error']=residual
            r.update(_energy_balance(raw,output/name/'body.dat'))
            r['engineering_screen']='fail' if residual<1e-4 and r['maximum_vertical_displacement_m']>.0256 else 'unknown'
        cases.append(r)
    refinement=wheel_body._displacement_refinement(cases);balanced=all(_case_valid(c) for c in cases);converged=balanced and refinement['status']=='pass'
    missing=['Native per-axis joint fixtures do not qualify actual preload, slip, bearing, fatigue or failure','Linear synthetic laminate/core/bond and rigid intact bolt transfer; no physical correlation','Full-body stress/buckling/flexible modes and all installed mass properties','Dynamic bogie/door/cassette clearance, manufacturing and fire/thermal evidence']
    value=dict(schema='osr-four-bolt-body-evaluation/1',candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],parameters=p,mesh_override=deepcopy(mesh_override or {}),selected_case_labels=[m[0] for m in modes],
        execution='completed' if all(c['execution']=='completed' for c in cases) else 'completed_with_errors',numerical_validity='mesh_confirmed' if converged else 'nonconverged' if balanced and refinement['status']=='fail' else 'unconfirmed' if balanced else 'unknown',
        engineering_screen='fail' if any(c.get('engineering_screen')=='fail' for c in cases) else 'unknown',displacement_refinement=refinement,cases=cases,
        native_jobs_used=len(cases),source_sha256=sources,tool=tool,constitutive_hypotheses={**wheel_body.CONSTITUTIVE,'joint':vehicle['joint_body']['joint_hypothesis']},joint_hypothesis=vehicle['joint_body']['joint_hypothesis'],missing_gates=missing,**FLAGS)
    if digest(__file__)!=sources[PRODUCER]:raise ValueError('Body adapter changed during execution')
    _verify_sources(sources,root)
    if digest(tool['ccx_path'])!=tool['ccx_sha256']:raise ValueError('Native body CCX changed during execution')
    value['tool_binary_unchanged']=True;value['evaluation_id']=identity(value);(output/'result.json').write_bytes(encoded(value));manifest=dict(evaluation_id=value['evaluation_id'],candidate_id=vehicle['candidate_id'],source_sha256=sources,tool=tool,files_sha256={q.relative_to(output).as_posix():digest(q) for q in output.rglob('*') if q.is_file()},**FLAGS);manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return value


def finite_parameters():
    return {**default_parameters(),'joint':'bonded_backing_insert_four_bolt','face_bond_thickness_m':.00025,'perimeter_bond_thickness_m':.00025,'insert_height_m':.08,'insert_material':'6082-T6-proposed'}


def _finite_parameters(parameters):
    p=deepcopy(parameters);wanted=finite_parameters()
    if set(p)!=set(wanted):raise ValueError('Explicit finite backing insert parameters required')
    for key in ('joint','face_bond_thickness_m','perimeter_bond_thickness_m','insert_height_m','insert_material'):
        if p[key]!=wanted[key]:raise ValueError('Outside counted finite insert family: '+key)
    _parameters({**{k:p[k] for k in default_parameters()},'joint':'four_bolt_rectangle'})
    return p


def _subtract_rectangle(rect,cut):
    x0,x1,z0,z1=rect;a,b,c,d=cut;a=max(a,x0);b=min(b,x1);c=max(c,z0);d=min(d,z1)
    if b-a<1e-10 or d-c<1e-10:return [rect]
    return [r for r in ((x0,a,z0,z1),(b,x1,z0,z1),(a,b,z0,c),(a,b,d,z1)) if r[1]-r[0]>1e-10 and r[3]-r[2]>1e-10]


def _subtract_box(bounds,cut):
    lo=[max(bounds[i],cut[i]) for i in (0,2,4)];hi=[min(bounds[i+1],cut[i+1]) for i in (0,2,4)]
    if any(b-a<1e-10 for a,b in zip(lo,hi)):return [bounds]
    x0,x1,y0,y1,z0,z1=bounds;a,c,e=lo;b,d,f=hi
    pieces=[(x0,a,y0,y1,z0,z1),(b,x1,y0,y1,z0,z1),(a,b,y0,c,z0,z1),(a,b,d,y1,z0,z1),(a,b,c,d,z0,e),(a,b,c,d,f,z1)]
    return [p for p in pieces if min(p[1]-p[0],p[3]-p[2],p[5]-p[4])>1e-10]


def materialize_finite_body(base_vehicle,parameters=None,root=ROOT):
    """Count real backing inserts and bonds; retain point-body as a control."""
    p=_finite_parameters(finite_parameters() if parameters is None else parameters);point_p={**{k:p[k] for k in default_parameters()},'joint':'four_bolt_rectangle'}
    v=materialize_body(base_vehicle,point_p,root);point_id=v['body_candidate_id'];variant=wheel_body._analysis_variant(v);posts={m['id']:m for m in variant['members']};patches=[];added=[];holes=[]
    for i,pad in enumerate(v['wheel_body']['pads']):
        m=posts[pad['post_id']];side=pad['side'];x=pad['x_m'];z=pad['z_m'];w=min(.08,max(q['at_m'][0]+q['size_m'][0] for q in m['stock'])-min(q['at_m'][0] for q in m['stock']))
        near=min(q['at_m'][1] for q in m['stock']) if side<0 else max(q['at_m'][1]+q['size_m'][1] for q in m['stock']);outer=side*1.325;lo,hi=sorted((near,outer));depth=hi-lo;h=p['insert_height_m'];b=p['face_bond_thickness_m'];e=p['perimeter_bond_thickness_m'];x0=x-w/2;z0=z-h/2
        if depth<=2*b or w<=2*e or h<=2*e:raise ValueError('Nonpositive finite backing material')
        patch=dict(pad_index=i,post_id=pad['post_id'],end=pad['end'],side=side,footprint_xz_m=[x0,x0+w,z0,z0+h],post_face_y_m=near,outer_face_y_m=outer,contact_area_m2=w*h,depth_m=depth)
        patches.append(patch);name='wheel-shell-clamp/finite/'+str(i)+'/plate-backing-insert'
        added.append(box(name,(x0+e,lo+b,z0+e),(w-2*e,depth-2*b,h-2*e),system='body-panel-connections'))
        strips=[((x0,lo,z0),(w,b,h)),((x0,hi-b,z0),(w,b,h)),((x0,lo+b,z0),(e,depth-2*b,h)),((x0+w-e,lo+b,z0),(e,depth-2*b,h)),((x0+e,lo+b,z0),(w-2*e,depth-2*b,e)),((x0+e,lo+b,z0+h-e),(w-2*e,depth-2*b,e))]
        for j,(at,size) in enumerate(strips):
            q=box(f'finite-body-bond/{i}/{j}',at,size,density=1100.,material='synthetic-intact-epoxy-bond',system='body-panel-connections');q['role']='panel-side';added.append(q)
        for xx,zz in pad['bolt_axes']:holes.append(dict(x_m=xx,z_m=zz,y_low_m=lo,y_high_m=hi,radius_m=.0045))
    # Restore only old panel-hole stock before replacing its complete local
    # sandwich patch. Post/outer-plate holes remain exactly as counted.
    parts=[];removed_panel_mass=0.;restored_panel_hole_mass=0.;changed_parents=[]
    for original in v['geometry_parts']:
        if original.get('role')!='panel-side':parts.append(deepcopy(original));continue
        q=deepcopy(original)
        if q.get('rectangular_cutouts'):raise ValueError('Finite insert requires explicit original panel prisms')
        if 'analysis_uncut_volume_m3' in q:
            restored_panel_hole_mass+=q['analysis_uncut_mass_kg']-q['mass_kg']
            q['volume_m3']=q.pop('analysis_uncut_volume_m3');q['mass_kg']=q.pop('analysis_uncut_mass_kg');q.pop('holes',None)
        x0,y0,z0=q['at_m'];lx,ly,lz=q['size_m'];rects=[(x0,x0+lx,z0,z0+lz)]
        for patch in patches:
            low,high=sorted((patch['post_face_y_m'],patch['outer_face_y_m']))
            if not min(y0+ly,high)>max(y0,low)+1e-10:continue
            if (y0<low-1e-8 or y0+ly>high+1e-8) and any(_subtract_rectangle(rect,patch['footprint_xz_m'])!=[rect] for rect in rects):raise ValueError('Panel layer only partially intersects finite backing depth; explicit3D cut required')
            rects=[r for old in rects for r in _subtract_rectangle(old,patch['footprint_xz_m'])]
        retained_volume=sum((b-a)*ly*(d-c) for a,b,c,d in rects)
        if abs(retained_volume-q['volume_m3'])<1e-10:parts.append(q);continue
        changed_parents.append(q.get('source_part_id',q['id']));removed_panel_mass+=q['mass_kg']-retained_volume*q['density_kg_m3']
        for j,(a,b,c,d) in enumerate(rects):
            r=deepcopy(q);r['id']=q.get('source_part_id',q['id'])+'-finite-segment-'+identity(rects)[:10]+f'-{j}';r['source_part_id']=q.get('source_part_id',q['id']);r['kind']='box';r['at_m']=[a,y0,c];r['size_m']=[b-a,ly,d-c];r['volume_m3']=(b-a)*ly*(d-c);r['mass_kg']=r['volume_m3']*r['density_kg_m3'];r['cg_m']=[a+(b-a)/2,y0+ly/2,c+(d-c)/2];r.pop('inertia_kg_m2',None);parts.append(r)
    # Bottom inserts cross12 existing thin top-lap strips. Define their exact
    # counted notches, rather than overlapping insert material or deleting a
    # complete floor joint. Their revised joint strength remains unqualified.
    trimmed=[];removed_lap_mass=0.;changed_laps=[]
    for q in parts:
        if '/lap/top/' not in q['id']:trimmed.append(q);continue
        if q.get('kind')!='box' or q.get('holes') or q.get('rectangular_cutouts'):raise ValueError('Lap notch requires an explicit simple parent prism')
        x,y,z=q['at_m'];lx,ly,lz=q['size_m'];bounds=[(x,x+lx,y,y+ly,z,z+lz)]
        for patch in patches:
            a,b,c,d=patch['footprint_xz_m'];lo,hi=sorted((patch['post_face_y_m'],patch['outer_face_y_m']));cut=(a,b,lo,hi,c,d);bounds=[p for old in bounds for p in _subtract_box(old,cut)]
        volume=sum((b-a)*(d-c)*(f-e) for a,b,c,d,e,f in bounds)
        if abs(volume-q['volume_m3'])<1e-12:trimmed.append(q);continue
        removed_lap_mass+=q['mass_kg']-volume*q['density_kg_m3'];changed_laps.append(q['id'])
        for k,(a,b,c,d,e,f) in enumerate(bounds):
            r=deepcopy(q);r['id']=q['id']+'-finite-notch-'+identity(bounds)[:10]+f'-{k}';r['source_part_id']=q.get('source_part_id',q['id']);r['at_m']=[a,c,e];r['size_m']=[b-a,d-c,f-e];r['volume_m3']=(b-a)*(d-c)*(f-e);r['mass_kg']=r['volume_m3']*r['density_kg_m3'];r['cg_m']=[(a+b)/2,(c+d)/2,(e+f)/2];r.pop('inertia_kg_m2',None);trimmed.append(r)
    parts=trimmed;added,insert_hole_mass=wheel_body._drill(added,holes);parts.extend(added)
    previous_mass=sum(q['mass_kg'] for q in v['geometry_parts']);extra=sum(q['mass_kg'] for q in parts)-previous_mass;delta=sum(q['mass_kg'] for q in parts)-sum(q['mass_kg'] for q in base_vehicle['geometry_parts'])
    physical=dict(parent_candidate_id=base_vehicle['candidate_id'],parent_body_candidate_id=base_vehicle['body_candidate_id'],point_transfer_control_body_id=point_id,parameters=p,geometry_parts=wheel_body._physical_body_parts(parts),support_interface_id=v['support_component_id'])
    v['geometry_parts']=parts;v['body_physical_definition']=physical;v['body_candidate_id']=identity(physical);v['candidate_id']=identity(dict(parent_candidate_id=base_vehicle['candidate_id'],body_candidate_id=v['body_candidate_id'],support_component_id=v['support_component_id'],propulsion_component_id=v['propulsion_component_id']))
    v['physical_definition']['body_revision']=dict(body_candidate_id=v['body_candidate_id'],parent_body_candidate_id=base_vehicle['body_candidate_id'],parameters=p);v['physical_definition']['geometry_definition_id']=identity(parts)
    for key in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car'):v['mass'][key]+=extra
    v['mass']['accounted_tare_kg_six_cars']=6*v['mass']['accounted_tare_kg_per_car'];v['mass']['located_material_kg']=sum(q['mass_kg'] for q in parts)
    v['axle_loads'].update(empty_kg_per_axle=v['mass']['accounted_tare_kg_per_car']/4,normal_kg_per_axle=v['mass']['accounted_cap_loaded_kg_per_car']/4,crowd_control_kg_per_axle=v['mass']['accounted_160_control_kg_per_car']/4)
    v['inventory']=[q for q in v['inventory'] if q['id']!='four-bolt-body-revision']+[dict(id='finite-backing-body-revision',system='body',mass_kg=delta,evidence_class='counted-stock-with-synthetic-intact-bond-and-rigid-post-face')]
    hypothesis='Explicit counted aluminium backing inserts, face/perimeter bonds and four bolt stacks per pad; intact no-slip perfect bonds. Finite post-face area follows existing frame section translation/rotation; local post-wall/bearing compliance and bolt preload/slip/failure are not resolved.'
    v['joint_body'].update(parameters=p,net_body_stock_delta_kg=delta,finite_backing=dict(patches=patches,added_stock_mass_kg=sum(q['mass_kg'] for q in added),removed_restored_panel_mass_kg=removed_panel_mass,restored_previous_panel_hole_mass_kg=restored_panel_hole_mass,removed_lap_notch_mass_kg=removed_lap_mass,changed_lap_parent_ids=changed_laps,new_insert_hole_mass_kg=insert_hole_mass,point_control_body_id=point_id,changed_panel_parent_ids=sorted(set(changed_parents)),material='6082-T6-proposed',bond_material='synthetic-intact-epoxy-bond'),joint_hypothesis=hypothesis)
    v['wheel_body'].update(stock_mass_delta_kg=delta,lineage='New finite-area backed four-bolt family; old point-control retained, no inherited numerical results',part_graph=dict(parts=[dict(id=q['id'],source_part_id=q.get('source_part_id'),mass_kg=q['mass_kg'],material=q.get('material')) for q in parts],pad_connections=v['wheel_body']['pads']))
    v['source_sha256'][PRODUCER]=digest(__file__);v['evaluation_id']=identity(v);return v


def _finite_body_deck(vehicle,parameters,*,dx=.6,load='normal',asymmetric=False,braking=False,joint_factor=1.):
    p=_finite_parameters(parameters)
    if p!=vehicle.get('joint_body',{}).get('parameters') or identity(vehicle['body_physical_definition'])!=vehicle['body_candidate_id']:raise ValueError('Mixed finite backing physical identity')
    if wheel_body._physical_body_parts(vehicle['geometry_parts'])!=vehicle['body_physical_definition']['geometry_parts']:raise ValueError('Finite backing physical stock differs')
    keys=dict(empty='accounted_tare_kg_per_car',normal='accounted_cap_loaded_kg_per_car',crowd='accounted_160_control_kg_per_car')
    if load not in keys:raise ValueError('Explicit body load required')
    variant=wheel_body._analysis_variant(vehicle);mass=vehicle['mass'][keys[load]]-6730.;raw,mesh=body_solid_frame.deck(variant,mass,dx,asymmetric=asymmetric,braking=braking,joint_factor=joint_factor)
    original_nodes=wheel_body._parse_nodes(raw);copy=deepcopy(vehicle);copy['wheel_body']['pads']=[];raw,extra=wheel_body._sandwich(raw,variant,copy,dx);nodes=wheel_body._parse_nodes(raw);new_nodes={n:xyz for n,xyz in nodes.items() if n not in original_nodes};frame=body_frame._mesh(variant,dx);nbase=max(frame['nodes']);equations=[];records=[];used=set()
    for patch in vehicle['joint_body']['finite_backing']['patches']:
        pad=vehicle['wheel_body']['pads'][patch['pad_index']];m=next(m for m in variant['members'] if m['id']==patch['post_id']);z=m['start_m'][2] if patch['end']==0 else m['end_m'][2]
        refs=[n for n,xyz in frame['nodes'].items() if abs(xyz[0]-m['start_m'][0])<1e-8 and abs(xyz[1]-m['start_m'][1])<1e-8 and abs(xyz[2]-z)<1e-8]
        master=min(refs);origin=frame['nodes'][master];rot=nbase+master;x0,x1,z0,z1=patch['footprint_xz_m'];contacts=[]
        for n,xyz in new_nodes.items():
            if abs(xyz[1]-patch['post_face_y_m'])>1e-8 or not x0-1e-9<=xyz[0]<=x1+1e-9 or not z0-1e-9<=xyz[2]<=z1+1e-9:continue
            if n in used:raise ValueError('Overlapping finite backing transfer footprints')
            used.add(n);contacts.append(n);r=[xyz[j]-origin[j] for j in range(3)];cross={0:[(2,-r[2]),(3,r[1])],1:[(3,-r[0]),(1,r[2])],2:[(1,-r[1]),(2,r[0])]}
            for j in range(3):equations.append([(n,j+1,1.),(master,j+1,-1.)]+[(rot,d,c) for d,c in cross[j] if abs(c)>1e-12])
        if len(contacts)<8 or joint_models.rank_and_work_checks(dict(transfer_points_m=[nodes[n] for n in contacts]))['rank']!=6:raise ValueError('Finite transfer face missing positive-area mesh support')
        records.append(dict(pad_index=patch['pad_index'],contact_nodes=len(contacts),contact_area_m2=patch['contact_area_m2'],post_id=patch['post_id']))
    inserts=[]
    for eq in equations:inserts += ['*EQUATION',str(len(eq)),','.join(f'{n},{d},{c:.12g}' for n,d,c in eq)]
    ids=wheel_body._solid_element_ids(raw);inserts+=['*ELSET,ELSET=J_BODY_ALL']+[','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)]
    raw=raw.replace('*STEP','\n'.join(inserts)+'\n*STEP',1).replace('*END STEP','*EL PRINT,ELSET=J_BODY_ALL,TOTALS=ONLY\nELSE\n*END STEP')
    return raw,dict(**mesh,**extra,sprung_mass_kg=mass,load=load,body_candidate_id=vehicle['body_candidate_id'],finite_area_transfer=records,finite_area_equations=len(equations),no_additional_global_supports=True,joint_hypothesis=vehicle['joint_body']['joint_hypothesis'],stress='Hole bearing/adhesive peel/post-wall stress and strength are held',modes='Not computed; complete installed mass/mode validation held')
