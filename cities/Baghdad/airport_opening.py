"""Price the named Airport corridor from its train workings and independent opening assets."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.outline import baghdad_diagrams as diagrams, baghdad_system as system
from engineering.outline.baghdad_power import PowerAssumptions, PowerNetwork, compare_power
from engineering.outline.baghdad_viaduct import PlanningRates, evaluate as civil_evaluate

CITY = Path(__file__).resolve().parent
GUIDE = CITY / "AIRPORT-OPENING.md"


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


def calculate():
    grid_sites = 3  # Test two end feeds and one intermediate feed before locating parcels.
    cfg = system.load()
    report, _ = diagrams.build()
    if json.loads(diagrams.PUBLICATION.read_bytes())["evaluation_id"] != report["evaluation_id"]:
        raise ValueError("Refresh the published service workings first")
    diagram = report["networks"]["first"]
    selected = json.loads((CITY / "system-results.json").read_bytes())["networks"]["first"]
    validate_parent(cfg, diagram, selected)
    group = diagram["groups"]["Airport"]
    stops = group["outward_stops"]
    v = cfg["vehicle"]
    route = group["one_way_km"]
    track = route * cfg["track_count"]
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
    candidate = system._id(bundle)
    network = PowerNetwork(
        candidate_id=candidate, route_km=route, normal_places_per_train=v["normal_places_per_train"],
        station_count=len(stops), line_count=1, active_trainsets=active, fleet_trainsets=fleet,
        grid_site_count=grid_sites, annual_train_km=km_year, train_mass_t=v["crowd_mass_t_per_train_before_supply"],
        train_energy_kwh_per_km=v["energy_kwh_per_train_km_overhead_comparator"],
        peak_headway_s=v["peak_headway_s"], dwell_s=v["dwell_s"], speed_cap_m_s=v["speed_cap_kmh"]/3.6,
        service_hours_per_day=v["service_hours_per_day"], service_days_per_year=v["service_days_per_year"])
    power = compare_power(network, PowerAssumptions(**cfg["power_assumptions"]))["protected_conductor"]
    works = civil_evaluate({"Airport": route}, span_m=bundle["span_m"], common_pier=False,
                           physical_candidate_id=power["physical_candidate_id"], rates=PlanningRates(**cfg["civil_rates"]),
                           train_crowd_mass_t=power["vehicle"]["mass_t"], target_years=2, civil_start_year=1)
    n = {"fleet_trainsets": fleet, "stations": len(stops), "route_km": route,
         "traction_supply_sites": grid_sites, "control_centres": bundle["control_centres"]}
    power_price = system._power_cost(power, cfg, n)
    r = cfg["capital_rates_usd_m"]
    direct = {
        "Viaduct, piers and foundations": works["prices"]["changed_elevated_scope_usd"]/1e6,
        "Six station shells and accessible approaches": len(stops) * r["station"],
        "Track and walkways": track * r["track_and_walkway_per_track_km"],
        "Signalling and communications": route * r["signalling_per_route_km"],
        "Wayside braking and recovery": route * r["wayside_brake_and_rescue_per_route_km"],
        "Protected conductor and switchgear": power_price["line_usd_m"],
        "Grid supply sites": power_price["grid_and_charging_usd_m"],
        "Fleet, including spare sets": power_price["fleet_usd_m"],
        "Depot and control centre": bundle["depots"] * r["depot"] + bundle["control_centres"] * r["control_centre"],
        "Land, utilities and disruption": route * r["land_utilities_disruption_per_route_km"],
        "Fixed production setup and route tooling": r["tooling_and_recovery_fixed"] + route*r["tooling_and_recovery_per_route_km"]}
    control_budgets = dict(vehicles=direct["Fleet, including spare sets"],
                           stations_access=direct["Six station shells and accessible approaches"],
                           signalling_comms=direct["Signalling and communications"],
                           grid_charging_buffers=direct["Grid supply sites"],
                           depots_control=direct["Depot and control centre"])
    controls = system._control_electronics(cfg, n, power, control_budgets)
    scope = allowances(direct, r)
    op = cfg["operation_rates"]
    opex = {"station_operations": len(stops) * op["station_operations_usd_m_per_year"],
            "train_operations": km_year * op["non_energy_vehicle_operations_usd_per_train_km"]/1e6,
            "electricity": power["energy"]["annual_grid_gwh"] * op["delivered_energy_usd_per_kwh"],
            "line_upkeep": track * cfg["annual_power_maintenance_usd_m"]["protected_conductor_per_track_km"]}
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
    sources = [Path(__file__).resolve(), diagrams.PUBLICATION, CITY/"system.toml", CITY/"system-results.json",
               ROOT/"engineering/outline/baghdad_system.py", ROOT/"engineering/outline/baghdad_power.py",
               ROOT/"engineering/outline/baghdad_viaduct.py"]
    source_hashes = {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in sources}
    return {"candidate_id": candidate, "evaluation_id": system._id({"bundle": bundle, "sources": source_hashes}),
            "timetable_id": report["evaluation_id"], "sources": source_hashes, "parent": parent,
            "bundle": bundle, "train": group, "civil": works["quantities"], "delivery": works["delivery"],
            "power": power, "controls": controls["quantities"], "scopes_usd_m": scope, "annual_opex_usd_m": opex,
            "facility_options": facility_options, "annual_opex_including_all_site_operations_usd_m": None,
            "complete_opening_capital_usd_m": None, "opening_date": None}


def guide(case):
    train, work, p = case["train"], case["civil"], case["power"]
    b, d, s = case["bundle"], case["delivery"], p["supply"]
    scopes = case["scopes_usd_m"]
    alt = case["facility_options"]["shared_or_temporary"]
    table = "\n".join(f"| {k} | {v:,.3f} |" for k, v in scopes.items())
    calls = " → ".join(stop["label"] for stop in train["outward_stops"])
    return f"""# Opening the Baghdad Airport corridor

The Airport service is a 12 km, six-stop opening option within the seven-corridor proposal. Its reference quantities price to **${sum(scopes.values()):,.3f}m** in 2026 USD. Three independent traction supply sites, a dedicated depot, a control centre and the full fixed production allowance are included. Terminal trackwork, temporary facilities and site-specific works still need quotations before the buyer has a complete opening cost. No opening date has been established.

{calls}

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

## Purchasing quantities and prices

| Scope priced using the Baghdad unit allowances | 2026 USD million |
|---|---:|
{table}
| **Priced scope including allowances** | **{sum(scopes.values()):,.3f}** |

The six named stops each receive one generic accessible station allowance. Each terminus needs at least two simultaneous turnback positions at peak. Keeping all trains at their arrival platforms throughout booked waits would occupy up to {train["platforms_if_linked_sets_wait_in_place"][0]} and {train["platforms_if_linked_sets_wait_in_place"][1]} berths. Ask bidders to price both terminal crossovers, the platform and stabling layout, empty moves, rescue access and depot connection against this service. A procurement drawing must show clearances for the full 104.5 m train. The published between-station block screen needs up to {train["time_based_minimum_blocks_worst_station_pair"]} blocks on the most restrictive pair before braking overlaps or degraded operation.

For a dedicated opening, quote one permanent depot and one permanent control centre for the 21-set fleet. The reference direct price is ${case["facility_options"]["dedicated"]["direct_reference_price_usd_m"]:.1f}m for the depot, control centre and three grid sites together. A buyer comparing another arrangement starts with ${alt["priced_other_scope_with_allowances_usd_m"]:.3f}m of other priced work and adds {alt["direct_price_multiplier"]:.3f} times the matched replacement direct price in millions. Add the uncovered terminal and site works on the same basis. Host capacity and annual service fees need separate returns. A shared-site return should identify the host, spare capacity, access tracks, incremental works and service fee. A temporary return should price the interim workshop, stabling, dispatch room, backup supervision, temporary connections, later transfer and removal. Keep each prospective credit conditional on available capacity and the host's agreement. The opening layout tests two end feeds and an intermediate feed. Its uniform-share grid request is lower per site than the request from one train. Check local feed sharing, losses, outages and coincident acceleration before sizing transformers or assigning a supply section. Utility reinforcement, power redundancy, airport access/security, exceptional crossings, foundations, land rights, yard mobilisation, unusual haulage and financing each require site scope and prices. The project allowance covers uncertainty on its stated basis.

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
