"""Coordinate architecture, adaptive proposals and generated physical bodies.

This is one dependency-driven execution path. A new body creates new physical
railway bundles and automatically invalidates the downstream mass, propulsion,
braking, civil, manufacturing and economic evaluations. Existing campaigns are
retained component adapters and historical evidence, not silently overwritten.
"""
from copy import deepcopy
from pathlib import Path
import fcntl,json,time,tomllib
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity,digest
from . import design_grammar as grammar,grammar_geometry,grammar_structure
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
    names=['railway_campaign','railway_bundle','railway_native','system_inventory','system_selection','system_motion','system_body','grammar_shell',
        'design_grammar','grammar_structure','grammar_geometry','interface_graph','failure_diagnosis','redesign_engine','revision_planner','design_variables','model_cost',
        'railway_architecture','architecture_demand','capabilities','requirement_policy','material_database','dfma','structural_families','joining_catalogue','wheel_motor']
    paths=[SPEC,'campaigns/whole-railway-architecture-search.toml',*[f'engineering/design_search/{n}.py' for n in names],
        'engineering/station_rail/common.py','engineering/station_rail/braking.py','engineering/station_rail/civil.py','engineering/station_rail/vehicle.py',
        'engineering/station_rail/electrical.py','engineering/station_rail/brief.toml','engineering/station_rail/__init__.py',
        'engineering/design_search/transient_lim.py','engineering/design_search/lim_materials.py','engineering/design_search/data/getdp-steel-generic.json',
        'engineering/station_rail/long_motor.py','engineering/station_rail/station_motor.py','engineering/station_rail/body_solid_frame.py',
        'docs/design-engine/ferrite-maglev/comfort-design/design.json.gz','docs/design-engine/ferrite-maglev/comfort-design/manifest.json',
        model_cost.RATE_DATA]
    return {n:digest(root/n) for n in paths}


def _write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix(path.suffix+'.pending');temp.write_bytes(encoded(value));temp.replace(path)


def _stage(folder,name,bundle,inputs,epoch,calculate,*,root=ROOT):
    if source_epoch(root)!=epoch:raise ValueError('Coupled source epoch changed before stage execution')
    request=dict(stage=name,bundle_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],inputs=inputs,source_sha256=epoch)
    key=identity(request);target=folder/'stages'/key
    if target.exists():
        r=json.loads(target.read_bytes())
        if r['request']!=request or r['record_id']!=identity({k:v for k,v in r.items() if k!='record_id'}):raise ValueError('Stage cache differs from exact candidate/dependency request')
        return r,True
    output=calculate()
    if source_epoch(root)!=epoch:raise ValueError('Coupled source epoch changed during stage execution')
    if isinstance(output,dict) and output.get('candidate_id',bundle['candidate_id'])!=bundle['candidate_id']:raise ValueError('Stage output belongs to another physical bundle')
    r=dict(schema='osr-coupled-stage-record/1',request=request,output=output,**FLAGS);r['record_id']=identity(r);_write(target,r);return r,False


def semantic_id(result):
    """Evidence identity excludes invocation/cache bookkeeping only."""
    def clean(value):
        if isinstance(value,dict):return {k:clean(v) for k,v in value.items() if k not in ('campaign_id','run_id','new_bundles','reused_bundles','new_native_jobs','reused_native_jobs','requested_native_jobs','reused')}
        if isinstance(value,list):return [clean(x) for x in value]
        return value
    return identity(clean(result))


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
    value=deepcopy(value)
    # Keep exact histories in immutable stage packets, index them in the report.
    def visit(node):
        if isinstance(node,dict):
            for key in list(node):
                if key=='trace' and isinstance(node[key],list):
                    rows=node.pop(key);node['trace_index']=dict(rows=len(rows),sha256=identity(rows))
                else:visit(node[key])
        elif isinstance(node,list):
            for x in node:visit(x)
    visit(value);return value


def run(root=ROOT,*,maximum_new_bundles=None,native_jobs=0,state=None):
    from . import system_inventory,system_motion,system_selection,grammar_shell
    root=Path(root);spec=specification(root);epoch=source_epoch(root)
    if type(native_jobs) is not int or not 0<=native_jobs<=spec['maximum_native_jobs']:raise ValueError('Explicit bounded native job allowance required')
    if maximum_new_bundles is not None and (type(maximum_new_bundles) is not int or maximum_new_bundles<0):raise ValueError('Nonnegative resumable bundle budget required')
    contract=identity(dict(specification=spec,source_sha256=epoch));folder=root/'build/coupled-railway'/contract if state is None else Path(state);folder.mkdir(parents=True,exist_ok=True)
    with (folder/'lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);started=time.monotonic();bodies,decisions=generate_bodies();rows=[];bundles=[];new=0;reused=0
        native=_native_campaign(bodies,folder,native_jobs,root=root)
        for body in bodies:
            for family in spec['families']:
                for motor in bundle_adapter.motor_options()[:2 if family=='P1' else 1]:
                    bundle=bundle_adapter.materialize(body,family=family,motor_parameters=motor,root=root);bundles.append(bundle)
        if len(bundles)>spec['maximum_bundle_cases']:raise ValueError('Campaign exceeds physical bundle bound')
        pending=[]
        for bundle in bundles:
            if source_epoch(root)!=epoch:raise ValueError('Coupled source epoch changed before case dispatch')
            structure_context=_structure_context(native,bundle['body_candidate_id'])
            case_context=identity(dict(bundle_definition_id=bundle['definition_id'],structure_evidence=structure_context))
            path=folder/'cases'/(case_context+'.json')
            if path.exists():
                row=json.loads(path.read_bytes())
                if row['case_context_id']!=case_context or row['bundle_definition_id']!=bundle['definition_id'] or row['row_id']!=identity({k:v for k,v in row.items() if k!='row_id'}):raise ValueError('Coupled case identity differs')
                rows.append(row);reused+=1;continue
            if maximum_new_bundles is not None and new>=maximum_new_bundles or time.monotonic()-started>spec['maximum_seconds']:
                pending.append(dict(kind='bundle-evaluation',bundle_id=bundle['candidate_id'],bundle_definition_id=bundle['definition_id'],state='ready'));continue
            body=next(b for b in bodies if b['candidate_id']==bundle['body_candidate_id']);records=[]
            def stage(name,dependencies,fn):
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
            row['row_id']=identity(row);_write(path,row);rows.append(row);new+=1
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
        result['campaign_id']=semantic_id(result);result['run_id']=identity(result);_write(folder/'invocations'/(result['run_id']+'.json'),result);_write(folder/'result.json',result);return result


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
