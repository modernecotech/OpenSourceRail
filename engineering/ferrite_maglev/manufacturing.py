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
    specs=[('body-and-passenger-systems',cars,'car',r['body_and_passenger_systems_per_car'],'cut/form/join frame; doors, glazing, interior and acceptance checks',True),
        ('ferrite',cars*ferrite,'kg',r['ferrite_per_kg'],'qualify stock blocks; retain in replaceable cartridges',True),
        ('magnetic-modules',cars,'car',r['magnetic_equipment_per_car'],'machine carriers/cores; wind, impregnate, assemble and calibrate',True),
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
        complete_factory_gate_price_usd=None,local_value_added_fraction=None,costs_are_quotes=False)


def civil(c,costs,*,area=None,span=None,walkway_area=.12,scenario='base'):
    from .model import positive
    from . import geometry
    r=costs['rates'];factor=costs['scenario_multipliers'][scenario]
    area=c['civil']['narrow_box_screen']['derived_concrete_area_m2'] if area is None else positive(area,'beam area')
    span=c['civil']['reference_span_m'] if span is None else positive(span,'span')
    positive(walkway_area,'walkway area',zero=True)
    concrete=(area+walkway_area)*2000
    supports=1000/span
    rail_mass=geometry.guideway_quantities(span)['magnetic_rail_line_mass_kg_m']*2000
    reinforcement=concrete*r['reinforcement_kg_per_m3']
    # Support/foundation units are explicit site-independent allowances, not
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
    return dict(rows=rows,total_allowance_usd_dual_km=sum(x['amount_usd'] for x in rows),
        quantities=dict(concrete_m3_dual_km=concrete,reinforcement_kg_dual_km=reinforcement,
            reaction_steel_kg_dual_km=rail_mass,shared_supports_per_route_km=supports,beam_lifts_per_route_km=2*supports),
        reinforcement_basis='unqualified intensity allowance; no rebar/prestress schedule',
        foundation_basis='unit allowance only; Baghdad/open-data estimates cannot qualify ground',
        complete_installed_price_usd=None,costs_are_quotes=False)


def city_programme(c,costs,lines,route_km):
    """Explicit priced scopes, quantities, processes and remaining city exclusions."""
    stations=sum(len(line['stations']) for line in lines)
    # Records include interchange platforms on separate lines. Count platform
    # packages per line, never infer unique buildings from an unspecified key.
    totals=[]
    for scenario in costs['scenario_multipliers']:
        fleet=[vehicle(c,costs,c['mass']['ferrite_base'],c['power']['gross_battery_matched_kwh_per_car'],
            cars=line['formation']['cars'],scenario=scenario) for line in lines]
        fleet_cost=sum(v['total_allowance_usd']*line['fleet']['total'] for v,line in zip(fleet,lines))
        guideway=civil(c,costs,scenario=scenario)
        totals.append(dict(scenario=scenario,repeat_fleet_allowance_usd=fleet_cost,
            ordinary_elevated_allowance_usd=guideway['total_allowance_usd_dual_km']*route_km,
            priced_scope_subtotal_usd=fleet_cost+guideway['total_allowance_usd_dual_km']*route_km,
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
            'station_charger_connections':sum(len(l['stations'])*l['formation']['cars'] for l in lines)},
        process_routes=processes,equipment_candidates=deepcopy(costs['equipment_candidates']),
        equipment_capex_usd=None,production_duration_days=None,local_value_added_fraction=None,
        sizing_method='Select annual route-km/car targets; convert BoQ to daily demand; size mould/curing, winding, test, transport and crane resources after measured cycle times and yields.',
        unpriced=['station structures, accessible exits and full MEP','charging/grid/storage/PV','depot/recovery/transfer equipment','special crossings and terminal loops','land/air rights and major utility works','surveys/qualified design/independent assurance','factory CAPEX and first articles','evacuation equipment and lifetime maintenance','programme management/EPC/finance/tax/duty/spares/OPEX'],
        complete_city_programme_usd=None,design_complete=False,manufacturing_release=False,physical_release=False)
