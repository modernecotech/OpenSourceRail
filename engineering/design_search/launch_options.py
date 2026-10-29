"""Cheap practical-launch bounds, separate from retained P1-P7 contracts.

Hardware options are concepts with absent materialized candidate IDs. Prescribed
accelerations and energy/adhesion bounds never supply a usable force map.
"""
from itertools import product
from math import ceil, isfinite, sqrt
from pathlib import Path
import argparse
import json
import time
import tomllib

from engineering.development_baseline import selection
from engineering.station_rail import ROOT, braking, operations
from engineering.station_rail.common import brief, digest, encoded, identity
from . import requirement_policy

PRODUCER = 'engineering/design_search/launch_options.py'
SPEC = 'campaigns/practical-launch-comparison.toml'
OUTPUT = 'docs/design-engine/practical-launch'
G = 9.80665
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False, selected_reference_changed=False,
             native_evaluator_admission=False, physical_journey_completed=False)


def _positive(value, *, zero=False):
    return (type(value) in (int, float) and isfinite(value)
            and (value >= 0 if zero else value > 0))


def specification(root=ROOT):
    value = tomllib.loads((Path(root) / SPEC).read_text())
    if (value['schema'] != 'osr-practical-launch-comparison/1'
            or value['purpose'] != 'next-experiment'
            or value['reference_selector'] != 'engineering/development-baseline.toml'
            or value['reference_changes_allowed'] is not False
            or value['native_dispatch'] is not False):
        raise ValueError('Explicit non-promoting launch research required')
    if (type(value['maximum_cases']) is not int
            or not 1 <= value['maximum_cases'] <= 400
            or not _positive(value['maximum_runtime_s'])
            or value['maximum_runtime_s'] > 30):
        raise ValueError('Bounded cheap comparison required')
    space, context = value['space'], value['comparison']
    for name in ('station_spacing_m', 'speed_m_s', 'acceleration_m_s2', 'fixed_drive_bank_m'):
        values = space[name]
        if (not values or len(values) > 4 or len(set(values)) != len(values)
                or any(not _positive(x) for x in values)):
            raise ValueError('Distinct finite positive launch samples required')
    if space['station_spacing_m'] != [1500.0, 2000.0]:
        raise ValueError('The common comparison requires both 1,500 m and 2,000 m station spacing')
    if (not space['grade_fraction'] or len(space['grade_fraction']) > 3
            or len(set(space['grade_fraction'])) != len(space['grade_fraction'])
            or any(type(x) not in (int, float) or not isfinite(x) or not 0 <= x <= .02
                   for x in space['grade_fraction'])):
        raise ValueError('Level/uphill grades 0..0.02 required; downhill needs signed drive/braking work')
    if (len(space['wheel_store_types']) != 3
            or set(space['wheel_store_types']) != {'battery', 'supercapacitor', 'hybrid'}):
        raise ValueError('Explicit separate storage architectures required')
    for key in ('target_headway_s', 'dwell_s', 'service_deceleration_m_s2',
                'cable_launch_stroke_m'):
        if not _positive(context[key]):
            raise ValueError('Finite positive service context required')
    if (type(context['total_axles']) is not int or context['total_axles'] != 24
            or type(context['driven_axles']) is not int
            or not 1 <= context['driven_axles'] <= context['total_axles']):
        raise ValueError('Explicit driven/total axle counts required')
    for key in ('traction_adhesion_hypotheses', 'drive_efficiency_hypotheses',
                'roller_friction_hypotheses'):
        if (not context[key] or len(context[key]) > 4
                or len(set(context[key])) != len(context[key])
                or any(not _positive(x) or x > 1 for x in context[key])):
            raise ValueError('Finite positive coefficients no greater than one required')
    for key in ('charger_efficiency_hypothesis', 'usable_store_fraction_hypothesis',
                'end_of_life_fraction_hypothesis'):
        if not _positive(context[key]) or context[key] > 1:
            raise ValueError('Explicit positive efficiency/usable fractions required')
    if (not context['additional_mass_sensitivity_kg_train']
            or len(context['additional_mass_sensitivity_kg_train']) > 4
            or len(set(context['additional_mass_sensitivity_kg_train'])) != len(context['additional_mass_sensitivity_kg_train'])
            or any(not _positive(x) for x in context['additional_mass_sensitivity_kg_train'])):
        raise ValueError('Positive hypothetical added masses required; unknown is not zero')
    return value


def bounds(mass_kg, rotating_equivalent_kg, speed, acceleration, *, cars=6,
           grade=0., rolling=.0025, bearing_per_car=50., aero_per_car=1.8):
    """Constant target acceleration; energy is an exact integral of this model.

    Grade is the same small-angle hypothesis as operations.profile. Added
    motor/gear rotor inertia and real force capability remain absent.
    """
    if (any(not _positive(x) for x in (mass_kg, speed, acceleration))
            or any(not _positive(x, zero=True) for x in
                   (rotating_equivalent_kg, rolling, bearing_per_car, aero_per_car))
            or type(cars) is not int or cars < 1
            or type(grade) not in (int, float) or not isfinite(grade)):
        raise ValueError('Finite physical launch comparison inputs required')
    effective = mass_kg + rotating_equivalent_kg
    distance = speed**2 / (2 * acceleration)
    constant = mass_kg * G * (rolling + grade) + bearing_per_car * cars
    resistance_at_cap = constant + aero_per_car * cars * speed**2
    effort = effective * acceleration + resistance_at_cap
    work = (.5 * effective * speed**2 + constant * distance
            + aero_per_car * cars * acceleration * distance**2)
    return dict(launch_distance_m=distance, launch_time_s=speed / acceleration,
                kinetic_energy_kWh=.5 * effective * speed**2 / 3.6e6,
                required_mechanical_work_kWh=work / 3.6e6,
                required_body_drive_or_shaft_effort_N=effort,
                required_mechanical_power_W=effort * speed,
                optimistic_wheel_contact_force_N=mass_kg * acceleration + resistance_at_cap,
                lossless_mean_train_CG_drop_m=.5 * effective * speed**2 / (mass_kg * G),
                launch_work_equivalent_CG_drop_m=work / (mass_kg * G))


def ideal_trip_time(distance, speed, acceleration, braking_deceleration):
    """Optimistic powered cruise, instantaneous acceleration changes, zero drag."""
    if any(not _positive(x) for x in (distance, speed, acceleration, braking_deceleration)):
        raise ValueError('Positive ideal trip parameters required')
    peak = min(speed, sqrt(2 * distance / (1 / acceleration + 1 / braking_deceleration)))
    ramp = peak**2 / (2 * acceleration) + peak**2 / (2 * braking_deceleration)
    return peak / acceleration + peak / braking_deceleration + max(0., distance - ramp) / peak


def options(spec, reference):
    """Concept hardware identity excludes route, targets, friction and efficiency."""
    v, c = reference['selection']['vehicle'], spec['comparison']
    train_length = v['cars'] * v['body_length_m'] + (v['cars'] - 1) * .5
    rows = []
    def add(name, mechanism, **hardware):
        physical = dict(reference_candidate_id=reference['vehicle']['candidate_id'],
                        mechanism=mechanism, hardware=hardware,
                        train_length_m=train_length, geometry_complete=False)
        rows.append(dict(name=name, physical_definition=physical,
                         physical_option_id=identity(physical), materialized_candidate_id=None,
                         complete_installed_mass_kg=None, complete_installed_cost_USD=None,
                         available_force_map_id=None, selection_id=None, **FLAGS))
    for length in spec['space']['fixed_drive_bank_m']:
        add(f'Wayside LIM, {length:g} m bank', 'lim', fixed_bank_m=length,
            secondary='retained passive fin concept; finite overlap remains unqualified')
        add(f'Wayside rollers, {length:g} m bank', 'rollers', fixed_bank_m=length,
            optimistic_passive_strip_length_m=train_length,
            strip_and_mounts_installed_mass_kg=None, continuous_strip_across_couplers=False)
    add('Launch-only cable and return trolley', 'cable-launch',
        powered_stroke_m=c['cable_launch_stroke_m'],
        grip_return_braking_and_reset_geometry=None, rope_and_trolley_mass_kg=None)
    add('Fixed-grip synchronous cable loop', 'cable-fixed',
        one_train_per_station_pitch=True, route_station_pitch_m=None,
        minimum_haul_path_per_leg_m=None, route_length_resolved_per_evaluation=True,
        rope_sheaves_grips_and_station_drives=None)
    add('Detachable continuous cable', 'cable-detachable',
        minimum_haul_path_per_leg_m=None, route_length_resolved_per_evaluation=True,
        station_speed_matching_and_grips=None, rope_and_drive_geometry=None)
    for store in spec['space']['wheel_store_types']:
        add(f'Station-charged {store} wheel drive', 'wheel-store', store=store,
            related_research_family='P6', driven_axles=c['driven_axles'],
            station_charging_contact_and_collector_required=True,
            separate_traction_bus_store_cooling_protection=True,
            reference_auxiliary_pack_available_for_traction=False,
            reference_LIM_secondary_replaced=True, equipment_mass_kg=None)
    add('Conductor-fed wheel drive', 'wheel-conductor', related_research_family='P6',
        driven_axles=c['driven_axles'], conductor_track_per_leg_m=None,
        conductor_length_resolved_per_evaluation=True,
        collectors_sectioning_protection_and_rescue_required=True, equipment_mass_kg=None)
    add('Gravity launch alignment', 'gravity', lowered_train_CG_alignment=None,
        vertical_curves_and_height_reset_system=None)
    return rows


def compare(root=ROOT):
    root = Path(root).resolve()
    started = time.monotonic()
    spec = specification(root)
    reference = selection.load(root)
    vehicle = reference['vehicle']
    b = brief(root)
    cars = b['vehicle']['cars']
    mass = vehicle['mass']['accounted_cap_loaded_kg_per_car'] * cars
    rotor = braking.rotating_stock(vehicle)['equivalent_inertial_mass_kg_per_car'] * cars
    c = spec['comparison']
    definitions = options(spec, reference)
    spacings = spec['space']['station_spacing_m']
    samples = list(product(spec['space']['speed_m_s'], spec['space']['acceleration_m_s2'],
                           spec['space']['grade_fraction']))
    route_options = [(spacing, option) for spacing in spacings for option in definitions]
    if len(samples) * len(route_options) > spec['maximum_cases']:
        raise ValueError('Launch comparison exceeds declared case budget')
    source = {**vehicle['source_sha256'], **reference['source_sha256']}
    for name in (PRODUCER, SPEC, 'engineering/station_rail/braking.py',
                 'engineering/station_rail/operations.py', 'engineering/design_search/requirement_policy.py',
                 'engineering/development_baseline/selection.py', OUTPUT + '/README.md'):
        source[name] = digest(root / name)
    if digest(root / PRODUCER) != digest(__file__):
        raise ValueError('Executing launch producer differs from declared source root')
    rows = []
    for (spacing, option), (speed, acceleration, grade) in product(route_options, samples):
        if time.monotonic() - started > spec['maximum_runtime_s']:
            raise ValueError('Cheap comparison runtime budget exceeded; no packet published')
        route_context = dict(c, station_spacing_m=spacing)
        request = dict(speed_m_s=speed, acceleration_m_s2=acceleration,
                       grade_fraction=grade, station_spacing_m=spacing,
                       comparison=route_context)
        metrics = bounds(mass, rotor, speed, acceleration, cars=cars, grade=grade)
        hardware = option['physical_definition']['hardware']
        mechanism = option['physical_definition']['mechanism']
        minimum_ramps = metrics['launch_distance_m'] + speed**2 / (2 * c['service_deceleration_m_s2'])
        stop_distance = speed**2 / (2 * c['service_deceleration_m_s2'])
        necessary = dict(optimistic_acceleration_and_brake_distance_m=minimum_ramps,
                         optimistic_service_stop_distance_m=stop_distance,
                         route_distance_screen='fails-bound' if minimum_ramps > spacing else 'not-ruled-out',
                         ideal_one_way_trip_time_s=ideal_trip_time(
                             spacing, speed, acceleration, c['service_deceleration_m_s2']),
                         route_cable_or_conductor_length_per_leg_m=None)
        if mechanism in ('lim', 'rollers'):
            # Even any remaining contact over a fictitious continuous train strip
            # cannot extend power beyond bank + whole train. This is generous for
            # either finite-fin LIM engagement or discontinuous car strips.
            reach = hardware['fixed_bank_m'] + option['physical_definition']['train_length_m']
            necessary.update(optimistic_any_contact_travel_m=reach,
                optimistic_reach_screen='not-ruled-out' if reach >= metrics['launch_distance_m'] else 'fails-bound',
                minimum_bank_under_any_contact_bound_m=max(0., metrics['launch_distance_m'] - option['physical_definition']['train_length_m']))
        if mechanism == 'rollers':
            necessary['conditional_total_clamp_normal_load_N'] = [dict(friction_hypothesis=mu,
                load_N=metrics['required_body_drive_or_shaft_effort_N'] / mu)
                for mu in c['roller_friction_hypotheses']]
        if mechanism.startswith('wheel-'):
            necessary['optimistic_uniform_axle_adhesion'] = [dict(adhesion_hypothesis=mu,
                minimum_driven_axles_lower_bound=ceil(metrics['optimistic_wheel_contact_force_N'] * c['total_axles'] / (mu * mass * G)),
                screen='not-ruled-out' if mu * mass * G * c['driven_axles'] / c['total_axles'] >= metrics['optimistic_wheel_contact_force_N'] else 'fails-bound')
                for mu in c['traction_adhesion_hypotheses']]
            necessary['actual_adhesion_screen'] = 'unknown'
        if mechanism == 'wheel-store':
            necessary['conditional_launch_only_store'] = [dict(drive_efficiency_hypothesis=eta,
                dc_peak_power_kW=metrics['required_mechanical_power_W'] / eta / 1000,
                dc_energy_kWh=metrics['required_mechanical_work_kWh'] / eta,
                energy_only_gross_kWh=metrics['required_mechanical_work_kWh'] / eta / c['usable_store_fraction_hypothesis'] / c['end_of_life_fraction_hypothesis'],
                installed_store_size_kWh=None, store_power_thermal_admission=False)
                for eta in c['drive_efficiency_hypotheses']]
        if mechanism == 'cable-launch':
            necessary.update(required_powered_stroke_m=metrics['launch_distance_m'],
                stroke_screen='not-ruled-out' if hardware['powered_stroke_m'] >= metrics['launch_distance_m'] else 'fails-bound',
                catch_car_stop_return_reset_time_s=None, headway_screen='unknown')
        if mechanism == 'cable-detachable':
            necessary.update(station_speed_matching_travel_m=metrics['launch_distance_m'],
                             minimum_haul_path_per_leg_m=spacing,
                             route_cable_or_conductor_length_per_leg_m=spacing,
                             grip_and_speed_matching_qualified=False)
        if mechanism == 'cable-fixed':
            necessary['route_cable_or_conductor_length_per_leg_m'] = spacing
        if mechanism == 'wheel-conductor':
            necessary['route_cable_or_conductor_length_per_leg_m'] = spacing
        if mechanism == 'gravity':
            necessary.update(lossless_mean_train_CG_drop_m=metrics['lossless_mean_train_CG_drop_m'],
                             loss_replacement_and_alignment_qualified=False)
        ideal = necessary['ideal_one_way_trip_time_s']
        if mechanism == 'cable-fixed':
            minimum_interval = ideal + c['dwell_s']
            necessary.update(optimistic_station_pitch_interval_s=minimum_interval,
                optimistic_capacity_pphpd=cars * b['vehicle']['normal_people_per_car'] * 3600 / minimum_interval,
                headway_screen='fails-bound' if minimum_interval > c['target_headway_s'] else 'not-ruled-out')
        rows.append(dict(physical_option_id=option['physical_option_id'], name=option['name'],
            request=request, required=metrics, necessary_bounds=necessary,
            comparison_scope=dict(station_spacing_m=spacing, normal_people_per_train=b['vehicle']['normal_people_per_car'] * cars,
                target_headway_s=c['target_headway_s'],
                target_capacity_pphpd=b['vehicle']['normal_people_per_car'] * cars * 3600 / c['target_headway_s'],
                dwell_s=c['dwell_s']),
            evidence_gaps=['Available force/effort map over position, speed and fault states',
                'Electrical or mechanical losses, cooling and repeated-duty temperature limits',
                'Independent stopping, holding, failed-launch recovery and rescue',
                'Complete installed equipment quantities, masses, grid peak and supplier prices',
                'Protected repeated headway, fleet/turnback and degraded-service demonstration'],
            execution='completed', numerical_validity='valid', engineering_screen='unknown',
            evidence_maturity='analytical-required-demand', evidence='prescribed-demand-and-necessary-bounds-only',
            evaluation_id=identity(dict(option_id=option['physical_option_id'], request=request,
                                        source_sha256=source)), **FLAGS))
    normal = bounds(mass, rotor, 20., .4, cars=cars)
    hotel_kW = cars * b['services']['reference_hotel_kW_per_car']
    route_contexts = []
    for spacing in spacings:
        profile = operations.profile(spacing, mass / cars,
            rotating_equivalent_mass_kg_per_car=rotor / cars, cars=cars,
            service_deceleration_m_s2=c['service_deceleration_m_s2'])
        ideal = ideal_trip_time(spacing, 20., .4, c['service_deceleration_m_s2'])
        storage = []
        for eta in c['drive_efficiency_hypotheses']:
            dc_energy = normal['required_mechanical_work_kWh'] / eta
            dc_peak = normal['required_mechanical_power_W'] / eta / 1000
            gross = dc_energy / c['usable_store_fraction_hypothesis'] / c['end_of_life_fraction_hypothesis']
            storage.append(dict(drive_efficiency_hypothesis=eta,
                launch_dc_energy_kWh=dc_energy, dc_peak_power_kW=dc_peak,
                launch_only_energy_gross_bound_kWh=gross,
                energy_only_peak_power_to_energy_per_hour=dc_peak / gross,
                repeated_launch_drive_loss_average_kW=(dc_energy - normal['required_mechanical_work_kWh']) * 3600 / c['target_headway_s'],
                launch_only_recharge_input_kW=dc_energy * 3600 / c['dwell_s'] / c['charger_efficiency_hypothesis'],
                grid_recharge_plus_hotel_during_dwell_kW=(dc_energy + hotel_kW * profile['runtime_s'] / 3600) * 3600 / c['dwell_s'] / c['charger_efficiency_hypothesis'] + hotel_kW,
                actual_installed_store_energy_kWh=None, actual_installed_store_power_kW=None,
                actual_peak_grid_demand_kW=None,
                hot_EOL_power_voltage_current_thermal_admission=False))
        route_contexts.append(dict(station_spacing_m=spacing,
            normal_people_per_train=b['vehicle']['normal_people_per_car'] * cars,
            target_headway_s=c['target_headway_s'],
            target_capacity_pphpd=b['vehicle']['normal_people_per_car'] * cars * 3600 / c['target_headway_s'],
            dwell_s=c['dwell_s'], required_normal_launch=normal,
            ideal_reference_one_way_trip_time_s=ideal,
            ideal_single_reversible_shuttle_round_trip_with_dwell_s=2 * (ideal + c['dwell_s']),
            conditional_reference_profile=profile, conditional_storage_screens=storage,
            actual_available_force_map=False, actual_protected_capacity=None,
            complete_installed_mass_kg=None, actual_peak_grid_demand_kW=None,
            **FLAGS))
    reference_context = next(row for row in route_contexts if row['station_spacing_m'] == 2000.0)
    result = dict(schema='osr-practical-launch-result/1', purpose='next-experiment',
        execution='completed', numerical_validity='valid-for-declared-algebraic-bounds',
        engineering_screen='unknown', evidence_maturity='analytical-required-demand',
        reference_candidate_id=vehicle['candidate_id'], reference_selection_id=reference['selection_id'],
        materialized_candidate_id=None, selection_id=None, integrated_selection=None,
        comparison_mass_basis='Unmodified inherited accounted mass, including passive-secondary accounts; replacement equipment is unweighed, not zero. No new vehicle mass is established.',
        normal_accounted_mass_kg=mass, retained_rotational_equivalent_kg=rotor,
        complete_installed_mass_kg=None, complete_installed_cost_USD=None,
        normal_reference_bound=normal, conditional_reference_profile=reference_context['conditional_reference_profile'],
        reference_conditional_storage=reference_context['conditional_storage_screens'],
        optimistic_single_reversible_shuttle_headway_s=reference_context['ideal_single_reversible_shuttle_round_trip_with_dwell_s'],
        hypothetical_added_mass_sensitivity=[dict(hypothetical_added_kg_train=extra,
            required=bounds(mass + extra, rotor, 20., .4, cars=cars),
            actual_added_equipment_mass_kg=None) for extra in c['additional_mass_sensitivity_kg_train']],
        options=definitions, route_contexts=route_contexts, route_cases=rows,
        cases=[row for row in rows if row['request']['station_spacing_m'] == 2000.0],
        required_closure_matrix=[
            dict(requirement='Available propulsion effort by position, speed and adverse/fault state', status='missing', evidence=None),
            dict(requirement='Electrical/mechanical losses, cooling and repeated duty', status='missing', evidence=None),
            dict(requirement='Independent service/emergency/parking stop and launch recovery', status='conditional-demand-only', evidence=None),
            dict(requirement='Installed equipment quantities, mass and price', status='unknown', evidence=None),
            dict(requirement='Peak grid demand and protected 120 s / 8,280 pphpd service', status='partially-screened', evidence='Ideal cable-loop bound only; other fleet, turnback and protection schedules are not evaluated')],
        requirement_policy=requirement_policy.assess({}),
        sources_sha256=dict(sorted(source.items())), specification=spec,
        limitations=['No available force, hardware mass, voltage/current/thermal map or equipment price.',
            'Higher acceleration is a revisable hypothesis; comfort, jerk, securement and adhesion limits are not approved.',
            'Contact bounds assume a continuous full-train strip with no coupling gaps and no lost contact margin.',
            'Wheel contact lower bounds omit unknown unpowered rotor share; shaft effort separately retains counted rotation.',
            'No regenerative energy credit or auxiliary-store traction connection.',
            'Complete safety, protection, recovery, civil, manufacturing and economic evaluation remain open.'], **FLAGS)
    result['comparison_id'] = identity(result)
    return result


def summary(result):
    return dict(comparison_id=result['comparison_id'], physical_options=len(result['options']),
                bound_cases=len(result['route_cases']), route_spacing_count=len(result['route_contexts']),
                complete_installed_mass_kg=None,
                integrated_selection=None, normal_reference_bound=result['normal_reference_bound'], **FLAGS)


def _write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.pending')
    temporary.write_bytes(raw)
    temporary.replace(path)


def publish(root=ROOT):
    root = Path(root)
    result = compare(root)
    destination = root / OUTPUT
    _write(destination / 'comparison.json', encoded(result))
    manifest = dict(schema='osr-practical-launch-publication/1', comparison_id=result['comparison_id'],
                    source_sha256=result['sources_sha256'],
                    files_sha256={'comparison.json': digest(destination / 'comparison.json')}, **FLAGS)
    manifest['manifest_id'] = identity(manifest)
    _write(destination / 'manifest.json', encoded(manifest))
    return dict(published=True, **summary(result))


def verify(root=ROOT):
    root = Path(root)
    destination = root / OUTPUT
    result = compare(root)
    manifest = json.loads((destination / 'manifest.json').read_bytes())
    if (manifest.get('schema') != 'osr-practical-launch-publication/1'
            or manifest.get('manifest_id') != identity({k: v for k, v in manifest.items() if k != 'manifest_id'})
            or manifest.get('source_sha256') != result['sources_sha256']
            or manifest.get('comparison_id') != result['comparison_id']
            or manifest.get('files_sha256') != {'comparison.json': digest(destination / 'comparison.json')}
            or any(manifest.get(k) is not v for k, v in FLAGS.items())
            or (destination / 'comparison.json').read_bytes() != encoded(result)):
        raise ValueError('Practical launch source, payload or non-promoting disposition differs')
    return dict(verified=True, **summary(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'compare', 'publish', 'verify'))
    args = parser.parse_args()
    if args.action == 'plan':
        result = specification()
    elif args.action == 'compare':
        result = summary(compare())
    else:
        result = globals()[args.action]()
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
