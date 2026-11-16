"""Coordinate architecture, adaptive proposals and generated physical bodies.

This is one dependency-driven execution path. A new body creates new physical
railway bundles and automatically invalidates the downstream mass, propulsion,
braking, civil, manufacturing and economic evaluations. Existing campaigns are
retained component adapters and historical evidence, not silently overwritten.
"""
from copy import deepcopy
from pathlib import Path
import fcntl,json,os,tempfile,time,tomllib,uuid
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity,digest
from . import aggregate_store,canonical_stream,case_node_store,design_grammar as grammar,grammar_geometry,grammar_structure
from . import failure_diagnosis,redesign_engine,revision_planner,design_variables,railway_bundle as bundle_adapter,model_cost

PRODUCER='engineering/design_search/railway_campaign.py'
SPEC='campaigns/coupled-railway-design.toml'
FLAGS=grammar.FLAGS
STAGES=('installed_inventory','interfaces','architecture','propulsion','motion_and_braking','civil','manufacturing_and_economics')
EDGES=[('body','installed_inventory'),('body','interfaces'),('interfaces','structure'),('body','structure'),('installed_inventory','propulsion'),
    ('installed_inventory','motion_and_braking'),('architecture','propulsion'),('propulsion','motion_and_braking'),
    ('installed_inventory','civil'),('structure','civil'),('installed_inventory','manufacturing_and_economics'),
    ('propulsion','manufacturing_and_economics'),('motion_and_braking','manufacturing_and_economics'),
    ('civil','manufacturing_and_economics'),('manufacturing_and_economics','selection')]


def specification(root=ROOT):
    s=tomllib.loads((Path(root)/SPEC).read_text())
    if s['schema']!='osr-coupled-railway-campaign/1' or s['reference_changes_allowed'] is not False or s['maintain_pending_tasks'] is not True:raise ValueError('Explicit non-promoting continuing railway campaign required')
    if not 1<=s['maximum_bundle_cases']<=128 or not 1<=s['maximum_native_jobs']<=12 or not 1<=s['maximum_seconds']<=1800:raise ValueError('Bounded execution required')
    if s['required_trajectory_is_available_thrust'] is not False or s['selection']['unknown_prices_are_zero'] is not False:raise ValueError('Missing physics or prices cannot become available capability')
    return s


def source_epoch(root=ROOT):
    root=Path(root)
    names=['railway_campaign','aggregate_store','case_node_store','canonical_stream','railway_bundle','railway_native','system_inventory','system_selection','system_motion','system_body','grammar_shell',
        'design_grammar','grammar_structure','grammar_geometry','interface_graph','failure_diagnosis','redesign_engine','revision_planner','design_variables','model_cost',
        'railway_architecture','architecture_demand','capabilities','requirement_policy','material_database','dfma','structural_families','joining_catalogue','wheel_motor']
    paths=[SPEC,'campaigns/whole-railway-architecture-search.toml',*[f'engineering/design_search/{n}.py' for n in names],
        'engineering/station_rail/common.py','engineering/station_rail/braking.py','engineering/station_rail/civil.py','engineering/station_rail/vehicle.py',
        'engineering/station_rail/electrical.py','engineering/station_rail/brief.toml','engineering/station_rail/__init__.py',
        'engineering/design_search/transient_lim.py','engineering/design_search/lim_materials.py','engineering/design_search/data/getdp-steel-generic.json',
        'engineering/station_rail/long_motor.py','engineering/station_rail/station_motor.py','engineering/station_rail/body_solid_frame.py',
        'docs/design-engine/ferrite-maglev/comfort-design/design.json.gz','docs/design-engine/ferrite-maglev/comfort-design/manifest.json',
        model_cost.RATE_DATA]
    return {**{n:digest(root/n) for n in paths},**case_node_store.codec_source_identity(root)}


def contract_identity(spec,epoch,*,root=ROOT):
    return identity(dict(specification=spec,source_sha256=epoch,case_stage_store=case_node_store.SCHEMA))


def _write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    descriptor,name=tempfile.mkstemp(prefix='.'+path.name+'.',suffix='.pending',dir=path.parent)
    pending=Path(name)
    with os.fdopen(descriptor,'wb') as output:
        canonical_stream.write_canonical(value,output)
        output.flush();os.fsync(output.fileno())
    os.replace(pending,path)


def _stage(folder,name,bundle,inputs,epoch,calculate,*,root=ROOT):
    if source_epoch(root)!=epoch:raise ValueError('Coupled source epoch changed before stage execution')
    request=dict(stage=name,bundle_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],inputs=inputs,source_sha256=epoch)
    key=identity(request);target=case_node_store.path_for(folder/'stages',key)
    def check(r):
        if r['request']!=request or r['record_id']!=identity({k:v for k,v in r.items() if k!='record_id'}):raise ValueError('Stage cache differs from exact candidate/dependency request')
    if target.exists() or target.is_symlink():
        r=_read_cached_stage(target,root=root)
        check(r)
        return r,True
    r=case_node_store.recover(target,'stage',check,root=root,maximum=_STAGE_RECORD_MAX_BYTES)
    if r is not None:return r,True
    output=calculate()
    if source_epoch(root)!=epoch:raise ValueError('Coupled source epoch changed during stage execution')
    if isinstance(output,dict) and output.get('candidate_id',bundle['candidate_id'])!=bundle['candidate_id']:raise ValueError('Stage output belongs to another physical bundle')
    r=dict(schema='osr-coupled-stage-record/1',request=request,output=output,**FLAGS);r['record_id']=identity(r)
    case_node_store.write(target,r,'stage',root=root)
    return r,False


def semantic_id(result):
    """Stream the exact semantic evidence identity; reject unsupported values."""
    return canonical_stream.canonical_identity(result,semantic=True)


def _aggregate_identity(result):
    return canonical_stream.canonical_identity(result)


class _Discard:
    def write(self,data):return len(data)


def current_aggregate(folder,contract):
    """Resolve one sealed active snapshot without admitting historical JSON."""
    folder=Path(folder)
    pointer=folder/'aggregate-current.json'
    if pointer.is_symlink() or not pointer.is_file() or pointer.stat().st_size>4096:
        raise ValueError('Bounded active aggregate pointer required')
    raw=pointer.read_bytes()
    value=json.loads(raw,object_pairs_hook=case_node_store._unique_pairs)
    if (not isinstance(value,dict) or set(value)!={'schema','contract_id','run_id','manifest_id','aggregate_sha256'}
            or value['schema']!='osr-coupled-aggregate-pointer/2' or value['contract_id']!=contract
            or not all(isinstance(value[k],str) and len(value[k])==64 and all(c in '0123456789abcdef' for c in value[k])
                       for k in ('run_id','manifest_id','aggregate_sha256'))
            or raw!=encoded(value)):
        raise ValueError('Active aggregate pointer differs')
    target=folder/'aggregates'/value['run_id']
    if target.is_symlink() or not target.is_dir():raise ValueError('Active aggregate snapshot unavailable')
    return target,value


def _write_aggregate(folder,result,*,root=ROOT):
    """Publish immutable Arrow core and row references, then advance the pointer."""
    folder=Path(folder);target=folder/'aggregates'/result['run_id']
    if target.exists() or target.is_symlink():
        manifest=aggregate_store.read(target,folder/'cases',_Discard(),root=root)
        if manifest['aggregate_sha256']!=canonical_stream.canonical_identity(result):
            raise ValueError('Existing aggregate snapshot differs from exact invocation')
    else:
        manifest=aggregate_store.write(target,result,folder/'cases',root=root)
    if (manifest['run_id']!=result['run_id'] or manifest['campaign_id']!=result['campaign_id']
            or manifest['contract_id']!=result['contract_id']):
        raise ValueError('Aggregate snapshot identity differs')
    pointer=dict(schema='osr-coupled-aggregate-pointer/2',contract_id=result['contract_id'],
                 run_id=result['run_id'],manifest_id=manifest['manifest_id'],
                 aggregate_sha256=manifest['aggregate_sha256'])
    _write(folder/'aggregate-current.json',pointer)
    return pointer


def _validate_cached_row(row,case_context,bundle,epoch):
    """Check the case envelope; stage file consistency is verified separately."""
    if row['case_context_id']!=case_context or row['bundle_definition_id']!=bundle['definition_id'] or row['row_id']!=canonical_stream.canonical_identity({k:v for k,v in row.items() if k!='row_id'}):
        raise ValueError('Coupled case identity differs')
    stages=row.get('stages')
    if (not isinstance(stages,list) or tuple(s.get('stage') for s in stages if isinstance(s,dict))!=STAGES
            or any(not isinstance(s,dict) or not isinstance(s.get('request'),dict)
                   or s['request'].get('source_sha256')!=epoch for s in stages)):
        raise ValueError('Coupled cached case source epoch differs')


_STAGE_RECORD_MAX_BYTES=128*1024*1024
_CASE_RECORD_MAX_BYTES=128*1024*1024
_EVALUATION_STAGES=frozenset(('installed_inventory','architecture','propulsion','motion_and_braking','manufacturing_and_economics'))


def _same_json(left,right):
    """Compare JSON types/values without conflating bool/int or signed zero."""
    if type(left) is not type(right):return False
    if isinstance(left,dict):
        return left.keys()==right.keys() and all(_same_json(left[k],right[k]) for k in left)
    if isinstance(left,list):
        return len(left)==len(right) and all(_same_json(a,b) for a,b in zip(left,right))
    if isinstance(left,float):return repr(left)==repr(right)
    return left==right


def _same_compacted_motion(original,compact):
    """Compare the motion projection without deep-copying its large traces."""
    if type(original) is not type(compact):return False
    if isinstance(original,dict):
        traced=isinstance(original.get('trace'),list)
        keys=(original.keys()-{'trace'}|{'trace_index'}) if traced else original.keys()
        if keys!=compact.keys():return False
        for key,value in original.items():
            if traced and key=='trace':
                expected=dict(rows=len(value),sha256=canonical_stream.canonical_identity(value))
                if not _same_json(expected,compact['trace_index']):return False
            elif traced and key=='trace_index':
                continue
            elif not _same_compacted_motion(value,compact[key]):return False
        return True
    if isinstance(original,list):
        return len(original)==len(compact) and all(_same_compacted_motion(a,b) for a,b in zip(original,compact))
    return _same_json(original,compact)


def _read_cached_stage(path,*,root=ROOT):return case_node_store.read(path,'stage',root=root,maximum=_STAGE_RECORD_MAX_BYTES)


def _read_cached_case(path,*,root=ROOT):return case_node_store.read(path,'case',root=root,maximum=_CASE_RECORD_MAX_BYTES)


def _verify_evaluation_identity(value,kind):
    if (not isinstance(value,dict) or 'evaluation_id' not in value
            or value['evaluation_id']!=canonical_stream.canonical_identity({k:v for k,v in value.items() if k!='evaluation_id'})):
        raise ValueError('Coupled cached '+kind+' evaluation identity differs')


def _verify_cached_stages(folder,row,bundle,epoch,structure_context,*,root=ROOT):
    """Verify all declared stage files and row projections before case reuse.

    These checks establish internal consistency, not authenticated physical
    evidence; regular file reads and advisory locks do not provide a sandbox.
    """
    if (row['candidate_id']!=bundle['candidate_id'] or row['body_candidate_id']!=bundle['body_candidate_id']
            or row['family_id']!=bundle['family_id'] or row['motor_component_id']!=bundle['propulsion_component_id']
            or not _same_json(row['accounted_mass'],bundle['mass'])
            or not _same_json(row['architecture_added_mass_unknown'],bundle['unweighed_architecture_equipment'])
            or not _same_json(row['structure_context'],structure_context)
            or row['case_context_id']!=identity(dict(bundle_definition_id=bundle['definition_id'],structure_evidence=structure_context))
            or row.get('installed_mass_kg') is not None or row.get('complete_body_qualified') is not False
            or row.get('physical_journey_completed') is not False or any(row.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError('Coupled cached case composition or disposition differs')
    base=dict(bundle_definition_id=bundle['definition_id']);body=dict(body_definition_id=bundle['body_definition_id'],**base)
    upstream=[];architecture_id=None;propulsion_id=None;source_ids=[]
    for index,name in enumerate(STAGES):
        ref=row['stages'][index]
        if set(ref)!={'stage','request','record_id','reused'} or type(ref['reused']) is not bool:
            raise ValueError('Coupled cached stage reference differs')
        if name in ('installed_inventory','interfaces'):inputs=body
        elif name=='architecture':inputs=base
        elif name=='propulsion':inputs=dict(architecture_evaluation_id=architecture_id,**base)
        elif name=='motion_and_braking':inputs=dict(propulsion_evaluation_id=propulsion_id,**base)
        elif name=='civil':inputs=dict(structure_context=structure_context,**base)
        else:inputs=dict(upstream=list(upstream),**base)
        expected=dict(stage=name,bundle_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],inputs=inputs,source_sha256=epoch)
        if ref['stage']!=name or not _same_json(ref['request'],expected):raise ValueError('Coupled cached stage request differs')
        record=_read_cached_stage(case_node_store.path_for(Path(folder)/'stages',identity(expected)),root=root)
        if (not isinstance(record,dict) or set(record)!={'schema','request','output','record_id',*FLAGS}
                or record['schema']!='osr-coupled-stage-record/1' or not _same_json(record['request'],expected)
                or record['record_id']!=ref['record_id']
                or record['record_id']!=canonical_stream.canonical_identity({k:v for k,v in record.items() if k!='record_id'})
                or any(record.get(k) is not v for k,v in FLAGS.items())):
            raise ValueError('Coupled cached stage record differs')
        out=record['output']
        if not isinstance(out,dict) or out.get('candidate_id',bundle['candidate_id'])!=bundle['candidate_id']:
            raise ValueError('Coupled cached stage output candidate differs')
        if 'body_candidate_id' in out and out['body_candidate_id']!=bundle['body_candidate_id']:
            raise ValueError('Coupled cached stage output body differs')
        if any(k in out and out[k] is not v for k,v in FLAGS.items()):raise ValueError('Coupled cached stage output disposition differs')
        if name in _EVALUATION_STAGES:_verify_evaluation_identity(out,name)
        elif 'evaluation_id' in out:raise ValueError('Unexpected cached stage evaluation identity')
        if name=='installed_inventory':
            if out.get('schema')!='osr-canonical-system-inventory/1':raise ValueError('Coupled cached inventory schema differs')
            source_ids.append(out['evaluation_id'])
        elif name=='architecture':
            if out.get('schema')!='osr-railway-architecture-screen-index/1':raise ValueError('Coupled cached architecture schema differs')
            trajectory=out.get('trajectory')
            if (not isinstance(trajectory,dict) or trajectory.get('schema')!='osr-architecture-demand-index/1'
                    or trajectory.get('indexed_demand_id')!=canonical_stream.canonical_identity({k:v for k,v in trajectory.items() if k!='indexed_demand_id'})):
                raise ValueError('Coupled cached indexed demand identity differs')
            source_ids.append(out['evaluation_id'])
        elif name in ('propulsion','motion_and_braking'):
            if name=='motion_and_braking' and out.get('schema')!='osr-coupled-longitudinal-research/1':raise ValueError('Coupled cached motion schema differs')
            source_ids.append(out['evaluation_id'])
        elif name=='civil':source_ids.append(canonical_stream.canonical_identity(out))
        elif name=='manufacturing_and_economics':
            if not _same_json(out.get('source_evaluation_ids'),source_ids):raise ValueError('Coupled cached economic source identities differ')
            model=out.get('model_cost');_verify_evaluation_identity(model,'model cost')
            model_inputs=dict(inventory_evaluation_id=source_ids[0],architecture_evaluation_id=source_ids[1],
                propulsion_evaluation_id=source_ids[2],motion_evaluation_id=source_ids[3],civil_evaluation_id=source_ids[4],bundle_definition_id=bundle['definition_id'])
            if (model.get('schema')!='osr-coupled-model-cost/1' or model.get('candidate_id')!=bundle['candidate_id']
                    or not _same_json(model.get('input_evaluation_ids'),model_inputs)):
                raise ValueError('Coupled cached model cost inputs differ')
        if name=='installed_inventory':matches=_same_json(row['inventory_summary'],_inventory_summary(out))
        elif name=='motion_and_braking':matches=_same_compacted_motion(out,row['motion'])
        else:matches=_same_json(out,row[{'interfaces':'interfaces','architecture':'architecture','propulsion':'propulsion','civil':'civil','manufacturing_and_economics':'economics'}[name]])
        if not matches:raise ValueError('Coupled cached stage output differs from case projection')
        if name=='architecture':architecture_id=out['evaluation_id']
        if name=='propulsion':propulsion_id=out['evaluation_id']
        upstream.append(record['record_id'])


def _ordinary_state_path(folder):
    path=Path(folder)
    if '..' in path.parts:raise ValueError('Coupled state path must not contain parent traversal')
    path=Path(os.path.abspath(path))
    if any(part.is_symlink() for part in (path,*path.parents)):
        raise ValueError('Coupled state path and ancestors must not be symlinks')
    return path


def state_source_contract(contract,epoch,*,root=ROOT):
    return dict(schema='osr-coupled-state-source/2',case_stage_store=case_node_store.SCHEMA,
                contract_id=contract,source_sha256=epoch)


def _bind_state_source(folder,contract,epoch,*,root=ROOT):
    """Check declared source context, not authentication or a sandbox."""
    folder=_ordinary_state_path(folder);marker=folder/'source-contract.json';journal=folder/'journal.json'
    expected=state_source_contract(contract,epoch,root=root)
    for path in (marker,journal):
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError('Coupled state contract metadata is not an ordinary file')
    for name in ('cases','stages','native'):
        path=folder/name
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ValueError('Coupled cache directories must be ordinary directories')
    if marker.is_file():
        if json.loads(marker.read_bytes())!=expected:raise ValueError('Coupled state source contract differs')
        for name in ('cases','stages'):
            cache=folder/name
            if cache.is_dir() and any(not (item.name.endswith('.parquet') or item.name.endswith('.parquet.pending')) for item in cache.iterdir()):
                raise ValueError('Coupled v2 state contains legacy or unexpected case/stage cache')
    else:
        for name in ('cases','stages','native'):
            p=folder/name
            if p.is_symlink() or (p.exists() and (not p.is_dir() or any(p.iterdir()))):
                raise ValueError('Coupled state has unbound existing cache')
        if journal.is_file() and json.loads(journal.read_bytes()).get('contract_id')!=contract:
            raise ValueError('Coupled state journal contract differs')
        _write(marker,expected)
    if journal.is_file() and json.loads(journal.read_bytes()).get('contract_id')!=contract:
        raise ValueError('Coupled state journal contract differs')


def generate_bodies():
    """Use the existing grammar and adaptive planner in the same execution."""
    from . import system_body,grammar_shell,railway_native
    parents=grammar.initial_candidates();bodies=list(parents);decisions=[]
    for parent in parents:
        rigidity=grammar_structure.diagnose_rigidity(parent['structure'])
        diagnosis=failure_diagnosis.diagnose(parent,rigidity=rigidity)
        observation=dict(candidate_id=parent['candidate_id'],evaluation_id=identity(rigidity),requirement_revision=parent['requirement_revision'],
            execution='completed',numerical_validity='valid',failure_class='design-failure' if rigidity['mechanism_count'] else 'evidence-gap',
            domain='body',diagnosis='Declared pin-jointed underfloor has mechanisms; this does not reject a complete bonded shell or welded frame')
        adaptive=revision_planner.plan(parent['candidate_id'],observation,maximum_proposals=4)
        revised=redesign_engine.revise(parent,diagnosis,maximum=1)
        for row in revised['revisions']:
            bodies.append(row['candidate']);decisions.append(dict(parent_id=parent['candidate_id'],child_id=row['candidate']['candidate_id'],operator=row['operator'],
                cause='conditional pin-graph mechanism',diagnosis_id=diagnosis['diagnosis_id'],adaptive_plan=adaptive,
                scope='An actual underfloor topology experiment; no full-body verdict follows'))
    for parent,topology in ((parents[0],'aluminium_frame'),(parents[2],'aluminium_stressed_skin')):
        child=system_body.build(parent,topology=topology);grammar.validate(child);bodies.append(child)
        decisions.append(dict(parent_id=parent['candidate_id'],child_id=child['candidate_id'],operator='physical-assembly-completion/'+topology,
            cause='Quantified frame/panel connection gaps and unavailable composite constitutive laws',
            scope='Counted new load paths and declared aluminium/weld numerical hypothesis; material/joint strength qualification remains open'))
        estimate=railway_native.cell_estimate(child,1.7)
        if estimate['solid_cells']>specification()['maximum_solid_cells_per_job']:
            aligned=system_body.build(parent,topology=topology,profile_policy='aligned');aligned['parent_candidate_ids']=[child['candidate_id']]
            aligned['revision_reason']='Standardize floor/roof profiles and alignment after an observed conformal-grid resource failure; preserve functional openings and physical load paths'
            aligned['definition_id']=identity({k:v for k,v in aligned.items() if k!='definition_id'});grammar.validate(aligned);bodies.append(aligned)
            decisions.append(dict(parent_id=child['candidate_id'],child_id=aligned['candidate_id'],operator='profile-standardization-and-alignment',
                cause='Retained 5GiB allocation failure and quantified conformal cut proliferation',prior_mesh_estimate=estimate,
                scope='A new physical/manufacturing arrangement, not a failed structural verdict or a weakened functional limit'))
    if len(bodies)!=14 or len({b['candidate_id'] for b in bodies})!=len(bodies):raise ValueError('Distinct bounded physical definitions required')
    return bodies,decisions


def propulsion(bundle,architecture_result):
    definition=bundle['motor_definition'];parameters=bundle['motor_parameters']
    result=dict(candidate_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],motor_component_id=bundle['propulsion_component_id'],
        required_force_N_per_car=architecture_result['trajectory']['peak_required_force_N_per_car'],
        required_peak_power_W_train=architecture_result['trajectory']['peak_required_power_W_train'],available_force_map=None,
        electrical_thermal_duty_verified=False,actual_installed_cost_USD=None,**FLAGS)
    if parameters is None:
        result.update(execution='model-development-required',bare_primary_kg_per_m=None,
            tasks=['Generate actual replacement propulsion geometry/material/circuit and installed stock before creating an available-force map'])
    else:
        result.update(execution='required-performance-and-stock-evaluated',bare_primary_kg_per_m=definition['bare_primary_stock_kg_per_m'],
            installed_winding_m_per_leg=sum(b-a for a,b in bundle['architecture_case']['physical_definition']['wayside']['installed_linear_track_intervals_per_leg_m']),
            physical_primary_definition_id=definition['motor_component_id'],
            tasks=['Transient nonlinear moving A-u/circuit model and independent limits','Finite-height return current and entry/exit/section handoff',
                'Actual steel law, heat flow, inverter voltage/current and repeated duty','Available force/current/normal-force/loss map over the exact operating domain'])
    result['evaluation_id']=identity(result);return result


def economics(bundle,inventory,architecture_result,propulsion_result,motion_result,civil_result,*,root=ROOT):
    quantities=architecture_result['quantity_coefficients']
    estimate=model_cost.evaluate(bundle,inventory,architecture_result,propulsion_result,motion_result,civil_result,root=root)
    result=dict(candidate_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],
        source_evaluation_ids=[r.get('evaluation_id',identity(r)) for r in (inventory,architecture_result,propulsion_result,motion_result,civil_result)],
        coefficients=quantities,vehicle_installed_cost_USD=None,wayside_installed_cost_USD=None,civil_installed_cost_USD=None,
        actual_energy_purchase_kWh=None,maintenance_renewal_downtime_cost_USD=None,whole_life_cost_USD=None,
        estimated_factory_gate_IQD=estimate['factory_gate_cost_iqd'],estimated_delivered_IQD=estimate['delivered_cost_iqd'],
        model_based_installed_CAPEX_IQD=estimate['model_based_installed_CAPEX_iqd'],
        model_based_whole_life_NPV_IQD=estimate['model_based_whole_life_NPV_iqd'],
        model_cost=estimate,
        tasks=['Replace Class C labour, plant, equipment and life assumptions with source-bound supplier/process evidence',
            'Replace right-of-way, foundation, utility, access, depot, transport and installation proxies with surveyed site quantities',
            'Validate propulsion electrical duty, available thrust, measured energy use, maintenance and failure rates',
            'Compare model-cost ranges at equal service; do not use this estimate as procurement approval or an integrated winner'],
        model_cost_complete_for_declared_case=estimate['model_cost_complete_for_declared_case'],
        procurement_ready=False,physical_or_safety_accepted=False,economic_winner=None,
        currency='IQD',estimate_class='C',
        scope='Candidate-bound model-based cost completion for the declared corridor; supplier/procurement evidence and physical acceptance remain separate.',**FLAGS)
    result['evaluation_id']=identity(result);return result


def _compact_motion(value):
    # Keep exact histories in immutable stage packets. Build only the report
    # projection; copying the full traces first doubles their live footprint.
    def compact(node):
        if isinstance(node,dict):
            result={key:compact(item) for key,item in node.items()
                    if key!='trace' or not isinstance(item,list)}
            rows=node.get('trace')
            if isinstance(rows,list):
                trace_id=canonical_stream.canonical_identity(rows)
                result['trace_index']=dict(rows=len(rows),sha256=trace_id)
            return result
        if isinstance(node,list):return [compact(item) for item in node]
        return deepcopy(node)
    return compact(value)


def run(root=ROOT,*,maximum_new_bundles=None,native_jobs=0,state=None):
    """Run a source-bound campaign under the target filesystem's disk budget."""
    root=Path(root)
    spec=specification(root)
    if type(native_jobs) is not int or not 0<=native_jobs<=spec['maximum_native_jobs']:
        raise ValueError('Explicit bounded native job allowance required')
    if maximum_new_bundles is not None and (type(maximum_new_bundles) is not int or maximum_new_bundles<0):
        raise ValueError('Nonnegative resumable bundle budget required')
    from engineering.performance import GIB,disk_reservation
    count=spec['maximum_bundle_cases'] if maximum_new_bundles is None else min(maximum_new_bundles,spec['maximum_bundle_cases'])
    projected=GIB + count*(GIB//2) + native_jobs*(8*GIB)
    target=root/'build/coupled-railway' if state is None else state
    with disk_reservation(root,target,'railway-campaign',projected) as lease:
        return _run_impl(root,maximum_new_bundles=maximum_new_bundles,
                         native_jobs=native_jobs,state=state,lease=lease)


def _run_impl(root,*,maximum_new_bundles,native_jobs,state,lease):
    """Execute after admission; each stage checks the actual free-space floor."""
    from . import system_inventory,system_motion,system_selection,grammar_shell
    from engineering.performance import check_disk_reservation
    def check_space():
        if lease is not None:check_disk_reservation(lease)
    root=Path(root);spec=specification(root);epoch=source_epoch(root)
    if type(native_jobs) is not int or not 0<=native_jobs<=spec['maximum_native_jobs']:raise ValueError('Explicit bounded native job allowance required')
    if maximum_new_bundles is not None and (type(maximum_new_bundles) is not int or maximum_new_bundles<0):raise ValueError('Nonnegative resumable bundle budget required')
    contract=contract_identity(spec,epoch,root=root);folder=_ordinary_state_path(root/'build/coupled-railway'/contract if state is None else state);folder.mkdir(parents=True,exist_ok=True)
    _ordinary_state_path(folder);lock_path=folder/'lock'
    if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):raise ValueError('Coupled state lock is not an ordinary file')
    with lock_path.open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);_bind_state_source(folder,contract,epoch,root=root)
        codec_receipt=folder/'codec-executions'/(uuid.uuid4().hex+'.json')
        codec_execution=dict(schema='osr-coupled-codec-execution/1',contract_id=contract,
                             source_sha256=case_node_store.codec_source_identity(root),
                             executable_sha256=case_node_store.codec_identity(root)['osr-campaign-case-nodes'],
                             execution='started',storage_schema=case_node_store.SCHEMA)
        _write(codec_receipt,codec_execution)
        started=time.monotonic();bodies,decisions=generate_bodies();rows=[];bundles=[];new=0;reused=0
        check_space();native=_native_campaign(bodies,folder,native_jobs,root=root);check_space()
        for body in bodies:
            for family in spec['families']:
                for motor in bundle_adapter.motor_options()[:2 if family=='P1' else 1]:
                    bundle=bundle_adapter.materialize(body,family=family,motor_parameters=motor,root=root);bundles.append(bundle)
        if len(bundles)>spec['maximum_bundle_cases']:raise ValueError('Campaign exceeds physical bundle bound')
        pending=[]
        for bundle in bundles:
            check_space()
            if source_epoch(root)!=epoch:raise ValueError('Coupled source epoch changed before case dispatch')
            structure_context=_structure_context(native,bundle['body_candidate_id'])
            case_context=identity(dict(bundle_definition_id=bundle['definition_id'],structure_evidence=structure_context))
            path=case_node_store.path_for(folder/'cases',case_context)
            def check_case(cached):
                _validate_cached_row(cached,case_context,bundle,epoch)
                _verify_cached_stages(folder,cached,bundle,epoch,structure_context,root=root)
            if path.exists() or path.is_symlink():
                row=_read_cached_case(path,root=root)
                check_case(row)
                rows.append(row);reused+=1;continue
            row=case_node_store.recover(path,'case',check_case,root=root,maximum=_CASE_RECORD_MAX_BYTES)
            if row is not None:
                rows.append(row);reused+=1;continue
            if maximum_new_bundles is not None and new>=maximum_new_bundles or time.monotonic()-started>spec['maximum_seconds']:
                pending.append(dict(kind='bundle-evaluation',bundle_id=bundle['candidate_id'],bundle_definition_id=bundle['definition_id'],state='ready'));continue
            body=next(b for b in bodies if b['candidate_id']==bundle['body_candidate_id']);records=[]
            def stage(name,dependencies,fn):
                check_space()
                record,cache=_stage(folder,name,bundle,dependencies,epoch,fn,root=root);records.append(dict(stage=name,record_id=record['record_id'],request=record['request'],reused=cache));return record['output']
            inv=stage('installed_inventory',dict(body_definition_id=body['definition_id'],bundle_definition_id=bundle['definition_id']),
                lambda:system_inventory.evaluate(body,bundle_id=bundle['candidate_id'],source_root=root,comparison_context=spec['experiment'],
                    component_substitutions=bundle['component_substitutions'],extra_equipment_tasks=bundle['unweighed_architecture_equipment']))
            if abs(inv['known_accounted_mass_subtotal_kg']-bundle['mass']['accounted_tare_kg_per_car'])>1e-6:raise ValueError('Installed inventory and dynamics common-stock accounts differ')
            interfaces=stage('interfaces',dict(body_definition_id=body['definition_id'],bundle_definition_id=bundle['definition_id']),lambda:_interfaces(body,bundle))
            arch=stage('architecture',dict(bundle_definition_id=bundle['definition_id']),lambda:bundle_adapter.assess_architecture(bundle))
            motor=stage('propulsion',dict(bundle_definition_id=bundle['definition_id'],architecture_evaluation_id=arch['evaluation_id']),lambda:propulsion(bundle,arch))
            motion=stage('motion_and_braking',dict(bundle_definition_id=bundle['definition_id'],propulsion_evaluation_id=motor['evaluation_id']),lambda:system_motion.evaluate(bundle,available_map=None))
            civil=stage('civil',dict(bundle_definition_id=bundle['definition_id'],structure_context=structure_context),lambda:bundle_adapter.assess_civil(bundle))
            cost=stage('manufacturing_and_economics',dict(bundle_definition_id=bundle['definition_id'],upstream=[r['record_id'] for r in records]),lambda:economics(bundle,inv,arch,motor,motion,civil,root=root))
            row=dict(candidate_id=bundle['candidate_id'],body_candidate_id=body['candidate_id'],bundle_definition_id=bundle['definition_id'],case_context_id=case_context,structure_context=structure_context,family_id=bundle['family_id'],
                motor_component_id=bundle['propulsion_component_id'],accounted_mass=bundle['mass'],architecture_added_mass_unknown=bundle['unweighed_architecture_equipment'],
                stages=records,inventory_summary=_inventory_summary(inv),interfaces=interfaces,architecture=arch,propulsion=motor,motion=_compact_motion(motion),
                civil=civil,economics=cost,installed_mass_kg=None,complete_body_qualified=False,physical_journey_completed=False,**FLAGS)
            row['row_id']=identity(row);case_node_store.write(path,row,'case',root=root);rows.append(row);new+=1
            _write(folder/'journal.json',dict(contract_id=contract,completed_rows=[r['row_id'] for r in rows],new_bundles=new,reused_bundles=reused,pending_count=len(bundles)-len(rows),**FLAGS))
            if source_epoch(root)!=epoch:raise ValueError('Coupled physical sources changed during execution')
        partial=_partial_selection(rows,bodies,root)
        cost_comparisons=_cost_comparisons(rows)
        frontier=_frontier(rows,bodies,native)+pending+native.get('pending',[])
        result=dict(schema='osr-coupled-railway-campaign/1',contract_id=contract,specification=spec,source_sha256=epoch,bodies=bodies,
            bundles=bundles,rows=rows,executed_body_revisions=decisions,native=native,dependency_graph=EDGES,
            partial_quantity_comparison=partial,model_cost_comparisons=cost_comparisons,frontier=frontier,search_status='work-remaining',new_bundles=new,reused_bundles=reused,
            integrated_selection=None,selected_reference_changed=False,city_performance_packages_written=0,**FLAGS)
        if source_epoch(root)!=epoch:raise ValueError('Coupled source epoch changed before final sealing')
        result['campaign_id']=semantic_id(result)
        result['run_id']=_aggregate_identity(result)
        check_space()
        pointer=_write_aggregate(folder,result,root=root)
        _write(codec_receipt,dict(codec_execution,execution='completed',run_id=result['run_id'],
                                  campaign_id=result['campaign_id'],aggregate_sha256=pointer['aggregate_sha256'],
                                  new_bundles=new,reused_bundles=reused))
        return result


def _inventory_summary(value):
    names=('schema','candidate_id','bundle_id','body_candidate_id','body_definition_id','requirement_revision','comparison_scope_id',
        'accounted_empty_mass_kg','known_accounted_mass_subtotal_kg','complete_installed_mass_kg','complete_installed_CG_m','complete_installed_inertia_kg_m2',
        'geometry_coverage','supply_coverage','quantities','integrated_suitability','economic_winner','qualified_winner','selected_reference_changed','evaluation_id',*FLAGS)
    return {k:value[k] for k in names if k in value}


def _structure_context(native,body_id):
    return dict(body_candidate_id=body_id,method_status=native.get('method_status','not-run'),
        method_evaluation_ids=native.get('method_evaluation_ids',[]),
        native_body_evaluation_ids=[r['evaluation_id'] for r in native.get('body_results',[]) if r['body_candidate_id']==body_id],
        admission=native.get('body_admission',{}).get(body_id))


def _interfaces(body,bundle):
    from . import interface_graph
    r=interface_graph.assess(grammar_geometry.interface_projection(body))
    return dict(candidate_id=bundle['candidate_id'],body_candidate_id=body['candidate_id'],body_interfaces=r,
        architecture_interfaces='unknown' if bundle['unweighed_architecture_equipment'] else 'retained reference interfaces remain unqualified',
        complete_installed_clearance=False,**FLAGS)


def _native_campaign(bodies,folder,budget,*,root):
    from . import railway_native
    return railway_native.run(bodies,folder/'native',maximum_new_jobs=budget,root=root)


def _partial_selection(rows,bodies,root):
    from . import system_inventory
    # All unqualified bundles are retained. The only current Pareto question is
    # explicitly declared partial stock at the same reference service context.
    values=[]
    for body in bodies:
        case=next((r for r in rows if r['body_candidate_id']==body['candidate_id'] and r['family_id']=='P1'),None)
        if case is None:continue
        values.append(system_inventory.evaluate(body,bundle_id=case['candidate_id'],source_root=root,comparison_context=specification(root)['experiment']))
    return dict(known_stock_operations=system_inventory.pareto(values,objectives={'known_gross_structure_stock_kg':'min','manufacturing_occurrences':'min'}),
        lifecycle=system_inventory.pareto(values,objectives={'known_gross_structure_stock_kg':'min','installed_CAPEX_USD':'min'}),
        selection_purpose='Partial inventory comparison only; candidate model-cost ranges are reported separately and do not constitute an integrated selection')


def _cost_comparisons(rows):
    groups={}
    for row in rows:
        cost=row.get('economics',{}).get('model_cost')
        if not isinstance(cost,dict):continue
        basis=cost['corridor_basis']
        key=(cost['currency'],cost['estimate_date'],cost['assumption_id'],basis['offered_capacity_pphpd'],
            basis['target_headway_s'],basis['directional_route_m'],basis['trackways'],basis['stations'])
        groups.setdefault(key,[]).append(cost)
    result=[]
    for key,values in sorted(groups.items(),key=lambda item:str(item[0])):
        comparison=model_cost.compare(values)
        result.append(dict(common_service_context=dict(currency=key[0],estimate_date=key[1],assumption_id=key[2],
            offered_capacity_pphpd=key[3],target_headway_s=key[4],directional_route_m=key[5],trackways=key[6],stations=key[7]),
            comparison=comparison))
    return result


def _frontier(rows,bodies,native):
    tasks=[]
    control=specification()['numerical_refinement']
    for body in bodies:
        normals=sorted([r for r in native.get('body_results',[]) if r['body_candidate_id']==body['candidate_id'] and r['case'].startswith('normal') and r['raw'].get('numerical_validity')=='equilibrium_energy_confirmed_only'],key=lambda r:r['mesh_m'],reverse=True)
        if len(normals)<2:continue
        a,b=normals[-2:];ua,ub=a['raw']['maximum_displacements'],b['raw']['maximum_displacements']
        changes={k:abs(ua[k]-ub[k])/max(abs(ub[k]),1e-9) for k in ua}
        if max(changes.values())>control['trigger_relative_change']:
            next_mesh=b['mesh_m']*control['factor']
            tasks.append(dict(kind='unresolved-numerical-refinement',body_candidate_id=body['candidate_id'],state='implementation-or-resource-work-required',
                evidence_ids=[a['evaluation_id'],b['evaluation_id']],component_relative_changes=changes,proposed_next_mesh_m=next_mesh,
                next_job_within_current_mesh_domain=next_mesh>=control['minimum_mesh_m'],physical_failure_inferred=False,
                required=['Develop/benchmark feature-adaptive or local quadratic junction discretization','Explicitly assess next grid/resources and same-point/energy/stress trends',
                    'Continue the frontier under a supported model; a numerical invocation limit is not a structural rejection']))
    for body in bodies:
        tasks.append(dict(kind='installed-assembly-and-material-evidence',body_candidate_id=body['candidate_id'],state='open',
            required=['Locate every equipment/mount/fastener and reconcile actual mass/CG/inertia','Material/joint strength, hot-wet/fire, fatigue, buckling and physical correlation']))
    for row in rows:
        if row['family_id']!='P1':continue
        tasks.append(dict(kind='available-propulsion-and-journey',bundle_id=row['candidate_id'],state='open',motor_component_id=row['motor_component_id'],
            required=['Validated nonlinear moving force/normal-force/loss/current/voltage/thermal map','Measured independent brake/WSP/adhesion model','Same-bundle forward journey and faults']))
    tasks.append(dict(kind='whole-life-economics',state='model-cost-complete-for-declared-cases; evidence-replacement-open',
        completed=['Generate low/base/high Class C factory-gate, delivered, installed, energy, maintenance, renewal, recovery and reliability estimates in IQD for every executed candidate',
            'Calculate production-cell, tooling, civil support, haul and erection quantities from the same candidate bundle'],
        required=['Replace provisional unit rates with source-bound Iraqi supplier, process and site evidence as it becomes available',
            'Add surveyed alignment, geotechnical, access, land, utility and depot quantities before city budgeting',
            'Validate propulsion energy, operating duty, maintenance intervals, failures and replacement lives',
            'Review equal-service Pareto ranges; retain uncertainty and do not promote a candidate from model-cost ranking alone']))
    return tasks
