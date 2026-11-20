"""Rebuild the factory load and staffing study from the published railway quantities."""
import argparse
import hashlib
import json
import runpy
from math import ceil, floor, isclose
from pathlib import Path
import tomllib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUTS = [
    "docs/reference-v07/digital/production/handoff.json",
    "docs/reference-v07/concept.toml",
    "cities/Baghdad/system.toml",
    "cities/Baghdad/system-results.json",
    "cities/Baghdad/service-diagrams.json",
]

# Direct labour hours per car in production sequence. Baghdad values are a
# time-study request for that car, particularly its eight openings per car.
ROUTE = {
    "core": [260, 120, 80, 80, 100, 80],
    "baghdad": [260, 120, 260, 80, 200, 80],
}
STAGES = ["body", "bogies and drive", "doors and interior", "HVAC and auxiliaries",
          "wiring, collection and cooling", "marriage and test"]


def read(path):
    data = (ROOT / path).read_text()
    return tomllib.loads(data) if path.endswith(".toml") else json.loads(data)


def vehicle_load(cars, days, route):
    interval = 5
    first_completion = len(route) * interval
    effective_days = floor(days * 85 / 100)
    cars_per_line = 1 + (effective_days - first_completion) // interval
    lines = ceil(cars / cars_per_line)
    crew = [ceil(hours / (interval * 8 * 0.80)) for hours in route]
    return {
        "cars": cars, "scheduled_workdays": days, "effective_line_days": effective_days,
        "first_car_effective_day": first_completion, "takt_effective_days": interval,
        "cars_per_line_in_window": cars_per_line, "lines": lines,
        "cars_capacity": lines * cars_per_line, "hours_per_car_by_stage": dict(zip(STAGES, route)),
        "direct_posts_by_stage": dict(zip(STAGES, crew)), "direct_posts_per_line": sum(crew),
        "direct_posts_all_lines": lines * sum(crew), "support_posts_all_lines": lines * 4,
        "direct_content_hours": cars * sum(route),
        "direct_content_job_years_at_1720_hours": round(cars * sum(route) / 1720, 1),
    }


def roster(stations, controls, depots, km, active, departures):
    # Average simultaneous train duties scale with the offered peak fleet.
    # Retain integer duties each hour. Inspect the future diagrams for actual turns.
    train_hours_day = sum(ceil(active * f / max(departures)) for f in departures)
    line_teams = ceil(km / 30)
    per_day = {
        "train operators": train_hours_day,
        "station duty and passenger assistance": stations * 3 * 18,
        "station security and cleaning": stations * 2 * 18,
        "OCC control, traction, incidents and information": controls * 4 * 24,
        "depot rolling-stock technicians": depots * (8 * 16 + 4 * 8),
        "civil, track and power response": line_teams * 4 * 24,
    }
    hours = {k: h * 365 for k, h in per_day.items()}
    hours["planning, payroll, stores and trainers"] = depots * 6 * 1720
    fte = {k: ceil(h / 1720) for k, h in hours.items()}
    return {"duty_hours_per_year": hours, "posts_fte": fte, "total_fte": sum(fte.values()),
            "train_operator_hours_per_day": train_hours_day, "field_groups": line_teams}


def workforce_scenarios(legacy, train_hours, basis):
    shared = dict(legacy["duty_hours_per_year"])
    del shared["train operators"]
    scenarios = {}
    options = {
        "goa4": ("Unattended GoA4", "scheduled onboard staff", 0),
        "supervised": ("Supervised commissioning", "onboard commissioning supervisors", 1),
        "assisted": ("Onboard passenger assistance", "onboard passenger assistants", 0.25),
    }
    for key, (label, role, share) in options.items():
        annual = {role: ceil(train_hours * 365 * share), **shared}
        posts = {name: ceil(h / 1720) for name, h in annual.items()}
        scenarios[key] = {"name": label, "onboard_role": role, "onboard_duty_fraction": share,
                          "duty_hours_per_year": annual, "posts_fte": posts,
                          "total_fte": sum(posts.values()), "train_duty_basis": basis}
    return scenarios


def opex_ledger(baseline, envelopes):
    if not 0 <= sum(envelopes.values()) <= baseline:
        raise ValueError("Workforce cost envelopes exceed annual operating cost")
    return {"baseline_usd_m_year": baseline, "eligible_envelopes_usd_m_year": envelopes,
            "other_costs_usd_m_year": baseline - sum(envelopes.values()),
            "embedded_payroll_usd_m_year": None, "operator_pay_rates_usd_per_fte_year": None}


def citywide_mainline_workforce(cfg, city, diagrams, staff):
    option = diagrams["citywide_mainline_option"]
    if (option["infrastructure_candidate_id"] != city["selected_candidate_id"]
            or option["selected_cost_evaluation_id"] != city["selected_evaluation_id"]):
        raise ValueError("Citywide mainline workings belong to another infrastructure estimate")
    original = diagrams["networks"]["metropolitan"]
    rows = [original["groups"][name] for name in option["base_groups_reused"]]
    rows.extend(option["mainline_workings"].values())
    train_hours = sum(row["scheduled_trips"] * (row["one_way_s_including_dwell"] + row["minimum_turn_s"])
                      for row in rows) / 3600
    distance = option["annual_diagrammed_train_km"]
    if not isclose(distance + option["annual_train_km_on_deferred_sections"], original["annual_cost_ledger_train_km"]):
        raise ValueError("Citywide operation must account for deferred mileage")
    rate = cfg["operation_rates"]
    baseline = city["selected_annual_opex_usd_m"]
    grid_gwh = city["power_cases"]["protected_conductor"]["annual_grid_gwh"] * distance / original["annual_cost_ledger_train_km"]
    costs = {"Non-energy train operations": distance * rate["non_energy_vehicle_operations_usd_per_train_km"] / 1e6,
             "Station operations": staff["opex"]["eligible_envelopes_usd_m_year"]["Station operations"],
             "Power maintenance": baseline["power_maintenance"]}
    total = sum(costs.values()) + grid_gwh * rate["delivered_energy_usd_per_kwh"]
    infrastructure = cfg["networks"]["metropolitan"]
    basis = (f'All {len(rows)} routes have timed workings, totalling {train_hours:,.1f} train-hours/day including minimum turns. '
             f'{len(option["deferred_sections_costed_km"])} access sections are deferred. The full {infrastructure["stations"]}-station '
             f'and {infrastructure["fleet_trainsets"]}-set capital programme and built line upkeep are retained.')
    return {"infrastructure_network": "metropolitan", "source_physical_id": option["infrastructure_candidate_id"],
            "source_evaluation_id": option["selected_cost_evaluation_id"], "source_diagram_evaluation_id": diagrams["evaluation_id"],
            "annual_train_km": distance, "annual_grid_gwh": grid_gwh, "train_hours_day_including_minimum_turns": train_hours,
            "opex": opex_ledger(total, costs), "workforce_scenarios": workforce_scenarios(staff["roster"], train_hours, basis)}


def build():
    handoff, core, baghdad, results, diagrams = [read(path) for path in INPUTS]
    production = handoff["production"]
    assert sum(ROUTE["core"]) == production["full_car_direct_assembly_hours_allowance"]
    stages = {s["stage"]: s for s in handoff["schedule"]["stages"]}
    yards = 2
    core_end = stages["beam-factory"]["end_month"]
    erection_start = stages["beam-erection"]["start_month"]
    minimum_buffer = max(0, ceil(production["beam_count"] / yards) - (core_end - erection_start) * 20 * 8)
    studies = {"core": {
        "source_physical_id": handoff["physical_candidate_id"],
        "source_evaluation_id": handoff["evaluation_id"], "source_selection_id": handoff["selection_id"],
        "vehicle": vehicle_load(production["fleet_cars"], 24 * 20, ROUTE["core"]),
        "civil": {"beams": production["beam_count"], "yards": yards, "erection_fronts": 2,
                  "minimum_pre_erection_stock_per_yard": minimum_buffer,
                  "off_yard_slots_needed_per_yard": max(0, minimum_buffer - 180)},
        "roster": roster(core["corridor"]["stations"], 1, 1, core["corridor"]["route_km"],
                         core["service"]["fleet_active"], [30] * 4 + [12] * 14),
    }}
    core_roster = studies["core"]["roster"]
    timetable_source = "docs/reference-v07/integration/timetable.py"
    core_workings = runpy.run_path(str(ROOT / timetable_source))["build"]()
    if core_workings["physical_candidate_id"] != handoff["physical_candidate_id"]:
        raise ValueError("Core train diagrams and workforce must share a vehicle and infrastructure selection")
    duty = core_workings["summary"]
    core_hours = duty["passenger_train_hours_day"] + duty["minimum_turnback_train_hours_day"]
    studies["core"]["source_diagram_evaluation_id"] = core_workings["evaluation_id"]
    studies["core"]["train_hours_day_including_minimum_turns"] = core_hours
    studies["core"]["workforce_scenarios"] = workforce_scenarios(
        core_roster, core_hours,
        f'{duty["trip_count"]} daily train workings account for {duty["passenger_train_hours_day"]:,.1f} passenger '
        f'train-hours and {duty["minimum_turnback_train_hours_day"]:,.1f} minimum turnback hours. '
        'Each onboard duty still needs crew relief, stabling moves and handover.')
    studies["core"]["opex"] = opex_ledger(core["economics"]["annual_opex_usd_m"], {
        "Control and operations staff": 4, "Fleet maintenance": 10,
        "Civil, station and overhead maintenance": 6, "Insurance and administration": 3})
    for key, city in results["networks"].items():
        network = baghdad["networks"][key]
        civil = city["selected_civil_delivery"]
        monthly = civil["monthly_delivery"]
        yards = civil["factory_yards_needed_at_declared_rate"]
        peak_inventory = max(m["cast_beams_awaiting_release"] + m["released_beams_awaiting_erection"]
                             for m in monthly["months"])
        cars = city["selected_service_allowance"]["fleet_trainsets"] * baghdad["vehicle"]["cars_per_train"]
        years = civil["civil_finish_year"] - civil["civil_start_year"] + 1
        studies[key] = {
            "source_physical_id": city["selected_candidate_id"], "source_evaluation_id": city["selected_evaluation_id"],
            "vehicle": vehicle_load(cars, years * baghdad["civil_rates"]["workdays_per_year"], ROUTE["baghdad"]),
            "civil": {"beams": monthly["beams_cast"], "yards": yards,
                      "erection_fronts": civil["erection_fronts_needed_at_declared_rate"],
                      "peak_month_end_total_inventory": peak_inventory,
                      "slots_per_yard_if_balanced": ceil(peak_inventory / yards),
                      "slots_per_yard_offered": 180},
            "roster": roster(network["stations"], network["control_centres"], network["depots"], network["route_km"],
                             network["active_trainsets"], baghdad["service_plan"]["departures_per_hour_direction"]),
        }
        diagram = diagrams["networks"][key]
        if (diagram["selected_candidate_id"] != city["selected_candidate_id"]
                or diagram["selected_system_evaluation_id"] != city["selected_evaluation_id"]):
            raise ValueError(f"{key} staff duty and cost ledger refer to different railway evaluations")
        studies[key]["source_diagram_evaluation_id"] = diagrams["evaluation_id"]
        hourly = baghdad["service_plan"]["departures_per_hour_direction"]
        held_hours = sum(ceil(diagram["held_peak_trainsets_cost_screen"] * f / max(hourly)) for f in hourly)
        diagram_hours = diagram["diagrammed_train_seconds_per_day"] / 3600
        basis = f"{diagram_hours:,.1f} diagrammed train-hours/day including minimum turnbacks."
        if diagram["held_service_group_ids"]:
            basis += (f" Add {held_hours:,} train-hours/day estimated from peak fleet and hourly frequency "
                      f"for unresolved groups {', '.join(diagram['held_service_group_ids'])}.")
        studies[key]["workforce_scenarios"] = workforce_scenarios(studies[key]["roster"],
                                                                  diagram_hours + held_hours, basis)
        op = city["selected_annual_opex_usd_m"]
        rates = baghdad["operation_rates"]
        distance = city["selected_service_allowance"]["annual_train_km"]
        train = distance * rates["non_energy_vehicle_operations_usd_per_train_km"] / 1e6
        station = network["stations"] * rates["station_operations_usd_m_per_year"]
        if not isclose(train + station, op["non_energy_and_station"]):
            raise ValueError(f"{key} train and station allowances disagree with operating ledger")
        studies[key]["opex"] = opex_ledger(op["total"], {
            "Non-energy train operations": train, "Station operations": station,
            "Power maintenance": op["power_maintenance"]})
        if not isclose(studies[key]["opex"]["other_costs_usd_m_year"], op["energy"]):
            raise ValueError(f"{key} workforce ledger does not conserve the energy budget")
    for study in studies.values():
        v, c = study["vehicle"], study["civil"]
        c["civil_yard_day_posts"] = c["yards"] * 18
        c["erection_day_posts"] = 8 * c["erection_fronts"]
        study["production_day_posts"] = v["direct_posts_all_lines"] + v["support_posts_all_lines"] + c["civil_yard_day_posts"] + c["erection_day_posts"]
    mainlines = citywide_mainline_workforce(baghdad, results["networks"]["metropolitan"], diagrams, studies["metropolitan"])
    return {"operating_options": {"metropolitan-mainlines": mainlines}, "schema": "osr.factory-workforce.study.3", "status": "capacity and quotation study",
            "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                              for p in [*INPUTS, timetable_source, "docs/reference-v07/cost/README.md", str(Path(__file__).resolve().relative_to(ROOT))]},
            "studies": studies}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare with the published quantities")
    args = parser.parse_args()
    payload = build()
    payload["study_evaluation_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    target = HERE / "quantities.json"
    if args.check:
        if target.read_text() != content:
            raise SystemExit("Factory/workforce quantities differ from the published study.")
    else:
        target.write_text(content)
    print(payload["study_evaluation_sha256"])
