"""Function-first research: explicit policy, open variables and resumable work.

A provisional target cannot reject an architecture or authorise operation. The
current demonstrated native adapter redistributes counted sill material. Other
registered choices require their own compatible generator/evaluator; they remain
live tasks rather than inheriting unrelated numbers. Budget exhaustion preserves
the frontier, never means a working design has been found or is impossible.
"""
from copy import deepcopy
from pathlib import Path
import fcntl,gzip,json,time,tomllib,shutil,os
from engineering.station_rail import ROOT,vehicle,civil,braking
from engineering.station_rail.common import encoded,identity,digest
from . import architecture_demand,wheel_body

PRODUCER='engineering/design_search/adaptive_campaign.py'
SPEC='campaigns/adaptive-railway-design.toml'
OUTPUT='docs/design-engine/v06-adaptive-design'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False)


def specification(root=ROOT):
    s=tomllib.loads((Path(root)/SPEC).read_text());b=s['invocation_budget']
    if s['schema']!='osr-adaptive-design-brief/1' or s['change_selected_reference'] is not False or s['continue_frontier_after_budget'] is not True:raise ValueError('Explicit continuing research brief required')
    if not 1<=b['native_jobs']<=8 or not 1<=b['body_candidates']<=3 or b['memory_mb'] not in (3072,5120) or b['workers']!=1 or not 1<=b['maximum_seconds']<=1800:raise ValueError('Bounded single-worker invocation required')
    return s


def sources(reference,root=ROOT):
    names=(PRODUCER,SPEC,'engineering/design_search/body_revision.py','engineering/design_search/requirement_policy.py',
        'engineering/design_search/design_variables.py','engineering/design_search/revision_planner.py',
        'engineering/design_search/section_proposals.py',
        'engineering/design_search/architecture_demand.py','engineering/design_search/wheel_body.py',
        'engineering/design_search/joint_body.py','engineering/design_search/joint_models.py',
        'engineering/station_rail/body_frame.py','engineering/station_rail/body_floor_fit.py','engineering/station_rail/body_solid_frame.py',
        'engineering/station_rail/braking.py','engineering/station_rail/civil.py',
        'docs/design-engine/v06-architecture/native-index.json','docs/design-engine/v06-architecture/manifest.json')
    return {**reference['source_sha256'],**{n:digest(Path(root)/n) for n in names}}


def coupled_requirements(car,spec):
    """Same actual accounted candidate mass; no available drive is invented."""
    c=spec['comparison'];v=car['physical_definition']['vehicle'];m=car['mass']
    if c['cars']!=v['cars'] or any(abs(m[key]-m['accounted_tare_kg_per_car']-c[people]*c['passenger_mass_kg'])>1e-6
        for key,people in [('accounted_cap_loaded_kg_per_car','normal_people_per_car'),('accounted_160_control_kg_per_car','crowd_control_people_per_car')]):
        raise ValueError('Materialize the changed formation/layout and load policy before coupling its actual mass and civil reactions')
    rot=braking.rotating_stock(car)['equivalent_inertial_mass_kg_per_car'];profiles=[]
    for load,key in [('normal','accounted_cap_loaded_kg_per_car'),('crowd','accounted_160_control_kg_per_car')]:
        for D in c['distances_m']:
            r=architecture_demand.demand(D,car['mass'][key],rot,cars=c['cars'],powered_windows=[[0.,c['launch_command_m']]],speed_cap_m_s=c['speed_cap_m_s'])
            raw_id=r.pop('demand_id');trace=r.pop('trace');r.update(schema='osr-adaptive-required-demand-index/1',raw_demand_id=raw_id,trace_sha256=identity(trace),trace_rows=len(trace));r['demand_id']=identity(r)
            profiles.append(dict(loading=load,demand=r))
    sections=[civil.alternative(car,20.,family,'crowd_control') for family in ('box-beam','twin-beam','u-beam')]
    return dict(candidate_id=car['candidate_id'],body_candidate_id=car['body_candidate_id'],
        accounted_mass=car['mass'],axle_loads=car['axle_loads'],rotating_equivalent_kg_per_car=rot,
        required_profiles=profiles,civil_comparisons=sections,available_traction_map=None,physical_journey_completed=False,
        mass_basis='Actual revised known stock plus inherited allocations; complete installed mass/CG/inertia unknown',**FLAGS)


def _write(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.pending');tmp.write_bytes(encoded(value));tmp.replace(path)


def _retain_source_epoch(root,epoch):
    """Keep exact coordinator inputs so a later publication can reproduce provenance."""
    root=Path(root);archive=root/'build/adaptive-design/coordinator-source-epochs'
    archive.parent.mkdir(parents=True,exist_ok=True)
    with (archive.parent/'source-epochs.lock').open('a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX)
        try:
            for relative,expected in epoch.items():
                source=root/relative
                if not source.is_file() or digest(source)!=expected:
                    raise ValueError('Cannot checkpoint changed or missing coordinator source: '+relative)
                target=archive/expected
                if target.exists():
                    if digest(target)!=expected:raise ValueError('Retained coordinator source hash collision: '+expected)
                    continue
                target.parent.mkdir(parents=True,exist_ok=True)
                temporary=target.with_name(target.name+'.pending.'+str(os.getpid()))
                temporary.write_bytes(source.read_bytes())
                if digest(temporary)!=expected:
                    temporary.unlink(missing_ok=True)
                    raise ValueError('Retained coordinator source failed its declared hash: '+relative)
                temporary.replace(target)
        finally:
            fcntl.flock(handle,fcntl.LOCK_UN)


def _checkpoint_invocation(root,value):
    """Persist the first and latest invocation for this exact source contract."""
    root=Path(root);base=root/'build/adaptive-design'
    canonical=base/'canonical-checkpoint.json';completed=base/'completed-invocation.json'
    base.mkdir(parents=True,exist_ok=True)
    with (base/'checkpoint.lock').open('a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX)
        try:
            previous=json.loads(canonical.read_bytes()) if canonical.is_file() else None
            previous_completed=json.loads(completed.read_bytes()) if completed.is_file() else None
            for label,record in (('canonical',previous),('completed',previous_completed)):
                if record is not None and (record.get('schema')!='osr-function-first-adaptive-campaign/1'
                        or record.get('campaign_id')!=identity({k:v for k,v in record.items() if k!='campaign_id'})):
                    raise ValueError('Prior adaptive '+label+' checkpoint identity differs')
            if (previous is None) != (previous_completed is None):
                raise ValueError('Adaptive checkpoint pair is incomplete; preserve and inspect it before resuming')
            if previous is not None and previous['contract_id']!=previous_completed['contract_id']:
                raise ValueError('Adaptive canonical and completed checkpoints have different source contracts')
            if previous is not None and previous.get('contract_id')!=value['contract_id']:
                history=base/'checkpoint-epochs'/previous['contract_id'];history.mkdir(parents=True,exist_ok=True)
                for path in (canonical,completed):
                    target=history/path.name
                    raw=path.read_bytes()
                    if target.exists() and target.read_bytes()!=raw:
                        raise ValueError('Conflicting prior adaptive checkpoint epoch: '+str(target))
                    if not target.exists():
                        temporary=target.with_name(target.name+'.pending.'+str(os.getpid()))
                        temporary.write_bytes(raw);temporary.replace(target)
                _write(canonical,value)
            elif previous is None:
                _write(canonical,value)
            elif previous.get('source_sha256')!=value.get('source_sha256'):
                raise ValueError('Adaptive checkpoint contract reused with different source hashes')
            _write(completed,value)
        finally:
            fcntl.flock(handle,fcntl.LOCK_UN)


def _native_record(folder,request):
    """Validate immutable raw inputs and exact request before reuse."""
    folder=Path(folder);m=json.loads((folder/'manifest.json').read_bytes());r=json.loads((folder/'result.json').read_bytes())
    if m['manifest_id']!=identity({n:v for n,v in m.items() if n!='manifest_id'}):raise ValueError('Native receipt differs')
    actual={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p.name not in ('manifest.json','request.json','reuse-context.json')}
    if actual!=m['files_sha256']:raise ValueError('Native payload differs')
    if json.loads((folder/'request.json').read_bytes())!=request:raise ValueError('Native request differs')
    if r['evaluation_id']!=identity({n:v for n,v in r.items() if n!='evaluation_id'}) or r['candidate_id']!=request['candidate_id']:raise ValueError('Native candidate/result identity differs')
    if r.get('definition_id')!=request.get('definition_id') or len(r.get('cases',[]))!=1 or r['cases'][0]['case']!=request.get('case') or r['cases'][0].get('mesh',{}).get('mesh_target_dx_m')!=request.get('mesh_m'):raise ValueError('Native definition/case/mesh differs')
    if r.get('tool',{}).get('requested_memory_mb')!=request.get('memory_mb') or r.get('tool',{}).get('ccx_sha256')!=request.get('ccx_sha256'):raise ValueError('Native tool/resource request differs')
    if not r.get('source_sha256') or m.get('source_sha256')!=r.get('source_sha256') or any(request.get('source_sha256',{}).get(n)!=h for n,h in r['source_sha256'].items()):raise ValueError('Native physics source binding differs')
    if any(r.get(k) is not v for k,v in FLAGS.items() if k!='configuration_adopted'):raise ValueError('Research worker cannot grant release')
    return r


def _adopt_identical_native(root,dest,request,car):
    """Reuse physics across policy/registry revisions, with explicit new context.

    No source receipt is rewritten. Only exact stock, loading, numerical model,
    mesh, solver and resource settings can match. A metadata-only policy change
    does not require pretending the geometry changed or repeating its solve.
    """
    fields=('candidate_id','definition_id','case','mesh_m','memory_mb','ccx_sha256')
    for path in sorted((Path(root)/'build/adaptive-design').glob('*/native/*/request.json')):
        old=json.loads(path.read_bytes())
        if not all(old.get(k)==request[k] for k in fields):continue
        result=_native_record(path.parent,old)
        if result['source_sha256']!=car['source_sha256']:continue
        if any(digest(Path(root)/name)!=h for name,h in result['source_sha256'].items()):continue
        shutil.copytree(path.parent,dest)
        _write(dest/'request.json',request)
        _write(dest/'reuse-context.json',dict(original_request=old,original_request_sha256=digest(path),
            original_contract_id=path.parents[2].name,new_contract_id=dest.parents[1].name,
            original_native_receipt_sha256=digest(path.parent/'manifest.json'),original_native_result_sha256=digest(path.parent/'result.json'),
            original_native_result_id=result['evaluation_id'],new_request=request,
            reason='Numerical stock/load/model/mesh/tool bytes unchanged; only coordinator/policy context differs',**FLAGS))
        return True
    return False


def aggregate(car,definition,records,spec):
    from . import requirement_policy as policy,joint_body
    labels=[]
    for r in records:
        if any(r.get(k)!=expected for k,expected in [('candidate_id',car['candidate_id']),('body_candidate_id',car['body_candidate_id']),('definition_id',definition['definition_id'])]) or len(r.get('cases',[]))!=1:raise ValueError('Cannot combine mixed physical definitions')
        if r.get('evaluation_id')!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Cannot combine a modified native result')
        labels.append(r['cases'][0]['case'])
    if len(labels)!=len(set(labels)):raise ValueError('Unique same-candidate cases required')
    cases=[r['cases'][0] for r in records];refinement=wheel_body._displacement_refinement(cases)
    valid=all(joint_body._case_valid(r) for r in cases) and refinement['status']=='pass'
    fine=next((r for r in cases if r['case']=='normal-fine' and r['execution']=='completed'),{})
    displacement=fine.get('maximum_vertical_displacement_m')
    # Bare result informs a provisional target only; actual functional limits,
    # interface evidence and qualification cannot be inferred from deflection.
    assessed=policy.assess({'body_vertical_displacement_m':displacement} if displacement is not None and valid else {},candidate_id=car['candidate_id'])
    result=dict(schema='osr-adaptive-body-result/1',candidate_id=car['candidate_id'],body_candidate_id=car['body_candidate_id'],
        definition_id=definition['definition_id'],native_cases=cases,native_record_ids=[r['evaluation_id'] for r in records],
        numerical_refinement=refinement,numerical_validity='mesh-trend-confirmed' if valid else 'unconfirmed',
        policy_assessment=assessed,provisional_target_is_acceptance_gate=False,
        accounted_tare_kg_per_car=car['mass']['accounted_tare_kg_per_car'],complete_installed_mass_kg=None,
        normal_vertical_displacement_m=displacement if valid else None,
        coupled=coupled_requirements(car,spec),integrated_suitability='unknown',**FLAGS)
    result['evaluation_id']=identity(result);return result


def _select_definitions(definitions,known,maximum_new,allow_new):
    """Resume partial work, retain finished results, then advance the frontier."""
    selected=[d for d in definitions if d['definition_id'] in known]
    unfinished=sum(len(known[d['definition_id']])<3 for d in selected)
    slots=max(0,maximum_new-unfinished) if allow_new else 0
    selected += [d for d in definitions if d['definition_id'] not in known][:slots]
    return selected


def _known_cases(root,definitions,spec):
    from . import joint_body
    valid_ids={d['definition_id'] for d in definitions};known={};records={}
    for p in sorted((Path(root)/'build/adaptive-design').glob('*/native/*/request.json')):
        if not (p.parent/'manifest.json').is_file():continue
        req=json.loads(p.read_bytes());uid=req.get('definition_id');label=req.get('case')
        if uid not in valid_ids or label not in spec['body_cases'] or req.get('mesh_m')!=spec['body_cases'][label] or req.get('memory_mb')!=spec['invocation_budget']['memory_mb'] or req.get('ccx_sha256')!=digest('/usr/bin/ccx'):continue
        r=json.loads((p.parent/'result.json').read_bytes())
        if any(not (Path(root)/n).is_file() or digest(Path(root)/n)!=h for n,h in r.get('source_sha256',{}).items()):continue
        _native_record(p.parent,req);known.setdefault(uid,set()).add(label);records.setdefault(uid,{})[label]=r['cases'][0]
    model_holds=[uid for uid,rr in records.items() if any(not joint_body._case_valid(c) for c in rr.values()) or
        'normal' in rr and 'normal-fine' in rr and wheel_body._displacement_refinement(list(rr.values()))['status']=='fail']
    return known,model_holds


def run(root=ROOT,*,maximum_new_jobs=None,state=None):
    from . import body_revision as body,design_variables,requirement_policy,revision_planner,section_proposals
    root=Path(root);spec=specification(root);reference=vehicle.build(root);epoch=sources(reference,root)
    _retain_source_epoch(root,epoch)
    contract=identity(dict(specification=spec,sources=epoch,reference_id=reference['candidate_id']))
    folder=root/'build/adaptive-design'/contract if state is None else Path(state);folder.mkdir(parents=True,exist_ok=True)
    budget=spec['invocation_budget']['native_jobs'] if maximum_new_jobs is None else maximum_new_jobs
    if type(budget) is not int or not 0<=budget<=spec['invocation_budget']['native_jobs']:raise ValueError('Explicit per-invocation native budget required')
    with (folder/'campaign.lock').open('a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB);started=time.monotonic();new_jobs=0;reused=0;rows=[];frontier=[];followup_plans=[]
        definitions=body.definitions(reference,root=root)+section_proposals.generate(reference,samples=spec['exploration']['section_samples'],root=root)
        # Minimum stock first, then a smaller envelope: diverse measurable
        # experiments, not an arbitrary deflection-limit acceptance ranking.
        definitions.sort(key=lambda d:(d['geometry_metrics']['sill_stock_delta_kg'],d['parameters']['sill_depth_m']))
        known,model_holds=_known_cases(root,definitions,spec)
        selected_definitions=_select_definitions(definitions,known,spec['invocation_budget']['body_candidates'],budget>0 and not model_holds)
        selected=[]
        for definition in selected_definitions:
            car=body.materialize(reference,definition,root=root)
            car['source_sha256'].update(definition.get('definition_source_sha256',{}))
            car['evaluation_id']=identity({k:v for k,v in car.items() if k!='evaluation_id'})
            selected.append((definition,car))
        jobs=[]
        for definition,car in selected:
            records=[]
            for label,mesh in spec['body_cases'].items():
                request=dict(candidate_id=car['candidate_id'],definition_id=definition['definition_id'],source_sha256=car['source_sha256'],
                    case=label,mesh_m=mesh,memory_mb=spec['invocation_budget']['memory_mb'],ccx_sha256=digest('/usr/bin/ccx'))
                job_id=identity(request);dest=folder/'native'/job_id;dest.parent.mkdir(exist_ok=True)
                if sources(reference,root)!=epoch:raise ValueError('Adaptive source changed during execution')
                if not dest.exists():_adopt_identical_native(root,dest,request,car)
                if (dest/'manifest.json').is_file():
                    records.append(_native_record(dest,request));reused+=1;jobs.append(dict(job_id=job_id,state='reused',request=request));continue
                if new_jobs>=budget or time.monotonic()-started>spec['invocation_budget']['maximum_seconds']:
                    frontier.append(dict(kind='native-evaluation',job_id=job_id,request=request,state='ready'));continue
                if dest.exists():
                    # Preserve interrupted raw input/logs. No complete receipt
                    # means no reuse and no inferred valid result.
                    partial=folder/'interrupted';partial.mkdir(exist_ok=True)
                    dest.rename(partial/(job_id+'-'+str(time.time_ns())))
                result=body.run(car,definition,dest,root=root,case_labels=[label],mesh_override={label:mesh},memory_mb=spec['invocation_budget']['memory_mb'])
                _write(dest/'request.json',request);records.append(_native_record(dest,request));new_jobs+=1
                jobs.append(dict(job_id=job_id,state=result['execution'],request=request))
                _write(folder/'journal.json',dict(contract_id=contract,new_jobs=new_jobs,reused_jobs=reused,jobs=jobs,frontier=frontier,**FLAGS))
            if records:
                result=aggregate(car,definition,records,spec)
                diagnosis=dict(candidate_id=car['candidate_id'],evaluation_id=result['evaluation_id'],
                    requirement_revision=result['policy_assessment']['requirement_revision'],execution='completed',
                    numerical_validity='valid' if result['numerical_validity']=='mesh-trend-confirmed' else 'unknown',
                    failure_class='evidence-gap' if result['numerical_validity']=='mesh-trend-confirmed' else 'numerical',
                    domain='body',diagnosis='Establish actual thin-wall strength/buckling/joint and functional interface limits after the measured displacement trend' if result['numerical_validity']=='mesh-trend-confirmed' else 'Complete or repair same-candidate mesh, equilibrium and energy checks before physical interpretation')
                next_plan=revision_planner.plan(car['candidate_id'],diagnosis,maximum_proposals=4)
                frontier.extend(dict(kind='engineering-task',proposal=p,state='prepared') for p in next_plan['proposals'])
                followup_plans.append(next_plan);rows.append(result)
        # Every unrun physical proposal remains visible instead of being lost
        # at a fixed generation count. Unsupported choices become development
        # tasks, never silently coerce into one of four old parameter pairs.
        frontier.extend(dict(kind='physical-proposal',definition=definition,state='ready-for-resource-allocation') for definition in definitions if definition not in selected_definitions)
        index=json.loads((root/'docs/design-engine/v06-architecture/native-index.json').read_bytes())
        seed_record=next(r['raw_result'] for r in index if r['name']=='finite-body-resource-r4')
        fine=next(c for c in seed_record['cases'] if c['case']=='normal-fine')
        seed=dict(candidate_id=seed_record['candidate_id'],execution=seed_record['execution'],numerical_validity='valid' if seed_record['numerical_validity']=='mesh_confirmed' else 'unknown',failure_class='advisory-target',
            evaluation_id=seed_record['evaluation_id'],requirement_revision=identity(requirement_policy.catalogue()['criteria']),domain='body',
            diagnosis='Provisional global deflection target exceeded; derive functional limits and compare efficient load paths rather than automatically reject or add stock',
            source_evaluation_id=seed_record['evaluation_id'],observations=dict(body_vertical_displacement_m=fine['maximum_vertical_displacement_m'],target_m=.0256),
            scope='Previously published finite-area body result, distinct from the selected reference; provisional target prompts requirements review and research, never structural rejection')
        plans=revision_planner.plan(seed['candidate_id'],seed,maximum_proposals=8)
        value=dict(schema='osr-function-first-adaptive-campaign/1',contract_id=contract,source_sha256=epoch,specification=spec,
            selected_reference_candidate_id=reference['candidate_id'],variable_registry=design_variables.catalogue(),requirement_policy=requirement_policy.catalogue(),
            physical_definitions=definitions,results=rows,result_revision_plans=followup_plans,seed_observation=seed,seed_assessment=requirement_policy.assess({'body_vertical_displacement_m':fine['maximum_vertical_displacement_m']},candidate_id=seed['candidate_id']),revision_plan=plans,frontier=frontier,
            new_native_jobs=new_jobs,reused_native_jobs=reused,model_repair_required_before_new_physical_trials=model_holds,search_status='work-remaining',
            stopping_reason='Invocation budget reached or current measurable experiments completed; frontier and model/measurement work remain active',
            integrated_selection=None,selected_reference_changed=False,city_packages_regenerated=0,**FLAGS)
        value['campaign_id']=identity(value);_write(folder/'result.json',value)
        _write(folder/'journal.json',dict(contract_id=contract,new_jobs=new_jobs,reused_jobs=reused,jobs=jobs,frontier=frontier,search_status=value['search_status'],**FLAGS))
        _checkpoint_invocation(root,value)
        return value


def verify(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);m=json.loads((out/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({n:v for n,v in m.items() if n!='manifest_id'}):raise ValueError('Adaptive publication identity differs')
    if any(digest(root/p)!=h for p,h in m['source_sha256'].items()):raise ValueError('Adaptive publication source differs')
    if {p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p!=out/'manifest.json'}!=m['files_sha256']:raise ValueError('Adaptive publication bytes differ')
    value=json.loads(gzip.decompress((out/'campaign.json.gz').read_bytes()))
    if value['campaign_id']!=identity({n:v for n,v in value.items() if n!='campaign_id'}):raise ValueError('Adaptive result identity differs')
    if any(value.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Adaptive research cannot grant acceptance')
    return dict(verified=True,campaign_id=value['campaign_id'],physical_definitions=len(value['physical_definitions']),evaluated_candidates=len(value['results']),search_status=value['search_status'],**FLAGS)
