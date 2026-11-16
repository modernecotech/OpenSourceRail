"""Candidate-bound single-solid STEP -> Gmsh MED -> Code_Aster component analysis.

Only an explicitly supplied material, end-face constraint and traction are used.
This is a bounded numerical component pathway, never physical qualification.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

from . import code_aster_control as box
from . import freecad_reference
from engineering.performance import disk_reservation, check_disk_reservation

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
GIB=1024**3
SOURCE_FILES=('code_aster_candidate.py','code_aster_candidate_mesh.py',
              'code_aster_control.py','code_aster_box.export','freecad_reference.py')


def _identity(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
                                     allow_nan=False).encode()).hexdigest()


def _finite(value,*,positive=False):
    if type(value) not in (int,float) or not math.isfinite(value) or (positive and value<=0):
        raise ValueError('Finite '+('positive ' if positive else '')+'numerical input required')
    return float(value)


def _vector(value,*,positive=False):
    if not isinstance(value,(list,tuple)) or len(value)!=3:
        raise ValueError('Three finite vector components required')
    return [_finite(x,positive=positive) for x in value]


def validate_definition(value):
    if not isinstance(value,dict) or set(value)!={'candidate_id','component_geometry_id','geometry',
            'material','boundary','mesh_size_m'}:
        raise ValueError('Explicit candidate, geometry, material and boundary contract required')
    for key in ('candidate_id','component_geometry_id'):
        entry=value[key]
        if not isinstance(entry,str) or len(entry)!=64 or any(c not in '0123456789abcdef' for c in entry):
            raise ValueError('64-digit candidate and geometry identity required')
    geometry=value['geometry']
    if not isinstance(geometry,dict) or set(geometry)!={'product_name','volume_m3','bounds_m'}:
        raise ValueError('Declared exact STEP solid geometry required')
    name=geometry['product_name']
    if not isinstance(name,str) or not name or len(name)>128 or any(ord(c)<32 for c in name):
        raise ValueError('Printable STEP product name required')
    bounds=geometry['bounds_m']
    if not isinstance(bounds,dict) or set(bounds)!={'min','max'}:
        raise ValueError('Explicit STEP bounds required')
    low=_vector(bounds['min']);high=_vector(bounds['max'])
    if any(a>=b for a,b in zip(low,high)):
        raise ValueError('Positive candidate bounding dimensions required')
    _finite(geometry['volume_m3'],positive=True)
    if geometry['volume_m3']>math.prod(b-a for a,b in zip(low,high))*(1+1e-8):
        raise ValueError('Solid volume exceeds declared envelope')
    material=value['material']
    if not isinstance(material,dict) or set(material)!={'E_Pa','nu','density_kg_m3'}:
        raise ValueError('Explicit isotropic material hypothesis required')
    _finite(material['E_Pa'],positive=True)
    _finite(material['density_kg_m3'],positive=True)
    nu=_finite(material['nu'])
    if not -1<nu<.5:raise ValueError('Stable isotropic Poisson ratio required')
    boundary=value['boundary']
    if not isinstance(boundary,dict) or set(boundary)!={'load_axis','fixed_side','loaded_side','force_N'}:
        raise ValueError('Explicit end-face constraint and force required')
    if (boundary['load_axis'] not in ('x','y','z') or type(boundary['fixed_side']) is not int
            or type(boundary['loaded_side']) is not int or boundary['fixed_side'] not in (0,1)
            or boundary['loaded_side']!=1-boundary['fixed_side']):
        raise ValueError('Opposite end faces on one declared axis required')
    force=_vector(boundary['force_N'])
    if math.sqrt(sum(x*x for x in force))<=0:raise ValueError('Nonzero applied force required')
    mesh=_finite(value['mesh_size_m'],positive=True)
    if not .01<=mesh<=1.:raise ValueError('Mesh size outside bounded component domain')
    return value


def validate_refusal(path,step,candidate_id,geometry_id):
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('Ordinary FieldCraft refusal receipt required')
    value=json.loads(path.read_text())
    if (value.get('candidate_id')!=candidate_id or value.get('component_geometry_id')!=geometry_id
            or value.get('source_step_sha256')!=box.digest(step) or value.get('source_format')!='STEP'
            or value.get('handoff_status')!='held' or value.get('step_extension_dispatch')!='rejected'
            or value.get('direct_geometry_open')!='rejected' or value.get('physical_accepted') is not False
            or not value.get('fieldcraft_binary_sha256')):
        raise ValueError('FieldCraft refusal differs from exact candidate and STEP')
    return value


def render_comm(request,mesh):
    material=request['material'];force=request['force_N'];area=mesh['face_groups']['LOADED']['area_m2']
    if area<=0:raise ValueError('Positive loaded face area required')
    traction=[v/area for v in force]
    lines=["DEBUT()", "mesh = LIRE_MAILLAGE(FORMAT='MED', UNITE=20)",
      "mesh = DEFI_GROUP(reuse=mesh, MAILLAGE=mesh, CREA_GROUP_NO=(",
      "    _F(NOM='FIXED_NODES', GROUP_MA='FIXED'),",
      "    _F(NOM='LOADED_NODES', GROUP_MA='LOADED')))" ,
      "model = AFFE_MODELE(MAILLAGE=mesh, AFFE=_F(TOUT='OUI', PHENOMENE='MECANIQUE', MODELISATION='3D'))",
      f"material = DEFI_MATERIAU(ELAS=_F(E={material['E_Pa']!r}, NU={material['nu']!r}, RHO={material['density_kg_m3']!r}))",
      "field = AFFE_MATERIAU(MAILLAGE=mesh, AFFE=_F(TOUT='OUI', MATER=material))",
      "bc = AFFE_CHAR_MECA(MODELE=model, DDL_IMPO=_F(GROUP_NO='FIXED_NODES', DX=0.0, DY=0.0, DZ=0.0))",
      f"load = AFFE_CHAR_MECA(MODELE=model, FORCE_FACE=_F(GROUP_MA='LOADED', FX={traction[0]!r}, FY={traction[1]!r}, FZ={traction[2]!r}))",
      "result = MECA_STATIQUE(MODELE=model, CHAM_MATER=field, EXCIT=(_F(CHARGE=bc), _F(CHARGE=load)))",
      "result = CALC_CHAMP(reuse=result, RESULTAT=result, FORCE=('REAC_NODA',), ENERGIE=('ENEL_ELEM',))",
      "reactions = POST_RELEVE_T(ACTION=_F(INTITULE='FIXED_REACTION', OPERATION='EXTRACTION', RESULTAT=result, NOM_CHAM='REAC_NODA', GROUP_NO='FIXED_NODES', RESULTANTE=('DX','DY','DZ')))"]
    for component in ('DX','DY','DZ'):
        lines.append(f"tip_{component} = POST_RELEVE_T(ACTION=_F(INTITULE='LOADED_{component}', OPERATION='MOYENNE_ARITH', RESULTAT=result, NOM_CHAM='DEPL', NOM_CMP='{component}', GROUP_NO='LOADED_NODES'))")
    lines += ["energy = POST_ELEM(RESULTAT=result, CHAM_MATER=field, ENER_ELAS=_F(TOUT='OUI'))",
      "import json", "with open('/work/aster-observables.json', 'w') as stream:",
      "    json.dump({'reactions':[dict(row) for row in reactions.EXTR_TABLE()],",
      "               'tip':{component:[dict(row) for row in table.EXTR_TABLE()] for component, table in",
      "                      [('DX',tip_DX),('DY',tip_DY),('DZ',tip_DZ)]},",
      "               'energy':[dict(row) for row in energy.EXTR_TABLE()]},stream,default=float)",
      "IMPR_RESU(FORMAT='MED', UNITE=80, RESU=_F(RESULTAT=result, NOM_CHAM=('DEPL','REAC_NODA')))","FIN()"]
    return '\n'.join(lines)+'\n'


def check_observables(observables,force):
    def one(rows,name):
        if not isinstance(rows,list) or len(rows)!=1 or not isinstance(rows[0],dict):
            raise ValueError('Exactly one native '+name+' row required')
        return rows[0]
    reaction_row=one(observables.get('reactions'),'reaction')
    energy_row=one(observables.get('energy'),'energy')
    if energy_row.get('ENTITE')!='TOUT':raise ValueError('Whole-solid elastic energy required')
    reaction=[];displacement=[]
    for component in ('DX','DY','DZ'):
        tip=one(observables.get('tip',{}).get(component),'loaded displacement '+component)
        if tip.get('CMP')!=component:raise ValueError('Native displacement component differs')
        reaction.append(_finite(reaction_row.get(component)))
        displacement.append(_finite(tip.get('MOYENNE')))
    energy=_finite(energy_row.get('TOTALE'))
    force=_vector(force)
    norm=math.sqrt(sum(v*v for v in force))
    work=sum(a*b for a,b in zip(force,displacement))
    force_residual=math.sqrt(sum((a+b)**2 for a,b in zip(force,reaction)))/norm
    work_residual=abs(energy-.5*work)/max(abs(.5*work),1e-30)
    passed=energy>0 and work>0 and force_residual<=1e-5 and work_residual<=.02
    return dict(reaction_N=reaction,loaded_face_mean_displacement_m=displacement,
        elastic_energy_J=energy,external_work_J=work,force_relative_residual=force_residual,
        energy_work_relative_residual=work_residual,numerical_screen_passed=passed,
        tolerances=dict(force_relative=1e-5,energy_work_relative=.02))


def _geometry_check(reference,request):
    bodies=reference.get('bodies',[])
    one=bodies[0] if len(bodies)==1 else None
    expected=request['geometry']
    return bool(reference.get('execution')=='completed' and
        reference.get('source_step_sha256')==request['step_sha256'] and
        one is not None and one['valid'] and one['closed'] and one['solid_count']==1 and
        abs(one['volume_m3']-expected['volume_m3'])<=max(1e-8,expected['volume_m3']*1e-5) and
        all(abs(a-b)<=2e-6 for a,b in zip(one['bbox_m']['min']+one['bbox_m']['max'],
            expected['bounds_m']['min']+expected['bounds_m']['max'])))


def _run(step,output,definition,refusal_path,*,image,python,lease):
    request=dict(schema='osr-code-aster-candidate-request/1',**definition,
        step_sha256=box.digest(step),fieldcraft_rejection_sha256=box.digest(refusal_path),
        fieldcraft_binary_sha256=json.loads(refusal_path.read_text())['fieldcraft_binary_sha256'],
        source_sha256={str(HERE/name):box.digest(HERE/name) for name in SOURCE_FILES},
        requested_image=image,requested_image_identity=box._image_identity(image),
        units='m-kg-s-N-Pa',memory_bytes=2*GIB,timeout_s=180,
        native_memory_enforcement='2 GiB POSIX per-process virtual-address limit; aggregate Docker cgroup unavailable',
        physical_accepted=False,engineering_component_analysis_complete=False)
    request['evaluation_id']=_identity(request)
    output.mkdir(parents=True,mode=0o700)
    shutil.copyfile(step,output/'assembly.step')
    shutil.copyfile(refusal_path,output/'fieldcraft-rejection.json')
    (output/'request.json').write_text(json.dumps(request,sort_keys=True,indent=2)+'\n')
    mesh=box._call([str(Path(python).absolute()),str(HERE/'code_aster_candidate_mesh.py'),
        '--request',str(output/'request.json'),'--output',str(output)],output/'gmsh.log',timeout=45,memory_bytes=2*GIB)
    result=dict(schema='osr-code-aster-candidate-result/1',request=request,mesh_execution=mesh,
        code_aster_execution=None,state='held',physical_accepted=False,
        engineering_component_analysis_complete=False)
    if mesh['state']!='completed':result['reason']='Exact candidate STEP mesh failed; see gmsh.log'
    else:
        measure=json.loads((output/'mesh-summary.json').read_text())
        result['mesh']=measure
        if measure['step_sha256']!=request['step_sha256']:
            result['reason']='Mesh source STEP hash differs'
        else:
            reference=freecad_reference.run(output/'assembly.step',output/'freecad-reference',
                timeout_s=45,memory_mb=2048)
            valid=_geometry_check(reference,request)
            result['independent_step_geometry_verified']=bool(valid)
            result['freecad_reference_sha256']=box.digest(output/'freecad-reference'/'result.json')
            if not valid:result['reason']='Independent FreeCAD candidate STEP geometry differs'
            else:
                (output/'candidate.comm').write_text(render_comm(request,measure))
                (output/'candidate.export').write_text((HERE/'code_aster_box.export').read_text()
                    .replace('box.','candidate.'))
                pin=request['requested_image_identity']
                result['native_evaluation_id']=_identity(dict(request_evaluation_id=request['evaluation_id'],
                    gmsh_python_sha256=measure['gmsh_python_sha256'],
                    gmsh_library_sha256=measure['gmsh_library_sha256'],
                    image_digest=None if pin is None else pin['digest']))
                if pin is None:result['reason']='Requested Code_Aster image unavailable; exact meshed candidate input retained'
                else:
                    result['image']=pin
                    name='osr-aster-'+request['step_sha256'][:12]
                    argv=['docker','run','--rm','--network','none','--pids-limit','128',
                        '--security-opt','no-new-privileges','--user','0:0','--name',name,
                        '--mount',f'type=bind,source={output},target=/work','--workdir','/work',
                        '--env','OMP_NUM_THREADS=1','--env','OPENBLAS_NUM_THREADS=1',
                        '--env','MKL_NUM_THREADS=1',pin['digest'],'/bin/bash','-c',
                        'source /opt/activate.sh && ulimit -v 2097152 && exec run_aster candidate.export']
                    execution=box._call(argv,output/'code-aster.log',timeout=180)
                    if execution['state']=='timeout':
                        subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=15,check=False)
                    result['code_aster_execution']=execution
                    if execution['state']=='completed' and (output/'aster-observables.json').is_file():
                        try:
                            result['numerical_checks']=check_observables(json.loads((output/'aster-observables.json').read_text()),request['force_N'])
                            result['state']='executed'
                        except (KeyError,ValueError,TypeError) as exc:
                            result['reason']='Native observables invalid: '+str(exc)
                    else:result['reason']='Code_Aster solve incomplete; see code-aster.log'
    check_disk_reservation(lease)
    result['artifact_sha256']={str(p.relative_to(output)):box.digest(p) for p in output.rglob('*')
        if p.is_file() and p!=output/'result.json'}
    (output/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result


def run_candidate(step,output,definition,*,fieldcraft_rejection,image,python=sys.executable):
    step=Path(step)
    if step.is_symlink() or step.suffix.lower() not in ('.step','.stp') or not step.is_file():
        raise ValueError('Ordinary exact STEP source required')
    step=step.resolve(strict=True)
    definition=validate_definition(definition)
    refusal_path=Path(fieldcraft_rejection)
    validate_refusal(refusal_path,step,definition['candidate_id'],definition['component_geometry_id'])
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh private output directory required')
    with disk_reservation(ROOT,output,'code-aster-candidate',2*GIB) as lease:
        return _run(step,output,dict(definition,load_axis=definition['boundary']['load_axis'],
            fixed_side=definition['boundary']['fixed_side'],loaded_side=definition['boundary']['loaded_side'],
            force_N=definition['boundary']['force_N']),refusal_path,image=image,python=python,lease=lease)


def verify_candidate(output):
    output=Path(output).resolve(strict=True)
    result=json.loads((output/'result.json').read_text())
    if result.get('schema')!='osr-code-aster-candidate-result/1' or result.get('physical_accepted') is not False:
        raise ValueError('Invalid candidate result disposition')
    files={str(p.relative_to(output)):p for p in output.rglob('*') if p.is_file() and p!=output/'result.json'}
    if set(files)!=set(result['artifact_sha256']):raise ValueError('Candidate artifact inventory differs')
    if any(path.is_symlink() or box.digest(path)!=result['artifact_sha256'][name] for name,path in files.items()):
        raise ValueError('Candidate artifact bytes differ')
    request=result['request']
    if request!=json.loads((output/'request.json').read_text()) or request['evaluation_id']!=_identity({k:v for k,v in request.items() if k!='evaluation_id'}):
        raise ValueError('Candidate request identity differs')
    definition={k:request[k] for k in ('candidate_id','component_geometry_id','geometry','material','boundary','mesh_size_m')}
    validate_definition(definition)
    if request['force_N']!=definition['boundary']['force_N'] or request['load_axis']!=definition['boundary']['load_axis']:
        raise ValueError('Candidate boundary projection differs')
    if box.digest(output/'assembly.step')!=request['step_sha256'] or box.digest(output/'fieldcraft-rejection.json')!=request['fieldcraft_rejection_sha256']:
        raise ValueError('Candidate STEP or FieldCraft refusal differs')
    validate_refusal(output/'fieldcraft-rejection.json',output/'assembly.step',request['candidate_id'],request['component_geometry_id'])
    for path,sha in request['source_sha256'].items():
        if box.digest(path)!=sha:raise ValueError('Candidate source implementation differs')
    if result.get('mesh') is not None:
        mesh=json.loads((output/'mesh-summary.json').read_text())
        if mesh!=result['mesh'] or mesh['step_sha256']!=request['step_sha256']:
            raise ValueError('Candidate mesh receipt differs')
        if box.digest(mesh['gmsh_python_path'])!=mesh['gmsh_python_sha256'] or box.digest(mesh['gmsh_library_path'])!=mesh['gmsh_library_sha256']:
            raise ValueError('Native Gmsh bytes differ')
        if box.digest(output/'freecad-reference'/'result.json')!=result['freecad_reference_sha256']:
            raise ValueError('Independent STEP geometry receipt differs')
        if _geometry_check(json.loads((output/'freecad-reference'/'result.json').read_text()),request)!=result['independent_step_geometry_verified']:
            raise ValueError('Independent STEP geometry verdict differs')
        if (output/'candidate.comm').exists() and (output/'candidate.comm').read_text()!=render_comm(request,mesh):
            raise ValueError('Code_Aster input deck differs')
        if (output/'candidate.export').exists() and (output/'candidate.export').read_text()!=(HERE/'code_aster_box.export').read_text().replace('box.','candidate.'):
            raise ValueError('Code_Aster export deck differs')
        pin=request['requested_image_identity']
        native_id=_identity(dict(request_evaluation_id=request['evaluation_id'],
            gmsh_python_sha256=mesh['gmsh_python_sha256'],gmsh_library_sha256=mesh['gmsh_library_sha256'],
            image_digest=None if pin is None else pin['digest']))
        if result.get('native_evaluation_id')!=native_id:raise ValueError('Candidate native evaluation identity differs')
    if result['state']=='executed':
        if result['code_aster_execution']['state']!='completed' or not result['independent_step_geometry_verified']:
            raise ValueError('Candidate native admission differs')
        if check_observables(json.loads((output/'aster-observables.json').read_text()),request['force_N'])!=result['numerical_checks']:
            raise ValueError('Candidate numerical checks differ')
    elif result['state']!='held':raise ValueError('Unknown candidate handoff state')
    return dict(state=result['state'],artifact_count=len(files),
        numerical_screen_passed=result.get('numerical_checks',{}).get('numerical_screen_passed'),
        physical_accepted=False)
