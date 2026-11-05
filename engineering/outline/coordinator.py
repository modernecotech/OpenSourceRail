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

from engineering.station_rail import ROOT, propulsion_layout, station_motor, civil as civil_geometry
from engineering.station_rail.common import digest, encoded, identity
from engineering.development_baseline import selection,propulsion_policy
from engineering.design_search import line_benchmark as budget
from engineering.design_search import line_benchmark_civil, model_cost
from . import approaches, maturity, reference_library, service_search, supply_economics

PRODUCER = 'engineering/outline/coordinator.py'
_LOADED={PRODUCER:digest(__file__),**{
    Path(module.__file__).resolve().relative_to(Path(ROOT).resolve()).as_posix():digest(module.__file__)
    for module in (approaches,maturity,reference_library,service_search,budget,
        line_benchmark_civil,model_cost,selection,propulsion_policy,supply_economics,
        propulsion_layout,station_motor,civil_geometry)}}
FLAGS = {**budget.FLAGS, 'movement_authority': False, 'business_records_submitted': False}
DEFAULT_BRIEF = dict(route_km=30., stations=12, peak_demand_pphpd=4000.,
    planning_occupancy=.85, maximum_headway_s=300., maximum_one_way_minutes=45.,
    operating_hours_per_day=18., availability_target=.99,
    planning_availability_assumption=.99,
    demand_source='declared-planning-example; replace with surveyed city demand')
DEFAULT_VARIABLES = dict(headways_s=[120.,150.,180.,240.,300.],
    speeds_kmh=[50.,60.,72.], accelerations_m_s2=[.8,1.2],service_decelerations_m_s2=[.6,.9],
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
    root=Path(root)
    if any(digest(root/name)!=sha for name,sha in _LOADED.items()):
        raise ValueError('Loaded outline sources changed; restart the calculation worker')
    spec=budget.specification(root)
    vehicle=selection.load(root)['vehicle']; vc=budget._vehicle_cost(root,vehicle)
    assumptions=model_cost.assumptions(root)
    names=(PRODUCER,maturity.PRODUCER,service_search.PRODUCER,
        'engineering/outline/__init__.py','engineering/outline/reference_library.py',
        'engineering/outline/rea_adapter.py',approaches.PRODUCER,approaches.POLICY)
    sources=merge_sources(_LOADED,budget.sources(root),vc['source_sha256'],vehicle['source_sha256'],supply_economics.sources(root),
        {n:digest(root/n) for n in names})
    return dict(spec=spec,vehicle=vehicle,vehicle_cost=vc,assumptions=assumptions,sources=sources)


def _cost(case, mode, context, civil):
    spec=deepcopy(context['spec']); spec['requirements']=case['request']['requirements']
    spec['design']=case['request']['design']
    service=case['service']; vc=context['vehicle_cost']; r=spec['requirements']; fx=spec['currency']['iqd_per_usd']
    supply=supply_economics.evaluate_case(spec,context['vehicle'],vc,service,civil,context['assumptions'],mode,
        context['pricing_scenario'],cache=context['_supply_cache'],root=context['root'])
    capital,production=supply['capital'],supply['production']
    life,operating=supply['lifecycle'],supply['operating']
    cap={x:round(fsum(z['costs_iqd'][x] for z in capital),2) for x in budget.CASES}
    whole={x:round(cap[x]+fsum(z['costs_iqd'][x] for z in life),2) for x in budget.CASES}
    scopes={scope:{x:round(fsum(z['costs_iqd'][x] for z in capital+life if z['scope']==scope),2)
        for x in budget.CASES} for scope in model_cost.SCOPES}
    if any(scopes[s]['base']<=0 for s in model_cost.SCOPES):
        raise ValueError('Every outline must account for all fourteen cost scopes')
    return seal(dict(schema='osr-outline-cost/1',service_case_id=case['case_id'],
        reference_vehicle_candidate_id=context['vehicle']['candidate_id'],
        mechanism=mode,service_evaluation_id=service['evaluation_id'],capital_lines=capital,
        lifecycle_lines=life,scope_totals_iqd=scopes,installed_capital_iqd=cap,
        installed_capital_usd={x:cap[x]/fx for x in budget.CASES},
        price_per_route_km_usd={x:cap[x]/fx/r['route_km'] for x in budget.CASES},
        whole_life_npv_usd={x:whole[x]/fx for x in budget.CASES},
        production=production,operating=operating,estimate_class='C',
        terminal_resource_planning=case.get('terminal_resource_planning'),
        pricing_scenario=context['pricing_scenario'],supply_analysis=supply,**FLAGS))


def _outline(case, cost, screen, context):
    vehicle=context['vehicle']; vc=cost['supply_analysis'].get('vehicle',{}).get('vehicle_cost',context['vehicle_cost']); service=case['service']
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
    installation=_installation(case,cost,context)
    geometry=_outline_geometry(case,cost,installation,context)
    outline_id=identity(dict(service_case_id=case['case_id'],cost_evaluation_id=cost['evaluation_id'],
        requirements_id=screen['requirements_id'],
        physical_installation_id=installation['physical_installation_id'],
        installation_evaluation_id=installation['evaluation_id'],geometry_id=geometry['geometry_id']))
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
        physical_installation_id=installation['physical_installation_id'],
        source_propulsion_installation_evaluation_id=installation['evaluation_id'],
        outline_geometry_id=geometry['geometry_id'],
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
        propulsion_installation=installation,outline_geometry=geometry,
        physical_candidate_id=None,reference_vehicle_candidate_id=vehicle['candidate_id'],
        outline_input=record,maturity=assessment,cost=cost,service=service,delivery_draft=delivery,
        design=case['request']['design'],requirements=case['request']['requirements'],
        remaining_tasks=assessment.get('next_tasks',[]),**FLAGS)


def _installation(case,cost,context):
    """Reconcile one departure-site geometry with the whole-corridor cost ledger.

    ``departure_sites`` already counts the two service directions and terminal
    topology. Multiplying it by another direction factor would double stock.
    Receiving is assigned to independent onboard braking, not an unpriced LIM.
    """
    vehicle=context['vehicle'];service=case['service'];mode=cost['mechanism']
    if cost.get('evaluation_id')!=identity({k:v for k,v in cost.items() if k!='evaluation_id'}) or any(cost.get(k) is not False for k in FLAGS):
        raise ValueError('Sealed unaccepted propulsion cost record required')
    if (mode not in budget.MODES or cost['service_case_id']!=case['case_id']
            or cost['reference_vehicle_candidate_id']!=vehicle['candidate_id']
            or cost['service_evaluation_id']!=service['evaluation_id']
            or service['evaluation_id']!=identity({k:v for k,v in service.items() if k!='evaluation_id'})):
        raise ValueError('Mixed service, mechanism or reference vehicle in propulsion installation')
    sites=service['departure_sites']
    if type(sites) is not int or sites<=0:
        raise ValueError('Explicit positive departure-site count required')
    stroke=service['jerk_launch_distance_m'];coverage=service['jerk_full_train_fin_launch_envelope_m']
    keys=('LIM-primary-installed' if mode=='compact-launch-LIM' else 'launch-contact-and-return-hardware',)
    lines=[r for r in cost['capital_lines'] if r['key'] in keys]
    if len(lines)!=1:raise ValueError('One matching propulsion quantity ledger required')
    line=lines[0];priced=line['quantity']
    if line.get('line_id')!=identity({k:v for k,v in line.items() if k!='line_id'}):
        raise ValueError('Sealed propulsion quantity line required')
    if priced['sites']!=sites:raise ValueError('Propulsion site quantity differs from service')
    spec=context['spec'];rotary=spec['rotary']
    if mode=='compact-launch-LIM':
        unit=station_motor.definition()
        layout=propulsion_layout.layout(candidate_id=vehicle['candidate_id'],
            body_candidate_id=vehicle['body_candidate_id'],passive_interface_id=vehicle['propulsion_component_id'],
            sections=[dict(section_id='departure-launch',start_m=0.,length_m=coverage,role='launch')],
            module_length_m=unit['addressed_module_length_m'],module_policy='whole-modules',
            magnetic_period_m=unit['wavelength_m'],directions=1,independent_branches_per_direction=1,
            faces_per_track=2,root=context['root'])
        quantities=propulsion_layout.quantities(layout,root=context['root'])
        per_site=layout['per_direction'];installed=per_site['installed_length_m']
        expected=dict(requested_launch_envelope_m_per_site=coverage,
            installed_length_m_per_site=installed,metres=sites*installed,
            modules_per_site=per_site['full_modules'],module_length_m=unit['addressed_module_length_m'],
            stator_face_module_joints_per_site=per_site['stator_face_module_joints'],
            stock_proxy_kg_per_m=unit['bare_primary_stock_kg_per_m'])
        if any(priced.get(k)!=v for k,v in expected.items()):
            raise ValueError('LIM geometry and priced module/length/joint quantities differ')
        physical_id=quantities['installed_primary_candidate_id']
        geometry=dict(layout=layout,quantities=quantities,
            geometry_scope='One departure launch site; direction already included in corridor site count')
        totals=dict(departure_sites=sites,installed_length_m=sites*installed,
            full_modules=sites*per_site['full_modules'],
            stator_face_module_joints=sites*per_site['stator_face_module_joints'],
            copper_kg=sites*installed*unit['copper_kg_per_m'],
            steel_kg=sites*installed*unit['primary_steel_kg_per_m'],
            bare_primary_stock_kg=sites*installed*unit['bare_primary_stock_kg_per_m'])
        sources={**layout['source_sha256'],**quantities['source_sha256']}
    else:
        if mode=='cable-capstan':
            expected=dict(stroke_m=stroke,rope_m_per_site=rotary['rope_length_per_stroke']*stroke)
            geometry=dict(mode=mode,launch_stroke_m=stroke,
                full_train_contact_envelope_m=coverage,continuous_coupling=True,
                rope_length_m_per_site=expected['rope_m_per_site'],return_guide_length_m_per_site=stroke,
                connection='Persistent grip through launch stroke; release and return remain unqualified',
                grip_drum_anchor_guard_package_per_site=1,
                rope_diameter_m=None,rope_material_grade=None)
            totals=dict(departure_sites=sites,launch_stroke_m=sites*stroke,
                rope_length_m=sites*expected['rope_m_per_site'],return_guide_length_m=sites*stroke,
                grip_drum_anchor_guard_packages=sites)
        else:
            from math import ceil
            contacts=ceil(coverage/rotary['roller_spacing_m'])
            expected=dict(bank_m_per_site=coverage,contacts_per_site=contacts)
            geometry=dict(mode=mode,full_train_contact_envelope_m=coverage,bank_length_m=coverage,
                common_drive=True,contact_spacing_m=rotary['roller_spacing_m'],contacts_per_site=contacts,
                contact_positions=dict(start_m=0.,spacing_m=rotary['roller_spacing_m'],count=contacts),
                motor_per_roller_assumed=False,roller_diameter_m=None,
                contact_placement_and_load_sharing_qualified=False)
            totals=dict(departure_sites=sites,installed_common_drive_bank_m=sites*coverage,
                roller_contacts=sites*contacts)
        if any(priced.get(k)!=v for k,v in expected.items()):
            raise ValueError('Rotary launch geometry and priced contact/return quantities differ')
        geometry['physical_dimensions_are_outline_hypotheses']=True
        physical_id=identity(dict(geometry=geometry,reference_vehicle_candidate_id=vehicle['candidate_id'],
            body_candidate_id=vehicle['body_candidate_id'],passive_interface_id=vehicle['propulsion_component_id']))
        sources={PRODUCER:digest(Path(context['root'])/PRODUCER)}
    value=dict(schema='osr-outline-propulsion-installation/1',mechanism=mode,
        physical_installation_id=physical_id,reference_vehicle_candidate_id=vehicle['candidate_id'],
        service_evaluation_id=service['evaluation_id'],cost_evaluation_id=cost['evaluation_id'],
        geometry=geometry,departure_sites=sites,corridor_quantities=totals,
        cost_quantity_line_id=line['line_id'],cost_quantities_reconciled=True,
        direction_counting='Already included in departure_sites; no second direction multiplier',
        source_sha256=sources,receiving_propulsion_selected=False,
        independent_onboard_braking_required=True,
        available_force_N=None,electrical_thermal_qualified=False,actual_installed_mass_kg=None,
        physical_candidate_scope='Provisional propulsion geometry; complete installed hardware remains unresolved',
        selection_scope='Candidate outline only; never the mandatory development installation',**FLAGS)
    return seal(value)


def _outline_geometry(case,cost,installation,context):
    """Compact repeated geometry from the actual priced definitions, not CAD claims."""
    vehicle=context['vehicle'];v=vehicle['physical_definition']['vehicle']
    r,d=case['request']['requirements'],case['request']['design']
    c=cost['supply_analysis'].get('civil',{}).get('civil',context['_civil_reference'])
    beam=c['beam'];section=civil_geometry.section(beam['family']);q=c['quantities']
    platform=next(z['quantity'] for z in cost['capital_lines'] if z['key']=='station-platform-structures')
    if (platform['boarding_edges']!=case['service']['boarding_edges']
            or platform['platform_area_m2']!=platform['boarding_edges']*d['platform_length_m']*d['platform_width_m']):
        raise ValueError('Station geometry and priced platform quantities differ')
    car=dict(source_body_candidate_id=vehicle['body_candidate_id'],
        source_geometry_definition_id=vehicle['physical_definition']['geometry_definition_id'],
        body_length_m=v['body_length_m'],body_width_m=v['body_width_m'],
        complete_installed_height_m=None,planning_envelope_height_m_hypothesis=4.2,
        envelope_assumption_id='equipment-envelope',floor_top_above_rail_m=v['floor_top_above_rail_m'],
        source_stock_occurrences=len(vehicle['geometry_parts']),installed_equipment_layout_complete=False)
    formation=dict(car_module=car,cars_per_train=v['cars'],coupling_gap_m=v['coupling_gap_m'],
        length_m=case['service']['train_length_m'],
        instance_pattern=dict(origin='first car centre',longitudinal_pitch_m=v['body_length_m']+v['coupling_gap_m'],count=v['cars']),
        purchased_trainsets=case['service']['total_trainsets'])
    guideway=dict(physical_civil_component_id=beam['physical_civil_component_id'],family=beam['family'],
        module=dict(span_m=beam['span_m'],section_dimensions=section['dimensions'],
            coordinate_frame='Local beam x along span; z=0 at beam top. Offset to top of rail is unresolved.',
            top_of_beam_to_rail_m=None,prestress_strands=beam['prestress_strands']),
        independent_track_lines=2,priced_span_count=q['span_count'],
        repeat_pattern=dict(pitch_m=beam['span_m'],count_per_track=q['span_count']//2),
        priced_supports=q['independent_supports'],pier_height_m=d['pier_height_m'],
        relative_track_centres_m=None,foundation_dimensions=None,
        declared_counted_span_mass_kg=beam['total_counted_span_mass_kg'],
        complete_installed_civil_mass=False,source_civil_evaluation_id=c['evaluation_id'])
    stations=dict(count=r['stations'],chainages_m=[i*r['route_km']*1000/(r['stations']-1) for i in range(r['stations'])],
        platform_module=dict(length_m=d['platform_length_m'],width_m=d['platform_width_m'],
            thickness_m=None,height_above_rail_m=None,clearance_to_vehicle_m=None),
        priced_boarding_edges=platform['boarding_edges'],priced_platform_area_m2=platform['platform_area_m2'],
        drive_geometry=installation['geometry'],drive_relative_origin='Departure launch origin of each outgoing site',
        independent_onboard_braking_required=True,evacuation_and_accessibility_qualified=False)
    value=dict(schema='osr-preliminary-corridor-geometry/1',
        coordinate_frame='Synthetic straight corridor; x is route chainage in metres. No surveyed world CRS or track-centre offsets are claimed.',
        world_crs=None,route_length_m=r['route_km']*1000,vehicle=formation,guideway=guideway,stations=stations,
        physical_installation_id=installation['physical_installation_id'],
        geometry_scope='Repeated source vehicle stock, priced guideway modules, platform envelopes and candidate launch geometry',
        detailed_CAD_generated=False,native_solver_jobs=0,source_sha256={
            PRODUCER:digest(Path(context['root'])/PRODUCER),civil_geometry.PRODUCER:digest(Path(context['root'])/civil_geometry.PRODUCER)},**FLAGS)
    return seal(value,'geometry_id')


def evaluate(brief=None, variables=None, root=ROOT, *, pricing_scenario=None):
    started=time.perf_counter(); root=Path(root)
    context=prepare(root); context['root']=root
    pricing_scenario=pricing_scenario or supply_economics.policy(root)['default_scenario']
    if pricing_scenario not in supply_economics.SCENARIOS:raise ValueError('Unknown pricing scenario')
    context['pricing_scenario']=pricing_scenario;context['_supply_cache']={}
    brief=deepcopy(DEFAULT_BRIEF if brief is None else brief)
    variables=deepcopy(DEFAULT_VARIABLES if variables is None else variables)
    screen=service_search.screen(brief,variables,context['spec'],context['vehicle'],root=root)
    eligible=[c for c in screen['cases'] if c['eligible_for_costing']]
    civil_spec=deepcopy(context['spec']['requirements'])
    civil_spec.update(route_km=brief['route_km'],stations=brief['stations'])
    civil=line_benchmark_civil.evaluate(civil_spec,context['spec']['design'],context['vehicle'],root=root)
    context['_civil_reference']=civil
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
    policy=approaches.catalogue(root=root)
    pending_approaches=[approaches.propose(dict(name=row['name'],approach=row['id'],
        transport_function='Meet the same declared transport goal',concept=row['scope']),
        requirements_id=screen['requirements_id'],root=root)
        for row in policy['policy']['approaches'] if row['id']!='station-launch-wheel-supported']
    sources=merge_sources(context['sources'],civil['source_sha256'],screen['source_sha256'],
        library.get('source_sha256',{}),policy['source_sha256'],*(o['maturity']['source_sha256'] for o in outlines),
        *(c['supply_analysis']['source_sha256'] for c in costs),
        *(o['propulsion_installation']['source_sha256'] for o in outlines))
    if any(digest(root/n)!=sha for n,sha in sources.items()):raise ValueError('Outline input sources changed during evaluation')
    value=seal(dict(schema='osr-demand-outline-study/1',brief=brief,variables=variables,
        requirements_id=screen['requirements_id'],service_screen=screen,civil=civil,
        pricing_scenario=pricing_scenario,supply_policy=supply_economics.policy(root),
        cost_index=index,outlines=outlines,pending_costs=pending_costs,
        recommended_outline_id=best_outline['outline_id'] if best_outline else None,
        selection_purpose='next-outline-for-detailing; minimum base whole-life cost among bounded passing cases',
        selection_is_physical_adoption=False,reference_library=library,
        active_propulsion_policy=selection.load(root).get('active_propulsion_policy'),
        approach_policy=policy,unassessed_approaches=pending_approaches,
        global_optimum_established=False,
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
            propulsion_installation=row['propulsion_installation'],outline_geometry=row['outline_geometry'],
            assumptions=row['outline_input']['assumptions'],tasks=row['maturity'].get('next_tasks',[])))
    return dict(schema='osr-demand-outline-summary/1',evaluation_id=value['evaluation_id'],
        requirements_id=value['requirements_id'],brief=value['brief'],
        pricing_scenario=value['pricing_scenario'],
        approach_policy_id=value['approach_policy']['catalogue_id'],
        evaluated_scope=value['approach_policy']['policy']['current_calculator_scope'],
        unassessed_approach_count=len(value['unassessed_approaches']),global_optimum_established=False,
        recommended_outline_id=value['recommended_outline_id'],outlines=rows,
        counters=value['service_screen']['counters'],costed_cases=len(value['cost_index']),
        source_sha256=value['source_sha256'],**FLAGS)


def run(output,brief=None,variables=None,root=ROOT,*,pricing_scenario=None):
    output=Path(output)
    if output.exists():raise ValueError('Use a fresh immutable outline output directory')
    value,timing=evaluate(brief,variables,root,pricing_scenario=pricing_scenario)
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
    (output/'inputs.json').write_bytes(encoded(dict(brief=value['brief'],variables=value['variables'],pricing_scenario=value['pricing_scenario'])))
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
    value,_=evaluate(inputs['brief'],inputs['variables'],root,pricing_scenario=inputs.get('pricing_scenario'))
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
        actual,_=evaluate(value['brief'],value['variables'],root,pricing_scenario=value.get('pricing_scenario'))
        if encoded(actual)!=encoded(value):raise ValueError('Outline calculation replay differs')
    return manifest
