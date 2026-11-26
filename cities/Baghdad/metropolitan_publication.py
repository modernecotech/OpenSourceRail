"""Publish one selected Baghdad planning network and its delivery records."""

import argparse
import gzip
from hashlib import sha256
from pathlib import Path
import tomllib

from engineering.performance import disk_reservation

from . import central_access as access, holistic_network, residential_planning, straight_network_publication as stock
from . import straight_network_study as resources, third_ring_publication as comparison_view, third_ring_study
from .engineering.mechanical.civil import alignment_beams

CITY = access.CITY
SELECTOR = CITY / "metropolitan-default.toml"
COMPARISON = CITY / comparison_view.DATA
RECORD = CITY / "metropolitan-network.json"
REPORT = CITY / "METROPOLITAN-NETWORK.md"
DELIVERY = CITY / "METROPOLITAN-DELIVERY.md"
MAP = CITY / "maps/baghdad-metropolitan-network.png"
GEOJSON = MAP.with_suffix(".geojson")


def evaluate():
    selection = tomllib.loads(SELECTOR.read_text())
    comparison = access.read(COMPARISON)
    code = selection["layout"]
    network = comparison["layouts"][code]
    summary = comparison["summary"][code]
    expected = comparison["costs"][code]
    journeys = comparison["named_suburban_journeys"]["variants"][code]
    packet = {key: value for key, value in comparison.items() if key != "publication_id"}
    if sha256(access.encode(packet)).hexdigest() != comparison["publication_id"]:
        raise ValueError("Baghdad comparison data differ from the published identity")
    if ({row["candidate_id"] for row in (network, summary, expected, journeys)}
            != {selection["candidate_id"]} or network["physical_accepted"]
            or network["operating_timetable_validated"] or selection["physical_acceptance"]
            or selection["procurement_release"] or selection["purpose"] != "metropolitan-planning"):
        raise ValueError("The default may select one mapped planning candidate")
    if holistic_network._identity(dict(network))["evaluation_id"] != network["evaluation_id"]:
        raise ValueError("The selected network evaluation is inconsistent")
    polygons = third_ring_study.validate_layout(network)
    context = access.original_cases()[3]
    through = third_ring_study.classify_through(network, context)
    if (set(polygons) != set(third_ring_study.RINGS) or through != summary["through_lines"]
            or len(through) != len(network["lines"]) - len(polygons) - len(summary["local_services"])
            or "Airport-00" not in network["stations"]
            or any(not row["walkable_through_routes"] for row in journeys["origins"].values())):
        raise ValueError("The selected planning layout must retain its verified rings and through services")

    policy = tomllib.loads(residential_planning.POLICY.read_text())
    beam, civil, cost = resources._selected_resources(network, context, policy)
    if (civil["evaluation_id"] != expected["civil_evaluation_id"]
            or beam["evaluation_id"] != expected["beam_evaluation_id"] or cost["cost_cases"] != expected["cost_cases"]):
        raise ValueError("Re-evaluate the three-ring comparison with the current delivery calculation")
    sources = dict(comparison["source_sha256"]) | civil["source_sha256"]
    for path in (SELECTOR, COMPARISON, Path(__file__)):
        sources[path.relative_to(access.ROOT).as_posix()] = access.digest(path)
    for path, digest in sources.items():
        if access.digest(access.ROOT / path) != digest:
            raise ValueError(f"Refresh the Baghdad comparison before selecting it. Source differs: {path}")
    benchmark = comparison["costs"]["published"]
    previous = {"track_km": benchmark["running_track_km"], "cases": benchmark["cost_cases"],
                "paid_casting_haul_and_erection_hours": benchmark["standard_stock_paid_hours"],
                "standard_deck_handover_day": benchmark["standard_stock_last_deck_day"]}
    record = {"schema": "osr-baghdad-metropolitan/1", "reference": comparison["publication_id"],
              "display_trial": code, "planning_selection": selection, "network": network, "summary": summary,
              "named_suburban_journeys": journeys, "access_holds": comparison["selection"]["holds"][code],
              "previous_cost": previous, "civil": civil, "cost": cost, "beam_schedule": beam,
              "source_sha256": sources}
    record["publication_id"] = sha256(access.encode(resources.public_record(record))).hexdigest()
    return record, comparison, context


def report(record):
    row, net = record["summary"], record["network"]
    lines = ["# Baghdad metropolitan railway", "",
             f"The active planning network has **{row['lines']} services, {row['route_km']:.2f} route-km and "
             f"{row['stations']} station sites**. The {len(row['rings'])} rings connect "
             f"{row['through_count']} cross-Tigris trunks. The table gives named suburban access to through trains.", "",
             "![Baghdad metropolitan railway planning network](maps/baghdad-metropolitan-network.png)", "",
             "[Proposal](PROPOSAL.md) · [Delivery, labour and cost](METROPOLITAN-DELIVERY.md) · "
             "[Editable routes and stations](maps/baghdad-metropolitan-network.geojson) · "
             "[Machine results](metropolitan-network.json) · [Options and journey comparison](THREE-RING-STUDY.md)", "",
             f"Within a 1.3 km street walk, the layout reaches **{row['worldpop_1300_pct']:.2f}%** of WorldPop "
             f"and **{row['ghsl_1300_pct']:.2f}%** of GHSL residents. This is the planning choice for connected "
             "through service and a simpler route set. The broader two-ring benchmark covers more residents. "
             "The remaining gaps inform the next station and route refinements.", "",
             "| Suburb | Through train | Tested centres reachable without a change | Within two changes |",
             "|---|---|---:|---:|"]
    for name, result in record["named_suburban_journeys"]["origins"].items():
        routes = ", ".join(result["walkable_through_routes"])
        lines.append(f"| {name} | {routes} | {result['direct_through_destination_count']} | "
                     f"{result['destination_count_by_max_transfers']['2']} |")
    lines += ["", "The service comparison uses a fixed train-km budget. The delivery estimate uses a six-minute "
              "costing offer. Land, structures, operating safety, accessibility and procurement approvals remain open.", "",
              "## Open service and coverage checks", "",
              *(f"- {hold}." for hold in record["access_holds"]), "",
              f"Candidate `{net['candidate_id']}` · publication `{record['publication_id']}`.", ""]
    return "\n".join(lines)


def readers(record):
    civil, system, beam = (record[key] for key in ("civil", "cost", "beam_schedule"))
    q, service, power = civil["quantities"], system["service"], system["power"]
    summary = record["summary"]
    costs = system["cost_cases"]
    figures = lambda field: " | ".join(f"US${costs[case][field]/1000:.2f}bn" for case in ("low", "base", "high"))
    headline = (f"**Current metropolitan planning case.** {q['unique_guideway_km']:,.2f} km of distinct mapped "
                f"guideway, {q['double_track_km']:,.2f} running-track km and {q['station_sites']} station sites. "
                f"The base installed planning allowance is **US${costs['base']['installed_planning_usd_m']/1000:.2f}bn**. "
                f"Standard casting, haul and erection account for "
                f"{civil['workforce']['paid_deck_and_casting_hours']/1e6:.2f} million paid hours. "
                "[Quantities, labour and costs](METROPOLITAN-DELIVERY.md) · [Network and map](METROPOLITAN-NETWORK.md)")
    curves = sum(row["girders"] for family, row in beam["by_family"].items() if "curved_ugirder" in family)
    programme = (
        f"The active layout has {summary['through_count']} cross-Tigris trunks and {len(summary['rings'])} rings. "
        "The planning inventory identifies "
        f"**{curves:,} curved girder pieces** and **{beam['totals']['held_route_length_m']/1000:.2f} service-route km** "
        "of interfaces that need detailed geometry and engineering.\n\n"
        "| 2026 planning scope | Low | Base | High |\n|---|---:|---:|---:|\n"
        f"| Installed allowance | {figures('installed_planning_usd_m')} |\n"
        f"| Annual operation | {figures('annual_operations_total_usd_m')} |\n"
        f"| 30-year present cost | {figures('whole_life_present_usd_m')} |\n\n"
        f"The six-minute costing offer uses {service['fleet_trainsets']:,} trainsets including reserves, "
        f"{power['nominal_supply_sites']} nominal supply sites and {power['annual_grid_gwh']:,.1f} GWh per year. "
        "The project opening date depends on the complete construction and commissioning programme. "
        "[Delivery programme](METROPOLITAN-DELIVERY.md) · "
        "[Beam designs and work orders](engineering/mechanical/civil/CURVED-BEAM-PROGRAMME.md)"
    )
    result = {}
    for filename in ("README.md", "PROPOSAL.md"):
        path = CITY / filename
        content = stock._replace_block(path.read_text(), "current housing budget", headline)
        if filename == "PROPOSAL.md":
            content = stock._replace_block(content, "current route programme", programme)
        result[path] = content.encode()
    return result


def outputs(record, comparison, context):
    code = record["display_trial"]
    gis = comparison_view.geojson(comparison, code)
    gis.update(publication_id=record["publication_id"], study_status="active-metropolitan-planning")
    beam = record["beam_schedule"]
    delivery = stock.delivery_report(record).replace("Earlier central ring", "Two-ring benchmark")
    return {
        RECORD: access.encode(resources.public_record(record)),
        REPORT: report(record).encode(),
        DELIVERY: delivery.replace("STRAIGHT-THROUGH-NETWORK.md", REPORT.name).encode(),
        MAP: comparison_view.draw(comparison, context, only=code),
        GEOJSON: access.encode(gis),
        resources.BEAM_PLAN: stock.beam_report(beam).replace("STRAIGHT-THROUGH-DELIVERY.md", DELIVERY.name).encode(),
        resources.BEAM_CSV: stock.beam_csv(beam),
        resources.BEAM_DRAWING: alignment_beams.render_svg(beam).encode(),
        resources.BEAM_CAD: alignment_beams.render_dxf(beam).encode(),
        resources.BEAM_DATA: gzip.compress(access.encode(beam), mtime=0),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--output", type=Path)
    args = parser.parse_args()
    target = args.output or CITY
    with disk_reservation(access.ROOT, target, "Baghdad metropolitan proposal, cost and work orders", 160 << 20):
        record, comparison, context = evaluate()
        generated = outputs(record, comparison, context)
        if args.output is None:
            generated.update(readers(record))
        stock._compare_or_write(generated, target, check=args.check, map_files={MAP})
    print(record["publication_id"])


if __name__ == "__main__":
    main()
