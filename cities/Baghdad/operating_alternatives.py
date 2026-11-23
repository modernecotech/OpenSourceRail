"""Compare the six-car Airport opening, a 30-minute Airport trial and the urban survey priority."""

import csv
from hashlib import sha256
import json
from pathlib import Path
import tomllib
from zipfile import ZipFile

from cities.Baghdad import airport_opening, airport_service, urban_opening
from engineering.outline import baghdad_diagrams as diagrams, baghdad_system as system
from engineering.station_rail.common import digest

PROTOTYPE_PACKET = Path(__file__).with_name("engineering") / "prototype" / "airport-prototype.zip"
PROCUREMENT_ESTIMATE = PROTOTYPE_PACKET.with_name("sourcing-estimate.json")


def lower_frequency(cfg, airport):
    """Rebuild the six-car workings at two departures per hour in each direction."""
    departures_per_hour = 2
    headway = 3600 // departures_per_hour
    hourly = [departures_per_hour] * cfg["vehicle"]["service_hours_per_day"]
    amended = {
        **cfg,
        "vehicle": {**cfg["vehicle"], "peak_headway_s": headway},
        "service_plan": {**cfg["service_plan"], "departures_per_hour_direction": hourly},
    }
    route = airport["one_way_km"]
    group, trips, patterns = diagrams.group_diagram("Airport", airport["outward_stops"], route, amended)
    profiles = airport_service.leg_profiles(patterns, route, cfg)
    positioning = airport_service.positioning_trips(trips, group)
    terminal = airport_service.terminal_screen(cfg, group, trips + positioning, patterns, profiles)
    value = dict(
        group=group,
        hourly=hourly,
        peak_headway_s=headway,
        trips=trips,
        positioning_trips=positioning,
        patterns=patterns,
        leg_profiles=profiles,
        terminal=terminal,
        scheduled_places_per_hour_direction=departures_per_hour * cfg["vehicle"]["normal_places_per_train"],
        non_revenue_km_per_day=len(positioning) * route + sum(move["distance_km"] for move in terminal["yard_moves"]),
        physical_accepted=False,
        source_sha256={
            str(path.relative_to(system.ROOT)): digest(path)
            for path in (Path(__file__).resolve(), Path(airport_service.__file__).resolve(),
                         Path(diagrams.__file__).resolve(), airport_service.TRIAL.resolve())
        },
    )
    value["evaluation_id"] = system._id(value)
    return value


def airport_cost_sensitivity(cfg, reference, reference_service, trial, trial_candidate, receipt):
    """Hold site scope and roster fixed and vary rolling-stock purchase and mileage."""
    days = cfg["vehicle"]["service_days_per_year"]
    reserve = tomllib.loads(airport_opening.SITE_INPUT.read_text())["operations"]["non_revenue_distance_share"][1]
    annual_km = {}
    for name, service in (("airport_15_minute", reference_service), ("airport_30_minute_trial", trial)):
        group = service["group"]
        passenger_km = group["scheduled_trips"] * group["one_way_km"] * days
        empty_km = max(passenger_km * reserve, service["non_revenue_km_per_day"] * days)
        annual_km[name] = dict(passenger=passenger_km, non_revenue=empty_km, total=passenger_km + empty_km)
    iraq = reference["iraq_operations"]
    central = iraq["cases"]["central"]
    train_nonlabour = (reference["annual_opex_usd_m"]["train_operations"]
                      - iraq["estimated_credit_by_envelope_usd_m_year"]["Non-energy train operations"]
                      + central["non_revenue_non_energy_usd_m"])
    retained = central["opex_usd_m"] - central["electricity_usd_m"] - train_nonlabour
    if min(train_nonlabour, retained - central["payroll_usd_m"]) < 0:
        raise ValueError("Reference payroll and mileage envelopes do not reconcile")
    fleet_heading = "Fleet, including spare sets"
    direct = {key: value for key, value in reference["scopes_usd_m"].items()
              if key not in {"Design and assurance", "Testing and commissioning", "Project allowance"}}
    fleet_sets = reference["bundle"]["active_sets"] + reference["bundle"]["spares"]
    unit_price = direct[fleet_heading] / fleet_sets
    cases = {}
    for name, service, candidate in (
        ("airport_15_minute", reference_service, reference["candidate_id"]),
        ("airport_30_minute_trial", trial, trial_candidate),
    ):
        fleet = service["group"]["diagrammed_sets"] + reference["bundle"]["spares"]
        ratio = annual_km[name]["total"] / annual_km["airport_15_minute"]["total"]
        price = airport_opening.allowances({**direct, fleet_heading: fleet * unit_price},
                                         cfg["capital_rates_usd_m"])
        bands = {}
        for split, share in (("all_train_nonlabour_fixed", 0), ("half_train_nonlabour_variable", .5),
                             ("all_train_nonlabour_variable", 1)):
            fixed = retained + (1 - share) * train_nonlabour
            mileage = ratio * share * train_nonlabour
            energy = ratio * central["electricity_usd_m"]
            annual_total = fixed + mileage + energy
            bands[split] = dict(
                train_nonlabour_variable_share=share,
                fixed_payroll_and_upkeep_usd_m=fixed,
                variable_train_mileage_usd_m=mileage,
                variable_electricity_usd_m=energy,
                annual_opex_usd_m=annual_total,
                paid_journeys_day_to_cover_opex=annual_total * 1e6 / (days * receipt),
            )
        cases[name] = dict(
            candidate_id=candidate,
            service_evaluation_id=service["evaluation_id"],
            annual_train_km=annual_km[name],
            mileage_ratio_to_15_minute=ratio,
            retained_reference_payroll_usd_m=central["payroll_usd_m"],
            fleet_sets=fleet,
            capital_scopes_usd_m=price,
            capital_usd_m=sum(price.values()),
            capital_if_all_six_sets_retained_usd_m=sum(reference["scopes_usd_m"].values()),
            annual_cost_cases=bands,
        )
    sensitivity = dict(
        reference_opening_evaluation_id=reference["evaluation_id"],
        assumptions=[
            f"Retain all {reference['bundle']['grid_sites']} priced supply sites and all nonfleet direct capital scopes. "
            "Unit price per set held constant including the embedded factory and delivery allowance per set. "
            "Design, testing and contingency reapplied to the revised direct subtotal.",
            "Retain the central Iraq payroll, station, workshop and line upkeep envelopes. "
            "Retain any incremental feed-site and switch upkeep. "
            "Split only the net train nonlabour allowance between fixed and mileage-related costs.",
            "Traction and hotel electricity follow modelled train-km at the common reference cost per km. "
            "Use the higher of timed non-revenue mileage and the central planning allowance. "
            "Duty, grid sizing, local enabling works, renewal and funding need separate evidence.",
        ],
        fleet_unit_price_usd_m=unit_price,
        non_revenue_mileage_allowance_fraction=reserve,
        cases=cases,
        complete_opening_cost_usd_m=None,
    )
    sensitivity["evaluation_id"] = system._id(sensitivity)
    return sensitivity


def procurement_sensitivity(cfg, service, trial, receipt):
    with ZipFile(PROTOTYPE_PACKET) as packet:
        manifest = json.loads(packet.read("manifest.json"))
        members = {}
        for name in ("opening.json", "opening-bom.csv", "service.json"):
            raw = packet.read(name)
            if sha256(raw).hexdigest() != manifest["sha256"][name]:
                raise ValueError(f"Airport prototype member changed: {name}")
            members[name] = raw
    reference = json.loads(members["opening.json"])
    archived_service = json.loads(members["service.json"])
    estimate = json.loads(PROCUREMENT_ESTIMATE.read_bytes())
    if (reference["candidate_id"] != manifest["candidate_id"]
            or reference["bundle"]["grid_sites"] != 30
            or archived_service["evaluation_id"] != service["evaluation_id"]
            or estimate["candidate_id"] != reference["candidate_id"]
            or estimate["opening_evaluation_id"] != reference["evaluation_id"]):
        raise ValueError("Procurement sensitivity requires the matching 30-site Airport service and BOM")
    direct = {
        "Fleet, including spare sets" if lot["lot_id"] == "fleet" else lot["lot_id"]: lot["base_usd"] / 1e6
        for lot in estimate["lots"] if lot["inclusion_group"] == "opening-direct"
    }
    scopes = airport_opening.allowances(direct, cfg["capital_rates_usd_m"])
    if abs(sum(scopes.values()) - estimate["subtotal_opening_priced_allowances"]["base_usd"] / 1e6) > 1e-6:
        raise ValueError("Procurement sensitivity capital must reconcile to the published buyer estimate")
    fixed_bom_rows = {}
    for row in csv.DictReader(members["opening-bom.csv"].decode().splitlines()):
        if row["scope"] == "opening works and equipment" and row["item"] != "onboard_contact_sets":
            fixed_bom_rows[row["item"]] = None if not row["opening_quantity"] else {
                "quantity": float(row["opening_quantity"]), "unit": row["unit"],
            }
    projected = {
        **reference["bundle"],
        "parent": reference["candidate_id"],
        "active_sets": trial["group"]["diagrammed_sets"],
    }
    sensitivity = airport_cost_sensitivity(
        cfg, {**reference, "scopes_usd_m": scopes}, archived_service, trial, system._id(projected), receipt
    )
    sensitivity.update(
        source_packet_candidate_id=reference["candidate_id"],
        source_packet_evaluation_id=manifest["evaluation_id"],
        source_packet_member_sha256={name: manifest["sha256"][name] for name in members},
        source_estimate_evaluation_id=estimate["evaluation_id"],
        fixed_opening_bom=fixed_bom_rows,
        projected_bundle=projected,
        requalified_feeder=False,
        freight_return=None,
    )
    sensitivity.pop("evaluation_id")
    sensitivity["evaluation_id"] = system._id(sensitivity)
    return sensitivity


def compare(cfg, report, selected):
    urban = urban_opening.urban_comparison(cfg, report)
    airport = report["networks"]["first"]["groups"]["Airport"]
    trial = lower_frequency(cfg, airport)
    airport_opening.validate_parent(cfg, report["networks"]["first"], selected)
    fleet = trial["group"]["diagrammed_sets"] + 3
    trial_candidate = system._id({
        "parent": urban["airport"]["candidate_id"],
        "formation": cfg["vehicle"]["cars_per_train"],
        "fleet_sets": fleet,
        "stops": [stop["id"] for stop in airport["outward_stops"]],
        "terminal_layout": "one face and one shared throat per end, Airport depot",
        "supply": "protected_conductor",
        "feed_site_count": None,
    })
    try:
        lower = airport_opening.calculate(inputs=(cfg, report, selected), service=trial)
    except ValueError as error:
        if str(error) != "Estimated payroll exceeds the Non-energy train operations budget":
            raise
        lower = None
        price_hold = str(error)
    else:
        price_hold = None
    capacity = trial["scheduled_places_per_hour_direction"]
    places = cfg["vehicle"]["normal_places_per_train"]
    service_days = cfg["vehicle"]["service_days_per_year"]
    annual_passenger_train_km = trial["group"]["scheduled_trips"] * airport["one_way_km"] * service_days
    receipt = urban["net_receipt_usd_per_paid_journey"]
    reference_service = airport_service.build_service(cfg, airport)
    reference_opening = airport_opening.calculate(inputs=(cfg, report, selected), service=reference_service)
    sensitivity = airport_cost_sensitivity(
        cfg, reference_opening, reference_service, trial, lower["candidate_id"] if lower else trial_candidate, receipt
    )
    common_opex = sum(lower["annual_opex_usd_m"].values()) if lower else None
    lower_metrics = dict(
        group_name="Airport",
        candidate_id=lower["candidate_id"] if lower else trial_candidate,
        evaluation_id=lower["evaluation_id"] if lower else None,
        service_evaluation_id=trial["evaluation_id"],
        route_km=airport["one_way_km"],
        station_count=len(airport["outward_stops"]),
        active_sets=trial["group"]["diagrammed_sets"],
        fleet_sets=fleet,
        scheduled_trips_day=trial["group"]["scheduled_trips"],
        hourly_departures_per_direction=trial["hourly"],
        annual_passenger_service_train_km=annual_passenger_train_km,
        annual_empty_train_km_allowance=trial["non_revenue_km_per_day"] * service_days,
        annual_place_km=annual_passenger_train_km * places,
        normal_places_hour_direction=capacity,
        capital_usd_m=sum(lower["scopes_usd_m"].values()) if lower else None,
        annual_opex_usd_m=common_opex,
        paid_journeys_day_to_cover_common_opex=common_opex * 1e6 / (service_days * receipt)
            if common_opex is not None else None,
        terminal_and_block_screen=trial["terminal"]["schedule_screen_passed"],
        terminal_conflicts=trial["terminal"]["conflicts"],
        power_evaluation_id=lower["power"]["evaluation_id"] if lower else None,
        grid_sites=lower["bundle"]["grid_sites"] if lower else None,
        price_hold=price_hold,
    )
    demand_levels = (700, 1400, 2100)
    cases = {}
    for key, row in (("airport_15_minute", urban["airport"]),
                     ("airport_30_minute_trial", lower_metrics), ("urban_15_minute", urban["urban"])):
        capacity = row["normal_places_hour_direction"]
        cases[key] = {
            **{field: row[field] for field in lower_metrics
               if field in row},
            "nominal_headway_min": 60 / max(row["hourly_departures_per_direction"]),
            "capital_usd_per_offered_peak_place_hour": row["capital_usd_m"] * 1e6 / capacity
                if row["capital_usd_m"] is not None else None,
            "annual_opex_usd_per_offered_place_km": row["annual_opex_usd_m"] * 1e6 / row["annual_place_km"]
                if row["annual_opex_usd_m"] is not None else None,
            "illustrative_peak_load_cases": [
                {"assumed_passengers_hour_direction": demand,
                 "offered_load_fraction": demand / capacity,
                 "remaining_places_hour_direction": capacity - demand}
                for demand in demand_levels
            ],
            "observed_paid_journeys_day": None,
            "observed_peak_directional_load": None,
            "operating_authorisation": False,
        }
    value = dict(
        policy="Compare frequent service and lower frequency using the same six-car formation and planning rate family.",
        comparison_cost_basis={
            "airport_and_urban_15_minute": urban["comparator_basis"],
            "airport_30_minute_trial": (
                "Attempted comparison on the common three-site planning allowance. "
                "Pricing requires a reconciled fixed operating roster and a route-specific feeder review."
            ),
        },
        timetable_parent_id=report["evaluation_id"],
        urban_comparison_evaluation_id=urban["evaluation_id"],
        urban_survey_priority_basis=urban["selection_purpose"],
        demand_basis="Illustrative peak onboard directional load scenarios. Obtain local surveys and fare-paying counts.",
        net_receipt_usd_per_paid_journey=receipt,
        cases=cases,
        airport_cost_sensitivity=sensitivity,
        airport_procurement_cost_sensitivity=procurement_sensitivity(cfg, reference_service, trial, receipt),
        physical_readiness=False,
        investment_rankable=False,
        source_sha256={**urban["source_sha256"], **reference_opening["sources"], **(lower["sources"] if lower else {}),
                       **trial["source_sha256"],
                       "docs/operator-review/delivery/calculate.py":
                           digest(system.ROOT / "docs/operator-review/delivery/calculate.py"),
                       "cities/Baghdad/service-diagrams.json":
                           digest(system.ROOT / "cities/Baghdad/service-diagrams.json"),
                       str(PROTOTYPE_PACKET.relative_to(system.ROOT)): digest(PROTOTYPE_PACKET),
                       str(PROCUREMENT_ESTIMATE.relative_to(system.ROOT)): digest(PROCUREMENT_ESTIMATE)},
    )
    value["evaluation_id"] = system._id(value)
    return value


if __name__ == "__main__":
    print(json.dumps(compare(*airport_opening.opening_inputs()), indent=2, allow_nan=False))
