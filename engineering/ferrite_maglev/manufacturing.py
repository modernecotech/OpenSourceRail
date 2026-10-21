"""Quantity-based maglev planning and process routes; no supplier quote or release.

Rates are explicitly project assumptions in cost-rates.json. Equipment references
establish capability/origin only. They do not validate a price or an OSR part.
"""
from copy import deepcopy
import json
import math
from pathlib import Path

INPUT = Path(__file__).with_name('data')/'cost-rates.json'


def load():
    from .model import positive
    data=json.loads(INPUT.read_text())
    if data['schema']!='osr-maglev-process-rates/1' or data['costs_are_quotes'] is not False:
        raise ValueError('unquoted process rate schema required')
    for name,value in data['rates'].items():positive(value,name)
    for name,value in data['scenario_multipliers'].items():positive(value,name)
    return data


def row(identity,quantity,unit,rate,process,*,origin='unverified',local_operation=False):
    from .model import positive
    positive(quantity,identity,zero=True);positive(rate,identity+' rate')
    return dict(id=identity,quantity=quantity,unit=unit,unit_rate_usd=rate,
        amount_usd=quantity*rate,process=process,input_origin=origin,
        local_operation_candidate=local_operation,imported_input_usd=None,
        rate_evidence='project planning assumption; unquoted',accepted=False)


def vehicle(c,costs,ferrite,battery,*,cars=None,hardware_target=None,scenario='base'):
    from .model import positive
    cars=c['vehicle']['cars_per_train'] if cars is None else cars
    if type(cars) is not int or cars<1:raise ValueError('positive integer cars required')
    positive(ferrite,'ferrite');positive(battery,'battery')
    r=costs['rates'];factor=costs['scenario_multipliers'][scenario]
    # Finished body systems and mass-derived ferrite are distinct scopes. The
    # magnetic integration row excludes raw ferrite and the protected battery.
    specs=[('body-and-passenger-systems',cars,'car',r['body_and_passenger_systems_per_car'],'GFRP sandwich panels, sized hardpoints and joints; doors, glazing, interior and acceptance checks',True),
        ('ferrite',cars*ferrite,'kg',r['ferrite_per_kg'],'qualify stock blocks; retain in replaceable cartridges',True),
        ('magnetic-modules',cars,'car',r['magnetic_equipment_per_car'],'support/guidance carriers/cores/coils/drives; station main traction excluded',True),
        ('battery-pack',cars*battery,'kWh',r['battery_pack_per_kwh'],'cell receipt; protected pack integration and electrical test',True),
        ('capture-and-brake',cars,'car',r['capture_brake_per_car'],'fabricate and verify capture, landing and emergency brake hardware',True),
        ('hvac-and-auxiliary',cars,'car',r['hvac_auxiliary_per_car'],'install cooling, ventilation and low-voltage services',True),
        ('coupling-and-gangway',max(cars-1,0),'interface',r['coupling_gangway_per_interface'],'fit structural coupling and accessible passenger gangway',True),
        ('train-control-and-protection',1,'train',r['train_control_per_train'],'integrate SBCs, independent protection, isolated I/O and software tests',True),
        ('assembly-and-test',cars*r['assembly_test_hours_per_car'],'labour-hour',r['labour_per_hour'],'controlled assembly, dimensional survey, static and functional tests',True)]
    rows=[row(i,q,u,p*factor,process,local_operation=local) for i,q,u,p,process,local in specs]
    if hardware_target is not None:
        positive(hardware_target,'magnetic hardware target')
        item=next(x for x in rows if x['id']=='magnetic-modules')
        item.update(unit_rate_usd=hardware_target/cars,amount_usd=hardware_target,rate_evidence='unqualified train-level optimisation target; unquoted')
    subtotal=sum(x['amount_usd'] for x in rows)
    reserve=subtotal*r['vehicle_integration_reserve_fraction']
    return dict(cars=cars,rows=rows,priced_scope_subtotal_usd=subtotal,
        integration_reserve_usd=reserve,total_allowance_usd=subtotal+reserve,
        excluded=['complete evacuation devices and lifetime maintenance','development and qualification','factory CAPEX','warranty and initial spares','tax/duty/freight and finance'],
        architecture='station-lsm-and-coast',onboard_main_traction_included=False,station_main_traction_included=False,
        complete_factory_gate_price_usd=None,local_value_added_fraction=None,costs_are_quotes=False)


def civil(c,costs,*,area=None,span=None,walkway_area=.12,scenario='base'):
    from .model import positive
    from . import geometry
    r=costs['rates'];factor=costs['scenario_multipliers'][scenario]
    area=c['civil']['narrow_box_screen']['derived_concrete_area_m2'] if area is None else positive(area,'beam area')
    span=c['civil']['reference_span_m'] if span is None else positive(span,'span')
    positive(walkway_area,'walkway area',zero=True)
    box=c['civil']['narrow_box_screen'];infill_each=.4
    infill_area=2*infill_each*max(0,(box['outer_width_m']-2*box['web_thickness_m'])*(box['outer_depth_m']-2*box['flange_thickness_m']))/span
    concrete=(area+infill_area+walkway_area)*2000
    supports=1000/span
    rail_mass=geometry.guideway_quantities(span)['magnetic_rail_line_mass_kg_m']*2000
    reinforcement=concrete*r['reinforcement_kg_per_m3']
    # Itemised target packages retain explicit site/connection uncertainty, not
    # a ground design; no reduction proportional to train mass is granted.
    specs=[('structural_supply',concrete,'m3',r['concrete_cast_cure_per_m3'],'batch, cast, cure and demould beam/walkway concrete'),
        ('reinforcement',reinforcement,'kg',r['reinforcement_fabricated_per_kg'],'cut/bend cage; position prestressing and verify cover'),
        ('passive_rail_supply',rail_mass,'kg',r['reaction_steel_finished_per_kg'],'cut/machine reaction faces; retain, align and survey'),
        ('supports',supports,'shared support',r['support_foundation_per_unit'],'investigate ground; construct foundation, pier and cap'),
        ('walkway_brackets',2000 if walkway_area else 0,'direction-m',r['walkway_attachment_per_m'],'fit fallback access attachments; removal requires evacuation approval'),
        ('transport',2*supports,'beam delivery',r['delivery_per_beam'],'transport full span on surveyed access route'),
        ('erection',2*supports,'beam lift',r['erection_per_beam'],'lift, locate, secure and inspect beam'),
        ('temporary',supports,'support position',r['temporary_per_support'],'temporary stability and ground bearing works'),
        ('installation',2000,'direction-m',r['alignment_joint_per_m'],'connect and align joints/reaction faces'),
        ('night',1,'route-km',r['access_allowance_per_km'],'possession/access planning and restricted-hour allowance'),
        ('qa',1,'route-km',r['qa_per_km'],'survey, material/connection records and independent checks'),
        ('relocation',1,'route-km',r['utility_allowance_per_km'],'provisional ordinary utility-diversion allowance; major diversions unpriced'),
        ('traffic',1,'route-km',r['traffic_allowance_per_km'],'maintain road and pedestrian access during construction')]
    rows=[row(i,q,u,p*factor,process,local_operation=True) for i,q,u,p,process in specs]
    from . import station_structure
    dimensions=station_structure.civil(c,span=span)
    support_components=[dict(id=i,quantity=q,unit=u,amount_usd=amount*factor,unit_rate_usd=(amount/q)*factor,rate_is_target=True,accepted=False) for i,q,u,amount in [('foundation-excavation',1,'favourable ordinary-site package',10500.),('column',dimensions['supports']['hollow_column_m3'],'m3',3500.),('cap',dimensions['supports']['cap_m3'],'m3',2800.),('connections-bearings-grout',1,'package',1800.),('support-transport-erection',1,'package',2500.),('local-inspection-handover',1,'package',900.)]]
    return dict(support_components_per_unit=support_components,support_total_usd=sum(x['amount_usd'] for x in support_components),
        support_geometry=dimensions['supports'],foundation_families=dimensions['foundation_families'],qualified_foundation_selection=None,
        end_infill_concrete_m3_dual_km=infill_area*2000,rows=rows,total_allowance_usd_dual_km=sum(x['amount_usd'] for x in rows),
        quantities=dict(concrete_m3_dual_km=concrete,reinforcement_kg_dual_km=reinforcement,
            reaction_steel_kg_dual_km=rail_mass,shared_supports_per_route_km=supports,beam_lifts_per_route_km=2*supports),
        reinforcement_basis='unqualified intensity allowance; no rebar/prestress schedule',
        foundation_basis='itemised favourable ordinary-site procurement targets; support unit rates include unsized reinforcing/joint/process allowances; ground families, actual density and quotations remain unqualified',
        complete_installed_price_usd=None,costs_are_quotes=False)


def terminal_civil(c,costs,lines,*,scenario='base'):
    """Quantity-derived loop allowance with no sharing or curvature-price credit."""
    from . import geometry
    ordinary=civil(c,costs,scenario=scenario);rates={r['id']:r for r in ordinary['rows']}
    box=c['civil']['narrow_box_screen'];area=box['derived_concrete_area_m2'];span=c['civil']['reference_span_m']
    length=concrete=rail=0.;beams=supports=0
    for line in lines:
        for loop in line.get('operating_plan',{}).get('terminal_loops',[]):
            arc=loop['geometry']['length_m'];count=math.ceil(arc/span);bay=arc/count
            q=geometry.guideway_quantities(bay)
            length+=arc;beams+=count;supports+=count+1
            concrete+=q['beam_concrete_mass_kg']/geometry.MATERIALS['concrete']*count+.12*arc
            rail+=q['magnetic_rail_mass_kg']*count
    quantities=dict(structural_supply=concrete,reinforcement=concrete*costs['rates']['reinforcement_kg_per_m3'],
        passive_rail_supply=rail,supports=supports,walkway_brackets=length,transport=beams,erection=beams,
        temporary=supports,installation=length,night=length/1000,qa=length/1000,relocation=length/1000,traffic=length/1000)
    rows=[row(ident,q,rates[ident]['unit'],rates[ident]['unit_rate_usd'],
        'Proposed terminal loop: '+rates[ident]['process'],local_operation=True) for ident,q in quantities.items()]
    return dict(rows=rows,total_allowance_usd=sum(r['amount_usd'] for r in rows),
        single_direction_beam_length_m=length,beam_units=beams,support_positions=supports,
        concrete_m3=concrete,reaction_steel_kg=rail,
        basis='Exact loop arclength and span count with native straight-section/end-infill quantity equivalents; curved geometry,prestress,rail detailing and curvature premium unqualified',
        endpoint_foundation_sharing_credit=False,complete_loop_price_usd=None,costs_are_quotes=False)


def city_programme(c,costs,lines,route_km):
    """Explicit priced scopes, quantities, processes and remaining city exclusions."""
    stations=sum(len(line['stations']) for line in lines)
    # Records include interchange platforms on separate lines. Count platform
    # packages per line, never infer unique buildings from an unspecified key.
    from . import station
    def package(length,charger,index,*,charging=True):
        assumptions=station.load();assumptions['station'].update(winding_start_m=-length/2,winding_end_m=length/2)
        value=station.station_costs(assumptions)['sensitivity_cases'][index]['topologies']['B-two-fixed-groups']
        original=value['rows_usd']['charging']
        return value['direct_subtotal_usd']+original*((charger/200. if charging else 0.)-1)
    station_cases=station.station_costs()['sensitivity_cases']
    charger_input=max((line['charging']['candidate_kw_per_car'] for line in lines),default=c['power'].get('candidate_station_charger_kw_per_car',240.))
    charger_reference=200.;charger_scale=charger_input/charger_reference
    def electrical_target(case):
        topology=case['topologies']['B-two-fixed-groups']
        return topology['direct_subtotal_usd']+topology['rows_usd']['charging']*(charger_scale-1)
    station_costs={name:electrical_target(station_cases[index]) for index,name in enumerate(('low','base','high'))}
    terminal_zones=sum(line['topology'].get('terminal_service_zone_count',0) for line in lines)
    terminal_assumptions=station.load()
    for line in lines:
        if line['topology'].get('terminal_service_zone_count'):
            terminal_assumptions['station']['winding_start_m']=line['topology']['terminal_winding_start_m']
            terminal_assumptions['station']['winding_end_m']=line['topology']['terminal_winding_end_m'];break
    terminal_cases=station.station_costs(terminal_assumptions)['sensitivity_cases']
    terminal_station_costs={name:electrical_target(terminal_cases[index]) for index,name in enumerate(('low','base','high'))}
    from . import closure
    foundation=closure.foundation_cost_delta()
    totals=[]
    for scenario in costs['scenario_multipliers']:
        index={'low':0,'base':1,'high':2}[scenario]
        fleet=[vehicle(c,costs,c['mass']['ferrite_base'],c['power']['services_battery_kwh_per_car'],
            cars=line['formation']['cars'],scenario=scenario) for line in lines]
        fleet_cost=sum(v['total_allowance_usd']*line['fleet']['total'] for v,line in zip(fleet,lines))
        guideway=civil(c,costs,scenario=scenario)
        terminal=terminal_civil(c,costs,lines,scenario=scenario)
        main_electrical=sum(package(s.get('power_winding_length_m',200.),line['charging']['candidate_kw_per_car'],index) for line in lines for s in line['stations'])
        terminal_electrical=sum(package(line['topology']['terminal_winding_end_m']-line['topology']['terminal_winding_start_m'],line['charging']['candidate_kw_per_car'],index)*line['topology'].get('terminal_service_zone_count',0) for line in lines if line['topology'].get('terminal_service_zone_count'))
        station_electrical=main_electrical+terminal_electrical
        boosters=[zone for line in lines for zone in line.get('operating_plan',{}).get('powered_top_up_zones',[])]
        booster_electrical=sum(package(zone['length_m_per_direction'],0.,index,charging=False) for zone in boosters)
        factor=costs['scenario_multipliers'][scenario]
        booster_mount=sum(zone['mechanical_takeoff']['mount_and_cabinet_stock_target_usd'] for zone in boosters)*factor
        rescue=sum(line.get('operating_plan',{}).get('rescue_kit_count',0)*line.get('operating_plan',{}).get('rescue_kit_reference',{}).get('listed_kit_target_usd',0.) for line in lines)*factor
        additional_foundations=(guideway['quantities']['shared_supports_per_route_km']*route_km+terminal['support_positions'])*foundation['incremental_support_allowance_usd']*costs['scenario_multipliers'][scenario]
        previous_foundation_scope=fleet_cost+guideway['total_allowance_usd_dual_km']*route_km+station_electrical+terminal['total_allowance_usd']+booster_electrical+booster_mount+rescue
        totals.append(dict(scenario=scenario,repeat_fleet_allowance_usd=fleet_cost,station_electrical_allowance_usd=station_electrical,
            station_electrical_unit_allowance_usd=main_electrical/stations if stations else None,station_electrical_packages=stations+terminal_zones,
            mainline_station_electrical_packages=stations,terminal_service_electrical_packages=terminal_zones,
            mainline_station_electrical_allowance_usd=main_electrical,
            terminal_service_electrical_allowance_usd=terminal_electrical,
            terminal_service_electrical_unit_allowance_usd=terminal_electrical/terminal_zones if terminal_zones else None,
            booster_electrical_allowance_usd=booster_electrical,booster_mount_allowance_usd=booster_mount,
            rescue_kit_allowance_usd=rescue,booster_zone_count=len(boosters),
            recovery_kit_count=sum(line.get('operating_plan',{}).get('rescue_kit_count',0) for line in lines),
            terminal_civil_allowance_usd=terminal['total_allowance_usd'],terminal_civil_bill=terminal,
            ordinary_elevated_allowance_usd=guideway['total_allowance_usd_dual_km']*route_km,
            priced_scope_subtotal_usd=previous_foundation_scope+additional_foundations,
            comparison_scope_with_previous_foundation_allowance_usd=previous_foundation_scope,
            conditional_foundation_increment_usd=additional_foundations,
            priced_scope_with_conditional_foundation_proposal_usd=previous_foundation_scope+additional_foundations,
            selected_foundation_basis=(f"Conditional {foundation['foundation_square_side_m']:g}m square shallow-footing proposal at assumed "
                f"{closure.load()['civil']['foundation_allowable_pressure_pa']/1000:g}kPa; ground, connections, quantities and supplier rates remain unaccepted"),
            complete_city_programme_usd=None,epc_included=False,nre_included=False,supplier_quotes=False,
            ordinary_viaduct_proposal_km=route_km,ordinary_viaduct_unit_allowance_usd_dual_km=guideway['total_allowance_usd_dual_km'],
            fleet_scaling_basis='Each formation priced by car quantities, coupling interfaces and one shared control/protection set per train.',
            civil_basis='Native reaction steel and section concrete; explicit reinforcement, support, delivery, lift and site-work allowances.',
            formation_bills=[dict(cars=v['cars'],trainsets=line['fleet']['total'],train_allowance_usd=v['total_allowance_usd'],rows=v['rows']) for v,line in zip(fleet,lines)]))
    base=civil(c,costs);q=base['quantities']
    processes=deepcopy(costs['process_routes'])
    for p in processes:p.update(qualified=False,production_instruction_released=False)
    return dict(schema='osr-maglev-city-manufacturing/1',currency='USD',price_basis=costs['price_basis'],
        scenarios=totals,ordinary_route_km=route_km,ordinary_civil_bill_per_dual_km=base,
        quantities={**{key:value*route_km for key,value in q.items()},'platform_packages':stations,
            'cars':sum(l['formation']['cars']*l['fleet']['total'] for l in lines),
            'station_electrical_two_direction_packages':stations+terminal_zones,
            'terminal_service_zones':terminal_zones,
            'fixed_nonpassenger_top_up_zones':sum(len(line.get('operating_plan',{}).get('powered_top_up_zones',[])) for line in lines),
            'independent_one_way_rescue_kits':sum(line.get('operating_plan',{}).get('rescue_kit_count',0) for line in lines),
            'terminal_loop_single_direction_beam_m':terminal_civil(c,costs,lines)['single_direction_beam_length_m'],
            'station_charger_connections':sum((2*len(l['stations'])+l['topology'].get('terminal_service_zone_count',0))*l['formation']['cars'] for l in lines)},
        station_electrical_cost_basis=station.station_costs(),station_electrical_rating_qualified=False,
        terminal_electrical_cost_basis=station.station_costs(terminal_assumptions),
        terminal_service_zone_pricing='One complete two-direction electrical package per one-way service zone; no speculative shared supply or single-lane discount',
        charger_upgrade_target=dict(reference_input_kw_per_car=charger_reference,selected_input_kw_per_car=charger_input,
            selected_input_kw_per_car_by_line={line['line']:line['charging']['candidate_kw_per_car'] for line in lines},
            interface_cost_factor=charger_scale,rule='Linear charging-interface row scaling only; unquoted planning target, not supplier rating or transformer/thermal qualification',supplier_quote=False),
        configured_motor_voltage_current_rating_premium_usd=None,
        terminal_transfer_access_proposals=[connector for line in lines for connector in line.get('operating_plan',{}).get('terminal_transfer_access_proposals',[])],
        terminal_transfer_access_allowance_usd=None,
        motor_price_comparison_proved=False,
        wider_corridor_pricing_scope='Each passenger winding uses its installed length and selected research charger; every fixed top-up has a full two-direction electrical target without charger credit, plus separately counted mount/cabinet stock. Recovery kits have independent portals/footings and no sharing credit. Higher voltage/thermal supplier premiums, access and physical acceptance remain unpriced.',
        conditional_foundation_proposal=foundation,
        process_routes=processes,equipment_candidates=deepcopy(costs['equipment_candidates']),
        equipment_capex_usd=None,production_duration_days=None,local_value_added_fraction=None,
        sizing_method='Select annual route-km/car targets; convert BoQ to daily demand; size mould/curing, winding, test, transport and crane resources after measured cycle times and yields.',
        unpriced=['station structures, accessible exits and full MEP','actual45-second services charger upgrade and ratings,external utility reinforcement,storage/PV','depot/recovery/transfer equipment','special crossings and terminal curved-detail/land premiums','land/air rights and major utility works','surveys/qualified design/independent assurance','factory CAPEX and first articles','evacuation equipment and lifetime maintenance','programme management/EPC/finance/tax/duty/spares/OPEX'],
        complete_city_programme_usd=None,design_complete=False,manufacturing_release=False,physical_release=False)
