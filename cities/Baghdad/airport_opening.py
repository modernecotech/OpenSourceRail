"""Price the named Airport corridor from its train workings and independent opening assets."""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from math import ceil, pi
from pathlib import Path
import runpy
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.outline import baghdad_diagrams as diagrams, baghdad_system as system
from engineering.outline.baghdad_power import PowerAssumptions, PowerNetwork, compare_power
from engineering.outline.baghdad_viaduct import PlanningRates, evaluate as civil_evaluate
from cities.Baghdad.iraq_power import rates as iraq_power_rates

CITY = Path(__file__).resolve().parent
GUIDE = CITY / "AIRPORT-OPENING.md"
SITE_INPUT = CITY / "airport-works.toml"
MARKET_INPUT = CITY / "iraq-market.toml"
WORKFORCE_SOURCE = ROOT / "docs/operator-review/delivery/calculate.py"


def allowances(direct_rows, rates):
    direct = sum(direct_rows.values())
    design = direct * rates["design_fraction"]
    test = direct * rates["testing_fraction"]
    allowance = (direct + design + test) * rates["project_allowance_fraction"]
    return {**direct_rows, "Design and assurance": design, "Testing and commissioning": test,
            "Project allowance": allowance}


def validate_parent(cfg, diagram, selected):
    if (cfg["selected_span_m"] != 10 or cfg["selected_pier_family"] != "separate-track"
            or cfg["preferred_supply"] != "protected-conductor" or cfg["track_count"] != 2
            or selected["selected_digital_civil_family"] != "10m-separate"
            or selected["power_cases"]["protected_conductor"]["physical_candidate_id"] != selected["selected_candidate_id"]
            or diagram["selected_candidate_id"] != selected["selected_candidate_id"]
            or diagram["selected_system_evaluation_id"] != selected["selected_evaluation_id"]):
        raise ValueError("Airport opening requires the matching 10 m separate-track, protected-conductor parent")


def iraq_site_estimate(direct, rates, works, route, grid_sites):
    inputs = tomllib.loads(SITE_INPUT.read_text(encoding="utf-8"))
    fx = tomllib.loads(MARKET_INPUT.read_text(encoding="utf-8"))["currency"]
    ground, material = inputs["ground"], inputs["materials"]
    street, rail, site, haul = (inputs[key] for key in ("corridor", "rail", "site", "logistics"))
    quantities, delivery = works["quantities"], works["delivery"]
    yard_months = delivery["factory_yards_needed_at_declared_rate"] * delivery["target_years"] * 12
    material_iqd_m3 = (ground["cement_t_per_m3"] * material["resistant_cement_iqd_t"]
                       + ground["rebar_t_per_m3"] * material["reinforcing_steel_iqd_t"]
                       + ground["sand_m3_per_m3"] * material["sand_iqd_m3"]
                       + ground["gravel_m3_per_m3"] * material["crushed_gravel_iqd_m3"])
    road_iqd_km = street["comparator_iqd"] / street["comparator_km"]
    renewal_iqd_km = rail["renewal_estimate_usd"] / rail["renewal_km"] * fx["iqd_per_usd"]
    site_credit = direct["Land, utilities and disruption"]
    scenarios = {}
    for i, label in enumerate(("low", "base", "high")):
        n_supports = ceil(quantities["pier_foundation_count"] * ground["affected_support_share"][i])
        shaft_m3 = (n_supports * ground["piles_per_affected_support"] * pi / 4
                    * ground["diameter_m"]**2 * ground["bored_length_m"][i])
        items = [
            ("Land, utility conflicts and traffic reinstatement", "route-km", route,
             road_iqd_km * street["corridor_share_of_road_rate"][i]),
            ("Terminal and depot turnout premiums", "turnouts", rail["turnouts"][i], rail["turnout_premium_iqd"][i]),
            ("Extra depot lead and refuge track", "track-km", rail["extra_track_km"][i],
             renewal_iqd_km * rail["lead_factor_on_renewal"][i]),
            ("Landside airport forecourt and security interface", "forecourt", 1, site["airport_forecourt_iqd"][i]),
            ("Offsite distribution feeders and tie-ins", "sites", grid_sites, site["offsite_grid_iqd_per_site"][i]),
            ("Additional foundation shafts under standard caps", "shaft m³", shaft_m3,
             material_iqd_m3 * ground["installed_to_material_factor"][i]),
            ("Exceptional road-crossing works", "crossings", site["exceptional_road_crossings"][i], site["extra_crossing_iqd"][i]),
            ("Incremental yard premises and temporary access", "yard-months", yard_months, haul["extra_yard_iqd_per_month"][i]),
            ("Extra beam haul above standard delivery", "load-km", quantities["beam_count"] * haul["extra_km_per_beam"][i],
             haul["haul_iqd_per_extra_km"][i]),
        ]
        rows = {name: {"unit": unit, "quantity": qty, "unit_iqd": price,
                       "direct_usd_m": qty * price / fx["iqd_per_usd"] / 1e6} for name, unit, qty, price in items}
        local_direct = sum(row["direct_usd_m"] for row in rows.values())
        revised = dict(direct)
        del revised["Land, utilities and disruption"]
        revised.update({name: row["direct_usd_m"] for name, row in rows.items()})
        ledger = allowances(revised, rates)
        scenarios[label] = {"items": rows, "affected_supports": n_supports, "direct_site_usd_m": local_direct,
                            "direct_change_usd_m": local_direct - site_credit, "scopes_usd_m": ledger,
                            "capital_usd_m": sum(ledger.values())}
    return {"iqd_per_usd": fx["iqd_per_usd"], "currency_source": fx["source"],
            "credited_land_utilities_usd_m": site_credit, "pile_material_iqd_m3": material_iqd_m3,
            "inputs": inputs, "scenarios": scenarios}


def airport_operations(cfg, group, bundle, power, opex, site_inputs, market, *, demand_reference_trips, positioning_km_day=0):
    staff = runpy.run_path(str(WORKFORCE_SOURCE))
    stops, route = group["outward_stops"], group["one_way_km"]
    trips = group["scheduled_trips"]
    days = cfg["vehicle"]["service_days_per_year"]
    hours = cfg["vehicle"]["service_hours_per_day"]
    km_year = trips * days * route
    grid_gwh = power["energy"]["annual_grid_gwh"]
    hourly = cfg["service_plan"]["departures_per_hour_direction"]
    if trips != 2 * sum(hourly) or km_year != power["common_service"]["annual_train_km"]:
        raise ValueError("Airport roster and energy must use the same two-direction train workings")
    train_hours_day = trips * (group["one_way_s_including_dwell"] + group["minimum_turn_s"]) / 3600
    roster = staff["roster"](len(stops), bundle["control_centres"], bundle["depots"], route, bundle["active_sets"], hourly)
    work = staff["workforce_scenarios"](roster, train_hours_day, "Timed Airport trips and minimum turnbacks.")
    ledger = staff["opex_ledger"](sum(opex.values()), {"Non-energy train operations": opex["train_operations"],
                                 "Station operations": opex["station_operations"], "Power maintenance": opex["line_upkeep"]})
    wages = staff["iraq_payroll"]({"workforce_scenarios": work, "opex": ledger}, market["currency"])
    # Same boardings per eligible call, uniform choice among remaining local stops.
    distances = [route * s["fraction"] for s in stops]
    local = distances[1:]
    mean_local_km = sum(sum(abs(x - y) for y in direction[i+1:]) / len(direction[i+1:])
                        for direction in (local, local[::-1]) for i, x in enumerate(direction[:-1])) / (2 * (len(local) - 1))
    mean_airport_km = sum(local) / len(local)
    energy_rates = iraq_power_rates()
    cases = {}
    for i, (name, cost) in enumerate((("downside", "high"), ("central", "base"), ("upside", "low"))):
        j = 2 - i
        wage = wages["cases"][cost]
        positions = site_inputs["additional_airport_interface_posts_on_duty"][j]
        additional_fte = ceil(positions * hours * days / 1720)
        extra_pay = additional_fte * wage["loaded_usd_per_fte_year"]["station duty and passenger assistance"] / 1e6
        # Include every diagrammed empty trip within the allowance. The remainder
        # covers yard and maintenance moves pending a surveyed depot layout.
        deadhead_fraction = max(positioning_km_day * days / km_year, site_inputs["non_revenue_distance_share"][j])
        grid_price = energy_rates[cost]["delivered_usd_per_kwh"]
        energy_bill = grid_gwh * (1 + deadhead_fraction) * grid_price
        train_nonlabour = opex["train_operations"] - wages["estimated_credit_by_envelope_usd_m_year"]["Non-energy train operations"]
        deadhead_nonenergy = train_nonlabour * deadhead_fraction
        total = (wage["goa4"]["annual_opex_usd_m_year"] - opex["electricity"] + energy_bill
                 + extra_pay + deadhead_nonenergy)
        air = site_inputs["air_passenger_movements_2024"] * site_inputs["rail_share_of_air_passengers"][i]
        employees = days * site_inputs["airport_employee_and_visitor_one_way_journeys_per_day"][i]
        residents = demand_reference_trips * days * (len(local) - 1) * site_inputs["local_boardings_per_eligible_train_call"][i]
        journeys = air + employees + residents
        passenger_km = mean_airport_km * (air + employees) + mean_local_km * residents
        paid = journeys * market["demand"]["paying_share_of_linked_journeys"]
        posted = market["fare"]["posted_iqd"][i]
        receipts = paid * posted * market["fare"]["receipt_fraction"][i] / market["currency"]["iqd_per_usd"] / 1e6
        cases[name] = {"total_fte": work["goa4"]["total_fte"] + additional_fte, "airport_liaison_fte": additional_fte,
                       "payroll_usd_m": wage["goa4"]["payroll_usd_m_year"] + extra_pay,
                       "embedded_credit_usd_m": wage["goa4"]["embedded_credit_usd_m_year"],
                       "non_revenue_train_km": km_year * deadhead_fraction,
                       "non_revenue_non_energy_usd_m": deadhead_nonenergy, "total_grid_gwh": grid_gwh * (1 + deadhead_fraction),
                       "tariff_iqd_kwh": energy_rates[cost]["delivered_iqd_per_kwh"], "electricity_usd_m": energy_bill,
                       "air_journeys": air, "airport_workers_and_visitors": employees, "local_journeys": residents,
                       "all_journeys": journeys, "paid_journeys": paid, "mean_trip_km": passenger_km / journeys,
                       "occupancy": passenger_km / (km_year * cfg["vehicle"]["normal_places_per_train"]),
                       "posted_iqd": posted, "net_farebox_usd_m": receipts, "opex_usd_m": total,
                       "annual_operating_support_usd_m": total - receipts}
    return {"goa4_posts": work["goa4"]["posts_fte"], "train_hours_day": train_hours_day,
            "local_trip_km": mean_local_km, "airport_trip_km": mean_airport_km,
            "estimated_credit_by_envelope_usd_m_year": wages["estimated_credit_by_envelope_usd_m_year"],
            "cases": cases}


def opening_inputs():
    # Verify the published timetable's method and source chain before reuse.
    # Rebuilding all three networks for a six-stop costing took most of its time.
    from cities.Baghdad.engineering.mechanical.compare_returns import verified_record

    cfg = system.load(network="first")
    report = json.loads(diagrams.PUBLICATION.read_bytes())
    timetable_id = report.pop("evaluation_id")
    if system._id({"data": report, "method": sha256(Path(diagrams.__file__).read_bytes()).hexdigest()}) != timetable_id:
        raise ValueError("Refresh the published service workings first")
    report["evaluation_id"] = timetable_id
    system_record = verified_record(CITY / "system-results.json", ROOT)
    review = CITY / "maps/corridor-review.geojson"
    verified_record(review, ROOT)
    register = json.loads((CITY / "station-register.json").read_bytes())
    register_id = register.pop("evaluation_id")
    if (system._id(register) != register_id
            or system._id({k: v for k, v in system_record.items() if k != "evaluation_id"}) != system_record["evaluation_id"]
            or report["source_system_evaluation_id"] != system_record["evaluation_id"]
            or report["corridor_review_sha256"] != sha256(review.read_bytes()).hexdigest()
            or register_id != system_record["station_register"]["evaluation_id"]):
        raise ValueError("Refresh the Airport timetable and source station register")
    return cfg, report, system_record["networks"]["first"]


def common_opening_cost(cfg, works, power, route, fleet, station_count, grid_sites, annual_km):
    """Price one standalone corridor with one dedicated depot and control centre."""
    track = route * cfg["track_count"]
    n = {"fleet_trainsets": fleet, "stations": station_count, "route_km": route,
         "traction_supply_sites": grid_sites, "control_centres": 1}
    power_price = system._power_cost(power, cfg, n)
    r = cfg["capital_rates_usd_m"]
    direct = {
        "Viaduct, piers and foundations": works["prices"]["changed_elevated_scope_usd"]/1e6,
        ("Six station shells and accessible approaches" if station_count == 6 else "Station shells and accessible approaches"): station_count * r["station"],
        "Track and walkways": track * r["track_and_walkway_per_track_km"],
        "Signalling and communications": route * r["signalling_per_route_km"],
        "Wayside braking and recovery": route * r["wayside_brake_and_rescue_per_route_km"],
        "Protected conductor and switchgear": power_price["line_usd_m"],
        "Grid supply sites": power_price["grid_and_charging_usd_m"],
        "Fleet, including spare sets": power_price["fleet_usd_m"],
        "Depot and control centre": r["depot"] + r["control_centre"],
        "Land, utilities and disruption": route * r["land_utilities_disruption_per_route_km"],
        "Fixed production setup and route tooling": r["tooling_and_recovery_fixed"] + route*r["tooling_and_recovery_per_route_km"]}
    op = cfg["operation_rates"]
    opex = {"station_operations": station_count * op["station_operations_usd_m_per_year"],
            "train_operations": annual_km * op["non_energy_vehicle_operations_usd_per_train_km"]/1e6,
            "electricity": power["energy"]["annual_grid_gwh"] * op["delivered_energy_usd_per_kwh"],
            "line_upkeep": track * cfg["annual_power_maintenance_usd_m"]["protected_conductor_per_track_km"]}
    return direct, opex, power_price


def apply_feeder_quantities(power, feeder, assumptions):
    supply = power["supply"]
    q = feeder["procurement"]
    sections = q["feed_half_bays"]
    if (supply["grid_sites"] != feeder["grid_sites"] or sections < 1
            or q["dc_outgoing_breaker_circuits"] != sections):
        raise ValueError("Feed paths and priced switchgear must use the same topology")
    # Preserve the comparison result in ancestry and carry the engineered DC peak
    # through site price and replacement. Utility AC conversion remains a quote item.
    parent_eval = power["evaluation_id"]
    supply["uniform_share_site_mw"] = supply["provisional_grid_site_rating_mw"]
    supply["provisional_grid_site_rating_mw"] = max(supply["uniform_share_site_mw"], q["minimum_site_peak_dc_mw"])
    supply["powered_section_count"] = sections
    power["maintenance_quantities"]["powered_section_count"] = sections
    screen = power["traction"]["electrical_screen"]
    screen.update(powered_section_count=sections, mean_powered_section_length_km=supply["line_power_track_km"]/sections)
    for event in power["renewal_events"]:
        if event["component"] == "line_section_protection":
            event["quantity"] = sections * assumptions.power_electronics_renewal_fraction_year_15
    power["parent_evaluation_id"] = parent_eval
    power["feeder_design_id"] = feeder["design_id"]
    power["evaluation_id"] = system._id({"parent": parent_eval, "feeder": feeder["design_id"], "supply": supply})


def calculate(*, inputs=None, service=None, size_feeder=False, loaded_mass_t=None,
              vehicle_revision=None, mass_basis_id=None):
    cfg, report, selected = inputs or opening_inputs()
    grid_sites = 3
    diagram = report["networks"]["first"]
    validate_parent(cfg, diagram, selected)
    reference_group = diagram["groups"]["Airport"]
    group = service["group"] if service else reference_group
    if service:
        cfg = {**cfg, "vehicle": {**cfg["vehicle"], "peak_headway_s": service["peak_headway_s"]},
               "service_plan": {**cfg["service_plan"], "departures_per_hour_direction": service["hourly"]}}
    stops = group["outward_stops"]
    v = cfg["vehicle"]
    route = group["one_way_km"]
    active = group["diagrammed_sets"]
    spares = 3  # one workshop, one inspection and one ready spare, independently priced
    fleet = active + spares
    km_year = route * group["scheduled_trips"] * v["service_days_per_year"]
    parent = report["networks"]["first"]["selected_candidate_id"]
    bundle = {"parent": parent, "service_group": "Airport", "route_km": route,
              "stops": [s["id"] for s in stops], "active_sets": active, "spares": spares,
              "depots": 1, "control_centres": 1, "grid_sites": grid_sites,
              "supply": "protected_conductor", "span_m": cfg["selected_span_m"],
              "pier_family": cfg["selected_pier_family"]}
    if service:
        bundle["formation_cars"] = v["cars_per_train"]
        bundle["vehicle_revision"] = vehicle_revision
        bundle["terminal_layout"] = {key: service["terminal"][key] for key in (
            "open_platform_faces_each_end", "common_throats_each_end", "yard_track_km_assumed", "depot_end")}
    if mass_basis_id:
        bundle["installed_mass_return"] = mass_basis_id
    candidate = system._id(bundle)
    network = PowerNetwork(
        candidate_id=candidate, route_km=route, normal_places_per_train=v["normal_places_per_train"],
        station_count=len(stops), line_count=1, active_trainsets=active, fleet_trainsets=fleet,
        grid_site_count=grid_sites, annual_train_km=km_year, train_mass_t=v["crowd_mass_t_per_train_before_supply"],
        train_energy_kwh_per_km=v["energy_kwh_per_train_km_overhead_comparator"],
        peak_headway_s=v["peak_headway_s"], dwell_s=v["dwell_s"], speed_cap_m_s=v["speed_cap_kmh"]/3.6,
        service_hours_per_day=v["service_hours_per_day"], service_days_per_year=v["service_days_per_year"])
    assumptions = PowerAssumptions(**cfg["power_assumptions"])
    if loaded_mass_t is not None:
        # The network input is referenced to the overhead comparator.
        delta = compare_power(network, assumptions)["protected_conductor"]["vehicle"]["delta_from_overhead_comparator_t"]
        new_comparator_mass = loaded_mass_t - delta
        adjusted_energy = network.train_energy_kwh_per_km + (
            new_comparator_mass - network.train_mass_t) * assumptions.incremental_energy_kwh_per_km_per_t
        network = replace(network, train_mass_t=new_comparator_mass, train_energy_kwh_per_km=adjusted_energy)
    power = compare_power(network, assumptions)["protected_conductor"]
    feeder = None
    if size_feeder:
        from cities.Baghdad.airport_supply import bind_supply, build_supply
        feeder = build_supply(service, power, route)
        if feeder["grid_sites"] is None:
            raise ValueError("No priceable supply design for this train load: " + feeder["status"])
        grid_sites = feeder["grid_sites"]
        bundle.update(grid_sites=grid_sites, feeder_design_id=feeder["design_id"])
        candidate = system._id(bundle)
        network = replace(network, candidate_id=candidate, grid_site_count=grid_sites)
        power = compare_power(network, assumptions)["protected_conductor"]
        apply_feeder_quantities(power, feeder, assumptions)
        feeder = bind_supply(feeder, service, power, route)
    works = civil_evaluate({"Airport": route}, span_m=bundle["span_m"], common_pier=False,
                           physical_candidate_id=power["physical_candidate_id"], rates=PlanningRates(**cfg["civil_rates"]),
                           train_crowd_mass_t=power["vehicle"]["mass_t"], target_years=2, civil_start_year=1)
    r = cfg["capital_rates_usd_m"]
    direct, opex, power_price = common_opening_cost(cfg, works, power, route, fleet, len(stops), grid_sites, km_year)
    n = {"fleet_trainsets": fleet, "stations": len(stops), "route_km": route,
         "traction_supply_sites": grid_sites, "control_centres": bundle["control_centres"]}
    control_budgets = dict(vehicles=direct["Fleet, including spare sets"],
                           stations_access=direct["Six station shells and accessible approaches"],
                           signalling_comms=direct["Signalling and communications"],
                           grid_charging_buffers=direct["Grid supply sites"],
                           depots_control=direct["Depot and control centre"])
    controls = system._control_electronics(cfg, n, power, control_budgets)
    if feeder:
        # Budget the normally open ties at a provisional section-equipment rate.
        # Outgoing breakers are already in the section count above.
        tie_cost = feeder["procurement"]["normally_open_track_ties"] * power_price["section_unit_usd_m"]
        direct["Protected conductor and switchgear"] += tie_cost
    scope = allowances(direct, r)
    op = cfg["operation_rates"]
    # Compare returns on the same basis. Remove only the identified host scopes;
    # price all changes, transfer and reinstatement before applying allowances.
    base_with_host_assets_replaced = {key: value for key, value in direct.items()
                                      if key not in ("Depot and control centre", "Grid supply sites")}
    alternative_base = sum(allowances(base_with_host_assets_replaced, r).values())
    facility_options = {
        "dedicated": {"new_grid_sites": grid_sites, "new_depots": 1, "new_control_centres": 1,
                      "direct_reference_price_usd_m": direct["Depot and control centre"] + direct["Grid supply sites"]},
        "shared_or_temporary": {"supply_feed_points_required": grid_sites, "servicing_bases_required": 1,
                                "control_rooms_required": 1, "matched_return_direct_usd_m": None,
                                "priced_other_scope_with_allowances_usd_m": alternative_base,
                                "direct_price_multiplier": (1 + r["design_fraction"] + r["testing_fraction"])
                                                           * (1 + r["project_allowance_fraction"])}}
    iraq = iraq_site_estimate(direct, r, works, route, grid_sites)
    market = tomllib.loads(MARKET_INPUT.read_text(encoding="utf-8"))
    annual = airport_operations(cfg, group, bundle, power, opex, iraq["inputs"]["operations"], market,
                                demand_reference_trips=reference_group["scheduled_trips"],
                                positioning_km_day=service["non_revenue_km_per_day"] if service else 0)
    renewal = [{"year": event["year"], "component": event["component"],
                "usd_m": system._renewal_cost(event, power, cfg, power_price)}
               for event in power["renewal_events"]]
    renewal.extend([
        {"year": 15, "component": "common_signalling_and_brake", "usd_m": (
            direct["Signalling and communications"] + direct["Wayside braking and recovery"]) * op["year_15_common_systems_replacement_fraction"]},
        {"year": 25, "component": "fleet_major_renewal", "usd_m": direct["Fleet, including spare sets"] * op["year_25_fleet_replacement_fraction"]}])
    if feeder:
        balance = iraq["inputs"]["feeder_upkeep"]
        base_grid_allowance = 3 * r["traction_supply_site"]
        added_equipment = (direct["Grid supply sites"] - base_grid_allowance + tie_cost
                           + max(0, power["supply"]["powered_section_count"] - 2 * (len(stops)-1)) * power_price["section_unit_usd_m"])
        renewal.append({"year": 15, "component": "midpoint_tie_equipment",
                        "usd_m": tie_cost * assumptions.power_electronics_renewal_fraction_year_15})
        for key, row in annual["cases"].items():
            extra = added_equipment * balance[key]
            row["incremental_site_and_switch_upkeep_usd_m"] = extra
            row["opex_usd_m"] += extra
            row["annual_operating_support_usd_m"] += extra
    sources = [Path(__file__).resolve(), SITE_INPUT, WORKFORCE_SOURCE, diagrams.PUBLICATION, CITY/"system.toml",
               CITY/"system-results.json", CITY/"iraq-power.toml", CITY/"iraq_power.py",
               ROOT/"engineering/outline/baghdad_system.py", ROOT/"engineering/outline/baghdad_power.py",
               ROOT/"engineering/outline/baghdad_viaduct.py"]
    source_hashes = {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in sources}
    if service:
        source_hashes.update(service["source_sha256"])
    if feeder:
        source_hashes.update(feeder["source_sha256"])
    used_market = {"currency": market["currency"], "fare": market["fare"],
                   "paying_share_of_linked_journeys": market["demand"]["paying_share_of_linked_journeys"]}
    source_hashes["cities/Baghdad/iraq-market.toml#airport_inputs"] = sha256(json.dumps(used_market, sort_keys=True).encode()).hexdigest()
    return {"candidate_id": candidate, "evaluation_id": system._id({"bundle": bundle, "sources": source_hashes, "service": service["evaluation_id"] if service else group, "power": power["evaluation_id"], "feeder": feeder["evaluation_id"] if feeder else None}),
            "timetable_id": report["evaluation_id"], "sources": source_hashes, "parent": parent,
            "bundle": bundle, "train": group, "civil": works["quantities"], "delivery": works["delivery"],
            "power": power, "section_power": feeder, "civil_option_id": works["civil_option_physical_id"],
            "civil_evaluation_id": works["evaluation_id"], "civil_load": works["physical_screen"], "renewals": renewal, "controls": controls["quantities"], "scopes_usd_m": scope, "annual_opex_usd_m": opex,
            "facility_options": facility_options, "iraq_site_estimate": iraq, "iraq_operations": annual,
            "annual_opex_including_all_site_operations_usd_m": None,
            "complete_opening_capital_usd_m": None, "opening_date": None}


def local_works_guide(case):
    iraq = case["iraq_site_estimate"]
    low, base, high = (iraq["scenarios"][key] for key in ("low", "base", "high"))
    inp = iraq["inputs"]
    street, rail, materials = inp["corridor"], inp["rail"], inp["materials"]
    table = []
    for name, row in base["items"].items():
        amounts = [scenario["items"][name]["direct_usd_m"] for scenario in (low, base, high)]
        table.append(f"| {name} | {row['quantity']:,.2f} {row['unit']} | {row['unit_iqd']:,.0f} | "
                     + " | ".join(f"{amount:,.2f}" for amount in amounts) + " |")
    joined = "\n".join(table)
    credit = iraq["credited_land_utilities_usd_m"]
    return f"""## Iraq site works and opening budget

The three cases use the same six stations, 21 trains, depot, control centre and three traction supply sites. The low case assumes accessible public rights of way, short extra haulage and limited ground treatment. The high case allows for more utility and traffic conflicts, deeper foundations, longer leads and more road crossings. These are conditional planning scenarios in constant 2026 money. The operator can replace each quantity and rate when surveys and bids arrive.

| Local work | Base quantity | IQD per base unit | Low USD m | Base USD m | High USD m |
|---|---:|---:|---:|---:|---:|
{joined}
| **Direct site works** | | | **{low['direct_site_usd_m']:.2f}** | **{base['direct_site_usd_m']:.2f}** | **{high['direct_site_usd_m']:.2f}** |
| Deduct generic land, utilities and disruption | | | −{credit:.2f} | −{credit:.2f} | −{credit:.2f} |
| **Net direct change to reference** | | | **{low['direct_change_usd_m']:+.2f}** | **{base['direct_change_usd_m']:+.2f}** | **{high['direct_change_usd_m']:+.2f}** |
| **Opening capital including design, testing and project allowance** | | | **{low['capital_usd_m']:,.1f}** | **{base['capital_usd_m']:,.1f}** | **{high['capital_usd_m']:,.1f}** |

The calculation replaces the entire generic land, utilities and disruption line. Each case applies design, commissioning and contingency once to the revised direct ledger. The other published unit rates carry ordinary access, drainage, track, station approaches, depot equipment, production tooling and erection. The rows above cover additional work at those boundaries. The cost-plan conversion uses **{iraq['iqd_per_usd']:,} IQD/USD**, the Central Bank selling rate to banks from 7 October 2026. [Central Bank of Iraq]({iraq["currency_source"]}) · [Scenario quantities and unit rates](airport-works.toml)

**Land and utilities.** The Ministry of Planning reported about IQD 96bn for the 7 km Baghdad–Wasit entrance contract, including service roads, bridges and widening, and identified water, electricity and property conflicts. We use 10%, 22% and 42% of its historical cost per kilometre as rounded 2026 allowances for the narrower corridor land, diversions and reinstatement scope. Those fractions are engineering judgements. The road figure is carried at face value in IQD. A cadastral schedule and utility owners' estimates would replace it. [Ministry of Planning project report, in Arabic]({street['road_source']})

**Railway and airport.** The World Bank's May 2025 Iraq railway plan estimated USD 33m for 32 km of Al Yussufia–Baghdad track renewal. We use the published USD per kilometre directly with a 1.6–4.0 multiplier for short new track, formation, basic ramp, traction and controls. The low/base/high cases buy 0.40/0.85/1.50 extra track-km beyond the depot fence. Separately allow 5/6/8 point ends, including four for the two terminal crossovers. The turnout premium covers special trackwork, machines and local route proving above plain track and ordinary signalling. Landside works cover the connector to the existing passenger forecourt, managed drop-off and security interface beyond the station entrance. External grid works cover tie-ins upstream of the three priced railway substations. The track length, multipliers and premiums need a surveyed layout and utility connection offers. [World Bank project information document, table 1]({rail['rail_source']})

**Ground and delivery.** October 2026 Iraqi market averages for locally sourced resistant cement, reinforcement, sand and crushed gravel imply IQD {iraq['pile_material_iqd_m3']:,.0f}/m³ for the assumed pile material quantities. The trial rates multiply this by 2.4/3.4/4.6 for boring, casing, batching, installation, testing and contractor overhead. Allow two 1 m diameter shafts below each of {low['affected_supports']}/{base['affected_supports']}/{high['affected_supports']} standard support caps, 18/24/32 m deep. Boreholes must establish the actual founding solution. The reference beam and lift rates cover ordinary production and installation. Add only temporary yard premises, extra loaded-equivalent haul and exceptional road-crossing premiums. The base case carries 12 extra km per beam dispatch, including return-trip cost in the km rate. [Iraq Statistics and GIS Authority, October 2026 construction materials]({materials['source']}) · [10 m span, handling and erection assumptions](engineering/mechanical/civil/SPAN-COMPARISON.md)

The ranges assume a conventional landside terminal and a depot connectable by a short surface lead and ramp. Airport rebuilding, a major river crossing, network-wide grid reinforcement, debt service, escalation after the price date and taxes or duties beyond the unit allowances require separate budgets if triggered. The 1–10% ground-treatment share is an exposure assumption. Widespread piling can exceed the high case."""


def operating_guide(case):
    annual = case["iraq_operations"]
    base = annual["cases"]["central"]
    demand = case["iraq_site_estimate"]["inputs"]["operations"]
    common_posts = sum(annual["goa4_posts"].values())
    rows = []
    for name, row in annual["cases"].items():
        rows.append(f"| {name.title()} | {row['total_fte']} | {row['payroll_usd_m']:.2f} | {row['electricity_usd_m']:.2f} | "
                    f"{row['opex_usd_m']:.2f} | {row['paid_journeys']/1e6:.2f} | {row['posted_iqd']:,} | "
                    f"{row['net_farebox_usd_m']:.2f} | {row['annual_operating_support_usd_m']:.2f} |")
    joined = "\n".join(rows)
    return f"""## Annual operations, passengers and fares

In the central case this service costs **${base['opex_usd_m']:.2f}m/year** to operate. About **{base['paid_journeys']/365:,.0f} paid one-way journeys per day** bring in **${base['net_farebox_usd_m']:.2f}m/year**. The operator needs **${base['annual_operating_support_usd_m']:.2f}m/year** in operating support before capital repayments and renewals. These first-full-year cases combine demand, fare, wage and power-price assumptions. All money columns below use millions of 2026 USD except the posted fare.

| Opening case | Staff FTE | Payroll | Electricity | Total OPEX | Paid trips/year (m) | Posted IQD | Net receipts | Operating support |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{joined}

**Who rides.** Iraq's civil aviation figures count {demand['air_passenger_movements_2024']:,} arrivals and departures at Baghdad International Airport in 2024. Holding that volume constant, assume 5%, 12% or 22% use rail for one ground journey. Add 150, 500 or 1,100 one-way trips per day by airport workers and visitors. For residents travelling solely between the five other stops, assume 2, 5 or 9 boardings per eligible train call. Each of the {case['train']['scheduled_trips']} daily trains makes four calls where a local passenger can board and alight at another non-airport stop. Airline passengers, airport workers and local-only journeys are counted once each. [Iraq air transport statistics, tables 4–5]({demand['air_traffic_source']})

**Trip length and fare.** Assume equal choice among the downstream local stops and equal airport traffic to each of the five other stops. The diagram's planning chainages give mean distances of {annual['local_trip_km']:.1f} km locally and {annual['airport_trip_km']:.1f} km for airport trips. The central mix averages {base['mean_trip_km']:.1f} km and uses {100*base['occupancy']:.2f}% of all scheduled place-km. This low average calls for a pilot count of hourly loads before committing to the full service. With one train per journey, assume 92% pay. At IQD 750 the operator receives IQD 637.5 per paying journey after discounts and collection costs. Count actual airport access, worker shifts and neighbourhood boardings to update the forecast. [Baghdad fare assumptions and local bus comparator](IRAQ-ESTIMATES.md)

**Who operates it.** The dedicated unattended service requires {common_posts} ordinary posts, including station assistance and cleaning, the control room, depot, civil and power response, and administration. The central case adds {base['airport_liaison_fte']} FTE for two airport-interface posts over the operating day. The wage calculation credits ${base['embedded_credit_usd_m']:.3f}m of estimated payroll already in the train, station and line allowances, then adds the local roster once. It prices the airport liaison duties separately from ordinary station duties and construction labour. [Iraqi wage assumptions and roster method](../../docs/operator-review/delivery/README.md)

**Empty trains and power.** Allow 1%, 2.5% or 5% additional empty mileage. Price it at the non-payroll train allowance and the same grid energy per km as scheduled trains, pending a depot plan. The central case draws {base['total_grid_gwh']:.2f} GWh at IQD {base['tariff_iqd_kwh']:.1f}/kWh blended. The local power bill replaces the traction electricity line in the original ${sum(case['annual_opex_usd_m'].values()):.3f}m annual budget. Ordinary station running costs stay in the existing station envelope. Separate airport concession fees, extraordinary security requirements, building metering and renewal schedules need operating agreements. [Iraqi electricity price scenarios](IRAQ-POWER.md) · [Airport demand and empty-mileage inputs](airport-works.toml)"""


def guide(case):
    train, work, p = case["train"], case["civil"], case["power"]
    b, d, s = case["bundle"], case["delivery"], p["supply"]
    scopes = case["scopes_usd_m"]
    alt = case["facility_options"]["shared_or_temporary"]
    table = "\n".join(f"| {k} | {v:,.3f} |" for k, v in scopes.items())
    calls = " → ".join(stop["label"] for stop in train["outward_stops"])
    scenarios = case["iraq_site_estimate"]["scenarios"]
    return f"""# Opening the Baghdad Airport corridor

The Airport service is a 12 km, six-stop opening option within the seven-corridor proposal. The priced planning scope totals **${scenarios['base']['capital_usd_m']:,.1f}m**, with low and high cases of **${scenarios['low']['capital_usd_m']:,.1f}m and ${scenarios['high']['capital_usd_m']:,.1f}m** in 2026 USD. This dedicated opening includes a depot, a control centre, three traction supply sites, terminal trackwork and Iraqi site allowances. Surveyed quantities, supplier prices, committed financing and a funded opening date remain open. The published reference quantities and generic rates total ${sum(scopes.values()):,.3f}m. The railway authority still needs to agree the sites and opening date.

{calls}

{local_works_guide(case)}

## Passenger service and facilities

| Planning quantity | Airport opening assumption |
|---|---:|
| Train workings and fleet | {train["scheduled_trips"]} one-way trips/day, {b["active_sets"]} working sets plus {b["spares"]} spares |
| Annual distance and electricity | {p["common_service"]["annual_train_km"]:,.0f} train-km, {p["energy"]["annual_grid_gwh"]:.2f} GWh |
| Peak service | 700 places per train, 150-second interval, 16,800 places/hour/direction |
| Scheduled outward journey and intermediate dwell | {train["one_way_s_including_dwell"]} seconds including 35 seconds at each intermediate stop |
| Minimum turn and launch stock | {train["minimum_turn_s"]} seconds, {train["sets_starting_at_A_B"][0]} trains at the airport and {train["sets_starting_at_A_B"][1]} at Al Qadisiya for first dispatches |
| Double-track viaduct and supports | {work["beam_count"]:,} ten-metre beams, {work["pier_foundation_count"]:,} separate support positions |
| Conductor, switchgear and controls | {s["protected_conductor_track_km"]:g} track-km, {s["powered_section_count"]} section switches, {case["controls"]["station_dispatch_controllers"]} station controllers |
| Supply and collection | {s["grid_sites"]} sites, {s["provisional_grid_site_rating_mw"]:.2f} MW/site with uniform sharing, {s["train_collection_request_mw"]:.2f} MW/train |
| Operating allowances | ${sum(case["annual_opex_usd_m"].values()):.3f}m/year at the declared timetable and energy rates |

The three spare sets assume one in the workshop, one undergoing inspection and one available for service recovery. The model carries a {p["vehicle"]["mass_t"]:.3f} t crowd-load train. The opening case needs certified mass and a measured brake curve. Grade and adhesion use the first network's planning assumptions. Service runs on protected conductor. Each train carries the independently sized essential-services battery. Deadhead mileage, spare availability, staffing relief, accessible transfers to other lines and depot access require an operator decision.

{operating_guide(case)}

## Published reference quantities and prices

| Scope priced using the Baghdad unit allowances | 2026 USD million |
|---|---:|
{table}
| **Priced scope including allowances** | **{sum(scopes.values()):,.3f}** |

The six named stops each receive one generic accessible station allowance. Each terminus needs at least two simultaneous turnback positions at peak. Keeping all trains at their arrival platforms throughout booked waits would occupy up to {train["platforms_if_linked_sets_wait_in_place"][0]} and {train["platforms_if_linked_sets_wait_in_place"][1]} berths. Ask bidders to price both terminal crossovers, the platform and stabling layout, empty moves, rescue access and depot connection against this service. A procurement drawing must show clearances for the full 104.5 m train. The published between-station block screen needs up to {train["time_based_minimum_blocks_worst_station_pair"]} blocks on the most restrictive pair before braking overlaps or degraded operation.

For a dedicated opening, quote one permanent depot and one permanent control centre for the 21-set fleet. The reference direct price is ${case["facility_options"]["dedicated"]["direct_reference_price_usd_m"]:.1f}m for the depot, control centre and three grid sites together. A buyer comparing another arrangement starts with ${alt["priced_other_scope_with_allowances_usd_m"]:.3f}m of other priced work and adds {alt["direct_price_multiplier"]:.3f} times the matched replacement direct price in millions. For a localised comparison, start with the dedicated Iraq scenario above, deduct the dedicated reference price times the same multiplier, then add the matched host return times that multiplier. Credit any overlapping depot lead or external feeder in the local site rows. Host capacity and annual service fees need separate returns. A shared-site return should identify the host, spare capacity, access tracks, incremental works and service fee. A temporary return should price the interim workshop, stabling, dispatch room, backup supervision, temporary connections, later transfer and removal. Keep each prospective credit conditional on available capacity and the host's agreement. The opening layout tests two end feeds and an intermediate feed. Its uniform-share grid request is lower per site than the request from one train. Check local feed sharing, losses, outages and coincident acceleration before sizing transformers or assigning a supply section. Use the local site-works rows to scope surveys and tenders for access, land rights, feeders, special foundations, yard access and haulage. Financing follows the construction cash schedule.

## Opening sequence

| Release decision | Evidence requested |
|---|---|
| Secure route and sites | Airport operator agrees terminal entrance, locate Um Al Tubol, survey route and station chainage, utilities, street crossings, geotechnics, platform access, depot and grid parcels. |
| Release structures for production | Approved site and load data, beam and pier drawings, accessible station layouts, casting trials, storage and transport permits. In an illustrative two-year civil window, the casting and erection model needs {d["factory_yards_needed_at_declared_rate"]} yard(s) and {d["erection_fronts_needed_at_declared_rate"]} front(s). Ground works, stations and utility approvals can govern progress. |
| Energise and move test trains | Utility agreement and protection settings, isolation and return-current tests, controlled terminal routes, depot access, accepted braking, evacuation and recovery trials. |
| Start passenger service | Commission all six stations and protected routes, train staff, prove timed vehicle availability and emergency cover, demonstrate accessible passenger journeys, secure independent operating acceptance. |

[Train diagrams](SERVICE-DIAGRAMS.md) · [First-network estimate](COST-AND-DELIVERY.md) · [Pricing inputs](system.toml) · [Reproduce the opening quantities](airport_opening.py)

Calculation identity `{case["evaluation_id"]}`. The `--json` export includes the opening candidate, parent and timetable identifiers, source hashes and scope quantities.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    for flag in ("check", "write", "json"):
        actions.add_argument("--" + flag, action="store_true")
    args = parser.parse_args()
    case = calculate()
    if args.json:
        print(json.dumps(case, indent=2, allow_nan=False))
    elif args.write:
        GUIDE.write_text(guide(case), encoding="utf-8")
    elif GUIDE.read_text(encoding="utf-8") != guide(case):
        raise SystemExit("Airport opening guide is stale")


if __name__ == "__main__":
    main()
