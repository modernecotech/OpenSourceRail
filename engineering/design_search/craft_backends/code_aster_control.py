"""Explicit SolidCraft STEP -> Gmsh MED -> Code_Aster one-box control.

This diagnostic cannot admit an engineering component or physical design. The
selected candidate needs its own source-matched load, mesh and material packet.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
GIB = 1024**3


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def _call(argv,log,*,timeout,memory_bytes=None):
    def limits():
        if memory_bytes is not None:
            resource.setrlimit(resource.RLIMIT_AS,(memory_bytes,memory_bytes))
    with Path(log).open('wb') as out:
        started=time.monotonic()
        try:
            completed=subprocess.run(argv,stdout=out,stderr=subprocess.STDOUT,
                                     timeout=timeout,check=False,preexec_fn=limits,
                                     env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
            return dict(argv=list(map(str,argv)),returncode=completed.returncode,
                        state='completed' if completed.returncode==0 else 'failed',
                        wall_s=time.monotonic()-started)
        except subprocess.TimeoutExpired:
            return dict(argv=list(map(str,argv)),returncode=None,state='timeout',
                        wall_s=time.monotonic()-started)


def _image_identity(image):
    try:
        result=subprocess.run(['docker','image','inspect',image,'--format',
                               '{{json .RepoDigests}} {{.Size}}'],capture_output=True,text=True,
                              timeout=10,check=False)
    except (OSError,subprocess.TimeoutExpired):return None
    if result.returncode:return None
    data,size=result.stdout.strip().rsplit(' ',1)
    digests=json.loads(data)
    repository=image.rsplit(':',1)[0].split('@',1)[0]
    pinned=next((d for d in digests if d.startswith(repository+'@sha256:')),None)
    if pinned is None:raise ValueError('Container lacks immutable repository digest')
    return dict(tag=image,digest=pinned,uncompressed_bytes=int(size))


def check_observables(observables, *, force_N=1000., E_Pa=70e9):
    """Recompute the axial control's force and work balance from native tables."""
    def one(table):
        rows=observables.get(table)
        if not isinstance(rows,list) or len(rows)!=1 or not isinstance(rows[0],dict):
            raise ValueError('Exactly one native '+table+' table row required')
        return rows[0]
    def number(row,key):
        value=row.get(key)
        if not isinstance(value,(int,float)) or not math.isfinite(value):
            raise ValueError('Finite native '+key+' required')
        return float(value)
    reactions=one('reactions');tip=one('tip');energy_row=one('energy')
    if tip.get('CMP')!='DX' or energy_row.get('ENTITE')!='TOUT':
        raise ValueError('Expected native DX/whole-solid table selection differs')
    reaction=number(reactions,'DX')
    transverse=(number(reactions,'DY'),number(reactions,'DZ'))
    displacement=number(tip,'MOYENNE')
    energy=number(energy_row,'TOTALE')
    theory=force_N/(E_Pa*.06)
    force_relative=abs(force_N+reaction)/force_N
    transverse_relative=math.hypot(*transverse)/force_N
    energy_relative=abs(energy-.5*force_N*displacement)/max(abs(.5*force_N*displacement),1e-30)
    theory_relative=abs(displacement-theory)/theory
    passed=(displacement>0 and energy>0 and force_relative<=1e-5 and
            transverse_relative<=1e-5 and
            energy_relative<=.02 and theory_relative<=.05)
    return dict(reaction_N=reaction,mean_loaded_face_displacement_m=displacement,
                elastic_energy_J=energy,analytical_axial_displacement_m=theory,
                force_relative_residual=force_relative,energy_relative_residual=energy_relative,
                transverse_force_relative_residual=transverse_relative,
                analytical_displacement_relative_difference=theory_relative,
                numerical_screen_passed=passed,
                tolerances=dict(force_relative=1e-5,energy_relative=.02,
                                analytical_displacement_relative=.05))


def run_box(step,output,*,candidate_id,image,fieldcraft_rejection=None,python=sys.executable):
    """Run one named-face axial control using a fresh private directory.

    The caller must supply an explicit physical candidate ID. The module has no
    automatic FieldCraft or CalculiX fallback and never mutates selected packets.
    """
    step=Path(step)
    if step.is_symlink() or step.suffix.lower() not in ('.step','.stp'):
        raise ValueError('Regular exact STEP source required')
    step=step.resolve(strict=True)
    if not candidate_id or '/' in candidate_id:raise ValueError('Explicit candidate ID required')
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh private output directory required')
    if fieldcraft_rejection is None:raise ValueError('Exact FieldCraft STEP refusal receipt required')
    rejection_path=Path(fieldcraft_rejection)
    if rejection_path.is_symlink():raise ValueError('Regular FieldCraft refusal receipt required')
    rejection=json.loads(rejection_path.read_text())
    if (rejection.get('candidate_id')!=candidate_id or
        rejection.get('source_step_sha256')!=digest(step) or
        rejection.get('source_format')!='STEP' or
        rejection.get('handoff_status')!='held' or
        rejection.get('step_extension_dispatch')!='rejected' or
        rejection.get('direct_geometry_open')!='rejected' or
        rejection.get('physical_accepted') is not False or
        not rejection.get('component_geometry_id') or
        not rejection.get('fieldcraft_binary_sha256')):
        raise ValueError('FieldCraft refusal is not bound to this candidate and STEP')
    if shutil.disk_usage(output.parent).free<20*GIB+2*GIB:
        raise ValueError('20 GiB free-space floor plus 2 GiB run projection required')
    output.mkdir(parents=True,mode=0o700)
    image_pin=_image_identity(image)
    shutil.copyfile(step,output/'assembly.step')
    shutil.copyfile(rejection_path,output/'fieldcraft-rejection.json')
    for name in ('code_aster_box.comm','code_aster_box.export'):
        shutil.copyfile(HERE/name,output/name.removeprefix('code_aster_'))
    source={str(HERE/name):digest(HERE/name) for name in
            ('code_aster_control.py','code_aster_mesh.py','code_aster_box.comm',
             'code_aster_box.export','freecad_reference.py')}
    geometry=dict(part_name='assembly',shape='box',length_m=1.,width_m=.3,
                  height_m=.2,origin_m=[0.,0.,0.],units='m')
    geometry_id=hashlib.sha256(json.dumps(geometry,sort_keys=True,
                                         separators=(',',':')).encode()).hexdigest()
    request=dict(schema='osr-code-aster-box-request/1',candidate_id=candidate_id,
                 scope='Synthetic axial one-box numerical control only',
                 step_sha256=digest(output/'assembly.step'),source_sha256=source,
                 component_geometry_id=rejection['component_geometry_id'],
                 checked_geometry_definition=geometry,checked_geometry_sha256=geometry_id,
                 fieldcraft_binary_sha256=rejection['fieldcraft_binary_sha256'],
                 fieldcraft_rejection_sha256=digest(output/'fieldcraft-rejection.json'),
                 selection_id=None,
                 units='m-kg-s-N-Pa',material=dict(E_Pa=70e9,nu=.33,density_kg_m3=2700.),
                 requested_image=image,requested_image_identity=image_pin,
                 force_N=1000.,fixed_face='x=0',loaded_face='x=1',
                 timeout_s=180,memory_bytes=2*GIB,
                 native_memory_enforcement='2 GiB POSIX per-process virtual-address limit; rootless Docker aggregate cgroup memory and CPU quota unavailable',
                 native_cpu_request='Code_Aster one MPI worker and one thread via export and environment; no OS CPU quota',
                 physical_accepted=False,
                 engineering_component_analysis_complete=False)
    request['evaluation_id']=hashlib.sha256(json.dumps(request,sort_keys=True,
                                                      separators=(',',':')).encode()).hexdigest()
    (output/'request.json').write_text(json.dumps(request,sort_keys=True,indent=2)+'\n')
    mesh=_call([str(Path(python).absolute()),str(HERE/'code_aster_mesh.py'),
                '--step',str(output/'assembly.step'),'--output',str(output)],
               output/'gmsh.log',timeout=30,memory_bytes=2*GIB)
    result=dict(schema='osr-code-aster-box-result/1',request=request,
                mesh_execution=mesh,code_aster_execution=None,
                state='held',physical_accepted=False,
                engineering_component_analysis_complete=False)
    if mesh['state']!='completed':
        result['reason']='Exact STEP meshing failed; see gmsh.log'
    else:
        measure=json.loads((output/'mesh-summary.json').read_text())
        if measure['step_sha256']!=request['step_sha256'] or abs(measure['step_volume_m3']-.06)>1e-9 or abs(measure['mesh_corner_tet_volume_m3']-.06)>1e-8 or measure['min_scaled_jacobian']<=0:
            result['reason']='Mesh geometry or Jacobian check failed'
        else:
            result['mesh']=measure
            result['native_evaluation_id']=hashlib.sha256(json.dumps(dict(
                request_evaluation_id=request['evaluation_id'],
                gmsh_python_sha256=measure['gmsh_python_sha256'],
                gmsh_library_sha256=measure['gmsh_library_sha256'],
                image_digest=None if image_pin is None else image_pin['digest']),
                sort_keys=True,separators=(',',':')).encode()).hexdigest()
            from . import freecad_reference
            reference=freecad_reference.run(output/'assembly.step',output/'freecad-reference',
                                            timeout_s=30,memory_mb=2048,
                                            expected_body_ids=['assembly'])
            body=reference['bodies'][0] if len(reference.get('bodies',[]))==1 else None
            valid=(reference['execution']=='completed' and
                   reference['source_step_sha256']==request['step_sha256'] and body and
                   body['closed'] and body['valid'] and body['solid_count']==1 and
                   abs(body['volume_m3']-.06)<1e-9 and
                   all(abs(a-b)<1e-8 for a,b in zip(body['center_of_mass_m'],(.5,.15,.1))) and
                   all(abs(a-b)<1e-8 for a,b in zip(body['bbox_m']['min'],(0.,0.,0.))) and
                   all(abs(a-b)<1e-8 for a,b in zip(body['bbox_m']['max'],(1.,.3,.2))))
            result['independent_step_geometry_verified']=bool(valid)
            result['freecad_reference_sha256']=digest(output/'freecad-reference'/'result.json')
            if not valid:result['reason']='Independent FreeCAD STEP geometry check failed'
            elif image_pin is None:result['reason']='Requested Code_Aster image is unavailable'
            else:
                result['image']=image_pin
                container_name='osr-aster-'+request['step_sha256'][:12]
                argv=['docker','run','--rm','--network','none','--pids-limit','128',
                      '--security-opt','no-new-privileges',
                      '--user','0:0',
                      '--name',container_name,
                      '--mount',f'type=bind,source={output},target=/work',
                      '--workdir','/work','--env','OMP_NUM_THREADS=1',
                      '--env','OPENBLAS_NUM_THREADS=1','--env','MKL_NUM_THREADS=1',
                      image_pin['digest'],'/bin/bash','-c',
                      'source /opt/activate.sh && ulimit -v 2097152 && exec run_aster box.export']
                execution=_call(argv,output/'code-aster.log',timeout=180)
                if execution['state']=='timeout':
                    subprocess.run(['docker','rm','-f',container_name],
                                   capture_output=True,timeout=15,check=False)
                result['code_aster_execution']=execution
                if execution['state']=='completed' and (output/'aster-observables.json').is_file():
                    try:
                        observables=json.loads((output/'aster-observables.json').read_text())
                        result['numerical_checks']=check_observables(observables)
                        result['state']='executed'
                    except (ValueError,KeyError,TypeError,ZeroDivisionError) as exc:
                        result['reason']='Native observables could not be independently checked: '+str(exc)
                else:result['reason']='Code_Aster solve or native observables did not complete; see code-aster.log'
    files={str(p.relative_to(output)):digest(p) for p in output.rglob('*')
           if p.is_file() and p!=output/'result.json'}
    result['artifact_sha256']=files
    (output/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result


def verify_box(output):
    """Verify one preserved run without running a new native process."""
    output=Path(output).resolve(strict=True)
    result=json.loads((output/'result.json').read_text())
    if result.get('schema')!='osr-code-aster-box-result/1' or result.get('physical_accepted') is not False:
        raise ValueError('Invalid non-acceptance result receipt')
    files={str(p.relative_to(output)):p for p in output.rglob('*')
           if p.is_file() and p!=output/'result.json'}
    if set(files)!=set(result['artifact_sha256']):
        raise ValueError('Preserved artifact inventory differs')
    for name,path in files.items():
        if path.is_symlink() or digest(path)!=result['artifact_sha256'][name]:
            raise ValueError('Preserved artifact differs: '+name)
    request=result['request']
    if request!=json.loads((output/'request.json').read_text()):
        raise ValueError('Run request receipt differs')
    request_body={k:v for k,v in request.items() if k!='evaluation_id'}
    request_id=hashlib.sha256(json.dumps(request_body,sort_keys=True,
                                         separators=(',',':')).encode()).hexdigest()
    if request['evaluation_id']!=request_id:
        raise ValueError('Run evaluation identity differs')
    if hashlib.sha256(json.dumps(request['checked_geometry_definition'],sort_keys=True,
                                 separators=(',',':')).encode()).hexdigest()!=request['checked_geometry_sha256']:
        raise ValueError('Physical geometry fingerprint differs')
    if digest(output/'assembly.step')!=request['step_sha256']:
        raise ValueError('Source STEP bytes differ')
    refusal=json.loads((output/'fieldcraft-rejection.json').read_text())
    if (digest(output/'fieldcraft-rejection.json')!=request['fieldcraft_rejection_sha256'] or
        refusal['source_step_sha256']!=request['step_sha256'] or
        refusal['candidate_id']!=request['candidate_id'] or
        refusal['component_geometry_id']!=request['component_geometry_id'] or
        refusal['fieldcraft_binary_sha256']!=request['fieldcraft_binary_sha256'] or
        refusal['handoff_status']!='held'):
        raise ValueError('FieldCraft refusal source identity differs')
    for name,sha in request['source_sha256'].items():
        if digest(name)!=sha:raise ValueError('Source implementation differs: '+name)
    if result.get('mesh') is not None:
        if json.loads((output/'mesh-summary.json').read_text())!=result['mesh']:
            raise ValueError('Mesh receipt differs')
        if digest(output/'freecad-reference'/'result.json')!=result['freecad_reference_sha256']:
            raise ValueError('Independent STEP receipt differs')
        mesh=result['mesh'];pin=request['requested_image_identity']
        if digest(mesh['gmsh_python_path'])!=mesh['gmsh_python_sha256'] or digest(mesh['gmsh_library_path'])!=mesh['gmsh_library_sha256']:
            raise ValueError('Gmsh tool bytes differ')
        expected_id=hashlib.sha256(json.dumps(dict(
            request_evaluation_id=request['evaluation_id'],
            gmsh_python_sha256=mesh['gmsh_python_sha256'],
            gmsh_library_sha256=mesh['gmsh_library_sha256'],
            image_digest=None if pin is None else pin['digest']),
            sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if result['native_evaluation_id']!=expected_id:
            raise ValueError('Native evaluation identity differs')
    if result['state']=='executed':
        if result['code_aster_execution']['state']!='completed' or not result['independent_step_geometry_verified']:
            raise ValueError('Native solve admission differs')
        checked=check_observables(json.loads((output/'aster-observables.json').read_text()))
        if checked!=result['numerical_checks']:
            raise ValueError('Recomputed numerical checks differ')
    elif result['state']!='held':raise ValueError('Unknown handoff state')
    return dict(state=result['state'],artifact_count=len(files),
                numerical_screen_passed=result.get('numerical_checks',{}).get('numerical_screen_passed'),
                physical_accepted=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--step',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--candidate-id',required=True)
    parser.add_argument('--image',required=True)
    parser.add_argument('--fieldcraft-rejection',required=True)
    parser.add_argument('--python',default=sys.executable)
    args=parser.parse_args()
    print(json.dumps(run_box(args.step,args.output,candidate_id=args.candidate_id,
                             image=args.image,fieldcraft_rejection=args.fieldcraft_rejection,
                             python=args.python),
                     sort_keys=True,indent=2))
