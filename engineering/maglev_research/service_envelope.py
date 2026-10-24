"""Conditional service tradeoffs at counted AW3 mass; no operating adoption.

The jerk-limited station plant is reused with the retained 1,349 A force coupon.
Field/current/group sharing, receiving maps, cooling and support remain open.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import tomllib

import numpy as np

from engineering.ferrite_maglev import station
from . import propulsion_research

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/'docs/design-engine/ferrite-maglev/research-closure/service-envelope.json'
SUPPORT = Path('docs/design-engine/ferrite-maglev/research-closure/support-architecture.json')
FLAGS = dict(configuration_adopted=False, design_complete=False,
             engineering_accepted=False, physical_validation=False, physical_release=False)
SOURCE_NAMES = ['engineering/maglev_research/service_envelope.py', 'engineering/maglev_research/propulsion_research.py',
    'engineering/ferrite_maglev/station.py', 'engineering/ferrite_maglev/station.toml',
    'engineering/ferrite_maglev/corridor.py', 'engineering/ferrite_maglev/corridor.toml',
    'engineering/ferrite_maglev/operating-plan.toml', 'engineering/ferrite_maglev/line-capacity.toml',
    'ferrite-maglev-study.toml', str(propulsion_research.ARCHIVE/'executed/results.json'),
    str(propulsion_research.ARCHIVE/'executed/current-boundary-diagnostic.json')]


def _canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def sources(root=ROOT, extra_names=()):
    return {name:sha256((Path(root)/name).read_bytes()).hexdigest() for name in [*SOURCE_NAMES, *extra_names]}


def charging(*, runtime_s, dwell_s, charger_kw_per_car, hotel_kw_per_car=60.,
             connected_fraction=.75, efficiency=.9, battery_kwh=30.,
             eol_fraction=.8, soc_window=.6, reserve_minutes=10.):
    values = (runtime_s, dwell_s, charger_kw_per_car, hotel_kw_per_car,
              connected_fraction, efficiency, battery_kwh, eol_fraction, soc_window)
    if any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in values):
        raise ValueError('finite positive charging inputs required')
    if not 0 < connected_fraction <= 1 or not 0 < efficiency <= 1 or not 0 < eol_fraction <= 1 or not 0 < soc_window <= 1:
        raise ValueError('charging/usable fractions must lie in (0,1]')
    if type(reserve_minutes) not in (int, float) or not math.isfinite(reserve_minutes) or reserve_minutes < 0:
        raise ValueError('finite nonnegative reserve duration required')
    travel = hotel_kw_per_car*(runtime_s+(1-connected_fraction)*dwell_s)/3600
    replacement = (charger_kw_per_car*efficiency-hotel_kw_per_car)*connected_fraction*dwell_s/3600
    reserve = hotel_kw_per_car*reserve_minutes/60
    usable = battery_kwh*eol_fraction*soc_window
    net = efficiency*connected_fraction*charger_kw_per_car-hotel_kw_per_car
    return dict(travel_and_disconnected_dwell_kwh_per_car=travel,
                recharge_available_kwh_per_car=replacement,
                protected_reserve_kwh_per_car=reserve, usable_eol_soc_window_kwh_per_car=usable,
                recharge_screen_pass=replacement >= travel,
                reserve_screen_pass=usable >= travel+reserve,
                minimum_dwell_for_energy_s=hotel_kw_per_car*runtime_s/net if net > 0 else None,
                battery_and_charger_qualified=False)


def full_engagement_zone(trajectory, train_length_m, *, group_length_m=5.):
    """Construct a whole-group sufficient extent, not an optimised minimum."""
    if not trajectory.get('study_pass') or train_length_m <= 0 or group_length_m <= 0:
        raise ValueError('passing trajectory and positive installed dimensions required')
    launch = trajectory['phases']['launch']['distance_m']
    brake = trajectory['phases']['braking']['distance_m']
    start = -math.ceil((train_length_m+brake)/group_length_m)*group_length_m
    end = math.ceil(launch/group_length_m)*group_length_m
    spacing = trajectory['inputs']['distance_m']
    return dict(start_m=start, end_m=end, length_m=end-start,
                groups_per_direction=round((end-start)/group_length_m),
                continuous_full_engagement_bound_m=train_length_m+launch+brake,
                powered_fraction_per_direction=(end-start)/spacing,
                unpowered_gap_between_station_zones_m=spacing-(end-start),
                scope='Whole5m groups covering the complete train envelope through prescribed launch and receiving phases; sufficient geometric construction bound, no minimum-cost or magnetic sharing proof.')


def group_duty(trajectory, zone, *, mass_kg_per_car, cars, body_length_m,
               coupling_gap_m, band_length_m, force_per_a, reference_current_a,
               group_resistance_80c_ohm, group_copper_mass_kg, copper_specific_heat,
               copper_alpha, step_s=.1):
    """Sample ideal uniform group-current allocation and retain worst local I²t.

    Every overlapping 5m group receives the same signed current proportional to
    prescribed whole-train force. This is an unvalidated finite-overlap current
    allocation, not an executed harmonic/Rust/inverter field map.
    """
    if not 0 < step_s <= .1 or force_per_a <= 0 or not trajectory.get('study_pass'):
        raise ValueError('bounded phase sampling and positive force gain required')
    starts = np.arange(zone['start_m'], zone['end_m'], 5.)
    integral = np.zeros(len(starts))
    peak_current = peak_copper = copper_j80 = peak_input_bound = 0.
    per_car_constant = trajectory['resistance']['constant_n_per_car'] + mass_kg_per_car*9.81*trajectory['inputs']['grade']
    per_car_quadratic = trajectory['resistance']['quadratic_n_per_car_per_m_s_squared']
    band_offset = (body_length_m-band_length_m)/2
    relative_front = np.array([-band_offset-j*(body_length_m+coupling_gap_m) for j in range(cars)])
    for phase in ('launch', 'braking'):
        for segment in trajectory['segments'][phase]:
            duration = segment['duration_s']
            if duration <= 0:
                continue
            count = max(1, math.ceil(duration/step_s))
            dt = duration/count
            time = (np.arange(count)+.5)*dt
            v0, a0, jerk = (segment[key] for key in ('start_speed_m_s', 'start_acceleration_m_s2', 'jerk_m_s3'))
            speed = v0+a0*time+.5*jerk*time**2
            acc = a0+jerk*time
            x = segment['start_position_m']+v0*time+.5*a0*time**2+jerk*time**3/6
            if phase == 'braking':
                x -= trajectory['phases']['braking']['distance_m']
            per_car_force = mass_kg_per_car*acc+per_car_constant+per_car_quadratic*speed**2
            current = per_car_force/force_per_a
            active = np.zeros((count, len(starts)), dtype=bool)
            for offset in relative_front:
                right = x[:,None]+offset
                left = right-band_length_m
                active |= (np.minimum(right, starts[None,:]+5)-np.maximum(left, starts[None,:])) > 0
            i2 = current**2
            integral += np.sum(active*i2[:,None], axis=0)*dt
            watts = 1.5*group_resistance_80c_ohm*i2*np.sum(active, axis=1)
            copper_j80 += float(np.sum(watts)*dt)
            peak_copper = max(peak_copper, float(np.max(watts)))
            # Explicit copper is added to mechanical power; the older fixed
            # station efficiency assumption is not reused as an electrical map.
            peak_input_bound = max(peak_input_bound, float(np.max(cars*per_car_force*speed+watts)))
            peak_current = max(peak_current, float(np.max(np.abs(current))))
    worst = float(np.max(integral))
    equivalent_pulse = worst/reference_current_a**2
    no_cooling = propulsion_research.adiabatic_duty(current_a=reference_current_a,
        resistance_80c_ohm=group_resistance_80c_ohm, copper_mass_kg=group_copper_mass_kg,
        specific_heat_j_kg_k=copper_specific_heat, alpha_per_k=copper_alpha,
        pulse_s=max(equivalent_pulse, 1e-12), period_s=180., cycles=40)
    return dict(sample_interval_max_s=step_s, counted_groups_per_direction=len(starts),
                peak_allocated_current_a=peak_current, worst_group_i2t_a2_s=worst,
                worst_group_equivalent_1349a_pulse_s=equivalent_pulse,
                total_copper_heat_at_80c_kwh_per_train_cycle=copper_j80/3.6e6,
                peak_copper_heat_at_80c_kw=peak_copper/1000,
                peak_mechanical_plus_80c_copper_input_kw=peak_input_bound/1000,
                worst_group_40cycle_no_cooling=no_cooling,
                all_group_i2t_a2_s=integral.tolist(),
                group_resistance_at_40c_ohm=group_resistance_80c_ohm*(1+20*copper_alpha)/(1+60*copper_alpha),
                group_resistance_at_120c_ohm=group_resistance_80c_ohm*(1+100*copper_alpha)/(1+60*copper_alpha),
                thermal_equilibrium_established=False,
                scope='Midpoint sampling of declared uniform-current group allocation for arrival+departure. Slot/phase/end effects, common-current realizability, commutation, cooling and controller action remain unvalidated.')


def _slim(t):
    keys = ('runtime_s', 'peak_speed_kmh', 'launch_speed_kmh', 'brake_entry_speed_kmh',
            'peak_traction_force_n', 'peak_braking_force_n',
            'peak_mechanical_propulsion_kw', 'peak_mechanical_braking_kw',
            'launch_mechanical_work_kwh', 'receiving_brake_mechanical_work_kwh', 'phases', 'energy_balance')
    return {key:t[key] for key in keys}


def study(root=ROOT, comparison_mass_kg=None, accelerations_m_s2=(.15, .2)):
    root = Path(root).resolve()
    evidence = propulsion_research.study(root)
    primary = tomllib.loads((root/'ferrite-maglev-study.toml').read_text())
    a = station.load()
    corridor = tomllib.loads((root/'engineering/ferrite_maglev/corridor.toml').read_text())
    base = root/propulsion_research.ARCHIVE
    original = json.loads((base/'executed/results.json').read_text())
    boundary = json.loads((base/'executed/current-boundary-diagnostic.json').read_text())
    selected = next(row for row in boundary['rows'] if row['requested_q_current_a'] == 1349.)
    sample = next(row for row in original['resolved_corner_operating']['operating_samples'] if row.get('map_valid_for_this_sample') and row['speed_m_s'] == 20.)
    flux_inputs = json.loads((base/'executed/inputs/resolved8mm-256-40.json').read_text())
    canonical_mass = evidence['comparison']['canonical_comparison_mass_kg']
    mass = canonical_mass if comparison_mass_kg is None else comparison_mass_kg
    if type(mass) not in (int, float) or not math.isfinite(mass) or not 5000 <= mass <= 100000:
        raise ValueError('bounded finite AW3 comparison mass required')
    if (not isinstance(accelerations_m_s2, (list, tuple)) or not 1 <= len(accelerations_m_s2) <= 8 or
            any(type(x) not in (int, float) or not math.isfinite(x) or not .1 <= x <= .2 for x in accelerations_m_s2)):
        raise ValueError('bounded acceleration comparison values in0.1..0.2 required')
    accelerations_m_s2 = sorted(set(accelerations_m_s2))
    support_binding = None
    if comparison_mass_kg is not None and (root/SUPPORT).is_file():
        support = json.loads((root/SUPPORT).read_bytes())
        contract = support.get('recommended_next_design_contract', {})
        if contract.get('controlled_aw3_material_lower_bound_kg_per_car') == mass:
            support_binding = dict(source_path=str(SUPPORT), source_sha256=sha256((root/SUPPORT).read_bytes()).hexdigest(),
                proposed_case_id=contract['proposed_case_id'], contract_sha256=sha256(_canonical(contract)).hexdigest(),
                controlled_aw3_material_lower_bound_kg_per_car=mass,
                scope='Exact counted support proposal material lower bound only. The declared guide-field/airgap-MMF bound remains optimistic; steel MMF/leakage, bodycarrier, protection, controls and full installed interfaces remain open.')
    source_snapshot = sources(root, [str(SUPPORT)] if support_binding else [])
    if support_binding and support_binding['source_sha256'] != source_snapshot[str(SUPPORT)]:
        raise ValueError('support source changed while binding its material mass')
    cars = a['vehicle']['cars']
    length = cars*a['vehicle']['body_length_m']+(cars-1)*a['vehicle']['coupling_gap_m']
    force = selected['force_x_n_per_car']
    force_per_a = force/1349.
    vehicle, power = primary['vehicle'], primary['power']
    aw2, aw3 = cars*vehicle['aw2_passengers_per_car'], cars*vehicle['aw3_passengers_per_car']
    target = aw2*3600/vehicle['scheduled_headway_seconds']
    copper = flux_inputs['materials']['copper']
    motion_profiles = []
    rows = []
    runtime_attempts = 0
    search_holds = []
    baseline_cars = cars
    sweep = [(baseline_cars, d) for d in (750., 1000., 1500., 2000., 3000., 5000.)]
    sweep += [(n, d) for n in (8, 10, 12) for d in (750., 1000.)]
    sweep += [(12, d) for d in (1500., 2000.)]
    for cars, spacing in sweep:
        length = cars*a['vehicle']['body_length_m']+(cars-1)*a['vehicle']['coupling_gap_m']
        aw2, aw3 = cars*vehicle['aw2_passengers_per_car'], cars*vehicle['aw3_passengers_per_car']
        for speed in (8., 10., 12., 15., 20.):
            for acceleration in accelerations_m_s2:
                identity = f'C{cars}-D{spacing:g}-V{speed:g}-A{acceleration:g}'
                chosen = None
                rejected = []
                # Earliest sampled runtime satisfying the declared <=50% powered
                # layout comparison. This is a bounded10s grid, not a global optimum.
                for runtime in range(60, 601, 10):
                    runtime_attempts += 1
                    t = station.trajectory(distance_m=spacing, runtime_s=runtime,
                        car_mass_kg=mass, cars=cars, acceleration=acceleration,
                        deceleration=.2, jerk=vehicle['jerk_study_m_s3'], speed_limit_kmh=3.6*speed,
                        record_trace=False, resistance_constant_n_per_car=power['passive_rail_drag_study_n_per_car'],
                        resistance_quadratic_n_per_car=.5*power['air_density_study_kg_m3']*power['drag_area_study_m2_per_car'])
                    if not t['study_pass']:
                        rejected.append(dict(runtime_s=runtime, reason=t.get('reason')))
                        continue
                    zone = full_engagement_zone(t, length)
                    if t['peak_traction_force_n']/cars > force or t['peak_braking_force_n']/cars > force:
                        rejected.append(dict(runtime_s=runtime, reason='Prescribed force exceeds conditional1349A coupon'))
                        continue
                    if zone['powered_fraction_per_direction'] > .5:
                        rejected.append(dict(runtime_s=runtime, reason='Whole-group full-engagement construction exceeds declared50% powered-length comparison'))
                        continue
                    clear_front = length+zone['end_m']+corridor['downstream_overlap_m']
                    clear_time = station._time_at_position(t, clear_front)
                    if clear_time is None:
                        rejected.append(dict(runtime_s=runtime, reason='Full-tail protected overlap cannot clear before next stop'))
                        continue
                    chosen = (t, zone, clear_front, clear_time)
                    break
                if chosen is None:
                    search_holds.append(dict(id=identity, cars=cars, train_length_m=length, station_spacing_m=spacing, max_speed_m_s=speed,
                        acceleration_m_s2=acceleration, attempts=rejected, study_pass=False, **FLAGS))
                    continue
                t, zone, clear_front, clear_time = chosen
                duty = group_duty(t, zone, mass_kg_per_car=mass, cars=cars,
                    body_length_m=a['vehicle']['body_length_m'], coupling_gap_m=a['vehicle']['coupling_gap_m'],
                    band_length_m=a['vehicle']['magnetic_band_m_per_car'], force_per_a=force_per_a,
                    reference_current_a=1349., group_resistance_80c_ohm=sample['group_R_ohm'][0],
                    group_copper_mass_kg=sample['group_copper_mass_kg'][0],
                    copper_specific_heat=copper['specific_heat_j_kg_k'], copper_alpha=copper['resistance_temperature_coefficient_per_k'])
                motion_profiles.append(dict(id=identity, cars=cars, train_length_m=length, station_spacing_m=spacing,
                    max_speed_m_s=speed, acceleration_m_s2=acceleration, deceleration_m_s2=.2,
                    trajectory=_slim(t), full_engagement_zone=zone,
                    full_tail_clear_front_m=clear_front, full_tail_clear_after_departure_s=clear_time,
                    uniform_current_group_duty=duty, rejected_runtime_attempts=rejected, **FLAGS))
                for dwell in (30., 45., 60.):
                    for charger in (240., 400., 600.):
                        services = charging(runtime_s=t['runtime_s'], dwell_s=dwell,
                            charger_kw_per_car=charger, hotel_kw_per_car=power['hot_hotel_kw_per_car'],
                            connected_fraction=corridor['connected_fraction'], efficiency=corridor['charger_efficiency'],
                            battery_kwh=power['services_battery_kwh_per_car'], eol_fraction=power['eol_capacity_fraction'],
                            soc_window=power['normal_soc_high']-power['normal_soc_low'],
                            reserve_minutes=corridor['protected_services_reserve_minutes'])
                        headway = t['runtime_s']+dwell+clear_time+corridor['release_allowance_s']
                        capacity = aw2*3600/headway
                        # For a necessary lower bound use the minimum40C
                        # resistance and maximum permitted80K heat-sink gradient.
                        # R120 instead supplies a separate mean-load design screen;
                        # it is not a strict lower bound for a pulsed temperature.
                        heat_g = 1.5*duty['group_resistance_at_40c_ohm']*duty['worst_group_i2t_a2_s']/headway/(120-40)
                        hot_load_g = 1.5*duty['group_resistance_at_120c_ohm']*duty['worst_group_i2t_a2_s']/headway/(120-40)
                        hotel = cars*power['hot_hotel_kw_per_car']*(t['runtime_s']+dwell)/3600
                        copper_heat = duty['total_copper_heat_at_80c_kwh_per_train_cycle']
                        passes = services['recharge_screen_pass'] and services['reserve_screen_pass']
                        rows.append(dict(id=f'{identity}-dwell{dwell:g}-charge{charger:g}', motion_profile_id=identity,
                            cars=cars, train_length_m=length, aw3_train_mass_kg=mass*cars,
                            aw2_passengers_per_train=aw2, aw3_passengers_per_train=aw3,
                            station_spacing_m=spacing, max_speed_m_s=speed, acceleration_m_s2=acceleration,
                            deceleration_m_s2=.2, dwell_s=dwell, charger_input_kw_per_car=charger,
                            peak_connected_charger_input_mw_train=charger*cars/1000,
                            services=services, runtime_s=t['runtime_s'], headway_lower_bound_s=headway,
                            conditional_capacity_aw2_pph=capacity, conditional_capacity_aw3_pph=aw3*3600/headway,
                            commercial_speed_kmh=3.6*spacing/(t['runtime_s']+dwell),
                            reference_throughput_floor_pass=capacity >= target,
                            conditional_longitudinal_energy_screens_pass=passes,
                            station_sites_per_route_km=1000/spacing,
                            platform_length_m_two_directions_per_route_km=2*length*1000/spacing,
                            installed_charger_input_kw_two_directions_per_route_km=2*charger*cars*1000/spacing,
                            powered_direction_m_per_route_km=zone['length_m']*1000/spacing,
                            winding_copper_kg_two_directions_per_route_km=2*zone['groups_per_direction']*sample['group_copper_mass_kg'][0]*1000/spacing,
                            stator_only_target_usd_two_directions_per_route_km=2*zone['length_m']*a['cost']['stator_usd_per_direction_m'][1]*1000/spacing,
                            stator_only_target_is_quote=False,
                            hotel_plus_80c_copper_kwh_per_train_km=(hotel+copper_heat)/(spacing/1000),
                            hotel_plus_80c_copper_kwh_per_aw2_capacity_passenger_km=(hotel+copper_heat)/(spacing/1000)/aw2,
                            worst_group_minimum_mean_heat_rejection_w_k=heat_g,
                            worst_group_mean_heat_rejection_at_120c_load_w_k=hot_load_g,
                            group_40cycle_no_cooling_screen_pass=duty['worst_group_40cycle_no_cooling']['adiabatic_temperature_screen_pass'],
                            system_eligible=False, **FLAGS))
    passing = [row for row in rows if row['conditional_longitudinal_energy_screens_pass']]
    meets_floor = [row for row in passing if row['reference_throughput_floor_pass']]
    best_capacity = max((row['conditional_capacity_aw2_pph'] for row in passing), default=0.)
    least_formation = min((row['cars'] for row in meets_floor), default=baseline_cars)
    formation_pool = [row for row in (meets_floor or passing) if row['cars'] == least_formation]
    formation_best_capacity = max((row['conditional_capacity_aw2_pph'] for row in formation_pool), default=0.)
    finalists = meets_floor or [row for row in formation_pool if row['conditional_capacity_aw2_pph'] >= .9*formation_best_capacity]
    ranked = sorted(finalists, key=lambda row:(row['station_sites_per_route_km'],
        row['platform_length_m_two_directions_per_route_km'],
        round(row['hotel_plus_80c_copper_kwh_per_aw2_capacity_passenger_km'], 8), row['powered_direction_m_per_route_km'],
        row['installed_charger_input_kw_two_directions_per_route_km'], row['cars'], row['max_speed_m_s'],
        -round(row['conditional_capacity_aw2_pph'], 3), row['id']))
    winner = ranked[0] if ranked else None
    recommendation = dict(winner) if winner else dict(configuration_adopted=False)
    recommendation.update(research_target_only=True,
        conditional_capacity_pph=winner['conditional_capacity_aw2_pph'] if winner else 0.,
        reference_throughput_floor_met=bool(meets_floor),
        duty_limitations='Actual map sharing/current control/cooling and receiving duty remain open.40cycle no-cooling fixture must not inherit the earlier5s coupon pass.',
        failed_gates=['Same-revision validated magnetic lift/guidance support', 'Converged propulsion/receiving maps and phase registration',
            'Actual whole-train inverter/current control', 'Measured station winding cooling/repeated duty',
            'Boarding/door throughput for altered dwell and longer platforms/formations', 'Independent full-tail detection/protection, route grades and operating acceptance']+
            ([] if meets_floor else ['Existing720-passenger/180s reference throughput floor is not met under exclusive whole-leg reservation']))
    fastest = max(passing, key=lambda row:row['conditional_capacity_aw2_pph']) if passing else None
    grade = power['minimum_service_grade_case_percent']/100
    grade_required = mass*9.81*grade+power['passive_rail_drag_study_n_per_car']
    if grade_required > force:
        recommendation['failed_gates'].append('Existing5% uphill grade case exceeds conditional thrust even at zero acceleration')
    least_car_options = [row for row in ranked if row['cars'] == least_formation]
    pareto_keys = ('station_sites_per_route_km', 'powered_direction_m_per_route_km',
        'platform_length_m_two_directions_per_route_km', 'installed_charger_input_kw_two_directions_per_route_km',
        'hotel_plus_80c_copper_kwh_per_aw2_capacity_passenger_km')
    pareto = []
    seen = set()
    for row in ranked:
        metrics = tuple(round(row[key], 8) for key in pareto_keys)
        if metrics in seen:
            continue
        seen.add(metrics)
        dominated = any(all(other[key] <= row[key]+1e-8 for key in pareto_keys) and
            any(other[key] < row[key]-1e-8 for key in pareto_keys) for other in ranked)
        if not dominated:
            pareto.append(row)
    selected_acceleration = winner['acceleration_m_s2'] if winner else 0.
    selected_speed = winner['max_speed_m_s'] if winner else 0.
    selected_drag = power['passive_rail_drag_study_n_per_car'] + .5*power['air_density_study_kg_m3']*power['drag_area_study_m2_per_car']*selected_speed**2
    request = dict(comparison_mass_kg=mass, comparison_mass_override_used=comparison_mass_kg is not None,
        accelerations_m_s2=accelerations_m_s2)
    if sources(root, [str(SUPPORT)] if support_binding else []) != source_snapshot:
        raise ValueError('service calculation sources changed during execution; rerun required')
    return dict(schema='osr-conditional-service-envelope/1',
        parent_configuration_sha256=evidence['parent_configuration_sha256'],
        propulsion_hypothesis_sha256=evidence['hypothesis_sha256'], source_sha256=source_snapshot,
        comparison_mass_support_binding=support_binding,
        study_parameters=request, parameters_sha256=sha256(_canonical(request)).hexdigest(),
        assumptions=dict(baseline_cars=baseline_cars, formation_options=[6,8,10,12], aw3_mass_kg_per_car=mass,
            canonical_comparison_mass_kg_per_car=canonical_mass,
            comparison_mass_basis='Retained canonical ledger' if comparison_mass_kg is None else 'Explicit caller-supplied mass sensitivity; not a reconciled installed candidate',
            comparison_mass_reconciled_with_revised_magnetic_candidate=False,
            baseline_aw2_passengers_per_train=baseline_cars*vehicle['aw2_passengers_per_car'],
            baseline_aw3_passengers_per_train=baseline_cars*vehicle['aw3_passengers_per_car'],
            baseline_train_length_m=baseline_cars*a['vehicle']['body_length_m']+(baseline_cars-1)*a['vehicle']['coupling_gap_m'], force_coupon_n_per_car=force,
            current_interior_a=1349., magnetic_map_calibrated_temperature_c=40., force_coupon_speed_m_s=20.,
            existing_normal_reference_headway_s=vehicle['scheduled_headway_seconds'],
            reference_aw2_throughput_floor_pph=target, speed_caps_m_s=[8,10,12,15,20],
            spacings_m=[750,1000,1500,2000,3000,5000], accelerations_m_s2=accelerations_m_s2,
            deceleration_m_s2=.2, dwells_s=[30,45,60], chargers_kw_per_car=[240,400,600],
            runtime_grid_s=list(range(60,601,10)), maximum_powered_fraction_comparison=.5,
            support_or_new_installed_mass_adopted=False,
            topology='One combined launch/receiving zone per station/direction, no midpoint boosters in selected station-only comparisons; no mainline switching',
            protection='Exclusive whole-leg+receiving berth reserved until the complete counted formation tail clears winding end plus75m, then5s allowance. Position time is a lower bound, never detector proof.',
            formations=f'Repeated{mass/1000:.6f}t AW3 car sensitivity only. Longer platform/zone/occupancy counted; no8/10/12car structural/dynamics/vehicle acceptance or whole-train harmonic sharing inherited.',
            suspension_carrier_cooling_and_interface_mass_closed=False,
            progressive_release='Possible separate research only after independent braking/integrity/detectors and distributed protection qualification; no pipeline capacity credit here.',
            force_scope='Conditional40C fixed-field1349A force is extended below20m/s with unchanged field/current. This speed/position/shared-group domain has not been validated.',
            thermal_scope='Finite5m groups with sampled ideal uniform currents. Copper-only R(T) no-cooling fixture and necessary mean heat-rejection target; no actual thermal equilibrium or cooling hardware mass/cost.',
            cost_scope='Stator-only unquoted1250USD/direction-m sensitivity; not station/route CAPEX. Copper mass counted from retained5m winding; cooling/converters/rails/civil/access/fleet not priced.'),
        coverage=dict(runtime_attempts=runtime_attempts, motion_profiles=len(motion_profiles),
            no_station_only_profile=len(search_holds), service_variants=len(rows),
            longitudinal_and_services_screen_passes=len(passing), reference_throughput_floor_passes=len(meets_floor),
            accepted_or_system_eligible=0),
        motion_profiles=motion_profiles, motion_search_holds=search_holds, service_variants=rows,
        grade_necessary_force_screen=dict(existing_minimum_grade_case_fraction=grade,
            zero_speed_uphill_force_required_n_per_car=grade_required,
            conditional_force_available_n_per_car=force, existing_grade_case_force_screen_pass=grade_required <= force,
            maximum_zero_acceleration_grade_fraction_at_zero_speed=(force-power['passive_rail_drag_study_n_per_car'])/(mass*9.81),
            selected_research_acceleration_m_s2=selected_acceleration, selected_research_speed_cap_m_s=selected_speed,
            existing_grade_case_force_required_n_per_car_at_selected_acceleration_and_speed_cap=mass*(selected_acceleration+9.81*grade)+selected_drag,
            maximum_grade_fraction_at_selected_acceleration_and_speed_cap=(force-mass*selected_acceleration-selected_drag)/(mass*9.81),
            lower_grade_would_change_product_or_site_envelope=True,
            scope='Existing grade sensitivity remains unchanged. Necessary force arithmetic only; actual graded trajectories remain unexecuted. A lower grade would be an explicit product/site constraint, not acceptance of the retained5% case.'),
        ranking=dict(hierarchy=['Meet existing normal720pax/180s throughput floor',
            'Compare all repeated-car formations reaching floor; retain least-formation alternative separately',
            'If none meet floor, retain failure and compare baseline formation within90% of its best capacity',
            'Fewest station sites per route-km', 'Least installed platform length per route-km',
            'Least hotel+80C copper energy per AW2 capacity-passenger-km',
            'Least powered length per route-km', 'Least installed charging input per route-km', 'Fewest cars',
            'Lowest required speed cap', 'Highest conditional capacity'],
            fallback_capacity_retention_fraction=.9,
            least_formation_meeting_reference_floor=least_formation if meets_floor else None,
            maximum_conditional_capacity_aw2_pph=best_capacity,
            fastest_conditional_case_id=fastest['id'] if fastest else None,
            least_formation_alternative_id=least_car_options[0]['id'] if least_car_options else None,
            pareto_metric_keys=list(pareto_keys), pareto_research_case_ids=[row['id'] for row in pareto],
            selection_is_total_cost_optimum=False,
            ranked_finalist_ids=[row['id'] for row in ranked], cooling_and_protection_are_unclosed=True),
        recommended_research_specification=recommendation, **FLAGS)


def read_retained(path, root=ROOT):
    """Check exact sources, request parameters and retained arithmetic, not rerun.

    A source/publication binding preserves the executed numerical work; these
    checks neither independently validate its model nor certify its outcomes.
    """
    path, root = Path(path), Path(root)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16*1024*1024:
        raise ValueError('bounded ordinary service report required')
    value = json.loads(path.read_bytes())
    if value.get('schema') != 'osr-conditional-service-envelope/1' or any(value.get(key) is not False for key in FLAGS):
        raise ValueError('unadopted conditional service report required')
    binding = value.get('comparison_mass_support_binding')
    if binding is not None:
        if binding.get('source_path') != str(SUPPORT) or binding.get('source_sha256') != sha256((root/SUPPORT).read_bytes()).hexdigest():
            raise ValueError('support material-mass source binding differs')
        contract = json.loads((root/SUPPORT).read_bytes())['recommended_next_design_contract']
        if (binding.get('contract_sha256') != sha256(_canonical(contract)).hexdigest() or
                binding.get('proposed_case_id') != contract['proposed_case_id'] or
                binding.get('controlled_aw3_material_lower_bound_kg_per_car') != contract['controlled_aw3_material_lower_bound_kg_per_car']):
            raise ValueError('support contract material mass differs')
    if value.get('source_sha256') != sources(root, [str(SUPPORT)] if binding else []):
        raise ValueError('complete current service source bindings required')
    request = value.get('study_parameters', {})
    if set(request) != {'comparison_mass_kg', 'comparison_mass_override_used', 'accelerations_m_s2'}:
        raise ValueError('complete service parameter binding required')
    if value.get('parameters_sha256') != sha256(_canonical(request)).hexdigest():
        raise ValueError('retained service request digest differs')
    assumptions = value['assumptions']
    if (request['comparison_mass_kg'] != assumptions['aw3_mass_kg_per_car'] or
            request['accelerations_m_s2'] != assumptions['accelerations_m_s2'] or
            type(request['comparison_mass_override_used']) is not bool):
        raise ValueError('service request and evaluated mass/acceleration differ')
    if binding and request['comparison_mass_kg'] != binding['controlled_aw3_material_lower_bound_kg_per_car']:
        raise ValueError('service comparison mass differs from support material lower bound')
    archive = json.loads((root/propulsion_research.ARCHIVE/'executed/results.json').read_bytes())
    if (value['parent_configuration_sha256'] != archive['parent_configuration_sha256'] or
            value['propulsion_hypothesis_sha256'] != archive['resolved_corner_alternative']['hypothesis_sha256']):
        raise ValueError('service parent/propulsion hypothesis differs')
    primary = tomllib.loads((root/'ferrite-maglev-study.toml').read_text())
    expected_floor = primary['vehicle']['aw2_passengers_per_car']*assumptions['baseline_cars']*3600/primary['vehicle']['scheduled_headway_seconds']
    if assumptions['reference_aw2_throughput_floor_pph'] != expected_floor:
        raise ValueError('retained normal-service capacity floor differs')
    profiles = {row['id']:row for row in value['motion_profiles']}
    rows = {row['id']:row for row in value['service_variants']}
    if len(profiles) != value['coverage']['motion_profiles'] or len(rows) != value['coverage']['service_variants'] or len(rows) != 9*len(profiles):
        raise ValueError('retained service case inventory differs')
    for row in rows.values():
        if any(row.get(key) is not False for key in FLAGS) or row['system_eligible'] is not False:
            raise ValueError('conditional service cases cannot confer adoption')
        profile = profiles[row['motion_profile_id']]
        if row['cars'] not in (6,8,10,12) or row['cars'] != profile['cars']:
            raise ValueError('retained service formation differs')
        length = row['cars']*17+(row['cars']-1)*.5
        if (row['train_length_m'] != length or row['aw3_train_mass_kg'] != row['cars']*request['comparison_mass_kg'] or
                profile['full_tail_clear_front_m'] != length+profile['full_engagement_zone']['end_m']+75):
            raise ValueError('retained mass/formation/full-tail dimensions differ')
        headway = row['runtime_s']+row['dwell_s']+profile['full_tail_clear_after_departure_s']+5
        capacity = row['cars']*primary['vehicle']['aw2_passengers_per_car']*3600/headway
        if (row['headway_lower_bound_s'] != headway or row['conditional_capacity_aw2_pph'] != capacity or
                row['reference_throughput_floor_pass'] != (capacity >= expected_floor)):
            raise ValueError('retained capacity/full-tail arithmetic differs')
    winner = value['recommended_research_specification']
    if 'id' in winner:
        if winner['id'] not in rows or any(winner.get(key) != item for key,item in rows[winner['id']].items()):
            raise ValueError('retained service recommendation differs from executed row')
        if not winner['failed_gates'] or winner.get('research_target_only') is not True:
            raise ValueError('failed engineering gates must remain visible')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--comparison-mass-kg', type=float)
    parser.add_argument('--accelerations-m-s2', type=float, nargs='+', default=[.15,.2])
    args = parser.parse_args()
    value = study(comparison_mass_kg=args.comparison_mass_kg, accelerations_m_s2=args.accelerations_m_s2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps(dict(output=str(args.output), coverage=value['coverage'],
        recommended_research_specification=value['recommended_research_specification']), sort_keys=True))


if __name__ == '__main__':
    main()
