"""Trace a corrected horizontal Airport study through service, vehicle, power and procurement."""
import argparse
import json
import inspect
import math
from pathlib import Path

from cities.Baghdad.engineering.mechanical.civil import family_comparison
from cities.Baghdad.engineering.simulation import (
    airport_alignment, airport_demand, audit_power_return, motion_power, passengers, scenario, vehicle_audit,
)
from engineering.design_search import requirement_policy
from engineering.performance import disk_reservation

HERE = scenario.HERE
REPORT = HERE / "AUDIT-RESULTS.md"
LAYOUTS = ("radial30", "paired6")


def service_inputs(route, vehicle, headway, ambient, observed, demand_mode):
    """Account for an assisted transfer at the demand used to book the working day."""
    cars = vehicle["physical"]["formation_cars"]
    dwell = route["dwell_s"]
    # Increase the booked dwell if necessary. A smaller updated dwell requirement
    # leaves the allowance in the timetable. Two unsuccessful revisions trigger review.
    for _ in range(3):
        demand = airport_demand.evaluate(route, headway_min=headway, dwell_s=dwell,
                                         observed=observed, mode=demand_mode, formation_cars=cars)
        climate = passengers.evaluate(dict(cars=cars, headway_min=headway, ambient_c=ambient,
                    busiest_departure_load=min(700 * cars // 6, math.ceil(demand["busiest_departure_load"])),
                    platform_queue=math.ceil(demand["platform_queue"])))
        required = math.ceil(climate["door_exchange"]["total_dwell_with_one_assisted_transfer_s"])
        if dwell >= required:
            return demand, climate
        dwell = required
    raise ValueError("Assisted dwell and the demand response require a revised timetable")


def phase_options(route, vehicle, headway, dwell):
    """Find a low-conflict terminal offset before running an expensive moving day."""
    references = motion_power.reference()
    inputs = dict(chainages_m=[km * 1000 for km in route["chainages_km"]], headway_min=headway,
                  dwell_s=dwell, length_m=vehicle["physical"]["length_m"])
    options = []
    for phase in [None, *range(0, headway * 60, 30)]:
        try:
            group, _, _, _, positioning, terminal = motion_power.service(dict(inputs, phase_s=phase), references)
        except ValueError as error:
            options.append(dict(requested_phase_s=phase, error=str(error)))
            continue
        options.append(dict(requested_phase_s=phase, phase_s=group["terminal_B_phase_s"],
                            conflicts=len(terminal["conflicts"]), operating_sets=group["diagrammed_sets"],
                            positioning=len(positioning)))
    feasible = [v for v in options if "conflicts" in v]
    if not feasible:
        raise ValueError("No terminal phase admits a booked timetable at this headway")
    best = min(feasible, key=lambda r:(r["conflicts"], r["operating_sets"], r["positioning"]))
    return dict(as_booked=options[0], best=best, evaluated=len(options), spacing_s=30)


def positioning_trial(route, vehicle, interval, dwell, phase, slack):
    """Give empty trains additional turning time and test the resulting resource reservations."""
    cfg = dict(chainages_m=[km * 1000 for km in route["chainages_km"]], headway_min=interval,
               dwell_s=dwell, length_m=vehicle["physical"]["length_m"], phase_s=phase)
    ref = motion_power.reference()
    *_, original = motion_power.service(cfg, ref)
    overlap = max((-r["margin_s"] for r in original["conflicts"] if r["resource"].startswith("block-")), default=0)
    if slack is None:
        slack = 30 * math.ceil(overlap / 30)
    group, _, _, _, positions, updated = motion_power.service(dict(cfg, positioning_slack_s=slack), ref)
    return dict(phase_s=phase, positioning_slack_s=slack, conflicts=len(updated["conflicts"]),
                initial_block_overlap_s=overlap, operating_sets=group["diagrammed_sets"], positioning=len(positions))


def working_day(route, demand, vehicle, climate, layout, condition, grade_pct, cache, sources, phase=None, slack=0, step=2, mass_state="central", constant_grade=False):
    airport_demand.validate(demand, route)
    physical = vehicle["physical"]
    if route["parent_candidate_id"] != physical["parent_candidate_id"]:
        raise ValueError("Vehicle and route came from different opening issues")
    mass = vehicle["mass_cases"][mass_state]
    inputs = dict(candidate_id=vehicle["candidate_id"], cars=physical["formation_cars"],
                  material=physical["material"], headway_min=demand["headway_min"],
                  chainages_km=route["chainages_km"], alignment=route, demand_record=demand,
                  dwell_s=demand["dwell_s"], grade_pct=float(grade_pct), auxiliary_kw=climate["auxiliary_kw"],
                  tare_train_kg=mass["tare_train_kg"], loaded_train_kg=mass["loaded_train_kg"],
                  topology=layout, condition=condition, phase_s=phase, step_s=float(step))
    if constant_grade and route["grade_profile"] is not None:
        inputs["grade_basis"] = "constant_sensitivity"
    if slack:
        inputs["positioning_slack_s"] = slack
    def calculate(request):
        result = motion_power.compact(motion_power.evaluate(request))
        result["cost_scope"] = motion_power.unit_cost_basis(result)
        from .audit_production import seal_motion
        return seal_motion(result)
    result = scenario.stage("audited-motion", inputs, sources, calculate, cache, {})
    if (result["physical"]["upstream_candidate_id"] != vehicle["candidate_id"]
            or result["physical"]["alignment_id"] != route["alignment_id"]
            or result["scenario"]["demand_evaluation_id"] != demand["evaluation_id"]
            or result["physical"]["feeder"]["sites"][-1] != route["route_km"] * 1000):
        raise ValueError("Moving power and service results differ from the requested railway")
    return result


def screen_day(row):
    m = row["metrics"]
    g = row["gates"]
    return dict(**audit_power_return.binding(row), candidate_id=row["candidate_id"], evaluation_id=row["evaluation_id"],
                topology=row["physical"]["feeder"]["name"], site_chainages_m=row["physical"]["feeder"]["sites"],
                condition=row["scenario"]["condition"], failure=row["failure"],
                booked=m["booked_passenger_trips"], completed=m["completed_passenger_trips"],
                minimum_v=m["minimum_collector_v"], peak_site_ka=m["peak_site_current_ka"],
                maximum_delay_s=m["maximum_arrival_delay_s"],
                rms_branch_ka=m["bound_branch_rms_current_ka"], site_rms_ka=m["max_site_rms_current_ka"],
                served=m["boarded_passengers"], fleet=m["fleet_sets_required"],
                energy_kwh_per_train_km=row["energy_kwh_per_train_km"],
                numerical_valid=g["dc_numerical_screen"] and g["motion_work_balance_screen"],
                failed_screens=[k for k, v in g.items() if not v], gates=g,
                equipment_enquiry=row["electrical_enquiry"], installed_cost=row["cost_scope"])


def audit(*, headway=30, cars=6, material="steel", ambient=40, grade=None, soil=200.,
          survey=None, observed=None, demand_mode="service_sensitive", span=None, offers=None, phase_s=None, positioning_slack_s=None, vehicle_return=None,
          lift_radius=12., crane_capacity=None, erection_offer=(), supply_return=None,
          cache=scenario.CACHE):
    from . import audit_feeder_cost, audit_offers, audit_production
    route = airport_alignment.evaluate(survey=survey)
    evidence = Path(vehicle_return) if vehicle_return else None
    use_constant_grade = grade is not None
    grade = 0. if grade is None else grade
    slopes = route["grade_profile"]["grades_pct"] if route["grade_profile"] else []
    braking_grade = abs(grade) if use_constant_grade else max((abs(x) for x in slopes), default=0.)
    vehicle = vehicle_audit.evaluate(cars=cars, material=material, alignment=route, grade_pct=braking_grade,
        evidence_return=json.loads(evidence.read_bytes()) if evidence else None,
        evidence_directory=evidence.parent if evidence else None)
    demand, climate = service_inputs(route, vehicle, headway, ambient, observed, demand_mode)
    sources = scenario.source_contract(scenario.read_bound_sources()[0])["motion"]
    sources.update(scenario.source_hashes([HERE / "airport_alignment.py", HERE / "airport_demand.py"]))
    sources["compact_motion_contract"] = scenario.sha(
        (inspect.getsource(working_day) + inspect.getsource(audit_production.seal_motion)).encode()
    )
    # An observation file belongs to the service on which the counts were collected.
    service_offers = {}
    if positioning_slack_s is not None and phase_s is None:
        raise ValueError("Choose a terminal phase for a custom positioning allowance")
    if phase_s is not None and not 0 <= phase_s < headway * 60:
        raise ValueError("Terminal phase must fall within the chosen headway")
    for interval in ((headway,) if observed else (15, 20, 30)):
        passengers_at_interval, station = service_inputs(route, vehicle, interval, ambient, observed, demand_mode)
        phases = phase_options(route, vehicle, interval, passengers_at_interval["dwell_s"])
        phase = phase_s if interval == headway else None
        # This offset was discovered on the reference horizontal trace by replaying
        # 30-second candidates and refining the minimum delay at 2-second intervals.
        if (phase is None and interval == 30 and survey is None and cars == 6 and material == "steel"):
            phase = 1308
        if phase is not None:
            phases["static_shortlist"] = phases["best"]
            phases["best"] = positioning_trial(route, vehicle, interval, passengers_at_interval["dwell_s"],
                                               phase, positioning_slack_s if interval == headway else None)
        nominal = working_day(route, passengers_at_interval, vehicle, station, "paired6", "normal",
                              grade, cache, sources, constant_grade=use_constant_grade, phase=phases["best"]["phase_s"],
                              slack=phases["best"].get("positioning_slack_s", 0))
        service_offers[interval] = dict(phases=phases, annual_requested=passengers_at_interval["annual_all_journeys"],
                                ordinary=screen_day(nominal))
    chosen_timing = service_offers[headway]["phases"]["best"]
    civil = family_comparison.evaluate_high_load(route_km=route["route_km"], cars=cars, material=material,
                                                 soil_kpa=soil, selected_span_m=span, lift_radius_m=lift_radius,
                                                 crane_limit_t=crane_capacity, erection_offers=[
                                                     json.loads(Path(path).read_bytes()) for path in erection_offer])
    for state, load in civil["load_cases"].items():
        installed = vehicle["mass_cases"][state]
        if not math.isclose(load["loaded_train_kg"], installed["loaded_train_kg"]) or any(
            not math.isclose(a, b) for a, b in zip(load["axle_kg_per_car"], installed["axle_kg_per_car"], strict=True)
        ):
            raise ValueError("Civil and vehicle inputs differ on loaded mass or axle distribution")
    leader = civil["quotation_leaders"]["base"]
    girder = next((r for r in civil["rows"] if leader and r["physical_id"] == leader["physical_id"]), None)
    bids = json.loads(Path(offers).read_bytes()) if offers is not None else None
    if bids is not None and (not isinstance(bids, dict) or not isinstance(bids.get("layouts"), dict)
                             or set(bids["layouts"]) - set(LAYOUTS)):
        raise ValueError("Every offered layout must match a priced comparison in this working day")
    days, delivery, configs, comparisons = [], {}, [], {}
    for layout in LAYOUTS:
        for condition in motion_power.CONDITIONS:
            day = working_day(route, demand, vehicle, climate, layout, condition, grade, cache, sources, constant_grade=use_constant_grade,
                              phase=chosen_timing["phase_s"], slack=chosen_timing.get("positioning_slack_s", 0))
            days.append(screen_day(day))
            if condition == "normal":
                configs.append(day["scenario"])
                if girder:
                    kwargs = dict(civil_evaluation_id=civil["evaluation_id"], topology=layout, demand=demand)
                    priced = audit_production.evaluate(route, vehicle, day, girder, **kwargs)
                    if bids is not None:
                        chosen, comparisons[layout] = audit_offers.choices(bids, layout, priced["pricings"], priced["inputs"])
                        if chosen:
                            priced = audit_production.evaluate(route, vehicle, day, girder, supplier_offers=chosen, **kwargs)
                    delivery[layout] = priced
                elif bids is not None:
                    raise ValueError("No comparable civil and production scope for submitted offers")
    timing = dict(phase=chosen_timing["phase_s"], slack=chosen_timing.get("positioning_slack_s", 0))
    step_trials = {step:screen_day(working_day(route, demand, vehicle, climate, "paired6", "normal",
                    grade, cache, sources, step=step, constant_grade=use_constant_grade, **timing)) for step in (1, 2, 4)}
    # Same OD and auxiliary duty for every feeder. Heavier fitted equipment and
    # passengers follow the high BOM case; the train still boards actual riders.
    stress = []
    for layout in ("radial30", "paired6", "paired8", "paired6_heavy"):
        day = working_day(route, demand, vehicle, climate, layout, "combined", 2, cache, sources,
                          mass_state="high", constant_grade=True, **timing)
        stress.append(screen_day(day))
    supplied = Path(supply_return) if supply_return else None
    equipment = audit_power_return.assess(days, stress,
        json.loads(supplied.read_bytes()) if supplied else None,
        evidence_directory=supplied.parent if supplied else None)
    from .audit_register import register, disposition
    register_rows = register(route, demand, vehicle, civil, climate, configs, delivery, equipment)
    results = dict(schema="osr-airport-assumptions/1", historical_route=route["historical_route_order_screen"],
                alignment=route, demand={k:v for k,v in demand.items() if k != "hourly_od"},
                vehicle=vehicle, climate=climate, service_offers=service_offers, power_days=days,
                civil={k:v for k,v in civil.items() if k != "rows"}, civil_quotation=girder, feeder_equipment=equipment, step_trials=step_trials, high_mass_power=stress,
                production=delivery, supplier_comparisons=comparisons, assumptions=register_rows,
                requirement_policy_id=requirement_policy.catalogue()["policy_id"],
                decision=disposition(route, demand, vehicle, days, girder, delivery))
    for layout, assessment in results["decision"]["candidates"].items():
        heavy = next(r for r in stress if r["topology"] == layout)
        assessment["equipment_return_screen"] = equipment["layouts"][heavy["feeder_physical_id"]]["equipment_return_screen"]
        assessment["high_mass_combined_outage"] = {
            "evaluation_id":heavy["evaluation_id"], "failed_or_open_checks":heavy["failed_screens"]}
        if any(not passed for key,passed in heavy["gates"].items()
               if key not in ("protection_approved", "utility_connection_approved", "thermal_ratings_verified")):
            assessment["operating_screen"] = "failed"
    results["feeder_price_sensitivities"] = {
        layout: audit_feeder_cost.evaluate(model, [row for row in days + stress if row["topology"] == layout],
                                           comparison=delivery.get(next(other for other in LAYOUTS if other != layout)))
        for layout, model in delivery.items()
    }
    results["evaluation_id"] = scenario._id(results)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supply-return", type=Path, help="Candidate-bound feeder equipment ratings and protection evidence with adjacent documents")
    parser.add_argument("--vehicle-return", type=Path, help="Scoped first-article evidence manifest with adjacent documents")
    parser.add_argument("--lift-radius", type=float, default=12., help="Working crane radius (m)")
    parser.add_argument("--crane-capacity", type=float, help="Optional site capacity at the specified radius (tonnes)")
    parser.add_argument("--erection-offer", type=Path, action="append", default=[], help="Scoped civil erection offer JSON, repeatable")
    parser.add_argument("--offers", type=Path, help="Buyer-scoped supplier quotations and explicit awards (JSON)")
    parser.add_argument("--survey", type=Path, help="Submitted horizontal centreline and stop vertices")
    parser.add_argument("--observed", type=Path, help="Observed counts bound to the alignment and service")
    parser.add_argument("--demand-mode", choices=("fixed", "service_sensitive"), default="service_sensitive")
    parser.add_argument("--headway", type=int, choices=(15, 20, 30), default=30)
    parser.add_argument("--cars", choices=(3, 6), type=int, default=6)
    parser.add_argument("--material", choices=("steel", "aluminium", "hybrid"), default="steel")
    parser.add_argument("--phase-s", type=int, help="Terminal B offset within the chosen headway (seconds)")
    parser.add_argument("--positioning-slack-s", type=int, help="Time added before first and after last empty moves (seconds)")
    parser.add_argument("--ambient", type=int, choices=(32, 40, 48), default=40)
    parser.add_argument("--grade", type=float, help="Override the submitted grade profile with a signed constant-grade sensitivity (%)")
    parser.add_argument("--soil", type=float, default=200, help="Illustrative allowable soil pressure in kPa")
    parser.add_argument("--span", type=int, choices=(10,15,20,25,30), help="Limit the civil quotation comparison to a stock span (m)")
    action = parser.add_mutually_exclusive_group()
    for flag in ("json", "publish", "check"):
        action.add_argument("--" + flag, action="store_true")
    action.add_argument("--packet", type=Path, help="Export a budgetary supplier enquiry ZIP for one layout")
    parser.add_argument("--layout", choices=LAYOUTS, help="Feeder layout for the enquiry")
    opts = vars(parser.parse_args())
    packet, layout = opts.pop("packet"), opts.pop("layout")
    if (packet is None) != (layout is None):
        parser.error("Choose both --packet PATH and --layout for a supplier enquiry")
    raw, publish, check = (opts.pop(k) for k in ("json","publish","check"))
    if (check or publish) and any(opts[k] != parser.get_default(k) for k in opts):
        parser.error("The published comparison uses the documented defaults. Use --json for another case.")
    try:
        with disk_reservation(scenario.ROOT, scenario.ROOT, "Airport design assumption audit", 96 << 20):
            result = audit(**opts)
            if packet:
                from .audit_packet import issue
                manifest = issue(result, layout, packet)
                print(f"{packet}  {manifest['issue_id']}")
                return
            from .audit_register import markdown, review_page
            report = markdown(result)
            pages = {REPORT:report, HERE / "assumption-review.html":review_page(result)}
            if check or publish:
                from .airport_audit_verify import RECEIPT, verify_receipt
                native = verify_receipt(RECEIPT)
                for label, interval in (("adverse_15min",15), ("refined_30min",30)):
                    day = result["service_offers"][interval]["ordinary"]
                    if day["evaluation_id"] != native["cases"][label]["motion_evaluation_id"]:
                        raise ValueError("Independent native comparison and published timetable differ")
            if check or publish:
                from .audit_packet import PUBLISHED_RECEIPT, issue, verify
                published_packet = HERE / "audited-enquiry.zip"
                if publish:
                    manifest = issue(result, "paired6", published_packet)
                    receipt = {k: manifest[k] for k in ("issue_id", "evaluation_id", "candidate_id", "layout")}
                    scenario.write_atomic(PUBLISHED_RECEIPT, scenario.encode(receipt) + b"\n")
                else:
                    from tempfile import TemporaryDirectory
                    with TemporaryDirectory() as tmp:
                        fresh = Path(tmp) / "enquiry.zip"
                        if issue(result, "paired6", fresh) != verify(published_packet):
                            raise ValueError("Rebuild the corrected supplier packet with --publish")
            if publish:
                for path, content in pages.items():
                    scenario.write_atomic(path, content.encode())
            if check and any(path.read_text() != content for path,content in pages.items()):
                raise ValueError("Rebuild the current assumption audit from its sources")
            print(json.dumps(result, allow_nan=False, indent=2) if raw else report)
    except (OSError, ValueError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    main()
