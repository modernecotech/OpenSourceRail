"""Compare user-seeded propulsion layouts with counted catalogue feedback.

This is a non-promoting study of contact, adhesion, power, mass and service
requests. Available force maps, installed designs and prices remain unknown.
"""
from itertools import product
from hashlib import sha256
from math import ceil, isfinite, sqrt
from pathlib import Path
import argparse
import gzip
import io
import json
import tarfile
import time
import tomllib

from engineering.development_baseline import selection
from engineering.station_rail import ROOT, braking, operations
from engineering.station_rail.common import brief, digest, encoded, identity
from . import requirement_policy, launch_options
from . import propulsion_storage, sparse_launch, storage as records

PRODUCER = 'engineering/design_search/propulsion_layout.py'
SPEC = 'campaigns/simple-affordable-propulsion.toml'
DRIVE = 'engineering/design_search/data/tsa-type-x-drive-lead.json'
CAPACITOR = 'engineering/design_search/data/skeleton-102v94f-catalogue.json'
OUTPUT = 'docs/design-engine/propulsion-layout'
FLAGS = dict(physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
             manufacturing_release=False, operating_release=False, selected_reference_changed=False,
             native_evaluator_admission=False, physical_journey_completed=False)
G = 9.80665


def positive(value):
    return type(value) in (float, int) and isfinite(value) and value > 0


def specification(root=ROOT):
    s = tomllib.loads((Path(root) / SPEC).read_text())
    if (s['schema'] != 'osr-propulsion-layout-study/1' or s['purpose'] != 'next-experiment'
            or s['reference_changes_allowed'] is not False or s['native_dispatch'] is not False):
        raise ValueError('Explicit non-promoting propulsion study required')
    for key, upper in (('maximum_cases', 400), ('maximum_runtime_s', 120), ('maximum_mass_iterations', 12)):
        if type(s[key]) is not int or not 1 <= s[key] <= upper:
            raise ValueError('Bounded propulsion study required')
    w, service, sparse = s['wheel'], s['service'], s['sparse']
    for group, key, limit in ((w, 'powered_bogies', 6), (w, 'speed_m_s', 3),
                              (w, 'acceleration_m_s2', 3), (w, 'grade_fraction', 3),
                              (w, 'adhesion_hypotheses', 3), (sparse, 'site_counts', 4),
                              (sparse, 'bank_lengths_m', 3)):
        values = group[key]
        if not values or len(values) > limit or len(set(values)) != len(values):
            raise ValueError('Distinct bounded samples required')
    if any(type(n) is not int or n < 2 or n > 12 or n % 2 for n in w['powered_bogies']):
        raise ValueError('Symmetric two-group powered bogie counts required')
    if any(not positive(x) for key in ('speed_m_s', 'acceleration_m_s2', 'adhesion_hypotheses') for x in w[key]):
        raise ValueError('Positive finite operating hypotheses required')
    if any(type(x) not in (float, int) or not isfinite(x) or not 0 <= x <= .02 for x in w['grade_fraction']):
        raise ValueError('Only level/uphill positive-traction cases are admitted to this study')
    if set(w['traction_policies']) != {'launch-coast', 'sustain-to-brake'} or len(w['traction_policies']) != 2:
        raise ValueError('Explicit propulsion duty alternatives required')
    if (not positive(w['drive_efficiency_hypothesis']) or w['drive_efficiency_hypothesis'] > 1
            or any(not positive(w[k]) for k in ('unweighed_installation_per_powered_bogie_kg_hypothesis',
                'unweighed_common_installation_kg_hypothesis', 'extra_powered_rotor_equivalent_kg_per_axle_hypothesis'))):
        raise ValueError('Unknown installed equipment cannot become zero')
    if any(not positive(v) for v in service.values()) or service['auxiliary_charger_efficiency_hypothesis'] > 1:
        raise ValueError('Positive service inputs required')
    if abs(service['directional_ring_length_m'] / service['station_spacing_m'] - round(service['directional_ring_length_m'] / service['station_spacing_m'])) > 1e-9:
        raise ValueError('Explicit integral station count required')
    if (any(type(n) is not int or not 3 <= n <= 6 for n in sparse['site_counts'])
            or any(not positive(x) for x in sparse['bank_lengths_m'])
            or not positive(sparse['spacing_beyond_front_m']) or not positive(sparse['required_launch_travel_m'])):
        raise ValueError('Explicit positive sparse geometry required')
    if (w['seed_powered_bogies'] != 2 or sparse['seed_sites'] != 3
            or w['seed_powered_bogies'] not in w['powered_bogies']
            or sparse['seed_sites'] not in sparse['site_counts']
            or sparse['independent_receiving_and_braking_design_complete'] is not False
            or s['storage']['separate_boost_converter_required'] is not True):
        raise ValueError('Preserve user seeds and unresolved receiving/voltage interfaces')
    return s


def trajectory_request(mass, rotor, speed, acceleration, grade, policy, service, cars=6):
    """Target demand at counted/scenario mass; never an available-force journey."""
    distance, deceleration = service['station_spacing_m'], service['independent_service_deceleration_m_s2']
    if policy == 'launch-coast':
        p = operations.profile(distance, mass / cars, rotating_equivalent_mass_kg_per_car=rotor / cars,
            cars=cars, speed_cap_m_s=speed, acceleration_m_s2=acceleration,
            service_deceleration_m_s2=deceleration, grade_fraction=grade)
        if not p['reachable']:
            return dict(target_reachable=False, reason=p['reason'], physical_journey_completed=False)
        return dict(target_reachable=True, runtime_s=p['runtime_s'], peak_speed_m_s=p['peak_speed_m_s'],
            launch_distance_m=p['launch_distance_m'], traction_active_s=p['launch_time_s'],
            required_mechanical_energy_kWh=p['launch_mechanical_energy_J_per_car'] * cars / 3.6e6,
            required_peak_shaft_force_N=p['peak_launch_force_N_per_car'] * cars,
            required_peak_mechanical_power_W=p['peak_launch_power_W_per_car'] * cars,
            physical_journey_completed=False)
    if policy != 'sustain-to-brake':
        raise ValueError('Explicit traction policy required')
    peak = min(speed, sqrt(2 * distance / (1 / acceleration + 1 / deceleration)))
    launch = launch_options.bounds(mass, rotor, peak, acceleration, cars=cars, grade=grade)
    brake_distance = peak**2 / (2 * deceleration)
    cruise_distance = max(0., distance - launch['launch_distance_m'] - brake_distance)
    resistance = mass * G * (.0025 + grade) + cars * (50 + 1.8 * peak**2)
    return dict(target_reachable=True, runtime_s=peak / acceleration + cruise_distance / peak + peak / deceleration,
        peak_speed_m_s=peak, launch_distance_m=launch['launch_distance_m'],
        traction_active_s=peak / acceleration + cruise_distance / peak,
        required_mechanical_energy_kWh=launch['required_mechanical_work_kWh'] + resistance * cruise_distance / 3.6e6,
        required_peak_shaft_force_N=launch['required_body_drive_or_shaft_effort_N'],
        required_peak_mechanical_power_W=launch['required_mechanical_power_W'], physical_journey_completed=False)


def powered_bogie_indices(count):
    # Identical three-car groups each retain six bogies. These are explicit
    # mounting concepts; the actual axle/hardpoint/weight distribution is open.
    order = [1, 4, 2, 5, 0, 3]
    return sorted(order[:count // 2] + [6 + n for n in order[:count // 2]])


def wheel_case(count, speed, acceleration, grade, policy, reference, spec, cap, drive):
    v = reference['vehicle']
    mass_reference = 6 * v['mass']['accounted_cap_loaded_kg_per_car']
    retained_rotor = 6 * braking.rotating_stock(v)['equivalent_inertial_mass_kg_per_car']
    driven_axles = 2 * count
    f = driven_axles / 24
    w, service, storage = spec['wheel'], spec['service'], spec['storage']
    request = dict(powered_bogies=count, speed_m_s=speed, acceleration_m_s2=acceleration,
                   grade_fraction=grade, traction_policy=policy)
    # A necessary uniform-loading floor independent of added module mass.
    floor_mu = (acceleration / G + .0025 + grade) / f
    nominal_mu = max(w['adhesion_hypotheses'])
    base = dict(request=request, hypothetical_uniform_loading_adhesion_floor=floor_mu,
                materialized_candidate_id=None, actual_installed_mass_kg=None,
                actual_installed_cost_USD=None, available_force_map_id=None,
                actual_store_power_kW=None, physical_selection_id=None, **FLAGS)
    if floor_mu > nominal_mu:
        return dict(base, execution='completed', numerical_validity='necessary-bound', engineering_screen='unknown',
                    calculation_status='fails-optimistic-adhesion-bound', sizing_trials=[],
                    next_tasks=['More driven axles, lower acceleration or independently evidenced axle-load/adhesion redesign'])
    catalogue_drive_mass = driven_axles * (drive['motor']['listed_mass_kg'] + drive['gearbox']['listed_total_weight_including_couplings_kg'])
    unknown_allowance = (count * w['unweighed_installation_per_powered_bogie_kg_hypothesis']
                         + w['unweighed_common_installation_kg_hypothesis'])
    extra_rotor = driven_axles * w['extra_powered_rotor_equivalent_kg_per_axle_hypothesis']
    trials = []
    module_mass = 0.  # Initial seed only; never published as installed equipment.
    last_count = None
    for iteration in range(spec['maximum_mass_iterations']):
        mass = mass_reference + catalogue_drive_mass + unknown_allowance + module_mass
        rotor = retained_rotor + extra_rotor
        profile = trajectory_request(mass, rotor, speed, acceleration, grade, policy, service)
        if not profile['target_reachable']:
            return dict(base, execution='completed', numerical_validity='conditional-target-demand', engineering_screen='unknown',
                        calculation_status='coasting-target-unreachable', target_profile=profile, sizing_trials=trials,
                        next_tasks=['Use sustained wheel traction or revise speed, spacing and formation with service consequences'])
        bank_settings = {key: storage[key] for key in propulsion_storage.SETTINGS}
        bank = propulsion_storage.size_bank(profile['required_mechanical_energy_kWh'] / w['drive_efficiency_hypothesis'],
            profile['required_peak_mechanical_power_W'] / w['drive_efficiency_hypothesis'],
            profile['traction_active_s'], service['dwell_s'], cap, bank_settings)
        trials.append(dict(iteration=iteration, comparison_mass_kg=mass, capacitor_bare_mass_used_kg=module_mass,
                           mass_seed_status='lower-bound-iteration-seed-only' if iteration == 0 else 'counted-catalogue-mass',
                           storage=bank))
        if bank.get('calculation_status') != 'sized-conditional-bound':
            return dict(base, execution='completed', numerical_validity='conditional-scalar-model', engineering_screen='unknown',
                        calculation_status='storage-bound-unresolved', sizing_trials=trials,
                        next_tasks=['Different store family, cooling input, voltage interface or complete supplier power/duty data'])
        new_count = bank['module_count']
        if new_count == last_count:
            break
        last_count, module_mass = new_count, bank['bare_module_mass_kg']
    else:
        return dict(base, execution='completed', numerical_validity='mass-loop-not-converged', engineering_screen='unknown',
                    calculation_status='mass-feedback-unresolved', sizing_trials=trials,
                    next_tasks=['Retain all iterations and revise component/store architecture'])
    # Final profile was evaluated at the same counted bare-module mass.
    contact_force = (profile['required_peak_shaft_force_N']
        - acceleration * (retained_rotor * f + extra_rotor))
    mu_required = contact_force / (mass * G * f)
    service_time = profile['runtime_s'] + service['dwell_s']
    stations = round(service['directional_ring_length_m'] / service['station_spacing_m'])
    fleet_floor = ceil(stations * service_time / service['headway_target_s'])
    physical = dict(parent_reference_candidate_id=v['candidate_id'], powered_bogie_indices=powered_bogie_indices(count),
        driven_axles=driven_axles, motor_count=driven_axles, gearbox_count=driven_axles,
        drive_catalogue_lead=drive['manufacturer_ID'], drive_fit_approved=False,
        capacitor_module=cap['component_id'], capacitor_modules=new_count,
        series_modules=storage['series_modules'], parallel_strings_per_bank=bank['parallel_strings_per_bank'],
        bank_count=storage['banks'], boost_conversion_required=True,
        auxiliary_store_traction_connection=False, reference_secondary_replaced=True,
        geometry_and_mounts_complete=False)
    hotel_kW = 6 * brief_services(reference)['reference_hotel_kW_per_car']
    management_kW = new_count * cap['management_supply_voltage_V'] * cap['management_supply_current_A'] / 1000
    hotel_kW += management_kW
    aux_grid_energy = hotel_kW * service_time / 3600 / service['auxiliary_charger_efficiency_hypothesis']
    return dict(base, execution='completed', numerical_validity='conditional-scalar-model', engineering_screen='unknown',
        calculation_status='counted-bound-not-qualification', physical_definition=physical,
        physical_option_id=identity(physical), target_profile=profile, storage=bank, sizing_trials=trials,
        inventory=dict(inherited_account_kg=mass_reference, donor_motor_and_gear_catalogue_kg=catalogue_drive_mass,
            retained_rotating_equivalent_kg=retained_rotor,
            extra_powered_rotor_equivalent_hypothesis_kg=extra_rotor,
            capacitor_bare_module_kg=bank['bare_module_mass_kg'], unweighed_allowance_hypothesis_kg=unknown_allowance,
            comparison_total_kg=mass, actual_complete_installed_kg=None,
            motor_inverter_channels=driven_axles, charger_interfaces=storage['banks'],
            converter_cooling_mounts_wiring_protection_fasteners_installed_kg=None),
        adhesion=dict(required_coefficient_uniform_loading=mu_required,
            assumed_powered_axle_normal_load_N=mass * G * f, required_powered_contact_N=contact_force,
            scenarios=[dict(coefficient_hypothesis=mu, necessary_screen='not-ruled-out' if mu >= mu_required else 'fails-bound')
                       for mu in w['adhesion_hypotheses']], actual_adhesion_qualified=False),
        donor_nameplate_comparison=dict(required_peak_kW_per_axle=profile['required_peak_mechanical_power_W'] / driven_axles / 1000,
            donor_nominal_kW_per_axle=drive['motor']['nominal_power_kW'],
            full_torque_speed_voltage_current_map=None, physical_fit_approved=False),
        dependent_load_requests=dict(physical_option_id=identity(physical),
            normal_translation_weight_kN=mass * G / 1000,
            uniform_normal_axle_load_t=mass / 24 / 1000,
            crowd_control_comparison_mass_kg=mass + (160 - 46) * 75 * 6,
            uniform_crowd_control_axle_load_t=(mass + (160 - 46) * 75 * 6) / 24 / 1000,
            required_brake_kinetic_energy_kWh=.5 * (mass + rotor) * profile['peak_speed_m_s']**2 / 3.6e6,
            approved_brake_force_and_heat_map=None, actual_structural_response=None,
            existing_body_brake_civil_results_reusable=False,
            required_rechecks=['body and bogie hardpoints', 'wheelsets, brakes and independent stopping',
                'rails, beams, piers and foundations', 'charging, cooling and reserve',
                'manufacturing, installation and removal access']),
        service=dict(conditional_vehicle_cycle_s=service_time, headway_target_s=service['headway_target_s'],
            directional_ring_train_floor=fleet_floor, actual_required_fleet=None,
            no_regen_model_scope_grid_energy_upper_kWh=bank['grid_recharge_energy_upper_kWh'] + aux_grid_energy,
            catalogue_cap_management_kW=management_kW,
            actual_grid_energy_kWh=None, hotel_grid_energy_kWh=aux_grid_energy,
            actual_protected_headway_s=None),
        next_tasks=['Approved donor fit or lighter drive definition; full inverter/boost/gear/store hot-duty maps',
                    'Counted installations, axle loads, drive inertia, independent braking and degraded recovery',
                    'Supplier quotes, maintenance/renewal data and equal-service civil/fleet comparison'])


def brief_services(reference):
    return reference['_services']


def compare(root=ROOT):
    root = Path(root).resolve()
    started = time.monotonic()
    spec = specification(root)
    reference = selection.load(root)
    reference['_services'] = brief(root)['services']
    cap = json.loads((root / CAPACITOR).read_bytes())
    drive = json.loads((root / DRIVE).read_bytes())
    if (drive.get('schema') != 'osr-public-drive-catalogue-lead/1'
            or drive.get('compatibility', {}).get('not_selected') is not True
            or drive.get('compatibility', {}).get('unmodified_catalogue_hardware_fit_proven') is not False):
        raise ValueError('Explicit non-selected drive catalogue lead with unproven fit required')
    w = spec['wheel']
    samples = list(product(w['powered_bogies'], w['speed_m_s'], w['acceleration_m_s2'],
                           w['grade_fraction'], w['traction_policies']))
    if len(samples) + len(spec['sparse']['site_counts']) * len(spec['sparse']['bank_lengths_m']) > spec['maximum_cases']:
        raise ValueError('Propulsion study case budget exceeded')
    wheels, pending = [], []
    for index, row in enumerate(samples):
        if time.monotonic() - started > spec['maximum_runtime_s']:
            pending = samples[index:]
            break
        wheels.append(wheel_case(*row, reference, spec, cap, drive))
    v = reference['vehicle']
    m = 6 * v['mass']['accounted_cap_loaded_kg_per_car']
    rot = 6 * braking.rotating_stock(v)['equivalent_inertial_mass_kg_per_car']
    required = launch_options.bounds(m, rot, 20., .4)
    length = reference['selection']['vehicle']['cars'] * 17 + 5 * .5
    sparse_rows = []
    sparse_requests = list(product(spec['sparse']['site_counts'], spec['sparse']['bank_lengths_m']))
    pending_sparse = sparse_requests if pending else []
    for index, (count, bank_length) in enumerate([] if pending else sparse_requests):
        if time.monotonic() - started > spec['maximum_runtime_s']:
            pending_sparse = sparse_requests[index:]
            break
        starts = [0., *[length + i * spec['sparse']['spacing_beyond_front_m'] for i in range(count - 1)]]
        geo = sparse_launch.geometry(starts, bank_length, initial_nose_m=length,
            launch_distance_m=spec['sparse']['required_launch_travel_m'])
        end_sites = geo['breakpoint_records'][-1]['active_sites']
        sparse_rows.append(dict(site_count=count, bank_length_m=bank_length, geometry=geo,
            execution='completed', numerical_validity='geometry-only', engineering_screen='unknown',
            required_train_peak_force_N=required['required_body_drive_or_shaft_effort_N'],
            required_train_peak_mechanical_power_W=required['required_mechanical_power_W'],
            necessary_force_at_least_one_final_site_N=None if end_sites == 0 else required['required_body_drive_or_shaft_effort_N'] / end_sites,
            available_position_force_map=None, complete_installed_cost_USD=None,
            receiving_winding_and_cost=None, candidate_materialized_id=None,
            next_tasks=['Position-dependent nonlinear force/current/thermal map for actual one/two-fin handoffs',
                'Train-level fin/hanger and changing coupler loads, clearances, cooling and failed-site recovery'], **FLAGS))
    sources = {**reference['source_sha256'], **v['source_sha256']}
    for name in (PRODUCER, SPEC, DRIVE, CAPACITOR, OUTPUT + '/README.md',
                 'engineering/design_search/propulsion_storage.py', 'engineering/design_search/sparse_launch.py',
                 'engineering/design_search/launch_options.py', 'engineering/design_search/requirement_policy.py',
                 'engineering/design_search/storage.py',
                 'engineering/requirements.txt',
                 'engineering/station_rail/braking.py', 'engineering/station_rail/operations.py'):
        sources[name] = digest(root / name)
    if digest(root / PRODUCER) != digest(__file__):
        raise ValueError('Executing propulsion producer differs from declared source tree')
    result = dict(schema='osr-propulsion-layout-result/1', purpose='next-experiment',
        execution='interrupted-budget' if pending or pending_sparse else 'completed',
        numerical_validity='partial-only' if pending or pending_sparse else 'valid-for-declared-models',
        engineering_screen='unknown', evidence_maturity='catalogue-and-conditional-models',
        pending_wheel_requests=pending, pending_sparse_requests=pending_sparse,
        reference_candidate_id=v['candidate_id'], reference_selection_id=reference['selection_id'],
        integrated_selection=None, actual_installed_mass_kg=None, actual_whole_life_cost_USD=None,
        requirement_policy=requirement_policy.assess({}), specification=spec,
        wheel_cases=wheels, sparse_cases=sparse_rows, source_sha256=dict(sorted(sources.items())),
        comparison_basis='Inherited accounted vehicle plus listed donor component masses and explicit unknown-equipment/inertia hypotheses. No reference-secondary subtraction, complete installation or accepted drive interface.',
        limitations=['Supplier cap PDF metadata says Draft and is a grid-module lead; rail qualification unconfirmed.',
            'Donor AC voltage and cap DC voltage require a new boost/inverter interface; no map is available.',
            'Scalar hot continuous-current and worst-case loss bounds do not qualify cyclic thermal duty or lifetime.',
            '120s station headway is not onboard store cycle period.',
            'Sparse overlap is geometry only and never a force multiplier; receiving/civil/economics remain incomplete.'], **FLAGS)
    for row in wheels:
        row['evaluation_id'] = identity(dict(request=row['request'], physical_option_id=row.get('physical_option_id'), source_sha256=sources))
    result['study_id'] = identity(result)
    return result


def summary(value):
    from collections import Counter
    return dict(study_id=value['study_id'], execution=value['execution'],
                wheel_cases=len(value['wheel_cases']), sparse_cases=len(value['sparse_cases']),
                pending_requests=len(value['pending_wheel_requests']) + len(value['pending_sparse_requests']),
                wheel_states=dict(Counter(r['calculation_status'] for r in value['wheel_cases'])),
                integrated_selection=None, actual_whole_life_cost_USD=None, **FLAGS)


def findings(value):
    lines = ['# Propulsion layout findings', '',
        'Generated from the same source-bound comparison packet. All results are conditional numerical or geometric screens; physical acceptance and whole-life cost remain open.', '',
        f"Wheel scenarios: **{len(value['wheel_cases'])}**. Sparse layouts: **{len(value['sparse_cases'])}**.", '',
        '## Sparse launch geometry', '',
        '| Sites | Bank length | Launch-only bank extent | Minimum summed fin overlap | Coverage of 500 m |',
        '|---:|---:|---:|---:|---:|']
    for row in value['sparse_cases']:
        geo = row['geometry']
        lines.append(f"| {row['site_count']} | {row['bank_length_m']:g} m | {row['site_count'] * row['bank_length_m']:g} m | {geo['min_sum_overlap_m']:.3f} m | {geo['geometric_covered_m']:.3f} m |")
    lines += ['', 'This is overlap only. One bank can remain responsible for the complete train force; no available motor map or receiving installation is established.', '',
        '## Wheel-drive bounds at 72 km/h', '',
        'Rows below use sustained traction on the 2% uphill case. Required adhesion is compared separately with the 0.10 and 0.15 hypotheses. A counted storage result is not an adhesion pass or hardware qualification.', '',
        '| Powered bogies | Acceleration | Calculation state | Comparison mass | Cap modules | Required adhesion | At 0.10 | Ring fleet floor |',
        '|---:|---:|---|---:|---:|---:|---|---:|']
    for row in value['wheel_cases']:
        r = row['request']
        if r['speed_m_s'] != 20 or r['grade_fraction'] != .02 or r['traction_policy'] != 'sustain-to-brake':
            continue
        inv = row.get('inventory', {})
        storage = row.get('storage', {})
        mu = row.get('adhesion', {}).get('required_coefficient_uniform_loading')
        mass = inv.get('comparison_total_kg')
        adhesion_screen = ('fails-bound' if row['calculation_status'] == 'fails-optimistic-adhesion-bound' else 'unknown') if mu is None else 'fails-bound' if mu > .10 else 'not-ruled-out'
        lines.append(f"| {r['powered_bogies']} | {r['acceleration_m_s2']:g} m/s² | {row['calculation_status']} | {'Unknown' if mass is None else f'{mass/1000:.2f} t'} | {storage.get('module_count', 'Unknown')} | {'Unknown' if mu is None else f'{mu:.3f}'} | {adhesion_screen} | {row.get('service', {}).get('directional_ring_train_floor', 'Unknown')} |")
    lines += ['', 'Comparison mass includes catalogue accounts and stated installation/inertia hypotheses; it is not installed tare. No price ranking or physical selection is produced.', '',
        '## Next experiments', '',
        '- Retain the two-bogie user seed as a conditional lower-acceleration comparison; add driven axles where the uniform-load adhesion bound fails.',
        '- Investigate six 20 m primary sites for the stronger geometric handoff envelope. Obtain a finite-position, one/two-fin force/current/thermal map and train-level hanger/coupler assessment.',
        '- Replace the illustrative grid-capacitor/metro-drive leads with compatible supplier-defined rail hardware. Compare cooling, higher-density or hybrid storage, complete power/energy maps and actual quotations.',
        '- Propagate a materialized revision through independently protected journeys, full installed inventory, braking, civil loads, assembly and whole-life economics before ranking an integrated railway.', '',
        f"Study identity: `{value['study_id']}`.", '']
    return '\n'.join(lines)


def quote_scope(value):
    """Counted enquiry scope only; no prices or external submissions invented."""
    wheel = []
    for row in value['wheel_cases']:
        if 'physical_definition' not in row:
            continue
        p = row['physical_definition']
        wheel.append(dict(physical_option_id=row['physical_option_id'], evaluation_id=row['evaluation_id'],
            request=row['request'], item_quantities=dict(motors=p['motor_count'], gearboxes=p['gearbox_count'],
                capacitor_modules=p['capacitor_modules'], conceptual_capacitor_cabinets=p['bank_count'],
                inverter_motor_channels=p['driven_axles'], boost_conversion_channels=p['bank_count'],
                charging_interfaces=p['bank_count'], branch_protection_channels=p['bank_count'] * p['parallel_strings_per_bank'],
                actual_fastener_joint_wiring_cooling_quantities=None),
            required_supplied_data=['Physical fit and dimensional drawings; new/worn wheel interfaces',
                'Hot/end-of-life torque, speed, voltage, current, loss and repeated-duty maps',
                'Complete installed mass, CG/inertia, maintenance envelopes and component origin',
                'Charge, isolation, protection, reserve and degraded recovery definitions',
                'Itemised equipment, assembly, installation, spares, cooling and renewal quotations'],
            required_peak_mechanical_power_W=row['target_profile']['required_peak_mechanical_power_W'],
            conditional_vehicle_cycle_s=row['service']['conditional_vehicle_cycle_s'],
            required_reviewed_prices=None, quotation_currency=None,
            supplier_approved_fit=False, purchase_or_RFQ_submitted=False))
    sparse = [dict(physical_geometry_id=row['geometry']['physical_geometry_id'],
        site_count=row['site_count'], primary_face_count=2 * row['site_count'],
        launch_only_longitudinal_extent_m=row['site_count'] * row['bank_length_m'],
        launch_primary_face_length_sum_m=2 * row['site_count'] * row['bank_length_m'],
        required_train_peak_force_N=row['required_train_peak_force_N'],
        required_reviewed_prices=None, quotation_currency=None,
        receiving_installation_quantity=None, conductor_copper_cooling_bracket_fastener_quantities=None,
        required_supplied_data=['Actual finite-position/partial-fin force, current, normal-force and thermal maps',
            'Train-level fin/hanger/coupler load interfaces and worn/swept clearances',
            'Complete primary/inverter/feeder/cooling/installation and access quantities',
            'Failed site, stuck thrust, receiving, independent stopping and rescue definitions',
            'Itemised installation, maintenance, energy, reliability, renewal and origin quotations'],
        purchase_or_RFQ_submitted=False) for row in value['sparse_cases']]
    return dict(schema='osr-propulsion-quotation-scope/1', study_id=value['study_id'],
        status='draft-not-submitted', wheel_options=wheel, sparse_options=sparse,
        wheel_quantity_basis='One six-car train per independent alternative; never sum evaluation rows into a fleet BOM',
        sparse_quantity_basis='One station departure direction; receiving and the opposite direction remain separate',
        equal_service=dict(normal_people_per_train=276, target_pphpd=8280,
            actual_protected_headway_s=None, actual_fleet=None),
        whole_railway_cost_scope=['vehicles and fitted equipment', 'launch and receiving', 'power supply and charging',
            'civil works and access', 'factories, tooling and assembly', 'fleet, spares and rescue',
            'purchased energy, maintenance, renewals and service disruption'],
        monetary_totals=None, cheapest_railway=None, live_business_records_created=False, **FLAGS)


def overlap_figure(value):
    """Render a deterministic SVG of piecewise-linear geometry; no thrust claim."""
    from html import escape

    rows = value['sparse_cases']
    min_bank = min(row['bank_length_m'] for row in rows)
    max_bank = max(row['bank_length_m'] for row in rows)
    max_sites = max(row['site_count'] for row in rows)
    chosen = {(3, max_bank), (max_sites, min_bank), (max_sites, max_bank)}
    selected = [row for row in rows if (row['site_count'], row['bank_length_m']) in chosen]
    if not selected:
        raise ValueError('At least one bounded sparse geometry is required for the plot')

    width, height = 1000, 380
    left, right, top, bottom = 92.0, 976.0, 50.0, 300.0
    x_max = float(value['specification']['sparse']['required_launch_travel_m'])
    if not isfinite(x_max) or x_max <= 0:
        raise ValueError('Positive required launch travel is required for the plot')
    y_max = max(point['sum_overlap_m'] for row in selected
                for point in row['geometry']['breakpoint_records'])
    y_step = 5.0 if y_max > 5.0 else 1.0
    y_limit = y_step * ceil(y_max / y_step)
    y_limit = max(y_step, y_limit)

    def number(x):
        return f'{x:.3f}'.rstrip('0').rstrip('.')

    def label_number(x):
        return f'{x:.6g}'

    def px(x):
        return left + float(x) / x_max * (right - left)

    def py(y):
        return bottom - float(y) / y_limit * (bottom - top)

    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>Sparse launch: geometric contact continuity, not available thrust</title>',
        '<desc>Piecewise-linear overlap geometry. The curves do not represent available propulsion force.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<g font-family="DejaVu Sans, sans-serif" fill="#222222">',
        '<text x="92" y="28" font-size="16">Sparse launch: geometric contact continuity, not available thrust</text>',
        '</g>',
        '<g stroke="#b0b0b0" stroke-opacity="0.25" stroke-width="1">',
    ]
    x_step = x_max / 5.0
    x_tick = 0.0
    while x_tick <= x_max + x_step * 1e-9:
        x = px(x_tick)
        pieces.append(f'<path d="M {number(x)} {number(top)} V {number(bottom)}"/>')
        x_tick += x_step
    y_tick = 0.0
    while y_tick <= y_limit + y_step * 1e-9:
        y = py(y_tick)
        pieces.append(f'<path d="M {number(left)} {number(y)} H {number(right)}"/>')
        y_tick += y_step
    pieces.extend(['</g>', '<g font-family="DejaVu Sans, sans-serif" fill="#222222" font-size="12">'])
    x_tick = 0.0
    while x_tick <= x_max + x_step * 1e-9:
        pieces.append(f'<text x="{number(px(x_tick))}" y="319" text-anchor="middle">{escape(label_number(x_tick))}</text>')
        x_tick += x_step
    y_tick = 0.0
    while y_tick <= y_limit + y_step * 1e-9:
        pieces.append(f'<text x="82" y="{number(py(y_tick) + 4)}" text-anchor="end">{escape(label_number(y_tick))}</text>')
        y_tick += y_step
    pieces.extend([
        f'<text x="{number((left + right) / 2)}" y="356" text-anchor="middle">Forward travel from the berthed position (m)</text>',
        f'<text x="22" y="{number((top + bottom) / 2)}" text-anchor="middle" transform="rotate(-90 22 {number((top + bottom) / 2)})">Summed fin / primary overlap (m)</text>',
        '</g>',
        f'<path d="M {number(left)} {number(top)} V {number(bottom)} H {number(right)}" fill="none" stroke="#222222" stroke-width="1"/>',
        f'<clipPath id="plot"><rect x="{number(left)}" y="{number(top)}" width="{number(right-left)}" height="{number(bottom-top)}"/></clipPath>',
        '<g clip-path="url(#plot)" fill="none" stroke-width="1.6">',
    ])
    colors = ('#1f77b4', '#ff7f0e', '#2ca02c')
    for index, row in enumerate(selected):
        points = row['geometry']['breakpoint_records']
        commands = []
        for point_index, point in enumerate(points):
            command = 'M' if point_index == 0 else 'L'
            commands.append(f'{command} {number(px(point["nose_advance_m"]))} {number(py(point["sum_overlap_m"]))}')
        dash = ' stroke-dasharray="5 4"' if row['site_count'] == 3 else ''
        pieces.append(f'<path d="{" ".join(commands)}" stroke="{colors[index % len(colors)]}"{dash}/>')
    pieces.extend(['</g>'])

    legend_x, legend_y = left + 12.0, top + 106.0
    legend_height = 16.0 + 18.0 * len(selected)
    pieces.append(f'<rect x="{number(legend_x)}" y="{number(legend_y)}" width="220" height="{number(legend_height)}" rx="2" fill="#ffffff" fill-opacity="0.92" stroke="#777777" stroke-width="0.6"/>')
    pieces.append('<g font-family="DejaVu Sans, sans-serif" fill="#222222" font-size="11">')
    for index, row in enumerate(selected):
        y = legend_y + 16.0 + 18.0 * index
        color = colors[index % len(colors)]
        dash = ' stroke-dasharray="5 4"' if row['site_count'] == 3 else ''
        pieces.append(f'<path d="M {number(legend_x + 8)} {number(y - 3)} H {number(legend_x + 38)}" fill="none" stroke="{color}" stroke-width="1.6"{dash}/>')
        text = f'{row["site_count"]} sites × {row["bank_length_m"]:g} m'
        pieces.append(f'<text x="{number(legend_x + 45)}" y="{number(y)}">{escape(text)}</text>')
    pieces.extend(['</g>', '</svg>'])
    return ('\n'.join(pieces) + '\n').encode('utf-8')


def retain(root, value):
    """Immutable numerical input/output package; preserves interrupted work."""
    root = Path(root)
    study_id = value.get('study_id')
    if not isinstance(study_id, str) or len(study_id) != 64 or any(c not in '0123456789abcdef' for c in study_id):
        raise ValueError('Explicit content-addressed study identity required')
    if (study_id != identity({k:v for k,v in value.items() if k != 'study_id'})
            or any(value.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError('Retained study identity or non-promoting disposition differs')
    target = root / 'build/propulsion-layout/runs' / value['study_id']
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w') as archive:
        total = 0
        for name, expected in sorted(value['source_sha256'].items()):
            path = Path(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Ordinary source paths required')
            source = root / path
            if source.is_symlink():
                raise ValueError('Numerical input changed before immutable retention')
            raw = source.read_bytes()
            if sha256(raw).hexdigest() != expected:
                raise ValueError('Numerical input changed before immutable retention')
            total += len(raw)
            if total > 32 * 1024**2:
                raise ValueError('Bounded numerical input package required')
            item = tarfile.TarInfo(name)
            item.size, item.mtime, item.mode = len(raw), 0, 0o644
            archive.addfile(item, io.BytesIO(raw))
    records.atomic_immutable(target / 'input-sources.tar.gz', gzip.compress(buffer.getvalue(), mtime=0))
    records.atomic_immutable(target / 'result.json.gz', gzip.compress(encoded(value), mtime=0))
    return target


def publish(root=ROOT):
    root = Path(root)
    value = compare(root)
    retained = retain(root, value)
    if value['execution'] != 'completed':
        return dict(published=False, retained_run=retained.relative_to(root).as_posix(), **summary(value))
    target = root / OUTPUT
    launch_options._write(target / 'comparison.json.gz', gzip.compress(encoded(value), mtime=0))
    launch_options._write(target / 'comparison-summary.md', findings(value).encode())
    launch_options._write(target / 'quotation-scope.json', encoded(quote_scope(value)))
    launch_options._write(target / 'overlap.svg', overlap_figure(value))
    manifest = dict(schema='osr-propulsion-layout-publication/1', study_id=value['study_id'],
        source_sha256=value['source_sha256'], files_sha256={name: digest(target / name) for name in ('comparison.json.gz', 'comparison-summary.md', 'quotation-scope.json', 'overlap.svg')}, **FLAGS)
    manifest['manifest_id'] = identity(manifest)
    launch_options._write(target / 'manifest.json', encoded(manifest))
    return dict(published=True, **summary(value))


def verify(root=ROOT):
    root = Path(root)
    value = compare(root)
    if value['execution'] != 'completed':
        retain(root, value)
        raise ValueError('Verification interrupted; partial numerical package retained')
    target = root / OUTPUT
    manifest = json.loads((target / 'manifest.json').read_bytes())
    if (manifest.get('schema') != 'osr-propulsion-layout-publication/1'
            or manifest.get('manifest_id') != identity({k:v for k,v in manifest.items() if k != 'manifest_id'})
            or manifest.get('study_id') != value['study_id'] or manifest.get('source_sha256') != value['source_sha256']
            or manifest.get('files_sha256') != {name: digest(target / name) for name in ('comparison.json.gz', 'comparison-summary.md', 'quotation-scope.json', 'overlap.svg')}
            or any(manifest.get(k) is not v for k,v in FLAGS.items())
            or gzip.decompress((target / 'comparison.json.gz').read_bytes()) != encoded(value)
            or (target / 'comparison-summary.md').read_text() != findings(value)
            or (target / 'quotation-scope.json').read_bytes() != encoded(quote_scope(value))
            or (target / 'overlap.svg').read_bytes() != overlap_figure(value)):
        raise ValueError('Propulsion study source, payload or non-promoting disposition differs')
    return dict(verified=True, **summary(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'compare', 'publish', 'verify'))
    action = parser.parse_args().action
    if action == 'plan':
        value = specification()
    elif action == 'compare':
        result = compare()
        retain(ROOT, result)
        value = summary(result)
    else:
        value = globals()[action]()
    print(json.dumps(value, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
