"""Execute or import a bounded, same-candidate CAD/CAE/delivery comparison."""
from copy import deepcopy
from pathlib import Path
import json,platform,shutil,sys,time

from engineering.station_rail.common import identity,digest
from engineering.design_search import quality_diversity
from . import native,viaduct_cases,viaduct_cad,viaduct_admission,viaduct_delivery,viaduct_replay,backend_api
from .cases import FLAGS

ROOT=Path(__file__).resolve().parents[3]
PRODUCER='engineering/design_search/craft_backends/viaduct_workflow.py'
FINALISTS=('reference_box--reference','folded_plate--reference')
LIMITS=dict(maximum_cases=12,maximum_native_invocations=48,maximum_active_native_workers=1,
    ordinary_native_address_space_mib=2048,optional_fine_memory_revision_mib=3072,
    timeout_s_per_native_invocation=120,aggregate_memory_cgroup_enforced=False,
    CPU_affinity_enforced=False,thread_environment_limits_requested=True)


def runtime_observation():
    import gmsh
    paths=dict(python=Path(sys.executable).resolve(),calculix=Path(shutil.which('ccx')).resolve(),
        gmsh_python=Path(gmsh.__file__).resolve(),gmsh_library=Path(gmsh.libpath).resolve())
    return dict(python=platform.python_version(),gmsh=gmsh.__version__,
        artifacts={k:dict(path=str(p),sha256=digest(p)) for k,p in paths.items()},
        requested_thread_environment={'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','RAYON_NUM_THREADS':'1'},
        CPU_affinity_enforced=False,observation_is_authenticated_physical_evidence=False)


def plan(*,root=ROOT,verification_python=None):
    from . import viaduct_fem
    context=viaduct_delivery.prepare(root);cases=viaduct_cases.portfolio(root=root)
    names=(PRODUCER,'engineering/design_search/craft_backends/backend_api.py',
        'engineering/design_search/craft_backends/viaduct_admission.py',
        'engineering/design_search/craft_backends/viaduct_delivery.py',
        'engineering/design_search/craft_backends/viaduct_fem_resource.py',
        'engineering/design_search/craft_backends/viaduct_replay.py')
    sources={**context['source_sha256'],**viaduct_cad.sources(root),**viaduct_fem.sources(root),
        **{n:digest(Path(root)/n) for n in names}}
    value=dict(schema='osr-viaduct-backend-workflow-request/1',cases=cases,
        numerical_finalists=list(FINALISTS),numerical_finalist_purpose='Predeclared method comparisons across two geometries; not a winning railway selection',
        registry=backend_api.registry(),source_sha256=sources,delivery_context_id=context['context_id'],
        runtime=runtime_observation(),numerical_replay_runtime=viaduct_replay.invoke(python=verification_python,root=root)['runtime'],
        limits=deepcopy(LIMITS),
        selected_baseline_control=dict(included_in_this_native_cohort=False,
            nominal_selected_stock_kg=55704.,portfolio_box_stock_kg=54720.,
            difference='Selected beam has two end diaphragms and a different world-frame vertical origin; no inherited baseline result'),
        **FLAGS)
    value['request_id']=identity(value);return value


def _unreleased(value):
    viaduct_admission._unreleased(value)


def numerical_summary(result,folder):
    """Recompute numerical claims, keeping missing calculations unknown."""
    folder=Path(folder);_unreleased(result)
    request=json.loads((folder/'request.json').read_bytes())
    if result['evaluation_id']!=request['evaluation_id'] or set(result['levels'])!={'coarse','fine'}:
        raise ValueError('Numerical evaluation identity or mesh-level coverage differs')
    levels={}
    for level,row in result.get('levels',{}).items():
        outputs=row.get('results',{});field=outputs.get('fieldcraft');reference=outputs.get('calculix')
        both=field is not None and reference is not None
        delta=None
        if both:
            a,b=field['displacement_m'][2],reference['displacement_m'][2]
            delta=abs(a-b)/max(abs(b),1e-30)
            if outputs.get('cross_solver_displacement_relative_difference')!=delta or outputs.get('cross_solver_screen_passed') is not (delta<=.02):
                raise ValueError('Derived cross-solver summary differs')
        mesh_path=folder/('mesh-'+level)/'mesh.json'
        if mesh_path.exists() and 'mesh_id' in row:
            model=json.loads(mesh_path.read_bytes())
            if row['mesh_id']!=model['mesh_id'] or row['node_count']!=len(model['nodes']) or row['element_count']!=len(model['elements']) or row['min_scaled_jacobian']!=model['min_scaled_jacobian']:
                raise ValueError('Derived mesh summary differs')
        passed=both and delta<=.02 and all(value.get('force_equilibrium_passed') is True and value.get('moment_equilibrium_passed') is True for value in (field,reference))
        levels[level]=dict(execution='dual-solver-completed' if both else 'partial-or-held',
            fieldcraft_midspan_uz_m=None if field is None else field['displacement_m'][2],
            calculix_midspan_uz_m=None if reference is None else reference['displacement_m'][2],
            cross_solver_relative_difference=delta,numerical_screen_passed=passed,
            node_count=row.get('node_count'),element_count=row.get('element_count'),
            jacobian_diagnostic=row.get('min_scaled_jacobian'),
            quality_scope='Positive straight-sided Jacobian check; not a complete aspect-ratio/dihedral quality criterion')
    refinement=None
    if all(levels.get(k,{}).get('fieldcraft_midspan_uz_m') is not None for k in ('coarse','fine')):
        a,b=(levels[k]['fieldcraft_midspan_uz_m'] for k in ('coarse','fine'))
        refinement=abs(a-b)/abs(b)
        if not isinstance(result.get('refinement'),dict) or result['refinement'].get('displacement_relative_change')!=refinement or result['refinement']['screen_passed'] is not (refinement<=.05):
            raise ValueError('Derived refinement summary differs')
    elif result.get('refinement') is not None:raise ValueError('Missing fine solve cannot establish refinement')
    passed=all(levels.get(k,{}).get('numerical_screen_passed') is True for k in ('coarse','fine')) and refinement is not None and refinement<=.05
    return dict(source_result_id=result['result_id'],levels=levels,
        displacement_refinement_relative=refinement,numerical_screen_passed=passed,
        engineering_screen='open; uncracked material, load transfer, reinforcement/prestress and physical bearing behavior unresolved',
        mesh_independence_established=False,physical_accepted=False)


def import_resource(analysis,state,*,root=ROOT,verification_python=None):
    from . import viaduct_fem_resource
    state=Path(state).resolve();original=Path(analysis['source_path']).resolve()
    spec=json.loads((original/'input.json').read_bytes())
    verification=viaduct_replay.invoke('resource',state,python=verification_python,root=root)
    request=json.loads((state/'request.json').read_bytes());result=json.loads((state/'result.json').read_bytes())
    _unreleased(request);_unreleased(result)
    if Path(request['original_case_run']).resolve()!=original or request['original_result_id']!=analysis['summary']['source_result_id']:
        raise ValueError('Resource revision refers to a different numerical comparison')
    execution=json.loads((state/'fieldcraft/execution.json').read_bytes())
    if execution!=result['execution']:raise ValueError('Duplicated resource execution metadata differs')
    original_result=json.loads((original/'result.json').read_bytes())
    summary=deepcopy(analysis['summary']);summary['original_numerical_screen_passed']=summary['numerical_screen_passed']
    effective=False
    if result['state']=='numerical-comparison-completed':
        field=result['fieldcraft'];coarse=original_result['levels']['coarse']['results']['fieldcraft'];ccx=original_result['levels']['fine']['results']['calculix']
        expected=viaduct_fem_resource.comparisons(field,coarse,ccx)
        if result['comparisons']!=expected:raise ValueError('Resource comparison summary differs')
        effective=(expected['cross_solver_screen_passed'] and expected['displacement_refinement_screen_passed']
            and field['force_equilibrium_passed'] and field['moment_equilibrium_passed']
            and analysis['summary']['levels']['coarse']['numerical_screen_passed'])
        summary['effective_fine_midspan_uz_m']=field['displacement_m'][2]
        summary['effective_refinement_relative']=expected['displacement_refinement_relative_change']
    summary['resource_comparison']=dict(source_path=str(state),evaluation_id=result['evaluation_id'],result_id=result['result_id'],
        resources=request['resources'],verification=verification,state=result['state'],
        numerical_screen_passed=effective,original_failed_evaluation_preserved=True)
    summary['numerical_screen_passed']=effective
    value=deepcopy(analysis);value['summary']=summary
    value['resource_evaluation_id']=result['evaluation_id']
    return value


def import_analysis(case,cad_state,state,*,root=ROOT,verification_python=None):
    from . import viaduct_fem
    state=Path(state).resolve();spec=json.loads((state/'input.json').read_bytes())
    artifact=backend_api.CivilCAD().export(case,cad_state,root=root)
    old=spec['cad_artifact']
    for k in ('candidate_id','component_geometry_id','step_sha256'):
        if old.get(k)!=artifact[k]:raise ValueError('Analysis does not use verified CAD '+k)
    if Path(old['step_path']).resolve()!=Path(artifact['step_path']).resolve():
        raise ValueError('Analysis CAD path/context differs')
    expected=viaduct_fem.prepare(case,old,spec['load_case']['name'],root=root)
    if spec!=expected:raise ValueError('Analysis physical, material, source or load assumptions differ')
    verification=viaduct_replay.invoke('analysis',state,python=verification_python,root=root)
    result=json.loads((state/'result.json').read_bytes())
    summary=numerical_summary(result,state)
    return dict(source_path=str(state),input_id=spec['input_id'],evaluation_id=result['evaluation_id'],
        verification=verification,summary=summary,**FLAGS)


def _row(case,delivery,cad,analysis):
    base=delivery['cost']['cases']['base']
    value=dict(case_id=case['case_id'],candidate_id=case['candidate_id'],component_geometry_id=case['component_geometry_id'],
        family=case['family'],profile=case['profile'],cad_evaluation_id=cad['evaluation_id'],
        outline_geometry_complete=cad['exact_step']['comparison_passed'],
        nominal_stock_mass_kg=case['canonical_quantities']['total_nominal_stock_mass_kg'],
        structural_factory_base_iqd=base['factory_gate_iqd'],scoped_installed_base_iqd=base['scoped_installed_iqd'],
        delivery_evaluation_id=delivery['delivery_evaluation_id'],
        numerical_evaluation_id=None if analysis is None else analysis['evaluation_id'],
        numerical_summary=None if analysis is None else analysis['summary'],
        pending_tasks=['Resolve actual bearing/contact and support compliance before structural selection',
            'Detail reinforcement/prestress, lifting and load/rail interfaces',
            'Replace dated cost proxies with scoped current sourcing evidence'],
        selection_purpose='Next research experiment only',**FLAGS)
    value['row_id']=identity(value);return value


def outline_archive(rows):
    objectives=('nominal_stock_mass_kg','structural_factory_base_iqd')
    pool=[dict(candidate_id=r['candidate_id'],descriptor=dict(family=r['family']),metrics={k:r[k] for k in objectives}) for r in rows]
    return quality_diversity.archive(pool,objectives,('family',))


def verify_process_counts(value,output,cad_manifest):
    output=Path(output).resolve()
    fresh=sum(1 for _ in output.rglob('execution.json'))
    imported=cad_manifest['native_processes'] if not Path(value['cad_source_path']).resolve().is_relative_to(output) else 0
    if value['fresh_native_invocations']!=fresh or value['imported_CAD_native_invocations']!=imported or fresh>LIMITS['maximum_native_invocations']:
        raise ValueError('Workflow native execution accounting differs')


def run(output,*,cad_state=None,analysis_states=(),resource_states=(),execute=False,root=ROOT,verification_python=None):
    from . import viaduct_fem
    output=Path(output).resolve();root=Path(root).resolve()
    if output.exists():raise ValueError('Fresh immutable workflow output required')
    request=plan(root=root,verification_python=verification_python);output.mkdir(parents=True,mode=0o700);native.write(output/'request.json',request)
    context=viaduct_delivery.prepare(root);started=time.monotonic()
    if cad_state is None:
        if not execute:raise ValueError('Supply verified CAD evidence or explicitly execute native workers')
        cad_state=output/'cad';viaduct_cad.generate_portfolio(request['cases'],cad_state,root=root)
    cad_state=Path(cad_state).resolve();admission=viaduct_admission.verify(cad_state,root=root)
    raw_cad=json.loads((cad_state/'manifest.json').read_bytes())
    if set(raw_cad['cases'])!={c['case_id'] for c in request['cases']}:
        raise ValueError('Complete twelve-case CAD cohort required')
    by_candidate={c['candidate_id']:c for c in request['cases']};analyses={}
    for state in analysis_states:
        spec=json.loads((Path(state)/'input.json').read_bytes());case=by_candidate.get(spec['candidate_id'])
        if case is None or case['case_id'] not in FINALISTS or case['case_id'] in analyses:
            raise ValueError('Unique predeclared numerical finalists required')
        analyses[case['case_id']]=import_analysis(case,cad_state,state,root=root,verification_python=verification_python)
    if execute:
        for case in request['cases']:
            if case['case_id'] not in FINALISTS or case['case_id'] in analyses:continue
            spec=backend_api.CivilAnalysis().prepare(case,cad_state,root=root)
            state=output/'analysis'/case['case_id'];viaduct_fem.run(spec,state)
            analyses[case['case_id']]=import_analysis(case,cad_state,state,root=root,verification_python=verification_python)
            fine=json.loads((state/'result.json').read_bytes())['levels'].get('fine',{}).get('results',{})
            if 'fieldcraft' not in fine and 'calculix' in fine:
                stderr=state/'solve-fine/fieldcraft/stderr.log'
                text=stderr.read_text(errors='replace').lower() if stderr.exists() else ''
                if 'memory' in text or 'alloc' in text:
                    from . import viaduct_fem_resource
                    resource=output/'resource'/case['case_id']
                    viaduct_fem_resource.revisionrun(spec,state,resource)
                    analyses[case['case_id']]=import_resource(analyses[case['case_id']],resource,root=root,verification_python=verification_python)
    for state in resource_states:
        record=json.loads((Path(state)/'request.json').read_bytes());case=by_candidate.get(record['candidate_id'])
        if case is None or case['case_id'] not in analyses or 'resource_evaluation_id' in analyses[case['case_id']]:
            raise ValueError('Unique resource revision with an original numerical comparison required')
        analyses[case['case_id']]=import_resource(analyses[case['case_id']],state,root=root,verification_python=verification_python)
    rows=[]
    for case in request['cases']:
        delivery=viaduct_delivery.build(case['physical_definition'],context,root=root)
        native.write(output/'delivery'/(case['case_id']+'.json'),delivery)
        rows.append(_row(case,delivery,raw_cad['cases'][case['case_id']],analyses.get(case['case_id'])))
    archive=outline_archive(rows)
    if plan(root=root,verification_python=verification_python)!=request:raise ValueError('Workflow source or runtime changed during execution')
    fresh=sum(1 for _ in output.rglob('execution.json'))
    if fresh>LIMITS['maximum_native_invocations']:raise ValueError('Native workflow invocation budget exceeded')
    value=dict(schema='osr-viaduct-backend-workflow/1',request_id=request['request_id'],
        source_sha256=request['source_sha256'],cad_source_path=str(cad_state),cad_result_id=raw_cad['result_id'],
        independent_cad_verification=admission,rows=rows,analyses=analyses,outline_archive=archive,
        archive_scope='Nominal mass and dated structural factory cost only; no unknown numerical performance receives a zero objective',
        complete_calculated_geometry_outlines=sum(r['outline_geometry_complete'] is True for r in rows),fresh_native_invocations=fresh,
        imported_CAD_native_invocations=raw_cad['native_processes'] if not cad_state.is_relative_to(output) else 0,
        elapsed_s=time.monotonic()-started,integrated_selection=None,default_backends_changed=False,
        native_reuse_scope='Imported immutable evidence is explicitly distinguished from fresh solves; historical Gmsh binary pre-pin is not established by a later runtime observation',
        **FLAGS)
    value['result_id']=identity(value);native.write(output/'result.json',value)
    manifest=dict(schema='osr-viaduct-backend-workflow-manifest/1',request_id=request['request_id'],result_id=value['result_id'],
        files_sha256={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file()},**FLAGS)
    manifest['manifest_id']=identity(manifest);native.write(output/'manifest.json',manifest)
    return value


def verify(output,*,root=ROOT):
    output=Path(output).resolve();m=json.loads((output/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Workflow manifest seal differs')
    files={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file() and p!=output/'manifest.json'}
    if files!=m['files_sha256']:raise ValueError('Workflow artifact coverage differs')
    request=json.loads((output/'request.json').read_bytes());value=json.loads((output/'result.json').read_bytes())
    verification_python=request['numerical_replay_runtime']['interpreter_entrypoint']
    _unreleased(request);_unreleased(value);_unreleased(m)
    if request!=plan(root=root,verification_python=verification_python) or request['request_id']!=m['request_id'] or value['request_id']!=request['request_id']:
        raise ValueError('Workflow source, request or runtime context differs')
    if value['result_id']!=identity({k:v for k,v in value.items() if k!='result_id'}) or value['result_id']!=m['result_id']:
        raise ValueError('Workflow result seal differs')
    admission=viaduct_admission.verify(value['cad_source_path'],root=root)
    if admission!=value['independent_cad_verification']:raise ValueError('CAD independent verification differs')
    context=viaduct_delivery.prepare(root)
    raw_cad=json.loads((Path(value['cad_source_path'])/'manifest.json').read_bytes())
    if value['cad_result_id']!=raw_cad['result_id'] or value['source_sha256']!=request['source_sha256']:
        raise ValueError('Workflow evidence/source provenance differs')
    verify_process_counts(value,output,raw_cad)
    if set(value['analyses'])-set(FINALISTS):raise ValueError('Undeclared numerical finalist')
    expected=[]
    for case in request['cases']:
        delivery=viaduct_delivery.build(case['physical_definition'],context,root=root)
        if delivery!=json.loads((output/'delivery'/(case['case_id']+'.json')).read_bytes()):raise ValueError('Same-candidate delivery differs')
        analysis=value['analyses'].get(case['case_id'])
        if analysis is not None:
            reproduced=import_analysis(case,value['cad_source_path'],analysis['source_path'],root=root,verification_python=verification_python)
            if 'resource_evaluation_id' in analysis:
                reproduced=import_resource(reproduced,analysis['summary']['resource_comparison']['source_path'],root=root,verification_python=verification_python)
            if analysis!=reproduced:raise ValueError('Native numerical evidence differs')
        expected.append(_row(case,delivery,raw_cad['cases'][case['case_id']],analysis))
    if expected!=value['rows']:raise ValueError('Compared candidate rows differ')
    if value['outline_archive']!=outline_archive(expected) or value['complete_calculated_geometry_outlines']!=sum(r['outline_geometry_complete'] is True for r in expected):
        raise ValueError('Derived outline archive or coverage differs')
    if value['integrated_selection'] is not None or value['default_backends_changed'] is not False:
        raise ValueError('Research comparison cannot select the integrated baseline')
    return dict(verified=True,fresh_native_solve=False,result_id=value['result_id'],manifest_id=m['manifest_id'],**FLAGS)
