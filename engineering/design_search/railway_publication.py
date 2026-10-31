"""Portable comparison of one coordinated railway experiment and its holds."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from math import isfinite
import gzip,json,shutil,tarfile,io
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity,digest
from . import railway_campaign as engine,design_grammar,railway_bundle,grammar_shell,transient_lim,railway_delivery
from .generative_publication import archive

PRODUCER='engineering/design_search/railway_publication.py'
OUTPUT='docs/design-engine/coupled-railway'
FLAGS=engine.FLAGS


def compact_native_archive(folder):
    """Keep exact solver decks/logs; index duplicate large node/body metadata."""
    buf=io.BytesIO();kept={};omitted={}
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for p in sorted(Path(folder).rglob('*')):
            if p.is_symlink():raise ValueError('Ordinary native evidence files required')
            if not p.is_file() or '__pycache__' in p.parts:continue
            name=p.relative_to(folder).as_posix();h=digest(p)
            if p.suffix.lower() in ('.dat','.frd','.12d','.step','.fcstd','.fcstd1') or p.name in ('candidate.json','definition.json','worker-result.json') and p.stat().st_size>1_000_000:
                omitted[name]=h;continue
            raw=p.read_bytes();kept[name]=h;t=tarfile.TarInfo(name);t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
        raw=encoded(dict(retained_sha256=kept,omitted_sha256=omitted,storage='Exact FEM decks/results/logs retained; large fields and duplicate node/body metadata remain local or regenerate from exact source/body/request. Full raw-payload hashes preserved.'))
        t=tarfile.TarInfo('archive-index.json');t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
    return gzip.compress(buf.getvalue(),mtime=0)


def current(root=ROOT):
    root=Path(root);epoch=engine.source_epoch(root);spec=engine.specification(root);contract=identity(dict(specification=spec,source_sha256=epoch))
    folder=root/'build/coupled-railway'/contract;value=json.loads((folder/'result.json').read_bytes())
    if value['contract_id']!=contract or value['source_sha256']!=epoch or value['campaign_id']!=engine.semantic_id(value):raise ValueError('Source-matched coordinated execution required')
    if value['run_id']!=identity({k:v for k,v in value.items() if k!='run_id'}):raise ValueError('Invocation receipt differs')
    if len(value['rows'])!=len(value['bundles']):raise ValueError('Finish the pending bundle evaluation queue before publishing the complete comparison')
    return folder,value


def _body_response(native,body_id):
    cases=[r for r in native['body_results'] if r['body_candidate_id']==body_id]
    normal=next((r['raw'] for r in cases if r['case']=='normal'),{})
    fine=next((r['raw'] for r in cases if r['case']=='normal-fine'),{})
    refined=next((r['raw'] for r in cases if r['case']=='normal-refined'),{})
    a=normal.get('maximum_displacements',{}).get('vertical_m');b=fine.get('maximum_displacements',{}).get('vertical_m');extra=refined.get('maximum_displacements',{}).get('vertical_m')
    before,last=(b,extra) if extra is not None else (a,b)
    change=None if before is None or last is None else abs(before-last)/max(abs(last),1e-30)
    valid=all(r['raw'].get('numerical_validity')=='equilibrium_energy_confirmed_only' for r in cases) and len(cases)>=3
    hold=native['body_admission'].get(body_id,{}).get('computational_hold')
    return dict(native_cases=len(cases),normal_vertical_m=a,fine_vertical_m=b,extra_refined_vertical_m=extra,relative_vertical_refinement_change=change,
        mesh_levels=[dict(case=r['case'],mesh_m=r['mesh_m'],evaluation_id=r['evaluation_id'],maximum_displacements=r['raw'].get('maximum_displacements')) for r in cases],
        numerical_status='equilibrium/energy checked; maxima refinement reported' if valid else 'unconfirmed' if cases else 'computational resource hold' if hold else 'full-body model not admitted',
        engineering_screen='unknown',full_body_qualified=False)


def _cost_simulation_completion(row):
    """Audit the declared cost simulation without promoting physical evidence."""
    estimate=row.get('economics',{}).get('model_cost',{})
    candidate_id=row['candidate_id']
    required=set(engine.model_cost.SCOPES)
    totals=estimate.get('scope_totals_iqd',{})
    lines=estimate.get('cost_line_items',[])
    assumptions_id=estimate.get('assumption_id')
    complete=(estimate.get('candidate_id')==candidate_id
        and estimate.get('model_cost_complete_for_declared_case') is True
        and estimate.get('model_cost_missing_scopes')==[]
        and set(estimate.get('required_cost_scopes',[]))==required
        and set(totals)==required
        and all(isinstance(totals.get(scope),list) and len(totals[scope])==3
                and all(isinstance(x,(int,float)) and isfinite(x) and x>=0 for x in totals[scope])
                and totals[scope][0]<=totals[scope][1]<=totals[scope][2] and totals[scope][1]>0
                for scope in required)
        and bool(assumptions_id) and bool(estimate.get('source_sha256'))
        and bool(lines) and all(line.get('candidate_id')==candidate_id
            and line.get('scope') in required and line.get('source_ids')
            and isinstance(line.get('calculation_basis'),str) and line['calculation_basis'].strip()
            and set(line.get('scenario_iqd',{}))=={'low','base','high'}
            and all(isinstance(x,(int,float)) and isfinite(x) and x>=0
                    for x in line.get('scenario_iqd',{}).values())
            for line in lines)
        and {line.get('scope') for line in lines}==required)
    return dict(candidate_id=candidate_id,
        simulation_complete=complete,
        simulation_scope='Candidate-bound Class C manufacturing, delivery, civil and lifecycle cost scenario; 14 declared cost scopes.',
        simulation_input_basis='Source-linked quantities and explicitly identified Class C assumptions; supplier quotations are not required for this provisional calculation.',
        assumption_id=assumptions_id,
        integrated_force_driven_journey_complete=row.get('physical_journey_completed') is True,
        engineering_validated=False,
        engineering_validation_state='open',
        engineering_validation_basis='Cost estimates and numerical screens do not supply independently reviewed physical qualification evidence.',
        approved_for_manufacture_or_operation=False,
        approval_state='not-approved',
        approval_basis='Requires completed engineering and safety evidence plus independent release approval.')


def completion_summary(rows):
    records=[_cost_simulation_completion(row) for row in rows]
    return dict(candidate_count=len(records),
        simulation_scope='The simulation-complete flag applies to the declared 14-scope Class C cost scenario only. Integrated force-driven journey simulation is reported separately.',
        simulation_complete=sum(r['simulation_complete'] for r in records),
        integrated_force_driven_journey_complete=sum(r['integrated_force_driven_journey_complete'] for r in records),
        engineering_validated=sum(r['engineering_validated'] for r in records),
        approved_for_manufacture_or_operation=sum(r['approved_for_manufacture_or_operation'] for r in records),
        candidate_states=records)


def _retain_exact_prior_body_cases(root,value,out,native_index):
    """Carry forward prior solves only when their exact physical request matches."""
    root=Path(root);out=Path(out)
    body_by_id={b['candidate_id']:b for b in value['bodies']}
    bundle_by_id={b['candidate_id']:b for b in value['bundles']}
    spec=value['specification'];cases=dict(zip(spec['body_cases'],spec['body_mesh_m']))
    expected={
        'normal':('normal',cases['normal']),
        'normal-fine':('normal',cases['normal-fine']),
        'crowd':('crowd',cases['crowd']),
        'normal-refined':('normal',cases['normal-fine']*spec['numerical_refinement']['factor']),
    }
    seen={r['raw_result']['evaluation_id'] for r in native_index if r.get('kind') in ('body','body-refinement','body-exact-cache-reuse')}
    reused=[];rejections=[]
    previous_root=root/'build/coupled-railway/replaced-publications'
    for publication in sorted(previous_root.glob('*/native-index.json')):
        folder=publication.parent
        try:
            receipt=json.loads((folder/'manifest.json').read_bytes())
            if receipt['manifest_id']!=identity({k:v for k,v in receipt.items() if k!='manifest_id'}):
                raise ValueError('prior publication receipt identity differs')
            indexed=json.loads(publication.read_bytes())
            if receipt['files_sha256'].get('native-index.json')!=digest(publication):
                raise ValueError('prior native index hash differs')
        except (OSError,KeyError,ValueError) as error:
            rejections.append(dict(publication=folder.name,reason=str(error)));continue
        for item in indexed:
            if item.get('kind') not in ('body','body-refinement'):
                continue
            raw_result=item.get('raw_result',{});evaluation_id=raw_result.get('evaluation_id')
            if evaluation_id in seen:
                continue
            try:
                archive_path=folder/item['archive']
                if receipt['files_sha256'].get(item['archive'])!=digest(archive_path):
                    raise ValueError('prior native archive hash differs')
                with tarfile.open(archive_path) as tar:
                    names=set(tar.getnames())
                    if not {'archive-index.json','manifest.json','result.json'}<=names:
                        raise ValueError('prior native archive is incomplete')
                    archive_index=json.loads(tar.extractfile('archive-index.json').read())
                    manifest=json.loads(tar.extractfile('manifest.json').read())
                    result=json.loads(tar.extractfile('result.json').read())
                    if manifest!=item['raw_manifest'] or result!=raw_result:
                        raise ValueError('prior index and archived native records differ')
                    if manifest['manifest_id']!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):
                        raise ValueError('prior native receipt identity differs')
                    if result.get('evaluation_id')!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):
                        raise ValueError('prior native result identity differs')
                    archived_hashes={**archive_index['retained_sha256'],**archive_index['omitted_sha256']}
                    if manifest['files_sha256']!={k:v for k,v in archived_hashes.items() if k!='manifest.json'}:
                        raise ValueError('prior native archive index differs from its receipt')
                    for name,expected_hash in archive_index['retained_sha256'].items():
                        if sha256(tar.extractfile(name).read()).hexdigest()!=expected_hash:
                            raise ValueError('prior archived native payload differs: '+name)
                if manifest.get('source_sha256')!=result.get('source_sha256'):
                    raise ValueError('prior native source receipt differs')
                if any(digest(root/name)!=h for name,h in result['source_sha256'].items()):
                    raise ValueError('prior native physics source is no longer exact')
                tool=result['tool']
                if digest(tool['ccx_path'])!=tool['ccx_sha256']:
                    raise ValueError('prior native solver executable differs')
                if (tool.get('requested_memory_mb')!=spec['maximum_native_memory_mb']
                        or tool.get('timeout_s')!=spec['body_timeout_s']):
                    raise ValueError('prior native resource request differs')
                body_id=result['candidate_id'];body=body_by_id.get(body_id)
                mesh_summary=result['mesh_summary'];basis=mesh_summary['load_basis']
                bundle=bundle_by_id.get(basis.get('bundle_id'))
                if body is None or bundle is None or bundle['body_candidate_id']!=body_id:
                    raise ValueError('prior native physical candidate is not in this campaign')
                if basis.get('bundle_definition_id')!=bundle['definition_id'] or mesh_summary.get('candidate_id')!=body_id:
                    raise ValueError('prior native body/bundle identity differs')
                if basis.get('scope')!=bundle['mass_scope']:
                    raise ValueError('prior native mass scope differs')
                load_case=mesh_summary['load_case'];mesh=float(mesh_summary['mesh_m'])
                if load_case=='crowd':case='crowd'
                elif abs(mesh-cases['normal'])<1e-10:case='normal'
                elif abs(mesh-cases['normal-fine'])<1e-10:case='normal-fine'
                elif abs(mesh-cases['normal-fine']*spec['numerical_refinement']['factor'])<1e-10:case='normal-refined'
                else:raise ValueError('prior native load/mesh pair is outside the current request set')
                if expected[case]!=(load_case,mesh):
                    raise ValueError('prior native case label and requested mesh differ')
                expected_mass=(bundle['crowd_sprung_mass_hypothesis_kg'] if case=='crowd'
                               else bundle['normal_sprung_mass_hypothesis_kg'])
                if abs(mesh_summary['load_mass_kg']-expected_mass)>1e-7:
                    raise ValueError('prior native load mass differs from this exact bundle')
                target=out/item['archive'].replace('native/','native/reused-',1)
                target.parent.mkdir(parents=True,exist_ok=True)
                if target.exists() and digest(target)!=digest(archive_path):
                    raise ValueError('reused native archive target already has different bytes')
                if not target.exists():shutil.copyfile(archive_path,target)
                native_index.append(dict(kind='body-exact-cache-reuse',job_id=item.get('job_id'),archive=target.relative_to(out).as_posix(),
                    source_publication=folder.relative_to(root).as_posix(),source_manifest_id=receipt['manifest_id'],
                    raw_manifest=manifest,raw_result=result,
                    reuse_basis='Exact body candidate, physical definition, bundle/load basis, mesh, solver executable, resource request and native physics source hashes match; no new solve was dispatched.'))
                reused.append(dict(body_candidate_id=body_id,bundle_id=bundle['candidate_id'],case=case,mesh_m=mesh,
                    evaluation_id=evaluation_id,raw=result,exact_prior_reuse=dict(source_manifest_id=receipt['manifest_id'],
                        source_archive=item['archive'],native_job_id=item.get('job_id'))))
                seen.add(evaluation_id)
            except (OSError,KeyError,ValueError,TypeError) as error:
                rejections.append(dict(publication=folder.name,evaluation_id=evaluation_id,reason=str(error)))
    return reused,rejections


def _current_refinement(root, value):
    """Load the exact current-source continuation when its sealed package exists."""
    from . import railway_refinement_current, railway_refinement_current_verifier
    parent = Path(root) / 'build/coupled-railway' / value['contract_id'] / 'result.json'
    context = railway_refinement_current._context(
        root, parent_result=parent, candidate_id=railway_refinement_current.CANDIDATE_ID)
    request = railway_refinement_current._request(context[0], context[2], context[3], context[4],
        context[5], context[6], context[7])
    folder = railway_refinement_current._package(root, request)
    if not folder.exists():
        return None
    verified = railway_refinement_current_verifier.verify(
        root, parent_result=parent, candidate_id=railway_refinement_current.CANDIDATE_ID)
    return dict(folder=folder, request=json.loads((folder/'request.json').read_bytes()),
        result=json.loads((folder/'native/result.json').read_bytes()),
        report=json.loads((folder/'report.json').read_bytes()),
        manifest=json.loads((folder/'manifest.json').read_bytes()), verified=verified)


def _published_frontier(value, refinement):
    tasks=deepcopy(value['frontier'])
    if refinement is None or refinement['result'].get('execution')!='completed':
        return tasks
    report=refinement['report'];body_id=report['body_candidate_id']
    # Keep the original task if the run did not establish numerical validity.
    if refinement['result'].get('numerical_validity')!='equilibrium_energy_confirmed_only':
        for task in tasks:
            if task.get('kind')=='unresolved-numerical-refinement' and task.get('body_candidate_id')==body_id:
                task['state']='completed-run-invalid-or-unconfirmed; diagnosis-required'
                task['completed_evaluation_id']=refinement['result']['evaluation_id']
        return tasks
    tasks=[task for task in tasks if not (task.get('kind')=='unresolved-numerical-refinement' and task.get('body_candidate_id')==body_id)]
    comparison=next((x for x in report['matched_point_displacement_comparisons']
                     if x.get('from_mesh_m')==0.425 and x.get('status')=='compared'),None)
    changes={} if comparison is None else {k:v['maximum_relative_to_fine_component']
        for k,v in comparison.get('components',{}).items()}
    threshold=value['specification']['numerical_refinement']['trigger_relative_change']
    if changes and max(changes.values())>threshold:
        body=next(b for b in value['bodies'] if b['candidate_id']==body_id)
        next_mesh=0.10625
        from . import railway_native
        estimate=railway_native.cell_estimate(body,next_mesh)
        tasks.append(dict(kind='unresolved-numerical-refinement',body_candidate_id=body_id,state='explicit-resource-revision-required',
            evidence_ids=[x['evaluation_id'] for x in report['mesh_and_residual_trend'] if x['mesh_m'] in (0.425,0.2125)],
            component_relative_changes=changes,trigger_relative_change=threshold,proposed_next_mesh_m=next_mesh,
            computational_cell_estimate=estimate,previous_mesh_budget_cells=refinement['request']['computational_cell_budget'],
            next_mesh_exceeds_previous_cell_budget=estimate['solid_cells']>refinement['request']['computational_cell_budget'],
            numerical_run_id=refinement['result']['evaluation_id'],physical_failure_inferred=False,
            required=['Assess a separately bounded 0.10625 m resource request','Compare matched-point displacement and residual trends with this exact current-source result',
                      'Keep stress, joint strength, fatigue, buckling, clearance and physical validation as separate gates']))
    return tasks


def _retain_prior_historical_packets(root, out, value, native, epochs):
    """Carry exact historical evidence forward when local build caches are absent."""
    root=Path(root);out=Path(out);seen={x.get('raw_result',{}).get('evaluation_id') or x.get('raw_result',{}).get('candidate_id') for x in native}
    candidates=[]
    for folder in sorted((root/'build/coupled-railway/replaced-publications').glob('*/')):
        manifest_path=folder/'manifest.json';summary_path=folder/'summary.json'
        if not manifest_path.is_file() or not summary_path.is_file():continue
        try:
            manifest=json.loads(manifest_path.read_bytes());s=json.loads(summary_path.read_bytes())
            actual={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p!=manifest_path}
            if (s.get('campaign_id')==value['campaign_id']
                    and manifest.get('manifest_id')==identity({k:v for k,v in manifest.items() if k!='manifest_id'})
                    and manifest.get('files_sha256')==actual):
                candidates.append((folder,s,manifest))
        except (OSError,KeyError,ValueError,TypeError):
            continue
    if not candidates:return
    # Older source-bound packets are immutable; only unique historical evidence
    # absent from the current build cache is copied into the new receipt.
    for folder,_summary,_manifest in candidates:
        old_epochs=json.loads((folder/'source-epochs.json').read_bytes())
        for item in json.loads((folder/'native-index.json').read_bytes()):
            if item.get('kind') not in ('historical-CAD','historical-resource-or-numerical-failure','transient-method'):
                continue
            result=item.get('raw_result',{});evaluation_id=result.get('evaluation_id') or result.get('candidate_id')
            if evaluation_id in seen:continue
            for name,h in result.get('source_sha256',item.get('raw_manifest',{}).get('source_sha256',{})).items():
                path=root/name
                if (path.is_file() and digest(path)==h) or h in epochs:continue
                source=old_epochs.get(h)
                if source is None:raise ValueError('Prior historical packet lacks its exact source bytes')
                raw=folder/source['artifact']
                if digest(raw)!=h:raise ValueError('Prior historical source archive differs')
                (out/'historical-sources').mkdir(exist_ok=True);target='historical-sources/'+h
                if not (out/target).exists():shutil.copyfile(raw,out/target)
                epochs[h]=dict(repository_path=source.get('repository_path',name),artifact=target)
            suffix=(evaluation_id or identity(item))[:12]
            target=f"native/retained-{item['kind']}-{suffix}.tar.gz"
            if not (out/target).exists():shutil.copyfile(folder/item['archive'],out/target)
            native.append(dict(item,archive=target))
            seen.add(evaluation_id)


def _prior_magnetic_summary(root,value):
    root=Path(root)
    for folder in sorted((root/'build/coupled-railway/replaced-publications').glob('*/')):
        manifest_path=folder/'manifest.json';summary_path=folder/'summary.json';payload=folder/'magnetic-method.json.gz'
        if not (manifest_path.is_file() and summary_path.is_file() and payload.is_file()):continue
        try:
            manifest=json.loads(manifest_path.read_bytes());summary_value=json.loads(summary_path.read_bytes())
            actual={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p!=manifest_path}
            if (summary_value.get('campaign_id')!=value['campaign_id']
                    or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
                    or manifest.get('files_sha256')!=actual):continue
            cases=json.loads(gzip.decompress(payload.read_bytes()))
            if cases:return cases
        except (OSError,KeyError,ValueError,TypeError):
            continue
    return []


def summary(value,magnetic=None,*,reused_body_cases=(),reuse_rejections=(),refinement=None):
    new_native_body_case_count=len(value['native']['body_results'])
    if reused_body_cases:
        value=deepcopy(value)
        value['native']['body_results']=value['native']['body_results']+list(reused_body_cases)
    rows=[]
    for b in value['bodies']:
        cases=[r for r in value['rows'] if r['body_candidate_id']==b['candidate_id']]
        baseline=next((r for r in cases if r['family_id']=='P1'),None);response=_body_response(value['native'],b['candidate_id'])
        rows.append(dict(label=b['label'],body_candidate_id=b['candidate_id'],parent_ids=b['parent_candidate_ids'],
            known_structure_stock_kg=b['known_structure_stock_kg'],accounted_empty_mass_kg=None if baseline is None else baseline['accounted_mass']['accounted_tare_kg_per_car'],
            architecture_cases=len(cases),structural_status=response['numerical_status'],response=response,complete_installed_mass_kg=None))
    magnetic=[] if magnetic is None else magnetic
    model_costs=[r['economics']['model_cost'] for r in value['rows'] if isinstance(r.get('economics',{}).get('model_cost'),dict)]
    completion=completion_summary(value['rows'])
    refinement_count=0 if refinement is None else 1
    result=dict(schema='osr-coupled-railway-summary/1',campaign_id=value['campaign_id'],contract_id=value['contract_id'],body_count=len(rows),
        initial_body_count=value['specification']['initial_structural_recipes'],body_rewrite_count=len(value['executed_body_revisions']),
        bundle_count=len(value['bundles']),evaluated_bundle_count=len(value['rows']),downstream_stage_count=sum(len(r['stages']) for r in value['rows']),
        body_rows=rows,method_fixture_count=len(value['native']['independent_fixtures']),native_body_case_count=len(value['native']['body_results'])+len(reused_body_cases)+refinement_count,
        CAD_case_count=len(value['native']['CAD_results']),magnetic_method_cases=len(magnetic),magnetic_completed=sum(r['result']['execution']=='completed' for r in magnetic),
        native_new_body_case_count=new_native_body_case_count+refinement_count,
        native_campaign_body_case_count=new_native_body_case_count,
        native_current_source_refinement_count=refinement_count,
        current_source_refinement=None if refinement is None else dict(request_id=refinement['manifest']['request_id'],
            evaluation_id=refinement['result']['evaluation_id'],mesh_m=refinement['report']['generated_mesh']['mesh_m'],
            execution=refinement['result'].get('execution'),numerical_validity=refinement['result'].get('numerical_validity'),
            manifest_id=refinement['manifest']['manifest_id'],physical_and_engineering_acceptance=False),
        native_reused_body_case_count=len(reused_body_cases),native_prior_reuse_rejections=list(reuse_rejections),
        model_cost_summary=dict(candidate_estimates=len(model_costs),complete_for_declared_case=sum(r['model_cost_complete_for_declared_case'] is True for r in model_costs),
            currency='IQD',estimate_class='C',required_scope_count=len(engine.model_cost.SCOPES),
            comparison_context_count=len(value.get('model_cost_comparisons',[])),supplier_quotes=0,
            procurement_ready=False,physical_or_safety_accepted=False,integrated_winner=None),
        completion_status=completion,
        actual_force_driven_journeys=0,complete_installed_vehicle_masses=0,complete_lifecycle_costs=0,
        frontier_tasks=len(_published_frontier(value,refinement)),dependency_graph=value['dependency_graph'],selection=value['partial_quantity_comparison'],
        integrated_selection=None,selected_reference_changed=False,city_performance_packages_written=0,**FLAGS)
    return result


def readme(s):
    lines=['# One coordinated railway experiment','',
        'Architecture, adaptive revision planning and physical body generation now share one coordinator, one explicit railway bundle and one dependency graph. A body edit creates new body/railway identities and automatically reevaluates inventory, interfaces, architecture, motor requirements, independent braking, civil loads, manufacture and economic coverage. The earlier campaigns remain reproducible component/historical tools. New coordinated work starts with `./osr design railway`.','',
        f"The executed comparison starts with **{s['initial_body_count']} structural recipes**, makes **{s['body_rewrite_count']} physical revisions**, and evaluates **{s['evaluated_bundle_count']} railway bundles through {s['downstream_stage_count']} downstream stage records**. Two primary-iron alternatives share unchanged onboard fin stock. Seven architecture families retain their own changed interfaces and unweighed equipment. **Class C model-cost estimates cover {s['model_cost_summary']['complete_for_declared_case']} of {s['model_cost_summary']['candidate_estimates']} executed bundles across {s['model_cost_summary']['required_scope_count']} cost scopes. Installed mass, available operating LIM maps, physical journeys, supplier-priced budgets and a qualified whole-life-cost winner remain open.**",'',
        '## Completion levels','',
        f"Each candidate reports three separate completion levels. The declared cost scenario is simulation-complete for **{s['completion_status']['simulation_complete']} of {s['completion_status']['candidate_count']} candidates**, using source-linked quantities and explicit Class C assumptions across 14 scopes. This flag covers that cost scenario only; it does not claim an integrated journey simulation. **{s['completion_status']['integrated_force_driven_journey_complete']}** candidates have a completed force-driven journey, **{s['completion_status']['engineering_validated']}** are engineering-validated, and **{s['completion_status']['approved_for_manufacture_or_operation']}** are approved for manufacture or operation. Engineering validation requires independent physical evidence and review; release requires a separate approval record.",'',
        '## Closed-loop physical and system changes','',
        'The existing adaptive planner diagnoses each declared pin-graph mechanism; the grammar produces a braced physical child instead of changing a pass threshold. A separate assembly-completion operator closes quantified frame/floor/roof gaps using counted metal stock and finite shared-face weld hypotheses. It generates an aluminium frame and an aluminium stressed-skin body, preserving passenger openings and required roof/PV/channel/drain functions. Missing composite laws are not replaced by isotropic GFRP.','',
        '| Body / physical revision | Known structure stock | Empty-mass account | 3D evidence | Architecture cases |',
        '|---|---:|---:|---|---:|']
    for r in s['body_rows']:
        mass='Unknown' if r['accounted_empty_mass_kg'] is None else f"{r['accounted_empty_mass_kg']/1000:.3f} t"
        lines.append(f"| {r['label']} | {r['known_structure_stock_kg']:.1f} kg | {mass} | {r['structural_status']} | {r['architecture_cases']} |")
    lines += ['',
        'These are exact generated nominal/net stock quantities plus retained source accounts. They are not complete vehicle tare or certified lower bounds: original gross-stock overlaps/cuts and missing installed hardware have different boundaries. The new welded children count net disjoint metal, retained covers, PV rails/spacers, trays/gutter/hangers and unknown weld/joint realization separately. Whole installed CG, inertia, clearances, hardware and repair access remain open.','',
        '## Three-dimensional structural method','',
        f"Four independent fixtures check bending/shear refinement, intact finite-face transfer and orthotropic axial/shear constitutive patches. The two new metal bodies have **{s['native_body_case_count']} exact native body cases** across normal, normal-fine and crowd loading: {s['native_new_body_case_count']} dispatched in this coordinated run and {s['native_reused_body_case_count']} carried forward from byte-verified prior publications after matching candidate, load, mesh, solver, resources and source hashes. Reuse is provenance-preserving and does not count as a new solve. C3D8I solids resolve the declared actual metal geometry; no invisible gap ties or arbitrary rigid offsets create the load path. Intact autogenous weld/continuous-face transfer is an unqualified numerical hypothesis.",'',
        '| New solid body | Normal 1.7 m target | Finer 0.85 m | Extra 0.425 m | Last-step change |',
        '|---|---:|---:|---:|---:|']
    for r in s['body_rows']:
        a=r['response']
        if not a['native_cases']:continue
        val=lambda x:'Unknown' if x is None else f'{x*1000:.3f} mm'
        change='Unknown' if a['relative_vertical_refinement_change'] is None else f"{a['relative_vertical_refinement_change']*100:.2f}%"
        lines.append(f"| {r['label']} | {val(a['normal_vertical_m'])} | {val(a['fine_vertical_m'])} | {val(a['extra_refined_vertical_m'])} | {change} |")
    lines += ['',
        'The source-bound resource revision uses 1.7/0.85 m global subdivision targets; thin physical-feature cuts dominate the conformal grid. All actual mesh counts, resources, force/moment/work/energy residuals and failures are retained. A displacement trend is not strength or operating acceptance. C3D8I torsion limitations, quadratic confirmation, local/global buckling, material/HAZ/joint strength, fatigue, modes, thermal/fire/crash behaviour and physical calibration remain necessary work. Equipment loads are currently lumped over the floor with actual structural selfweight; real component positions and suspension compliance are not resolved.','',
        'The first baseline metal-frame job produced 152,004 cells and exceeded its 5 GiB allocation while factoring. It yielded no structural verdict. The generator then standardized and aligned floor/roof extrusion profiles, preserving openings, support pads and actual load paths. These are new physical children with different identities, fewer profile families and roughly 71% fewer conformal cells. The original failed execution, source epoch and CAD remain retained. A 60,000-cell dispatch budget is a computational control, not a railway acceptance rule or proof that the baseline body cannot work.','',
        'The frame\'s first refinement changed the three displacement maxima by about 10-12%. The coordinator therefore requested another unchanged-candidate numerical experiment at a 0.425 m target. Its 61,352-cell estimate justified an explicit computational budget revision to 65,000 cells under the same 5 GiB/150 s limits. Exact unchanged prior solves/CAD are reused across coordinator epochs, with new context records. A 5% refinement trigger requests work; it does not qualify a body. Whole-field, stress, torsion and physical convergence remain separate questions.','',
        (f"The current-source continuation then ran the same P1 body and normal-load basis at **{s['current_source_refinement']['mesh_m']:.5g} m** with its separately declared 90,000-cell budget. It completed as **{s['current_source_refinement']['numerical_validity']}** under evaluation `{s['current_source_refinement']['evaluation_id'][:12]}`. This closes only that numerical invocation. The matched-displacement trend requests the next mesh/resource assessment where it remains above the stated trigger; physical material/joint allowables and acceptance remain open." if s.get('current_source_refinement') and s['current_source_refinement']['execution']=='completed' else 'The current-source continuation package is not yet available; the exact 0.2125 m request remains in the frontier.'),'',
        'Original foam/honeycomb and GFRP bodies remain non-admitted to this whole-body solver until their own complete directional material laws, attachment stock and joint models are provided. Orthotropic method patches demonstrate implementation, not purchased composite properties.','',
        '## Available propulsion and forward motion','',
        'Every changed mass automatically reaches the 2 km required-force calculation, nine independent-brake loading/fault hypotheses and three crowd-loaded precast alternatives. Rotor equivalent mass enters acceleration and braking; it is excluded from static axle gravity. P6/P7 remove the old passive-secondary account and preserve unknown replacement mass. A candidate-bound available-map gate checks actual position/speed/current/temperature samples, electrical work, thermal/current/voltage domains and normal-force interfaces. No linear, generic DC or synthetic map is silently admitted as an operating motor.','',
        f"A new transient A-z/floating-current kernel executed {s['magnetic_method_cases']} bounded method controls ({s['magnetic_completed']} completed). It uses nonlinear reversible H(B), implicit timesteps, actual phase-current excitation, net-secondary-current closure and explicit stored-energy/Joule/mechanical/discrete-time work. Its finite conductor mask stays fixed at a declared frozen velocity. The generic curve, short secondary, incomplete circuit/copper/thermal model, independent steady/mesh/transit confirmation and actual 20 m/s operating domain prevent it supplying an available-force map. Residual closure is reported without relabelling this fixture as the full LIM.",'',
        'The forward-motion method has independent synthetic tests for constant-force energy, finite powered windows, zero entry force, thermal/bus limits and stopping. Actual railway journeys remain not-run because available propulsion and complete installed inputs are missing. The receiving drive receives no safety credit in independent-braking screens.','',
        '## Manufacturing, economics and evidence','',
        'Each shared bundle produces an EBOM of actual stock, retained accounts and unresolved joints; MBOM cuts/blanks and process groups; assembly/inspection dependencies; material, supplier, access, repair and QA tasks; and source-bound price/lead-time coverage. Missing equipment is neither a box invented for an animation nor a zero-mass part. Quotes require the exact bundle/component/quantity/unit/currency context.','',
        f"The campaign now also produces **{s['model_cost_summary']['required_scope_count']} low/base/high IQD model-cost scopes** per executed candidate: rolling stock, guideway, stations/power, factory/tooling, construction, land/utilities/depot, fleet, energy, operations, maintenance, renewals, recovery, reliability and decommissioning. Dated July 2026 Iraqi CSO materials/wages are used where matched; the remaining rates and missing site/asset quantities are explicit Class C assumptions. Production capacity and civil scheduling use two 8-hour shifts, with second-shift premiums and per-shift construction productivity included. The low/base operations cases cover 16/18 service hours with two shifts; the high case prices 24-hour service with three shifts, including related staffing, energy, maintenance, reliability and renewal effects. See the [model-based cost and delivery plan](../model-based-cost-and-delivery.md). These are design-stage estimates with zero supplier quotations, not procurement-ready prices or accepted city budgets.", '',
        'The two executed new body CADs also compile candidate-bound delivery packages: the same stock IDs feed EBOM/MBOM, disabled research ERPNext Item/BOM drafts, assembly and procurement tasks, and reopened IFC body-stock geometry. Drafts are not posted to ERPNext and cannot release purchasing or manufacture. Unlocated equipment, unknown joint realization and missing commercial/process evidence remain explicit.','',
        'Candidate cost ranges are compared only where currency, rate assumptions, corridor length, trackways, station count, headway and offered capacity match. Overlapping low/base/high whole-life scenarios remain incomparable; cost dominance does not select a candidate or change the v0.6 reference. Cost inputs include declared energy, staffing, maintenance, replacement, recovery, reliability and end-of-life scenarios. City alignment/site surveys, tariffs, staffing rules, failures, supplier quotes, tax/finance and physical performance are not established. Civil results count axle envelopes, section/tendon quantities and preliminary foundation/erection hypotheses; geotechnical, torsional and construction qualification remain open.','',
        'Immutable stage requests include candidate and upstream evidence IDs. Native cache admission checks source/executable/payload plus exact body, load, mesh, method and resource request. New structural evidence invalidates dependent case evaluations even if geometry is unchanged. Stable experiment identity is separate from invocation cache counters; interrupted/pending work remains in the frontier. Native/CAD packets retain their original receipts.','',
        '```bash','./osr design railway plan','./osr design railway run --max-bundles 2 --native-jobs 1','./osr design railway run --native-jobs 12','./osr design railway publish','./osr design railway verify','```','',
        '[Summary](summary.json) · [Body definitions](bodies.json.gz) · [Canonical bundles](bundles.json.gz) · [Coupled evaluations](comparison.json.gz) · [Inventory/manufacturing records](inventories.json.gz) · [Delivery/IFC/ERP drafts](delivery-index.json) · [Native/CAD index](native-index.json) · [Current refinement](current-refinement.json.gz) · [Transient method controls](magnetic-method.json.gz) · [Pending work](frontier.json.gz) · [Source epochs](source-epochs.json) · [Source/payload manifest](manifest.json)','',
        'Large fields and CAD solids stay local or regenerate with exact sources and indexed inputs; no remote artifact object or complete manufacturing/operating release is claimed. The selected reference and all 266 city performance packages remain unchanged.','']
    return '\n'.join(lines)


def build(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output)
    folder,value=current(root)
    if (out/'manifest.json').is_file():
        m=json.loads((out/'manifest.json').read_bytes())
        if all(digest(root/n)==h for n,h in m['source_sha256'].items()):
            execution=json.loads((out/'execution.json').read_bytes())
            if (execution.get('contract_id')==value['contract_id']
                    and execution.get('run_id')==value['run_id']
                    and execution.get('campaign_id')==value['campaign_id']):
                return verify(root,out)
    if out.exists():
        retained=root/'build/coupled-railway/replaced-publications'/digest(out/'manifest.json');retained.parent.mkdir(parents=True,exist_ok=True)
        if retained.exists():raise ValueError('Previous coordinated publication already retained')
        shutil.move(out,retained)
    out.mkdir(parents=True);(out/'native').mkdir();native=[];epochs={}
    for i,r in enumerate(value['native']['packet_index']):
        p=folder/'native'/r['raw_path'];target='native/'+str(i)+'.tar.gz';(out/target).write_bytes(compact_native_archive(p))
        native.append(dict(kind=r['kind'],job_id=r['job_id'],archive=target,raw_manifest=json.loads((p/'manifest.json').read_bytes()),raw_result=json.loads((p/'result.json').read_bytes())))
    for r in value['native']['CAD_results']:
        p=folder/'native/CAD'/r['candidate_id'];target='native/CAD-'+r['candidate_id'][:12]+'.tar.gz';(out/target).write_bytes(archive(p))
        native.append(dict(kind='CAD',archive=target,raw_manifest=json.loads((p/'manifest.json').read_bytes()),raw_result=r))
    cad_ids={r['candidate_id'] for r in value['native']['CAD_results']}
    body_ids={b['candidate_id'] for b in value['bodies']}
    for p in sorted((root/'build/coupled-railway').glob('*/native/CAD/*/manifest.json')):
        r=json.loads((p.parent/'result.json').read_bytes())
        if r['candidate_id'] in cad_ids or r['candidate_id'] not in body_ids:continue
        target='native/historical-CAD-'+r['candidate_id'][:12]+'.tar.gz';(out/target).write_bytes(archive(p.parent));cad_ids.add(r['candidate_id'])
        native.append(dict(kind='historical-CAD',archive=target,raw_manifest=json.loads(p.read_bytes()),raw_result=r))
    magnetic_path=root/'build/coupled-railway/transient-method-r1/summary.json'
    magnetic=[] if not magnetic_path.is_file() else json.loads(magnetic_path.read_bytes())
    for i,r in enumerate(magnetic):
        p=root/r['path'];transient_lim.verify(p,root=root);target='native/magnetic-'+str(i)+'.tar.gz';(out/target).write_bytes(archive(p))
        native.append(dict(kind='transient-method',archive=target,raw_manifest=json.loads((p/'manifest.json').read_bytes()),raw_result=r['result']))
    seen={r['raw_result'].get('evaluation_id') for r in native}
    for p in sorted((root/'build/coupled-railway').glob('*/native/jobs/*/raw/result.json')):
        r=json.loads(p.read_bytes())
        if r.get('evaluation_id') in seen or r.get('execution')=='completed':continue
        target='native/historical-failed-'+r['evaluation_id'][:12]+'.tar.gz';(out/target).write_bytes(compact_native_archive(p.parent));seen.add(r['evaluation_id'])
        native.append(dict(kind='historical-resource-or-numerical-failure',archive=target,raw_manifest=json.loads((p.parent/'manifest.json').read_bytes()),raw_result=r))
    reused_body_cases,reuse_rejections=_retain_exact_prior_body_cases(root,value,out,native)
    refinement=_current_refinement(root,value)
    if refinement is not None:
        target='native/current-source-refinement.tar.gz';(out/target).write_bytes(archive(refinement['folder']))
        native.append(dict(kind='body-current-source-refinement',archive=target,
            raw_manifest=refinement['manifest'],raw_result=refinement['result']))
    _retain_prior_historical_packets(root,out,value,native,epochs)
    for r in native:
        result=r['raw_result'];manifest=r['raw_manifest']
        for name,h in result.get('source_sha256',manifest.get('source_sha256',{})).items():
            source=root/name
            if source.is_file() and digest(source)==h:continue
            if h in epochs:continue
            original=root/'build/coupled-railway/source-epochs'/h
            if not original.is_file() or digest(original)!=h:raise ValueError('Historical native producer bytes are unavailable')
            (out/'historical-sources').mkdir(exist_ok=True);target='historical-sources/'+h;(out/target).write_bytes(original.read_bytes());epochs[h]=dict(repository_path=name,artifact=target)
    if not magnetic:magnetic=_prior_magnetic_summary(root,value)
    inventories=[];deliveries=[]
    for b in value['bodies']:
        row=next(r for r in value['rows'] if r['body_candidate_id']==b['candidate_id'] and r['family_id']=='P1')
        stage=next(r for r in row['stages'] if r['stage']=='installed_inventory');record=json.loads((folder/'stages'/identity(stage['request'])).read_bytes())
        if record['record_id']!=stage['record_id']:raise ValueError('Inventory stage changed')
        inventories.append(record['output'])
        CAD=next((r for r in value['native']['CAD_results'] if r['candidate_id']==b['candidate_id']),None)
        if CAD is not None:
            bundle=next(x for x in value['bundles'] if x['candidate_id']==row['candidate_id']);target=folder/'delivery'/bundle['candidate_id']
            if target.exists():
                manifest=json.loads((target/'manifest.json').read_bytes())
                if manifest['files_sha256']!={p.name:digest(p) for p in target.iterdir() if p.is_file() and p.name!='manifest.json'}:raise ValueError('Delivery cache changed')
            else:manifest=railway_delivery.write(target,bundle,b,record['output'],CAD=CAD)
            prefix='delivery/'+bundle['candidate_id'][:12];(out/prefix).mkdir(parents=True)
            for name in ('delivery.json.gz','ERPNext-draft.json.gz','bim.json','body-stock.ifc.gz'):
                if (target/name).is_file():shutil.copyfile(target/name,out/prefix/name)
            deliveries.append(dict(candidate_id=bundle['candidate_id'],body_candidate_id=b['candidate_id'],prefix=prefix,raw_manifest=manifest))
    s=summary(value,magnetic,reused_body_cases=reused_body_cases,reuse_rejections=reuse_rejections,refinement=refinement)
    frontier=_published_frontier(value,refinement)
    files={'summary.json':encoded(s),'bodies.json.gz':gzip.compress(encoded(value['bodies']),mtime=0),'bundles.json.gz':gzip.compress(encoded(value['bundles']),mtime=0),
        'comparison.json.gz':gzip.compress(encoded(value['rows']),mtime=0),'inventories.json.gz':gzip.compress(encoded(inventories),mtime=0),
        'frontier.json.gz':gzip.compress(encoded(frontier),mtime=0),'magnetic-method.json.gz':gzip.compress(encoded(magnetic),mtime=0),
        'current-refinement.json.gz':gzip.compress(encoded(None if refinement is None else dict(request=refinement['request'],result=refinement['result'],
            report=refinement['report'],manifest=refinement['manifest'],verification=refinement['verified'])),mtime=0),
        'native-index.json':encoded(native),'source-epochs.json':encoded(epochs),'delivery-index.json':encoded(deliveries),'execution.json':encoded(dict(campaign_id=value['campaign_id'],run_id=value['run_id'],contract_id=value['contract_id'],
            new_bundles=value['new_bundles'],reused_bundles=value['reused_bundles'],native=value['native'],
            exact_prior_body_case_reuse=[dict(evaluation_id=r['evaluation_id'],body_candidate_id=r['body_candidate_id'],case=r['case'],source=r['exact_prior_reuse']) for r in reused_body_cases],
            executed_body_revisions=value['executed_body_revisions'])),
        'README.md':readme(s).encode()}
    for name,raw in files.items():(out/name).write_bytes(raw)
    m=dict(schema='osr-coupled-railway-publication/1',source_sha256={**value['source_sha256'],PRODUCER:digest(root/PRODUCER),
        railway_delivery.PRODUCER:digest(root/railway_delivery.PRODUCER),'engineering/design_search/wheel_twin.py':digest(root/'engineering/design_search/wheel_twin.py'),
        'engineering/design_search/generative_publication.py':digest(root/'engineering/design_search/generative_publication.py'),
        'engineering/design_search/railway_refinement_current.py':digest(root/'engineering/design_search/railway_refinement_current.py'),
        'engineering/design_search/railway_refinement_current_verifier.py':digest(root/'engineering/design_search/railway_refinement_current_verifier.py')},
        files_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},**FLAGS)
    m['manifest_id']=identity(m);(out/'manifest.json').write_bytes(encoded(m));return verify(root,out)


def verify(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);m=json.loads((out/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Coordinated publication receipt differs')
    if any(digest(root/p)!=h for p,h in m['source_sha256'].items()):raise ValueError('Coordinated source epoch changed')
    if m['files_sha256']!={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p!=out/'manifest.json'}:raise ValueError('Coordinated payload changed')
    s=json.loads((out/'summary.json').read_bytes());bodies=json.loads(gzip.decompress((out/'bodies.json.gz').read_bytes()));bundles=json.loads(gzip.decompress((out/'bundles.json.gz').read_bytes()));rows=json.loads(gzip.decompress((out/'comparison.json.gz').read_bytes()))
    for b in bodies:design_grammar.validate(b)
    for b in bundles:railway_bundle.validate(b)
    if len({b['candidate_id'] for b in bundles})!=len(bundles) or {r['candidate_id'] for r in rows}!={b['candidate_id'] for b in bundles}:raise ValueError('Mixed or incomplete bundle results')
    index={b['candidate_id']:b for b in bundles}
    for row in rows:
        if row['row_id']!=identity({k:v for k,v in row.items() if k!='row_id'}) or row['bundle_definition_id']!=index[row['candidate_id']]['definition_id']:raise ValueError('Coupled case identity differs')
        if row['body_candidate_id']!=index[row['candidate_id']]['body_candidate_id'] or row['accounted_mass']!=index[row['candidate_id']]['mass']:raise ValueError('Coupled body/mass mismatch')
        if row['motion']['forward_motion']['execution']!='not-run' or row['physical_journey_completed'] is not False:raise ValueError('Required motion cannot become an available physical journey')
        estimate=row.get('economics',{}).get('model_cost',{})
        if (estimate.get('candidate_id')!=row['candidate_id']
                or estimate.get('evaluation_id')!=identity({k:v for k,v in estimate.items() if k!='evaluation_id'})
                or estimate.get('model_cost_complete_for_declared_case') is not True
                or estimate.get('model_cost_missing_scopes')
                or estimate.get('procurement_ready') is not False
                or estimate.get('physical_or_safety_accepted') is not False):
            raise ValueError('Candidate model-cost receipt incomplete, mixed or improperly accepted')
    expected_cost_count=sum(isinstance(r.get('economics',{}).get('model_cost'),dict) for r in rows)
    cost_summary=s['model_cost_summary']
    if (cost_summary.get('candidate_estimates')!=expected_cost_count
            or cost_summary.get('complete_for_declared_case')!=expected_cost_count
            or cost_summary.get('integrated_winner') is not None):
        raise ValueError('Published model-cost summary differs from candidate estimates')
    if s.get('completion_status')!=completion_summary(rows):
        raise ValueError('Published candidate completion levels differ from their calculation evidence')
    continuation=json.loads(gzip.decompress((out/'current-refinement.json.gz').read_bytes()))
    if continuation is None:
        if s.get('current_source_refinement') is not None:
            raise ValueError('Current refinement summary has no retained package')
    else:
        request=continuation['request'];result=continuation['result'];report=continuation['report'];manifest=continuation['manifest']
        if (manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
                or manifest.get('request_id')!=identity(request)
                or request.get('parent_contract_id')!=s['contract_id']
                or request.get('body_candidate_id')!=report.get('body_candidate_id')
                or result.get('evaluation_id')!=report.get('evaluation_id')
                or result.get('evaluation_id')!=identity({k:v for k,v in result.items() if k!='evaluation_id'})
                or result.get('source_sha256')!=request.get('source_sha256')
                or manifest.get('parent_result_sha256')!=request.get('parent_result_sha256')
                or report.get('physical_and_engineering_acceptance') is not False
                or any(result.get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'))
                or continuation['verification'].get('verified') is not True
                or s.get('current_source_refinement',{}).get('manifest_id')!=manifest.get('manifest_id')):
            raise ValueError('Current-source refinement packet is mixed, changed or improperly accepted')
        indexed=next((x for x in json.loads((out/'native-index.json').read_bytes())
                      if x.get('kind')=='body-current-source-refinement'),None)
        if indexed is None or indexed.get('raw_manifest')!=manifest or indexed.get('raw_result')!=result:
            raise ValueError('Current refinement is absent or differs from native index')
        with tarfile.open(out/indexed['archive']) as tar:
            if (json.loads(tar.extractfile('request.json').read())!=request
                    or json.loads(tar.extractfile('report.json').read())!=report
                    or json.loads(tar.extractfile('manifest.json').read())!=manifest):
                raise ValueError('Archived current refinement differs from its published packet')
    if any(s.get(k) is not False for k in FLAGS) or s['integrated_selection'] is not None:raise ValueError('Research comparison cannot release a railway')
    native_index=json.loads((out/'native-index.json').read_bytes())
    native_body_count=sum(item.get('kind') in ('body','body-refinement','body-exact-cache-reuse','body-current-source-refinement') for item in native_index)
    reused_body_count=sum(item.get('kind')=='body-exact-cache-reuse' for item in native_index)
    if (native_body_count!=s.get('native_body_case_count')
            or s.get('native_body_case_count')!=s.get('native_new_body_case_count',0)+s.get('native_reused_body_case_count',0)
            or reused_body_count!=s.get('native_reused_body_case_count')):
        raise ValueError('Native body summary differs from its indexed cases')
    epochs=json.loads((out/'source-epochs.json').read_bytes())
    for h,r in epochs.items():
        if digest(out/r['artifact'])!=h:raise ValueError('Historical producer bytes differ')
    for item in native_index:
        with tarfile.open(out/item['archive']) as tar:
            ai=json.loads(tar.extractfile('archive-index.json').read());manifest=json.loads(tar.extractfile('manifest.json').read())
            result_name='native/result.json' if item.get('kind')=='body-current-source-refinement' else 'result.json'
            result=json.loads(tar.extractfile(result_name).read())
            if manifest!=item['raw_manifest'] or result!=item['raw_result']:raise ValueError('Native index differs from raw receipt')
            if manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('Nested native manifest identity differs')
            if 'evaluation_id' in result and result['evaluation_id']!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):raise ValueError('Nested native evaluation identity differs')
            if manifest['files_sha256']!={k:v for k,v in {**ai['retained_sha256'],**ai['omitted_sha256']}.items() if k!='manifest.json'}:raise ValueError('Native archive does not cover original payload')
            for name,h in ai['retained_sha256'].items():
                if sha256(tar.extractfile(name).read()).hexdigest()!=h:raise ValueError('Native payload changed')
            for name,h in result.get('source_sha256',manifest.get('source_sha256',{})).items():
                if digest(root/name)!=h and h not in epochs:raise ValueError('Native source changed')
    for r in json.loads((out/'delivery-index.json').read_bytes()):
        prefix=out/r['prefix'];manifest=r['raw_manifest'];value=json.loads(gzip.decompress((prefix/'delivery.json.gz').read_bytes()))
        if value['candidate_id']!=r['candidate_id'] or value['body_candidate_id']!=r['body_candidate_id'] or value['delivery_id']!=identity({k:v for k,v in value.items() if k!='delivery_id'}):raise ValueError('Mixed delivery identity')
        for p in prefix.iterdir():
            if digest(p)!=manifest['files_sha256'][p.name]:raise ValueError('Delivery bytes differ')
        if (prefix/'body-stock.ifc.gz').is_file() and sha256(gzip.decompress((prefix/'body-stock.ifc.gz').read_bytes())).hexdigest()!=manifest['files_sha256']['wheel-stock.ifc']:raise ValueError('Compressed IFC differs from native delivery')
    return dict(verified=True,manifest_id=m['manifest_id'],campaign_id=s['campaign_id'],body_count=len(bodies),evaluated_bundle_count=len(rows),
        native_body_case_count=s['native_body_case_count'],physical_journeys=0,complete_installed_masses=0,**FLAGS)
