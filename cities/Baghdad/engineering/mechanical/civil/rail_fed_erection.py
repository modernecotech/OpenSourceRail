"""Compare road-crane and two-end rail-fed girder erection on matched viaduct stock."""

import argparse
from decimal import Decimal
from hashlib import sha256
import json
from math import ceil, isfinite
from pathlib import Path
import tomllib

from cities.Baghdad.engineering.mechanical.civil import family_comparison as family
from cities.Baghdad.engineering.simulation import vehicle_audit

HERE = Path(__file__).resolve().parent
ASSUMPTIONS = HERE / "rail_fed_assumptions.toml"
SHIFT_H = 8
SPAN_M = 20
GIRDERS_PER_BAY = 2
METHODS = {
    "road_day": ("road", 8),
    "road_extended": ("road", 16),
    "rail_extended": ("rail", 16),
    "rail_24h": ("rail", 24),
}


def load_assumptions():
    with ASSUMPTIONS.open("rb") as source:
        return tomllib.load(source)


def split_fronts(count):
    return (count // 2, count - count // 2)


def exposure_schedule(count, protected):
    """Spread fallback bays over the interior approaches without duplicating end lifts."""
    if not 0 <= protected <= count:
        raise ValueError("Fallback count must fit available bays")
    return {(index * count + count // 2) // protected for index in range(protected)}


def feed_hours(distance_km, assumptions):
    """One bidirectional flatbed's loaded and empty legs and yard/gantry handoffs."""
    return (distance_km / assumptions["flatbed_loaded_speed_kmh"]
            + distance_km / assumptions["flatbed_empty_speed_kmh"]
            + assumptions["flatbed_terminal_load_unload_h_per_trip"])


def simulate_front(count, *, start, end_road_lifts, family_rate, delivery, kind, hours_per_day, protected):
    availability = delivery[f"{'road' if kind == 'road' else 'launcher'}_front_availability"]
    released = min(count, delivery["initial_released_bays_each_end"])
    shifts_per_day = hours_per_day / SHIFT_H
    max_casts = min(delivery["cast_pieces_per_yard_day"],
                    delivery["moulds_per_yard"] * 24 / delivery["mould_cycle_h"])
    initial_stock = delivery["initial_stock_per_yard"]
    cast_period_h = 24 / max_casts
    ready_h = start*24
    stopwatch = ready_h
    road_hours = 0.
    rail_hours = 0.
    track_release_hours = 0.
    flatbed_hours = 0.
    cast_wait_h = 0.
    pier_wait_h = 0.
    critical_shuttle_h = 0.
    by_road = 0
    for index in range(count):
        pieces = GIRDERS_PER_BAY * (index + 1)
        cast_available = ready_h + max(0, pieces - initial_stock) * cast_period_h
        pier_available = (ready_h + 24 * max(0, index + 1 - released)
                          / delivery["additional_pier_releases_per_end_per_day"])
        cast_wait_h += max(0., cast_available-stopwatch)
        stopwatch = max(stopwatch, cast_available)
        pier_wait_h += max(0., pier_available-stopwatch)
        stopwatch = max(stopwatch, pier_available)
        street = kind == "road" or index < end_road_lifts or index in protected
        if street:
            active = SHIFT_H * GIRDERS_PER_BAY / family_rate
            road_hours += active
            by_road += 1
        else:
            distance = delivery["yard_to_deck_rail_km_each"] + index*SPAN_M/1000
            shuttle = GIRDERS_PER_BAY * feed_hours(distance, delivery)
            site = (delivery["launcher_hours_per_standard_bay"]
                    + delivery["track_extension_and_ground_check_h_per_bay"])
            # One shuttle and one restricted feed path/front. A serial cycle
            # leaves clearance for track extension, placement and the empty return.
            active = shuttle + site
            flatbed_hours += shuttle
            critical_shuttle_h = max(critical_shuttle_h, shuttle)
            rail_hours += active
        # Each cross-road fallback or starter bay is closed and released
        # before feed continues. Assume only the road day window for those lifts.
        window = 8 if street and kind == "rail" else hours_per_day
        availability_used = delivery["road_front_availability"] if street else availability
        stopwatch += active * 24/(window*availability_used)
        if kind == "rail":
            # Construction-stage release only. This stationary wait earns no
            # throughput and is distinct from the priced stressing work.
            track_release = delivery["after_landing_deck_release_h"]
            stopwatch += track_release
            track_release_hours += track_release
    return dict(
        standard_bays=count,
        road_bays=by_road,
        rail_bays=count-by_road,
        calendar_days=stopwatch/24,
        road_productive_hours=road_hours,
        rail_productive_hours=rail_hours,
        flatbed_hours=flatbed_hours,
        track_release_hours=track_release_hours,
        maximum_shuttle_hours_per_bay=critical_shuttle_h,
        pier_wait_days=pier_wait_h/24,
        casting_wait_days=cast_wait_h/24,
        nominal_cast_pieces_per_yard_day=max_casts,
        scheduled_shifts_per_day=shifts_per_day,
    )


def crews(params, rail, rail_days, booked_shifts, hours_per_day, trips):
    """Separate crane/driver crew allowances from the new gantry payroll."""
    d = params["delivery"]
    rate_cases = params["prices"]["effective_paid_labor_usd_hour"]
    shifts = ((360, "06:00–14:00"), (840, "14:00–22:00"), (1320, "22:00–06:00"))
    rows = []
    road_shifts_per_day = 1 if rail else hours_per_day // SHIFT_H
    for i, (start, label) in enumerate(shifts[:road_shifts_per_day]):
        booked, extra = divmod(booked_shifts, road_shifts_per_day)
        booked += int(i < extra)
        for name, count in params["road_crew"].items():
            if name.startswith("Haul driver"):
                loads, extra = divmod(trips, road_shifts_per_day)
                paid_hours = count*(loads + int(i < extra))*4
            else:
                paid_hours = count*booked*SHIFT_H
            rows.append(dict(phase="road erection and public haul", role=name, posts_per_front=count,
                             shift=label, start_minute=start, staffed_front_shifts=booked,
                             paid_hours=paid_hours, cost_usd=dict.fromkeys(family.CASES),
                             price_basis="Embedded in road haul and operated crane rates"))
    if not rail:
        return rows
    for i, (start, label) in enumerate(shifts[:hours_per_day // SHIFT_H]):
        for name, count in params["rail_crew"].items():
            paid_hours = rail_days*SHIFT_H*count
            premium = d["rail_shift_pay_factors"][i]
            rows.append(dict(phase="rail-fed erection", role=name, posts_per_front=count,
                             shift=label, start_minute=start, staffed_front_shifts=rail_days,
                             paid_hours=paid_hours, price_basis="Modeled paid shift included in launcher payroll",
                             cost_usd={case: paid_hours*premium*rate for case, rate in zip(family.CASES, rate_cases, strict=True)}))
    return rows


def compare_method(kind, hours, *, bays, residual_m, stock, params, exclusion_pct):
    d, prices = params["delivery"], params["prices"]
    rail = kind == "rail"
    meet = d["meeting_bays"] if rail else 0
    starters = d["starter_bays_each_end"] if rail else 0
    if bays < meet + 2*starters + 2:
        raise ValueError("Route must admit starter, meeting and advancing bays")
    if rail and any(n <= starters for n in split_fronts(bays-meet)):
        raise ValueError("Each end needs an advancing front beyond the starter bays")
    placement_rate = stock["standard_only_cost_cases"]["base"]["placements_per_shift"]
    if placement_rate is None:
        raise ValueError("The matched street comparator requires a priced road-crane case")
    cast_pieces_day = min(d["cast_pieces_per_yard_day"], d["moulds_per_yard"] * 24 / d["mould_cycle_h"])
    cast_start_days = d["mould_cycle_h"]/24 + d["initial_stock_per_yard"]/cast_pieces_day
    start_days = max(d["pier_release_first_day"], cast_start_days,
                     d["launch_prelim_days"] if rail else d["mobile_prelim_days"])
    fronts = []
    for count in split_fronts(bays-meet):
        n_excluded = ceil((count-starters)*exclusion_pct/100) if rail else 0
        reserved = {starters+i for i in exposure_schedule(count-starters, n_excluded)}
        fronts.append(simulate_front(count, start=start_days, end_road_lifts=starters,
                                     family_rate=placement_rate, delivery=d, kind=kind, hours_per_day=hours,
                                     protected=reserved))
    regular_road_bays = sum(front["road_bays"] for front in fronts)
    launched_bays = sum(front["rail_bays"] for front in fronts)
    if regular_road_bays + launched_bays + meet != bays:
        raise AssertionError("Construction methods must erect identical standard bays")
    last_bays = meet + int(residual_m > 0)
    road_bays = regular_road_bays + last_bays
    road_trips = road_bays*GIRDERS_PER_BAY
    booked_shifts = sum(ceil(f["road_productive_hours"]/SHIFT_H) for f in fronts) + ceil(last_bays*GIRDERS_PER_BAY/placement_rate)
    # Lease and the full staffed roster are charged over each front's booked
    # calendar, including wait for casting and deck release.
    if rail and not launched_bays:
        raise ValueError("No standard bays left for rail feed under this overhead exclusion scenario")
    launcher_days_by_front = sum(ceil(f["calendar_days"] - start_days) for f in fronts) if rail else 0
    crew_rows = crews(params, rail, launcher_days_by_front, booked_shifts, hours, road_trips)
    crew_rows = [row for row in crew_rows if row["paid_hours"]]
    costs = {}
    route_km_with_temporary_rail = bays*SPAN_M/1000 + 2*d["yard_to_deck_rail_km_each"]
    for i, case in enumerate(family.CASES):
        parent = stock["standard_only_cost_cases"][case]["installed_breakdown_usd"]
        removed = {"haul", "erection", "road_occupation", "forms"}
        common = {k: v for k, v in parent.items() if k not in removed}
        common["two_yard_forms"] = parent["forms"]*2*d["moulds_per_yard"]/stock["mould_positions"]
        inherited = {k: parent[k]*road_trips/(bays*GIRDERS_PER_BAY) for k in ("haul", "erection")}
        inherited["road_occupation"] = booked_shifts*family.TRIALS["closure_usd_shift"][i]
        extras = {}
        if rail:
            extras = dict(
                launcher_mobilisation=2*prices["launcher_mobilisation_usd_each"][i],
                launcher_dry_use=launcher_days_by_front*prices["launcher_dry_use_usd_day_each"][i],
                flatbed_mobilisation=2*prices["flatbed_mobilisation_usd_each"][i],
                flatbed_dry_use=launcher_days_by_front*prices["flatbed_dry_use_usd_day_each"][i],
                temporary_track=route_km_with_temporary_rail*prices["temporary_track_installed_and_recovered_usd_km"][i],
                terminal_transfer=2*prices["terminal_transfer_and_enabling_usd_each"][i],
                supplies=launched_bays*GIRDERS_PER_BAY*prices["power_consumables_usd_per_launched_girder"][i],
                launcher_payroll=sum(r["cost_usd"][case] or 0 for r in crew_rows),
                staged_engineering=prices["construction_stage_engineering_usd_per_line"][i],
                meeting_interfaces=prices["meeting_interfaces_usd"][i],
                terminal_street_access=d["terminal_access_lane_hours"]/(SHIFT_H*d["road_lanes_occupied"])
                                       *family.TRIALS["closure_usd_shift"][i],
            )
        # A residual bay retains the same provisional conservative heavy-lift
        # allowance under both methods. Actual fabricated stock/geometry absent.
        if residual_m:
            extras["residual_interface_allowance"] = prices["residual_interfaces_usd"][i]
        method_cost = sum(inherited.values())+sum(extras.values())
        costs[case] = dict(method_scope_usd=method_cost, common_scope_usd=sum(common.values()),
                           installed_standard_stock_usd=method_cost+sum(common.values()),
                           road_allowance_usd=inherited, temporary_and_other_costs_usd=extras,
                           common_scope_breakdown_usd=common)
    completion = max(f["calendar_days"] for f in fronts)+d["meeting_days"]*bool(meet)+d["residual_days"]*bool(residual_m)
    return dict(
        calendar_days=completion, erection_elapsed_days=completion-start_days,
        setup_and_initial_release_days=start_days, staffed_hours_per_front_day=hours,
        launcher_dry_hire_days_across_fronts=launcher_days_by_front, fronts=fronts, launched_bays=launched_bays,
        starter_bays=2*starters, meeting_bays=meet, overhead_fallback_bays=regular_road_bays-2*starters if rail else 0,
        residual_bay_m=residual_m, routine_public_road_beam_trips=road_trips,
        public_road_beam_trips=road_trips,
        road_lane_hours=booked_shifts*SHIFT_H*d["road_lanes_occupied"]+(d["terminal_access_lane_hours"] if rail else 0),
        road_plant_shift_bookings=booked_shifts,
        temporary_track_km=route_km_with_temporary_rail if rail else 0,
        labour_hours=sum(row["paid_hours"] for row in crew_rows),
        crew_shifts=crew_rows, cases=costs,
    )


def evaluate(route_km=12.0, overhead_exclusion_pct=None):
    params = load_assumptions()
    d = params["delivery"]
    exclusion = d["overhead_exclusion_pct"] if overhead_exclusion_pct is None else overhead_exclusion_pct
    if not isfinite(route_km) or not 0.2 <= route_km <= 300:
        raise ValueError("Evaluate a corridor from 0.2 to 300 km")
    if not isfinite(exclusion) or not 0 <= exclusion <= 100:
        raise ValueError("Overhead closure share must be between zero and 100 percent")
    positive = ("additional_pier_releases_per_end_per_day", "moulds_per_yard", "mould_cycle_h",
                "cast_pieces_per_yard_day", "flatbed_loaded_speed_kmh", "flatbed_empty_speed_kmh",
                "flatbed_axles", "road_lanes_occupied")
    if any(not isfinite(d[key]) or d[key] <= 0 for key in positive):
        raise ValueError("Positive finite release and plant capacities are required")
    if any(not 0 < d[key] <= 1 for key in ("road_front_availability", "launcher_front_availability")):
        raise ValueError("Front availability must be in (0, 1]")
    if not 0 <= d["initial_stock_per_yard"] <= d["stock_slots_per_yard"]:
        raise ValueError("Initial released buffer must fit each yard")
    route_m = Decimal(str(route_km))*1000
    bays = int(route_m//SPAN_M)
    residual = float(route_m % SPAN_M)
    vehicle = vehicle_audit.evaluate(cars=6, material="steel")
    civil = family.evaluate_high_load(route_km=route_km, selected_family="U", selected_span_m=SPAN_M,
                                     installed_vehicle=vehicle)
    stock = next(row for row in civil["rows"] if row["span_m"] == SPAN_M
                 and row["shared_pier"] and row["section"]["shape"] == "U"
                 and row["section"]["depth_m"] == 1.55)
    if stock["full_standard_bays"] != bays:
        raise ValueError("Source civil row and construction order quantities differ")
    methods = {key: compare_method(kind, hours, bays=bays, residual_m=residual, stock=stock, params=params,
                                    exclusion_pct=exclusion) for key, (kind, hours) in METHODS.items()}
    break_even = {}
    for reference in ("road_day", "road_extended"):
        break_even[reference] = {}
        for key in ("rail_extended", "rail_24h"):
            road, rail = methods[reference], methods[key]
            break_even[reference][key] = {
                case: {
                    "saving_usd": road["cases"][case]["method_scope_usd"] - rail["cases"][case]["method_scope_usd"],
                    "maximum_combined_launcher_mobilisation_usd":
                        road["cases"][case]["method_scope_usd"] - rail["cases"][case]["method_scope_usd"]
                        + rail["cases"][case]["temporary_and_other_costs_usd"]["launcher_mobilisation"],
                } for case in family.CASES
            }
    prototype_members = {name.removeprefix("prototype:"): digest
                         for name, digest in vehicle["source_sha256"].items() if name.startswith("prototype:")}
    package_sources = {name: digest
                       for name, digest in vehicle["source_sha256"].items() if not name.startswith("prototype:")}
    package_sources.update(civil["member_sources"])
    for path in (ASSUMPTIONS, Path(__file__), Path(vehicle_audit.__file__)):
        package_sources[path.relative_to(family.ROOT).as_posix()] = sha256(path.read_bytes()).hexdigest()
    a = stock["actions"]
    high_axle_t = max(civil["load_cases"]["high"]["axle_kg_per_car"])/1000
    mean_flatbed_axle_t = (a["mass_t"]+d["flatbed_tare_t"])/d["flatbed_axles"]
    report = dict(
        schema="osr-rail-fed-erection-study/1",
        scope=dict(route_km=route_km, route_kind="illustrative straight double-track corridor",
                   overhead_exclusion_pct=exclusion, rolling_stock="Baghdad six-car steel high-load civil envelope",
                   permanent_cost_scope="Standard-stock package plus temporary erection method. Actual nonstandard stock and site costs open.",
                   calendar_scope="Initial release and superstructure erection windows. Operating opening date is outside this study.",
                   rate_basis="Published road haul, crane-class, stock and road-occupation allowances plus explicit rail-fed planning estimates in constant USD.",
                   physical_acceptance=False),
        geometry=dict(span_m=SPAN_M, standard_bays=bays, standard_girders=2*bays,
                      standard_shared_support_positions=bays+1, residual_m=residual,
                      single_girder_bare_mass_t=a["mass_t"], source_hook_demand_t=a["chart_demand_t"],
                      girder_width_m=stock["section"]["width_m"], girder_depth_m=stock["section"]["depth_m"],
                      track_pitch_m=civil["trials"]["track_pitch_m"],
                      flatbed_gross_loaded_t=a["mass_t"]+d["flatbed_tare_t"],
                      flatbed_mean_loaded_axle_t=mean_flatbed_axle_t,
                      high_operating_max_axle_t=high_axle_t,
                      flatbed_mean_exceeds_high_operating_max_axle=mean_flatbed_axle_t > high_axle_t,
                      minimum_axles_to_match_operating_max_mean_only=ceil((a["mass_t"]+d["flatbed_tare_t"])/high_axle_t),
                      flatbed_axles=d["flatbed_axles"], civil_physical_id=stock["physical_id"],
                      civil_audit_row_id=stock["audit_row_id"], civil_evaluation_id=civil["evaluation_id"],
                      train_candidate_id=vehicle["candidate_id"], train_evaluation_id=vehicle["evaluation_id"]),
        shared_quantities=dict(yards=2, area_ha_each=d["yard_area_ha_each"], moulds_per_yard=d["moulds_per_yard"],
                               mould_cycle_h=d["mould_cycle_h"], released_stock_slots_per_yard=d["stock_slots_per_yard"]),
        engineering_screen=dict(rail_feed_deck_and_equipment="held pending construction-stage load and geometry review",
                                physically_eligible_methods=[], cost_scenarios_ranked=False),
        assumptions=params, methods=methods, break_even=break_even, source_sha256=package_sources,
        source_prototype_member_sha256=prototype_members,
        holds=[
            "Public road hours are booked lane-hours for girder erection and terminal access. They exclude road impacts of both methods' common foundations, piers, utilities, material deliveries and station works.",
            "The prescribed foundation release and casting rates are planning inputs. Check end land, supplier output, beam storage, crew competence and availability.",
            "Verify launcher reactions and cross-track transfer, one-girder/two-girder stages, lateral stability, midline discontinuity, curves, grade, camber and emergency recovery.",
            "Approve temporary rails, rear loading and terminal transload, transporter braking and axle group loads. Mean axle mass is a planning value. The deck must be checked for actual axle groups plus gantry reactions at construction stages, even if the mean falls within the operating envelope.",
            "The travelling girder is wider than the receiving U channel. Design an elevated cradle, prove clearance at curves and verify transfer across the two track centres.",
            "A starter or crossing fallback bay must reach the required construction strength and be inspected before the temporary feed track is extended. The after-landing hold is a planning allowance.",
            "Two identical yards are compared at 16 moulds and 24 released slots per yard. Release dates are earliest production dates under call-off. Confirm feasible casting batches, dispatch inventory and rejection reserve against the supplier schedule.",
            "Street control beneath overhead operations, nighttime restrictions, wind, lifting permissions and public safety need project-specific approval.",
        ])
    report["evaluation_id"] = family.digest(report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route-km", type=float, default=12.0)
    parser.add_argument("--overhead-exclusion-pct", type=float)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(evaluate(args.route_km, args.overhead_exclusion_pct), indent=2, allow_nan=False))
    except (ValueError, StopIteration) as error:
        parser.error(str(error) or "Matching high-load civil row unavailable")


if __name__ == "__main__":
    main()
