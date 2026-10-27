"""Execute grammar, interface, diagnosis, rewrite, native and assembly stages."""
from pathlib import Path
from hashlib import sha256
import json,time
from importlib.metadata import version,PackageNotFoundError
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity,digest
from . import design_grammar as g,grammar_structure as structure,grammar_geometry as geometry
from . import interface_graph,dfma,material_database,failure_diagnosis,redesign_engine,grammar_coupling

PRODUCER='engineering/design_search/generative_campaign.py'
FLAGS=g.FLAGS


def specification():
    return dict(schema='osr-generative-structural-competition/1',native_jobs_per_invocation=6,CAD_jobs_per_invocation=6,
        wall_time_seconds=1800,native_job_timeout_seconds=45,CAD_job_timeout_seconds=180,
        demonstration='Five composable structural recipes; real mechanism diagnosis, topology/layout/function rewrites',
        native_scope=structure.SCOPE,integrated_acceptance=False,**FLAGS)


def sources():
    names=['remit','design_grammar','grammar_structure','grammar_geometry','interface_graph','dfma','material_database','failure_diagnosis','redesign_engine','grammar_coupling','generative_campaign']
    return {'engineering/design_search/'+n+'.py':digest(ROOT/'engineering/design_search'/ (n+'.py')) for n in names}


def _native(folder,graph,subdivisions):
    folder=Path(folder)
    if folder.exists():
        m=json.loads((folder/'manifest.json').read_bytes());r=json.loads((folder/'result.json').read_bytes())
        if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Native receipt differs')
        if m['files_sha256']!={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p.name!='manifest.json'}:raise ValueError('Native payload differs')
        if r['input_graph_id']!=identity(graph) or r['subdivisions']!=subdivisions or any(digest(ROOT/n)!=h for n,h in r['source_sha256'].items()):raise ValueError('Native source/graph/settings mismatch')
        return r
    return structure.run(graph,folder,subdivisions=subdivisions)


def evaluate(candidate):
    g.validate(candidate);projection=geometry.interface_projection(candidate)
    return dict(candidate_id=candidate['candidate_id'],interfaces=interface_graph.assess(projection),rigidity=structure.diagnose_rigidity(candidate['structure']),
        stock_mass_properties=geometry.mass_properties(candidate),DFMA=dfma.evaluate(candidate),coupled_accounts=grammar_coupling.evaluate(candidate),
        full_body_numerical_evaluator='not available for these new shell/frame/laminate topologies',integrated_suitability='unknown',**FLAGS)


def method_admission(root=ROOT):
    """Numerical method eligibility is scoped to these axial fixtures only."""
    plan=structure.benchmark_plan();base=Path(root)/'build/generative-design/native-benchmarks-r2';rows=[]
    for job in plan['native_jobs']:rows.append(_native(base/job['id'],job['graph'],job['subdivisions']))
    if any(r.get('numerical_validity')!='verified_axial_method' for r in rows):raise ValueError('Current independent axial method fixtures have not passed')
    axial=rows[0];tripod=rows[2];expected=plan['analytical_checks']
    if abs(axial['displacements_m']['tip'][0]-expected['axial_tip_x_m'])>abs(expected['axial_tip_x_m'])*1e-4 or abs(tripod['displacements_m']['3'][2]-expected['tripod_tip_z_m'])>abs(expected['tripod_tip_z_m'])*1e-4:raise ValueError('Independent closed-form method reference differs')
    return dict(status='benchmarked-numerical-axial-method-only',source_sha256={structure.PRODUCER:digest(root/structure.PRODUCER)},evaluation_ids=[r['evaluation_id'] for r in rows],
        scope=structure.SCOPE,physical_material_or_joint_validation=False,full_body_model_admitted=False,**FLAGS)


def run(*,root=ROOT,native=True,cad=True):
    root=Path(root);epoch=sources();spec=specification();contract=identity(dict(sources=epoch,specification=spec,native=native,cad=cad));folder=root/'build/generative-design/campaigns'/contract;folder.mkdir(parents=True,exist_ok=True)
    started=time.monotonic();candidates=g.initial_candidates();evaluations=[];native_results=[];cad_results=[];rewrites=[]
    def event(stage,**data):
        if time.monotonic()-started>spec['wall_time_seconds']:raise TimeoutError('Campaign invocation budget exhausted; immutable completed packets remain resumable')
        with (folder/'journal.jsonl').open('a') as stream:stream.write(json.dumps(dict(stage=stage,**data),sort_keys=True)+'\n')
    event('started',contract_id=contract)
    for c in candidates:evaluations.append(evaluate(c))
    initial=candidates[0];diagnosis=failure_diagnosis.diagnose(initial,rigidity=evaluations[0]['rigidity'],interfaces=evaluations[0]['interfaces']);revision=redesign_engine.revise(initial,diagnosis)
    for row in revision['revisions']:
        c=row['candidate'];candidates.append(c);evaluations.append(evaluate(c));rewrites.append(dict(operator=row['operator'],parent_id=initial['candidate_id'],candidate_id=c['candidate_id'],trigger_diagnosis_id=diagnosis['diagnosis_id']))
    repaired=next(c for c in candidates if c['parameters']['braced'])
    admission=method_admission(root) if native else None
    if native:
        initial_result=_native(folder/'native'/'mechanism-control',initial['structure'],1);native_results.append(initial_result)
        for n in (1,2):
            event('native',candidate_id=repaired['candidate_id'],subdivisions=n)
            native_results.append(_native(folder/'native'/('rewritten-s'+str(n)),repaired['structure'],n))
    # CAD for each initial family and the actual changed structural topology.
    # These are gross stock, with unknown joint cuts/hardware explicitly held.
    if cad:
        for c in [*candidates[:5],repaired]:
            event('CAD',candidate_id=c['candidate_id'])
            dest=folder/'cad'/c['candidate_id']
            r=geometry.read_export(c,dest) if (dest/'manifest.json').is_file() else geometry.export(c,dest)
            cad_results.append(r)
    roof_child=next(c for c in candidates if c['parameters']['integrated_roof'])
    integration=dict(interfaces=interface_graph.compare_integration(geometry.interface_projection(initial),geometry.interface_projection(roof_child)),
        DFMA=dfma.compare(initial,roof_child))
    if epoch!=sources():raise ValueError('Generative sources changed during execution')
    def installed(name):
        try:return version(name)
        except PackageNotFoundError:return None
    result=dict(schema='osr-executed-generative-design/1',contract_id=contract,specification=spec,source_sha256=epoch,candidates=candidates,evaluations=evaluations,
        diagnosis=diagnosis,executed_rewrites=rewrites,model_development_tasks=revision['model_and_measurement_tasks'],method_admission=admission,native_results=native_results,CAD_results=cad_results,
        integration_comparison=integration,material_search=material_database.search(dict(function='structural-core',operating_temperature_C=80.,require_hot_wet=True)),
        tool_strategy=dict(pymoo=dict(installed=installed('pymoo'),executed=False),OpenMDAO=dict(installed=installed('openmdao'),executed=False,reason='No invented feedback laws'),build123d=dict(installed=installed('build123d'),executed=False,reason='Native FreeCAD reused'),Dakota=dict(installed=installed('dakota'),executed=False)),
        partial_quantity_Pareto_scope='Known gross stock and manufactured occurrence counts only; no integrated feasibility or cost ranking',
        integrated_selection=None,selected_reference_changed=False,city_packages_regenerated=0,**FLAGS)
    event('completed',candidates=len(candidates),native_records=len(native_results),CAD_records=len(cad_results))
    result['campaign_id']=identity(result);target=folder/'result.json'
    if target.exists() and target.read_bytes()!=encoded(result):raise ValueError('Existing immutable campaign differs')
    target.write_bytes(encoded(result));return result
