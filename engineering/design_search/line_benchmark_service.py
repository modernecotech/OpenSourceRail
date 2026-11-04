"""Conditional terminal-line service quantities for the cost benchmark.

This adapts the selected six-car accounting scenario, not installed-mass or
available-drive evidence. It does not change the selected reference vehicle.
"""
from copy import deepcopy
from math import ceil, fsum, isclose, isfinite, sqrt

from engineering.station_rail import braking, electrical, operations
from engineering.station_rail.common import identity
from .compact_launch import jerk_bound

PRODUCER = "engineering/design_search/line_benchmark_service.py"
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    installed_mass_complete=False, manufacturing_release=False,
    operating_release=False, physical_journey_completed=False,
    selected_reference_changed=False, movement_authority=False)


def _number(value, name, *, zero=False):
    if (type(value) not in (int, float) or not isfinite(value)
            or (value < 0 if zero else value <= 0)):
        raise ValueError("Finite " + ("nonnegative " if zero else "positive ") + name + " required")
    return float(value)


def _tail_clearance(distance, speed, acceleration, jerk):
    """Tail passage under the exact S-curve bound, then capped-speed travel."""
    bound = jerk_bound(speed, acceleration, jerk)
    ramp = bound["ramp_time_s"]
    plateau = bound["plateau_time_s"]
    peak = bound["peak_acceleration_m_s2"]
    x1 = jerk * ramp**3 / 6
    v1 = jerk * ramp**2 / 2
    x2 = x1 + v1 * plateau + peak * plateau**2 / 2
    v2 = v1 + peak * plateau
    def position(t):
        if t <= ramp:
            return jerk * t**3 / 6
        if t <= ramp + plateau:
            u = t - ramp
            return x1 + v1*u + peak*u*u/2
        u = t - ramp - plateau
        return x2 + v2*u + peak*u*u/2 - jerk*u**3/6
    if distance >= bound["distance_m"]:
        return bound["total_time_s"] + (distance-bound["distance_m"])/speed
    low, high = 0., bound["total_time_s"]
    for _ in range(60):
        mid = (low+high)/2
        if position(mid) < distance:
            low = mid
        else:
            high = mid
    return (low+high)/2


def _jerk_launch_work(profile, bound):
    """Exact polynomial integral of v^3 over the three zero-grade/wind phases."""
    def integral_cube(coefficients, duration):
        polynomial = [1.]
        for _ in range(3):
            product = [0.] * (len(polynomial)+len(coefficients)-1)
            for i,a in enumerate(polynomial):
                for k,b in enumerate(coefficients):
                    product[i+k] += a*b
            polynomial = product
        return fsum(coefficient*duration**(i+1)/(i+1) for i,coefficient in enumerate(polynomial))
    ramp = bound["ramp_time_s"]; plateau = bound["plateau_time_s"]
    peak = bound["peak_acceleration_m_s2"]; jerk = bound["jerk_m_s3"]
    v1 = jerk*ramp*ramp/2
    v2 = v1+peak*plateau
    integral = fsum((integral_cube([0.,0.,jerk/2],ramp),
        integral_cube([v1,peak],plateau),integral_cube([v2,peak,-jerk/2],ramp)))
    p = profile["inputs"]
    speed = p["speed_cap_m_s"]
    kinetic = p["effective_inertial_mass_kg_per_car"]*speed*speed/2
    rolling = profile["constant_wheel_drag_N_per_car"]*bound["distance_m"]
    aerodynamic = p["quadratic_drag_N_per_car_per_m_s_squared_hypothesis"]*integral
    return dict(kinetic_J_per_car=kinetic,rolling_bearing_J_per_car=rolling,
        aerodynamic_J_per_car=aerodynamic,velocity_cubed_integral_m3_s2=integral,
        total_J_per_car=fsum((kinetic,rolling,aerodynamic)),
        method="Exact polynomial convolution/integration of the three S-curve velocity phases; level track, zero wind",
        electrical_efficiency_and_actual_force_map_applied=False)


def evaluate(requirements, design, vehicle):
    """Return deterministic demand, fleet and energy quantities without costing."""
    r, d = deepcopy(requirements), deepcopy(design)
    for key in ("stations", "trackways", "cars_per_train", "fixed_seats_per_car", "wheelchair_places_per_car"):
        if type(r.get(key)) is not int:
            raise ValueError("Integer " + key + " required")
    if not 2 <= r["stations"] <= 100:
        raise ValueError("Two to 100 stations required for this bounded benchmark")
    if (r["trackways"], r["cars_per_train"], r["fixed_seats_per_car"], r["wheelchair_places_per_car"]) != (2, 6, 44, 2):
        raise ValueError("Benchmark requires the current double-track, six-car 44-seat/two-wheelchair reference")
    for key in ("route_km", "headway_s", "dwell_s", "operating_hours_per_day"):
        _number(r[key], key)
    if r["operating_hours_per_day"] > 24:
        raise ValueError("Operating hours cannot exceed 24 per day")
    for key in ("speed_m_s", "acceleration_m_s2", "service_deceleration_m_s2", "jerk_m_s3", "aux_kw_per_car", "charger_kw_per_car", "charge_efficiency"):
        _number(d[key], key)
    for key in ("terminal_turnback_s", "reserve_fraction", "added_vehicle_mass_kg_per_car"):
        _number(d[key], key, zero=True)
    margin = _number(d.get("schedule_running_time_margin_fraction",0.),
        "schedule_running_time_margin_fraction",zero=True)
    if d["reserve_fraction"] > 1 or d["charge_efficiency"] > 1:
        raise ValueError("Reserve fraction and charge efficiency cannot exceed one")
    if vehicle.get("evaluation_id") != identity({k:v for k,v in vehicle.items() if k != "evaluation_id"}):
        raise ValueError("Vehicle evaluation identity differs")
    definition = vehicle["physical_definition"]
    vc = definition["vehicle"]
    if (vc["cars"], vc["fixed_seats_per_car"], vc["wheelchair_places_per_car"]) != (6,44,2):
        raise ValueError("Vehicle and benchmark seating/formation differ")
    expected = identity(dict(physical_definition=definition,
        body_candidate_id=vehicle["body_candidate_id"],support_component_id=vehicle["support_component_id"],
        propulsion_component_id=vehicle["propulsion_component_id"]))
    if expected != vehicle["candidate_id"]:
        raise ValueError("Vehicle physical identity differs")
    base_mass = _number(vehicle["mass"]["accounted_cap_loaded_kg_per_car"], "accounted normal mass")
    mass = base_mass + d["added_vehicle_mass_kg_per_car"]
    rotor = braking.rotating_stock(vehicle)["equivalent_inertial_mass_kg_per_car"]
    length = 6*vc["body_length_m"] + 5*vc["coupling_gap_m"]
    offset = (vc["body_length_m"]-definition["propulsion"]["secondary_length_m"])/2
    segment = r["route_km"]*1000/(r["stations"]-1)
    args = dict(speed_cap_m_s=d["speed_m_s"],acceleration_m_s2=d["acceleration_m_s2"],
        service_deceleration_m_s2=d["service_deceleration_m_s2"],cars=6,
        rotating_equivalent_mass_kg_per_car=rotor,loading="provisional-accounted-plus-added-reserve")
    profile = operations.profile(segment,mass,**args)
    jerk = jerk_bound(d["speed_m_s"],d["acceleration_m_s2"],d["jerk_m_s3"])
    # The symmetric S-curve has x=V*T/2. An equivalent constant acceleration
    # therefore matches only its time/distance/end-speed before the unchanged
    # natural-coast and brake phases. Its force and energy are not adopted.
    timing_profile = operations.profile(segment,mass,**{**args,
        "acceleration_m_s2":d["speed_m_s"]/jerk["total_time_s"]})
    timing_valid = (timing_profile["reachable"]
        and isclose(timing_profile["launch_time_s"],jerk["total_time_s"],rel_tol=1e-12)
        and isclose(timing_profile["launch_distance_m"],jerk["distance_m"],rel_tol=1e-12)
        and isclose(timing_profile["peak_speed_m_s"],d["speed_m_s"],rel_tol=1e-12))
    raw_runtime = timing_profile["runtime_s"] if timing_valid else None
    scheduled_runtime = raw_runtime*(1+margin) if raw_runtime is not None else None
    work = _jerk_launch_work(profile,jerk)
    clear_jerk = _tail_clearance(length,d["speed_m_s"],d["acceleration_m_s2"],d["jerk_m_s3"])
    launch_distance = profile["launch_distance_m"]
    clear_constant = (sqrt(2*length/d["acceleration_m_s2"])
        if length <= d["speed_m_s"]**2/(2*d["acceleration_m_s2"])
        else d["speed_m_s"]/d["acceleration_m_s2"]+(length-d["speed_m_s"]**2/(2*d["acceleration_m_s2"]))/d["speed_m_s"])
    unpadded_one_way = ((r["stations"]-1)*raw_runtime+(r["stations"]-2)*r["dwell_s"]
        if raw_runtime is not None else None)
    unpadded_cycle = 2*(unpadded_one_way+d["terminal_turnback_s"]) if unpadded_one_way is not None else None
    unpadded_active = ceil(unpadded_cycle/r["headway_s"]) if unpadded_cycle is not None else None
    unpadded_spares = ceil(unpadded_active*d["reserve_fraction"]) if unpadded_active is not None else None
    one_way = ((r["stations"]-1)*scheduled_runtime+(r["stations"]-2)*r["dwell_s"]
        if scheduled_runtime is not None else None)
    cycle = 2*(one_way+d["terminal_turnback_s"]) if one_way is not None else None
    active = ceil(cycle/r["headway_s"]) if cycle is not None else None
    spare = ceil(active*d["reserve_fraction"]) if active is not None else None
    total = active+spare if active is not None else None
    positions = max(1,ceil(d["terminal_turnback_s"]/r["headway_s"]))
    places = 6*(44+2)
    berth = (timing_profile["braking_time_s"]+r["dwell_s"]+clear_jerk if timing_valid else None)
    auxiliary = None
    if timing_valid:
        moving = (r["stations"]-1)*scheduled_runtime
        charge_seconds = (r["stations"]-2)*r["dwell_s"]+d["terminal_turnback_s"]
        charge_reference = electrical.charge_leg(scheduled_runtime,dwell_s=r["dwell_s"],
            hotel_kW=d["aux_kw_per_car"],charging_power_kW=d["charger_kw_per_car"],efficiency=d["charge_efficiency"])
        allowed = charge_reference["catalogue_low_voltage_current_capped_charge_kW_per_car"]
        gross_input = allowed*charge_seconds/3600
        demand = d["aux_kw_per_car"]*(moving+charge_seconds)/3600
        margin = gross_input*d["charge_efficiency"]-demand
        net = allowed*d["charge_efficiency"]-d["aux_kw_per_car"]
        min_terminal = (max(0.,d["aux_kw_per_car"]*moving/net-(r["stations"]-2)*r["dwell_s"])
            if net > 0 else None)
        auxiliary = dict(aux_kw_per_car=d["aux_kw_per_car"],requested_charger_kw_per_car=d["charger_kw_per_car"],
            catalogue_capped_charger_kw_per_car=allowed,charge_efficiency=d["charge_efficiency"],
            moving_s_per_half_cycle=moving,charging_s_per_half_cycle=charge_seconds,
            charge_input_kwh_per_car_per_half_cycle=gross_input,
            hotel_energy_kwh_per_car_per_half_cycle=demand,
            energy_margin_kwh_per_car_per_half_cycle=margin,
            minimum_terminal_charge_s=min_terminal,per_leg=charge_reference,
            energy_balance_screen="pass" if margin>=-1e-10 else "fail",
            actual_charge_map_available=False,transient_SOC_verified=False,thermal_qualified=False)
    hours = r["operating_hours_per_day"]
    operation_shifts = 2 if hours <= 18 else 3
    grade_cases = [operations.profile(segment,mass,grade_fraction=grade,**args) for grade in (.01,.02)]
    value = dict(schema="osr-line-benchmark-service/1",requirements=r,design=d,
        reference_vehicle_candidate_id=vehicle["candidate_id"],reference_vehicle_evaluation_id=vehicle["evaluation_id"],
        accounted_reference_mass_kg_per_car=base_mass,added_vehicle_mass_reserve_kg_per_car=d["added_vehicle_mass_kg_per_car"],
        provisional_normal_mass_kg_per_car=mass,rotating_equivalent_mass_kg_per_car=rotor,
        mass_scope="Retained accounted mass plus declared added reserve; not complete installed mass or a certified lower bound. No reference hardware is silently removed.",
        segment_distance_m=segment,grade_fraction_hypothesis=0.,headwind_m_s_hypothesis=0.,
        profile=profile,jerk_bound=jerk,jerk_timing_profile=timing_profile,jerk_timing_model_valid=timing_valid,
        jerk_timing_profile_role="Equivalent acceleration matches S-curve time, stroke and end velocity for coast/brake timing only; its force/power/work are not used for equipment rating",
        unpadded_segment_runtime_s=raw_runtime,scheduled_segment_runtime_s=scheduled_runtime,
        schedule_running_time_margin_fraction=margin,
        schedule_margin_scope="Explicit planning recovery allowance on moving time only, not simulated slower motion or extra dwell/turnback",
        minimum_unpadded_one_way_s=unpadded_one_way,minimum_unpadded_round_trip_s=unpadded_cycle,
        minimum_unpadded_active_trainsets=unpadded_active,minimum_unpadded_spare_trainsets=unpadded_spares,
        minimum_unpadded_total_trainsets=unpadded_active+unpadded_spares if unpadded_active is not None else None,
        one_way_s=one_way,round_trip_s=cycle,
        active_trainsets=active,spare_trainsets=spare,total_trainsets=total,totalcars=total*6 if total else None,
        normal_places_per_train=places,capacity_pphpd=places*3600/r["headway_s"],
        fixed_seats_pphpd=264*3600/r["headway_s"],wheelchair_places_pphpd=12*3600/r["headway_s"],
        train_km_per_day=2*3600/r["headway_s"]*hours*r["route_km"],
        departure_sites=2*(r["stations"]-1),boarding_edges=2*r["stations"],
        minimum_turnback_positions_per_end=positions,terminal_additional_positions=2*(positions-1),
        terminal_position_cost_basis="Additional positions beyond one basic turnaround position per terminus; do not double-count if station costs already include them.",
        peak_train_force_N=profile["peak_launch_force_N_per_car"]*6 if profile["reachable"] else None,
        peak_train_mechanical_power_W=profile["peak_launch_power_W_per_car"]*6 if profile["reachable"] else None,
        mechanical_work_kwh_per_departure=work["total_J_per_car"]*6/3.6e6,
        constant_acceleration_mechanical_work_kwh_per_departure=profile.get("launch_mechanical_energy_kWh_train"),
        jerk_launch_work=work,
        jerk_launch_distance_m=jerk["distance_m"],train_length_m=length,
        full_train_fin_launch_envelope_m=launch_distance+length-2*offset if launch_distance is not None else None,
        jerk_full_train_fin_launch_envelope_m=jerk["distance_m"]+length-2*offset,
        tail_clearance_s_constant_acceleration=clear_constant,tail_clearance_s_jerk_bound=clear_jerk,
        berth_resource_s=berth,berth_headway_necessary_screen="pass" if berth is not None and berth<=r["headway_s"] else "fail",
        auxiliary=auxiliary,grade_sensitivities=grade_cases,
        shift_info=dict(production_shifts_per_day=2,construction_shifts_per_day=2,production_hours_per_shift=8,
            construction_hours_per_shift=8,operating_hours_per_day=hours,operations_shifts_per_day=operation_shifts,
            operations_hours_per_shift=hours/operation_shifts,extended_operations_scenario=dict(hours_per_day=24,shifts=3,hours_per_shift=8)),
        terminal_turnback_definition="Per-end arrival-at-rest to next departure, including terminal dwell; no second terminal dwell or extra tail-clearance trip time added.",
        journey_scope="Symmetric S-curve launch state followed by analytical natural coasting and constant-net-deceleration receiving brake; braking jerk is not modeled. Equipment rating uses requested peak-acceleration envelope. No available drive, braking or dynamic model is demonstrated.",
        braking_jerk_applied=False,
        interface_holds=["One-sided doors require compatible platform and terminal orientation/layout", "Protected turnback, shared approach/departure resources and recovery remain unqualified"],
        supported_journey_state="not-run",actual_available_force_map=None,
        execution="completed-analytic-research",numerical_validity="conditional-kinematic-targets",**FLAGS)
    value["evaluation_id"] = identity(value)
    return value
