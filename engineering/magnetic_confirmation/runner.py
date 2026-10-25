"""Bounded new continuation runs; historical drivers/archives stay unchanged."""
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from engineering.design_search.storage import atomic_immutable
from engineering.trip_dynamics.fixtures.magnetics import finite_coupon as legacy
from . import analysis,constitutive
from .formulation import formulation

SCHEMA='osr-magnetic-confirmation/1'
PLAN={'coarse':dict(margin_m=.15,near_mesh_size_m=.023,gap_mesh_size_m=.008),'fine':dict(margin_m=.15,near_mesh_size_m=.017,gap_mesh_size_m=.006),'expanded':dict(margin_m=.25,near_mesh_size_m=.017,gap_mesh_size_m=.006)}
FLAGS=dict(force_map_generated=False,hover_executed=False,material_proxy_validated=False,configuration_adopted=False,engineering_accepted=False,physical_accepted=False)


def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(v):return sha256(encoded(v)).hexdigest()
def file_hash(p):return sha256(Path(p).read_bytes()).hexdigest()
def write(path,value):return atomic_immutable(path,encoded(value))


def source_snapshot(root):
    root=Path(root);code=Path(__file__).parent
    paths={p for p in code.rglob('*.py') if '__pycache__' not in p.parts}
    paths.update((Path(legacy.__file__),Path(sys.modules['engineering.design_search.storage'].__file__)))
    paths.update(analysis.magnets.source_paths())
    records={}
    for path in sorted(paths):
        if path.is_symlink():raise ValueError('ordinary implementation sources required')
        # The source checkout may differ from the data root in an isolated worktree.
        parts=path.parts;index=parts.index('engineering');name='/'.join(parts[index:]);records[name]=file_hash(path)
    source=legacy.source_input(root);publication=root/'docs/design-engine/vehicle-optimisation/manifest.json';manifest=json.loads(publication.read_bytes())
    for name,digest in source['source_sha256'].items():
        if manifest['files_sha256'].get(Path(name).name)!=digest:raise ValueError('retained source payload differs from vehicle publication manifest')
    records[publication.relative_to(root).as_posix()]=file_hash(publication)
    records.update(source['source_sha256'])
    return records


def inventory(directory,exclude=()):
    directory=Path(directory);result={}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():raise ValueError('symlink in retained numerical output')
        if path.is_file():
            name=path.relative_to(directory).as_posix()
            if name not in exclude:result[name]=file_hash(path)
    return result


def _tool(getdp):
    path=Path(getdp).resolve(strict=True)
    if not path.is_file():raise ValueError('GetDP executable required')
    before=file_hash(path);p=subprocess.run([str(path),'-version'],capture_output=True,text=True,timeout=10,check=True);version=(p.stdout+p.stderr).strip()
    if version!='3.5.0':raise ValueError('this confirmation requires the retained GetDP 3.5.0 toolchain')
    return dict(path=str(path),sha256=before,version=version,version_stdout=p.stdout,version_stderr=p.stderr,python=sys.version,packages={name:importlib.metadata.version(name) for name in ('numpy','gmsh')})


def _terminate(process):
    # Hard deadline: kill the entire newly created worker/solver process group,
    # even when the direct worker exits before a descendant.
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    process.wait(timeout=5)


def _derived(directory,request,name):
    directory=Path(directory);record=json.loads((directory/'calculation.json').read_bytes())
    if record.get('case')!=name or record.get('candidate_id')!=request['source']['vehicle_candidate_id'] or record.get('magnet_component_id')!=request['source']['value']['physical_id'] or record.get('request_id')!=request['request_id']:raise ValueError('case candidate/component/request identity differs')
    if record.get('settings')!=PLAN[name] or json.loads((directory/'source-input.json').read_bytes())!=request['source']:raise ValueError('case settings/physical input copy differs')
    expected=dict(record)
    try:
        if 'mesh' in record:
            expected['mesh_verification']=analysis.validate_mesh(directory/'coupon.msh',record['mesh'],request['source']['value'],PLAN[name]['margin_m'])
            if (directory/'coupon.pro').is_file() and (directory/'coupon.pro').read_text()!=formulation(request['source']['value'],record['mesh'],request['contours_m']):raise ValueError('executed formulation differs from explicit current generator')
        stdout=(directory/'getdp.stdout.log').read_text(errors='replace') if (directory/'getdp.stdout.log').is_file() else ''
        expected['continuation']=analysis.parse_stages(stdout)
        expected['full_source_converged']=expected['continuation']['full_source_converged']
        admitted=record.get('solver_returncode')==0 and expected['full_source_converged']
        if admitted:
            if not (directory/'coupon.pro').is_file():raise ValueError('executed formulation missing')
            expected['analysis']=analysis.analyze(directory,request['source'],record['mesh'],request['contours_m'],legacy)
            expected['execution_status']='completed';expected['force_credit']=True
        else:
            expected['force_credit']=False;expected.pop('analysis',None)
            expected['execution_status']='nonconverged' if record.get('solver_returncode')==0 else 'failed'
    except (ValueError,OSError,KeyError,IndexError) as error:
        expected.update(execution_status='failed',force_credit=False,full_source_converged=False,error_type=type(error).__name__,error=str(error));expected.pop('analysis',None)
    return json.loads(encoded(expected))


def run(output,root,getdp,reuse_mesh_root=None,cases=('coarse','fine','expanded')):
    root=Path(root).resolve();output=Path(output).absolute();cases=tuple(cases)
    if not cases or len(cases)>3 or len(set(cases))!=len(cases) or any(name not in PLAN for name in cases):raise ValueError('unique bounded coarse/fine/expanded case names required')
    source=legacy.source_input(root);value=analysis.validate_source(source);before=source_snapshot(root);tool=_tool(getdp)
    request=dict(schema=SCHEMA,source=source,source_sha256=before,getdp=tool,cases=list(cases),case_settings={k:PLAN[k] for k in cases},contours_m=analysis.contours(value),root=str(root),reuse_mesh_root=str(Path(reuse_mesh_root).resolve()) if reuse_mesh_root is not None else None,budget=dict(seconds_per_case=300,numerical_workers=1,max_cases=3),temperature_C=80.,currents_A={},frame=dict(x='travel',y='left',z='up',handedness='right',moment_origin_m=[0.,0.,0.]),**FLAGS)
    request['request_id']=identity(request);output.mkdir(parents=True,exist_ok=False)
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):raise ValueError('ordinary fresh run directory required')
    write(output/'request.json',request);write(output/'source-input.json',source);write(output/'jacobian-fixture.json',constitutive.fixture(value['materials']['steel']))
    if not json.loads((output/'jacobian-fixture.json').read_bytes())['passed']:raise ValueError('constitutive tangent fixture failed before solving')
    rows=[];code_root=Path(__file__).resolve().parents[2]
    for name in cases:
        directory=output/name;directory.mkdir();started=time.monotonic();command=[sys.executable,'-m','engineering.magnetic_confirmation.worker','--request',str(output/'request.json'),'--case',name,'--output',str(directory)]
        env=dict(os.environ,PYTHONPATH=str(code_root)+os.pathsep+str(root),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        with (directory/'worker.stdout.log').open('wb') as stdout,(directory/'worker.stderr.log').open('wb') as stderr:
            process=subprocess.Popen(command,cwd=code_root,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try:code=process.wait(timeout=300);timed_out=False
            except subprocess.TimeoutExpired:_terminate(process);code=process.returncode;timed_out=True
        execution=dict(command=command,returncode=code,timed_out=timed_out,elapsed_s=time.monotonic()-started)
        write(directory/'execution.json',execution)
        if not timed_out and code==0 and (directory/'calculation.json').is_file():
            try:row=_derived(directory,request,name)
            except (ValueError,OSError,KeyError) as error:row=dict(case=name,execution_status='failed',force_credit=False,full_source_converged=False,error=str(error))
        else:row=dict(case=name,execution_status='interrupted' if timed_out else 'failed',force_credit=False,full_source_converged=False,error='Case wall-clock deadline' if timed_out else 'Worker did not complete')
        row['execution']=execution;row['files_sha256']=inventory(directory);rows.append(row)
    if source_snapshot(root)!=before or file_hash(tool['path'])!=tool['sha256']:raise ValueError('implementation, physical source or GetDP changed during campaign')
    result=dict(schema=SCHEMA,request_id=request['request_id'],candidate_id=source['vehicle_candidate_id'],magnet_component_id=value['physical_id'],execution_status='completed',rows=rows,comparisons=analysis.comparisons(rows),jacobian_fixture=json.loads((output/'jacobian-fixture.json').read_bytes()),scope='Finite 1 m N35UH at 80°C/zero-current coupon, isotropic 50 Hz steel proxy. Continuation and sampled mesh/domain/air-contour diagnostic only; no hover/full force map/selection.',**FLAGS)
    write(output/'result.json',result);manifest=dict(schema=SCHEMA,request_id=request['request_id'],source_sha256=before,files_sha256=inventory(output,exclude=('manifest.json',)),**FLAGS);write(output/'manifest.json',manifest)
    verify(output,root=root);return result


def verify(output,*,root=None):
    directory=Path(output);request=json.loads((directory/'request.json').read_bytes());root=Path(root or request['root']);manifest=json.loads((directory/'manifest.json').read_bytes());result=json.loads((directory/'result.json').read_bytes())
    if manifest.get('schema')!=SCHEMA or request.get('schema')!=SCHEMA or result.get('schema')!=SCHEMA or request.get('request_id')!=identity({k:v for k,v in request.items() if k!='request_id'}):raise ValueError('confirmation schema/request identity differs')
    expected_sources=source_snapshot(root)
    if request['source_sha256']!=expected_sources or manifest['source_sha256']!=expected_sources or request['source']!=legacy.source_input(root):raise ValueError('confirmation physical/implementation source binding differs')
    analysis.validate_source(request['source'])
    if not request['cases'] or any(name not in PLAN for name in request['cases']):raise ValueError('bounded known case inventory required')
    if request.get('temperature_C')!=80. or request.get('currents_A')!={} or request.get('frame')!=dict(x='travel',y='left',z='up',handedness='right',moment_origin_m=[0.,0.,0.]):raise ValueError('fixed operating point/frame differs')
    if json.loads((directory/'source-input.json').read_bytes())!=request['source']:raise ValueError('top-level source input copy differs')
    if result.get('execution_status')!='completed':raise ValueError('collection disposition differs')
    if request['case_settings']!={k:PLAN[k] for k in request['cases']} or len(request['cases'])>3 or len(set(request['cases']))!=len(request['cases']) or request['budget']!=dict(seconds_per_case=300,numerical_workers=1,max_cases=3) or request['contours_m']!=analysis.contours(request['source']['value']):raise ValueError('case, domain, contour or budget contract differs')
    if request['getdp']['sha256']!=file_hash(request['getdp']['path']):raise ValueError('executed GetDP binary differs')
    if manifest['files_sha256']!=inventory(directory,exclude=('manifest.json',)):raise ValueError('confirmation payload inventory/hash differs')
    for record in (manifest,request,result):
        if any(record.get(k) is not v for k,v in FLAGS.items()):raise ValueError('confirmation scope/acceptance flags differ')
        if record.get('request_id')!=request['request_id']:raise ValueError('confirmation request linkage differs')
    if result['candidate_id']!=request['source']['vehicle_candidate_id'] or result['magnet_component_id']!=request['source']['value']['physical_id'] or [r['case'] for r in result['rows']]!=request['cases']:raise ValueError('candidate/component/case membership differs')
    fixture=constitutive.fixture(request['source']['value']['materials']['steel'])
    if json.loads((directory/'jacobian-fixture.json').read_bytes())!=fixture or result['jacobian_fixture']!=fixture or not fixture['passed']:raise ValueError('Jacobian mathematical fixture differs')
    for row in result['rows']:
        case=directory/row['case'];execution=json.loads((case/'execution.json').read_bytes())
        if row['execution']!=execution or row['files_sha256']!=inventory(case):raise ValueError('case execution/inventory differs')
        if not execution['timed_out'] and execution['returncode']==0 and (case/'calculation.json').is_file():
            expected=_derived(case,request,row['case']);expected.update(execution=execution,files_sha256=inventory(case))
            if row!=expected:raise ValueError('recomputed stage/mesh/contour/force/demagnetisation result differs')
        elif row.get('force_credit') or row.get('full_source_converged') or 'analysis' in row:raise ValueError('interrupted/failed case cannot receive force credit')
    if result['comparisons']!=analysis.comparisons(result['rows']):raise ValueError('recomputed mesh/domain/contour comparisons differ')
    return dict(current=True,case_count=len(result['rows']),full_source_cases=sum(bool(r['force_credit']) for r in result['rows']),source_sha256=expected_sources,**FLAGS)


def publish(output,*,run_dir,root=None):
    from .publication import publish as publisher
    return publisher(output,run_dir=run_dir,root=root)
