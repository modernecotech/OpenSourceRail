"""Strict old-evidence admission and fresh-mesh normal-load FEM request.

Old crowd solves never become normal-load evidence. An old replay discrepancy
refuses mesh reuse and proposes a separately identified fresh-mesh experiment.
"""
from pathlib import Path
from copy import deepcopy
import json,os,sys,platform,shutil,time
from . import native,identity,FLAGS
from . import viaduct_cases,viaduct_fem as fem,viaduct_admission,viaduct_cad
from .fieldcraft import batch_results

PRODUCER='engineering/design_search/craft_backends/linear_load_reuse.py'
MAX_BYTES=512*1024**2


def runtime():
    import numpy as np,gmsh
    import numpy.linalg._umath_linalg as linalg
    paths={'python':Path(sys.executable).resolve(),'numpy_linalg':Path(linalg.__file__),
           'gmsh_python':Path(gmsh.__file__),'gmsh_library':Path(gmsh.lib._name)}
    return dict(python_version=platform.python_version(),numpy_version=np.__version__,gmsh_version=gmsh.__version__,
        executable=str(Path(sys.executable).absolute()),component_sha256={k:native.digest(p) for k,p in paths.items()},
        thread_environment={k:os.environ.get(k) for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')})


def plan(original_fem,cad_root,*,root,producer_source=None):
    original_fem,cad_root,root=map(Path,(original_fem,cad_root,root))
    source=Path(producer_source) if producer_source is not None else root/PRODUCER
    if native.digest(source)!=native.digest(__file__):raise ValueError('Loaded new-load producer source required')
    old=json.loads((original_fem/'input.json').read_text())
    request=json.loads((original_fem/'request.json').read_text())
    if request['source_sha256']!=fem.sources(root):raise ValueError('Old FEM source epoch differs; no reuse admission')
    case=viaduct_cases.build('reference_box','reference',root=root)
    cad=viaduct_admission.verify(cad_root,case,root=root)
    if cad['verified'] is not True or cad['nominal_geometry_comparison_passed'] is not True:
        raise ValueError('Source-bound exact CAD admission required')
    if old['load_case']['name']!='crowd_control':raise ValueError('Expected original crowd control, not relabelled normal evidence')
    if any(old[k]!=case[k] for k in ('candidate_id','component_geometry_id')):raise ValueError('Old/CAD physical identities differ')
    # This is deliberately strict. A discrepancy is retained, never rounded away.
    old_replay=dict(state='verified',receipt=None)
    try:old_replay['receipt']=fem.verify(original_fem,old)
    except (ValueError,KeyError,OSError) as exc:old_replay=dict(state='held',reason=str(exc))
    generated=cad_root/case['case_id']/'generate'
    artifact=dict(candidate_id=case['candidate_id'],component_geometry_id=case['component_geometry_id'],
        sc_path=str((generated/'assembly.sc').resolve()),sc_sha256=native.digest(generated/'assembly.sc'),
        step_path=str((generated/'assembly.step').resolve()),step_sha256=native.digest(generated/'assembly.step'))
    if old['cad_artifact']!=artifact:raise ValueError('Old CAD pointer differs from independently authenticated canonical archive')
    spec=fem.prepare(case,artifact,'normal',root=root);fem.validate_input(spec,root=root)
    if spec['input_id']==old['input_id'] or spec['load_case']==old['load_case']:raise ValueError('New normal load requires its own evaluation input')
    # Parent approval selected the fresh-mesh alternative after failed replay.
    # Even if replay later succeeds this plan makes no old-load/solve reuse claim.
    result=dict(schema='osr-v07-normal-fem-plan/1',mode='fresh-mesh-normal-load',input=spec,
        original_input_id=old['input_id'],old_replay=old_replay,old_mesh_reused=False,old_solve_reused=False,
        cad_admission=cad,cad_root=str(cad_root.resolve()),original_fem=str(original_fem.resolve()),
        runtime=runtime(),source_sha256={**fem.sources(root),**viaduct_cad.sources(root),
            PRODUCER:native.digest(source),'engineering/design_search/craft_backends/viaduct_admission.py':native.digest(root/'engineering/design_search/craft_backends/viaduct_admission.py')},
        tools={name:native.pin(name) for name in ('solidcraft','fieldcraft')},
        fieldcraft_executable_sha256=native.digest(native.executable('fieldcraft')),
        calculix_executable_sha256=native.digest(shutil.which('ccx')),
        native_process_plan=[dict(operation='independent exact STEP check',memory_mib=2048,wall_seconds=120),
            dict(operation='fresh coarse Gmsh',memory_mib=2048,wall_seconds=120),
            dict(operation='coarse FieldCraft',memory_mib=2048,wall_seconds=120),
            dict(operation='coarse CalculiX',memory_mib=2048,wall_seconds=120),
            dict(operation='fresh fine Gmsh',memory_mib=2048,wall_seconds=120),
            dict(operation='fine FieldCraft',memory_mib=3072,wall_seconds=120),
            dict(operation='fine CalculiX',memory_mib=2048,wall_seconds=120)],
        maximum_native_processes=7,maximum_total_wall_seconds=900,maximum_output_bytes=MAX_BYTES,
        minimum_host_free_bytes=20*1024**3,physics_scope='Existing admitted uncracked isotropic reference-box normal-load control only',
        source_solver_functions_unchanged=True,execution='planned',**FLAGS)
    result['plan_id']=identity(result);return result


def _field(spec,model,folder,memory_mib):
    folder.mkdir(parents=True,exist_ok=False)
    meshdeck=folder/'import-mesh.inp';meshdeck.write_text(fem.deck(spec,model).split('*BOUNDARY')[0])
    commands=fem.commands(spec,model,meshdeck)
    calls=[('batch',dict(commands=commands[i:i+4000])) for i in range(0,len(commands),4000)]
    execution,replies=native.mcp('fieldcraft',calls,folder/'fieldcraft',read_root=folder,
                                 memory_mb=memory_mib,timeout_s=120)
    if execution['execution']!='executed':raise ValueError('Fresh FieldCraft execution did not complete')
    rows=[]
    for reply in replies:
        if reply.get('id',0)>1:rows.extend(batch_results(native.payload(reply)))
    return dict(execution=execution,numerical=fem.parse_field(rows,model))


def _ccx(spec,model,folder):
    folder.mkdir(parents=True,exist_ok=False)
    inp=folder/'viaduct.inp';inp.write_text(fem.deck(spec,model))
    argv=['/usr/bin/python3','-c',"import os,shutil;shutil.copyfile("+repr(str(inp))+",'viaduct.inp');os.execv('/usr/bin/ccx',['ccx','viaduct'])"]
    execution=fem.bounded(argv,folder/'calculix',read_roots=(folder,),timeout_s=120)
    if execution['state']!='executed':raise ValueError('Fresh independent CalculiX execution did not complete')
    return dict(execution=execution,numerical=fem.parse_ccx((folder/'calculix/viaduct.dat').read_text(),model))


def run(request,output,*,root,coordinator_admitted=False):
    """Explicit seven-process experiment; call only after coordinator admission."""
    if coordinator_admitted is not True:raise ValueError('Explicit coordinator execution request required')
    if request.get('plan_id')!=identity({k:v for k,v in request.items() if k!='plan_id'}):raise ValueError('Sealed normal-load plan required')
    root=Path(root);output=Path(output).absolute()
    if output.exists() or output.resolve().is_relative_to(root.resolve()):raise ValueError('Fresh external experiment directory required')
    if request['runtime']!=runtime():raise ValueError('Runtime changed after preflight')
    for name,sha in request['source_sha256'].items():
        source=Path(__file__) if name==PRODUCER else root/name
        if native.digest(source)!=sha:raise ValueError('Source changed after preflight')
    output.parent.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(output.parent).free<request['minimum_host_free_bytes']+MAX_BYTES:raise ValueError('Host reserve plus run reservation unavailable')
    output.mkdir();native.write(output/'plan.json',request);started=time.monotonic();calls=[];levels={}
    def budget(operation):
        if time.monotonic()-started+120>request['maximum_total_wall_seconds']:raise ValueError('Remaining run wall budget cannot admit next process')
        if len(calls)>=request['maximum_native_processes']:raise ValueError('Native process budget exhausted')
        if shutil.disk_usage(output).free<request['minimum_host_free_bytes']:raise ValueError('Host reserve exhausted')
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>MAX_BYTES:raise ValueError('Observed aggregate output exceeds budget')
        calls.append(operation)
    try:
        spec=request['input'];case=viaduct_cases.build('reference_box','reference',root=root)
        if request.get('schema')!='osr-v07-normal-fem-plan/1' or request.get('mode')!='fresh-mesh-normal-load':raise ValueError('Known new-load experiment required')
        if request.get('maximum_native_processes')!=7 or request.get('maximum_total_wall_seconds')!=900 or request.get('maximum_output_bytes')!=MAX_BYTES or request.get('minimum_host_free_bytes')!=20*1024**3:raise ValueError('Declared new-load resource contract differs')
        if any(request.get(k) is not False for k in FLAGS):raise ValueError('New-load control cannot confer acceptance')
        if spec!=fem.prepare(case,spec['cad_artifact'],'normal',root=root):raise ValueError('Fresh normal-load admission differs')
        fem.validate_input(spec,root=root)
        budget('independent STEP')
        reference=viaduct_cad._reference_batch([(case,Path(request['cad_root'])/case['case_id'])],output/'independent-step')
        independent=viaduct_cad.compare(case,reference[case['case_id']],exact=True,associate=True)
        for level,memory in [('coarse',2048),('fine',3072)]:
            budget(level+' mesh');model=fem.mesh(spec,level,output/('mesh-'+level),python=sys.executable)
            budget(level+' FieldCraft');field=_field(spec,model,output/('field-'+level),memory)
            budget(level+' CalculiX');ccx=_ccx(spec,model,output/('ccx-'+level))
            u,v=field['numerical']['displacement_m'][2],ccx['numerical']['displacement_m'][2]
            delta=abs(u-v)/abs(v)
            levels[level]=dict(mesh_id=model['mesh_id'],nodes=len(model['nodes']),elements=len(model['elements']),
                fieldcraft=field,calculix=ccx,cross_solver_displacement_relative_difference=delta,
                cross_solver_screen_passed=delta<=fem.SCREENS['cross_solver_displacement_relative'])
        a,b=[levels[l]['fieldcraft']['numerical']['displacement_m'][2] for l in ('coarse','fine')]
        change=abs(a-b)/abs(b)
        result=dict(schema='osr-v07-normal-fem-result/1',plan_id=request['plan_id'],input_id=spec['input_id'],
            candidate_id=spec['candidate_id'],component_geometry_id=spec['component_geometry_id'],
            independent_step=independent,levels=levels,refinement=dict(displacement_relative_change=change,
                screen_passed=change<=fem.SCREENS['displacement_refinement_relative'],mesh_independence_established=False),
            native_processes=len(calls),native_operations=calls,wall_seconds=time.monotonic()-started,
            old_mesh_reused=False,old_solve_reused=False,execution='completed',engineering_screen='unqualified-research',
            resource_enforcement='Recorded per-process native limits and between-process disk observations; no aggregate quota',**FLAGS)
        for name,sha in request['source_sha256'].items():
            if native.digest(Path(__file__) if name==PRODUCER else root/name)!=sha:raise ValueError('Source changed during experiment')
        if runtime()!=request['runtime']:raise ValueError('Runtime changed during experiment')
        result['artifact_sha256']={p.relative_to(output).as_posix():native.digest(p) for p in output.rglob('*') if p.is_file()}
        result['result_id']=identity(result);native.write(output/'result.json',result);return result
    except BaseException as exc:
        native.write(output/'failure.json',dict(type=type(exc).__name__,reason=str(exc),native_operations=calls,wall_seconds=time.monotonic()-started,**FLAGS));raise
