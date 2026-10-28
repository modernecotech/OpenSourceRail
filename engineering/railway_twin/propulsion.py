"""Count a new short-bank motor; available propulsion remains an evidence hold.

The stock and circuit arithmetic describe proposed hardware, not measured force,
finished winding geometry, an installed converter or a qualified railway.
"""
from copy import deepcopy
from math import fsum, sqrt
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.design_search import launch_options, railway_bundle, sparse_launch, wheel_motor

PRODUCER = 'engineering/railway_twin/propulsion.py'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False, physical_journey_completed=False,
             native_evaluator_admission=False)
BANK_STARTS_M = [91.5, 191.875, 292.25, 392.625, 493.]


def _winding(parameters, definition):
    """Explicit proposed slot/coil/path registration, with physical routing open."""
    p = parameters['physical']
    paths, periods = p['parallel_paths_per_phase'], p['periods']
    coils = []
    phase_slots = [('A', 0, 3), ('B', 2, 5), ('C', 4, 1)]
    for side_index, face in enumerate((-1, 1)):
        for period in range(periods):
            for phase_index, (phase, positive, negative) in enumerate(phase_slots):
                path = (side_index * periods + period) % paths
                slots = [period * 6 + positive, period * 6 + negative]
                coils.append(dict(coil_id=f'face/{face}/period/{period}/phase/{phase}',
                    face=face, period=period, phase=phase,
                    branch_id=f'{phase}/{path}', series_order=(side_index * periods + period) // paths,
                    signed_slots=[dict(slot_index=slot, sign=sign,
                        centre_x_m=(slot + .5) * definition['slot_pitch_m'])
                        for slot, sign in zip(slots, (1, -1))],
                    turns=p['turns_per_coil'], wire_length_m_hypothesis=definition['wire_length_m_per_coil']))
    branches = []
    for phase, _, _ in phase_slots:
        for path in range(paths):
            members = [c for c in coils if c['branch_id'] == f'{phase}/{path}']
            members.sort(key=lambda c: c['series_order'])
            length = fsum(c['wire_length_m_hypothesis'] for c in members)
            resistance = definition['copper_resistivity_20C_ohm_m_hypothesis'] * length / p['conductor_area_m2']
            branches.append(dict(branch_id=f'{phase}/{path}', phase=phase,
                coil_ids=[c['coil_id'] for c in members], coils_in_series=len(members),
                coils_per_face={str(face): sum(c['face'] == face for c in members) for face in (-1, 1)},
                wire_length_m_hypothesis=length, resistance_20C_ohm_hypothesis=resistance,
                resistance_80C_ohm_hypothesis=resistance * (1 + definition['copper_temperature_coefficient_K_inv_hypothesis'] * 60),
                leakage_inductance_H=None, flux_linkage_map=None,
                actual_lead_and_terminal_resistance_ohm=None))
    result = dict(schema='osr-short-bank-winding-hypothesis/1',
        motor_component_id=definition['motor_component_id'], faces=2,
        periods_per_face=periods, slot_occurrences_per_face=6 * periods,
        slot_occurrences_both_faces=12 * periods, coil_count_both_faces=len(coils),
        branches=len(branches), parallel_paths_per_phase=paths,
        coils_per_branch_both_faces=8, coils_per_branch_per_face=4,
        phase_sequence=deepcopy(p['phase_sequence']), coils=coils, branch_records=branches,
        neutral='proposed floating neutral; total branch current closes to zero',
        registration='Round-robin face-period coil pairs; signed slots follow the retained six-slot phase order',
        actual_connection_verified=False, phase_polarity_and_force_direction_verified=False,
        end_turn_geometry=None, insulation_and_creepage_geometry=None,
        interbank_phase_and_current_handoff=None, **FLAGS)
    result['winding_definition_id'] = identity(result)
    return result


def materialize():
    """Return one 20 m, double-sided bank; never duplicate the onboard fin."""
    parameters = wheel_motor.default_parameters()
    parameters['physical'].update(name='sparse-20m-primary-research', primary_length_m=20., periods=40)
    definition = wheel_motor.definition(parameters)
    stock = [p for p in wheel_motor.stock(parameters) if p['installation'] == 'wayside']
    value = dict(schema='osr-short-bank-propulsion-materialization/1',
        parameters=parameters, motor_definition=definition, wayside_stock=stock,
        winding=_winding(parameters, definition), onboard_secondary_added=False,
        stock_scope='Bare primary copper and steel; copper is equal-volume stock with a wire-length hypothesis, not finished coil placement',
        complete_installed_mass_kg=None, available_force_map=None, **FLAGS)
    value['materialization_id'] = identity(value)
    return value


def _bound(bundle, geometry):
    railway_bundle.validate(bundle)
    plant = materialize()
    expected = sparse_launch.geometry(BANK_STARTS_M, 20., initial_nose_m=104.5, launch_distance_m=500.)
    if encoded(geometry) != encoded(expected):
        raise ValueError('Exact five-bank contact geometry required; revise this experiment explicitly')
    if (encoded(bundle['motor_definition']) != encoded(plant['motor_definition'])
            or encoded(bundle['motor_parameters']) != encoded(plant['parameters'])):
        raise ValueError('Bundle motor differs from the counted 20 m plant')
    wayside = bundle['architecture_case']['physical_definition']['wayside']
    if (wayside.get('sparse_geometry_id') != geometry['physical_geometry_id']
            or wayside.get('sparse_contact_evaluation_id') != geometry['geometry_result_id']):
        raise ValueError('Installed sparse bank identities differ from the canonical bundle')
    onboard = bundle['architecture_case']['physical_definition']['onboard']
    if (onboard.get('drive') != 'none' or onboard.get('driven_axle_count') != 0
            or onboard.get('supply') != 'auxiliary-only'
            or onboard.get('traction_store_geometry_id') != 'not-applicable'):
        raise ValueError('This propulsion direction retains passive bogies and no onboard traction store')
    if (bundle['cars'] != 6 or bundle['car_length_m'] != 17. or bundle['coupling_gap_m'] != .5
            or bundle['family_id'] != 'P1' or bundle['requirements']['target_headway_s'] != 120.
            or bundle['requirements']['speed_cap_m_s'] != 20.
            or bundle['requirements']['acceleration_m_s2'] != .4
            or bundle['architecture_case']['commanded_power_windows_m'] != [[0., 500.]]):
        raise ValueError('Fixed passive six-car launch and service interfaces required')
    return plant


def _contact_intervals(geometry, index):
    """Intervals of possible engagement, independent of force or energization."""
    events, records = geometry['breakpoints_m'], geometry['interval_records']
    intervals = []
    for lo, hi, row in zip(events, events[1:], records):
        if any(p['site_index'] == index for p in row['overlap_pairs']):
            if intervals and intervals[-1][1] == lo:
                intervals[-1][1] = hi
            else:
                intervals.append([lo, hi])
    return intervals


def requirements(bundle, geometry, *, root=ROOT):
    """Same-candidate stock, necessary launch bounds and open electrical duty."""
    root = Path(root)
    if digest(root / PRODUCER) != digest(__file__):
        raise ValueError('Executing propulsion producer differs from declared source root')
    plant = _bound(bundle, geometry)
    p, d, wiring = plant['parameters']['physical'], plant['motor_definition'], plant['winding']
    load_keys = dict(empty='accounted_tare_kg_per_car', normal='accounted_cap_loaded_kg_per_car',
                     crowd='accounted_160_control_kg_per_car')
    demands = [dict(load=load, grade_fraction=grade, accounted_train_mass_kg=6 * bundle['mass'][key],
        result=launch_options.bounds(6 * bundle['mass'][key], 6 * bundle['rotating_equivalent_kg_per_car'],
            20., .4, grade=grade)) for load, key in load_keys.items() for grade in (0., .02, -.02)]
    stock = []
    sites = []
    records = geometry['breakpoint_records'] + geometry['interval_records'] + geometry['single_fin_envelope_records']
    for index, start in enumerate(geometry['physical_geometry']['bank_starts_m']):
        local = []
        for part in plant['wayside_stock']:
            row = deepcopy(part)
            row.update(id=f'bank/{index}/' + part['id'], site_index=index,
                       candidate_id=bundle['candidate_id'])
            row['at_m'][0] += start
            row['cg_m'][0] += start
            local.append(row)
        stock.extend(local)
        intervals = _contact_intervals(geometry, index)
        contact_s = fsum(sqrt(2 * hi / .4) - sqrt(2 * lo / .4) for lo, hi in intervals)
        solo = [r['nose_advance_m'] for r in records if r['active_sites'] == 1
                and any(pair['site_index'] == index for pair in r['overlap_pairs'])]
        force_rows = []
        for load, key in load_keys.items():
            m = 6 * bundle['mass'][key]
            inertial = m + 6 * bundle['rotating_equivalent_kg_per_car']
            for grade in (0., .02, -.02):
                def effort(advance):
                    return inertial * .4 + m * launch_options.G * (.0025 + grade) + 6 * 50 + 6 * 1.8 * (2 * .4 * advance)
                force_rows.append(dict(load=load, grade_fraction=grade,
                    necessary_solo_peak_force_N=None if not solo else max(effort(x) for x in solo),
                    available_force_N=None))
        sites.append(dict(site_index=index, start_m_from_first_bank=start, length_m=20., primary_faces=2,
            motor_component_id=bundle['propulsion_component_id'], branch_count=wiring['branches'],
            stock_part_ids=[s['id'] for s in local], bare_primary_stock_kg=fsum(s['mass_kg'] for s in local),
            potential_contact_windows_nose_advance_m=intervals,
            potential_contact_time_s_required_motion=contact_s,
            potential_contact_fraction_at_120s_headway=contact_s / 120.,
            actual_energized_time_s=None, actual_current_trace_A=None,
            required_force_envelopes=force_rows, actual_available_force_map=None,
            inverter_channel_count=None, feeder_and_isolation_design=None,
            cooling_capacity_W=None, repeated_temperature_C=None,
            actual_thermal_capacity_J_K=None, installed_mass_kg=None, installed_cost_USD=None))
    peak = plant['parameters']['evaluation']['current_peak_A']
    copper_cases = [dict(temperature_C=T, branch_current_peak_A_hypothesis=peak,
        balanced_phase_current_peak_A_hypothesis=10 * peak,
        copper_heat_W_per_bank_hypothesis=fsum(b[key] for b in wiring['branch_records']) * peak**2 / 2)
        for T, key in ((20., 'resistance_20C_ohm_hypothesis'), (80., 'resistance_80C_ohm_hypothesis'))]
    tasks = [
        dict(id='short-bank/wiring', question='Confirm the proposed 20 m,40-period,30-branch,8-coil/path connection, signs and finite3D end-turn routing',
             required=['As-built slot/coil/branch connectivity and terminals', 'Phase/polarity, resistance, leakage and flux-linkage records']),
        dict(id='short-bank/moving-map', question='Extend and independently verify a separately versioned moving evaluator for this exact20m geometry and wiring',
             required=['Zero/reversal/blocked/moving matched controls', 'Mesh/time/outer-domain convergence', 'Finite-height, current-sharing, position/speed/gap/temperature force map']),
        dict(id='short-bank/current-control', question='Resolve converter, branch current, sectional phase registration, isolation and handoff',
             required=['R/L/flux converter circuit and bus/current/voltage limits', 'Per-bank normal/transient forces and wheel/fin/hanger/coupler interfaces', 'Independent brake and external rescue interfaces']),
        dict(id='short-bank/repeated-duty', question='Resolve120s repeated station duty, primary/secondary/inverter heat, cooling and receiving',
             required=['Installed thermal masses and heat-transfer paths', 'Measured losses, cooling and hot restart', 'Receiving/regeneration or dump plant and simultaneous station duties']),
        dict(id='short-bank/installation', question='Complete the power, protection, supports and repair installation without assuming one shared drive',
             required=['Inverters, switching, feeders, busbars, supply, protection, earthing, sensors and controls', 'Supports, joints, insulation, cooling, access, spares and quantities', 'Installed supplier mass, prices, origin and replacement data'])]
    names = (PRODUCER, wheel_motor.PRODUCER, 'engineering/station_rail/station_motor.py',
             'engineering/design_search/moving_lim.py', 'engineering/design_search/sparse_launch.py',
             'engineering/design_search/launch_options.py', 'engineering/design_search/railway_bundle.py')
    value = dict(schema='osr-short-bank-propulsion-requirements/1',
        candidate_id=bundle['candidate_id'], bundle_definition_id=bundle['definition_id'],
        body_candidate_id=bundle['body_candidate_id'], support_component_id=bundle['support_component_id'],
        propulsion_component_id=bundle['propulsion_component_id'],
        geometry_id=geometry['physical_geometry_id'], contact_evaluation_id=geometry['geometry_result_id'],
        materialization=plant, sites=sites, wayside_stock=stock, launch_demands=demands,
        launch_bank_count=5, primary_faces=10, primary_bank_extent_m=100., primary_face_extent_m=200.,
        coil_count_both_faces_all_banks=5 * wiring['coil_count_both_faces'],
        branch_count_all_banks=5 * wiring['branches'],
        bare_copper_stock_kg=fsum(s['mass_kg'] for s in stock if s['role'] == 'copper-stock'),
        bare_steel_stock_kg=fsum(s['mass_kg'] for s in stock if s['role'] != 'copper-stock'),
        bare_primary_stock_kg=fsum(s['mass_kg'] for s in stock),
        copper_heat_hypotheses=copper_cases, actual_electrical_input_W=None,
        operating_force_map_id=None, force_map_admitted=False, full_installed_mass_kg=None,
        full_installed_cost_USD=None, receiving_equipment_count=None,
        native_moving_evaluator_compatible=False,
        native_incompatibility='Retained moving_lim validates only12.5m/25periods/5coils-per-path with a hardcoded25-period side offset;20m/40periods/8coils-per-path is a different component',
        repeated_thermal_duty_verified=False, required_tests=tasks,
        scope='Launch-side bare stock and necessary motion/circuit hypotheses; no available thrust, actual electrical/thermal duty, receiving installation, cheapest architecture or physical qualification',
        source_sha256={name:digest(root / name) for name in names}, **FLAGS)
    value['evaluation_id'] = identity(value)
    return value
