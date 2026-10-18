"""Couple manufactured units, handling, delivery, immutable QA scope and ranking."""
from copy import deepcopy
import csv
import math

from engineering.twin_workflow import core
from . import civil_kit,construction_stage,delivery_simulation,operation_graph,processes,qa_traveller


def service_response(kit,mesh=4):
    from engineering.civil_exploration.model import System
    candidate=deepcopy(kit['candidate']);study=deepcopy(kit['study'])
    bridge_mass=sum(u['mass_kg'] for u in kit['units'] if not u['category'].startswith('station-'))
    gross_addition=max(0.,bridge_mass-kit['mass_ledger']['canonical_installed_study_mass_kg'])
    candidate['mass_allowances']['superimposed_dead_kg_m_per_track']+=gross_addition/40
    study['mass_allowances']=deepcopy(candidate['mass_allowances'])
    result=System(candidate,study,study['ground_scenarios'][0],mesh).static_envelope()
    return dict(response=result,candidate=candidate,study=study,bridge_kit_mass_kg=bridge_mass,
        conservative_service_mass_kg=kit['mass_ledger']['canonical_installed_study_mass_kg']+gross_addition,
        added_kit_dead_load_kg=gross_addition,
        scope='Existing elastic reference bridge/pier/soil-spring model; gross extra kit mass propagated, no mass-removal credit. Station independent supports, local cap/bearing/connection resistance and dynamics remain unverified.')


def quoted_cost(kit,scheduled,quotes=None):
    """Supply-only unit prices plus installation rates; no factory double charge.

    Optional inputs are scenario/quotation records, not authenticated acceptance.
    Every unit revision and every cost category must be present before a total.
    """
    if quotes is None:return dict(total_usd=None,missing=['revision-specific supply quotes','site labour, cranes, transport, mobilisation, temporary works, road disruption and maintenance'],accepted=False)
    if not scheduled.get('passed'):return dict(total_usd=None,missing=['feasible delivery scenario'],accepted=False)
    plant_names=('crane','truck','mixer','concrete_pump','excavator')
    lump_sums=('mobilisation_usd','temporary_works_usd','road_disruption_usd','maintenance_present_value_usd')
    rates=('site_person_hour_usd',*[name+'_hour_usd' for name in plant_names],*lump_sums)
    if quotes.get('currency')!='USD' or not quotes.get('basis_reference'):raise ValueError('USD comparison cost basis required')
    missing=[];supply=0.
    for unit in kit['units']:
        record=quotes.get('unit_supply_only',{}).get(unit['revision'],quotes.get('unit_supply_only',{}).get(unit['id']))
        if not record or record.get('unit_revision')!=unit['revision'] or not record.get('basis_reference'):
            missing.append(unit['id']);continue
        value=record.get('usd')
        if type(value) not in (int,float) or not math.isfinite(value) or value<0:raise ValueError('finite nonnegative unit price required')
        supply+=value
    for key in rates:
        value=quotes.get(key)
        if value is None:missing.append(key)
        elif type(value) not in (int,float) or not math.isfinite(value) or value<0:raise ValueError('finite nonnegative installation rate required')
    if missing:return dict(total_usd=None,missing=missing,accepted=False)
    plant=scheduled['resources']
    total=supply+scheduled['onsite_person_hours']*quotes['site_person_hour_usd']
    total+=sum(plant[name]['busy_resource_hours']*quotes[name+'_hour_usd'] for name in plant_names)
    total+=sum(quotes[key] for key in lump_sums)
    return dict(total_usd=total,supply_only_usd=supply,basis_reference=quotes['basis_reference'],missing=[],accepted=False,
        scope='Input cost records only; supplier authenticity, tax, currency/date validity, scope and commercial acceptance still require review; factory work is included in supply prices once')


def evaluate(parameters,output,basis=None):
    civil_kit.validate(parameters);kit=civil_kit.build(parameters['variables'],basis)
    physical=kit['physical_contract'];graph=operation_graph.evaluate(kit['operation_graph']);handling=construction_stage.handling(kit)
    jobs=construction_stage.tasks(kit);scheduled=delivery_simulation.schedule(jobs,kit['basis']['capacities']);stages=construction_stage.verify_schedule(kit,jobs,scheduled)
    response=service_response(kit)
    checks=dict(manufacturing_mass_balance=abs(kit['mass_ledger']['mass_balance_residual_kg'])<1e-6,
        complete_component_plan=all(kit['component_coverage'][k] for k in ('piles','foundation_caps','piers','pier_caps','decks','bearings','track_support','services')),
        qa_plan_coverage=all(t['required']==qa_traveller.requirements(u) for u,t in zip(kit['units'],kit['travellers'])),
        finite_service_response=all(math.isfinite(v) for v in response['response']['envelope'].values() if type(v) in (int,float)),
        conservative_service_mass=response['conservative_service_mass_kg']>=response['bridge_kit_mass_kg']-1e-6,
        resource_schedule=scheduled['passed'])
    checks.update({'kit-contract/'+k:v for k,v in civil_kit.validate_kit(kit).items()})
    checks.update({'handling/'+k:v for k,v in handling['checks'].items()});checks.update({'construction/'+k:v for k,v in stages['checks'].items()})
    # The same reference service limits apply, but lifting is evaluated on the
    # actual manufacturing/erection units rather than an unsplit 20m beam.
    limits=[]
    for metric,limit in kit['study']['research_limits'].items():
        value=handling['maximum_lift_mass_kg'] if metric=='suspended_mass_kg' else response['response']['envelope'].get(metric)
        state='unknown' if limit is None or value is None else 'passed' if value<=limit else 'failed'
        limits.append(dict(metric=metric,value=value,limit=limit,state=state,approved=False))
        if state!='unknown':checks['reference-limit/'+metric]=state=='passed'
    assignments={u['id']:('purchased-section-fastener' if u['process']=='purchased' else 'sheet-duct' if u['category'] in {'service','station-canopy'} else 'profile-cut-weld' if u['process']=='steel-fabrication' else 'precast-reusable') for u in kit['units']}
    inventory=[dict(id=u['id'],bounds_m=u['bounds_m'],mass_kg=u['mass_kg']) for u in kit['units']]
    process=processes.evaluate('precast-reusable',parts=inventory,part_profiles=assignments,graph=kit['operation_graph'],
        contract=physical,observations=dict(suspended_mass_kg=handling['maximum_lift_mass_kg']),output=output)
    process['part_coverage']='Manufactured units assigned, with exact unit-to-CAD-region map; fabrication detail and process qualification remain open'
    checks.update({'manufacturing/'+k:v for k,v in process['checks'].items()})
    timed={r['id']:r for r in scheduled.get('tasks',[])};events=[]
    for u in kit['units']:
        start=timed.get(u['id']+'/factory-test',{}).get('end_h');end=timed.get(u['id']+'/transport',{}).get('start_h')
        if start is not None and end is not None:events.extend([(start,1),(end,-1)])
    stock=peak=0
    for time,delta in sorted(events,key=lambda r:(r[0],r[1])):stock+=delta;peak=max(peak,stock)
    checks['factory_finished_goods_capacity']=peak<=kit['basis']['factory']['maximum_finished_stock_units']
    cost=quoted_cost(kit,scheduled,kit['basis'].get('quotes'))
    metrics=dict(mass_kg=kit['mass_ledger']['installed_study_mass_kg'],manufactured_unit_count=len(kit['units']),
        maximum_lift_mass_kg=handling['maximum_lift_mass_kg'],total_lifts=handling['lift_count'],
        temporary_plant_mass_kg=sum(u['mass_kg'] for u in kit['temporary_units']),
        offsite_mass_fraction=sum(u['mass_kg'] for u in kit['units'] if u['offsite'])/kit['mass_ledger']['installed_study_mass_kg'],
        onsite_wet_concrete_m3=sum(u.get('concrete_m3',0.) for u in kit['units'] if not u['offsite']),
        onsite_operation_count=sum(j['site'] for j in jobs),scenario_onsite_person_hours=scheduled.get('onsite_person_hours'),
        scenario_factory_person_hours=scheduled.get('factory_person_hours'),scenario_work_at_height_hours=scheduled.get('working_at_height_person_hours'),
        scenario_delivery_hours=scheduled.get('makespan_h'),factory_finished_goods_peak_units=peak,
        scenario_transport_vehicle_hours=scheduled.get('resources',{}).get('truck',{}).get('busy_resource_hours'),
        site_bulk_concrete_deliveries=sum('/mixer-' in j['id'] for j in jobs),
        scenario_cost_usd=cost['total_usd'],required_planned_tests=sum(len(tests) for t in kit['travellers'] for tests in t['required'].values()),
        covered_planned_tests=sum(len(tests) for t in kit['travellers'] for tests in t['required'].values()) if checks['qa_plan_coverage'] else 0)
    process['metrics'].update(metrics);process['metrics']['inspection_effort_person_hours']=sum(t['person_hours'] for t in scheduled.get('tasks',[]) if t['id'].endswith(('/factory-test','/site-accept')))
    process['metrics']['comparison_basis_sha256']=kit['basis_sha256']
    process['metrics']['required_test_scope_sha256']=core.digest(dict(procedures=qa_traveller.REQUIRED,components=kit['basis']['mandatory_coverage'],station=parameters['variables']['station_package']))
    process['metrics']['planned_test_coverage_complete']=checks['qa_plan_coverage']
    held=['driven-pile ground applicability'] if parameters['variables']['foundation_route']=='precast-driven' and kit['basis'].get('driven_pile_ground_verified') is not True else []
    failures=[key for key,passed in checks.items() if not passed]
    for name,value in [('physical-contract',physical),('civil-kit',kit),('handling-stages',handling),('delivery-tasks',jobs),('delivery-schedule',scheduled),
        ('construction-verification',stages),('qa-travellers',kit['travellers']),('cost-input-review',cost),('reference-service',response),('reference-limits',limits)]:
        core.write(output/(name+'.json'),value,exclusive=True)
    bottlenecks=delivery_simulation.bottlenecks(jobs,kit['basis']['capacities'],scheduled)
    core.write(output/'delivery-bottlenecks.json',bottlenecks,exclusive=True)
    physics=dict(candidate=response['candidate'],study=response['study'],response=response['response'],kit=kit,
        source_scope=response['scope'],staged_checks=stages,handling=handling)
    core.write(output/'physics.json',physics,exclusive=True)
    with (output/'manufacturing-units.csv').open('w',newline='') as stream:
        fields=['unit_id','revision','category','process','offsite','study_mass_kg','defined_geometry_mass_kg','unresolved_mass_allowance_kg','physical_region_ids','required_support_ids','supply_only_quote_usd','qa_status']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for u in kit['units']:writer.writerow(dict(unit_id=u['id'],revision=u['revision'],category=u['category'],process=u['process'],offsite=u['offsite'],
            study_mass_kg=u['mass_kg'],defined_geometry_mass_kg=u['defined_mass_kg'],unresolved_mass_allowance_kg=u['allocated_mass_kg'],
            physical_region_ids='|'.join(u['physical_part_ids']),required_support_ids='|'.join(u['support_ids']),supply_only_quote_usd='',qa_status='unexecuted; acceptance open'))
    return dict(study_pass=not failures and not held,checks=checks,failed_checks=failures,held_checks=held,metrics=metrics,
        assessment=dict(context_id=parameters['context_id'],candidate_family='civil-manufactured-kit/'+parameters['variables']['architecture'],
            variables=parameters['variables'],geometry=dict(parts=[dict(id=p['id']) for p in physical['parts']]),manufactured_units=[dict(id=u['id']) for u in kit['units']]),
        manufacturing_process=process,physical_contract_sha256=core.sha(output/'physical-contract.json'),physics_sha256=core.sha(output/'physics.json'),
        needs=[dict(item_id='qualified-civil-kit-delivery-inputs',required='Bind measured production, actual crane/radius/ground and transport capacities, unit-specific connection/temporary works/strength designs, accepted railway loads/durability and authenticated QA/quotes before delivery or cost acceptance.')],
        open_evidence=kit['unknown']+handling['unknown']+stages['held'],bottlenecks=bottlenecks,
        scope='Equal-function manufactured/erected kit research scenario. QA plans and simulated locks are unexecuted; cheapest option and engineering/physical/manufacturing acceptance remain unresolved.',**core.FLAGS)


def benchmark(output,basis=None):
    output.mkdir(parents=True,exist_ok=False);results=[];fingerprints=[]
    for architecture in civil_kit.ARCHITECTURES:
        folder=output/architecture;folder.mkdir()
        p=dict(context_id=civil_kit.CONTEXT,variables=civil_kit.defaults(architecture))
        result=evaluate(p,folder,basis);core.write(folder/'result.json',result,exclusive=True)
        kit=core.read(folder/'civil-kit.json',maximum=20_000_000)
        fingerprints.append(dict(architecture=architecture,train_sha256=core.digest(kit['study']['train']),ground_sha256=core.digest(kit['study']['ground_scenarios']),
            durability_sha256=core.digest(kit['basis']['durability']),acceptance_sha256=core.digest(kit['study']['research_limits']),
            comparison_basis_sha256=kit['basis_sha256']))
        results.append(dict(architecture=architecture,study_pass=result['study_pass'],checks=result['checks'],metrics=result['metrics'],
            physical_contract_sha256=result['physical_contract_sha256'],scope=result['scope']))
    comparison=dict(schema='osr-civil-kit-delivery-comparison/1',alternatives=results,
        identical_basis_sha256=core.digest(basis or core.read(civil_kit.BASIS)),comparison_fingerprints=fingerprints,
        same_train_ground_durability=all(len({r[key] for r in fingerprints})==1 for key in ('train_sha256','ground_sha256','durability_sha256','acceptance_sha256','comparison_basis_sha256')),
        cheapest='unresolved until complete revision-specific quotations and installation cost inputs exist',
        scope='Conditional declared scenario, not measured production, accepted railway structure or executable erection instruction',**core.FLAGS)
    core.write(output/'comparison.json',comparison,exclusive=True);return comparison
