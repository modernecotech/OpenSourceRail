"""Test nested Baghdad loops with 5 km continuous separation and simpler services."""

import argparse
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import tomllib

from engineering.performance import disk_reservation
from engineering.station_rail.publication import write

from . import (
    central_access, holistic_network, network_station_sites, residential_planning,
    ring_corridors, ring_grid_comparison as grid, spaced_ring_geometry as geometry,
    spaced_ring_layouts as layouts,
)


REPORT = grid.CITY / "SPACED-RINGS.md"
RECORD = grid.CITY / "spaced-rings.json"
FIGURE = grid.CITY / "maps/baghdad-spaced-rings.png"
GEOJSON = grid.CITY / "maps/baghdad-spaced-rings.geojson"
PRIOR = grid.CITY / "ring-grid.json"
PRIOR_MAP = grid.CITY / "maps/baghdad-ring-grid.geojson"
WIDE = "wide-angle inter-district"
NAMES = {"current": "Published Baghdad network", "previous": "Previous two-ring grid",
         "overlay": "Compact rings with current routes", "one-ring": "Simplified routes with outer ring only"}


def _file_id(file):
    return file.relative_to(central_access.ROOT).as_posix()


def prepare(current, graph, context, screen):
    outer, outer_evidence = ring_corridors.evaluate_rings(current, graph, context, include_inner=False)
    search = geometry.evaluate_geometry(outer["lines"]["M09"], outer, context, walking_graph=graph)
    trials = {}
    shortlist = [opt for opt in search["bridge_pairs"] if opt["passes_connectivity_screen"]]
    if search["selected"] and search["selected"] not in shortlist:
        shortlist.insert(0, search["selected"])
    for option in shortlist:
        try:
            overlay, inner_evidence = geometry.insert(outer, option, graph, context)
        except ValueError as error:
            trials[str(option["bridge_ways"])] = str(error)
            continue
        break
    else:
        raise ValueError(f"No spaced ring passed integration: {trials}")
    overlay_evidence = {"inner": inner_evidence, "bridge_ways": option["bridge_ways"],
                        "bridges": option["bridges"], "outer_evaluation_id": outer["evaluation_id"]}
    alternatives = layouts.alternatives(overlay, graph=graph, context=context,
                                       protected_stations=grid.PROTECTED, screen=screen)
    networks = {"current": current, "overlay": overlay}
    known = {net["candidate_id"] for net in networks.values()}
    for key, row in alternatives.items():
        net = row.get("network")
        if net and net["candidate_id"] not in known:
            networks[key] = net
            known.add(net["candidate_id"])
    evidence = {"outer": outer_evidence, "geometry_search": search, "overlay": overlay_evidence,
                "insertion_rejections": trials, "layout_options": {
                    key: {item: value for item, value in row.items() if item not in {"network", "source_metrics"}}
                    for key, row in alternatives.items()}}
    return networks, evidence


def _screen_rings(network):
    rings = network["lines"]
    if not all(rings.get(line, {}).get("loop") for line in ("M09", "M15")):
        raise ValueError("Both mapped rings must be closed")
    gap = geometry.separation(rings["M09"], rings["M15"]["geometry"])
    if gap["minimum_ring_separation_m"] < geometry.MIN_SEPARATION_M:
        raise ValueError("Two-ring trial violates the 5 km alignment clearance")
    spokes = [{line for stop in rings[code]["station_ids"] for line in network["stations"][stop]["lines"]}
              for code in ("M09", "M15")]
    return gap | {"direct_spokes": sorted((spokes[0] & spokes[1]) - {"M09", "M15"})}


def _summary(record, key):
    geo = record["geometry"][key]
    housing = record["same_train_km_housing"]["variants"][key]
    metro = record["same_train_km_metropolitan"]["variants"][key]
    wide = metro["cohorts"][WIDE]
    paired = metro["paired_cohorts"][WIDE]
    delivery = record["six_minute_delivery_and_cost"][key]
    return {"route_km": geo["route_km"], "lines": geo["lines"], "stations": geo["stations"],
            "parallel_pair_km": geo["parallel_pair_km"], "rings": geo["rings"],
            "walk_worldpop_pct": record["coverage"]["worldpop-2026"]["metropolitan"]["cases"][key]["1200"]["share_pct"],
            "walk_ghsl_pct": record["coverage"]["ghsl-2025"]["metropolitan"]["cases"][key]["1200"]["share_pct"],
            "metro_served_pct": metro["journeys"]["served_share_pct"],
            "wide_angle_served_pct": wide["served_share_pct"],
            "same_trip_p90_reference_min": paired["reference_elapsed_p90_min"],
            "same_trip_p90_trial_min": paired["candidate_elapsed_p90_min"],
            "housing_two_changes_pct": housing["journeys"]["reachable_with_at_most_share_of_all_pct"]["2"],
            "average_headway_min": metro["service"]["directional_headway_s"] / 60,
            "track_km": delivery["track_km"], "paid_crew_hours": delivery["paid_casting_haul_and_erection_hours"],
            "standard_deck_handover_day": delivery["standard_deck_handover_day"],
            "fleet_trainsets": delivery["fleet_including_spares"],
            "installed_usd_bn": delivery["cases"]["base"]["installed_planning_usd_m"] / 1000,
            "whole_life_usd_bn": delivery["cases"]["base"]["whole_life_present_usd_m"] / 1000}


def _prior_map():
    data = central_access.read(PRIOR_MAP)
    features = [item for item in data["features"] if item["properties"].get("kind") == "line"]
    lines = {item["properties"]["line_id"]: {"geometry": item["geometry"]["coordinates"]} for item in features}
    stations = {item["properties"]["station_id"]: {"coordinates": item["geometry"]["coordinates"]}
                for item in data["features"] if item["properties"].get("kind") in {"station", "interchange"}}
    return lines, stations


def _choose(summaries):
    current = summaries["current"]
    eligible = [key for key, row in summaries.items() if key not in {"current", "previous", "overlay"}
                and {"M09", "M15"} <= row["rings"].keys() and row["lines"] < current["lines"]
                and row["parallel_pair_km"] < current["parallel_pair_km"]
                and row["close_site_pairs"] < current["close_site_pairs"]]
    within_length = [key for key in eligible if summaries[key]["route_km"] <= current["route_km"] + .01]
    pool = within_length or eligible or [key for key in summaries
                                         if key not in {"current", "previous", "overlay", "one-ring"}]
    return max(pool or ["overlay"], key=lambda key: (
        summaries[key]["housing_two_changes_pct"], summaries[key]["wide_angle_served_pct"], key))


def _without_inner(network):
    """Keep the same outer ring and radial routes for a paired comparison."""
    revised = deepcopy(network)
    del revised["lines"]["M15"]
    layouts._membership_and_links(revised)
    revised["topology"] = holistic_network.validate(revised)
    revised["paired_ring_control"] = {"source_candidate_id": network["candidate_id"],
                                     "source_evaluation_id": network["evaluation_id"],
                                     "removed_line": "M15"}
    revised["source_sha256"][_file_id(Path(__file__))] = central_access.digest(Path(__file__))
    return holistic_network._identity(revised)


def evaluate(baseline_path):
    baseline = central_access.read(baseline_path)
    current = baseline["network"]
    if current["candidate_id"] != grid.REFERENCE_ID:
        raise ValueError(f"Use the published network at {grid.REFERENCE_COMMIT}")
    graph = central_access.walking_graph()
    context = central_access.original_cases()[3]
    screen = tomllib.loads(residential_planning.POLICY.read_text())["corridor_screen"]
    networks, evidence = prepare(current, graph, context, screen)
    prior = central_access.read(PRIOR)
    old_lines, old_sites = _prior_map()
    previous = _summary(prior, prior["display_trial"])
    from shapely.geometry import LineString
    import numpy as np

    previous["minimum_ring_separation_m"] = LineString(
        np.asarray(old_lines["M09"]["geometry"]) * holistic_network.LOCAL_METRES).distance(
        LineString(np.asarray(old_lines["M15"]["geometry"]) * holistic_network.LOCAL_METRES))
    previous["close_site_pairs"] = len(network_station_sites._nearby(old_sites, layouts.CLOSE_SITE_M))
    distances = {key: _screen_rings(net) for key, net in networks.items() if key != "current"}
    if any(len(gap["direct_spokes"]) < 2 for gap in distances.values()):
        networks = {key: net for key, net in networks.items()
                    if key == "current" or len(distances[key]["direct_spokes"]) >= 2}
    # Price and assign the physical variants together at the same operating budget.
    # Reuse the identical published control and preceding grid result as an external comparison.
    actual = grid.assess(networks, graph, baseline_record=baseline, trials={}, ring_evidence={})
    summary = {}
    for key, network in networks.items():
        summary[key] = _summary(actual, key) | distances.get(key, {}) | {
            "close_site_pairs": len(network_station_sites._nearby(network["stations"], layouts.CLOSE_SITE_M))}
    picked = _choose(summary)
    networks["one-ring"] = _without_inner(networks[picked])
    # The second assignment checks that the inner ring is being compared on the very same radial layout.
    control = grid.assess({key: networks[key] for key in ("current", "one-ring")}, graph, baseline_record=baseline,
                          trials={}, ring_evidence={})
    for metric in ("same_train_km_housing", "same_train_km_metropolitan"):
        sample = actual[metric]["demand_sample"]["sample_id"]
        if sample != prior[metric]["demand_sample"]["sample_id"] or sample != control[metric]["demand_sample"]["sample_id"]:
            raise ValueError(f"Unmatched {metric} inputs")
        actual[metric]["variants"]["one-ring"] = control[metric]["variants"]["one-ring"]
    actual["geometry"]["one-ring"] = control["geometry"]["one-ring"]
    actual["six_minute_delivery_and_cost"]["one-ring"] = control["six_minute_delivery_and_cost"]["one-ring"]
    for dataset, coverage in actual["coverage"].items():
        for area, cells in coverage.items():
            if isinstance(cells, dict) and "cases" in cells:
                cells["cases"]["one-ring"] = control["coverage"][dataset][area]["cases"]["one-ring"]
    summary["one-ring"] = _summary(control, "one-ring") | {
        "close_site_pairs": len(network_station_sites._nearby(networks["one-ring"]["stations"], layouts.CLOSE_SITE_M))}
    summary["previous"] = previous
    sources = baseline["sources"] | current["source_sha256"]
    for path in (Path(__file__), Path(geometry.__file__), Path(layouts.__file__), Path(grid.__file__),
                 residential_planning.POLICY, PRIOR, PRIOR_MAP, central_access.ROOT / "cities/Baghdad/ring_grid_journeys.py"):
        sources[_file_id(path)] = central_access.digest(path)
    record = {"schema": "osr-baghdad-spaced-rings/1", "published_candidate_id": current["candidate_id"],
              "reference_publication_id": baseline["publication_id"], "reference_revision": grid.REFERENCE_COMMIT,
              "reference_packet_sha256": central_access.digest(baseline_path),
              "earlier_comparison_id": prior["comparison_id"], "earlier_display_trial": prior["display_trial"],
              "display_trial": picked, "sources": sources, "summary": summary,
              "same_train_km_housing": actual["same_train_km_housing"],
              "same_train_km_metropolitan": actual["same_train_km_metropolitan"],
              "coverage": actual["coverage"], "six_minute_delivery_and_cost": actual["six_minute_delivery_and_cost"],
              "geometry": actual["geometry"], "ring_evidence": evidence}
    record["comparison_id"] = sha256(central_access.encode(record)).hexdigest()
    return record, networks, context


def _name(record, key):
    if key in NAMES:
        return NAMES[key]
    return record["ring_evidence"]["layout_options"][key]["name"]


def report(record):
    rows = record["summary"]
    key = record["display_trial"]
    base, selected, old, single = (rows[code] for code in ("current", key, "previous", "one-ring"))
    gap = selected["minimum_ring_separation_m"] / 1000
    overlay = record["ring_evidence"]["overlay"]
    route = selected["rings"]["M15"]
    minimum_km = record["ring_evidence"]["geometry_search"]["minimum_required_separation_m"] / 1000
    service = record["same_train_km_metropolitan"]["variants"]["current"]["service"]["running_train_km_day"]
    base_wins = (selected["housing_two_changes_pct"] < base["housing_two_changes_pct"]
                 or selected["walk_worldpop_pct"] < base["walk_worldpop_pct"]
                 or selected["wide_angle_served_pct"] < base["wide_angle_served_pct"])
    decision = ("Keep the published network as the service reference. The compact network sacrifices some of its measured "
                "access or journey reach in exchange for fewer lines and less duplication."
                if base_wins else "The compact network merits the next engineering comparison on the strength of these service results.")
    lines = ["# Baghdad compact rings and through routes", "",
             f"A compact inner loop can maintain at least **{minimum_km:g} km** of horizontal clearance from the outer ring. "
             f"The tested loop runs **{route['route_km']:.2f} km** via the {overlay['bridges'][0]} and {overlay['bridges'][1]} "
             f"road corridors. At its closest point the rings are **{gap:.2f} km** apart, compared with "
             f"**{old['minimum_ring_separation_m']/1000:.2f} km** in the previous two-ring study.", "",
             decision, "",
             "![Baghdad’s previous and compact two-ring layouts at the same scale, with an inset of the two rings](maps/baghdad-spaced-rings.png)", "",
             "[Current city map](maps/baghdad-network.png) · [Previous ring-and-grid study](RING-GRID.md) · "
             "[Compact network GIS](maps/baghdad-spaced-rings.geojson) · [Machine results](spaced-rings.json)", "",
             "## Route structure and station spacing", "",
             f"The compact inner loop has {route['interchanges']} interchange sites in the displayed layout. "
             f"The lines joining both rings directly are {', '.join(selected['direct_spokes'])}. The outer ring restores "
             f"{record['ring_evidence']['outer']['route_km_added']:.2f} km of the former M09 alignment. "
             "The separation rule applies to the complete alignments. Stations on each ring can be spaced for local walking access.", "",
             "| Layout | Lines | Route km | Distinct station sites | Site pairs within 280 m | Close parallel pair-km |",
             "|---|---:|---:|---:|---:|---:|"]
    order = ["current", "previous", "overlay", key, "one-ring"]
    order += [code for code in rows if code not in order]
    order = list(dict.fromkeys(order))
    for code in order:
        row = rows[code]
        lines.append(f"| {_name(record, code)} | {row['lines']} | {row['route_km']:.2f} | {row['stations']} | "
                     f"{row['close_site_pairs']} | {row['parallel_pair_km']:.2f} |")
    lines.extend(["", "The close-parallel screen counts each pair of lines where they run for at least 2 km within 1 km of "
                  "each other with similar directions. The station screen counts distinct site pairs by straight-line distance. "
                  "The consolidation model preserves named centres and rail interchanges. Nearby calls are removed or moved only where "
                  "the mapped alignments and a dry, short, two-way walk support the change. The machine results list every tested "
                  "withdrawal, station change, retained walking connection and rejected proposal.", "",
                  "## Walking access and journeys", "",
                  f"The journey comparisons use equal effort of **{service:,.0f} running train-km per day** across an 18-hour service day. "
                  "Walking access follows mapped streets from WorldPop and GHSL population cells. "
                  "The housing sample applies a hard maximum of two changes to six central destinations. "
                  "Wide-angle trips run between outlying districts on different sides of central Baghdad.", "",
                  "| Layout | Walk ≤1.2 km WorldPop | Walk ≤1.2 km GHSL | All metro trips served | Wide-angle trips served | Housing to centre ≤2 changes |",
                  "|---|---:|---:|---:|---:|---:|"])
    for code in order:
        row = rows[code]
        lines.append(f"| {_name(record, code)} | {row['walk_worldpop_pct']:.2f}% | {row['walk_ghsl_pct']:.2f}% | "
                     f"{row['metro_served_pct']:.2f}% | {row['wide_angle_served_pct']:.2f}% | {row['housing_two_changes_pct']:.2f}% |")
    lines.extend(["", f"On the same simplified routes, adding the inner loop changes wide-angle reach from "
                  f"{single['wide_angle_served_pct']:.2f}% to {selected['wide_angle_served_pct']:.2f}% and housing-to-centre reach "
                  f"within two changes from {single['housing_two_changes_pct']:.2f}% to {selected['housing_two_changes_pct']:.2f}%. "
                  f"For the wide-angle trips served by both the compact layout and the published map, the 90th-percentile journey "
                  f"time changes from {selected['same_trip_p90_reference_min']:.1f} to {selected['same_trip_p90_trial_min']:.1f} minutes. "
                  "Trip assignments use synthetic demand. The published rail layout has been retained.", "",
                  "## Construction, labour and cost", "",
                  "Delivery estimates use the same civil rates and a uniform six-minute directional interval. Track-km count both tracks. "
                  "The programme day is the last standard-deck handover day in the model, counted from mobilisation.", "",
                  "| Layout | Track-km | Paid casting, haul and erection hours | Deck day | Trainsets with spares | Installed US$bn | 30-year present US$bn |",
                  "|---|---:|---:|---:|---:|---:|---:|"])
    for code in order:
        row = rows[code]
        lines.append(f"| {_name(record, code)} | {row['track_km']:,.2f} | {row['paid_crew_hours']:,.0f} | "
                     f"{row['standard_deck_handover_day']:,.0f} | {row['fleet_trainsets']} | "
                     f"{row['installed_usd_bn']:.2f} | {row['whole_life_usd_bn']:.2f} |")
    outer = record["ring_evidence"]["outer"]["outer_gis_context"]
    lines.extend(["", "The inner ring follows mapped road corridors. Rail curves, grades, fit at transfer stations, "
                  "and dedicated river structures require engineering. The restored outer alignment also includes "
                  f"{outer['crossings_above_provisional_span_limit']} mapped water reaches beyond the 550 m screening bound. "
                  "Special crossing premiums remain unpriced. The figures are modelled planning allowances in 2026 US dollars.", "",
                  "Verify with `tools/automation/osr-python -m cities.Baghdad.spaced_ring_comparison --check`. "
                  f"The published reference is pinned at `{record['reference_revision']}`.", "",
                  f"Comparison `{record['comparison_id']}`.", ""])
    return "\n".join(lines)


def draw(record, networks, context):
    from io import BytesIO

    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon
    import numpy as np

    from . import central_service_map

    key = record["display_trial"]
    old, _ = _prior_map()
    chosen = networks[key]
    summary = record["summary"][key]
    paper, ink, outer, inner = "#f7f5ee", "#183742", "#087d77", "#ba4e22"
    fig, axes = plt.subplots(1, 3, figsize=(16, 7.8),
                             gridspec_kw={"left": .04, "right": .976, "top": .82, "bottom": .165, "wspace": .08})
    fig.patch.set_facecolor(paper)
    water, rivers, roads = central_service_map.source_geometry(context)
    extent = np.concatenate([line["geometry"] for group in (old, chosen["lines"]) for line in group.values()])
    bounds = extent.min(axis=0) - .006, extent.max(axis=0) + .006
    ring_pts = np.concatenate([chosen["lines"][code]["geometry"] for code in ("M09", "M15")])
    zoom = ring_pts.min(axis=0) - .008, ring_pts.max(axis=0) + .008
    colors = {"M09": outer, "M15": inner}
    for ax, lines, label, limits in zip(
        axes, (old, chosen["lines"], chosen["lines"]),
        ("Previous two-ring grid", "Simplified compact network", "Ring detail"), (bounds, bounds, zoom), strict=True
    ):
        ax.set_facecolor("#f3ecdf")
        ax.add_collection(PatchCollection([Polygon(path, closed=True) for path in water],
                                           facecolor="#c0dfe5", edgecolor="none", zorder=1))
        ax.add_collection(LineCollection(rivers, colors="#86b7c0", linewidths=.9, zorder=1.1))
        ax.add_collection(LineCollection(roads, colors="#b6ac9d", linewidths=.25, alpha=.42, zorder=2))
        for code, line in lines.items():
            lw = 2.8 if code in colors else .76
            z = 5 if code in colors else 3
            if code in colors:
                ax.plot(*np.asarray(line["geometry"]).T, color=paper, linewidth=4.7, zorder=z - .2)
            ax.plot(*np.asarray(line["geometry"]).T, color=colors.get(code, "#667d87"), linewidth=lw,
                    alpha=1 if code in colors else .70, zorder=z)
        if ax is axes[2]:
            loop = chosen["lines"]["M15"]
            for stop in loop["station_ids"]:
                site = chosen["stations"][stop]
                ax.scatter(*site["coordinates"], s=29 if len(site["lines"]) > 1 else 12, facecolors=paper,
                           edgecolors=inner, linewidths=1.1, zorder=6)
            first = np.asarray(summary["nearest_inner_coordinates"])
            last = np.asarray(summary["nearest_outer_coordinates"])
            ax.plot(*np.stack([first, last]).T, color="#282b3f", linestyle=(0, (3, 2)), linewidth=1.55, zorder=7)
            ax.annotate(f"{summary['minimum_ring_separation_m']/1000:.2f} km", (first + last) / 2,
                        xytext=(4, 4), textcoords="offset points", fontsize=9, weight="bold", color=ink, zorder=8,
                        bbox={"boxstyle": "round,pad=.24", "fc": paper, "ec": "none"})
        lo, hi = limits
        ax.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), xticks=[], yticks=[],
               aspect=holistic_network.LOCAL_METRES[1] / holistic_network.LOCAL_METRES[0])
        for spine in ax.spines.values():
            spine.set_color("#d5cab5")
        ax.set_title(label, fontsize=13, weight="bold", color=ink, loc="left", pad=10)
    fig.text(.04, .94, "Baghdad | A compact inner ring", color=ink, size=25, weight="bold")
    fig.text(.041, .89, "Two continuous alignments with a minimum five-kilometre separation",
             color="#405761", size=12)
    handles = [Line2D([], [], color=color, lw=width, label=label) for color, width, label in
               ((outer, 3, "Outer ring"), (inner, 3, "Inner ring"), ("#667d87", 1.5, "Other rail routes"))]
    handles.append(Line2D([], [], color="#282b3f", linestyle="--", label="Closest approach"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .086), ncol=4, frameon=False,
               fontsize=10, labelcolor=ink)
    fig.text(.04, .046, "First two panels use the same scale. GIS planning alignments and basemap © OpenStreetMap contributors.",
             color="#405761", size=9)
    output = BytesIO()
    fig.savefig(output, format="png", dpi=150, facecolor=paper)
    plt.close(fig)
    return output.getvalue()


def outputs(record, networks, context):
    key = record["display_trial"]
    selected = networks[key]
    features = holistic_network.geojson(selected)
    gap = record["summary"][key]
    features["features"].append({
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": [
            gap["nearest_inner_coordinates"], gap["nearest_outer_coordinates"]]},
        "properties": {"kind": "minimum-ring-clearance", "minimum_separation_m": gap["minimum_ring_separation_m"]},
    })
    features["comparison_id"] = record["comparison_id"]
    features["trial"] = key
    return {REPORT: report(record).encode(), RECORD: central_access.encode(record),
            FIGURE: draw(record, networks, context), GEOJSON: central_access.encode(features)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--publish", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--output", type=Path)
    parser.add_argument("--baseline", type=Path, default=grid.BASELINE)
    args = parser.parse_args()
    out = args.output or grid.CITY
    with disk_reservation(central_access.ROOT, out, "Baghdad compact rings comparison", 96 << 20):
        record, networks, context = evaluate(args.baseline)
        for path, content in outputs(record, networks, context).items():
            target = out / path.relative_to(grid.CITY)
            if args.check:
                actual = target.read_bytes()
                equal = central_access.map_pixels_match(actual, content) if path == FIGURE else actual == content
                if not equal:
                    raise SystemExit(f"Regenerate the compact rings comparison. {target.name} differs.")
            else:
                write(target, content)
        print(record["comparison_id"])


if __name__ == "__main__":
    main()
