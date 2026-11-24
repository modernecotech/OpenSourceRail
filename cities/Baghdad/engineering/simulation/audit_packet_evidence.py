"""Reconcile projected Airport enquiry evidence with its upstream calculations."""

from math import ceil, isclose, isfinite
import tomllib

from cities.Baghdad.engineering.prototype import factory

from . import airport_demand, audit_feeder_cost, audit_power_return, passengers, scenario

APPROVAL_GATES = {"protection_approved", "thermal_ratings_verified", "utility_connection_approved"}
OD_AGGREGATES = {"annual_all_journeys", "annual_paid_journeys", "annual_passenger_km",
                 "busiest_departure_load", "platform_queue", "mean_trip_km"}


def require(condition, scope):
    if not condition:
        raise ValueError(f"Enquiry {scope} differs from its upstream evidence")


def project(record, omitted):
    return {key: value for key, value in record.items() if key not in omitted}


def demand_projection(demand, alignment, cars):
    mode = demand["mode"]
    require(mode in ("fixed", "service_sensitive", "observed"), "demand mode")
    upstream = airport_demand.evaluate(alignment, headway_min=demand["headway_min"], dwell_s=demand["dwell_s"],
                                       formation_cars=cars, mode="fixed" if mode == "observed" else mode)
    if mode != "observed":
        require(scenario.encode(demand) == scenario.encode(project(upstream, {"hourly_od"})), "forecast demand")
        return

    source = demand["observed_source"]
    require(source["service_offer"] == upstream["service_offer"]["observation_context"], "observed service offer")
    digest = source["file_sha256"]
    require(isinstance(digest, str) and len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest), "observed OD source digest")
    require(demand["source_sha256"] == dict(upstream["source_sha256"], observed_od_input=digest),
            "observed demand sources")
    excluded = OD_AGGREGATES | {"hourly_od", "mode", "observed_source", "source_sha256", "evaluation_id"}
    require(scenario.encode(project(demand, excluded)) == scenario.encode(project(upstream, excluded)),
            "observed demand context")
    totals = {key: demand[key] for key in OD_AGGREGATES - {"mean_trip_km"}}
    require(all(type(value) in (int, float) and isfinite(value) and value >= 0 for value in totals.values()),
            "observed demand aggregates")
    all_trips = totals["annual_all_journeys"]
    passenger_km = totals["annual_passenger_km"]
    max_demand = all_trips / airport_demand.SERVICE_DAY_COUNT * demand["headway_min"] / 60
    require(totals["annual_paid_journeys"] <= all_trips
            and passenger_km <= all_trips * alignment["route_km"] + 1e-6
            and all(totals[key] <= max_demand + 1e-6 for key in ("busiest_departure_load", "platform_queue"))
            and demand["mean_trip_km"] == (passenger_km / all_trips if all_trips else None),
            "observed journey and loading balance")


def check_duties(feeder, assessment, layout, feeder_id):
    duties = feeder["duties"]
    heavy_rows = feeder["high_mass"]
    require(len(heavy_rows) == 1 and heavy_rows[0]["condition"] == "combined", "high-mass duty coverage")
    heavy = heavy_rows[0]
    normal, = (day for day in duties if day["condition"] == "normal")
    require(all(day["topology"] == layout and day["candidate_id"] == normal["candidate_id"]
                for day in duties + heavy_rows), "duty candidate")
    require(all(APPROVAL_GATES <= day["gates"].keys()
                and all(type(met) is bool for met in day["gates"].values())
                and not any(day["gates"][key] for key in APPROVAL_GATES)
                and sorted(day["failed_screens"]) == sorted(key for key, met in day["gates"].items() if not met)
                and type(day["numerical_valid"]) is bool
                and day["numerical_valid"] == (day["gates"]["dc_numerical_screen"]
                                               and day["gates"]["motion_work_balance_screen"])
                and type(day["booked"]) is int and type(day["completed"]) is int
                and 0 <= day["completed"] <= day["booked"]
                and (not day["gates"]["all_workings_complete"] or day["completed"] == day["booked"])
                for day in duties + heavy_rows),
            "duty gate and trip results")
    require(assessment["high_mass_combined_outage"] == dict(evaluation_id=heavy["evaluation_id"],
            failed_or_open_checks=heavy["failed_screens"]), "high-mass decision")
    inventory = audit_power_return._inventory(duties, heavy_rows)[feeder_id]
    equipment = feeder["equipment"]
    require(equipment["duties"] == inventory["duties"]
            and equipment["envelope"] == audit_power_return._envelope(inventory["duties"])
            and equipment["equipment_return_screen"] in ("pass", "fail", "unknown")
            and equipment["complete_equipment_duty_screen"] in ("pass", "fail", "unknown")
            and equipment["production_ranking_eligible"] is False,
            "equipment duty inventory and margins")
    if equipment["supplier_return_id"] is None:
        expected = audit_power_return.assess(duties, heavy_rows)["layouts"][feeder_id]
        require(equipment == expected, "equipment declaration")
    return normal, heavy


def check_decision(decision, route, vehicle, price, feeder, heavy):
    from .audit_register import vehicle_screens, functional_screen
    assessment = decision["assessment"]
    require(assessment["vehicle_screens"] == vehicle_screens(vehicle), "vehicle decision")
    duties = feeder["duties"]
    failures = {day["condition"]: [key for key in day["failed_screens"] if key not in APPROVAL_GATES]
                for day in duties}
    heavy_failed = any(key not in APPROVAL_GATES for key in heavy["failed_screens"])
    require(assessment["failures_by_duty"] == failures
            and assessment["numerical_valid"] is all(day["numerical_valid"] for day in [*duties, heavy])
            and assessment["operating_screen"] == ("failed" if any(failures.values()) or heavy_failed else "passed")
            and assessment["supplier_and_utility_checks"] == dict.fromkeys(APPROVAL_GATES, False)
            and assessment["equipment_return_screen"] == feeder["equipment"]["equipment_return_screen"]
            and assessment["complete_equipment_duty_screen"] == feeder["equipment"]["complete_equipment_duty_screen"],
            "operating decision")
    require(assessment["functional_screen"] == functional_screen(assessment), "combined functional decision")
    require(assessment["qualification"] == "open" and assessment["investment_rank"] is None
            and assessment["scope_cost_status"] == "partial or unpriced"
            and assessment["remaining_cost_scope"] == price["unpriced_lots"]
            and price["complete_installed_price_usd"] is None and price["complete_owner_present_value_usd"] is None
            and price["financial_selection_eligible"] is False and price["physical_acceptance"] == "open",
            "budget and qualification decision")
    holds = decision["evidence_needed"]
    require(holds.keys() == {"alignment", "demand", "stopping and vehicle", "traction supply", "civil", "procurement"}
            and all(holds.values()) and holds["alignment"] == route["review_gaps"]
            and holds["stopping and vehicle"] == vehicle["physical_measurements_required"], "evidence holds")


def check_evidence(docs, manifest):
    """Validate replayable projections and ties to the parent study."""
    route = docs["engineering/alignment.json"]
    demand = docs["engineering/service.json"]
    vehicle = docs["engineering/vehicle.json"]
    climate = docs["engineering/station.json"]
    price = docs["pricing/production.json"]
    feeder = docs["engineering/feeder.json"]
    decision = docs["decision.json"]
    cars = vehicle["physical"]["formation_cars"]
    demand_projection(demand, route, cars)
    require(price["child_ids"]["demand_evaluation_id"] == demand["evaluation_id"], "pricing demand reference")

    climate_inputs = dict(cars=cars, headway_min=demand["headway_min"], ambient_c=climate["inputs"]["ambient_c"],
                          busiest_departure_load=min(700 * cars // 6, ceil(demand["busiest_departure_load"])),
                          platform_queue=ceil(demand["platform_queue"]))
    if demand["dwell_s"] != route["dwell_s"]:
        climate_inputs["dwell_s"] = demand["dwell_s"]
    require(scenario.encode(climate) == scenario.encode(passengers.evaluate(climate_inputs))
            and ceil(climate["door_exchange"]["total_dwell_with_one_assisted_transfer_s"]) <= demand["dwell_s"],
            "station, ventilation and accessible dwell")
    require(scenario.encode(docs["factory/routing-basis.json"]) == scenario.encode(factory.build()),
            "factory routing")
    normal, heavy = check_duties(feeder, decision["assessment"], manifest["layout"], manifest["feeder_physical_id"])
    sensitivity = feeder["planning_price_sensitivity"]
    independent = audit_feeder_cost.evaluate(price, feeder["duties"] + feeder["high_mass"])
    projected = {"priced_cash_break_even", "sensitivity_id"}
    require(sensitivity["sensitivity_id"] == scenario._id(project(sensitivity, {"sensitivity_id"}))
            and project(independent, projected) == project(sensitivity, projected), "feeder rate sensitivity")
    operations = price["operation_basis"]
    days = operations["service_days"]
    served = normal["served"] * days
    share = demand["annual_paid_journeys"] / demand["annual_all_journeys"] if demand["annual_all_journeys"] else 0.
    require(days == tomllib.loads(airport_demand.SYSTEM.read_text())["vehicle"]["service_days_per_year"]
            and operations["booked_working_day_passenger_trips"] == normal["booked"]
            and operations["completed_working_day_passenger_trips"] == normal["completed"]
            and operations["working_day_completed"] is normal["gates"]["all_workings_complete"]
            and isclose(operations["annual_completed_journeys"], served, abs_tol=1e-6)
            and isclose(operations["annual_paid_journeys_proxy"], served * share, abs_tol=1e-6),
            "working-day operating and fare basis")
    check_decision(decision, route, vehicle, price, feeder, heavy)
