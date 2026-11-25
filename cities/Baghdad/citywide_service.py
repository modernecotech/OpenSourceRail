"""Select the connected Baghdad citywide planning scope and replay a resource-constrained timetable."""

import argparse
import csv
from hashlib import sha256
import json
from math import isclose
from pathlib import Path
import sys
import tomllib

from cities.Baghdad import airport_opening, citywide_clockface, iraq_budget
from cities.Baghdad.airport_integration import write_atomic
from engineering.outline import baghdad_system as system
from engineering.performance import check_disk_reservation, disk_reservation

CITY = Path(__file__).resolve().parent
ROOT = CITY.parents[1]
GUIDE = CITY / "CITYWIDE-SERVICE.md"
RECORD = CITY / "citywide-service.json"
TRIAL = CITY / "engineering/mechanical/vehicle/section-trial.toml"


def inputs():
    _, timetable, _ = airport_opening.opening_inputs()
    cfg = system.load(network="metropolitan")
    network = json.loads((CITY / "system-results.json").read_bytes())["networks"]["metropolitan"]
    original = timetable["networks"]["metropolitan"]
    mainlines = timetable["citywide_mainline_option"]
    staffing = json.loads(iraq_budget.WORKFORCE.read_bytes())["operating_options"]["metropolitan-mainlines"]
    if (
        network["selected_candidate_id"] != mainlines["infrastructure_candidate_id"]
        or staffing["source_physical_id"] != network["selected_candidate_id"]
        or original["selected_candidate_id"] != network["selected_candidate_id"]
        or network["selected_evaluation_id"] != mainlines["selected_cost_evaluation_id"]
        or staffing["source_evaluation_id"] != network["selected_evaluation_id"]
        or staffing["source_diagram_evaluation_id"] != timetable["evaluation_id"]
    ):
        raise ValueError("The citywide diagram, fleet and operating cost must match the infrastructure")
    groups = original["groups"] | mainlines["mainline_workings"]
    held = original["held_service_group_ids"]
    members = cfg["networks"]["metropolitan"]["service_groups"]
    if (
        set(mainlines["mainline_workings"]) != set(held)
        or set(groups) != set(members)
        or set(mainlines["deferred_sections_costed_km"]) != {s for g in held for s in members[g][1:]}
    ):
        raise ValueError("Each group and each deferred branch needs a disposition")
    return cfg, timetable, network, staffing, groups


def case_costs(staffing, main, km, cases):
    if not isclose(staffing["annual_train_km"], main["annual_diagrammed_train_km"]):
        raise ValueError("Cost rates and train mileage differ")
    ratio = km / staffing["annual_train_km"]
    costs = {}
    for name, case in cases.items():
        allowance = staffing["opex"]["eligible_envelopes_usd_m_year"]["Non-energy train operations"]
        payroll_credit = staffing["iraq_payroll"]["estimated_credit_by_envelope_usd_m_year"][
            "Non-energy train operations"
        ]
        if not allowance >= payroll_credit >= 0:
            raise ValueError("Embedded crew credit exceeds the train allowance")
        variable = allowance - payroll_credit
        fixed = case["opex_m"] - case["power_m"] - variable
        costs[name] = dict(
            retained_costed_investment_usd_m=case["installed_m"],
            published_annual_operations_usd_m=case["opex_m"],
            published_net_fares_usd_m=case["farebox_m"],
            fixed_operations_including_parent_payroll_usd_m=fixed,
            variable_operations_usd_m=ratio * variable,
            energy_usd_m=ratio * case["power_m"],
            priced_annual_operations_usd_m=fixed + ratio * (variable + case["power_m"]),
            incremental_yard_and_junction_capital_usd_m=None,
            incremental_site_upkeep_usd_m=None,
            observed_annual_net_fares_usd_m=None,
            funded_opening_budget_usd_m=None,
        )
    return costs


def build():
    cfg, timetable, n, staffing, groups = inputs()
    original, main = timetable["networks"]["metropolitan"], timetable["citywide_mainline_option"]
    network = cfg["networks"]["metropolitan"]
    mapping = n["map_and_service_coverage"]
    junctions = mapping["access_branch_junction_screen"]["branches"]
    deferred = {
        s: dict(
            group_id=junctions[s]["service_group_id"],
            km=km,
            nearest_main_location=junctions[s]["nearest_main_location"],
            schematic_gap_m=junctions[s]["distance_m"],
        )
        for s, km in main["deferred_sections_costed_km"].items()
    }
    active_km = sum(g["one_way_km"] for g in groups.values())
    reserve = mapping["non_revenue_sections_km"]
    if not isclose(
        active_km + sum(r["km"] for r in deferred.values()) + sum(reserve.values()), n["route_km"]
    ):
        raise ValueError("Main, deferred and reserved sections must account for the full corridor length")
    ordering = {
        g: [s for s in items if s not in deferred] for g, items in sorted(network["service_groups"].items())
    }
    selection = dict(
        infrastructure_candidate_id=n["selected_candidate_id"],
        group_sections=ordering,
        deferred_sections=sorted(deferred),
        reserved_sections=sorted(reserve),
        purpose="Network planning and field enquiry",
    )
    scope_id = system._id(selection)
    level_brake = tomllib.loads(TRIAL.read_text())["braking_deceleration_m_s2"]
    trials = []
    for headway in (900, 1200, 1800):
        trial = citywide_clockface.evaluate(groups, cfg, level_brake, headway)
        trials.append(
            dict(
                headway_s=headway,
                resource_screen_passed=trial["resource_screen_passed"],
                shared_crossing_phase_found=trial["origin_phases_s"] is not None,
                phase_trials=trial["phase_trials"],
                clearance_margins_s=trial["minimum_clearances_s"],
            )
        )
        if trial["resource_screen_passed"]:
            break
    if not trial["resource_screen_passed"]:
        raise ValueError(
            "No working alternative inside the tested grid of departure phases and service rates"
        )
    lines = trial["groups"]
    days, places = cfg["vehicle"]["service_days_per_year"], cfg["vehicle"]["normal_places_per_train"]
    km = sum(g["one_way_km"] * g["departures"] for g in lines.values()) * days
    yard = sum(g["yard_km_day"] for g in lines.values()) * days
    power = n["power_cases"]["protected_conductor"]
    costing = iraq_budget.funding_cases()["metropolitan"]["metropolitan-mainlines"]
    stock = sum(r["sets"] for r in lines.values())
    starts = sum(r["departures"] for r in lines.values())
    if stock > network["active_trainsets"]:
        raise ValueError("Timed trainset demand exceeds the retained fleet")
    layout = dict(
        parent_candidate_id=n["selected_candidate_id"],
        open_sections=ordering,
        merged_platform_markers={"M-075": "M-076"},
        train_length_m=cfg["vehicle_geometry"]["train_length_m"],
        platform_length_m=cfg["station_geometry"]["platform_clear_length_m"],
        terminal_faces_per_direction=[1, 1],
        staging_lead_km=citywide_clockface.YARD_KM,
        approach_throat_length_m=citywide_clockface.THROAT_M,
        staging_positions_by_group_and_origin={
            g: row["start_and_end_sets_by_origin"] for g, row in sorted(lines.items())
        },
    )
    layout_id = system._id(layout)
    selected = dict(
        scope_id=scope_id,
        layout_candidate_id=layout_id,
        service_day=cfg["service_plan"]["start_hour_local"],
        service_hours=cfg["vehicle"]["service_hours_per_day"],
        headway_s=headway,
        origin_phases_s=trial["origin_phases_s"],
        terminal_staging_km=citywide_clockface.YARD_KM,
        patterns={g: row["patterns"] for g, row in sorted(lines.items())},
    )
    originals = {
        g: dict(
            length_km=r["one_way_km"],
            diagrammed_sets=r["diagrammed_sets"],
            worst_block_margin_s=r["worst_block_clearance_margin_s"],
            platform_positions_if_stock_waits=r["platforms_if_linked_sets_wait_in_place"],
        )
        for g, r in sorted(groups.items())
    }
    sources = [
        Path(__file__),
        Path(citywide_clockface.__file__),
        Path(iraq_budget.__file__),
        Path(airport_opening.__file__),
        Path(iraq_budget.capital_estimates.__code__.co_filename),
        Path(iraq_budget.rates.__code__.co_filename),
        Path(system.__file__),
        iraq_budget.WORKFORCE,
        TRIAL,
        *(
            CITY / name
            for name in [
                "system-results.json",
                "system.toml",
                "service-diagrams.json",
                "iraq-capital.toml",
                "iraq-market.toml",
                "iraq-power.toml",
            ]
        ),
    ]
    decision = dict(
        schema="baghdad.citywide-planning-selection.1",
        selection_id=scope_id,
        scope=selection,
        source_system_evaluation_id=n["selected_evaluation_id"],
        source_diagram_evaluation_id=timetable["evaluation_id"],
        costed_route_km=n["route_km"],
        in_service_route_km=active_km,
        reserved_sections_km=reserve,
        deferred=deferred,
        original_unresolved_group_reasons=original["hold_reasons"],
        original_14_group_budget_train_km_year=original["annual_cost_ledger_train_km"],
        original_connected_train_km_year=original["annual_diagrammed_train_km"],
        original_held_train_km_year=original["annual_held_cost_ledger_train_km"],
        deferred_train_km_year=main["annual_train_km_on_deferred_sections"],
        published_peak_offer=dict(
            headway_s=cfg["vehicle"]["peak_headway_s"],
            sets=main["diagrammed_sets"],
            train_km_year=main["annual_diagrammed_train_km"],
            trips_day=main["daily_trips"],
            groups=originals,
            common_annual_opex_usd_m=staffing["opex"]["baseline_usd_m_year"],
            one_block_per_station_pair_screen_passed=all(
                row["worst_block_margin_s"] >= 0 for row in originals.values()
            ),
        ),
        timed_option_id=system._id(selected),
        timed_layout_candidate_id=layout_id,
        timed_layout=layout,
        timetable=trial,
        attempted_schedules=trials,
        vehicle=dict(
            cars=cfg["vehicle"]["cars_per_train"],
            places=places,
            length_m=cfg["vehicle_geometry"]["train_length_m"],
            planning_loaded_mass_t=power["train_crowd_mass_t"],
            weighed_loaded_mass_t=None,
            net_accel_m_s2=cfg["power_assumptions"]["required_net_accel_m_s2"],
            grade_fraction=cfg["power_assumptions"]["adverse_grade"],
            level_brake_m_s2=level_brake,
            dwell_s=cfg["vehicle"]["dwell_s"],
        ),
        demand_and_resources=dict(
            places_hour_direction=places * 3600 // headway,
            service_days_per_year=days,
            first_departure_hour=selected["service_day"],
            departure_hours=selected["service_hours"],
            passenger_trips_day=starts,
            passenger_train_km_year=km,
            yard_train_km_year=yard,
            working_sets=stock,
            budgeted_active_sets=network["active_trainsets"],
            retained_fleet=network["fleet_trainsets"],
            reserve_above_budgeted_active_sets=network["fleet_trainsets"] - network["active_trainsets"],
            terminal_or_ring_direction_faces=2 * len(groups),
            staging_leads=2 * len(groups),
            staging_positions=stock,
            track_km_per_staging_lead=citywide_clockface.YARD_KM,
            budgeted_stations=network["stations"],
            budgeted_depots=network["depots"],
            platform_length_m=cfg["station_geometry"]["platform_clear_length_m"],
            parent_grid_sites=network["traction_supply_sites"],
            traction_charge_ports=power["station_charge_ports"],
            parent_conductor_track_km=power["protected_conductor_track_km"],
            parent_service_battery_kwh=n["selected_service_power"]["nominal_battery_kwh_per_train"],
            section_voltage_and_rescue_replayed=False,
            grid_gwh_km_allowance=(km + yard) * staffing["annual_grid_gwh"] / staffing["annual_train_km"],
        ),
        market=case_costs(staffing, main, km + yard, costing),
        source_sha256={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources},
        owner_adopted=False,
        physical_accepted=False,
        consent_to_fund=False,
    )
    decision["evaluation_id"] = system._id(decision)
    return decision


def return_template(record):
    return {
        "selection_id": record["selection_id"],
        "timed_option_id": record["timed_option_id"],
        "evaluation_id": record["evaluation_id"],
        "line_peak_loads": {g: None for g in record["timetable"]["groups"]},
        "review_documents": dict.fromkeys(
            (
                "accessible_station_sites",
                "interlocking_and_staging",
                "traction_and_rescue",
                "ground_and_utilities",
                "supplier_lots",
                "operating_roster",
                "funding_authority",
            )
        ),
    }


def assess(record, form, directory):
    """Bind local evidence files to this revision; a checksum alone confers no approval."""
    blank = return_template(record)
    if (
        not isinstance(form, dict)
        or form.keys() != blank.keys()
        or any(form[k] != blank[k] for k in ("evaluation_id", "selection_id", "timed_option_id"))
        or any(
            not isinstance(form[k], dict) or form[k].keys() != blank[k].keys()
            for k in ("line_peak_loads", "review_documents")
        )
    ):
        raise ValueError("Use the return form for this exact network, timetable and evaluation")
    directory = Path(directory).resolve()

    def evidence(row):
        path = row.get("file")
        if not isinstance(path, str) or Path(path).is_absolute():
            raise ValueError("Use a relative evidence filename")
        resolved = (directory / path).resolve()
        if (
            not resolved.is_relative_to(directory)
            or not resolved.is_file()
            or sha256(resolved.read_bytes()).hexdigest() != row.get("sha256")
        ):
            raise ValueError("Evidence file or checksum differs")
        return dict(file=path, sha256=row["sha256"])

    loads, docs = {}, {}
    for name, row in form["line_peak_loads"].items():
        if row is None:
            continue
        if not isinstance(row, dict) or row.keys() != {
            "file",
            "sha256",
            "passengers_hour_direction",
            "direction",
            "period_local",
            "load_section",
        }:
            raise ValueError("Identify the measured section, peak hour and direction")
        count = row["passengers_hour_direction"]
        if (
            type(count) is not int
            or count < 0
            or row["direction"] not in ("A_to_B", "B_to_A")
            or any(
                not isinstance(row[k], str) or not row[k].strip() for k in ("period_local", "load_section")
            )
        ):
            raise ValueError("Peak returns need a nonnegative onboard section count over one hour")
        loads[name] = {
            **row,
            **evidence(row),
            "spare_places_hour": record["demand_and_resources"]["places_hour_direction"] - count,
        }
    for name, row in form["review_documents"].items():
        if row is not None:
            if not isinstance(row, dict) or row.keys() != {"file", "sha256"}:
                raise ValueError("Return a local file and its SHA-256")
            docs[name] = evidence(row)
    return dict(
        evaluation_id=record["evaluation_id"],
        seen_loads=loads,
        submitted_documents=docs,
        missing_groups=sorted(form["line_peak_loads"].keys() - loads.keys()),
        missing_review_documents=sorted(form["review_documents"].keys() - docs.keys()),
        field_evidence_authenticated=False,
        owner_adopted=False,
        complete_funded_cost=None,
    )


def render(r):
    net = r["demand_and_resources"]
    v = r["vehicle"]
    t = r["timetable"]
    peak = r["published_peak_offer"]
    c = r["market"]["central"]
    d = r["deferred"]
    rows = [
        "# Baghdad 14-route clockface trial",
        "",
        "The clockface trial diagrams fourteen main routes, including the M05 airport extension. The five access sections below remain deferred and the cost ledger retains every section. The [central passenger access review](CENTRAL-ACCESS.md) measures walking access to the actual calls and tests routes into central Baghdad. Use this clockface trial as a timetable comparison.",
        "",
        "| Costed and operated scope | Route-km |",
        "|---|---:|",
        f"| Connected passenger routes | {r['in_service_route_km']:.3f} |",
        f"| Five deferred access sections | {sum(x['km'] for x in d.values()):.3f} |",
        f"| Six reserved links and infill sections | {sum(r['reserved_sections_km'].values()):.3f} |",
        f"| Full costed guideway | {r['costed_route_km']:.3f} |",
        "",
        "| Original group | Deferred section | Costed km | Where it reaches its main line |",
        "|---|---|---:|---|",
    ]
    for section, row in sorted(d.items()):
        location = (
            f"{row['schematic_gap_m']:,.0f} m from its nearest point"
            if row["schematic_gap_m"] > 1
            else "Touches the interior on the schematic map"
        )
        rows.append(f"| {row['group_id']} | {section} | {row['km']:.3f} | {location} |")
    rows.extend(
        [
            "",
            "M01 and M02 omit the Jadriya access branches. M04 omits both Sadr City branches. M09 circulates around the ring in both directions and omits the eastern spur. Confirm entrances, transfers, accessible paths and junction geometry in the field. Survey both M04 gaps before pricing links across them.",
            "",
            "## Two service offers",
            "",
            "| Operating day | Published peak offer | Clockface test |",
            "|---|---:|---:|",
            f"| Shortest scheduled headway | {peak['headway_s']} s | {t['headway_s']//60} min |",
            f"| Places/hour/direction | {3600//peak['headway_s']*v['places']:,} | {net['places_hour_direction']:,} |",
            f"| Passenger workings/day | {peak['trips_day']:,} | {net['passenger_trips_day']:,} |",
            f"| Passenger train-km/year | {peak['train_km_year']:,.0f} | {net['passenger_train_km_year']:,.0f} |",
            f"| Working trainsets | {peak['sets']} | {net['working_sets']} |",
            f"| Separate staging movements, train-km/year | Outside original ledger | {net['yard_train_km_year']:,.0f} |",
            "",
            f"The original full proposal assigns {r['original_connected_train_km_year']/1e6:.2f}m train-km to connected workings and {r['original_held_train_km_year']/1e6:.2f}m to unresolved paths. The fourteen-route peak offer drops {r['deferred_train_km_year']:,.0f} annual train-km. Its 150-second peak needs shorter signalling blocks and additional terminal capacity. The existing cost includes {net['retained_fleet']} sets, with {net['reserve_above_budgeted_active_sets']} above the budgeted active fleet.",
            "",
            "The clockface case keeps the six-car, 700-place train and provides one directional block between each pair of stops. Each line end has one exclusive throat, one face and a local staging lead. M09 has a separate lap face and lead per direction. Each train starts from and returns to a local staging area. The two directions finish the day with their initial stock counts.",
            "",
            f"At 15 and 20 minutes, the evaluated departure phases could not clear every shared junction. The {t['headway_s']//60}-minute option clears all {len(t['shared_interchange_hints'])} shared map hints in the model. The smallest clear intervals are {t['minimum_clearances_s']['block_margin_s']} s between directional block occupations, {t['minimum_clearances_s']['berth_margin_s']} s at a platform face and {t['minimum_clearances_s']['throat_margin_s']} s at a throat. Passenger transfers need a separate walking and accessibility survey.",
            "",
            "| Group | Terminal stops or lap | One-way km | Run min | Working sets | First origin phase, s after 06:00 |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for g, line in sorted(t["groups"].items()):
        s = line["patterns"][0]
        rows.append(
            f"| {g} | {s[0][0]} → {s[-1][0]} | {line['one_way_km']:.2f} | {line['run_s']/60:.1f} | {line['sets']} | {t['origin_phases_s'][g]} |"
        )
    rows.extend(
        [
            "",
            "Each direction departs for 18 hours. The second origin has its own offset in the record. The model places a 35-second dwell at each intermediate call, reserves three minutes at turns and books 10 km/h terminal approach and departure movements with a full stop at the clear side of each throat. It allows for the 104.5 m train tail and route release. Running time covers acceleration at 0.60 m/s² net, the 72 km/h cap and a 0.60 m/s² level brake reduced by 2% downhill gravity. Survey gradients and curves, then verify tractive effort, adhesion, braking and the signal overlap at the measured train weight.",
            "",
            "On M05, markers M-075 and M-076 are 104.27 m apart. The clockface case uses M-076 for a single call serving these adjacent markers. Check actual sightlines, entrances, luggage and wheelchair access at the site. The earlier peak comparison retains both calls.",
            "",
            "## Money and equipment",
            "",
            f"The central Iraqi estimate retains **${c['retained_costed_investment_usd_m']/1000:,.3f}bn** of full-network capital. The fourteen-route peak offer has **${c['published_annual_operations_usd_m']:,.1f}m/year** of estimated operations. The clockface case prices **${c['priced_annual_operations_usd_m']:,.1f}m/year** for existing scopes, keeping common staffing, stations, fleet and conductor maintenance while scaling purchased electricity and net variable train costs by passenger and yard kilometres. Its incremental site works and upkeep await quotations.",
            "",
            f"The operating trial needs {net['terminal_or_ring_direction_faces']} faces and {net['staging_leads']} dedicated 250 m leads, with overnight space for {net['staging_positions']} working sets. Check how these facilities connect to the {net['budgeted_depots']} budgeted depots. The investment ledger includes {net['budgeted_stations']} station allowances and {net['parent_grid_sites']} traction supply sites. The protected conductor feeds the train continuously. The {net['parent_service_battery_kwh']:.0f} kWh service battery supports independent essential loads. Verify citywide feed outages, repeated braking heat, isolation and recovery against the local timetable. The 12 km Airport feeder result belongs to its own design.",
            "",
            "Fare income at the reduced frequency requires directional counts, passenger response and paid journeys. The phased seven-line funding scenario belongs to the first programme. Citywide construction draws, funded price and opening dates require an owner programme.",
            "",
            "## Operator and buyer records",
            "",
            "Export one group’s complete train movements and station times. Times are local seconds after midnight and may extend into the following day. Open the [machine record](citywide-service.json) for section identities, scenarios, stop patterns, stock positions and phase searches.",
            "",
            "```sh",
            "python3 -m cities.Baghdad.citywide_service --check",
            "python3 -m cities.Baghdad.citywide_service --events M05 > build/m05-workings.csv",
            "python3 -m cities.Baghdad.citywide_service --return-template > build/citywide-return.json",
            "python3 -m cities.Baghdad.citywide_service --assess-return build/citywide-return.json",
            "```",
            "",
            "Place attachments beside the return file. A peak return records passengers on a named load section across one full hour, direction A_to_B or B_to_A, the local observation period, evidence filename and SHA-256. The result reports remaining capacity for that observed hour. Each review document takes a file and SHA-256. Local checks establish file integrity. Acceptance requires independent authentication, complete demand by direction, physical measurements, supplier scope review and an owner decision.",
            "",
        ]
    )
    return "\n".join(rows)


def dump(obj):
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--events", metavar="GROUP")
    mode.add_argument("--return-template", action="store_true")
    mode.add_argument("--assess-return", type=Path)
    args = parser.parse_args()
    r = build()
    if args.publish or args.check:
        docs = {GUIDE: render(r), RECORD: dump(r)}
        if args.check:
            for path, text in docs.items():
                if path.read_text() != text:
                    raise SystemExit(f"Regenerate {path.name}")
        else:
            with disk_reservation(
                ROOT, CITY, "Publish connected citywide planning selection", 4 << 20
            ) as lease:
                for path, text in docs.items():
                    check_disk_reservation(lease)
                    write_atomic(path, text.encode())
        print(r["evaluation_id"])
    elif args.events:
        cfg, _, _, _, groups = inputs()
        if args.events not in groups:
            parser.error("Unknown citywide group")
        t = r["timetable"]
        name = args.events
        _, _, trips = citywide_clockface.line_plan(
            name, groups[name], cfg, t["headway_s"], r["vehicle"]["level_brake_m_s2"]
        )
        writer = csv.writer(sys.stdout)
        writer.writerow(["group", "train", "direction", "stop", "arrival_local_s", "departure_local_s"])
        phase = t["origin_phases_s"][name]
        for train, side, dep, _ in trips:
            for stop, arr, leave in t["groups"][name]["patterns"][side]:
                writer.writerow([name, train, side, stop, dep + phase + arr, dep + phase + leave])
    elif args.return_template:
        print(dump(return_template(r)), end="")
    elif args.assess_return:
        print(dump(assess(r, json.loads(args.assess_return.read_bytes()), args.assess_return.parent)), end="")
    else:
        print(dump(r), end="")


if __name__ == "__main__":
    main()
