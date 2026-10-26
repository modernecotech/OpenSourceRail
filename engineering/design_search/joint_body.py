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


def evaluate_body(vehicle,parameters,output,*,root=ROOT,confirmation=False):
    """Explicit opt-in native run. Coordinator freezes source before dispatch."""
    p=_parameters(parameters);output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh immutable native body directory required')
    sources={**vehicle['source_sha256'],PRODUCER:digest(__file__)};_verify_sources(sources,root)
    # Helpers are imported from this worktree. Their bytes must also equal the
    # declared root; isolated checkouts are not an OS-enforced sandbox.
    for module in (wheel_body,body_frame,body_solid_frame,joint_models):
        if digest(module.__file__)!=sources[module.PRODUCER]:raise ValueError('Imported helper differs from declared source: '+module.PRODUCER)
    output.mkdir(parents=True);(output/'candidate.json').write_bytes(encoded(vehicle));cases=[]
    tool=dict(ccx_path='/usr/bin/ccx',ccx_sha256=digest('/usr/bin/ccx'),OMP_threads=1,RLIMIT_AS_bytes=wheel_body._address_space_bound(),timeout_s=150)
    modes=[('normal','normal',.6,False,False,1.),('normal-fine','normal',.3,False,False,1.),('crowd','crowd',.6,False,False,1.)]
    if confirmation:modes += [('asymmetric-braking','normal',.6,True,True,1.),('joint-sensitivity','normal',.6,False,False,.1)]
    for name,load,dx,asym,brake,jf in modes:
        raw,definition=body_deck(vehicle,p,dx=dx,load=load,asymmetric=asym,braking=brake,joint_factor=jf)
        r=dict(case=name,mesh=definition,**wheel_body._native(raw,output/name));(output/name/'definition.json').write_bytes(encoded(definition))
        if r['execution']=='completed':
            residual=abs(r['support_reaction_z_N']+definition['applied_vertical_force_N'])/abs(definition['applied_vertical_force_N']);r['force_balance_relative_error']=residual
            r.update(_energy_balance(raw,output/name/'body.dat'))
            r['engineering_screen']='fail' if residual<1e-4 and r['maximum_vertical_displacement_m']>.0256 else 'unknown'
        cases.append(r)
    refinement=wheel_body._displacement_refinement(cases);balanced=all(_case_valid(c) for c in cases);converged=balanced and refinement['status']=='pass'
    missing=['Native per-axis joint fixtures do not qualify actual preload, slip, bearing, fatigue or failure','Linear synthetic laminate/core/bond and rigid intact bolt transfer; no physical correlation','Full-body stress/buckling/flexible modes and all installed mass properties','Dynamic bogie/door/cassette clearance, manufacturing and fire/thermal evidence']
    value=dict(schema='osr-four-bolt-body-evaluation/1',candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],parameters=p,
        execution='completed' if all(c['execution']=='completed' for c in cases) else 'completed_with_errors',numerical_validity='mesh_confirmed' if converged else 'nonconverged' if balanced else 'unknown',
        engineering_screen='fail' if any(c.get('engineering_screen')=='fail' for c in cases) else 'unknown',displacement_refinement=refinement,cases=cases,
        native_jobs_used=len(cases),source_sha256=sources,tool=tool,constitutive_hypotheses=wheel_body.CONSTITUTIVE,joint_hypothesis=vehicle['joint_body']['joint_hypothesis'],missing_gates=missing,**FLAGS)
    if digest(__file__)!=sources[PRODUCER]:raise ValueError('Body adapter changed during execution')
    _verify_sources(sources,root)
    if digest(tool['ccx_path'])!=tool['ccx_sha256']:raise ValueError('Native body CCX changed during execution')
    value['tool_binary_unchanged']=True;value['evaluation_id']=identity(value);(output/'result.json').write_bytes(encoded(value));manifest=dict(evaluation_id=value['evaluation_id'],candidate_id=vehicle['candidate_id'],source_sha256=sources,tool=tool,files_sha256={q.relative_to(output).as_posix():digest(q) for q in output.rglob('*') if q.is_file()},**FLAGS);manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return value
