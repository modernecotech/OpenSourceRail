"""Complete a bounded demand-to-outline study using existing engineering kernels.

The reference budget is immutable. A study changes its service hypotheses and
recalculates the fleet, launch equipment, production and whole-life costs. No
candidate, timetable, equipment or business record is released by this path.
"""
from copy import deepcopy
from math import fsum
from pathlib import Path
import json
import time

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.development_baseline import selection
from engineering.design_search import line_benchmark as budget
from engineering.design_search import line_benchmark_civil, model_cost
from . import maturity, reference_library, service_search

PRODUCER = 'engineering/outline/coordinator.py'
FLAGS = {**budget.FLAGS, 'movement_authority': False, 'business_records_submitted': False}
DEFAULT_BRIEF = dict(route_km=30., stations=12, peak_demand_pphpd=4000.,
    planning_occupancy=.85, maximum_headway_s=300., maximum_one_way_minutes=45.,
    operating_hours_per_day=18., availability_target=.99,
    planning_availability_assumption=.99,
    demand_source='declared-planning-example; replace with surveyed city demand')
DEFAULT_VARIABLES = dict(headways_s=[120.,150.,180.,210.,240.,300.],
    speeds_kmh=[50.,60.,72.], accelerations_m_s2=[.6,.8,1.,1.2],
    dwell_s=[35.], headway_quantum_s=10., maximum_screened=128)


def seal(value, key='evaluation_id'):
    value[key] = identity(value)
    return value


def merge_sources(*maps):
    result={}
    for mapping in maps:
        for name,sha in mapping.items():
            if name in result and result[name]!=sha:
                raise ValueError('Mixed source epochs for '+name)
            result[name]=sha
    return result


def prepare(root=ROOT):
    """Load/verify source-bound quantities once, outside the candidate loop."""
    root=Path(root); spec=budget.specification(root)
    vehicle=selection.load(root)['vehicle']; vc=budget._vehicle_cost(root,vehicle)
    assumptions=model_cost.assumptions(root)
    names=(PRODUCER,maturity.PRODUCER,service_search.PRODUCER,
        'engineering/outline/__init__.py','engineering/outline/reference_library.py',
        'engineering/outline/rea_adapter.py')
    sources=merge_sources(budget.sources(root),vc['source_sha256'],vehicle['source_sha256'],
        {n:digest(root/n) for n in names})
    return dict(spec=spec,vehicle=vehicle,vehicle_cost=vc,assumptions=assumptions,sources=sources)


def _cost(case, mode, context, civil):
    spec=deepcopy(context['spec']); spec['requirements']=case['request']['requirements']
    spec['design']=case['request']['design']
    service=case['service']; vc=context['vehicle_cost']; r=spec['requirements']; fx=spec['currency']['iqd_per_usd']
    capital,production=budget._capital(spec,context['vehicle'],vc,service,civil,context['assumptions'],mode)
    life,operating=budget._lifecycle(spec,service,vc,capital,context['assumptions'],mode)
    cap={x:round(fsum(z['costs_iqd'][x] for z in capital),2) for x in budget.CASES}
    whole={x:round(cap[x]+fsum(z['costs_iqd'][x] for z in life),2) for x in budget.CASES}
    scopes={scope:{x:round(fsum(z['costs_iqd'][x] for z in capital+life if z['scope']==scope),2)
        for x in budget.CASES} for scope in model_cost.SCOPES}
    if any(scopes[s]['base']<=0 for s in model_cost.SCOPES):
        raise ValueError('Every outline must account for all fourteen cost scopes')
    return seal(dict(schema='osr-outline-cost/1',service_case_id=case['case_id'],
        mechanism=mode,service_evaluation_id=service['evaluation_id'],capital_lines=capital,
        lifecycle_lines=life,scope_totals_iqd=scopes,installed_capital_iqd=cap,
        installed_capital_usd={x:cap[x]/fx for x in budget.CASES},
        price_per_route_km_usd={x:cap[x]/fx/r['route_km'] for x in budget.CASES},
        whole_life_npv_usd={x:whole[x]/fx for x in budget.CASES},
        production=production,operating=operating,estimate_class='C',
        terminal_resource_planning=case.get('terminal_resource_planning'),**FLAGS))


def _outline(case, cost, screen, context):
    vehicle=context['vehicle']; vc=context['vehicle_cost']; service=case['service']
    # Reserve sensitivities are design-stage bounds, not measured installed mass.
    mass=vehicle['mass']; reserve=case['request']['design']['added_vehicle_mass_kg_per_car']
    bounds={x:mass['located_material_kg']+mass['unlocated_or_reference_account_kg']*f+reserve
        for x,f in vc['mass_reserve_sensitivity']['case_factors'].items()}
    assumptions=[dict(id='installed-mass',bounds=bounds,
        source=vc['mass_reserve_sensitivity']['result_id'],
        purpose='Vary only residual accounts by existing 0.8/1.0/1.2 factors; retain located stock and new interface reserve once. Service and price results use the nominal mass, not a certified bound.'),
        dict(id='equipment-envelope',bounds={'choices':['17 x 2.65 x 4.2 m provisional car envelope']},
        source='Reference body length and width; declared 4.2 m height envelope',
        purpose='Outline interface envelope; complete equipment fit, clearances and access during detailing'),
        dict(id='launch-capability',bounds={'choices':['required-force design hypothesis']},
        source='Conditional S-curve and functional launch equipment cost package',
        purpose='Complete the planning calculation; obtain an available-force, protection and thermal map'),
        dict(id='service-availability',bounds=[screen['requirements_contract']['planning_availability_assumption']]*2,
        source='Declared planning assumption, not measured reliability',purpose='Demand capacity screen'),
        dict(id='production-route',bounds={'choices':['provisional factory and purchasing routes']},
        source=vc['cost_estimate_id'],purpose='Calculate production quantities and costs before procurement')]
    outline_id=identity(dict(service_case_id=case['case_id'],cost_evaluation_id=cost['evaluation_id'],
        requirements_id=screen['requirements_id']))
    constraints=[dict(key='declared-functional-service',status='pass',required_at='outline',
        explanation='Demand, journey and necessary planning bounds pass under recorded assumptions'),
        dict(key='available-launch-force',status='unknown',required_at='outline',assumption_id='launch-capability',
            explanation='Required force is calculated; actual machinery has not been selected or proven'),
        dict(key='complete-installed-mass-CG',status='unknown',required_at='detail',
            explanation='Accounted mass is bounded; complete installation, CG, inertia and attachment design remain open'),
        dict(key='structural-braking-fire-accessibility-and-independent-release',status='unknown',required_at='release',
            explanation='Existing qualification workflows and authenticated tests remain mandatory')]
    record=dict(outline_id=outline_id,requirements_id=screen['requirements_id'],
        envelopes=[dict(id='carbody-envelope',dimensions_m=[17.,2.65,4.2],assumption_id='equipment-envelope')],
        bounded_mass_kg=bounds,costs={**cost['installed_capital_usd'],'currency':'USD','source_class':'calculated-Class-C'},
        manufacturing_routes=[dict(kind='source-bound-provisional-vehicle-routes',source_cost_estimate_id=vc['cost_estimate_id']),
            dict(kind='precast-factory-delivery-installation',source='line_benchmark_civil')],
        assumptions=assumptions,service_constraints=constraints)
    assessment=maturity.assess(record,root=context['root'])
    delivery=seal(dict(schema='osr-outline-delivery-draft/1',outline_id=outline_id,
        requirements_id=screen['requirements_id'],physical_candidate_id=None,
        reference_vehicle_candidate_id=vehicle['candidate_id'],
        source_vehicle_cost_estimate_id=vc['cost_estimate_id'],
        provisional_account_BOM=[dict(source_line_id=line['line_id'],name=line['line_key'],
            source_account_quantities=line['quantity'],fleet_multiplier=service['total_trainsets'],
            disabled=1,physical_part_definition_complete=False) for line in vc['lines']],
        installed_quantity_takeoff=[dict(key=line['key'],scope=line['scope'],quantity=line['quantity'],
            source_cost_line_id=line['line_id']) for line in cost['capital_lines']],
        provisional_routings=record['manufacturing_routes'],
        workforce=dict(production_shifts=2,civil_shifts=2,
            operations_shifts=service['shift_info']['operations_shifts_per_day'],
            operator_workplaces_per_shift=cost['production']['workplaces'],
            assembly_bays=cost['production']['assembly_bays'],
            precast_moulds=cost['production']['moulds'],
            named_staff_or_machine_schedule=False),
        construction_precedence=[dict(operation=op,requires=parents) for op,parents in (
            ('survey-and-foundation-design',[]),('factory-production-and-QA',[]),
            ('foundation-pier-and-bearing-installation',['survey-and-foundation-design']),
            ('transport-and-span-erection',['factory-production-and-QA','foundation-pier-and-bearing-installation']),
            ('rail-services-and-launch-installation',['transport-and-span-erection']),
            ('integration-inspection-and-independent-release',['rail-services-and-launch-installation']))],
        ERPNext=dict(disabled=1,production_orders=[],external_transactions_performed=False),
        Frappe_HR=dict(submitted=False,named_workers_assigned=False),
        controls=dict(movement_authority=False,commissioned=False),**FLAGS),'draft_id')
    return dict(outline_id=outline_id,service_case_id=case['case_id'],mechanism=cost['mechanism'],
        physical_candidate_id=None,reference_vehicle_candidate_id=vehicle['candidate_id'],
        outline_input=record,maturity=assessment,cost=cost,service=service,delivery_draft=delivery,
        design=case['request']['design'],requirements=case['request']['requirements'],
        remaining_tasks=assessment.get('next_tasks',[]),**FLAGS)


def evaluate(brief=None, variables=None, root=ROOT):
    started=time.perf_counter(); root=Path(root)
    context=prepare(root); context['root']=root
    brief=deepcopy(DEFAULT_BRIEF if brief is None else brief)
    variables=deepcopy(DEFAULT_VARIABLES if variables is None else variables)
    screen=service_search.screen(brief,variables,context['spec'],context['vehicle'],root=root)
    eligible=[c for c in screen['cases'] if c['eligible_for_costing']]
    civil_spec=deepcopy(context['spec']['requirements'])
    civil_spec.update(route_km=brief['route_km'],stations=brief['stations'])
    civil=line_benchmark_civil.evaluate(civil_spec,context['spec']['design'],context['vehicle'],root=root)
    costs=[]; pending_costs=[]; by_case={c['case_id']:c for c in eligible}
    for case in eligible:
        # Every costed case was independently replayed by the service screen.
        for mode in case['eligible_mechanisms']:
            cost=_cost(case,mode,context,civil)
            if case.get('terminal_resource_planning',{}).get('cost_additional_positions',0):
                # Do not rank a layout needing unpriced extra terminal structures.
                pending_costs.append(dict(service_case_id=case['case_id'],mechanism=mode,
                    reason='Additional protected terminal positions need a revised geometry and cost model'))
                continue
            costs.append(cost)
    # Keep a complete compact cost index. Detailed ledgers are retained for the
    # best whole-life case of each mechanism. Other cases remain in the index.
    best=[]
    for mode in budget.MODES:
        group=[c for c in costs if c['mechanism']==mode]
        if group: best.append(min(group,key=lambda c:(c['whole_life_npv_usd']['base'],c['evaluation_id'])))
    outlines=[_outline(by_case[c['service_case_id']],c,screen,context) for c in best]
    best_outline=min(outlines,key=lambda o:(o['cost']['whole_life_npv_usd']['base'],o['outline_id'])) if outlines else None
    index=[dict(cost_evaluation_id=c['evaluation_id'],service_case_id=c['service_case_id'],mechanism=c['mechanism'],
        installed_capital_usd=c['installed_capital_usd'],price_per_route_km_usd=c['price_per_route_km_usd'],
        whole_life_npv_usd=c['whole_life_npv_usd']) for c in costs]
    library=reference_library.owned_pilot(root=root)
    sources=merge_sources(context['sources'],civil['source_sha256'],screen['source_sha256'],
        library.get('source_sha256',{}),*(o['maturity']['source_sha256'] for o in outlines))
    if any(digest(root/n)!=sha for n,sha in sources.items()):raise ValueError('Outline input sources changed during evaluation')
    value=seal(dict(schema='osr-demand-outline-study/1',brief=brief,variables=variables,
        requirements_id=screen['requirements_id'],service_screen=screen,civil=civil,
        cost_index=index,outlines=outlines,pending_costs=pending_costs,
        recommended_outline_id=best_outline['outline_id'] if best_outline else None,
        selection_purpose='next-outline-for-detailing; minimum base whole-life cost among bounded passing cases',
        selection_is_physical_adoption=False,reference_library=library,
        production_policy='Two production and civil shifts; two operations shifts for 18 h, three for 24 h',
        source_sha256=sources,**FLAGS))
    # Noncanonical elapsed time remains outside the reproducible evaluation.
    return value,dict(elapsed_s=time.perf_counter()-started,costed_cases=len(costs),
        detailed_outlines=len(outlines),native_solver_calls=0,source_loads=1,
        geometry_or_safety_qualification=False)


def summary(value):
    rows=[]
    for row in value['outlines']:
        service,cost=row['service'],row['cost']; req=row['requirements']; design=row['design']
        rows.append(dict(outline_id=row['outline_id'],mechanism=row['mechanism'],
            maturity=row['maturity']['outline_acceptance'],headway_s=req['headway_s'],
            speed_kmh=design['speed_m_s']*3.6,acceleration_m_s2=design['acceleration_m_s2'],
            journey_minutes=service['one_way_s']/60,trainsets=service['total_trainsets'],
            installed_capital_usd=cost['installed_capital_usd'],
            price_per_route_km_usd=cost['price_per_route_km_usd'],whole_life_npv_usd=cost['whole_life_npv_usd'],
            assumptions=row['outline_input']['assumptions'],tasks=row['maturity'].get('next_tasks',[])))
    return dict(schema='osr-demand-outline-summary/1',evaluation_id=value['evaluation_id'],
        requirements_id=value['requirements_id'],brief=value['brief'],
        recommended_outline_id=value['recommended_outline_id'],outlines=rows,
        counters=value['service_screen']['counters'],costed_cases=len(value['cost_index']),
        source_sha256=value['source_sha256'],**FLAGS)


def run(output,brief=None,variables=None,root=ROOT):
    output=Path(output)
    if output.exists():raise ValueError('Use a fresh immutable outline output directory')
    value,timing=evaluate(brief,variables,root)
    output.mkdir(parents=True)
    for name,record in [('result.json',value),('summary.json',summary(value)),('performance.json',timing)]:
        (output/name).write_bytes(encoded(record))
    manifest=seal(dict(schema='osr-demand-outline-manifest/1',evaluation_id=value['evaluation_id'],
        source_sha256=value['source_sha256'],files_sha256={n:digest(output/n) for n in ('result.json','summary.json','performance.json')},**FLAGS),'manifest_id')
    (output/'manifest.json').write_bytes(encoded(manifest))
    return manifest


def publish(state,output,root=ROOT):
    """Publish compact reproducible inputs and summary; keep full runs private."""
    state=Path(state); output=Path(output)
    verified=verify(state,root=root,replay=True)
    value=json.loads((state/'result.json').read_bytes())
    if output.exists():raise ValueError('Fresh compact publication directory required')
    output.mkdir(parents=True)
    (output/'inputs.json').write_bytes(encoded(dict(brief=value['brief'],variables=value['variables'])))
    (output/'summary.json').write_bytes(encoded(summary(value)))
    manifest=seal(dict(schema='osr-outline-compact-publication/1',evaluation_id=value['evaluation_id'],
        source_sha256=value['source_sha256'],canonical_result_sha256=verified['files_sha256']['result.json'],
        files_sha256={n:digest(output/n) for n in ('inputs.json','summary.json')},
        replay_command='python -m engineering.outline run --brief inputs.json --output FRESH_DIRECTORY',
        bulky_outputs_policy='Full result, cost ledgers and execution logs stay in the immutable private run or external artifact storage; regenerate from these inputs.',**FLAGS),'manifest_id')
    (output/'manifest.json').write_bytes(encoded(manifest))
    return manifest


def verify_compact(output,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m.get('schema')!='osr-outline-compact-publication/1' or m.get('manifest_id')!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Compact outline manifest differs')
    if set(m['files_sha256'])!={'inputs.json','summary.json'} or any(digest(output/n)!=sha for n,sha in m['files_sha256'].items()):raise ValueError('Compact outline payload differs')
    if any(m.get(k) is not False for k in FLAGS):raise ValueError('Compact outline cannot authorize release')
    if any(digest(Path(root)/n)!=sha for n,sha in m['source_sha256'].items()):raise ValueError('Compact outline sources differ')
    inputs=json.loads((output/'inputs.json').read_bytes())
    value,_=evaluate(inputs['brief'],inputs['variables'],root)
    if (value['evaluation_id']!=m['evaluation_id'] or encoded(summary(value))!=(output/'summary.json').read_bytes()
            or identity(value)!=m['canonical_result_sha256']):
        # identity(value) is SHA256 of the same newline-terminated encoded bytes.
        raise ValueError('Compact outline calculation replay differs')
    return m


def verify(output,root=ROOT,*,replay=True):
    output=Path(output); manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('Outline manifest identity differs')
    if set(manifest['files_sha256'])!={'result.json','summary.json','performance.json'}:raise ValueError('Unexpected outline artifact paths')
    if any(digest(output/n)!=sha for n,sha in manifest['files_sha256'].items()):raise ValueError('Outline payload differs')
    if any(digest(Path(root)/n)!=sha for n,sha in manifest['source_sha256'].items()):raise ValueError('Outline source epoch differs')
    value=json.loads((output/'result.json').read_bytes())
    if value.get('evaluation_id')!=manifest['evaluation_id'] or value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):raise ValueError('Outline evaluation identity differs')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Outline cannot authorize physical or business release')
    if encoded(summary(value))!=(output/'summary.json').read_bytes():raise ValueError('Outline summary differs')
    if replay:
        actual,_=evaluate(value['brief'],value['variables'],root)
        if encoded(actual)!=encoded(value):raise ValueError('Outline calculation replay differs')
    return manifest
