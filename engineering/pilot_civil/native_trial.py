"""Source-frozen fresh SolidCraft/FieldCraft/CalculiX pilot trials.

Uses generic bounded native adapters, never the historical viaduct admission
rule or its selected loads. Results keep the new civil and system identities.
"""
from copy import deepcopy
from math import fsum
from pathlib import Path
import json, shutil, time
from engineering.design_search.craft_backends import native, solidcraft, freecad_reference
from engineering.design_search.craft_backends import viaduct_fem as fem
from engineering.design_search.craft_backends.fieldcraft import batch_results
from . import FLAGS, ROOT
from .design import G, identity, seal, sources, validate_train, _response
from .assembly import cad_case, scene


def source_context(root=ROOT):
    values=sources(root)
    for n in ('native.py','solidcraft.py','freecad_reference.py','viaduct_fem.py','fieldcraft.py','tools.json'):
        path='engineering/design_search/craft_backends/'+n;values[path]=native.digest(Path(root)/path)
    return values


def generate(result,folder,*,gross_beam_only=False):
    out=Path(folder).resolve();out.mkdir(parents=True,exist_ok=False)
    case=cad_case(result,gross_beam_only=gross_beam_only);script=out/'commands.json'
    native.write(script,solidcraft.script_for(case));native.write(out/'case.json',case)
    generated=out/'execution'
    run=native.run('solidcraft',['run',script,'--save',generated/'assembly.sc','--out',generated/'assembly.step','--results','--json-out',generated/'results.json'],generated,timeout_s=58,memory_mb=2048,read_roots=(out,))
    artifact=dict(schema='osr-pilot-civil-cad/1',candidate_id=result['civil_candidate_id'],system_candidate_id=result['system_candidate_id'],component_geometry_id=case['component_geometry_id'],execution=run,gross_beam_only=gross_beam_only,**FLAGS)
    if run['execution']=='executed':
        artifact.update(step_path=str(generated/'assembly.step'),step_sha256=native.digest(generated/'assembly.step'),native_design_path=str(generated/'assembly.sc'),native_design_sha256=native.digest(generated/'assembly.sc'))
        try:
            measured=solidcraft.parse_measurements(json.loads((generated/'results.json').read_bytes()));artifact['measurements']=measured
            if gross_beam_only:
                want=result['quantities']['concrete_beam_m3'];got=measured['total_volume_m3']
                artifact['volume_relative_error']=abs(got-want)/want;artifact['gross_volume_screen_passed']=artifact['volume_relative_error']<=1e-6
        except (ValueError,KeyError,TypeError) as e:artifact['measurement_failure']=str(e)
    native.write(out/'artifact.json',seal(artifact));return artifact


def prepare(result,train,artifact,load_name,*,support_mode='patch',resources=None):
    if result['evaluation_id']!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):raise ValueError('Civil evaluation seal changed')
    if train['evaluation_id']!=identity({k:v for k,v in train.items() if k!='evaluation_id'}):raise ValueError('Axle evaluation seal changed')
    if artifact['evaluation_id']!=identity({k:v for k,v in artifact.items() if k!='evaluation_id'}):raise ValueError('CAD artifact seal changed')
    if result['system_candidate_id']!=train['candidate_id'] or result['input_load_evaluation_id']!=train['evaluation_id']:raise ValueError('Mixed system or axle evaluation')
    if artifact['candidate_id']!=result['civil_candidate_id'] or not artifact.get('gross_beam_only'):raise ValueError('Exact same-civil gross CAD required')
    if artifact['component_geometry_id']!=scene(result,gross_beam_only=True)['component_geometry_id']:raise ValueError('Physical CAD projection changed')
    if native.digest(artifact['step_path'])!=artifact['step_sha256']:raise ValueError('Exact STEP bytes changed')
    contract=result['physical_definition']['rail_interface']['track_interface']
    if train['track_interface']!=contract:raise ValueError('Native vehicle/civil track interface mismatch')
    load=next(l for l in train['load_cases'] if l['name']==load_name);d=next(d for d in result['load_demands'] if d['name']==load_name)
    shift=d['critical_train_translation_m']['deflection_m'];factor=result['policy']['dynamic_axle_factor']
    points=[dict(x_m=a['x_m']+shift,force_N=a['vertical_force_N']*factor) for a in load['axles'] if 0<=a['x_m']+shift<=20]
    if any(not .15<=a['x_m']<=19.85 for a in points):raise ValueError('Critical axle patch clips beam end; request different pose, not invented load')
    spec=dict(schema='osr-pilot-civil-fem/1',candidate_id=result['civil_candidate_id'],system_candidate_id=train['candidate_id'],input_load_evaluation_id=train['evaluation_id'],load_name=load_name,
        component_geometry_id=artifact['component_geometry_id'],cad_artifact=deepcopy(artifact),nominal_quantity=result['section']['quantities'],superimposed_mass_kg=result['quantities']['accounted_superstructure_kg']-result['quantities']['nominal_concrete_mass_kg'],
        live_pose=dict(points=points,translation_m=shift),track_interface=deepcopy(contract),
        rail_patch_hypothesis=dict(centres_y_m=contract['nominal_contact_centres_y_m'],length_m=.30,width_m=.20,
            scope='Concrete load spread over nominal fastener footprint; not wheel tread contact stress or actual rail/fastener load-transfer verification'),support_hypothesis=dict(patches_x_m=[[.125,.575],[19.425,19.875]],patch_y_m=[-.25,.25],scope='Bottom horizontal finite patches centred on actual 0.35/19.65 m bearing lines. Two physical transverse bearings idealised as continuous bottom patch.'),
        material_hypothesis=dict(young_Pa=35e9,poisson=.2,density_kg_m3=2500.),
        evaluation_domain='Perfectly bonded gross continuum, no cracking/prestress/reinforcement/joint/soil stiffness credit. Axle and dead gravity including declared conductor eccentricity; lateral train inertia and handling remain separate analytical screens.',
        resource_request=dict(max_cells=20000,cpu_s_each_process=60,wall_s_each_process=58,memory_mib_each_process=2048),**FLAGS)
    if support_mode not in ('patch','rotation-free-line'):raise ValueError('Declared support idealisation required')
    if support_mode=='rotation-free-line':
        size=result['physical_definition']['bearing_layout']['size_m'];offsets=result['physical_definition']['bearing_layout']['offset_y_m']
        spec['support_hypothesis']=dict(mode=support_mode,bottom_z_m=result['section']['zmin_m'],lines_x_m=result['policy']['support']['bearing_lines_x_m'],
            bearing_intervals_y_m=[[y-size[1]/2,y+size[1]/2] for y in offsets],
            scope='Zero vertical displacement only on exact transverse bottom bearing lines at0.35/19.65m. Rotation about transverse axis is free; no finite longitudinal patch clamp. Real finite bearing contact/compliance unresolved.')
    line=result['quantities'].get('line_equipment_dead_mass_kg',0.)
    if line:
        spec['line_equipment_gravity']=dict(mass_kg=line,lateral_y_m=result['physical_definition']['wayside_conductor_and_supports']['lateral_offset_from_track_centre_m'],spread_width_m=.10,
            basis='Conductor/support gravity at actual declared lateral offset; not smeared into centred reserve. Electrical protection/ampacity evidence separate.')
    if resources is not None:
        request=deepcopy(resources)
        if set(request)!=set(spec['resource_request']):raise ValueError('Complete explicit native budget required')
        if not 1<=request['max_cells']<=50000 or not 1<=request['cpu_s_each_process']<=75 or not 1<=request['wall_s_each_process']<=100 or not 256<=request['memory_mib_each_process']<=3072:raise ValueError('Native budget exceeds approved bounded pilot domain')
        # Existing POSIX wrappers set CPU hard limit to timeout+2. A lower
        # actual wall limit keeps both beneath the explicit CPU allocation.
        if request['wall_s_each_process']+2>request['cpu_s_each_process']:raise ValueError('Wall timeout must leave POSIX CPU hard limit within allocation')
        spec['resource_request']=request
    return seal(spec,'input_id')


def load_model(spec,model):
    """Assemble body gravity, reserve UDL and the exact candidate axle patches."""
    import numpy as np
    fem.validate_elements(model);nodes=model['nodes'];forces={int(n):0. for n in nodes};volume=0.
    for _,e in fem.numeric_items(model['elements']):
        xyz=np.array([nodes[str(n)] for n in e[:4]]);v=abs(float(np.linalg.det((xyz[1:]-xyz[0]).T)))/6;volume+=v
        for n,w in zip(e,[-1/20]*4+[1/5]*6):forces[n]-=2500*G*v*w
    want=spec['nominal_quantity']['total_nominal_volume_m3']
    if abs(volume-want)>1e-6*want:raise ValueError('Exact mesh stock volume differs')
    def add(rect,total):
        for n,f in fem.surface_forces(model,rect,total).items():forces[n]+=f
    line=spec.get('line_equipment_gravity',{});line_mass=line.get('mass_kg',0.)
    add([0,20,-1,1],(spec['superimposed_mass_kg']-line_mass)*G)
    if line_mass:
        y=line['lateral_y_m'];half=line['spread_width_m']/2
        if not -1<=y-half<y+half<=1:raise ValueError('Conductor load spread lies outside actual deck')
        add([0,20,y-half,y+half],line_mass*G)
    for n,f in live_forces(spec,model).items():forces[n]+=f
    depth=min(v[2] for v in nodes.values());supports=[]
    support=spec['support_hypothesis']
    if support.get('mode')=='rotation-free-line':
        for x in support['lines_x_m']:
            ns=[int(n) for n,v in nodes.items() if abs(v[0]-x)<1e-8 and abs(v[2]-depth)<1e-8 and any(lo-1e-8<=v[1]<=hi+1e-8 for lo,hi in support['bearing_intervals_y_m'])]
            if len(ns)<4:raise ValueError('Exact rotation-free bearing lines unresolved in actual mesh')
            supports.append(ns)
    else:
        for lo,hi in support['patches_x_m']:
            ns=[int(n) for n,v in nodes.items() if lo-1e-8<=v[0]<=hi+1e-8 and abs(v[1])<=.25+1e-8 and abs(v[2]-depth)<1e-8]
            if len(ns)<2:raise ValueError('Physical bearing patch unresolved in actual mesh')
            supports.append(ns)
    anchor=[min(ns,key=lambda n:sum((nodes[str(n)][j]-v[j])**2 for j in range(3))) for ns,v in zip(supports,([.35,0,depth],[19.65,0,depth]))]
    probe=min(nodes,key=lambda n:sum((nodes[n][j]-[10,0,0][j])**2 for j in range(3)))
    if max(abs(a-b) for a,b in zip(nodes[probe],[10,0,0]))>1e-7:raise ValueError('Exact deck observation missing')
    applied=[0.,0.,fsum(forces.values())];moment=[fsum(nodes[str(n)][1]*f for n,f in forces.items()),-fsum(nodes[str(n)][0]*f for n,f in forces.items()),0.]
    model.update(nodal_load_N={str(n):[0.,0.,f] for n,f in forces.items()},support_nodes=supports,anchor_nodes=anchor,probe_nodes=[int(probe)],probe_xyz_m=[[10.,0.,0.]],applied_N=applied,applied_moment_Nm=moment,mesh_volume_m3=volume,
        stress_scope='Exact midspan deck sampled stress for cross-comparison; restraint/patch peak is not concrete strength evidence')
    expected=volume*2500*G+spec['superimposed_mass_kg']*G+fsum(a['force_N'] for a in spec['live_pose']['points'])
    if abs(-applied[2]-expected)>1e-8*expected:raise ValueError('Assembled candidate force balance fails')
    return model


BEARING_LINES_WORKER=r'''
# Embed transverse support lines into the exact imported bottom surface. A
# longitudinal band of fixed U3 would introduce an unintended bending couple.
depth=min(gmsh.model.getBoundingBox(3,t)[2] for d,t in gmsh.model.getEntities(3))
# OCC bounding boxes carry geometric tolerance; obtain the exact planar bottom.
bottom=[t for d,t in gmsh.model.getEntities(2) if abs(gmsh.model.occ.getCenterOfMass(d,t)[2]-request['bottom_z_m'])<1e-8]
for x in request['bearing_lines_x_m']:
 for lo,hi in request['bearing_intervals_y_m']:
  candidates=[t for t in bottom if gmsh.model.isInside(2,t,[x,(lo+hi)/2,request['bottom_z_m']])]
  if len(candidates)!=1:raise ValueError('Unique exact bottom bearing surface required')
  a=gmsh.model.occ.addPoint(x,lo,request['bottom_z_m']);b=gmsh.model.occ.addPoint(x,hi,request['bottom_z_m'])
  edge=gmsh.model.occ.addLine(a,b);gmsh.model.occ.synchronize();gmsh.model.mesh.embed(1,[edge],2,candidates[0])
'''


def mesh_worker(spec):
    worker=fem.GMSH_WORKER.replace("faces=[]",f"if len(elements)>{spec['resource_request']['max_cells']}:raise ValueError('Cell budget exceeded; execution retained')\nfaces=[]")
    if spec['support_hypothesis'].get('mode')=='rotation-free-line':
        worker=worker.replace("gmsh.model.mesh.embed(0,[pt],2,inside[0])", "gmsh.model.mesh.embed(0,[pt],2,inside[0])\n"+BEARING_LINES_WORKER)
    return worker


def live_forces(spec,model):
    """Split each full axle once over explicitly aligned concrete load patches."""
    from .design import validate_track_interface
    validate_track_interface(spec['track_interface'])
    patch=spec['rail_patch_hypothesis'];centres=spec['track_interface']['nominal_contact_centres_y_m']
    if patch['centres_y_m']!=centres or not 0<patch['length_m']<=.30 or not 0<patch['width_m']<=.20:raise ValueError('Native rail patch differs from declared interface')
    forces={};hx=patch['length_m']/2;hy=patch['width_m']/2
    for a in spec['live_pose']['points']:
        for y in centres:
            for n,f in fem.surface_forces(model,[a['x_m']-hx,a['x_m']+hx,y-hy,y+hy],a['force_N']/2).items():forces[n]=forces.get(n,0.)+f
    return forces


def commands(spec,model,import_path):
    """Pilot-local rail loading; historical generic +/-600mm defaults untouched."""
    line=spec.get('line_equipment_gravity',{});mass=line.get('mass_kg',0.)
    adjusted=deepcopy(spec);adjusted['superimposed_mass_kg']-=mass
    # Generic code retains its historical rail spacing. Suppress its live loads
    # and install the exact same pilot-local nodal traction used by CalculiX.
    adjusted['live_pose']['points']=[]
    commands=fem.commands(adjusted,model,import_path)
    forces=live_forces(spec,model)
    if mass:
        y=line['lateral_y_m'];half=line['spread_width_m']/2
        for n,f in fem.surface_forces(model,[0,20,y-half,y+half],mass*G).items():forces[n]=forces.get(n,0.)+f
    extra=[];names=[]
    for n,f in sorted(forces.items()):
        if abs(f)<1e-12:continue
        name='PilotLoad'+str(n);names.append(name)
        extra.extend([dict(command='model.set.create',params=dict(name=name,nodes=[n])),dict(command='model.load.create',params=dict(name=name,type='force',target=dict(set=name),vector=[0.,0.,f],distribution='total'))])
    index=next(i for i,c in enumerate(commands) if c['command']=='model.step.create')
    commands[index]['params']['loads']+=names;commands[index:index]=extra
    # Bound undo snapshots and scratch disk use. Only private checkpoints are
    # overwritten; input commands and final evidence remain immutable.
    plain=[c for c in commands[:-5] if c['command'] not in ('file.save','file.open')]
    prepared=[]
    for i,c in enumerate(plain,1):
        prepared.append(c)
        if i%8==0:
            path=Path(import_path).parent/'fieldcraft'/('rolling-'+str((i//8)%8)+'.fieldcraft')
            prepared.extend([dict(command='file.save',params=dict(path=str(path),results=False)),dict(command='file.open',params=dict(path=str(path)))])
    return prepared+commands[-5:]


def support_audit(model,readback,support):
    """Recover support wrenches; a finite U3 band can transmit a clamp couple."""
    rows=[];nodes=model['nodes'];forces=readback['reaction_distribution']
    axes=support.get('lines_x_m',[.35,19.65])
    for ns,axis in zip(model['support_nodes'],axes):
        F=fsum(forces[str(n)][2] for n in ns)
        moment=fsum((nodes[str(n)][0]-axis)*forces[str(n)][2] for n in ns)
        low=min(nodes[str(n)][0] for n in ns);high=max(nodes[str(n)][0] for n in ns)
        rows.append(dict(axis_x_m=axis,nodes=len(ns),node_x_range_m=[low,high],vertical_reaction_N=F,
            equivalent_vertical_resultant_x_m=axis+moment/F,vertical_reaction_bending_couple_Nm=moment,
            zero_longitudinal_constraint_width=high-low<1e-8))
    return dict(rows=rows,rotation_free_line_definition_resolved=all(r['zero_longitudinal_constraint_width'] for r in rows),
        local_bearing_contact_and_stress_verified=False)


def analytical_reference(result,spec):
    """Same gravity/point load pose; gross Euler and declared shear correction."""
    s=result['section'];p=result['policy'];a,b=p['support']['bearing_lines_x_m'];EI=p['young_Pa']*s['I_y_m4']
    w=result['quantities']['accounted_superstructure_kg']*G/20;pts=[(q['x_m'],q['force_N']) for q in spec['live_pose']['points']]
    R1,R2,y,_=_response(pts,w,a,b,EI);U1,U2,_,_=_response([(10.,1.)],0.,a,b,1.)
    knots=sorted(set([0.,a,b,10.,20.]+[x for x,P in pts]));shear_work=0.
    # Real shear is linear between knots; virtual unit-load shear constant.
    for lo,hi in zip(knots,knots[1:]):
        x=(lo+hi)/2;V=(R1 if x>a else 0)+(R2 if x>b else 0)-w*x-fsum(P for xp,P in pts if xp<x)
        unit=(U1 if x>a else 0)+(U2 if x>b else 0)-(1 if x>10 else 0)
        shear_work+=V*unit*(hi-lo)
    Gmod=p['young_Pa']/(2*(1+p['poisson']));area=s['effective_web_shear_area_m2'];shear=-shear_work/((5/6)*Gmod*area)
    return dict(probe_xyz_m=[10.,0.,0.],bearing_axes_x_m=[a,b],gravity_N=w*20,live_N=fsum(P for x,P in pts),
        Euler_Bernoulli_displacement_m=y(10.),shear_correction_m=shear,declared_Timoshenko_displacement_m=y(10.)+shear,
        shear_coefficient_hypothesis=5/6,effective_web_shear_area_m2=area,
        scope='Same exact gross geometry and applied vertical loads. Lateral conductor torque exists in3D model; shear coefficient, local bearing/deck deformation and real contact remain unverified.')


def trial(spec,folder,*,size_m=.3):
    if size_m not in (.3,.25,.2):raise ValueError('Declared bounded mesh levels only')
    out=Path(folder).resolve();out.mkdir(parents=True,exist_ok=False);native.write(out/'input.json',spec)
    step=out/'input.step';shutil.copyfile(spec['cad_artifact']['step_path'],step)
    budget=spec['resource_request'];wall=budget['wall_s_each_process'];memory=budget['memory_mib_each_process']
    worker=out/'mesh-worker.py';worker.write_text(mesh_worker(spec))
    req=dict(step=str(step),volume=spec['nominal_quantity']['total_nominal_volume_m3'],size=size_m,output=str(out/'mesh-native/imported.json'),msh=str(out/'mesh-native/imported.msh'))
    if spec['support_hypothesis'].get('mode')=='rotation-free-line':
        req.update(bearing_lines_x_m=spec['support_hypothesis']['lines_x_m'],bearing_intervals_y_m=spec['support_hypothesis']['bearing_intervals_y_m'],bottom_z_m=spec['support_hypothesis']['bottom_z_m'])
    native.write(out/'mesh-request.json',req)
    # Resolve the environment directory, not its Python symlink. Invoking the
    # system interpreter directly loses the venv's gmsh package discovery.
    python=str((ROOT/'.venv').resolve()/'bin/python');execution=fem.bounded([python,str(worker),str(out/'mesh-request.json')],out/'mesh-native',read_roots=(out,Path(python).parent.parent),timeout_s=wall)
    result=dict(schema='osr-pilot-civil-native-trial/1',input_id=spec['input_id'],candidate_id=spec['candidate_id'],system_candidate_id=spec['system_candidate_id'],size_m=size_m,mesh_execution=execution,**FLAGS)
    if execution['state']!='executed':
        result['failure_reason']='Exact STEP mesh failed; retained without substituted mesh';native.write(out/'result.json',seal(result));return result
    try:
        model=load_model(spec,json.loads((out/'mesh-native/imported.json').read_bytes()))
        if len(model['elements'])>budget['max_cells']:raise ValueError('Cell budget exceeded')
        model.update(input_id=spec['input_id'],component_geometry_id=spec['component_geometry_id'],candidate_id=spec['candidate_id']);model['mesh_id']=identity(model);native.write(out/'mesh.json',model)
        result.update(cells=len(model['elements']),nodes=len(model['nodes']),mesh_id=model['mesh_id'])
        deck=out/'import.inp';deck.write_text(fem.deck(spec,model).split('*BOUNDARY')[0])
        cmds=commands(spec,model,deck)
        calls=[('batch',dict(commands=cmds[i:i+4000])) for i in range(0,len(cmds),4000)]
        ex,replies=native.mcp('fieldcraft',calls,out/'fieldcraft',timeout_s=wall,memory_mb=memory,read_root=out)
        result['fieldcraft_execution']=ex
        if ex['execution']=='executed':
            try:
                rows=[]
                for r in replies:
                    if r.get('id',0)>1:rows.extend(batch_results(native.payload(r)))
                result['fieldcraft']=fem.parse_field(rows,model)
            except (ValueError,KeyError,IndexError) as e:result['fieldcraft_failure']=str(e)
        inp=out/'viaduct.inp';inp.write_text(fem.deck(spec,model))
        argv=['/usr/bin/python3','-c',"import os,shutil;shutil.copyfile("+repr(str(inp))+",'viaduct.inp');os.execv('/usr/bin/ccx',['ccx','viaduct'])"]
        ex=fem.bounded(argv,out/'calculix',read_roots=(out,),timeout_s=wall);result['calculix_execution']=ex
        if ex['state']=='executed':
            try:
                result['calculix']=fem.parse_ccx((out/'calculix/viaduct.dat').read_text(),model)
                result['support_audit']=support_audit(model,result['calculix'],spec['support_hypothesis'])
            except (ValueError,OSError,KeyError) as e:result['calculix_failure']=str(e)
        if all(k in result for k in ('fieldcraft','calculix')):
            a=result['fieldcraft']['displacement_m'][2];b=result['calculix']['displacement_m'][2]
            result.update(cross_solver_relative_difference=abs(a-b)/abs(b),cross_solver_screen_passed=abs(a-b)/abs(b)<=.02)
    except (ValueError,KeyError,OSError) as e:result['failure_reason']=str(e)
    native.write(out/'result.json',seal(result));return result
