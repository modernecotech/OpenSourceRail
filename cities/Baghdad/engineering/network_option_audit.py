"""Compare all already-priced civil/supply combinations on one first-programme service."""
import argparse
import json
from itertools import product
from math import isfinite
from pathlib import Path

from engineering.design_search import requirement_policy
from engineering.outline import baghdad_system as system

SUPPLIES = ("protected_conductor", "overhead", "limited_conductor_battery", "station_battery")
SERVICE = ("route_km", "stations", "line_count", "annual_train_km", "active_trainsets",
           "fleet_trainsets", "normal_places_per_train", "offered_places_per_hour_direction")


def decision_basis(cfg):
    """Read the actual local inputs, including their decision use and TOML locator."""
    groups = (
        ("fixed_comparison_scope", "", ("tunnel_km", "underground_stations", "track_count")),
        ("project_preference", "", ("preferred_supply", "overhead_exception")),
        ("local_service_offer", "service_plan", ("departures_per_hour_direction", "terminal_layover_min_each_end")),
        ("planning_allowance", "networks.first", ("route_km", "stations", "active_trainsets", "fleet_trainsets", "traction_supply_sites")),
        ("local_service_offer", "vehicle", ("cars_per_train", "normal_places_per_train", "door_openings_per_car_each_side", "peak_headway_s", "dwell_s", "commercial_speed_kmh", "speed_cap_kmh")),
        ("vehicle_trial", "vehicle", ("crowd_mass_t_per_train_before_supply", "energy_kwh_per_train_km_overhead_comparator")),
        ("traction_duty_trial", "power_assumptions", ("adverse_grade", "required_net_accel_m_s2", "resistance_accel_m_s2", "low_adhesion_mu", "adhesion_force_margin", "total_axles", "driven_axle_pair_multiple", "traction_rating_margin", "electrical_screen_voltage_kv", "electrical_screen_low_voltage_fraction")),
        ("quote_or_measure", "civil_rates", ("factory_beams_per_workday_per_yard", "erection_lifts_per_workday_per_front", "workdays_per_year", "beam_release_lag_months", "independent_pier_foundation_usd", "common_pier_crosshead_foundation_usd")),
        ("economic_scenario", "", ("price_year", "discount_rate_real", "comparison_years")),
        ("economic_scenario", "networks.first", ("construction_start_year", "construction_finish_year", "construction_cash_weights")),
        ("quote_or_measure", "operation_rates", ("delivered_energy_usd_per_kwh", "year_15_common_systems_replacement_fraction", "year_25_fleet_replacement_fraction")),
        ("quote_or_measure", "power_assumptions", ("buffer_life_years", "battery_life_years", "power_electronics_renewal_fraction_year_15", "line_equipment_renewal_fraction_year_25")),
    )
    inputs = {}
    for use, section, names in groups:
        values = cfg
        for part in section.split(".") if section else ():
            values = values[part]
        for name in names:
            key = f"{section}.{name}" if section else name
            inputs[key] = {"use": use, "value": values[name]}
    catalogue = requirement_policy.catalogue()
    return {
        "source": system.CONFIG.as_posix(), "inputs_by_toml_key": inputs,
        "policy_id": catalogue["policy_id"],
        "mandatory_obligations": [key for key, record in catalogue["criteria"].items()
                                  if record["category"] == "mandatory_obligation"],
        "compared_supply_options": SUPPLIES, "compared_spans_m": system.SUPPORTED_SPANS_M,
        "comparison_domain": "Price-model coverage only. Other spans, drives and erection methods require corresponding quantities.",
    }


def engineering_and_delivery(case, cfg):
    duty = case["service"]["service_duty"]
    traction = case["traction"]
    power = cfg["power_assumptions"]
    civil = case["civil"]
    physical = civil["physical_screen"]
    delivery = civil["delivery"]
    # Invert the same equal axle-load force balance as baghdad_power.compare_power.
    demand_accel = (power["required_net_accel_m_s2"] + 9.81 * power["adverse_grade"]
                    + power["resistance_accel_m_s2"])
    return {
        "active_fleet_lower_bound_for_this_offer": duty["peak_fleet_with_declared_layover"],
        "active_fleet_above_lower_bound": duty["active_fleet_above_lower_bound"],
        "working_timetable_established_by_this_model": case["service"]["timetable_established"],
        "loaded_train_t": case["vehicle"]["mass_t"],
        "traction_battery_kwh": case["vehicle"]["traction_battery_kwh_per_train"],
        "dc_traction_rating_request_mw": traction["dc_input_rating_request_mw"],
        "all_axles_driven_min_adhesion_for_declared_duty": demand_accel * power["adhesion_force_margin"] / 9.81,
        "driven_axles": case["vehicle"]["driven_axles"],
        "independent_braking_modelled": traction["independent_braking_modelled_here"],
        "section_current_rating_established": traction["electrical_screen"]["section_current_rating_established"],
        "grid_site_request_mw": case["supply_quantities"]["provisional_grid_site_rating_mw"],
        "longer_span_redesign_required": physical["longer_span_section_and_prestress_redesign_required"],
        "below_trial_crane_chart": physical["surrogate_hook_below_reference_crane_chart"],
        "actual_crane_at_radius_verified": physical["crane_at_actual_radius_verified"],
        "factory_yards_at_assumed_rate": delivery["factory_yards_needed_at_declared_rate"],
        "erection_fronts_at_assumed_rate": delivery["erection_fronts_needed_at_declared_rate"],
        "factory_and_crane_availability_verified": delivery["factory_shifts_and_crane_availability_verified"],
        "additional_yard_and_front_cost_usd": delivery["additional_yard_and_front_cost_usd"],
    }


def discounted_cost(case, rate, years):
    """Reprice identical year-zero investment and unchanged operating and renewal duty."""
    annual = case["operation_usd_m_year"]["total"]
    factor = 1 / (1 + rate)
    try:
        pv = (case["capital_usd_m"]["installed"]
              + sum(annual * factor**year for year in range(1, years + 1))
              + sum(event["usd_m"] * factor**event["year"] for event in case["renewals_usd_m"]
                    if event["year"] <= years))
    except OverflowError as error:
        raise ValueError("Present value exceeds numerical range at the requested real rate") from error
    if not isfinite(pv):
        raise ValueError("Present value exceeds numerical range at the requested real rate")
    return pv


def evaluate(discount_rate=None):
    cfg = system.load(network="first")
    rate = cfg["discount_rate_real"] if discount_rate is None else discount_rate
    if not isfinite(rate) or rate <= -1:
        raise ValueError("The real annual discount rate must be finite and greater than -100%")
    common_service = None
    rows = []
    for span, shared, supply in product(system.SUPPORTED_SPANS_M, (False, True), SUPPLIES):
        case = system.evaluate("first", supply, span_m=span, common_pier=shared)
        service = {name: case["service"][name] for name in SERVICE}
        if common_service is None:
            common_service = service
        elif service != common_service:
            raise ValueError("Alternatives differ in passenger service or fleet scope")
        assessment = requirement_policy.assess({}, candidate_id=case["physical_candidate_id"])
        rows.append({
            "span_m": span, "pier": "shared" if shared else "separate", "supply": supply,
            "physical_id": case["physical_candidate_id"], "evaluation_id": case["evaluation_id"],
            "installed_capital_usd_m": case["capital_usd_m"]["installed"],
            "priced_30y_pv_usd_m": discounted_cost(case, rate, cfg["comparison_years"]),
            "pv_usd_m_by_real_discount_rate": {
                str(rate): discounted_cost(case, rate, cfg["comparison_years"])
                for rate in sorted({0.02, cfg["discount_rate_real"], 0.08, rate})
            },
            "site_or_physical_accepted": case["site_or_physical_accepted"],
            "engineering_and_delivery": engineering_and_delivery(case, cfg),
            "obligation_assessment_id": assessment["evaluation_id"],
            "declared_hard_screen": assessment["declared_hard_screen"],
            "selection_eligible": False,
        })
    if len({r["physical_id"] for r in rows}) != len(rows):
        raise ValueError("A supply or civil change failed to receive a distinct physical identity")
    sources = dict(case["source_sha256"])
    for source in (Path(__file__), Path(requirement_policy.__file__)):
        sources[source.relative_to(system.ROOT).as_posix()] = system._hash(source)
    report = {
        "real_discount_rate": rate, "service": common_service, "cases": rows, "sources": sources, "basis": decision_basis(cfg),
        "selection_id": None, "decision_status": "priced comparison only",
        "selection_holds": [
            "Boarding, crowd loads, independent stopping and engineering limits need candidate-specific evidence.",
            "Dispatch, protected power, site-specific supports and erection feasibility are open for this network.",
            "Availability, additional yard/front costs and delivered supplier scope remain unconfirmed.",
        ],
    }
    report["audit_id"] = system._id(report)
    return report


def price_table(rows):
    lines = [
        "| Span and piers | Protected conductor | Overhead | Partial conductor and battery | Station charging and battery |",
        "|---|---:|---:|---:|---:|",
    ]
    amounts = {(r["span_m"], r["pier"], r["supply"]): r["priced_30y_pv_usd_m"] for r in rows}
    for span, pier in product(system.SUPPORTED_SPANS_M, ("separate", "shared")):
        prices = [f"{amounts[span, pier, supply]:,.0f}" for supply in SUPPLIES]
        lines.append("| " + " | ".join([f"{span} m {pier}", *prices]) + " |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="verify the published decision table")
    modes.add_argument("--json", action="store_true", help="include identities and prices for each case")
    parser.add_argument("--discount-percent", type=float, help="real annual discount rate in percent")
    args = parser.parse_args()
    rate = args.discount_percent / 100 if args.discount_percent is not None else None
    result = evaluate(rate)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    table = price_table(result["cases"])
    if args.check:
        if rate is not None and rate != system.load(network="first")["discount_rate_real"]:
            parser.error("--check uses the published financing assumption")
        if table not in (system.ROOT / "docs/DESIGN-DECISIONS.md").read_text():
            raise SystemExit("The decision table differs from the current network comparison")
    else:
        print(f"First programme, 30-year priced present value in USD millions at {result['real_discount_rate']:.2%} real.")
        print(table)
        print("All figures are planning estimates. Site and physical acceptance remain open.")
    print("Audit ID", result["audit_id"])


if __name__ == "__main__":
    main()
