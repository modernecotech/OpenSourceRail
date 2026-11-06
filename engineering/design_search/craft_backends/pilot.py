"""Opt-in backend sidecar: immutable native evidence, never baseline promotion."""
from pathlib import Path
import json
import math
import platform
import shutil
import time
import tomllib
from . import FLAGS, PROVIDERS, identity
from . import cases as fixtures, native, solidcraft, fieldcraft

ROOT = Path(__file__).resolve().parents[3]
POLICY = 'campaigns/craft-backend-pilot.toml'


def sources(root=ROOT):
    from . import handoff
    names = [POLICY, *[str(p.relative_to(ROOT)) for p in Path(__file__).parent.glob('*.py')],
             'engineering/design_search/craft_backends/tools.json']
    return {**{n:native.digest(Path(root)/n) for n in sorted(names)},**handoff.sources(root)}


def plan(root=ROOT,*,include_rc=False):
    policy = tomllib.loads((Path(root)/POLICY).read_text())
    if (policy['schema']!='osr-craft-backend-pilot/1' or policy['selected_reference_changed'] is not False
        or policy['physical_accepted'] is not False or policy['parallel_native_workers']!=1
        or not 1<=policy['timeout_s']<=120 or not 256<=policy['memory_mb_per_process']<=2048
        or not 1<=policy['max_native_processes']<=32 or not 1<=policy['max_parts']<=30):
        raise ValueError('Bounded sequential non-promoting pilot policy required')
    records = fixtures.cases(root)
    if sum(c['expected']['part_count'] for c in records)>policy['max_parts']:
        raise ValueError('Declared CAD occurrence budget exceeded')
    slots=5*len(records)+5+(4 if include_rc else 0)
    if slots>policy['max_native_processes']:raise ValueError('Declared native process budget cannot admit this pilot')
    reference_tools={name:native.digest(Path(path).resolve()) if (path:=shutil.which(name)) else None
                     for name in ('ccx','bwrap','flatpak','time')}
    result = dict(schema='osr-craft-pilot-request/1', providers=PROVIDERS,
                  policy=policy, toolchain=json.loads(native.LOCK.read_bytes()),
                  source_sha256=sources(root), cases=records,
                  execution_options=dict(include_rc=include_rc,admitted_native_process_slots=slots),
                  runtime=dict(python=platform.python_version(),machine=platform.machine(),system=platform.system(),reference_tool_sha256=reference_tools),
                  evaluation_scope='Provider comparison; existing railway/BIM/delivery contracts retained',
                  **FLAGS)
    return dict(result, evaluation_id=identity(result))


def _limits(request):
    return dict(timeout_s=request['policy']['timeout_s'],memory_mb=request['policy']['memory_mb_per_process'])


def compare_geometry(case, measured, *, exact=False, policy=None,require_closed=True):
    """Check each named occurrence, not just a compensating total volume."""
    fixtures.validate_case(case)
    policy = policy or tomllib.loads((ROOT/POLICY).read_text())['comparison']
    relative = policy['exact_volume_relative' if exact else 'diagnostic_volume_relative']
    position = policy['exact_position_m' if exact else 'diagnostic_position_m']
    rows = measured.get('bodies', [])
    ids = [b.get('id') for b in rows]
    expected = case['expected']['part_measures']
    if len(ids)!=len(set(ids)) or set(ids)!=set(expected):
        raise ValueError('Body occurrence names or coverage differ')
    checks = []
    for b in rows:
        e=expected[b['id']]
        volume=b.get('volume_m3'); center=b.get('center_of_mass_m'); box=b.get('bbox_m')
        if (type(volume) not in (float,int) or not math.isfinite(volume) or volume<=0
            or (require_closed and b.get('closed') is not True) or center is None or box is None):
            raise ValueError('Positive closed material solids and explicit SI measurements required')
        coords=[*center,*box['min'],*box['max']]
        if len(coords)!=9 or any(type(x) not in (int,float) or not math.isfinite(x) for x in coords):
            raise ValueError('Finite SI positions required')
        volume_error=abs(volume-e['volume_m3'])/e['volume_m3']
        position_error=max(abs(a-b) for a,b in zip(coords,[*e['centroid_m'],*e['bounds_m'][0],*e['bounds_m'][1]]))
        passed=volume_error<=relative and position_error<=position and (not exact or b.get('valid') is True)
        checks.append(dict(id=b['id'], relative_volume_error=volume_error,
                           maximum_position_error_m=position_error, comparison_passed=passed))
    return dict(parts=checks, comparison_passed=all(c['comparison_passed'] for c in checks),
        exact_brep=exact, closure_checked=require_closed, tolerance=dict(volume_relative=relative, position_m=position), **FLAGS)


def associate_exact(case, measured, comparison):
    """Unique geometric correspondence; explicitly NOT native name retention.

    Some STEP importers label solids with the product name. A bijection based
    on *all* volume, centroid and bounding coordinates can check geometry while
    preserving that naming failure. Ambiguous identical shapes are refused.
    """
    from copy import deepcopy
    result=deepcopy(measured)
    # The reference runner exposes its same native list at both top level and
    # under `native`. Break that Python alias before adding correspondence IDs;
    # raw importer labels must stay raw after JSON save/reopen as well.
    result['bodies']=deepcopy(measured['bodies'])
    unused=set(case['expected']['part_measures']);mapping=[]
    for body in result['bodies']:
        matches=[]
        for name in sorted(unused):
            e=case['expected']['part_measures'][name]
            position=[*body['center_of_mass_m'],*body['bbox_m']['min'],*body['bbox_m']['max']]
            expected=[*e['centroid_m'],*e['bounds_m'][0],*e['bounds_m'][1]]
            if (abs(body['volume_m3']-e['volume_m3'])<=e['volume_m3']*comparison['exact_volume_relative']
                and max(abs(a-b) for a,b in zip(position,expected))<=comparison['exact_position_m']):matches.append(name)
        if len(matches)!=1:raise ValueError('Independent STEP solids do not have a unique exact geometric correspondence')
        name=matches[0];unused.remove(name)
        mapping.append(dict(imported_label=body['id'],source_occurrence=name))
        body['id']=name
    if unused:raise ValueError('Independent STEP occurrence coverage incomplete')
    result.update(native_names_preserved=all(m['imported_label']==m['source_occurrence'] for m in mapping),
                  geometric_correspondence=mapping,identity_basis='Unique exact volume/centroid/bounds matching; source names remain in sidecar')
    return result


def _reply(replies, index=0):
    row=next((r for r in replies if r.get('id')==index+2),None)
    if row is None: raise ValueError('Missing JSON-RPC response')
    return native.payload(row)


def _require_execution(result):
    if result['execution']!='executed': raise ValueError('Native process failed; see preserved logs')


def _batch(value):
    if value.get('failed') or value.get('ok') is False:
        raise ValueError('Native command batch failed: '+str(value.get('failed')))
    return value


def _capture(folder, function):
    """Retain a failed stage and keep independent pilot stages running."""
    try:
        value=function()
        result=dict(status='completed', result=value, **FLAGS)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        result=dict(status='held', reason=str(exc), **FLAGS)
    native.write(folder/'stage.json',result)
    return result


def cad(case, folder, *, request, tool_root=native.DEFAULT_TOOLS):
    folder.mkdir(parents=True,exist_ok=False)
    native.write(folder/'case.json',case)
    script=folder/'commands.json';native.write(script,solidcraft.script_for(case))
    work=folder/'generate'
    limits=dict(**_limits(request),tool_root=tool_root)
    execution=native.run('solidcraft',['run',script,'--save',work/'assembly.sc','--out',work/'assembly.step',
        '--results','--json-out',work/'results.json'],work,read_roots=(folder,),**limits)
    _require_execution(execution)
    measured=solidcraft.parse_measurements(json.loads((work/'results.json').read_bytes()))
    native.write(folder/'generated-measures.json',measured)
    checks={'generated':compare_geometry(case,measured,policy=request['policy']['comparison'])}
    for extension in ('sc','step'):
        reopen=folder/('reopen-'+extension)
        e=native.run('solidcraft',['eval',work/('assembly.'+extension),'--json-out',reopen/'measure.json'],
            reopen,read_roots=(folder,),**limits)
        _require_execution(e)
        m=solidcraft.parse_measurements(json.loads((reopen/'measure.json').read_bytes()))
        checks['reopen_'+extension]=compare_geometry(case,m,policy=request['policy']['comparison'])
    from . import freecad_reference
    reference=freecad_reference.run(work/'assembly.step',folder/'freecad-reference',
        timeout_s=limits['timeout_s'],memory_mb=limits['memory_mb'])
    if reference['execution']!='completed':raise ValueError('Independent STEP reference failed; see preserved measurements/logs')
    associated=associate_exact(case,reference,request['policy']['comparison'])
    native.write(folder/'independent-correspondence.json',associated)
    checks['exact_step']=compare_geometry(case,associated,exact=True,policy=request['policy']['comparison'])
    checks['exact_step']['native_names_preserved']=associated['native_names_preserved']
    field=interoperability(work/'assembly.sc',folder/'fieldcraft-interchange',case=case,tool_root=tool_root,limits=_limits(request))
    native.write(folder/'comparisons.json',checks)
    return dict(case_id=case['case_id'],candidate_id=case['candidate_id'],
                component_geometry_id=case['component_geometry_id'],checks=checks,
                geometry_comparison_passed=all(c['comparison_passed'] for c in checks.values()),
                native_step_names_preserved=associated['native_names_preserved'],fieldcraft_interchange=field,
                automatic_backend_promotion=False,
                material_mass_scope=case['expected'], native_geometry_units='mm', returned_units='m',**FLAGS)


def interoperability(design, folder, *, case=None, tool_root=native.DEFAULT_TOOLS,limits=None):
    folder.mkdir(parents=True,exist_ok=False)
    calls=[('open',dict(path=str(design),model='new')),
           ('execute',dict(command='model.units',params=dict(system='m-kg-s-N-Pa'))),
           ('execute',dict(command='geometry.open',params=dict(path=str(design),model='new'))),
           ('inspect_model',{})]
    face_check=case and case['case_id']=='asymmetric-si-control'
    if face_check:
        calls += [('execute',dict(command='model.set.create',params=dict(name='OSR-Root',geometry=[dict(body=case['entities'][0]['id'],face='F1:-x')]))),
                  ('execute',dict(command='geometry.open',params=dict(path=str(design),model='keep'))),('inspect_model',{})]
    e,replies=native.mcp('fieldcraft',calls,folder/'native',read_root=folder.parent,tool_root=tool_root,**(limits or {}))
    _require_execution(e)
    result=decode_interchange(replies,case)
    native.write(folder/'readback.json',result['readback'])
    return result


def decode_interchange(replies,case=None):
    face_check=case and case['case_id']=='asymmetric-si-control'
    tools=['open','execute','execute','inspect_model']+(['execute','execute','inspect_model'] if face_check else [])
    ids=[r.get('id') for r in replies if r.get('id') is not None]
    if len(set(ids))!=len(ids) or set(ids)!=set(range(1,len(tools)+2)):
        raise ValueError('Interchange JSON-RPC response coverage differs')
    results=[]
    for i,tool in enumerate(tools):
        try:results.append(dict(tool=tool,status='completed',result=_reply(replies,i)))
        except ValueError as exc:results.append(dict(tool=tool,status='rejected',reason=str(exc)))
    verified=False;comparison=None
    if case and results[2]['status']=='completed' and results[3]['status']=='completed':
        opened=results[2]['result'];inspected=results[3]['result']
        if opened.get('errors') or opened.get('mismatched') or opened.get('renamed'):
            raise ValueError('Native design rebuild or identity differs')
        model=inspected['model']
        if model.get('display_units')!='m-kg-s-N-Pa' or model.get('own_units') is not True:
            raise ValueError('FieldCraft geometry measures require explicit SI units')
        bodies=[dict(id=b['name'],volume_m3=b['volume'],center_of_mass_m=b['centroid'],
                     bbox_m=dict(zip(('min','max'),b['bbox']))) for b in inspected['bodies']]
        # FieldCraft does not return solid-closure evidence here. Compare measures
        # only; closure is separately checked by the CAD and exact STEP stages.
        comparison=compare_geometry(case,dict(bodies=bodies),require_closed=False)
        verified=comparison['comparison_passed']
    persistent=False
    if face_check and all(r['status']=='completed' for r in results[4:]):
        reopened=results[5]['result'];model=results[6]['result']['model']
        persistent=(not any(reopened.get('stale',{}).values()) and not reopened.get('errors') and
                    not reopened.get('renamed') and not reopened.get('mismatched') and
                    model['definitions']['sets']==1 and model.get('display_units')=='m-kg-s-N-Pa')
    return dict(native_extension_dispatch=results[0]['status'],
                direct_geometry_open=results[2]['status'],readback=results,
                geometry_names_and_units_verified=verified,geometry_comparison=comparison,
                named_face_set_reopen_verified=persistent,
                materials_transferred=False,candidate_metadata_carried_by='source-bound sidecar',
                scope='Measures/name interchange; material definitions assigned independently for analysis',**FLAGS)


def prerelease(case, folder, *, tool_root=native.DEFAULT_TOOLS,limits=None):
    folder.mkdir(parents=True,exist_ok=False)
    limits=limits or {}
    script=folder/'commands.json';native.write(script,solidcraft.script_for(case))
    generated=folder/'generate'
    e=native.run('solidcraft-rc',['run',script,'--save',generated/'assembly.sc','--results','--json-out',generated/'results.json'],
                 generated,read_roots=(folder,),tool_root=tool_root,**limits)
    _require_execution(e)
    direct=interoperability(generated/'assembly.sc',folder/'direct-fieldcraft',tool_root=tool_root,limits=limits)
    exported=folder/'tagged-export'
    e,replies=native.mcp('solidcraft-rc',[('open',dict(path=str(generated/'assembly.sc'))),
        ('export',dict(path=str(exported/'assembly.3mf'),format='3mf-tagged'))],exported,
        read_root=folder,tool_root=tool_root,**limits)
    _require_execution(e)
    for i in range(2):_batch(_reply(replies,i))
    e,replies=native.mcp('fieldcraft',[('open',dict(path=str(exported/'assembly.3mf'))),('inspect_model',{})],
                       folder/'tagged-import',read_root=folder,tool_root=tool_root,**limits)
    _require_execution(e);imported=_reply(replies);inspected=_reply(replies,1)
    return dict(direct_native_interchange=direct,tagged_mesh_import=imported,inspection=inspected,
                exact_brep=False,parametric_history_transferred=False,materials_transferred=False,
                full_identity_and_geometry_preservation_verified=False,
                scope='Tagged surface fallback only; not interchangeable with exact parametric geometry',**FLAGS)


def controls(folder, *, request,tool_root=native.DEFAULT_TOOLS):
    folder.mkdir(parents=True,exist_ok=False)
    coarse=fieldcraft.cantilever_commands();fine=fieldcraft.remesh_cantilever_commands()
    e,replies=native.mcp('fieldcraft',[('batch',dict(commands=coarse+fine))],folder/'bending',
                         read_root=folder,tool_root=tool_root,**_limits(request))
    _require_execution(e)
    result=_reply(replies);rows=fieldcraft.batch_results(result,len(coarse)+len(fine))
    def packet(part):return dict(ok=True,failed=None,completed=len(part),results=part)
    c=fieldcraft.parse_cantilever_result(packet(rows[:len(coarse)]),len(coarse))
    f=fieldcraft.parse_cantilever_result(packet(rows[len(coarse):]),len(fine))
    refinement=fieldcraft.compare_refinement(c,f)
    commands=fieldcraft.axial_commands()
    e,replies=native.mcp('fieldcraft',[('batch',dict(commands=commands))],folder/'axial',read_root=folder,tool_root=tool_root,**_limits(request))
    _require_execution(e)
    axial=fieldcraft.parse_axial_result(_reply(replies),len(commands))
    from . import calculix_reference
    reference=calculix_reference.run(folder/'calculix-reference',**_limits(request))
    result=compare_controls(c,f,axial,reference,request)
    native.write(folder/'controls.json',result)
    return result


def compare_controls(c,f,axial,reference,request):
    refinement=fieldcraft.compare_refinement(c,f)
    cross=[]
    if reference.get('state')!='completed':raise ValueError('Independent CalculiX controls did not complete')
    for name,field,axis in [('cantilever-coarse',c,2),('cantilever-fine',f,2),('axial',axial,0)]:
        ccx=reference['cases'][name]['comparison']['displacement_m'][axis]
        relative=abs(field['displacement_m'][axis]-ccx)/abs(ccx)
        tolerance=request['policy']['comparison']['structural_cross_solver_relative']
        cross.append(dict(case=name,relative_displacement_difference=relative,tolerance=tolerance,comparison_passed=relative<=tolerance))
    passed=(all(v['numerical_screen_passed'] for v in (c,f,axial)) and
            refinement['refinement_screen_passed'] and reference['numerical_screens_passed'] and all(v['comparison_passed'] for v in cross))
    result=dict(coarse=c,fine=f,refinement=refinement,axial=axial,calculix_reference=reference,
                cross_solver=cross,numerical_controls_passed=passed,**FLAGS)
    return result


def software_screen(stages,request):
    control=stages.get('asymmetric-si-control',{}).get('result',{})
    return (all(stages[c['case_id']]['status']=='completed' and
        stages[c['case_id']]['result']['geometry_comparison_passed'] and
        stages[c['case_id']]['result']['fieldcraft_interchange']['geometry_names_and_units_verified'] for c in request['cases']) and
        control.get('fieldcraft_interchange',{}).get('named_face_set_reopen_verified') is True and
        stages['linear-controls']['status']=='completed' and stages['linear-controls']['result']['numerical_controls_passed'])


def run(output, *, root=ROOT, tool_root=native.DEFAULT_TOOLS,include_rc=False):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh private output directory required')
    request=plan(root,include_rc=include_rc);output.mkdir(parents=True,mode=0o700)
    native.write(output/'request.json',request)
    started=time.monotonic();stages={}
    for case in request['cases']:
        folder=output/case['case_id']
        stages[case['case_id']]=_capture(folder,lambda c=case,f=folder:cad(c,f,request=request,tool_root=tool_root))
    if include_rc:
        control=next(c for c in request['cases'] if c['case_id']=='asymmetric-si-control')
        stages['prerelease-interchange']=_capture(output/'prerelease-interchange',lambda:prerelease(control,output/'prerelease-interchange',tool_root=tool_root,limits=_limits(request)))
    stages['linear-controls']=_capture(output/'linear-controls',lambda:controls(output/'linear-controls',request=request,tool_root=tool_root))
    from . import handoff
    native.write(output/'delivery-handoffs.json',[handoff.build(c,root) for c in request['cases']])
    # Reconstruct the request after execution to refuse mid-run input/source drift.
    if plan(root,include_rc=include_rc)!=request:raise ValueError('Pilot inputs changed during execution; results retained without promotion')
    inventory={str(p.relative_to(output)):native.digest(p) for p in sorted(output.rglob('*')) if p.is_file()}
    native_runs=[json.loads(p.read_bytes()) for p in output.rglob('execution.json')]
    freecad_runs=[json.loads(p.read_bytes()) for p in output.glob('*/freecad-reference/result.json')]
    ccx_runs=[json.loads(p.read_bytes()) for p in output.glob('linear-controls/calculix-reference/*/result.json')]
    rss=[r.get('usage',{}).get('peak_rss_kib') for r in native_runs+freecad_runs if r.get('usage')]
    rss += [r.get('process',{}).get('peak_rss_KiB') for r in ccx_runs]
    process_count=len(native_runs)+len(freecad_runs)+len(ccx_runs)
    if process_count>request['execution_options']['admitted_native_process_slots']:
        raise ValueError('Native process inventory exceeded admitted slots; retained without promotion')
    result=dict(schema='osr-craft-pilot-result/1',evaluation_id=request['evaluation_id'],
        stages=stages,elapsed_s=time.monotonic()-started,artifact_sha256=inventory,
        measurements=dict(native_processes=process_count,cached_native_evaluations=0,
            maximum_individual_process_rss_kib=max([n for n in rss if n is not None],default=None),
            artifact_bytes=sum((output/p).stat().st_size for p in inventory),
            cache_context='Fresh native processes/private tool caches; OS page cache uncontrolled',
            comparison_scope='SolidCraft generation versus FreeCAD reimport is not a like-for-like CAD rebuild benchmark'),
        default_backends_changed=False,engineering_component_analysis_complete=False,
        **FLAGS)
    result['software_pilot_passed']=software_screen(stages,request)
    result['result_id']=identity(result);native.write(output/'manifest.json',result)
    return result


def verify(output, *, root=ROOT):
    output=Path(output).resolve();manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest.get('result_id')!=identity({k:v for k,v in manifest.items() if k!='result_id'}):
        raise ValueError('Pilot result identity differs')
    if any(manifest.get(k) is not False for k in FLAGS):raise ValueError('Pilot cannot grant physical acceptance')
    request=json.loads((output/'request.json').read_bytes())
    if request!=plan(root,include_rc=request['execution_options']['include_rc']) or request['evaluation_id']!=manifest['evaluation_id']:
        raise ValueError('Pilot source, physical case, assumptions, resource or tool context differs')
    files={str(p.relative_to(output)):p for p in output.rglob('*') if p.is_file() and p!=output/'manifest.json'}
    if set(files)!=set(manifest['artifact_sha256']):raise ValueError('Pilot artifact coverage differs')
    for relative,path in files.items():
        if path.is_symlink() or native.digest(path)!=manifest['artifact_sha256'][relative]:
            raise ValueError('Pilot artifact changed: '+relative)
    stage_names={c['case_id'] for c in request['cases']}|{'linear-controls'}
    if request['execution_options']['include_rc']:stage_names.add('prerelease-interchange')
    if set(manifest['stages'])!=stage_names:raise ValueError('Pilot stage coverage differs')
    for name,stage in manifest['stages'].items():
        if stage!=json.loads((output/name/'stage.json').read_bytes()):raise ValueError('Pilot stage receipt differs: '+name)
        if any(stage.get(k) is not False for k in FLAGS):raise ValueError('Stage cannot grant acceptance')
    # Recompute native CAD diagnostics instead of trusting a stored pass boolean.
    for case in request['cases']:
        if manifest['stages'][case['case_id']]['status']!='completed':continue
        folder=output/case['case_id']
        stage=manifest['stages'][case['case_id']]['result']
        if any(stage.get(k)!=case[k] for k in ('candidate_id','component_geometry_id','case_id')):
            raise ValueError('Mixed pilot candidate or component identity')
        if json.loads((folder/'case.json').read_bytes())!=case:raise ValueError('Stored physical case differs')
        generated=solidcraft.parse_measurements(json.loads((folder/'generate/results.json').read_bytes()))
        expected=stage['checks']['generated']
        if compare_geometry(case,generated,policy=request['policy']['comparison'])!=expected:
            raise ValueError('Recomputed CAD comparison differs')
        for ext in ('sc','step'):
            measured=solidcraft.parse_measurements(json.loads((folder/('reopen-'+ext)/'measure.json').read_bytes()))
            if compare_geometry(case,measured,policy=request['policy']['comparison'])!=stage['checks']['reopen_'+ext]:
                raise ValueError('Reopened CAD comparison differs')
        reference=json.loads((folder/'freecad-reference/result.json').read_bytes())
        associated=associate_exact(case,reference,request['policy']['comparison'])
        if associated!=json.loads((folder/'independent-correspondence.json').read_bytes()):raise ValueError('STEP correspondence differs')
        exact=compare_geometry(case,associated,exact=True,policy=request['policy']['comparison'])
        exact['native_names_preserved']=associated['native_names_preserved']
        if exact!=stage['checks']['exact_step']:raise ValueError('Exact STEP comparison differs')
        raw=[json.loads(line) for line in (folder/'fieldcraft-interchange/native/stdout.jsonl').read_text().splitlines() if line.strip()]
        decoded=decode_interchange(raw,case)
        if decoded!=stage['fieldcraft_interchange'] or decoded['readback']!=json.loads((folder/'fieldcraft-interchange/readback.json').read_bytes()):
            raise ValueError('Recomputed native interchange readback differs')
        if all(c['comparison_passed'] for c in stage['checks'].values())!=stage['geometry_comparison_passed']:
            raise ValueError('Recomputed geometry aggregate differs')
    from . import handoff
    if json.loads((output/'delivery-handoffs.json').read_bytes())!=[handoff.build(c,root) for c in request['cases']]:
        raise ValueError('Recomputed same-candidate delivery handoff differs')
    if manifest['stages']['linear-controls']['status']=='completed':
        folder=output/'linear-controls'
        def replies(path):return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        count=len(fieldcraft.cantilever_commands());fine_count=len(fieldcraft.remesh_cantilever_commands())
        rows=fieldcraft.batch_results(_reply(replies(folder/'bending/stdout.jsonl')),count+fine_count)
        def packet(part):return dict(ok=True,failed=None,completed=len(part),results=part)
        c=fieldcraft.parse_cantilever_result(packet(rows[:count]),count)
        f=fieldcraft.parse_cantilever_result(packet(rows[count:]),fine_count)
        a=fieldcraft.parse_axial_result(_reply(replies(folder/'axial/stdout.jsonl')),len(fieldcraft.axial_commands()))
        from . import calculix_reference
        reference=json.loads((folder/'calculix-reference/result.json').read_bytes())
        for name,row in reference['cases'].items():
            base=folder/'calculix-reference'/name
            definition=json.loads((base/'definition.json').read_bytes())
            if calculix_reference.parse_dat((base/'control.dat').read_text(),definition)!=row['comparison']:
                raise ValueError('Recomputed independent solver readback differs')
        if compare_controls(c,f,a,reference,request)!=manifest['stages']['linear-controls']['result']:
            raise ValueError('Recomputed numerical control comparison differs')
    if software_screen(manifest['stages'],request)!=manifest['software_pilot_passed']:
        raise ValueError('Pilot aggregate screen differs')
    return dict(result_id=manifest['result_id'],evaluation_id=manifest['evaluation_id'],
                integrity_verified=True,software_pilot_passed=manifest['software_pilot_passed'],
                stages=manifest['stages'],fresh_solve=False,**FLAGS)
