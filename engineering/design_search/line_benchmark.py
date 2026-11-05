"""Quantity-driven terminal-line planning budget, separate from hardware release.

The benchmark fixes transport service and publishes an inspectable cost ledger.
It reuses source-bound vehicle accounts and civil quantities, with explicit
functional-package estimates for launch equipment that is not yet engineered.
"""
from copy import deepcopy
from math import ceil, fsum, isfinite
from pathlib import Path
import argparse
import json
import tomllib

from engineering.station_rail import ROOT, station_motor
from engineering.station_rail.common import digest, encoded, identity
from engineering.development_baseline import selection, system_cost
from . import model_cost, line_benchmark_service, line_benchmark_civil

PRODUCER = 'engineering/design_search/line_benchmark.py'
SPEC = 'campaigns/line30-affordable-benchmark.toml'
SELECTOR = 'engineering/analysis-baseline.toml'
VEHICLE_COST = 'docs/design-engine/current/exports/selected-vehicle-cost.json'
CASES = ('low', 'base', 'high')
MODES = ('cable-capstan', 'common-drive-rollers', 'compact-launch-LIM')
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    installed_mass_complete=False, manufacturing_release=False,
    operating_release=False, selected_reference_changed=False,
    physical_journey_completed=False, procurement_ready=False)


def _seal(value, key='evaluation_id'):
    value[key] = identity(value)
    return value


def functional_requirements(spec):
    """Keep reference formation and acceleration out of the transport obligation."""
    r=spec['requirements']
    return dict(alignment_id=r['alignment_id'],route_km=r['route_km'],stations=r['stations'],
        trackways=r['trackways'],minimum_capacity_pphpd=r['minimum_capacity_pphpd'],
        maximum_headway_s=r['headway_s'],planned_standing_per_car=r['planned_standing_per_car'],
        operating_hours_per_day=r['operating_hours_per_day'],operating_days_per_year=r['operating_days_per_year'],
        accounting_horizon_years=r['design_life_years'],real_discount_rate=r['real_discount_rate'],
        mandatory_accessibility_and_safety=True)


def specification(root=ROOT):
    value = tomllib.loads((Path(root)/SPEC).read_text())
    if (value.get('schema') != 'osr-line-budget-benchmark/1'
            or value.get('purpose') != 'equal-service-cost-analysis'
            or value.get('physical_reference_changed') is not False
            or value.get('baseline_mechanism') not in MODES):
        raise ValueError('Explicit non-promoting line-cost benchmark required')
    def check(node):
        if isinstance(node, dict):
            for item in node.values(): check(item)
        elif isinstance(node, list):
            if len(node) != 3 or any(type(x) not in (int, float) or not isfinite(x) or x <= 0 for x in node):
                raise ValueError('Positive finite low/base/high triples required')
        elif type(node) in (int, float) and (not isfinite(node) or node < 0):
            raise ValueError('Finite nonnegative benchmark inputs required')
    check(value)
    r, d = value['requirements'], value['design']
    if (r['route_km'], r['stations'], r['trackways'], r['planned_standing_per_car']) != (30., 12, 2, 0):
        raise ValueError('This version fixes the 30 km, 12-station, double-track seated comparison')
    if (d['production_shifts'], d['civil_shifts']) != (2, 2):
        raise ValueError('Two-shift production and construction required')
    if not 0 <= r['real_discount_rate'] < 1 or not 1 <= r['design_life_years'] <= 100:
        raise ValueError('Bounded lifecycle required')
    return value


def sources(root=ROOT):
    root = Path(root)
    names = (PRODUCER, SPEC, SELECTOR, VEHICLE_COST, line_benchmark_service.PRODUCER,
        line_benchmark_civil.PRODUCER, model_cost.PRODUCER, model_cost.RATE_DATA,
        system_cost.PRODUCER, 'engineering/design_search/compact_launch.py',
        'engineering/development-baseline.toml', 'engineering/development_baseline/selection.py',
        'engineering/station_rail/operations.py', 'engineering/station_rail/braking.py',
        'engineering/station_rail/electrical.py', 'engineering/station_rail/station_motor.py',
        'engineering/station_rail/vehicle.py', 'engineering/station_rail/civil.py',
        'engineering/station_rail/common.py', 'engineering/station_rail/brief.toml')
    return {name: digest(root/name) for name in names}


def _vehicle_cost(root, vehicle):
    value = json.loads((Path(root)/VEHICLE_COST).read_bytes())
    if (value['cost_estimate_id'] != identity({k:v for k,v in value.items() if k != 'cost_estimate_id'})
            or value['candidate_id'] != vehicle['candidate_id']
            or any(digest(Path(root)/name) != sha for name,sha in value['source_sha256'].items())):
        raise ValueError('Exact current vehicle cost account required')
    if any(value.get(k) is not False for k in ('physical_accepted', 'engineering_accepted', 'installed_mass_complete')):
        raise ValueError('A cost account cannot grant vehicle acceptance')
    return value


def fixed_mass_vehicle_price(value):
    """Separate rate uncertainty from the source account's .8/1.2 mass cases."""
    factors=value['mass_reserve_sensitivity']['case_factors']
    repriced={}
    for case in CASES:
        adjustment=fsum(row['cost_iqd'][case]*(1/factors[case]-1)
            for row in value['lines'] if row['line_key'].startswith('unlocated-account/'))
        repriced[case]=value['total_vehicle_factory_delivery_assembly_iqd_per_train'][case]+adjustment
    return dict(source_cost_estimate_id=value['cost_estimate_id'],source_mass_factors=factors,
        fixed_mass_per_train_iqd=repriced,
        policy='Reprice the linear residual-account material/process/overhead subtotal to factor 1.0; located stock, final assembly and delivery are unchanged. No overlap credit.')


def _add(lines, key, scope, quantity, costs, basis, life=None):
    if scope not in model_cost.SCOPES or len(costs) != 3 or any(not isfinite(x) or x < 0 for x in costs):
        raise ValueError('Finite disjoint budget line required')
    row = dict(key=key, scope=scope, quantity=quantity,
        costs_iqd={case:round(costs[i], 2) for i,case in enumerate(CASES)},
        basis=basis, source_class='C', life_years=life)
    lines.append(_seal(row, 'line_id'))


def _drive(spec, service, rates, mode):
    d, rotary, lim = spec['design'], spec['rotary'], spec['lim']
    fx = spec['currency']['iqd_per_usd']; n = service['departure_sites']
    mechanical = service['peak_train_mechanical_power_W']/1000
    stroke = service['jerk_launch_distance_m']; bank = service['jerk_full_train_fin_launch_envelope_m']
    primary = station_motor.definition(); lines=[]; capacities=[]
    requested_bank=bank
    modules_per_site=None
    if mode=='compact-launch-LIM':
        modules_per_site=ceil(bank/primary['addressed_module_length_m'])
        bank=modules_per_site*primary['addressed_module_length_m']
    for i,case in enumerate(CASES):
        efficiency = lim['efficiency'] if mode == 'compact-launch-LIM' else rotary['transmission_efficiency']*rotary['motor_efficiency']*rotary['vfd_efficiency']
        active_input = mechanical/efficiency
        pf = lim['power_factor'][i] if mode == 'compact-launch-LIM' else rotary['power_factor'][i]
        kva = active_input/pf*rotary['capacity_margin'][i]
        shaft = mechanical/rotary['transmission_efficiency']*rotary['capacity_margin'][i]
        capacities.append(dict(case=case, sites=n, active_input_kw_per_site=active_input,
            budget_kva_per_site=kva, budget_shaft_kw_per_site=shaft,
            actual_available_power=None, power_factor_is_assumption=True))
    _add(lines, 'launch-converters', 'stations-power', dict(capacities=capacities),
        [n*x['budget_kva_per_site']*rotary['converter_usd_per_kva'][i]*fx for i,x in enumerate(capacities)],
        'One converter capacity budget per outgoing launch site; common per-kVA rate across mechanisms, with explicit efficiency, power factor and headroom.', spec['lifecycle']['electronics_life_years'])
    _add(lines, 'launch-grid-protection-install', 'stations-power', dict(capacities=capacities),
        [n*x['budget_kva_per_site']*(rotary['grid_protection_usd_per_kva'][i]+rotary['electrical_install_usd_per_kva'][i])*fx for i,x in enumerate(capacities)],
        'Incremental transformer/switchgear/protection and installation per launch kVA. Auxiliary charging capacity is priced separately without another traction converter.', [30,25,20])
    if mode == 'compact-launch-LIM':
        metres = n*bank
        factory=[]
        for i,case in enumerate(CASES):
            direct = (primary['copper_kg_per_m']*lim['copper_iqd_per_kg'][i]
                + primary['primary_steel_kg_per_m']*lim['electrical_steel_iqd_per_kg'][i]
                + primary['bare_primary_stock_kg_per_m']*lim['fabrication_h_per_kg'][i]*rates[case]['loaded_two_shift_wage_iqd_h'])
            factory.append(metres*(direct*(1+[.1,.2,.3][i])*lim['unresolved_thrust_design_cost_multiplier'][i]
                +lim['support_cooling_installed_iqd_per_m'][i]))
        _add(lines, 'LIM-primary-installed', 'stations-power', dict(sites=n, metres=metres,
            requested_launch_envelope_m_per_site=requested_bank,installed_length_m_per_site=bank,
            modules_per_site=modules_per_site,module_length_m=primary['addressed_module_length_m'],
            stator_face_module_joints_per_site=2*max(0,modules_per_site-1),
            layout_policy='whole-modules; launch-only with independent onboard receiving brakes',
            joints_priced_in='support-cooling-installation allowance; not a detailed joint quotation',
            stock_proxy_kg_per_m=primary['bare_primary_stock_kg_per_m'], thrust_design_cost_multiplier=lim['unresolved_thrust_design_cost_multiplier']), factory,
            'Existing stator copper/steel quantities are a COST proxy; fabrication, support/cooling/installation and explicit unresolved-thrust cost allowance are included. This does not make the old stator deliver the new required force.', spec['lifecycle']['drive_life_years'])
    else:
        _add(lines, 'rotary-motors-and-integration', 'stations-power', dict(capacities=capacities),
            [n*x['budget_shaft_kw_per_site']*(rotary['motor_usd_per_shaft_kw'][i]+rotary['integration_usd_per_shaft_kw'][i])*fx for i,x in enumerate(capacities)],
            'Motor-only catalogue-calibrated rate plus transmission/cooling/cabinet integration; converter is separate. No catalogue model is selected or qualified.', spec['lifecycle']['drive_life_years'])
        if mode == 'cable-capstan':
            unit=[rotary['rope_length_per_stroke']*stroke*rotary['rope_usd_per_m'][i]
                +stroke*rotary['return_guide_usd_per_m'][i]+rotary['winch_grip_drum_anchors_usd_per_site'][i] for i in range(3)]
            quantity=dict(sites=n, stroke_m=stroke, rope_m_per_site=rotary['rope_length_per_stroke']*stroke,
                minimum_line_tension_N=service['peak_train_force_N'],
                necessary_reset_cycle_s=service['jerk_bound']['total_time_s']+stroke/rotary['return_speed_m_s']+rotary['coupling_reset_s'],
                rope_strength_fatigue_release_qualified=False)
            basis='Rope and return-guide lengths plus drum/grip/trolley/anchors/guards package. Persistent coupling, fatigue, redundant stopping and release remain unqualified.'
        else:
            contacts=ceil(bank/rotary['roller_spacing_m'])
            unit=[bank*rotary['roller_common_drive_usd_per_m'][i]+contacts*rotary['roller_unit_usd'][i] for i in range(3)]
            quantity=dict(sites=n, bank_m_per_site=bank, contacts_per_site=contacts,
                mechanical_common_drive_assumed=True, overlap_force_map_available=False)
            basis='Full train-fin coverage, common mechanical power distribution and distributed contact assemblies; independent small rollers are not assumed able to share power without this hardware.'
        _add(lines, 'launch-contact-and-return-hardware', 'stations-power', quantity,
            [n*x*fx for x in unit], basis, spec['lifecycle']['drive_life_years'])
    return lines, capacities


def _capital(spec, vehicle, vc, service, civil, assumptions, mode):
    r,d,c = spec['requirements'],spec['design'],spec['capital']
    a=assumptions['assumptions']; fx=spec['currency']['iqd_per_usd']; lines=[]
    fleet,cars=service['total_trainsets'],service['totalcars']
    fixed_vehicle=fixed_mass_vehicle_price(vc)
    _add(lines,'delivered-and-assembled-fleet','rolling-stock',dict(trainsets=fleet,cars=cars,
        per_train_iqd=fixed_vehicle['fixed_mass_per_train_iqd'],mass_case_repricing=fixed_vehicle,source_cost_estimate_id=vc['cost_estimate_id']),
        [fleet*fixed_vehicle['fixed_mass_per_train_iqd'][x] for x in CASES],
        'Selected vehicle stock plus residual accounts, factory process, delivery and final assembly, counted once for the purchased fleet; possible account overlap remains unresolved.',spec['lifecycle']['vehicle_life_years'])
    _add(lines,'new-launch-vehicle-interfaces','rolling-stock',dict(cars=cars,reserve_kg_per_car=d['added_vehicle_mass_kg_per_car']),
        [cars*d['added_vehicle_mass_kg_per_car']*x for x in c['vehicle_interface_iqd_per_kg']],
        'Nonzero mounting/coupler/reaction-structure manufacturing reserve; original secondary account is retained without a speculative removal credit.',spec['lifecycle']['vehicle_life_years'])
    for item in civil['capital_lines']:
        _add(lines,item['key'],item['scope'],item['quantity'],[item['costs_iqd'][x] for x in CASES],item['basis'],[60,50,40])
    drive,capacities=_drive(spec,service,civil['unit_rates'],mode);lines.extend(drive)
    platforms=service['boarding_edges']*d['platform_length_m']*d['platform_width_m']
    _add(lines,'station-platform-structures','stations-power',dict(stations=r['stations'],boarding_edges=service['boarding_edges'],platform_area_m2=platforms),
        [platforms*x for x in a['station_platform_iqd_per_m2']],
        'New boarding platform structures only; running beams/piers are in guideway. Asymmetric platform/door interfaces and evacuation design remain open.',[40,30,20])
    _add(lines,'station-access-protection-controls','stations-power',dict(stations=r['stations']),
        [r['stations']*(a['station_access_iqd_each'][i]+a['station_control_iqd_each'][i]+a['station_install_iqd_each'][i]) for i in range(3)],
        'Accessible access, lifts, passenger/fire/egress protection, station controls and fitout/installation packages. No accessibility requirement is removed.',[20,15,10])
    _add(lines,'terminal-turnback-and-line-controls','stations-power',dict(terminals=2,positions_per_end=service['minimum_turnback_positions_per_end'],
        additional_platform_edges_counted=0,route_km=r['route_km']),
        [2*c['terminal_layout_iqd_per_end'][i]+r['route_km']*c['route_control_iqd_per_km'][i] for i in range(3)],
        'Protected crossovers/approach and route communications allowance; two terminal boarding edges already supply two budget positions, so their platforms are not added twice. Conflict-free operations remain unproven.',[20,15,10])
    charger_kw=service['boarding_edges']*r['cars_per_train']*d['charger_kw_per_car']
    _add(lines,'auxiliary-charging-and-grid-increment','stations-power',dict(platforms=service['boarding_edges'],required_kw=charger_kw,
        energy_margin_kwh_per_car_per_half_cycle=service['auxiliary']['energy_margin_kwh_per_car_per_half_cycle']),
        [charger_kw*(c['charger_usd_per_kw'][i]*(1+c['charger_install_fraction'][i])+spec['rotary']['grid_protection_usd_per_kva'][i])*fx for i in range(3)],
        'One charging capacity package per boarding edge, with extra grid capacity priced once; no traction motor or traction battery onboard. Nominal charge balance is conditional on the unvalidated battery/charge map.',spec['lifecycle']['electronics_life_years'])
    # Labour positions are not complete factories. Purchased component machinery
    # and hired machine hours are already inside the delivered vehicle unit price.
    hours=[]
    for i in range(3):
        hours.append(fsum(l['quantity'].get('process_hours_per_train',[0,0,0])[i]/(vc['mass_reserve_sensitivity']['case_factors'][CASES[i]] if l['line_key'].startswith('unlocated-account/') else 1)
            +r['cars_per_train']*l['quantity'].get('process_hours_per_car',[0,0,0])[i]
            +l['quantity'].get('labour_hours_per_car',[0,0,0])[i]*l['quantity'].get('cars',0)
            for l in vc['lines']))
    capacity=d['production_years']*d['production_days_per_year']*d['production_shifts']*d['hours_per_production_shift']*d['productive_utilisation']
    workplaces=[ceil(h*fleet/capacity) for h in hours]
    assembly_row=next(z for z in vc['lines'] if z['line_key']=='six-car-final-vehicle-assembly')
    assembly_hours=[assembly_row['quantity']['labour_hours_per_car'][i]*r['cars_per_train'] for i in range(3)]
    assembly=[max(1,ceil(fleet*h/(capacity*c['assembly_crew_per_bay']))) for h in assembly_hours]
    building=[(workplaces[i]*c['workspace_area_m2']+assembly[i]*c['assembly_bay_area_m2'])*c['factory_storage_area_factor'] for i in range(3)]
    spans=civil['quantities']['span_count']
    moulds=[ceil(spans*x/(d['production_years']*d['production_days_per_year'])) for x in c['precast_mould_cycle_days']]
    beam_h=civil['process_assumptions']['beam_factory_h_per_span']
    precast_cells=[ceil(spans*beam_h[i]/(capacity*c['precast_crew_per_cell'])) for i in range(3)]
    precast_covered=[n*(d['span_m']+4)*c['precast_bed_width_m'] for n in moulds]
    yard_storage=ceil(spans/(d['production_years']*d['production_days_per_year'])*c['precast_yard_hold_workdays'])*(d['span_m']+2)*c['precast_storage_width_m']/c['precast_storage_utilisation']
    precast_area=[x+yard_storage for x in precast_covered]
    _add(lines,'project-production-buildings-and-tooling','factory-tooling',dict(fleet_process_hours=[fleet*x for x in hours],productive_hours_per_workplace=capacity,
        operator_workplaces_per_shift=workplaces,assembly_bays=assembly,vehicle_building_m2=building,
        precast_moulds=moulds,precast_crew_cells=precast_cells,precast_covered_m2=precast_covered,
        precast_yard_storage_m2=yard_storage,production_shifts=d['production_shifts']),
        [workplaces[i]*c['workplace_tooling_iqd'][i]+c['vehicle_fixture_sets']*c['vehicle_fixture_iqd'][i]
            +building[i]*c['factory_building_iqd_per_m2'][i]+moulds[i]*c['precast_mould_iqd'][i]
            +precast_cells[i]*c['precast_cell_iqd'][i]+precast_covered[i]*c['factory_building_iqd_per_m2'][i]
            +precast_area[i]*c['precast_yard_iqd_per_m2'][i] for i in range(3)],
        'Project buildings, local benches/handling fixtures, precast moulds and concrete cells. Each labour position is not charged as a complete vehicle cell; hired machine use and purchased-component factories stay in unit prices. No second complete motor factory is added.',[30,25,20])
    bays=max(1,ceil(fleet*c['depot_workshop_fraction_of_fleet']))
    storage=fleet*c['depot_storage_length_per_train_m']*c['depot_storage_track_pitch_m']
    workshop=bays*c['depot_bay_length_m']*c['depot_bay_width_m']
    depot_area=(storage+workshop)*(1+c['depot_circulation_fraction'])
    depot_track=(fleet*c['depot_storage_length_per_train_m']+bays*c['depot_bay_length_m'])*(1+c['depot_circulation_fraction'])
    turnouts=ceil(fleet/5)+4
    costs=[]
    for i,x in enumerate(CASES):
        rail_per_track_m=civil['beam']['running_rail_kg']/d['span_m']
        fasteners_per_track_m=civil['beam']['direct_fastener_sets']/d['span_m']
        costs.append(storage*c['depot_earthworks_iqd_per_m2'][i]+workshop*c['depot_building_iqd_per_m2'][i]
            +depot_track*(c['depot_trackbed_iqd_per_track_m'][i]+rail_per_track_m*civil['unit_rates'][x]['rail_factory_iqd_kg']
                +fasteners_per_track_m*civil['unit_rates'][x]['complete_8kg_fastener_factory_iqd_set']
                +civil['unit_rates'][x]['rail_field_install_iqd_track_m'])
            +2*max(0,ceil(depot_track/20)-1)*civil['process_assumptions']['butt_weld_complete_iqd_each'][i]
            +turnouts*c['depot_turnout_iqd_each'][i]+bays*c['depot_workshop_equipment_iqd_per_bay'][i]+c['depot_services_iqd'][i])
    _add(lines,'depot-and-workshop','land-utilities-depot',dict(area_m2=depot_area,storage_m2=storage,covered_workshop_m2=workshop,track_m=depot_track,
        butt_weld_allowance=2*max(0,ceil(depot_track/20)-1),turnouts=turnouts,workshop_bays=bays),costs,
        'Sized storage tracks, trackbed/rails/fasteners, rail installation/weld/QA, covered maintenance bays, shop equipment, turnout and utility allowances; no generic full-depot charge per trainset.',[40,30,20])
    _add(lines,'land-and-utility-relocation','land-utilities-depot',dict(route_row_m2=r['route_km']*1000*c['row_width_m'],depot_area_m2=depot_area,
        vehicle_factory_m2=building,precast_factory_yard_m2=precast_area,acquired_row_fraction=c['new_row_acquisition_fraction']),
        [((r['route_km']*1000*c['row_width_m']*c['new_row_acquisition_fraction'][i])+depot_area+building[i]+precast_area[i])*c['land_iqd_per_m2'][i]
            +r['route_km']*c['utilities_iqd_per_route_km'][i] for i in range(3)],
        'Assumed partial public-corridor reuse, purchased depot/factory footprint and relocation allowance. No land rights, city valuation, surveyed utilities or major water crossing is established.')
    rolling=[fsum(l['costs_iqd'][x] for l in lines if l['scope']=='rolling-stock') for x in CASES]
    _add(lines,'fleet-spares-and-commissioning','fleet',dict(trainsets=fleet,spares_fraction=a['fleet_spares_fraction']),
        [rolling[i]*a['fleet_spares_fraction'][i]+fleet*a['fleet_commission_iqd_per_train'][i] for i in range(3)],
        'Component spares and commissioning; spare trainsets are already inside delivered fleet count, and vehicle delivery is not added twice.')
    _add(lines,'recovery-assets','recovery',dict(units=ceil(r['route_km']/15)),
        [ceil(r['route_km']/15)*x for x in a['rescue_iqd_each']],
        'One protected recovery asset budget per 15 route-km; tow capacity, access and response remain unqualified.',[25,20,15])
    direct=[fsum(l['costs_iqd'][x] for l in lines) for x in CASES]
    _add(lines,'engineering-prototypes-independent-testing','construction',dict(direct_budget_iqd=direct,fraction=c['engineering_testing_fraction']),
        [direct[i]*x for i,x in enumerate(c['engineering_testing_fraction'])],
        'Project design, surveys, representative prototypes, independent engineering/safety review and integration testing provision; factory QA is already in component prices.')
    tax_base=[rolling[i]+fsum(l['costs_iqd'][x] for l in drive) for i,x in enumerate(CASES)]
    _add(lines,'tax-and-import-duty-provision','construction',dict(eligible_equipment_iqd=tax_base,fraction=c['tax_duty_provision_fraction']),
        [tax_base[i]*c['tax_duty_provision_fraction'][i] for i in range(3)],
        'Unverified tax/duty cash allowance on vehicles and launch equipment. These percentages are budget hypotheses, not statements of Iraqi tax law.')
    subtotal=[fsum(l['costs_iqd'][x] for l in lines) for x in CASES]
    _add(lines,'project-risk-contingency','construction',dict(pre_contingency_iqd=subtotal,fraction=c['project_contingency_fraction']),
        [subtotal[i]*x for i,x in enumerate(c['project_contingency_fraction'])],
        'Explicit contingency for unresolved installed detail, site and development scope; no physical requirement is waived by this allowance.')
    return lines,dict(capacities=capacities,workplaces=workplaces,assembly_bays=assembly,moulds=moulds,
        precast_factory_yard_m2=precast_area,depot_area_m2=depot_area)


def _lifecycle(spec, service, vc, lines, assumptions, mode):
    r,d,l=spec['requirements'],spec['design'],spec['lifecycle']; a=assumptions['assumptions']
    years,discount=r['design_life_years'],r['real_discount_rate']
    annuity=fsum((1+discount)**-y for y in range(1,years+1));cap=[fsum(z['costs_iqd'][x] for z in lines) for x in CASES]
    annual_km=service['train_km_per_day']*r['operating_days_per_year']
    departures=2*3600/r['headway_s']*r['operating_hours_per_day']*(r['stations']-1)*r['operating_days_per_year']
    aux=service['active_trainsets']*r['cars_per_train']*d['aux_kw_per_car']*r['operating_hours_per_day']*r['operating_days_per_year']/d['charge_efficiency']
    efficiency=spec['lim']['efficiency'] if mode=='compact-launch-LIM' else spec['rotary']['transmission_efficiency']*spec['rotary']['motor_efficiency']*spec['rotary']['vfd_efficiency']
    reserve_aux=service['spare_trainsets']*r['cars_per_train']*d['aux_kw_per_car']*l['reserve_aux_fraction']*r['operating_hours_per_day']*r['operating_days_per_year']
    kwh=[departures*service['mechanical_work_kwh_per_departure']/efficiency+aux+reserve_aux
        +(r['stations']*l['station_aux_kw_each'][i]+l['depot_aux_kw'][i])*r['operating_hours_per_day']*r['operating_days_per_year'] for i in range(3)]
    energy=[kwh[i]*x for i,x in enumerate(a['electricity_iqd_per_kwh'])]
    shift=service['shift_info']; covered=[a['controllers_per_shift'][i]+r['stations']*a['station_staff_per_station_per_shift'][i] for i in range(3)]
    shifts=shift['operations_shifts_per_day']
    wage=[assumptions['benchmark_rates_iqd']['wage_skilled_iqd_per_h']*a['wage_burden_multipliers'][i]
        *(1+(a['second_shift_wage_premium'][i]+(a['third_shift_wage_premium'][i] if shifts==3 else 0))/shifts) for i in range(3)]
    staffing=[covered[i]*shift['operations_shifts_per_day']*a['operations_reliever_multiplier'][i]*shift['operations_hours_per_shift']*r['operating_days_per_year']*wage[i] for i in range(3)]
    maintainable=[fsum(z['costs_iqd'][x] for z in lines if z['scope'] in ('rolling-stock','guideway','stations-power','land-utilities-depot')) for x in CASES]
    exposure=r['operating_hours_per_day']/18.
    maintenance=[maintainable[i]*l['maintenance_fraction'][i]*exposure for i in range(3)]
    reliability=[annual_km*x for x in a['reliability_iqd_per_train_km']]
    standby=[ceil(r['route_km']/15)*x for x in a['rescue_standby_iqd_per_year']]
    renewal=[0.,0.,0.];events=[]
    for row in lines:
        if row['life_years'] is None:continue
        for i,x in enumerate(CASES):
            for year in model_cost.replacement_event_times(years,row['life_years'][i]/exposure):
                pv=row['costs_iqd'][x]/(1+discount)**year;renewal[i]+=pv
                events.append(dict(line_id=row['line_id'],case=x,year=year,present_value_iqd=round(pv,2)))
    # The service account has a shorter cycle than a complete vehicle. Whole-car
    # replacements reset its age; never replace the same account twice at a reset.
    services=next(z for z in vc['lines'] if z['line_key']=='unlocated-account/services')
    schedules=[]
    for i,x in enumerate(CASES):
        parents=model_cost.replacement_event_times(years,l['vehicle_life_years'][i]/exposure)
        schedule=system_cost.component_renewal_schedule(years,l['service_battery_life_years'][i]/exposure,parents)
        price=services['cost_iqd'][x]/vc['mass_reserve_sensitivity']['case_factors'][x]*service['total_trainsets']
        for event in schedule['events']:
            if event.get('covered_by_parent_replacement',False):continue
            pv=price/(1+discount)**event['year'];renewal[i]+=pv
            events.append(dict(line_id=services['line_id'],case=x,year=event['year'],present_value_iqd=round(pv,2)))
        schedules.append(schedule)
    result=[]
    for key,scope,annual,basis in (
        ('annual-electricity','energy',energy,'Required launch work plus active-fleet hotel load, declared losses and tariff; no regeneration credit or measured energy.'),
        ('operations-staff','operations',staffing,'Covered station/control positions, two shifts and relief; maintenance staff are inside the maintenance provision.'),
        ('routine-maintenance','maintenance',maintenance,'Routine labour/consumables reserve excludes the scheduled asset replacements.'),
        ('corrective-disruption','reliability',reliability,'Train-km corrective/disruption reserve; no observed availability or fare revenue.'),
        ('recovery-standby','recovery',standby,'Standby budget for the separately purchased recovery assets.')):
        _add(result,key,scope,dict(annual_iqd=annual,annuity=annuity),[v*annuity for v in annual],basis)
    _add(result,'scheduled-renewals','renewals',dict(events=events,service_account_age_reset_schedules=schedules),renewal,'Disjoint initial asset lines renewed at declared planning lives; complete vehicle resets service-account age.')
    _add(result,'decommissioning','disposal',dict(year=years),[cap[i]*l['decommission_fraction'][i]/(1+discount)**years for i in range(3)],'Year-30 removal/disposal provision with no speculative salvage credit.')
    return result,dict(annual_electricity_kwh=dict(zip(CASES,kwh)),annual_train_km=annual_km,
        annual_energy_iqd=dict(zip(CASES,energy)),annual_operations_iqd=dict(zip(CASES,staffing)),
        annual_maintenance_iqd=dict(zip(CASES,maintenance)),annual_reliability_iqd=dict(zip(CASES,reliability)),
        annual_recovery_standby_iqd=dict(zip(CASES,standby)),operations_shifts=shift['operations_shifts_per_day'])


def evaluate(root=ROOT):
    root=Path(root);spec=specification(root);epoch=sources(root)
    vehicle=selection.load(root)['vehicle']; vc=_vehicle_cost(root,vehicle)
    assumptions=model_cost.assumptions(root)
    service=line_benchmark_service.evaluate(spec['requirements'],spec['design'],vehicle)
    if not service['profile']['reachable'] or service['auxiliary']['energy_balance_screen']!='pass':
        raise ValueError('The benchmark must expose and resolve its conditional nominal service/energy failure before price comparison')
    civil=line_benchmark_civil.evaluate(spec['requirements'],spec['design'],vehicle,root=root)
    variants=[];r=spec['requirements'];fx=spec['currency']['iqd_per_usd']
    for mode in MODES:
        capital,production=_capital(spec,vehicle,vc,service,civil,assumptions,mode)
        life,operating=_lifecycle(spec,service,vc,capital,assumptions,mode)
        lines=[*capital,*life]
        cap={x:round(fsum(z['costs_iqd'][x] for z in capital),2) for x in CASES}
        whole={x:round(fsum(z['costs_iqd'][x] for z in lines),2) for x in CASES}
        scopes={scope:{x:round(fsum(z['costs_iqd'][x] for z in lines if z['scope']==scope),2) for x in CASES} for scope in model_cost.SCOPES}
        if any(scopes[s]['base']<=0 for s in model_cost.SCOPES):raise ValueError('Missing nonzero budget scope')
        extended_spec=deepcopy(spec);extended_spec['requirements']['operating_hours_per_day']=24.
        extended_service=line_benchmark_service.evaluate(extended_spec['requirements'],extended_spec['design'],vehicle)
        extended_life,extended_operating=_lifecycle(extended_spec,extended_service,vc,capital,assumptions,mode)
        extended_npv={x:cap[x]+fsum(z['costs_iqd'][x] for z in extended_life) for x in CASES}
        value=dict(mechanism=mode,capital_lines=capital,lifecycle_lines=life,scope_totals_iqd=scopes,
            installed_capital_iqd=cap,installed_capital_usd={x:cap[x]/fx for x in CASES},
            price_per_route_km_usd={x:cap[x]/fx/r['route_km'] for x in CASES},
            price_per_track_km_usd={x:cap[x]/fx/(r['route_km']*r['trackways']) for x in CASES},
            whole_life_npv_iqd=whole,whole_life_npv_usd={x:whole[x]/fx for x in CASES},
            funding_envelope_including_financing_usd={x:cap[x]*(1+spec['capital']['financing_provision_fraction'][i])/fx for i,x in enumerate(CASES)},
            service=service,production=production,operating=operating,estimate_class='C',
            extended_24h_three_shift_sensitivity=dict(operating=extended_operating,
                service_evaluation_id=extended_service['evaluation_id'],
                whole_life_npv_usd={x:extended_npv[x]/fx for x in CASES},
                requirement_hours_changed=True,physical_repeated_duty_qualified=False),
            physical_candidate_id=None,actual_installed_price=None,**FLAGS)
        variants.append(_seal(value))
    baseline=next(v for v in variants if v['mechanism']==spec['baseline_mechanism'])
    value=dict(schema='osr-line-budget-result/1',specification=spec,
        functional_requirements=functional_requirements(spec),
        requirements_id=identity(functional_requirements(spec)),benchmark_definition_id=identity(dict(requirements=r,design=spec['design'])),
        benchmark_selection_id=identity(dict(purpose=spec['purpose'],requirements=r,design=spec['design'],mechanism=spec['baseline_mechanism'])),
        selected_reference_vehicle_candidate_id=vehicle['candidate_id'],vehicle_cost_estimate_id=vc['cost_estimate_id'],
        source_sha256={**epoch,**vc['source_sha256'],**civil['source_sha256'],**vehicle['source_sha256']},
        statistical_assumption_id=assumptions['assumption_id'],vehicle_rate_assumptions=vc['assumption_values'],civil=civil,variants=variants,
        rate_assumption_id=identity(dict(economic_sections={k:spec[k] for k in ('currency','rotary','lim','capital','lifecycle')},
            statistical_assumption_id=assumptions['assumption_id'],vehicle_rate_assumptions=vc['assumption_values'])),
        baseline_mechanism=spec['baseline_mechanism'],baseline_evaluation_id=baseline['evaluation_id'],
        baseline_price_per_route_km_usd=baseline['price_per_route_km_usd'],
        comparison_policy='Hold route, stations, offered peak capacity, comfort, daily service and horizon constant. Compare complete installed and whole-life estimates; physical acceptance is independent.',
        rate_basis='2026 planning IQD with dated July CSO materials/wages and explicitly declared engineering package rates; USD translated at fixed observed CBI rate. No supplier-installed quotes.',
        interpretation='Low/base/high are coupled planning sensitivities, not probability bounds. Cable is the analysis anchor, not an engineering selection or proven cheapest design.',
        analysis_priorities=[dict(key=z['key'],base_iqd=z['costs_iqd']['base'],
            ten_percent_direct_cost_sensitivity_usd_per_route_km=z['costs_iqd']['base']*.1/fx/r['route_km'],
            changing_an_allowance_is_not_an_engineering_saving=True)
            for z in sorted(baseline['capital_lines'],key=lambda z:z['costs_iqd']['base'],reverse=True)[:20]],
        limitations=['Level synthetic route, ordinary shallow-foundation hypothesis, no major river bridge or tunnel design.',
            'Installed mass, centre of gravity, reaction/coupler structures and added rotating inertia remain unresolved.',
            'The journey is a kinematic target; integrated jerk, actual force/current/thermal maps, independent braking and protected turnbacks remain unqualified.',
            'One-sided doors require a compatible platform/terminal layout. Platform continuity and construction access remain unverified.',
            'Nominal 35 kW auxiliary duty is conditional; 50 kW stress needs revised charging/turnback/fleet. Grade samples can fail station-only coasting.',
            'Vehicle residual cost accounts can overlap; no speculative overlap credit or shared-bogie saving is taken.',
            'Cable/roller structures and LIM thrust uprating are provisional functional-package estimates, not manufacturing-ready designs.',
            'Taxes/duties, project contingency and financing are explicit provisions, not legal or credit offers. Financing is separate from the installed-cost benchmark.'],
        simulation_budget_complete=True,engineering_validated=False,**FLAGS)
    if any(digest(root/name)!=sha for name,sha in value['source_sha256'].items()):raise ValueError('Benchmark source epoch changed')
    return _seal(value)


def validate_result(value,root=ROOT,*,verify_sources=True):
    """Check financial closure and record identities without implying physics."""
    def sealed(record,key):
        if record.get(key)!=identity({k:v for k,v in record.items() if k!=key}):
            raise ValueError('Benchmark record identity differs: '+key)
    def close(a,b):
        if not isfinite(a) or not isfinite(b) or abs(a-b)>max(.05,abs(b)*1e-11):
            raise ValueError('Benchmark financial ledger does not close')
    if value.get('schema')!='osr-line-budget-result/1':raise ValueError('Benchmark result schema differs')
    sealed(value,'evaluation_id')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Budget cannot grant acceptance')
    spec=value['specification'];r=spec['requirements'];fx=spec['currency']['iqd_per_usd']
    contract=functional_requirements(spec)
    if value['requirements_id']!=identity(contract) or value['functional_requirements']!=contract:
        raise ValueError('Benchmark requirements identity differs')
    if value['benchmark_definition_id']!=identity(dict(requirements=r,design=spec['design'])):
        raise ValueError('Benchmark definition differs')
    if value['benchmark_selection_id']!=identity(dict(purpose=spec['purpose'],requirements=r,design=spec['design'],mechanism=spec['baseline_mechanism'])):
        raise ValueError('Benchmark selection identity differs')
    expected_rates=identity(dict(economic_sections={k:spec[k] for k in ('currency','rotary','lim','capital','lifecycle')},
        statistical_assumption_id=value['statistical_assumption_id'],vehicle_rate_assumptions=value['vehicle_rate_assumptions']))
    if value['rate_assumption_id']!=expected_rates:raise ValueError('Benchmark rate assumptions identity differs')
    if not isinstance(value.get('source_sha256'),dict) or not set(sources(root)).issubset(value['source_sha256']):
        raise ValueError('Required benchmark source bindings are missing')
    if value['baseline_mechanism']!=spec['baseline_mechanism']:raise ValueError('Benchmark mechanism selection differs')
    if verify_sources:
        for name,sha in value['source_sha256'].items():
            p=Path(name)
            if p.is_absolute() or '..' in p.parts or digest(Path(root)/p)!=sha:
                raise ValueError('Benchmark source epoch differs: '+name)
    if {v['mechanism'] for v in value['variants']}!=set(MODES):raise ValueError('Missing mechanism budget')
    for v in value['variants']:
        sealed(v,'evaluation_id')
        if any(v.get(k) is not False for k in FLAGS):raise ValueError('Variant cannot grant acceptance')
        service=v['service'];sealed(service,'evaluation_id')
        if (service['requirements']!=r or service['design']!=spec['design']
                or service['reference_vehicle_candidate_id']!=value['selected_reference_vehicle_candidate_id']):
            raise ValueError('Variant service and benchmark requirements differ')
        if service['capacity_pphpd']<contract['minimum_capacity_pphpd'] or service['requirements']['headway_s']>contract['maximum_headway_s']:
            raise ValueError('Candidate service falls below the benchmark obligation')
        rows=v['capital_lines']+v['lifecycle_lines']
        if len({z['line_id'] for z in rows})!=len(rows):raise ValueError('Duplicate budget line')
        for z in rows:
            sealed(z,'line_id')
            if z['scope'] not in model_cost.SCOPES:raise ValueError('Unknown cost scope')
            if set(z['costs_iqd'])!=set(CASES) or any(type(n) not in (float,int) or not isfinite(n) or n<0 for n in z['costs_iqd'].values()):
                raise ValueError('Finite nonnegative budget line required')
        for i,x in enumerate(CASES):
            cap=fsum(z['costs_iqd'][x] for z in v['capital_lines']);whole=fsum(z['costs_iqd'][x] for z in rows)
            close(v['installed_capital_iqd'][x],cap);close(v['whole_life_npv_iqd'][x],whole)
            close(v['installed_capital_usd'][x],cap/fx);close(v['whole_life_npv_usd'][x],whole/fx)
            close(v['price_per_route_km_usd'][x],cap/fx/r['route_km'])
            close(v['price_per_track_km_usd'][x],cap/fx/r['route_km']/r['trackways'])
            close(v['funding_envelope_including_financing_usd'][x],cap/fx*(1+spec['capital']['financing_provision_fraction'][i]))
            for scope in model_cost.SCOPES:
                subtotal=fsum(z['costs_iqd'][x] for z in rows if z['scope']==scope)
                if subtotal<=0:raise ValueError('Missing positive cost scope')
                close(v['scope_totals_iqd'][scope][x],subtotal)
    chosen=next(v for v in value['variants'] if v['mechanism']==value['baseline_mechanism'])
    if chosen['evaluation_id']!=value['baseline_evaluation_id'] or chosen['price_per_route_km_usd']!=value['baseline_price_per_route_km_usd']:
        raise ValueError('Analysis baseline selection differs')
    return value


def markdown(value):
    base=next(v for v in value['variants'] if v['mechanism']==value['baseline_mechanism']);s=base['service'];fx=value['specification']['currency']['iqd_per_usd']
    lines=['# 30 km / 12 station cost benchmark','',
        '**Provisional engineering budget, not a supplier quotation or physical release.**',
        f"Analysis baseline: **{base['mechanism']}**, 30 route-km / 60 track-km, 12 stations including terminals, six 17 m cars, 276 places/train, 72 km/h, 1.0 m/s² and 120 s headway.",
        f"Conditional budget timetable: **{s['one_way_s']/60:.2f} min one-way**; **{s['active_trainsets']} active + {s['spare_trainsets']} reserve = {s['total_trainsets']} trainsets / {s['totalcars']} cars**. Offered capacity: 8,280 places/hour/direction. Launch jerk ramps and a 5% running-time recovery allowance enter the fleet budget; neither is an accepted timetable.",
        'Two production/construction shifts; 18 operating hours in two shifts. The result also calculates a separate 24-hour/three-shift operating and renewal sensitivity.','',
        '| Budget measure | Low | Base | High |','|---|---:|---:|---:|']
    for label,data,scale in [('Installed capital, USD million',base['installed_capital_usd'],1e6),('USD million per ROUTE km',base['price_per_route_km_usd'],1e6),('Installed capital, IQD billion',base['installed_capital_iqd'],1e9),('30-year whole-life NPV, USD million',base['whole_life_npv_usd'],1e6)]:
        lines.append('|'+label+'|'+ '|'.join(f'{data[x]/scale:,.2f}' for x in CASES)+'|')
    lines += ['', 'Installed capital includes rolling stock, spare trains, elevated civil works, stations/access, launch and auxiliary power, depot, production/tooling, land/utility allowances, testing, tax provision and contingency. Financing is shown separately in the machine-readable result.','',
        '| Initial capital category | Base USD million |','|---|---:|']
    groups={};civil_keys={z['key'] for z in value['civil']['capital_lines']}
    for row in base['capital_lines']:
        if row['key'] in civil_keys:group='Elevated guideway, foundations, erection and protected access'
        elif row['scope']=='rolling-stock':group='Delivered rolling stock and launch interfaces'
        elif row['key']=='auxiliary-charging-and-grid-increment':group='Auxiliary charging and grid capacity'
        elif row['key'].startswith(('launch-','rotary-','LIM-')):group='Launch machinery and traction power'
        elif row['scope']=='stations-power':group='Stations, accessible access, controls and turnbacks'
        elif row['scope']=='factory-tooling':group='Production buildings, yards and tooling'
        elif row['scope']=='land-utilities-depot':group='Depot, land and utility relocations'
        elif row['scope']=='fleet':group='Fleet component spares and commissioning'
        elif row['scope']=='recovery':group='Recovery assets'
        else:group=row['key'].replace('-',' ').capitalize()
        groups[group]=groups.get(group,0)+row['costs_iqd']['base']/fx/1e6
    lines += [f'|{name}|{number:,.2f}|' for name,number in groups.items()]
    lines += ['', '| Launch budget comparison, same service and common electrical rates | Base USD million / route-km |','|---|---:|']
    lines += [f"|{v['mechanism']}|{v['price_per_route_km_usd']['base']/1e6:,.2f}|" for v in value['variants']]
    lines += ['', 'These are cost hypotheses with overlapping uncertainty, not a qualified winner. The cable baseline is a stable analysis anchor. A different drive must supply its own force/contact/thermal evidence and installation details.',
        'Formation, bogies, seating arrangement and acceleration are revisable design hypotheses. The functional comparison fixes route/access, minimum offered capacity, maximum headway, comfort policy and accounting basis; a different vehicle needs its own quantities and service evaluator.',
        f"USD translation uses **IQD {fx:,.0f}/USD**, recorded from the [CBI](https://cbi.iq/) on 4 November 2026. The [motor]("+value['specification']['calibration']['motor_url']+') and [VFD]('+value['specification']['calibration']['vfd_url']+') catalogue observations calibrate bare equipment only.',
        '', 'The ledger calculates rail and complete 8 kg fastening assemblies from material, labour, processing and QA. Labour workplaces are not priced as complete factories. Converter capacities count all outgoing launch sites, not just two tracks.',
        '', 'The retained source vehicle price includes mass-reserve sensitivities. Here residual-account prices/process-hours are normalized back to the same base mass, so price uncertainty does not secretly change the service mass.',
        '', 'Important holds: actual available propulsion, independent braking, structural and soil qualification, turnback conflicts, one-sided-door interfaces, battery charge acceptance and complete installed mass. A +1% route grade can invalidate station-only coasting; high auxiliary load needs a revised service case.',
        '', 'Reproduce into a fresh directory:', '```bash','python -m engineering.design_search.line_benchmark --output build/my-line30-benchmark','python -m engineering.design_search.line_benchmark --verify --output build/my-line30-benchmark','```',
        '', '[Versioned criteria](../../../campaigns/line30-affordable-benchmark.toml) · [Analysis baseline selector](../../../engineering/analysis-baseline.toml) · [Complete quantities, assumptions and ledger](result.json) · [Receipt](manifest.json)',
        '',f"Requirements `{value['requirements_id']}`; evaluation `{value['evaluation_id']}`.",'']
    return '\n'.join(lines)


def run(output,root=ROOT):
    output=Path(output)
    if output.exists() or output.is_symlink():raise ValueError('Fresh immutable benchmark output required')
    value=evaluate(root);output.mkdir(parents=True)
    (output/'result.json').write_bytes(encoded(value));(output/'README.md').write_text(markdown(value))
    manifest=_seal(dict(schema='osr-line-budget-publication/1',evaluation_id=value['evaluation_id'],
        source_sha256=value['source_sha256'],files={n:digest(output/n) for n in ('result.json','README.md')},**FLAGS),'manifest_id')
    (output/'manifest.json').write_bytes(encoded(manifest))
    return dict(output=str(output),evaluation_id=value['evaluation_id'],manifest_id=manifest['manifest_id'],baseline_usd_per_route_km=value['baseline_price_per_route_km_usd'])


def verify(output,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());v=json.loads((output/'result.json').read_bytes())
    if (m.get('schema')!='osr-line-budget-publication/1' or m['manifest_id']!=identity({k:x for k,x in m.items() if k!='manifest_id'})
            or set(m['files'])!={'result.json','README.md'}
            or any(digest(output/n)!=sha for n,sha in m['files'].items())
            or any(digest(Path(root)/n)!=sha for n,sha in m['source_sha256'].items())):
        raise ValueError('Benchmark source or payload mismatch')
    validate_result(v,root);replay=evaluate(root)
    if v!=replay or (output/'README.md').read_text()!=markdown(replay) or m['evaluation_id']!=v['evaluation_id']:
        raise ValueError('Benchmark does not replay')
    return dict(verified=True,evaluation_id=v['evaluation_id'],manifest_id=m['manifest_id'],**FLAGS)


def compare(candidate,baseline):
    validate_result(candidate);validate_result(baseline)
    if candidate['requirements_id']!=baseline['requirements_id']:
        raise ValueError('Different transport requirements cannot use this cost benchmark')
    if candidate['rate_assumption_id']!=baseline['rate_assumption_id']:
        raise ValueError('Reprice both designs on the same rate assumptions before comparison')
    def selected(v):return next(x for x in v['variants'] if x['mechanism']==v['baseline_mechanism'])
    a,b=selected(candidate),selected(baseline)
    return dict(requirements_id=baseline['requirements_id'],candidate_evaluation_id=candidate['evaluation_id'],
        baseline_evaluation_id=baseline['evaluation_id'],
        base_usd_per_route_km_delta=a['price_per_route_km_usd']['base']-b['price_per_route_km_usd']['base'],
        physical_selection=None,scope='Planning-cost difference only; engineering eligibility remains separate')


def active_baseline(root=ROOT):
    root=Path(root);selector=tomllib.loads((root/SELECTOR).read_text())
    if (selector.get('schema')!='osr-analysis-baseline/1' or selector.get('hardware_selection') is not False
            or selector.get('criteria')!=SPEC or selector.get('purpose')!='equal-service-cost-analysis'):
        raise ValueError('Explicit analysis-only baseline selector required')
    output=root/selector['publication'];verify(output,root)
    return json.loads((output/'result.json').read_bytes())


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--verify',action='store_true')
    args=p.parse_args();print(json.dumps(verify(args.output) if args.verify else run(args.output)))


if __name__=='__main__':main()
