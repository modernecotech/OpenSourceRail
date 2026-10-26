"""Bounded failure-directed experiments across an extensible variable registry.

Input is a coordinator diagnosis envelope, not proof that a solver or hardware
is valid. It references the immutable evaluation and records its own content ID.
Plans do not contain fictitious physical candidates or fabricated performance.
An appropriate generator must materialize a proposal before evaluation dispatch.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
from . import design_variables as variables

PRODUCER='engineering/design_search/revision_planner.py'
FLAGS=variables.FLAGS
CLASSES=('functional','design-failure','system-incompatibility','advisory-target','numerical','model-domain','evidence-gap')
VALID=('valid','converged','mesh_confirmed')


def _sha(x):return isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x) is not None


def _strategy(name,domain,actions,why,counter_effects):
    return dict(strategy_id=name,domain=domain,actions=[dict(variable=n,direction=d,selected_value=None) for n,d in actions],
        rationale=why,counter_effects=counter_effects)


STRATEGIES={
 'body':[
    _strategy('redistribute-section-stock','body',[('body.sill.depth_m','redistribute'),('body.sill.wall_m','redistribute'),('body.section_family','compare')],
        'Change section proportions and distribute stock along load paths before assuming uniform added thickness is necessary',
        ['Package height and local buckling','floor/bogie/motor clearance','joints and fatigue','manufacturing and mass feedback']),
    _strategy('close-shell-loadpath','body',[('body.roof_floor_loadpath','replace'),('body.topology','compare'),('body.member_positions','redistribute')],
        'Investigate whether joined roof, floor and sidewall paths provide useful stiffness with less frame stock',
        ['Aperture loads and torsion','joint peel/slip','panel buckling and anisotropy','new topology native model and repair access']),
    _strategy('sandwich-and-oriented-faces','body',[('material.core_family','compare'),('body.core_thickness_m','redistribute'),('body.core_cell_direction','align-to-load'),('body.ply_angles_deg','redistribute')],
        'Compare foam, directional honeycomb, corrugated or hollow cores with load-aligned faces under a supported material model',
        ['Core shear/crushing, skin wrinkling and debonding','hot/wet/fire allowables','inserts, drainage and repair','complete mass and local sourcing']),
    _strategy('joint-and-hardpoint-loadpath','joints',[('joint.family','compare'),('joint.overlap_m','redistribute'),('joint.insert_geometry','replace'),('joint.fastener_layout','redistribute')],
        'Investigate transfer compliance and concentrated loads before adding global stock',
        ['Real preload, bearing, slip, peel and fatigue','assembly, corrosion and inspection','actual hardware mass','independent joint calibration']),
    _strategy('support-and-length-architecture','runninggear',[('runninggear.bogie_spacing_m','relocate'),('runninggear.layout','compare'),('body.car_length_m','compare')],
        'Change structural span, overhangs or articulation as separate physical families when local sizing is ineffective',
        ['Higher axle reactions and wheel dynamics','curve/swept envelope and ride','platform/coupler/accessibility changes','bogie maintenance and civil loads'])],
 'propulsion':[
    _strategy('primary-secondary-topology','propulsion',[('motor.topology','compare'),('motor.fin_geometry','replace'),('motor.tooth_backiron_geometry','redistribute')],
        'Compare a different physical magnetic circuit and passive secondary with topology-specific current and force models',
        ['New nonlinear moving model and independent benchmark','normal forces and air gap','secondary heating','installed motor/supply cost']),
    _strategy('winding-and-converter','propulsion',[('motor.winding_layout','replace'),('motor.conductor_area_m2','redistribute'),('motor.inverter_configuration','compare')],
        'Co-design winding, conductor and converter instead of increasing current in an invalid material model',
        ['Voltage/current limits and fill','copper/aluminium losses','insulation/cooling and installed mass','section handoff and control']),
    _strategy('powered-route-distribution','operations',[('motor.section_locations','relocate'),('service.powered_zone_positions','relocate'),('service.speed_m_s','compare')],
        'Change where propulsion acts and required speed under a separately identified route/service context',
        ['Journey, access and fleet effects','power supply and protection','installation cost and maintenance','coasting reach and recovery']),
    _strategy('traction-architecture','propulsion',[('motor.topology','compare'),('runninggear.driven_axles','redistribute'),('motor.onboard_energy_store','compare')],
        'Retain station-only launch as one hypothesis and compare onboard or hybrid traction where necessary',
        ['New bogie/drive/store geometry and installed mass','adhesion, charging, thermal and emergency limits','maintenance, rescue and total system cost'])],
 'braking':[
    _strategy('brake-distribution','braking',[('brake.actuator_distribution','redistribute'),('brake.independent_channels','compare'),('brake.disc_geometry','redistribute')],
        'Change realizable brake distribution and independent channels under actual axle loads and fault cases',
        ['Adhesion cannot be overcome by caliper force alone','disc/actuator mass and heat','WSP and independent supply','protected stopping envelope']),
    _strategy('protected-route-and-speed','operations',[('service.speed_m_s','compare'),('station.platform_and_berths','replace'),('service.headway_s','compare')],
        'Re-evaluate service and protected resource arrangements if braking cannot support the requested approach',
        ['Equal offered capacity and waiting time','fleet and access changes','safe overrun and occupied-berth faults','recovery and availability'])],
 'thermal':[
    _strategy('reduce-thermal-demand','services',[('services.insulation_and_solar_control','replace'),('material.glazing_grade','compare'),('fitout.roof_panel','replace')],
        'Reduce climate/solar/ventilation-associated thermal demand before assuming a larger cooling plant is optimal',
        ['Fire, weathering and roof hot strength','actual ventilation and occupant load','installed mass and repair','glazing retention and thermal movement']),
    _strategy('thermal-path-and-equipment','services',[('services.HVAC_architecture','compare'),('services.HVAC_routes','replace'),('services.cooling_and_wiring','replace'),('motor.cooling_layout','replace')],
        'Co-design heat paths, real ambient performance, equipment placement and repeated duty',
        ['Fans/pumps, filters, drainage and service access','electricity and auxiliary battery mass','single-unit failure','stationary hot-weather limits'])],
 'mass':[
    _strategy('body-stock-and-core','body',[('body.topology','compare'),('material.primary_grade','compare'),('material.core_family','compare')],
        'Compare structural efficiency and material/process alternatives using complete installed accounts',
        ['Qualified properties and structural modes','joining/repair/fire evidence','tooling and local supply','actual equipment must not disappear from the ledger']),
    _strategy('equipped-lightweight-modules','fitout',[('fitout.seat_bench_geometry','replace'),('fitout.floor_panel','replace'),('fitout.roof_panel','replace'),('fitout.door_leaf_and_drive','replace'),('material.glazing_grade','compare')],
        'Redesign actual seats, floor, roof, doors and glazing with their mounts, retainers and service access',
        ['Occupied loads, impact, fire and accessibility','thermal/acoustic performance','retention and removal paths','complete installed mass and manufacturing cost']),
    _strategy('bogie-and-formation-system','runninggear',[('runninggear.layout','compare'),('service.formation_cars','compare'),('service.seating_layout','replace')],
        'Compare vehicle support/layout and fleet/service effects rather than minimizing a car material subtotal',
        ['Axle loads, articulation and support structure','capacity, accessible routes and platforms','crowd verification remains applicable','fleet, headway and whole-life maintenance'])],
 'civil':[
    _strategy('civil-system','civil',[('civil.section_family','compare'),('civil.span_m','compare'),('civil.concrete_and_prestress','redistribute'),('civil.pier_foundation','compare')],
        'Compare complete section-span-support-foundation systems under actual moving reactions',
        ['Torsion, fatigue, gauge control and settlement','survey/geotechnical uncertainty','containment and emergency access','precast transport, lifts, erection and inspection']),
    _strategy('construction-and-service-jointly','manufacturing',[('manufacturing.process','compare'),('manufacturing.transport_erection','replace'),('station.platform_and_berths','replace')],
        'Change factory and station/erection arrangements when site logistics dominate the system outcome',
        ['Tooling, tolerances and curing/strength releases','crane radius, lifting stability and access','passenger/transfer service','priced supplier and labour coverage'])],
 'journey':[
    _strategy('route-power-and-formation','operations',[('service.powered_zone_positions','relocate'),('service.station_spacing_m','compare'),('service.speed_m_s','compare'),('service.formation_cars','compare')],
        'Investigate explicit booster, distributed-power, formation and service alternatives after a valid reach/resource failure',
        ['Changing stop spacing changes access service','installed powered length, electrical supply and maintenance','headway, fleet and passenger throughput','same-candidate mass and physical thrust maps']),
    _strategy('self-recovery-or-rescue','maintenance',[('service.recovery_strategy','compare'),('runninggear.driven_axles','redistribute'),('maintenance.recovery_resources','replace')],
        'Design how an off-zone stopped train is safely held, reached, coupled and moved',
        ['Drive/store or rescue equipment mass and cost','adhesion, degraded stopping and protected access','recovery time and availability','independent fault energy and evacuation'])],
 'general':[
    _strategy('resolve-coupled-interface-question','operations',[('service.seating_layout','investigate'),('station.transfer_access','investigate'),('manufacturing.joining_sequence','investigate')],
        'Identify the governing physical interfaces, broad function and missing capability before choosing a local parameter mutation',
        ['Explicit requirement and model provenance','Accessibility and passenger protection','Installed inventory and assembly consequences','New registered variables or evaluators where needed'])],
}


def failure_signature(evaluation,failure_class=None):
    return variables.identity(dict(failure_class=failure_class or evaluation['failure_class'],domain=evaluation.get('domain'),
        diagnosis=evaluation.get('diagnosis'),criterion_id=evaluation.get('criterion_id'),metric=evaluation.get('metric')))


def _group(e):
    text=' '.join(str(e.get(n,'')) for n in ('domain','diagnosis','metric')).lower()
    for key,words in [('thermal',('thermal','hvac','temperature','cooling')),('braking',('brak','adhesion','stopping')),
        ('journey',('journey','coast','reach','stall','berth','headway','recovery')),('mass',('mass','weight','fitout','glazing','bench','door-leaf')),
        ('civil',('civil','foundation','guideway','construction')),('propulsion',('motor','lim','propulsion','thrust','voltage','winding')),
        ('body',('body','joint','stiffness','deflection','structure','panel'))]:
        if any(word in text for word in words):return key
    return 'general'


def _classification(e):
    failure=e['failure_class'];validity=e.get('numerical_validity')
    if failure=='model-domain' or validity in ('outside-model-domain','out-of-domain'):return 'model-domain'
    if failure=='evidence-gap':return failure
    if e.get('execution')!='completed' or validity not in VALID:return 'numerical'
    if e.get('criterion_kind') in ('provisional-target','screening-hypothesis','design-hypothesis'):return 'advisory-target'
    return failure


def plan(candidate_id,evaluation,*,history=(),maximum_proposals=6,registry=None):
    """Prepare diverse bounded proposals; materialization and evidence follow.

    ``evaluation`` is a diagnosis envelope with immutable ``evaluation_id``,
    ``candidate_id``, ``requirement_revision``, ``execution``,
    ``numerical_validity``, ``failure_class``, ``domain`` and ``diagnosis``.
    An optional criterion_kind marks a provisional target. Prior history records
    reference candidate/evaluation IDs, a failure_signature, strategy_id and an
    explicit improved boolean; absent progress data is not invented.
    """
    e=deepcopy(evaluation);registry=variables.catalogue() if registry is None else deepcopy(registry)
    if not _sha(candidate_id) or e.get('candidate_id')!=candidate_id or not _sha(e.get('evaluation_id')):raise ValueError('Exact candidate/evaluation ancestry required')
    if not isinstance(e.get('requirement_revision'),str) or not e['requirement_revision']:raise ValueError('Separate requirement revision required')
    if e.get('failure_class') not in CLASSES or not isinstance(e.get('diagnosis'),str) or not e['diagnosis'] or not isinstance(e.get('domain'),str) or not e['domain']:raise ValueError('Typed failure diagnosis required')
    if e.get('hard_requirement') is True and (e['failure_class']=='advisory-target' or e.get('criterion_kind') in ('provisional-target','screening-hypothesis','design-hypothesis')):raise ValueError('A mandatory requirement cannot be relabelled an advisory target')
    if type(maximum_proposals) is not int or not 1<=maximum_proposals<=12 or len(history)>64:raise ValueError('One to twelve proposals and at most64 prior observations required')
    variables._checked_registry(registry)
    extensions=e.get('exploration_variable_ids',[])
    if not isinstance(extensions,list) or len(extensions)>8 or len(set(extensions))!=len(extensions) or any(n not in registry['variables'] for n in extensions):raise ValueError('At most eight unique registered exploration variables required')
    failure=_classification(e);signature=failure_signature(e,failure);matching=[]
    for row in history:
        if not isinstance(row,dict) or not _sha(row.get('candidate_id')) or not _sha(row.get('evaluation_id')) or type(row.get('improved')) is not bool:raise ValueError('History requires source evaluation identity and an explicit progress observation')
        if row.get('failure_signature')==signature:matching.append(row)
    stalled=len(matching)>=2 and all(r['improved'] is False for r in matching[-2:])
    tried={r.get('strategy_id') for r in matching if r['improved'] is False}
    proposed=[]
    def add(strategy,kind='coupled-design-experiment'):
        if len(proposed)>=maximum_proposals:return
        s=deepcopy(strategy);support=[];effects=set();checks=set();scopes=set()
        for a in s['actions']:
            d=registry['variables'].get(a['variable'])
            if d is None:raise ValueError('Planner variable requires registered descriptor: '+a['variable'])
            scopes.add(d['identity_scope']);effects.update(d['invalidates']);checks.update(d['requires_compatibility'])
            support.append(dict(variable=d['id'],descriptor_id=d['descriptor_id'],**d['model_support']))
        p=dict(schema='osr-adaptive-revision-proposal/1',parent_candidate_id=candidate_id,trigger_evaluation_id=e['evaluation_id'],
            parent_requirement_revision=e['requirement_revision'],diagnosis_input_id=variables.identity(e),failure_signature=signature,
            registry_id=registry['registry_id'],failure_class=failure,kind=kind,**s,
            identity_scopes=sorted(scopes),physical_candidate_id=None,materialization_status='not-generated',
            required_re_evaluations=sorted(effects),compatibility_checks=sorted(checks),adapter_requirements=support,
            requirement_review_required=kind=='criterion-review' or 'operational' in scopes,
            hard_requirement_relaxation_allowed=False,material_properties_invented=False,physical_improvement_claimed=False,
            expected_performance=None,complete_installed_mass_kg=None,complete_cost_USD=None,
            native_dispatch_allowed=False,maximum_native_jobs=4,maximum_runtime_s=600,**FLAGS)
        p['proposal_id']=variables.identity(p);proposed.append(p)
    if failure=='numerical':
        add(_strategy('repair-numerical-model','model',[('model.mesh_settings','investigate'),('model.solver_time_step_s','investigate'),('model.contact_joint_law','investigate')],
            'Resolve boundary conditions, mechanisms, discretization, residuals or resource interruption before physical ranking or redesign',
            ['Retain failed/interrupted runs','Independent force/work/modal benchmark','Same-physics resource revisions get separate evaluation identity']),kind='evaluator-development')
    elif failure=='model-domain':
        add(_strategy('extend-validated-model-domain','model',[('model.material_law','replace'),('model.contact_joint_law','investigate'),('model.material_temperature_data','investigate')],
            'Obtain and independently validate the appropriate nonlinear/contact/temperature model before trusting out-of-domain force or stiffness',
            ['No raised numerical-domain bound to manufacture a pass','Supplier/lot data remain unqualified until reviewed','New model must reproduce independent benchmarks']),kind='evaluator-development')
    elif failure=='evidence-gap':
        add(_strategy('resolve-material-and-interface-evidence','model',[('model.material_temperature_data','investigate'),('model.contact_joint_law','investigate')],
            'Obtain source-bound material/interface/installed-equipment evidence and design discriminating measurements',
            ['Actual specimen/lot identity, calibration and uncertainty','Unknown mass, cost and properties remain unknown','Measurements and reviewed qualification remain separate']),kind='measurement-and-data')
    else:
        group=_group(e)
        if failure=='advisory-target':
            add(_strategy('justify-functional-criterion','model',[('model.provisional_stiffness_target_m','review')],
                'Review the provisional target against actual door/glazing/floor/equipment clearances, structural response and independent evidence; an exceedance is advisory, not automatic rejection',
                ['No new target value chosen by the optimizer','Safety/strength/fatigue/accessibility obligations remain','Changing a target alone is not a physical improvement']),kind='criterion-review')
        if extensions:
            add(_strategy('investigate-registered-extensions',e['domain'],[(n,'investigate') for n in extensions],
                'Explore coordinator-identified registered variables whose interfaces and model-development needs are explicit',
                ['No inherited solver support or material properties','Materialize a new physical family where necessary','Re-evaluate every affected interface and retain unknown results']),kind='new-family-investigation')
        choices=list(STRATEGIES[group])
        if stalled:
            choices.sort(key=lambda r:(r['strategy_id'] in tried,r['strategy_id'] in ('redistribute-section-stock','winding-and-converter')))
            if group not in ('journey','civil'):choices+=STRATEGIES['journey']
        for strategy in choices:
            # Already unsuccessful local stock changes do not occupy the next
            # bounded batch while untried load-path/architecture changes exist.
            if stalled and strategy['strategy_id'] in tried:continue
            add(strategy)
    value=dict(schema='osr-adaptive-revision-plan/1',parent_candidate_id=candidate_id,trigger_evaluation_id=e['evaluation_id'],
        requirement_revision=e['requirement_revision'],diagnosis_input_id=variables.identity(e),failure_signature=signature,
        failure_class=failure,registry_id=registry['registry_id'],stagnation_detected=stalled,
        prior_matching_observations=len(matching),proposals=proposed,
        source_sha256={**variables.source_map(),PRODUCER:sha256(Path(__file__).read_bytes()).hexdigest()},
        integrated_suitability='unknown',selected_candidate_id=None,reference_default_changed=False,
        status='bounded-tasks-prepared' if proposed else 'new-capability-development-required',
        budget=dict(maximum_proposals=maximum_proposals,maximum_native_jobs_per_proposal=4,maximum_runtime_s_per_proposal=600),
        next_iteration='Materialize supported proposals, reject incompatibilities, rerun affected coupled evaluations and compare meaningful progress. On exhausted local options, commission a new family/evaluator or measurement task.',
        convergence_to_working_solution_guaranteed=False,**FLAGS)
    value['plan_id']=variables.identity(value);return value
