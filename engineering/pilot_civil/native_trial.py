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


def prepare(result,train,artifact,load_name):
    if result['evaluation_id']!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):raise ValueError('Civil evaluation seal changed')
    if train['evaluation_id']!=identity({k:v for k,v in train.items() if k!='evaluation_id'}):raise ValueError('Axle evaluation seal changed')
    if artifact['evaluation_id']!=identity({k:v for k,v in artifact.items() if k!='evaluation_id'}):raise ValueError('CAD artifact seal changed')
    if result['system_candidate_id']!=train['candidate_id'] or result['input_load_evaluation_id']!=train['evaluation_id']:raise ValueError('Mixed system or axle evaluation')
    if artifact['candidate_id']!=result['civil_candidate_id'] or not artifact.get('gross_beam_only'):raise ValueError('Exact same-civil gross CAD required')
    if artifact['component_geometry_id']!=scene(result,gross_beam_only=True)['component_geometry_id']:raise ValueError('Physical CAD projection changed')
    if native.digest(artifact['step_path'])!=artifact['step_sha256']:raise ValueError('Exact STEP bytes changed')
    load=next(l for l in train['load_cases'] if l['name']==load_name);d=next(d for d in result['load_demands'] if d['name']==load_name)
    shift=d['critical_train_translation_m']['deflection_m'];factor=result['policy']['dynamic_axle_factor']
    points=[dict(x_m=a['x_m']+shift,force_N=a['vertical_force_N']*factor) for a in load['axles'] if 0<=a['x_m']+shift<=20]
    if any(not .15<=a['x_m']<=19.85 for a in points):raise ValueError('Critical axle patch clips beam end; request different pose, not invented load')
    spec=dict(schema='osr-pilot-civil-fem/1',candidate_id=result['civil_candidate_id'],system_candidate_id=train['candidate_id'],input_load_evaluation_id=train['evaluation_id'],load_name=load_name,
        component_geometry_id=artifact['component_geometry_id'],cad_artifact=deepcopy(artifact),nominal_quantity=result['section']['quantities'],superimposed_mass_kg=result['quantities']['accounted_superstructure_kg']-result['quantities']['nominal_concrete_mass_kg'],
        live_pose=dict(points=points,translation_m=shift),support_hypothesis=dict(patches_x_m=[[.125,.575],[19.425,19.875]],patch_y_m=[-.25,.25],scope='Bottom horizontal finite patches centred on actual 0.35/19.65 m bearing lines. Two physical transverse bearings idealised as continuous bottom patch.'),
        material_hypothesis=dict(young_Pa=35e9,poisson=.2,density_kg_m3=2500.),
        evaluation_domain='Perfectly bonded gross continuum, no cracking/prestress/reinforcement/joint/soil stiffness credit. Vertical loads only; torsion/handling are separate analytical screens.',
        resource_request=dict(max_cells=20000,cpu_s_each_process=60,wall_s_each_process=58,memory_mib_each_process=2048),**FLAGS)
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
    add([0,20,-1,1],spec['superimposed_mass_kg']*G)
    for a in spec['live_pose']['points']:
        for y in (-.6,.6):add([a['x_m']-.15,a['x_m']+.15,y-.1,y+.1],a['force_N']/2)
    depth=min(v[2] for v in nodes.values());supports=[]
    for lo,hi in spec['support_hypothesis']['patches_x_m']:
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


def trial(spec,folder,*,size_m=.3):
    if size_m not in (.3,.25,.2):raise ValueError('Declared bounded mesh levels only')
    out=Path(folder).resolve();out.mkdir(parents=True,exist_ok=False);native.write(out/'input.json',spec)
    step=out/'input.step';shutil.copyfile(spec['cad_artifact']['step_path'],step)
    worker=out/'mesh-worker.py';worker.write_text(fem.GMSH_WORKER.replace("faces=[]","if len(elements)>20000:raise ValueError('Cell budget exceeded; execution retained')\nfaces=[]"))
    req=dict(step=str(step),volume=spec['nominal_quantity']['total_nominal_volume_m3'],size=size_m,output=str(out/'mesh-native/imported.json'),msh=str(out/'mesh-native/imported.msh'))
    native.write(out/'mesh-request.json',req)
    # Resolve the environment directory, not its Python symlink. Invoking the
    # system interpreter directly loses the venv's gmsh package discovery.
    python=str((ROOT/'.venv').resolve()/'bin/python');execution=fem.bounded([python,str(worker),str(out/'mesh-request.json')],out/'mesh-native',read_roots=(out,Path(python).parent.parent),timeout_s=58)
    result=dict(schema='osr-pilot-civil-native-trial/1',input_id=spec['input_id'],candidate_id=spec['candidate_id'],system_candidate_id=spec['system_candidate_id'],size_m=size_m,mesh_execution=execution,**FLAGS)
    if execution['state']!='executed':
        result['failure_reason']='Exact STEP mesh failed; retained without substituted mesh';native.write(out/'result.json',seal(result));return result
    try:
        model=load_model(spec,json.loads((out/'mesh-native/imported.json').read_bytes()))
        if len(model['elements'])>20000:raise ValueError('Cell budget exceeded')
        model.update(input_id=spec['input_id'],component_geometry_id=spec['component_geometry_id'],candidate_id=spec['candidate_id']);model['mesh_id']=identity(model);native.write(out/'mesh.json',model)
        result.update(cells=len(model['elements']),nodes=len(model['nodes']),mesh_id=model['mesh_id'])
        deck=out/'import.inp';deck.write_text(fem.deck(spec,model).split('*BOUNDARY')[0])
        cmds=fem.commands(spec,model,deck);ex,replies=native.mcp('fieldcraft',[('batch',dict(commands=cmds))],out/'fieldcraft',timeout_s=58,memory_mb=2048,read_root=out)
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
        ex=fem.bounded(argv,out/'calculix',read_roots=(out,),timeout_s=58);result['calculix_execution']=ex
        if ex['state']=='executed':
            try:result['calculix']=fem.parse_ccx((out/'calculix/viaduct.dat').read_text(),model)
            except (ValueError,OSError,KeyError) as e:result['calculix_failure']=str(e)
        if all(k in result for k in ('fieldcraft','calculix')):
            a=result['fieldcraft']['displacement_m'][2];b=result['calculix']['displacement_m'][2]
            result.update(cross_solver_relative_difference=abs(a-b)/abs(b),cross_solver_screen_passed=abs(a-b)/abs(b)<=.02)
    except (ValueError,KeyError,OSError) as e:result['failure_reason']=str(e)
    native.write(out/'result.json',seal(result));return result
