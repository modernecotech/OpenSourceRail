"""Calculated station-module budgets, separate from physics and full railways.

Rates, process times, support reserves and cycle lives are declared hypotheses.
No supplier confirmation, complete installed mass or physical release follows.
"""
import json
from math import ceil, fsum, isfinite, pi, sqrt
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity

PRODUCER = 'engineering/station_energy/arrestor_costs.py'
POLICY = 'engineering/station_energy/data/arrestor-cost-policy.json'
CASES = ('low', 'base', 'high')


def sources(root=ROOT):
    return {n:digest(Path(root)/n) for n in (PRODUCER, POLICY)}


def policy(root=ROOT):
    value = json.loads((Path(root)/POLICY).read_bytes())
    if (value.get('schema') != 'osr-arrestor-cost-policy/1'
        or value.get('supplier_confirmed') is not False
        or value.get('currency') != 'USD'):
        raise ValueError('Explicit provisional USD station-module cost policy required')
    for name, rate in value['rates'].items():
        numbers = rate if isinstance(rate, list) else [rate]
        if isinstance(rate, list) and len(rate) != 3:
            raise ValueError('Three declared cost cases required: '+name)
        if any(isinstance(x, bool) or not isinstance(x, (int,float))
            or not isfinite(x) or x < 0 for x in numbers):
            raise ValueError('Finite nonnegative cost assumption required: '+name)
    if (value['production_batch_sites'] <= 0 or value['life_years'] <= 0
        or value['real_discount_rate'] < 0
        or not 0 < value['productive_utilisation'] <= 1
        or any(not 0 < x <= 1 for x in value['rates']['purchase_yield'])
        or any(x <= 0 for x in value['rates']['active_store_life_cycles'])):
        raise ValueError('Positive production, life, cycle and yield assumptions required')
    for name, quantity in value['geometry'].items():
        numbers = quantity if isinstance(quantity, list) else [quantity]
        if any(type(x) not in (int, float) or not isfinite(x) or x <= 0 for x in numbers):
            raise ValueError('Positive finite geometry assumption required: '+name)
    if (not 0 < value['geometry']['rope_metal_fill_fraction'] <= 1
        or not 0 < value['operating_hours_per_day'] <= 24
        or value['production_shifts']*value['hours_per_shift'] > 24):
        raise ValueError('Compatible work/calendar and rope assumptions required')
    return value


def _seal(value, key):
    value[key] = identity(value)
    return value


def design_id(design):
    return identity({k:float(v) if type(v) in (int, float) else v
        for k,v in design.items()})


def prepare(root=ROOT):
    return policy(root), sources(root)


def estimate(inputs, result, *, cyclic_storage_closed, root=ROOT, context=None):
    p, source_context = prepare(root) if context is None else context
    rates, g = p['rates'], p['geometry']
    recovery = inputs['capture_entry_speed_m_s'] > 0
    stages = result['capture']['stages']
    booster = result['booster']
    if (stages is None or booster is None
        or (recovery and result['launch'] is None)):
        return dict(estimate_complete=False, cost=None,
            reason='A nominal motion/quantity model is unavailable for this event',
            physical_accepted=False, engineering_accepted=False)
    if not cyclic_storage_closed:
        return dict(estimate_complete=False, cost=None,
            reason='Repeated storage state has not closed within the invocation budget',
            physical_accepted=False, engineering_accepted=False)
    rows = []

    def purchased(name, quantity, unit, prices, mass=0.0, basis='Declared assembly allowance'):
        if quantity == 0:
            return
        rows.append(dict(component=name, quantity=quantity, unit=unit,
            estimated_installed_mass_kg=mass, route='estimated-purchased-assembly',
            factory_cost_usd={case:quantity*prices[i] for i,case in enumerate(CASES)},
            production_labour_h={case:0.0 for case in CASES},
            labour_included_in_assembly_allowance=True, supplier_confirmed=False,
            basis=basis))

    def fabricated(name, mass, material_rate, labour_rate):
        if mass == 0:
            return
        costs, hours = {}, {}
        for i, case in enumerate(CASES):
            h = mass*rates[labour_rate][i]/p['productive_utilisation']
            hours[case] = h
            direct = (mass/rates['purchase_yield'][i]*rates[material_rate][i]
                + h*rates['labour_usd_h'][i] + mass*(rates['machine_usd_kg'][i]
                    + rates['QA_usd_kg'][i] + rates['consumables_usd_kg'][i]))
            costs[case] = direct*(1+rates['overhead_fraction'][i])
        rows.append(dict(component=name, quantity=mass, unit='kg',
            estimated_installed_mass_kg=mass, route='calculated-local-manufacture',
            factory_cost_usd=costs, production_labour_h=hours,
            purchased_stock_kg={case:mass/rates['purchase_yield'][i] for i,case in enumerate(CASES)},
            supplier_confirmed=False, basis='Material/yield + paid process hours + machinery, QA, consumables and overhead; assumed route'))

    sizing = result['sizing']
    active = sizing['active_mass_kg'] if recovery else 0.0
    kind = sizing['kind']
    design = inputs['storage']['design']
    route = p['material_routes'].get(design_id(design)) if recovery else None
    if recovery and (not route or design_id(route['storage_design']) != design_id(design)):
        return dict(estimate_complete=False, cost=None,
            reason='An explicit material and manufacturing pricing route is required for this storage design',
            physical_accepted=False, engineering_accepted=False)
    if recovery:
        if kind == 'elastic':
            composite = route['material_family'] == 'composite'
            if route['material_family'] not in ('composite', 'spring-steel'):
                raise ValueError('Compatible explicit elastic material price route required')
            fabricated('active-composite-spring-material' if composite else 'active-steel-spring-material',
                active, 'composite_material_usd_kg' if composite else 'spring_steel_material_usd_kg',
                'composite_labour_h_kg' if composite else 'spring_labour_h_kg')
        elif kind == 'hydraulic':
            if route['material_family'] != 'pressure-vessel-steel':
                raise ValueError('Explicit vessel material route required')
            fabricated('accumulator-vessel-mass-hypothesis', active,
                'steel_material_usd_kg', 'vessel_labour_h_kg')
            volume = sizing['internal_volume_m3']
            gas_fraction = (design['precharge_pressure_pa']/design['max_pressure_pa'])**(1/design['polytropic_exponent'])
            oil = volume*(1-gas_fraction)*g['hydraulic_external_fluid_allowance']*g['hydraulic_fluid_density_kg_m3']
            purchased('hydraulic-fluid-including-external-volume-allowance', oil, 'kg',
                rates['hydraulic_fluid_usd_kg'], oil)
            purchased('pumps-valves-piping-return-reservoir-and-precharge', volume, 'precharge-m3',
                rates['hydraulic_balance_usd_per_m3'], mass=active*.25,
                basis='Declared pressure/flow package and nitrogen readiness allowance; no qualified vessel or flow map')
        elif kind == 'flywheel':
            if route['material_family'] != 'flywheel-steel':
                raise ValueError('Explicit rotor material route required')
            fabricated('active-flywheel-rim', active, 'steel_material_usd_kg', 'rotor_labour_h_kg')
            fabricated('flywheel-containment-and-hub-reserve', active*g['flywheel_containment_mass_to_rim'],
                'steel_material_usd_kg', 'fabricated_labour_h_kg')
            purchased('flywheel-bearing-vacuum-and-power-transfer-allowance',
                max(result['launch']['peak_mechanical_power_w'], 0.0)/1000, 'required-kW',
                rates['flywheel_balance_usd_per_kw'], mass=active*.5,
                basis='Required transfer-power calibration only; rotor containment, bearings and operating speed remain unverified')
        else:
            if route['material_family'] != 'spring-steel':
                raise ValueError('Explicit sensitivity material price route required')
            fabricated('active-declared-energy-density-material', active,
                'spring_steel_material_usd_kg', 'spring_labour_h_kg')
        fabricated('storage-housing-and-access-reserve',
            sizing['envelope_volume_m3']*g['store_housing_kg_per_envelope_m3'],
            'steel_material_usd_kg', 'fabricated_labour_h_kg')

    max_turn_load, ropes, drums, load_group_fasteners = 0.0, 0.0, 0.0, 0
    linkages = []
    for stage in stages:
        linkages.extend(((stage['distance_m'], stage['required_peak_force_n']),
            (stage['store_travel_m'], stage['store_force_upper_bound_n'])))
    launch_points = 0
    launch_force_kn = 0.0
    if recovery:
        launch = result['launch']
        ratio = g['launcher_displacement_ratio']
        for fraction in inputs['launch']['force_fractions']:
            if fraction > 0:
                launch_points += 1
                force = launch['required_peak_force_n']*fraction
                launch_force_kn += force/1000
                linkages.extend(((launch['distance_m'],force),
                    (launch['distance_m']/ratio,force*ratio)))
    for length, force in linkages:
            tension = force*g['dynamic_force_allowance']
            area = tension/g['rope_working_stress_pa']
            nominal_d = sqrt(4*area/(pi*g['rope_metal_fill_fraction']))
            drum_d = nominal_d*g['minimum_drum_diameter_to_rope_diameter']
            rope_length = (length+g['cable_tail_m_per_stage']+2*pi*drum_d)*g['rope_stock_allowance']
            ropes += area*g['rope_density_kg_m3']*rope_length
            width = nominal_d*g['drum_width_to_rope_diameter']
            drums += g['rope_density_kg_m3']*(
                2*pi*(drum_d/2)**2*g['drum_plate_thickness_m']*g['drum_web_solid_fraction']
                + pi*drum_d*width*g['drum_plate_thickness_m'])
            max_turn_load = max(max_turn_load, 2*tension)
            load_group_fasteners += max(g['minimum_fasteners_per_group'],
                ceil(2*tension/g['assumed_fastener_working_load_n']))
    fabricated('train-and-store-side-rope-stock', ropes,
        'rope_material_usd_kg', 'fabricated_labour_h_kg')
    fabricated('rope-sized-drums-and-sheaves', drums,
        'steel_material_usd_kg', 'fabricated_labour_h_kg')
    frame = (len(stages)*g['stage_frame_kg']
        + launch_points*g['launcher_fixed_frame_kg_per_point']
        + launch_force_kn*g['launcher_frame_kg_per_kn'])
    fabricated('capture-and-launch-frame-reserve', frame,
        'steel_material_usd_kg', 'fabricated_labour_h_kg')
    purchased('overrunning-clutches-release-locks-and-return-drives', len(stages)+launch_points,
        'assemblies', rates['clutch_release_usd_each'], mass=frame*.15)
    max_store_force = max((s['store_force_upper_bound_n'] for s in stages), default=0.0)
    purchased('store-side-transmission-load-allowance', max_store_force/1e6, 'MN',
        rates['transmission_usd_per_mn'], mass=max_store_force/1e6*500.)
    purchased('guarded-control-isolation-and-protection', 1., 'site',
        rates['guarded_control_isolation_usd_site'], mass=g['controls_isolation_mass_kg'])
    purchased('readiness-precharge-preload-and-commissioning-allowance', 1., 'site',
        rates['readiness_commissioning_usd_site'],
        basis='Precharge/minimum-speed/preload readiness and commissioning reserve; these are not recovered arrival energy')
    powered_path = booster['distance_m']
    source_kw = booster['peak_source_power_w']/1000
    purchased('remaining-booster-mechanical-hardware-allowance', powered_path, 'active-path-m',
        rates['booster_factory_hardware_usd_m'], mass=powered_path*g['booster_hardware_kg_per_m'],
        basis='Factory-gate allowance per active acceleration path metre; delivery/civil/installation separate. Installed powered length and available thrust unknown')
    purchased('booster-grid-conversion-and-protection', source_kw, 'required-kW',
        rates['booster_grid_usd_kw'], mass=source_kw*g['booster_grid_kg_per_kw'])
    loss_keys = ('capture_conversion_loss_j', 'store_conversion_loss_j', 'overflow_j',
        'standing_loss_j', 'release_loss_j')
    store_loss = fsum(result['storage'][k] for k in loss_keys)
    booster_loss = booster['source_energy_j'] - 0.5*inputs['effective_mass_kg']*(
        booster['exit_speed_m_s']**2-booster['entry_speed_m_s']**2)
    average_heat_kw = (store_loss+max(0., booster_loss))/inputs['headway_s']/1000
    cooling_kw = average_heat_kw*g['cooling_rating_margin']
    purchased('cooling-and-safe-overflow-disposal-allowance', cooling_kw, 'average-required-kW-margin',
        rates['thermal_usd_kw'], mass=cooling_kw*g['cooling_kg_per_kw'],
        basis='Conservative thermal/disposal reserve; overflow path and transient temperatures are not validated')
    joint_locations = 8*(len(stages)+launch_points)+(8 if recovery else 0)
    fasteners = joint_locations*g['minimum_fasteners_per_group']+load_group_fasteners
    purchased('module-joint-and-loaded-anchor-fastener-sets', fasteners, 'complete-sets',
        rates['fastener_set_usd'], mass=fasteners*g['fastener_set_mass_kg'],
        basis='General module joints plus separate pulley/attachment groups under an assumed bolt working load; prying, fatigue, breakout and actual joint capacity unverified')
    if joint_locations:
        hours = {c:joint_locations*rates['module_joint_assembly_h'][i]/p['productive_utilisation']
            for i,c in enumerate(CASES)}
        rows.append(dict(component='factory-module-bolted-assembly-and-final-check',
            quantity=joint_locations, unit='joint-locations', estimated_installed_mass_kg=0.,
            route='calculated-final-assembly-service', production_labour_h=hours,
            factory_cost_usd={c:hours[c]*rates['labour_usd_h'][i]+joint_locations*rates['final_joint_QA_usd'][i]
                for i,c in enumerate(CASES)}, supplier_confirmed=False,
            basis='Factory-module bolting/final inspection beyond stock fabrication; onsite anchoring/alignment remains in site labour'))
    wiring = ((result['capture']['total_distance_m'] or 0.)
        + (result['launch']['distance_m'] if result['launch'] else 0.)
        + powered_path+g['field_service_tail_m'])
    purchased('field-control-wiring-and-local-connector-supply', wiring, 'route-m',
        rates['field_service_supply_usd_m'], mass=wiring*g['field_service_kg_m'],
        basis='Control/local-service supply reserve; site routing labour separate, bulk power feeder reserve in grid assembly allowance; detailed voltage/current/fault sizing pending')

    mass = fsum(row['estimated_installed_mass_kg'] for row in rows)
    load_proxy_n = mass*9.80665+max_turn_load
    civil_area = load_proxy_n/(1000*g['civil_reference_pressure_kpa'])
    civil_volume = g['minimum_foundation_m3']+civil_area*g['foundation_allowance_depth_m']
    cycles = p['operating_hours_per_day']*3600/inputs['headway_s']*p['operating_days_per_year']
    if (not isfinite(cycles) or cycles <= 0
        or any(p['life_years']*cycles/x > 1000 for x in rates['active_store_life_cycles'])):
        return dict(estimate_complete=False, cost=None,
            reason='Declared lifecycle event count exceeds this bounded estimate domain',
            physical_accepted=False, engineering_accepted=False)
    annual_kwh = (booster['source_energy_j']*cycles/3.6e6
        + (g['idle_grid_kw_site']+cooling_kw*g['cooling_grid_fraction'])
            *p['operating_hours_per_day']*p['operating_days_per_year'])
    rate, years = p['real_discount_rate'], p['life_years']
    annuity = fsum((1+rate)**-year for year in range(1, years+1))
    totals, hours = {}, {}
    for i, scenario in enumerate(CASES):
        factory = fsum(row['factory_cost_usd'][scenario] for row in rows)
        h = fsum(row['production_labour_h'][scenario] for row in rows)
        tooling = rates['process_route_tooling_usd'][i]/p['production_batch_sites']
        delivery = mass/1000*rates['freight_usd_tonne_km'][i]*rates['factory_to_site_km']
        erection = mass/1000*rates['erection_usd_tonne'][i]
        civil = civil_volume*rates['concrete_installed_usd_m3'][i]
        install_labour = rates['civil_labour_h_site'][i]*rates['labour_usd_h'][i]
        installed = factory+tooling+delivery+erection+civil+install_labour
        annual = (annual_kwh*rates['electricity_usd_kwh'][i]
            + rates['annual_inspection_h_site'][i]*rates['labour_usd_h'][i]
            + factory*rates['annual_parts_fraction'][i])
        active_cost = fsum(row['factory_cost_usd'][scenario] for row in rows
            if row['component'].startswith(('active-', 'accumulator-vessel')))
        interval = rates['active_store_life_cycles'][i]/cycles
        times = []; renewal_pv = 0.0; replacement = interval
        while active_cost > 0 and replacement < years-1e-9:
            times.append(replacement)
            renewal_pv += (active_cost+tooling+delivery*.25+erection*.25)/(1+rate)**replacement
            replacement += interval
        terminal = installed*rates['decommission_fraction'][i]/(1+rate)**years
        totals[scenario] = dict(factory_usd=factory, tooling_allocation_usd=tooling,
            delivery_usd=delivery, erection_usd=erection, civil_reserve_usd=civil,
            installation_labour_usd=install_labour, installed_usd=installed,
            annual_operating_maintenance_usd=annual, renewal_pv_usd=renewal_pv,
            assumed_renewal_years=times, decommission_pv_usd=terminal,
            thirty_year_npv_usd=installed+annual*annuity+renewal_pv+terminal)
        hours[scenario] = h
    launch_distance = result['launch']['distance_m'] if result['launch'] else 0.0
    return _seal(dict(schema='osr-arrestor-module-estimate/1', estimate_complete=True,
        physical_candidate_id=None, comparison_scope=p['comparison_scope'],
        price_basis=p['price_basis'], source_class=p['source_class'], supplier_confirmed=False,
        factory_basis=p['factory_basis'], new_factory_capital_included=False,
        source_sha256=source_context, pricing_material_route=route,
        components=rows, costs=totals,
        estimated_site_equipment_mass_kg=mass, active_storage_element_mass_kg=active,
        independent_capture_units=len(stages), launcher_force_points=launch_points,
        capture_launch_bolted_joint_locations=joint_locations,
        capture_launch_fastener_sets=fasteners,
        booster_supports_allowance=ceil(powered_path/g['booster_support_pitch_m_hypothesis']),
        booster_fastener_sets_allowance=ceil(powered_path/g['booster_support_pitch_m_hypothesis'])*g['booster_fasteners_per_support_hypothesis'],
        booster_support_hardware_included_in_per_metre_allowance=True,
        fastener_working_load_is_assumed=True, joint_capacity_verified=False,
        field_service_route_m=wiring,
        required_maintenance_bay_area_m2=(sizing['envelope_volume_m3']**(1/3)
            + 2*g['maintenance_clearance_m'])**2 if recovery else 0.,
        maintenance_envelope_is_cube_proxy=True,
        complete_installed_mass=False, local_pulley_turn_load_bound_n=max_turn_load,
        foundation_allowance_m3=civil_volume, foundation_load_proxy_n=load_proxy_n,
        foundation_reference_area_m2=civil_area,
        foundation_reference_pressure_is_assumed=True, foundation_is_engineering_design=False,
        annual_cycles=cycles, cyclic_storage_closed=cyclic_storage_closed,
        annual_purchased_energy_kwh=annual_kwh, average_heat_kw=average_heat_kw,
        available_storage_and_booster_duty_verified=False,
        startup_minimum_energy_quantified=False,
        startup_readiness_cost_is_declared_allowance=True,
        production_labour_h=hours, production_shifts=p['production_shifts'], civil_shifts=p['civil_shifts'],
        operating_shifts=3 if p['operating_hours_per_day'] > 18 else 2,
        production_labour_scope='Additional own-factory process hours; supplier internal hours and procurement lead times remain unknown',
        production_days_at_one_position={c:hours[c]/(p['production_shifts']*p['hours_per_shift']) for c in CASES},
        batch_sites=p['production_batch_sites'], tooling_charged_once_per_batch=True,
        interface_allowance_per_train_usd={c:g['per_train_interface_reserve_kg'][i]*g['interface_assembly_usd_per_kg'][i] for i,c in enumerate(CASES)},
        fleet_and_corridor_total_usd=None,
        required_capture_path_m=result['capture']['total_distance_m'],
        required_launch_path_m=launch_distance, required_booster_path_m=powered_path,
        installed_powered_length_m=None,
        reset_return_lower_bound_s=g['reset_fixed_s']+max(
            [s['distance_m']/g['reset_return_speed_m_s'] for s in stages]
            + [launch_distance/g['reset_return_speed_m_s']]),
        reset_drive_capability_verified=False,
        limitations=p['limitations'], physical_accepted=False, engineering_accepted=False,
        manufacturing_release=False, operating_release=False, selected_reference_changed=False), 'cost_evaluation_id')
