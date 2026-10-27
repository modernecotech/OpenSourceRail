"""Same-candidate comfort/load comparisons, without a hover or installed-mass claim.

The immutable parent packets supply executed *component samples*. Changing cabin
stock or a research passenger cap changes the required load, not those samples.
In particular a positive force-minus-weight is not a stable operating point.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path
import tarfile
import tomllib

from engineering.vehicle_optimisation import equipment, hvac
from engineering import research_ancestry

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = 'osr-comfort-systems/1'
BODY_ID = '94ac95612ac6f5d2800a2e007f79361addc8f48407b2274bf104debd3e8d3354'
MAGNET_ID = '397ddf033ab98afaea053acaa3047249a3329f542f1f5e52a6eb1b466b9662e0'
PARENT_COMPOSITION_ID = 'd6059686fbf09a1b1d06e91c39935f89b79b6f95dd3cbd8fe0349dea04c879c5'
PARENT_TARE_KG = 17633.93699803974
G = 9.80665
MODULES = 24
RESERVE = 1.3
ANCESTRY_REVISION = '92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164'
FLAGS = dict(configuration_adopted=False, engineering_accepted=False,
             physical_accepted=False, installed_mass_complete=False,
             stable_hover_established=False, comfort_qualified=False,
             manufacturing_release=False)
PARENT_PACKETS = {
    'docs/design-engine/halbach-scaling/comparison.json': '556bc0acd5490f76bfe2d222576e4abedf7a028f43a8d3467975e6adcbcadb92',
    'docs/design-engine/halbach-scaling/finite.json': '4fe7dbe14a606f3918de6f7a0b8b8c9e35407eeb9a45887d5c687efa2e72ccca',
    'docs/design-engine/ferrite-maglev/engineering-readiness/confirmation-artifacts.tar.gz': '00107df6ef16972829cc472a91697dcc3f17deea2ab7f892f60226a4b3b7f7dd',
}


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def _number(value, name, minimum=0.):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError('finite '+name+' >= '+str(minimum)+' required')
    return float(value)


def _hash(path):
    with Path(path).open('rb') as stream:
        return sha256(stream.read()).hexdigest()


def _source_check(root, bindings):
    try:return research_ancestry.verify(root, bindings, source_revision=ANCESTRY_REVISION)
    except ValueError as exc:raise ValueError('retained source differs: '+str(exc)) from exc


@lru_cache(maxsize=4)
def _parent(root_name):
    """Pin numerical records independently of the changing readiness aggregate."""
    root = Path(root_name)
    _source_check(root, PARENT_PACKETS)
    comparison = json.loads((root/next(iter(PARENT_PACKETS))).read_bytes())
    vehicle = next(v for v in comparison['vehicle_candidates'] if v['candidate_id'] == BODY_ID)
    rows = [r for r in comparison['comparisons'] if r['body_candidate_id'] == BODY_ID
            and r['magnet_component_id'] == MAGNET_ID]
    if len(rows) != 1 or rows[0]['composition_id'] != PARENT_COMPOSITION_ID:
        raise ValueError('parent physical composition differs')
    if rows[0]['comparison_empty_kg_per_car'] != PARENT_TARE_KG:
        raise ValueError('parent accounted tare differs')
    _source_check(root, vehicle['source_sha256'])
    old_fitout = vehicle['equipment']
    # equipment is the complete source-bound record in this parent revision.
    if not isinstance(old_fitout, dict):
        raise ValueError('explicit retained fitout record required')
    if old_fitout['id'] != 'aluminium-sandwich-ES2-reference/solar-laminated-6.76mm':
        raise ValueError('unexpected retained fitout')
    if [r['id'] for r in vehicle['replacement_changes']] != ['frame', 'doors-windows', 'hvac']:
        raise ValueError('interior allowance survival requires a new trace')
    source_body = json.loads((root/'engineering/ferrite_maglev/data/candidate-parent-94ad.json').read_bytes())['configuration']
    station_name = 'engineering/ferrite_maglev/station-structure.toml'
    if source_body['source_sha256'].get(station_name) != _hash(root/station_name):
        raise ValueError('ancestor interior allocation source differs')
    station = tomllib.loads((root/station_name).read_text())
    interior = station['body']['cases']['central']['interior_kg']
    if interior != 800.:
        raise ValueError('retained interior allocation changed')
    removed = json.loads((root/'engineering/ferrite_maglev/data/candidate-replaced-cartridges.json').read_bytes())
    retained = json.loads((root/'engineering/ferrite_maglev/data/candidate-retained-body-stock.json').read_bytes())
    if any('seat' in p['id'].lower() or 'interior' in p['id'].lower()
           for p in removed['parts']+retained['parts']):
        raise ValueError('individual interior stock overlaps the retained allocation')
    residual = source_body['controlled_tare_kg']-removed['mass_kg_per_car']-source_body['magnetic']['winding_copper_kg_per_car']-retained['mass_kg_per_car']
    removed_allocations = sum(r['removed_kg_per_car'] for r in vehicle['replacement_changes'] if r['removal_kind'] == 'inherited-allocation')
    if residual-removed_allocations < interior:
        raise ValueError('remaining allocation insufficient for retained interior')
    finite = json.loads((root/'docs/design-engine/halbach-scaling/finite.json').read_bytes())
    _source_check(root, finite['source_sha256'])
    small = finite['rows'][0]
    if (small['candidate_id'] != MAGNET_ID or small['gap_m'] != .012
            or small['execution_status'] != 'completed' or not small['force_credit']
            or not small['full_source_converged']):
        raise ValueError('12 mm sample lacks matching executed full-source evidence')
    planned = comparison['finite_plan'][0]
    if (planned['candidate_id'] != MAGNET_ID or planned['current_body_candidate_id'] != BODY_ID
            or planned['gap_m'] != .012 or planned['temperature_C'] != 80.
            or planned['currents_A'] != {} or planned['field_request_id'] != finite['request_id']
            or planned['state_id'] != small['state_id']
            or planned['finite_Fz_contours_N'] != [c['force_N'][2] for c in small['analysis']['air_contour_results']]):
        raise ValueError('12 mm sample operating-state binding differs')
    samples = [dict(sample_id=small['evaluation_id'], gap_m=.012, temperature_C=80., currents_A={},
                    contour_Fz_N=[c['force_N'][2] for c in small['analysis']['air_contour_results']],
                    source='docs/design-engine/halbach-scaling/finite.json#rows/0')]
    archive_name = 'docs/design-engine/ferrite-maglev/engineering-readiness/confirmation-artifacts.tar.gz'
    with tarfile.open(root/archive_name, 'r:gz') as archive:
        data = {}
        for name in ('request.json', 'result.json', 'manifest.json'):
            member = archive.getmember('confirmation/'+name)
            if not member.isfile() or member.size > 8_000_000:
                raise ValueError('bounded ordinary retained JSON member required')
            data[name] = archive.extractfile(member).read()
    request, result, manifest = (json.loads(data[n]) for n in ('request.json', 'result.json', 'manifest.json'))
    for name in ('request.json', 'result.json'):
        if manifest['files_sha256'][name] != sha256(data[name]).hexdigest():
            raise ValueError('confirmation member digest differs')
    _source_check(root, result['source_sha256'])
    context = request['candidate']['mass_comparison_context']
    if (context['parent_composition_id'] != PARENT_COMPOSITION_ID
            or context['body_candidate_id'] != BODY_ID
            or request['candidate']['component_id'] != MAGNET_ID):
        raise ValueError('confirmation parent identity differs')
    for state in result['comparisons']['operating_states']:
        if state['candidate_id'] != MAGNET_ID or state['state']['currents_A'] != {}:
            raise ValueError('only matching zero-current samples may be reused')
        samples.append(dict(sample_id=result['evaluation_id']+'/'+state['case'],
            gap_m=state['state']['gap_m'], temperature_C=state['state']['temperature_C'], currents_A={},
            contour_Fz_N=state['observed']['contour_Fz_N'], source=archive_name+'#'+state['case']))
    for sample in samples:
        pair = sample['contour_Fz_N']
        if len(pair) != 2 or any(not math.isfinite(f) for f in pair):
            raise ValueError('two finite contour samples required')
        sample['vertical_contour_relative_difference'] = abs(pair[1]-pair[0])/max(abs(f) for f in pair)
        sample['numerical_force_convergence_established'] = False
        sample['sampled_contours_are_confidence_bounds'] = False
    ancestry=PARENT_PACKETS | vehicle['source_sha256'] | finite['source_sha256'] | result['source_sha256']
    provenance=_source_check(root,ancestry)
    return dict(vehicle=vehicle, fitout=old_fitout, samples=samples,
        interior_allocation_kg=interior, remaining_unlocated_allocation_kg=residual-removed_allocations,
        ancestry_source_revision=ANCESTRY_REVISION,
        ancestry_source_sha256=provenance['ancestry_source_sha256'],
        source_sha256={**provenance['source_sha256'],
            'engineering/comfort_options/systems.py':_hash(Path(__file__))})


def parent_evidence(root=ROOT):
    root = Path(root).resolve()
    value = _parent(str(root))
    # Cache parsing, never permission to reuse stale evidence after an edit.
    provenance=_source_check(root, value['ancestry_source_sha256'])
    current_sources={**provenance['source_sha256'],
        'engineering/comfort_options/systems.py':_hash(Path(__file__))}
    if current_sources!=value['source_sha256']:raise ValueError('Retained evidence projection source changed; restart before reuse')
    return deepcopy(value)


def support_comparison(accounted_tare_kg, passenger_limit, samples):
    """Required loads against unchanged samples, with a retained overcrowding case."""
    tare = _number(accounted_tare_kg, 'accounted tare')
    if type(passenger_limit) is not int or not 2 <= passenger_limit <= 160:
        raise ValueError('total passenger cap2..160 including two wheelchair users required')
    result = []
    for passengers in sorted({0, passenger_limit, 80, 100, 120, 160}):
        for additional in (0., 1000., 2000.):
            mass = tare+passengers*75.+additional
            mean = mass*G/MODULES
            reserve = RESERVE*mean
            states = []
            for sample in samples:
                pair = sample['contour_Fz_N']
                delta = [f-mean for f in pair]
                margins = [f-reserve for f in pair]
                spread = abs(pair[1]-pair[0])
                states.append(dict(sample_id=sample['sample_id'], gap_m=sample['gap_m'],
                    temperature_C=sample['temperature_C'], currents_A={}, contour_Fz_N=pair,
                    force_minus_mean_N_per_module=delta,
                    force_minus_1_3_required_N_per_module=margins,
                    both_sampled_contours_exceed_mean=min(delta) >= 0,
                    both_sampled_contours_exceed_1_3_load=min(margins) >= 0,
                    smaller_sampled_contour_1_3_margin_N=min(margins),
                    vertical_contour_spread_N=spread,
                    vertical_contour_relative_difference=sample['vertical_contour_relative_difference'],
                    contour_spread_exceeds_smaller_contour_reserve_margin=spread > abs(min(margins)),
                    fixed_gap_force_exceeds_mean_at_both_contours=min(delta) > 0,
                    force_at_other_gap_or_current=None, equilibrium_solved=False,
                    numerical_force_convergence_established=False,
                    sampled_contours_are_confidence_bounds=False, **FLAGS))
            result.append(dict(passengers_total=passengers,
                case_purpose='proposed-cap' if passengers == passenger_limit else 'empty-control' if passengers == 0 else 'retained-normal-control' if passengers == 120 else 'retained-credible-overcrowding-control' if passengers == 160 else 'research-demand-control',
                accounted_passenger_mass_kg=passengers*75., unclosed_additional_mass_kg=additional,
                additional_mass_scope='Sensitivity for unclosed installed equipment, mobility devices, luggage and other uncounted mass; no probability or completeness claim',
                accounted_loaded_kg_per_car=mass, accounted_loaded_kg_six_cars=6*mass,
                mean_weight_N_per_module=mean, required_1_3_N_per_module=reserve, samples=states,
                load_distribution_qualified=False, structural_load_reduction_authorised=False))
    return dict(cases=result, passenger_mass_kg_study_average=75., wheelchairs_included_in_passenger_count=2,
        mobility_device_and_luggage_mass_known=False, cap_enforcement_qualified=False,
        structural_and_credible_overcrowding_cases_reduced=False,
        scope='Lower payload improves arithmetic force reserve. At a fixed PM gap it can also produce excess upward force. Vertical/lateral stability, load distribution, current authority and safe hover are not established.', **FLAGS)


def service_comparison(passenger_limit, active_doors, *, accounted_tare_kg=None):
    if (type(passenger_limit) is not int or not 2 <= passenger_limit <= 160
            or type(active_doors) is not int or active_doors not in (2,3,4)):
        raise ValueError('explicit cap2..160 and2..4 active platform doors required')
    required = 6*passenger_limit*3600/14400
    flow = []
    for exchange in (.25, .5, 1.):
        for per_door in (1., 1.5, 2.):
            flow.append(dict(exchange_fraction_hypothesis=exchange,
                flow_pax_s_per_opening_hypothesis=per_door,
                proposed_exchange_time_s=passenger_limit*exchange/(active_doors*per_door),
                baseline_two_active_doors_same_cap_exchange_time_s=passenger_limit*exchange/(2*per_door),
                fixed_door_cycle_access_time_s=None, dwell_qualified=False))
    return dict(cars=6, proposed_total_passengers_per_car=passenger_limit,
        retained_normal_passengers_per_car=120, retained_AW3_passengers_per_car=160,
        target_normal_pphpd=14400, required_headway_s_arithmetic=required,
        at_180_s_pphpd=6*passenger_limit*3600/180,
        capacity_sensitivities=[dict(headway_s=h, pphpd=6*passenger_limit*3600/h) for h in (120,150,180)],
        frequency_ratio_to_180s=180/required,
        same_cycle_trainsets_ratio_to_180s=180/required,
        at_target_accounted_moving_tonnes_per_hour=None if accounted_tare_kg is None else
            14400*(75.+_number(accounted_tare_kg, 'accounted tare')/passenger_limit)/1000.,
        equal_service_mass_flow_scope='Fully occupied arithmetic. Smaller loads per train require more train departures and more empty-car mass movements at equal throughput; not electrical consumption or a cost model.',
        ratio_basis='Frequency arithmetic at an unchanged cycle, not a new fleet plan or current Baghdad fleet multiplier',
        baseline_doors_total=4, baseline_active_doors_at_normal_platform=2,
        proposed_active_doors_at_platform=active_doors, normal_boarding_flow_halved=False,
        declared_exchange_hypotheses=flow, safe_headway_s=None, dwell_qualified=False,
        installed_fleet_count=None, revised_charging_equipment=None,
        revised_platform_egress_and_evacuation=None, fleet_station_power_and_cost_complete=False,
        one_sided_platform_compatibility_qualified=False,
        cap_enforcement_qualified=False, **FLAGS)


def thermal_load(*, passengers, doors_total, active_doors, solar_factor, U_W_m2K,
                 humid=False, root=ROOT):
    """Adapt the old four-aperture shell explicitly; keep per-person ventilation."""
    if (type(doors_total) is not int or type(active_doors) is not int
            or doors_total not in (2,3,4) or active_doors not in (2,3,4) or active_doors > doors_total):
        raise ValueError('explicit2..4 door topology required')
    s = hvac.default_scenario(name='50C-humid-doors60s' if humid else '50C-dry-doors30s',
        passengers=passengers, outdoor_RH=.30 if humid else .15,
        door_open_s=60. if humid else 30., doors_open=active_doors,
        glazing_m2=24.+doors_total, solar_factor=solar_factor, glazing_U_W_m2K=U_W_m2K,
        fresh_air_L_s_per_person=6., door_cycle_s=180.)
    load = hvac.heat_load(s)
    door_area = s['door_width_m']*s['door_height_m']
    correction = (4-doors_total)*door_area*(load['upper_panel_U_W_m2K']-2.5)*(s['outdoor_C']-s['indoor_C'])
    load['sensible_components_W']['opaque_shell'] += correction
    raw_s = sum(load['sensible_components_W'].values())
    raw_l = sum(load['latent_components_W'].values())
    load.update(sensible_kWthermal=max(raw_s,0.)/1000., total_kWthermal=(max(raw_s,0.)+max(raw_l,0.))/1000.,
        signed_net_heat_W=raw_s+raw_l, heating_required_W=max(-raw_s,0.),
        HVAC_electric_scenario_kWe=None, complete_services_kWe=None,
        actual_hot_condition_electrical_input_kWe=None,
        opaque_door_topology_correction_W=correction,
        opaque_shell_geometry=dict(doors_total=doors_total, fixed_glazing_m2=24.,
            door_glazing_m2=float(doors_total), removed_apertures_replaced_with_upper_panel=4-doors_total,
            replacement_panel_U_W_m2K=load['upper_panel_U_W_m2K'], opaque_door_U_hypothesis_W_m2K=2.5),
        door_recurrence_is_train_headway=False,
        per_person_fresh_air_reduced=False, actual_glazing_properties_verified=False,
        blower_heat_basis='Retained1000W whole-car hypothesis; package-count-dependent fan/motor heat unknown',
        electrical_basis='No supplier50C capacity/COP/input map: thermal load does not establish electrical input')
    return load


def cooling_comparison(load_kWthermal, installed_units=5):
    _number(load_kWthermal, 'thermal load')
    if type(installed_units) is not int or installed_units not in (2,3,4,5):
        raise ValueError('explicit2/3/4/5-package quantity proposal required')
    rows = []
    for count in (2, 3, 4, 5):
        for failed in (0, 1):
            nominal = 33.*(count-failed)
            rows.append(dict(units_proposed=count, failed_units=failed,
                same_as_evaluated_candidate=count == installed_units,
                hardware_supplier_reference_kg=192.*count,
                available_nameplate_kWthermal=nominal,
                required_fraction_of_nameplate=load_kWthermal/nominal,
                nameplate_headroom_kWthermal=nominal-load_kWthermal,
                necessary_nameplate_screen='nominal-insufficient' if load_kWthermal > nominal else 'conditional-nameplate-covers-load',
                actual_50C_capacity_kWthermal=None, actual_50C_input_kWe=None,
                actual_50C_capacity_verified=False, installed_mass_kg=None,
                quantity_change_requires_new_mounts_ducts_power_and_clearance=True,
                independent_revised_candidate_selected=False, **FLAGS))
    return rows


def _layout_fields(layout):
    """Strict generated-record adapters; schema keys are fixed with the layout worker."""
    return (layout['passenger_limit'], layout['doors_total'], layout['active_doors_per_platform'],
            layout['seating_stock']['total_mass_kg'], layout['infill_stock']['total_mass_kg'])


def evaluate(layout, glazing, *, root=ROOT, hvac_units=5):
    """Compose explicit validated layout/glazing records against the retained parent."""
    from engineering.comfort_options import layout as layouts
    from engineering.comfort_options import glazing as glazings
    root = Path(root).resolve()
    layouts.validate_layout(layout, root=root)
    glazings.validate(glazing, doors_total=layout['doors_total'])
    cap, doors, active, seat_mass, infill_mass = _layout_fields(layout)
    if type(cap) is not int or not 2 <= cap <= 160 or doors not in (2,3,4) or not 2 <= active <= doors:
        raise ValueError('unsupported comfort study topology')
    if type(hvac_units) is not int or hvac_units not in (2,3,4,5):
        raise ValueError('explicit HVAC quantity2/3/4/5 required')
    seat_mass = _number(seat_mass, 'counted seat material')
    infill_mass = _number(infill_mass, 'counted infill material')
    if glazing['total_area_m2'] != 24.+doors:
        raise ValueError('door glass counted once in glazing only')
    parent = parent_evidence(root)
    old = parent['fitout']
    old_door = old['door']
    removed_leaf = old_door['physical_leaf_stock_mass_kg']
    removed_mechanisms = old_door['mechanism_reference_mass_kg']
    removed_glazing = old['glazing']['counted_material_mass_kg']
    if not math.isclose(removed_leaf+removed_mechanisms+removed_glazing, old['material_plus_reference_subtotal_kg'], abs_tol=1e-8):
        raise ValueError('old fitout disjoint inventory does not close')
    new_leaf = removed_leaf*doors/old_door['door_count']
    new_mechanisms = old_door['mechanism_reference_mass_kg_each']*doors
    new_glazing = _number(glazing['counted_material_mass_kg'], 'counted glazing material')
    seat_excess = max(0., seat_mass-parent['interior_allocation_kg'])
    # Resolve known seat material inside a retained account, without saving the rest.
    remaining_interior_budget = max(0., parent['interior_allocation_kg']-seat_mass)
    delta = new_leaf+new_mechanisms+new_glazing+infill_mass-removed_leaf-removed_mechanisms-removed_glazing+seat_excess+192.*(hvac_units-5)
    tare = PARENT_TARE_KG+delta
    physical = dict(parent_body_candidate_id=BODY_ID, parent_composition_id=PARENT_COMPOSITION_ID,
        magnet_component_id=MAGNET_ID, module_count=MODULES,
        layout_id=layout['physical_geometry_id'], glazing_id=glazing['physical_definition_id'],
        HVAC=dict(family='bus-ul700-electric', units=hvac_units),
        retained_interior_allocation_kg=parent['interior_allocation_kg'],
        passenger_limit=cap, passenger_mass_kg_study_average=75.)
    candidate_id = identity(physical)
    mass = dict(parent_accounted_tare_kg_per_car=PARENT_TARE_KG,
        removed=dict(door_leaf_stock_kg=removed_leaf, mechanism_reference_kg=removed_mechanisms,
                     glazing_and_retention_stock_kg=removed_glazing),
        added=dict(door_leaf_stock_kg=new_leaf, mechanism_reference_kg=new_mechanisms,
                   glazing_and_retention_stock_kg=new_glazing, aperture_infill_stock_kg=infill_mass),
        old_ancestor_500kg_door_and_500kg_glazing_allocations_removed_again=False,
        door_leaf_glazing_counted=False, door_glass_owned_only_by='glazing',
        original_interior_budget_kg=parent['interior_allocation_kg'],
        identified_seat_stock_within_interior_kg=min(seat_mass,parent['interior_allocation_kg']),
        counted_seating_mass_kg=seat_mass, retained_unidentified_interior_budget_kg=remaining_interior_budget,
        additional_seat_stock_above_retained_budget_kg=seat_excess,
        other_interior_installed_mass_kg=None, interior_allowance_saving_claimed_kg=0.,
        seat_budget_trace='Ancestor central interior800kg survives exact magnetic/frame/doors/windows/HVAC substitutions; seats resolve part of that account. Remaining budget is unlocated, not measured equipment or zero other fitout.',
        HVAC_hardware_reference_quantity=hvac_units, HVAC_hardware_reference_kg=192.*hvac_units,
        HVAC_reference_delta_from_parent_kg=192.*(hvac_units-5),
        net_accounting_change_kg_per_car=delta, accounted_tare_kg_per_car=tare,
        accounted_cap_loaded_kg_per_car=tare+75.*cap,
        accounted_160passenger_control_kg_per_car=tare+12000.,
        actual_installed_tare_kg_per_car=None, actual_installed_loaded_kg_per_car=None,
        CG_m=None, inertia_kg_m2=None, complete_installed_mass_known=False)
    thermal = []
    sensitivities = glazing['thermal_sensitivities']
    for optical in sensitivities:
        for passengers in sorted({cap,160}):
            for humid in (False,True):
                load = thermal_load(passengers=passengers, doors_total=doors, active_doors=active,
                    solar_factor=optical['solar_factor_g'], U_W_m2K=optical['U_W_m2K'], humid=humid, root=root)
                thermal.append(dict(glazing_hypothesis=deepcopy(optical), passengers=passengers,
                    load=load, cooling=cooling_comparison(load['total_kWthermal'], hvac_units),
                    actual_glazing_solar_factor_g=glazing['actual_solar_factor_g'],
                    actual_glazing_U_W_m2K=glazing['actual_U_W_m2K']))
    local_sources = {Path(__file__).relative_to(ROOT).as_posix():_hash(Path(__file__)),
        'engineering/vehicle_optimisation/hvac.py':_hash(Path(hvac.__file__)),
        'engineering/vehicle_optimisation/equipment.py':_hash(Path(equipment.__file__))}
    for module in (layouts,glazings):
        module_path=Path(module.__file__).resolve()
        local_sources[module_path.relative_to(module_path.parents[2]).as_posix()]=_hash(module_path)
    bindings=deepcopy(parent['source_sha256'])
    for binding in (layout['source_sha256'],local_sources):
        for name,digest in binding.items():
            if name in bindings and bindings[name]!=digest:
                raise ValueError('composed evaluator source identities differ: '+name)
            bindings[name]=digest
    value = dict(schema=SCHEMA, candidate_id=candidate_id, physical_definition=physical,
        layout_id=layout['layout_id'], glazing_id=glazing['glazing_id'],
        source_sha256=dict(sorted(bindings.items())),
        ancestry_source_revision=parent['ancestry_source_revision'],
        ancestry_source_sha256=deepcopy(parent['ancestry_source_sha256']),
        parent_body_candidate_id=BODY_ID, parent_composition_id=PARENT_COMPOSITION_ID,
        magnet_component_id=MAGNET_ID, mass=mass,
        occupancy=dict(seats_total=layout['seats_total'], transverse_seats=layout['transverse_seats'],
            doorway_bench_seats=layout['bench_seats'], wheelchair_places=layout['wheelchair_places'],
            standing_passengers=layout['standing_passengers'], total_passenger_limit=cap,
            fitted_seats_fraction_of_total_capacity=layout['seats_total']/cap,
            comfort_claim_basis='Proposed fitted-seat share and standing space; passenger comfort, accessibility, evacuation and boarding-load enforcement await qualification'),
        support=support_comparison(tare, cap, parent['samples']),
        service=service_comparison(cap, active, accounted_tare_kg=tare), thermal=thermal,
        layout_necessary_fit_pass=layout['engineering_screen']=='pass',
        layout_definition_failure_reasons=deepcopy(layout['failure_reasons']),
        layout_open_items=deepcopy(layout['unknown']),
        glazing_analytical_evaluation_id=glazing['evaluation_id'],
        glazing_engineering_screen=glazing['evaluation']['engineering_screen'],
        glazing_qualification_holds=deepcopy(glazing['qualification_holds']),
        complete_equipped_body_native_geometry=False, complete_flexible_body_modes=False,
        execution_status='completed', numerical_validity='valid-accounting-arithmetic; field-sample-convergence-unresolved',
        engineering_screen='integrated-performance-unknown',
        evidence_maturity='source-bound-component-samples-and-analytical-accounting',
        selection_id=None, selection_purpose='research-comparison',
        physical_acceptance='hold', integrated_baseline_eligible=False,
        unknown_installed_inventory=deepcopy(layout.get('unknown_installed_inventory', []))+deepcopy(glazing['unknown_installed_inventory'])+[
            dict(id='other-interior-equipment-and-seat-interfaces',mass_kg=None),
            dict(id='door-layout-opening-frame-reinforcement-and-egress',mass_kg=None),
            dict(id='HVAC-quantity-specific-mounts-ducts-wiring-protection-clearance',mass_kg=None),
            dict(id='mobility-devices-and-luggage-extra',mass_kg=None)], **FLAGS)
    value['evaluation_id'] = identity(value)
    return value


def validate(value, layout, glazing, *, root=ROOT):
    """Rebuild rather than trusting edited margins or acceptance fields."""
    expected = evaluate(layout, glazing, root=root,
        hvac_units=value['physical_definition']['HVAC']['units'])
    if value != expected:
        raise ValueError('comfort systems payload or identity differs from deterministic evaluation')
    return True
