"""Current 20 m shared-pier civil delivery plan over the pinned Baghdad maps."""

import argparse
import csv
import hashlib
import io
import json
from math import isclose
from pathlib import Path

from cities.Baghdad import financing
from cities.Baghdad.engineering.mechanical.civil import family_comparison as family
from cities.Baghdad.engineering.mechanical.civil import rail_fed_erection as erection
from cities.Baghdad.engineering.simulation import airport_alignment, corridor
from engineering.outline import baghdad_system as system

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "rail-fed"
ROOT = system.ROOT
NETWORKS = ("first", "metropolitan")
CASES = ("low", "base", "high")


def sections(network, config, lengths):
    if network == "first":
        return [(name, km, "deck", "nominal RFI corridor") for name, km in lengths.items()]
    mapped = json.loads((ROOT / config["map_sources"][network + "_path"]).read_bytes())
    ring_ids = {
        f["properties"].get("route_id") for f in mapped["features"]
        if f["geometry"]["type"] == "LineString"
        and f["geometry"]["coordinates"][0] == f["geometry"]["coordinates"][-1]
    }
    groups = config["networks"][network]["service_groups"]
    mains = {parts[0]: group for group, parts in groups.items()}
    return [
        (name, km, "deck", mains[name]) if name in mains and name not in ring_ids
        else (name, km, "road", "ring: two access sites needed" if name in ring_ids
              else "access or reserved section: common yard supply assumed")
        for name, km in lengths.items()
    ]


def section_order(name, length, preferred, purpose, exclusion):
    # Pass a readable decimal chainage. Precise locations await the survey.
    length = round(length, 9)
    rail = preferred == "deck"
    result = erection.evaluate(length, exclusion, include_rail=rail, shared_offsite_yard=not rail)
    geo = result["geometry"]
    choice = "rail_24h" if rail else "road_day"
    method, road = result["methods"][choice], result["methods"]["road_day"]
    residual = geo["residual_m"]
    return {
        "section": name, "purpose": purpose, "route_km": length,
        "selected_planning_method": choice, "erection_study_id": result["evaluation_id"],
        "civil_physical_id": geo["civil_physical_id"],
        "standard_bays": geo["standard_bays"], "standard_girders": geo["standard_girders"],
        "standard_support_positions": geo["standard_shared_support_positions"],
        "standard_bearings": geo["standard_bays"] * 8,
        "residual_bays_pending_design": int(bool(residual)),
        "residual_length_m": residual,
        "dedicated_yards": 2 if rail else 0,
        "moulds_per_dedicated_yard": result["shared_quantities"].get("moulds_per_yard", 0) if rail else 0,
        "area_ha_per_dedicated_yard": result["shared_quantities"].get("area_ha_each", 0) if rail else 0,
        "storage_slots_per_dedicated_yard": (result["shared_quantities"]
            .get("released_stock_slots_per_yard", 0)) if rail else 0,
        "launcher_sets": 2 if rail else 0, "flatbeds": 2 if rail else 0,
        "calendar_days": method["calendar_days"],
        "road_day_calendar_days": road["calendar_days"],
        "road_16h_calendar_days": result["methods"]["road_extended"]["calendar_days"],
        "paid_erection_hours": method["labour_hours"],
        "paid_road_day_erection_hours": road["labour_hours"],
        "paid_total_method_and_casting_hours": method["labour_hours_including_casting"],
        "loaded_beam_trips": method["public_road_beam_trips"],
        "road_day_loaded_beam_trips": road["public_road_beam_trips"],
        "erection_lane_hours": method["road_lane_hours"],
        "road_day_erection_lane_hours": road["road_lane_hours"],
        "temporary_track_km": method["temporary_track_km"],
        "civil_scope_usd": {case: method["cases"][case]["installed_standard_stock_usd"] for case in CASES},
        "road_day_civil_scope_usd": {case: road["cases"][case]["installed_standard_stock_usd"] for case in CASES},
        "method_cost_usd": {case: method["cases"][case]["method_scope_usd"] for case in CASES},
        "road_day_method_cost_usd": {case: road["cases"][case]["method_scope_usd"] for case in CASES},
        "crew_shifts": method["crew_shifts"],
        "casting_shifts": method["yard_shifts"],
        "supplier_yard_layout": result["shared_quantities"].get("yard") if rail else None,
    }


def slots(orders, simultaneous_lines):
    """Dispatch complete independent packages to one of the available launcher pairs."""
    deck = [row for row in orders if row["launcher_sets"]]
    clocks = [0.0] * min(simultaneous_lines, len(deck))
    allocation = []
    for row in sorted(deck, key=lambda row: (-row["calendar_days"], row["section"])):
        lane = min(range(len(clocks)), key=clocks.__getitem__)
        start = clocks[lane]
        clocks[lane] += row["calendar_days"]
        allocation.append(dict(section=row["section"], launcher_pair=lane + 1, start_day=start,
                               finish_day=clocks[lane]))
    road_finish = max((r["calendar_days"] for r in orders if not r["launcher_sets"]), default=0)
    return dict(available_launcher_pairs=len(clocks), paired_line_programmes=allocation,
                isolated_road_sections_finish_day=road_finish,
                last_standard_deck_day=max([road_finish, *clocks]))


def funding(config, net, prior, orders, civil_cost_key):
    """Replace the whole elevated direct scope once. Pass dependent scopes to the existing cash model."""
    source = prior["selected_capital_scope_usd_m"]
    direct = {key: amount for key, amount in source.items()
              if key not in ("design_assurance", "testing_commissioning", "project_allowance")}
    rates = config["capital_rates_usd_m"]
    rate = config["discount_rate_real"]
    annuity = sum((1 + rate)**-year for year in range(1, 31))
    cases = {}
    for index, case in enumerate(CASES):
        direct["elevated_civil"] = sum(row[civil_cost_key][case] for row in orders) / 1e6
        work = sum(direct.values())
        design = work * rates["design_fraction"]
        testing = work * rates["testing_fraction"]
        reserve = (work + design + testing) * rates["project_allowance_fraction"]
        installed = work + design + testing + reserve
        bearings = sum(row["standard_bearings"] for row in orders)
        bays = sum(row["standard_bays"] for row in orders)
        annual = (bearings * family.TRIALS["annual_inspection_usd_bearing"][index]
                  + 2 * bays * family.TRIALS["inspection_usd_span_year"][index]) / 1e6
        renewal = bearings * (family.TRIALS["bearing_purchase_usd_each"][index]
                              + family.TRIALS["bearing_renewal_labour_usd"][index]) / 1e6
        # The inherited O&M includes vehicle, station and power operations.
        # Add the distinct civil stock reserve for the compared structure.
        opex = prior["selected_annual_opex_usd_m"]["total"] + annual
        renewals = [*prior["selected_renewals_usd_m"],
                    dict(year=20, component="standard_bearings", usd_m=renewal)]
        service_pv = opex * annuity + sum(row["usd_m"] / (1 + rate)**row["year"] for row in renewals)
        construction = system._construction_cashflow(config["networks"][net], installed, service_pv, rate)
        finance_inputs = dict(selected_construction_cashflow=construction,
                              selected_annual_opex_usd_m={"total": opex}, selected_renewals_usd_m=renewals)
        cases[case] = dict(elevated_direct_usd_m=direct["elevated_civil"],
                           installed_planning_usd_m=installed, design_usd_m=design, test_usd_m=testing,
                           allowance_usd_m=reserve, inherited_other_direct_usd_m=work-direct["elevated_civil"],
                           annual_civil_inspection_reserve_usd_m=annual,
                           year20_bearing_reserve_usd_m=renewal, annual_opex_including_reserve_usd_m=opex,
                           whole_life_at_full_service_usd_m=installed + service_pv,
                           construction_cash_assumption=construction,
                           buyer_cash={key: financing.cash_schedule(finance_inputs, *terms)
                                       for key, terms in financing.CASES.items()})
    return cases


def programme(network, prior, exclusion):
    config = system.load(network=network)
    lengths, basis, _ = system._lines(ROOT, config, network)
    orders = [section_order(*items, exclusion) for items in sections(network, config, lengths)]
    if not isclose(sum(row["route_km"] for row in orders), config["networks"][network]["route_km"], abs_tol=1e-7):
        raise ValueError("Construction work packages must conserve the mapped planning length")
    counts = ("standard_bays", "standard_girders", "standard_support_positions", "standard_bearings",
              "residual_bays_pending_design", "residual_length_m", "dedicated_yards", "launcher_sets",
              "flatbeds", "paid_erection_hours", "paid_road_day_erection_hours",
              "paid_total_method_and_casting_hours", "loaded_beam_trips", "road_day_loaded_beam_trips",
              "erection_lane_hours", "road_day_erection_lane_hours", "temporary_track_km")
    totals = {key: sum(row[key] for row in orders) for key in counts}
    totals.update(total_precast_yard_area_ha=sum(row["area_ha_per_dedicated_yard"] * row["dedicated_yards"] for row in orders),
                  total_moulds=sum(row["moulds_per_dedicated_yard"] * row["dedicated_yards"] for row in orders),
                  total_released_storage_slots=sum(row["storage_slots_per_dedicated_yard"] * row["dedicated_yards"] for row in orders))
    records = dict(
        route_basis=basis, route_km=config["networks"][network]["route_km"], orders=orders, totals=totals,
        concurrency={n: slots(orders, n) for n in (1, 3, config["networks"][network]["lines"])},
        prior_10m_comparator=dict(
            civil_scope_usd_m=prior["selected_capital_scope_usd_m"]["elevated_civil"],
            installed_usd_m=prior["selected_construction_cashflow"]["total_capital_usd_m"],
            girders=prior["power_cases"][prior["digital_cost_leader"]]["civil_beams"],
            supports=prior["power_cases"][prior["digital_cost_leader"]]["civil_piers"],
        ),
        inherited_service_evaluation_id=prior["selected_evaluation_id"],
        civil_replacement_costs=funding(config, network, prior, orders, "civil_scope_usd"),
        matched_road_costs=funding(config, network, prior, orders, "road_day_civil_scope_usd"),
    )
    return records


def build(exclusion=5):
    source = ROOT / "cities/Baghdad/system-results.json"
    prior = json.loads(source.read_text())
    config = system.load()
    # The network scope retains its mapped nominal lengths. The corrected
    # Airport geometry has its own standalone cash and operating identities.
    route = airport_alignment.evaluate()
    standalone = section_order("Airport corrected alignment", route["route_km"], "deck",
                               "17.46 km horizontal audit; no surveyed terminal yards", exclusion)
    standalone["alignment_id"] = route["alignment_id"]
    sources = [source, Path(__file__).resolve(), ROOT / system.CONFIG,
               Path(system.__file__), Path(financing.__file__), Path(family.__file__),
               Path(erection.__file__), erection.ASSUMPTIONS, Path(corridor.__file__),
               corridor.REGISTER, corridor.PACKET]
    sources.extend(ROOT / config["map_sources"][key + "_path"]
                   for key in (*NETWORKS, "waypoints"))
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sources}
    short_source_names = {"opening.json", "service.json", "station-register.json", "corridor.py"}
    hashes.update({path: digest for path, digest in route["source_sha256"].items()
                   if path not in short_source_names})
    report = dict(schema="osr-baghdad-deck-fed-delivery/1", basis="current civil budgeting and supplier enquiry",
                  span_m=20, pier_family="shared-crosshead", erection="two terminal gantries per open main line",
                  overhead_fallback_pct=exclusion,
                  source_sha256=hashes,
                  networks={key: programme(key, prior["networks"][key], exclusion) for key in NETWORKS},
                  corrected_airport_standalone=standalone, physical_accepted=False,
                  holds=["Survey land, centreline, terminal yards and transfer point. Confirm noise and traffic windows.",
                         "Proof of construction load paths and safe rail carrier, gantry and temporary track arrangements.",
                         "Quote residual spans, special crossings and station transitions separately. The source study reserves interfaces.",
                         "Verify branch feed and queueing from shared yards and provide separate ring access. These planning rates are provisional.",
                         "Confirm gantry transport, test and setup for each successive package. Reuse scenarios retain mobilisation prices.",
                         "Replace inherited power, operations, station and price allowances when scope changes. Keep this comparison separate from certified costs.",
                         "The first programme contains a 12 km Airport length allowance. The separate corrected case needs a survey and joined service update."])
    report["evaluation_id"] = system._id(report)
    return report


def markdown(report):
    lines = ["# Baghdad civil delivery programme", "",
             "The current pricing and delivery case uses **20 m U-girders on shared piers** "
             "and inward deck-fed launching on open main lines. The published 10 m cost "
             "and prototype records remain reproducible as comparators.", "",
             "The seven-corridor and citywide programmes are independent studies. The civil "
             "replacement changes the elevated works and associated design, testing and "
             "allowances. Financial comparisons retain the inherited stations, service, "
             "non-civil rates and calendar. Ground works remain common to the two 20 m methods.", "",
             f"Evaluation `{report['evaluation_id']}`.", ""]
    for key, value in report["networks"].items():
        title = "Seven corridors" if key == "first" else "Independent citywide"
        totals = value["totals"]
        paid = totals["paid_total_method_and_casting_hours"]
        casting = paid - totals["paid_erection_hours"]
        base, road = (value[field]["base"] for field in ("civil_replacement_costs", "matched_road_costs"))
        amounts = value["civil_replacement_costs"]
        prior = value["prior_10m_comparator"]
        lines.extend([
            f"## {title} · {value['route_km']:g} km", "",
            "| Quantity, cost or programme measure | Current planning result |", "|---|---:|",
            f"| Standard 20 m girders / shared supports / bearings | {totals['standard_girders']:,} / "
            f"{totals['standard_support_positions']:,} / {totals['standard_bearings']:,} |",
            f"| Stock / foundations in earlier 10 m control | {prior['girders']:,} / {prior['supports']:,} |",
            f"| Residual bays awaiting design | {totals['residual_bays_pending_design']} |",
            f"| Terminal yards / total land allowance | {totals['dedicated_yards']} / {totals['total_precast_yard_area_ha']:.2f} ha |",
            f"| Moulds / released stock positions | {totals['total_moulds']} / {totals['total_released_storage_slots']} |",
            f"| Gantries / flatbeds for full parallel work | {totals['launcher_sets']} / {totals['flatbeds']} |",
            f"| Erection / casting paid hours | {totals['paid_erection_hours']:,.0f} / {casting:,.0f} |",
            f"| Booked erection lane-hours · road comparator → deck-led | {totals['road_day_erection_lane_hours']:,} → {totals['erection_lane_hours']:,} |",
            f"| Loaded beam trips on public roads · road comparator → deck-led | {totals['road_day_loaded_beam_trips']:,} → {totals['loaded_beam_trips']:,} |",
            f"| Direct elevated stock and construction · old 10 m vs matched 20 m road vs deck-led base | "
            f"${prior['civil_scope_usd_m']:,.1f}m / ${road['elevated_direct_usd_m']:,.1f}m / ${base['elevated_direct_usd_m']:,.1f}m |",
            "| Revised installed network planning estimate low / base / high | "
            + " / ".join(f"${amounts[c]['installed_planning_usd_m']/1000:.3f}bn" for c in CASES) + " |",
            f"| Civil inspection reserve/year and year 20 bearings, base | ${base['annual_civil_inspection_reserve_usd_m']:.2f}m / ${base['year20_bearing_reserve_usd_m']:.2f}m |",
            "",
            "### Parallel work and gantry reuse", "",
            "| Available launcher pairs | Last standard deck day from programme start |",
            "|---|---:|",
        ])
        for _, batch in value["concurrency"].items():
            lines.append(f"| {batch['available_launcher_pairs']} | {batch['last_standard_deck_day']:.0f} |")
        lines.extend(["", "This schedule starts each eligible work package as a complete job. It "
                      "retains mobilisation, inspections and terminal work for reused equipment. Ring, "
                      "short access and reserved works need separate access and can affect the critical path.", "",
                      "| Work section | Method | km | Girders | Days | Base civil scope |",
                      "|---|---|---:|---:|---:|---:|"])
        for row in value["orders"]:
            method = "Deck-fed" if row["launcher_sets"] else "Road/shared yard"
            lines.append(f"| {row['section']} | {method} | {row['route_km']:.3f} | {row['standard_girders']:,} "
                         f"| {row['calendar_days']:.0f} | ${row['civil_scope_usd']['base']/1e6:.2f}m |")
        lines.append("")
    a = report["corrected_airport_standalone"]
    lines.extend([
        "## Corrected Airport alignment, standalone civil case", "",
        f"The separate **{a['route_km']:.3f} km** horizontal study carries "
        f"**{a['standard_girders']:,}** standard girders and **{a['standard_support_positions']:,}** "
        f"shared support positions. The deck-fed work envelope is **{a['calendar_days']:.0f} days**, "
        f"with **{a['paid_total_method_and_casting_hours']:,.0f}** paid casting and erection hours and "
        f"**${a['civil_scope_usd']['base']/1e6:,.2f}m** base civil scope. The earlier seven-corridor "
        "estimate carries its own nominal 12 km Airport allowance. Survey and join the corrected "
        "Airport geometry to the rest of that programme before changing its route or service budget.", "",
        "## Evidence to obtain before release", "",
        *[f"- {hold}" for hold in report["holds"]], "",
        "[Exact programme, cash schedules and per-shift result](network-delivery.json) · "
        "[Section costing and resource worksheet](network-delivery.csv) · "
        "[Terminal yard and method study](../RAIL-FED-ERECTION.md)", "",
    ])
    return "\n".join(lines)


def csv_rows(report):
    fields = ("section", "purpose", "route_km", "selected_planning_method", "standard_girders",
              "standard_support_positions", "standard_bearings", "residual_bays_pending_design",
              "dedicated_yards", "area_ha_per_dedicated_yard", "moulds_per_dedicated_yard",
              "storage_slots_per_dedicated_yard", "calendar_days", "paid_erection_hours",
              "paid_total_method_and_casting_hours", "loaded_beam_trips", "erection_lane_hours",
              "temporary_track_km")
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("programme", *fields, *(f"civil_{c}_usd" for c in CASES), "erection_study_id"))
    for network, programmes in report["networks"].items():
        for row in programmes["orders"]:
            writer.writerow([network, *(row[field] for field in fields),
                             *(round(row["civil_scope_usd"][case], 2) for case in CASES), row["erection_study_id"]])
    return stream.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overhead-fallback-pct", type=float, default=5)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = build(args.overhead_fallback_pct)
    text = markdown(report)
    data = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if not (args.check or args.write):
        print(data if args.json else text, end="")
        return
    if args.overhead_fallback_pct != 5:
        parser.error("The published files use the 5% scenario")
    for name, contents in {
        "network-delivery.json": data,
        "network-delivery.md": text,
        "network-delivery.csv": csv_rows(report),
    }.items():
        target = OUTPUT / name
        if args.check:
            if not target.is_file() or target.read_text() != contents:
                parser.error(f"Regenerate {target.relative_to(ROOT)}")
        else:
            target.write_text(contents)


if __name__ == "__main__":
    main()
