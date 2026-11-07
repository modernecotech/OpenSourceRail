"""Bounded SolidCraft stock generation and independent STEP measurement.

The native case's separate material regions are retained. A later FEM union or
bond hypothesis belongs to its own evaluation and never changes the candidate.
"""
from copy import deepcopy
from hashlib import sha256
from math import isfinite,fsum
from pathlib import Path
import json,os,platform,resource,shutil,subprocess,time
from . import native,solidcraft,freecad_reference
from . import viaduct_cases as cases
from .cases import FLAGS,identity

ROOT=Path(__file__).resolve().parents[3]
PRODUCER='engineering/design_search/craft_backends/viaduct_cad.py'
LIMITS=dict(timeout_s=120,memory_mb=2048,maximum_native_processes=16,parallel_workers=1)
EXACT=dict(volume_relative=1e-7,position_m=1e-7)
DIAGNOSTIC=dict(volume_relative=1e-3,position_m=1e-3)


def sources(root=ROOT):
    names=(PRODUCER,'engineering/design_search/craft_backends/solidcraft.py',
        'engineering/design_search/craft_backends/freecad_reference.py',
        'engineering/design_search/craft_backends/native.py',
        'engineering/design_search/craft_backends/__init__.py',
        'engineering/design_search/craft_backends/tools.json')
    return {**cases.sources(root),**{n:native.digest(Path(root)/n) for n in names}}


def _seal(value,key):return dict(value,**{key:identity(value)})


def plan(case,*,root=ROOT):
    cases.validate(case,root=root)
    value=dict(schema='osr-viaduct-craft-evaluation/1',candidate_id=case['candidate_id'],
        component_geometry_id=case['component_geometry_id'],case_definition_id=case['case_definition_id'],
        source_sha256=sources(root),tools=dict(solidcraft=native.pin('solidcraft'),
            independent_reference='Existing FreeCAD Flatpak; actual FreeCAD/OpenCASCADE versions recorded at execution'),
        limits=LIMITS,comparison=dict(exact=EXACT,diagnostic=DIAGNOSTIC),
        scope='Nominal stock CAD and exact STEP comparison; no installed mass, structural load or bond credit',**FLAGS)
    return _seal(value,'evaluation_id')


def compare(case,measurements,*,exact=False,associate=False):
    expected=case['expected']['part_measures'];rows=deepcopy(measurements['bodies']);unused=set(expected);mapping=[]
    limits=EXACT if exact else DIAGNOSTIC
    checks=[]
    for row in rows:
        v=row.get('volume_m3');c=row.get('center_of_mass_m');box=row.get('bbox_m')
        if row.get('closed') is not True or not isinstance(c,list) or len(c)!=3 or not isinstance(box,dict):
            raise ValueError('Closed solids and explicit native SI quantities required')
        coords=[*c,*box['min'],*box['max']]
        if len(coords)!=9 or any(type(n) not in (int,float) or not isfinite(n) for n in [v,*coords]) or v<=0:
            raise ValueError('Finite positive native quantities required')
        if exact and (row.get('valid') is not True or row.get('solid_count')!=1):raise ValueError('One exact valid solid per occurrence required')
        candidates=[]
        for name in sorted(unused):
            e=expected[name];err=abs(v-e['volume_m3'])/e['volume_m3']
            pos=max(abs(a-b) for a,b in zip(coords,[*e['centroid_m'],*e['bounds_m'][0],*e['bounds_m'][1]]))
            if err<=limits['volume_relative'] and pos<=limits['position_m']:candidates.append((name,err,pos))
        if associate:
            if len(candidates)!=1:raise ValueError('No unique exact geometric correspondence for imported occurrence')
            name,err,pos=candidates[0]
        else:
            name=row['id']
            match=[m for m in candidates if m[0]==name]
            if len(match)!=1:raise ValueError('Source occurrence name or native geometry differs')
            _,err,pos=match[0]
        unused.remove(name);mapping.append(dict(source_occurrence=name,imported_label=row['id']))
        checks.append(dict(source_occurrence=name,relative_volume_error=err,maximum_position_error_m=pos))
    if unused or len(rows)!=len(expected):raise ValueError('Native material occurrence coverage differs')
    density={e['id']:case['materials'][e['material']]['density_kg_m3'] for e in case['entities']}
    mass=fsum(row['volume_m3']*density[m['source_occurrence']] for row,m in zip(rows,mapping))
    return dict(comparison_passed=True,parts=checks,exact_brep=exact,
        source_names_preserved=all(m['source_occurrence']==m['imported_label'] for m in mapping),
        correspondence=mapping,correspondence_basis='Per-body exact volume/centroid/tight-bounds bijection' if associate else 'Source body names plus per-body geometry',
        nominal_material_mass_kg=mass,material_density_is_hypothesis=True,**FLAGS)


def _generate(case,folder,tool_root,root):
    folder.mkdir(parents=True,exist_ok=False);request=plan(case,root=root)
    native.write(folder/'case.json',case);native.write(folder/'request.json',request)
    script=folder/'commands.json';native.write(script,solidcraft.script_for(case));out=folder/'generate'
    execution=native.run('solidcraft',['run',script,'--save',out/'assembly.sc','--out',out/'assembly.step','--results','--json-out',out/'results.json'],
        out,tool_root=tool_root,timeout_s=120,memory_mb=2048,read_roots=(folder,))
    if execution['execution']!='executed':raise ValueError('Native CAD generation failed; immutable logs retained')
    measured=solidcraft.parse_measurements(json.loads((out/'results.json').read_bytes()))
    diagnostic=compare(case,measured)
    native.write(folder/'generated-measures.json',measured)
    return dict(candidate_id=case['candidate_id'],component_geometry_id=case['component_geometry_id'],
        evaluation_id=request['evaluation_id'],diagnostic=diagnostic,
        sc_sha256=native.digest(out/'assembly.sc'),step_sha256=native.digest(out/'assembly.step'),
        execution='completed',**FLAGS)


def _reference_batch(case_folders,output):
    """One separately bounded FreeCAD process; one document per candidate."""
    output.mkdir(parents=True,exist_ok=False);rows=[]
    for case,folder in case_folders:
        dest=output/case['case_id'];dest.mkdir()
        shutil.copyfile(folder/'generate/assembly.step',dest/'input.step')
        native.write(dest/'input.json',dict(expected_body_ids=None,source_step_sha256=native.digest(dest/'input.step')))
        rows.append(case['case_id'])
    native.write(output/'cases.json',rows)
    driver="""from pathlib import Path
import json
root=Path(__file__).resolve().parent
inner=INNER
for name in json.loads((root/'cases.json').read_text()):
    exec(compile(inner,str(root/name/'worker.py'),'exec'),{'__file__':str(root/name/'worker.py'),'__name__':'__main__'})
""".replace('INNER',repr(freecad_reference.WORKER))
    (output/'worker.py').write_text(driver)
    command=['/usr/bin/time','-f','{"peak_rss_kib":%M,"user_s":%U,"system_s":%S,"exit":%x}',
        '-o',str(output/'resource.json'),'flatpak','run','--unshare=network','--nofilesystem=host','--nofilesystem=home',
        '--filesystem='+str(output),'--env=QT_QPA_PLATFORM=offscreen','--env=OMP_NUM_THREADS=1',
        '--env=XDG_CONFIG_HOME='+str(output/'config'),'--env=XDG_CACHE_HOME='+str(output/'cache'),
        '--command=sh','org.freecad.FreeCAD','-c','ulimit -v 2097152 && exec FreeCADCmd "$1"','osr-viaduct-reference',str(output/'worker.py')]
    native.write(output/'command.json',dict(argv=command,worker_sha256=sha256(driver.encode()).hexdigest(),
        limits=LIMITS,one_process_for_all_cases=True,aggregate_cgroup_memory_limit=False))
    start=time.monotonic();code=None;error=None
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(2048*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CPU,(121,122));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    with (output/'stdout.log').open('wb') as out,(output/'stderr.log').open('wb') as err:
        try:
            proc=subprocess.Popen(command,cwd=output,stdout=out,stderr=err,start_new_session=True,preexec_fn=limits)
            try:code=proc.wait(timeout=120)
            except subprocess.TimeoutExpired:
                from engineering.design_search.resource_limits import stop_group
                stop_group(proc.pid);code=proc.wait();error='timeout'
        except OSError as e:error=str(e)
    result=dict(execution='completed' if code==0 and error is None else 'failed',returncode=code,error=error,
        elapsed_s=time.monotonic()-start,case_count=len(rows),per_process_address_space_mib=2048,
        aggregate_cgroup_memory_limit=False,**FLAGS)
    native.write(output/'execution.json',result)
    if result['execution']!='completed':raise ValueError('Independent FreeCAD batch failed; retained logs')
    measured={}
    for case,folder in case_folders:
        value=json.loads((output/case['case_id']/'measurement.json').read_bytes())
        freecad_reference.validate_measurements(value)
        if value['native_process_usage']['actual_address_space_limit_bytes']!=[2048*1024**2]*2:
            raise ValueError('FreeCAD native resource limit not independently observed')
        if native.digest(output/case['case_id']/'input.step')!=native.digest(folder/'generate/assembly.step'):
            raise ValueError('Immutable STEP reference input differs')
        measured[case['case_id']]=value
    return measured


def generate_portfolio(records,output,*,tool_root=native.DEFAULT_TOOLS,root=ROOT):
    records=list(records);output=Path(output).resolve()
    if not 1<=len(records)<=12 or len({c['case_id'] for c in records})!=len(records):raise ValueError('Bounded unique CAD cases required')
    for c in records:cases.validate(c,root=root)
    if output.exists():raise ValueError('Fresh immutable CAD campaign directory required')
    output.mkdir(parents=True,mode=0o700)
    request=_seal(dict(schema='osr-viaduct-craft-campaign/1',cases=records,
        evaluations=[plan(c,root=root) for c in records],source_sha256=sources(root),limits=LIMITS,**FLAGS),'request_id')
    native.write(output/'request.json',request);started=time.monotonic();result={};ready=[]
    for case in records:
        try:
            row=_generate(case,output/case['case_id'],tool_root,root)
            ready.append((case,output/case['case_id']));result[case['case_id']]=row
        except (ValueError,OSError,KeyError,TypeError) as e:
            result[case['case_id']]=dict(candidate_id=case['candidate_id'],component_geometry_id=case['component_geometry_id'],execution='failed',reason=str(e),**FLAGS)
    try:
        measured=_reference_batch(ready,output/'freecad-reference') if ready else {}
        for case,folder in ready:
            try:result[case['case_id']]['exact_step']=compare(case,measured[case['case_id']],exact=True,associate=True)
            except (ValueError,OSError,KeyError,TypeError) as e:result[case['case_id']]['exact_step']=dict(comparison_passed=False,reason=str(e),**FLAGS)
    except (ValueError,OSError,KeyError,TypeError) as e:
        for case,folder in ready:result[case['case_id']]['exact_step']=dict(comparison_passed=False,reason=str(e),**FLAGS)
    if sources(root)!=request['source_sha256']:raise ValueError('Source epoch changed during native execution; no publication')
    slots=len(list(output.glob('*/generate/execution.json')))+(1 if ready else 0)
    if slots>16:raise ValueError('Native process budget exceeded')
    value=dict(schema='osr-viaduct-craft-result/1',request_id=request['request_id'],source_sha256=request['source_sha256'],
        cases=result,case_count=len(records),native_processes=slots,fresh_native_processes=slots,cached_native_evaluations=0,
        elapsed_s=time.monotonic()-started,nominal_geometry_comparison_passed=all(r.get('exact_step',{}).get('comparison_passed') is True for r in result.values()),
        default_backend_changed=False,complete_bridge_analysis=False,
        artifact_sha256={p.relative_to(output).as_posix():native.digest(p) for p in sorted(output.rglob('*')) if p.is_file()},**FLAGS)
    value=_seal(value,'result_id');native.write(output/'manifest.json',value);return value


def generate(case,output,*,tool_root=native.DEFAULT_TOOLS,root=ROOT):
    return generate_portfolio([case],output,tool_root=tool_root,root=root)


def verify(output,case=None,*,root=ROOT):
    output=Path(output).resolve();m=json.loads((output/'manifest.json').read_bytes())
    if m.get('result_id')!=identity({k:v for k,v in m.items() if k!='result_id'}):raise ValueError('CAD result seal differs')
    req=json.loads((output/'request.json').read_bytes())
    if req.get('request_id')!=identity({k:v for k,v in req.items() if k!='request_id'}) or m['request_id']!=req['request_id']:
        raise ValueError('CAD request seal differs')
    if req['source_sha256']!=sources(root) or m['source_sha256']!=sources(root):raise ValueError('CAD source epoch differs')
    if req['limits']!=LIMITS or req['evaluations']!=[plan(c,root=root) for c in req['cases']]:raise ValueError('CAD evaluation or resource request differs')
    if case is not None and case not in req['cases']:raise ValueError('Requested candidate does not match CAD campaign')
    inventory={p.relative_to(output).as_posix():native.digest(p) for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if inventory!=m['artifact_sha256']:raise ValueError('CAD artifact inventory differs')
    if any(m.get(k) is not False for k in FLAGS) or any(req.get(k) is not False for k in FLAGS):raise ValueError('CAD cannot confer release')
    for c in req['cases']:
        cases.validate(c,root=root);row=m['cases'][c['case_id']]
        if any(row.get(k)!=c[k] for k in ('candidate_id','component_geometry_id')):raise ValueError('Mixed CAD candidate identities')
        if row['execution']!='completed':continue
        folder=output/c['case_id']
        if json.loads((folder/'case.json').read_bytes())!=c or json.loads((folder/'request.json').read_bytes())!=plan(c,root=root):raise ValueError('CAD case input differs')
        generated=solidcraft.parse_measurements(json.loads((folder/'generate/results.json').read_bytes()))
        if compare(c,generated)!=row['diagnostic']:raise ValueError('CAD diagnostic differs')
        if row.get('exact_step',{}).get('comparison_passed'):
            measured=json.loads((output/'freecad-reference'/c['case_id']/'measurement.json').read_bytes())
            freecad_reference.validate_measurements(measured)
            if compare(c,measured,exact=True,associate=True)!=row['exact_step']:raise ValueError('Exact STEP correspondence differs')
        if native.digest(folder/'generate/assembly.step')!=row['step_sha256'] or native.digest(folder/'generate/assembly.sc')!=row['sc_sha256']:
            raise ValueError('Export geometry differs')
    return m
