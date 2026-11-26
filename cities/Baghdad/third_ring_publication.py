"""Publish the bounded three-ring and short-line withdrawal comparison for Baghdad."""

import argparse
import gzip
from io import BytesIO
from pathlib import Path

import numpy as np

from engineering.performance import disk_reservation
from engineering.station_rail.publication import write

from . import central_access, central_service_map, holistic_network, third_ring_study as study


REPORT = Path("THREE-RING-STUDY.md")
DATA = Path("three-ring-study.json.gz")
MAP = Path("maps/baghdad-three-ring-comparison.png")
GEOJSON = Path("maps/baghdad-three-ring-trial.geojson")
NAMES = {"published": "Published two rings", "suburban-orbital": "Suburban rings, short routes removed",
         "suburban-road-corridors": "Suburban rings aligned to mapped roads",
         "suburban-interchanges": "Suburban rings with consolidated stations", "custom-layout": "Edited network"}


def name(code):
    return NAMES.get(code, code.replace("-", " ").capitalize())


def _pct(value):
    return f"{value:.2f}%" if value is not None else "—"


def _money(value):
    return f"{value / 1000:.2f}"


def report(record):
    reference = record["summary"]["published"]
    selected = record["selection"]["illustrated_trial"]
    eligible = record["selection"]["eligible_replacement"]
    chosen = record["summary"][selected] if selected else reference
    text = ["# Baghdad · Suburban rings and through routes", "",
            "The middle ring targets neighbourhoods previously served by small standalone lines. "
            f"The planning target is about {study.MIDDLE_TARGET_GAP_M / 1000:g} km from the outer ring, "
            "with routes adapted to the areas they serve. "
            "A direct shared ring station on each bank shortens trips across the orbital network.", ""]
    if selected:
        intro = (f"**{name(selected)}** is the illustrated trial. It has **{chosen['short_count']} "
                 f"standalone routes up to {study.SHORT_KM:g} km**, **{chosen['middle_ring_through_count']} straight "
                 f"cross-Tigris services connecting the central and suburban rings**, and **{chosen['transfer_stations']} shared station sites**. "
                 f"The published two-ring network has {reference['short_count']} short routes.")
        text += [intro, ""]
    if eligible:
        text += [f"**{name(eligible)}** clears the digital replacement screen. Land, bridge and station design remain open.", ""]
    else:
        text += ["The published two-ring plan remains the planning reference while the trial’s open checks are resolved.", ""]
    text += ["![Baghdad network comparison with direct ring transfers and cross-Tigris services](maps/baghdad-three-ring-comparison.png)", "",
             "[Current proposal](PROPOSAL.md) · [Two-ring reference](STRAIGHT-THROUGH-NETWORK.md) · "
             "[Editable trial GIS](maps/baghdad-three-ring-trial.geojson) · [Machine results](three-ring-study.json.gz)", "",
             "## Network and access", "",
             "| Layout | Rings | Services | Short routes | Cross-Tigris links to inner and middle rings | Full through services | Route-km | Sites | Shared sites | Parallel pair-km |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for code, row in record["summary"].items():
        text.append(f"| {name(code)} | {len(row['rings'])} | {row['lines']} | {row['short_count']} | "
                    f"{row['middle_ring_through_count']} | {row['through_count']} | "
                    f"{row['route_km']:.2f} | {row['stations']} | {row['transfer_stations']} | {row['parallel_pair_km']:.2f} |")
    housing = record["housing"]["variants"]["published"]["service"]
    text += ["", f"The passenger models use **{housing['running_train_km_day']:,.0f} scheduled train-km/day**. "
             "All stops are served in both directions. A longer route portfolio has a longer headway at this fixed running "
             "budget. The housing model explicitly searches paths with at most two changes. The wide-district column reports "
             "what share finds a least-generalised-cost route with up to two changes.", "",
             "| Layout | WorldPop walk 1.3 km | GHSL walk 1.3 km | WorldPop beyond M09 served | Housing ≤2 changes | Wide-district ≤2 changes | Mean headway |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    worldpop = record["coverage"]["worldpop-2026"]
    for code, row in record["summary"].items():
        fringe = worldpop[code]["1300"]["district_access_pct"]["outside_existing_outer_ring"]
        text.append(f"| {name(code)} | {_pct(row['worldpop_1300_pct'])} | {_pct(row['ghsl_1300_pct'])} | "
                    f"{_pct(fringe)} | {_pct(row['housing_two_changes_pct'])} | {_pct(row['wide_two_changes_pct'])} | "
                    f"{row['headway_s']/60:.2f} min |")
    text += ["", "### Neighbourhoods previously served by short lines", "",
             "This subset could walk to a short-line stop within 1.3 km on the published network and had no "
             "other station within the same walking distance. The final column counts residents who rely on "
             "standalone middle-ring sites in the trial. Shared stations that already exist on a long route "
             "are assigned to that route’s catchment.", "",
             "| Layout | Population grid | Former short-line catchment | Still within 1.3 km | Middle-ring-only replacement | Lost access |",
             "|---|---|---:|---:|---:|---:|"]
    for code in record["summary"]:
        for dataset in ("worldpop-2026", "ghsl-2025"):
            row = record["coverage"][dataset][code]["1300"]["short_route_catchments"]
            original, reached, middle = (row[field] for field in ("baseline_short_only_people",
                "retained_access_people", "served_by_middle_only_sites_people"))
            text.append(f"| {name(code)} | {dataset} | {original:,} | {reached:,} | {middle:,} | {original - reached:,} |")
    text += ["", "The map marks the largest remaining gaps in former short-line catchments on a 1 km grid. "
             "The machine results include the coordinates, metropolitan gains and losses, "
             "a 1.2 km walking sensitivity, and access to named destinations.", ""]

    if selected and "middle_outer_gap_km" in chosen["orbital_metrics"]:
        metrics = chosen["orbital_metrics"]
        gaps = metrics["middle_outer_gap_km"]
        text += ["## Ring spacing and direct interchanges", "",
                 f"The median distance from middle to outer ring is **{gaps['median']:.2f} km**, with the central "
                 f"80% of sampled points between **{gaps['p10']:.2f} and {gaps['p90']:.2f} km**. "
                 "The distance can fall to zero at a mapped shared station. Both tracks retain their own alignment.", "",
                 f"The inner ring’s close non-adjacent reaches fall from "
                 f"**{reference['orbital_metrics']['inner_foldback_km']:.2f} km** to "
                 f"**{metrics['inner_foldback_km']:.2f} km**. The screen compares points within 850 m of each other "
                 "and at least 1.5 km apart along the ring.", "",
                 "| Bank | Shared station | Rings | Coordinates |", "|---|---|---|---|"]
        for contact in sorted(metrics["inter_ring_contacts"], key=lambda row: row["bank"]):
            site = contact["station_id"]
            station = record["layouts"][selected]["stations"][site]
            lon, lat = station["coordinates"]
            text.append(f"| {contact['bank']} | {station['name']} ({site}) | {' / '.join(contact['rings'])} | "
                        f"{lon:.5f}° E, {lat:.5f}° N |")
        text.append("")

    if selected:
        audit = record["layout_trials"][selected]
        if "withdrawal" in audit:
            withdrawal = audit["withdrawal"]
            closed = len(withdrawal["former_short_line_stations_closed"])
            missing = len(withdrawal["stops_without_a_replacement_walk"])
            text += ["## Route withdrawal and station consolidation", "",
                     f"The trial removes **{withdrawal['withdrawn_route_km']:.2f} route-km** across "
                     f"**{len(withdrawal['withdrawn_routes'])} short routes**. Of {closed} former stop sites "
                     f"that close, {missing} lack a replacement street walk within 1.3 km.", ""]
        if "station_consolidation" in audit:
            before = audit["station_consolidation"]["station_sites_before"]
            shared = audit["shared_sites_before_consolidation"]
            text += [f"Consolidation changes {before} sites to {chosen['stations']} sites and "
                     f"{shared} shared stations to {chosen['transfer_stations']}. "
                     "A shared station requires an actual mapped connection and reconciled calls. "
                     "Nearby sites that cannot be combined remain visible in the GIS.", ""]
        text += ["The straight trunk screen requires a Tigris crossing and a route within 1.10 times its end-to-end chord. "
                 "The full through-service count additionally requires shared stations on all rings and both terminals "
                 "outside the outermost ring.", ""]
        for code in ("published", selected):
            routes = record["summary"][code]["through_lines"]
            text.append(f"- **{name(code)}** qualifies {', '.join(routes) if routes else 'no routes'}.")
        if "orbitals" in audit:
            road = audit["orbitals"]["alignments"]
            text += ["", "Mapped major-road alignment support is "
                     + ", ".join(f"{road[code]['major_road_support_share']*100:.1f}% on {code}" for code in study.RINGS)
                     + ". Each proposed crossing and elevated alignment requires site design.", ""]
        joins = audit.get("trunk_joins", [])
        if joins:
            text += ["", "New trunk transfers to the rings use exact intersections on dry mapped streets. "
                     "Nearby single-service calls are folded into the interchange only when their replacement walk is mapped.", ""]
            for join in joins:
                text.append(f"- **{join['line']} to {join['ring']}** · {join['station_id']}.")
    if rejection := record["layout_trials"].get("suburban-road-corridors", {}).get("rejection_reason"):
        text += ["", f"The road-following variant was screened out. {rejection}.", ""]
    text += ["", "To evaluate an edited layout, change its line geometry and ordered station IDs in the trial GeoJSON. "
             "Omit any line to withdraw it. The evaluator rebuilds transfers, service and cost for the full network.", "",
             "`./osr design railway baghdad-three-rings --layout revised.geojson --output build/baghdad-layout-trial`", "",
             "## Like-for-like capital and service allowances", "",
             "The priced cases use the same six-minute budget offer, unit rates and curved-stock method. The six-minute costing "
             "offer sets fleet and supply quantities separately from the matched train-km passenger comparison.", "",
             "| Layout | Running-track km | Fleet | Standard casting, haul and erection hours | Base installed US$bn | Annual operation US$bn | 30-year present US$bn |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for code, row in record["costs"].items():
        cost = row["cost_cases"]["base"]
        text.append(f"| {name(code)} | {row['running_track_km']:,.2f} | {row['fleet_trainsets']:,} | "
                    f"{row['standard_stock_paid_hours']:,.0f} | {_money(cost['installed_planning_usd_m'])} | "
                    f"{_money(cost['annual_operations_total_usd_m'])} | {_money(cost['whole_life_present_usd_m'])} |")
    text += ["", "| Layout | Concurrent yards | Last standard-stock day | Curved girder pieces | Route-km on unresolved beam or crossing forms |",
             "|---|---:|---:|---:|---:|"]
    for code, row in record["costs"].items():
        text.append(f"| {name(code)} | {row['yard_sites']} | {row['standard_stock_last_deck_day']:,.0f} | "
                    f"{row['curved_pieces']:,} | {row['held_service_route_km']:.2f} |")
    text += ["", "These allowances include the counted recurring stock and curved-piece premium. New bridges, station "
             "interfaces and other held structures need separate design and prices. The model leaves the project opening date open.", "",
             "## Decision checks", ""]
    for code, holds in record["selection"]["holds"].items():
        text.append(f"- **{name(code)}** · " + (". ".join(holds) + "." if holds else "Clears the layout and matched-access screen."))
    text += ["", "Reproduce with `OPENBLAS_NUM_THREADS=1 ./osr design railway baghdad-three-rings --check`.", "",
             f"Publication `{record['publication_id']}`.", ""]
    return "\n".join(text)


def draw(record, context):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon

    selected = record["selection"]["illustrated_trial"] or "published"
    keys = ("published", selected) if selected != "published" else ("published",)
    water, rivers, roads = central_service_map.source_geometry(context)
    zoom_lines = [line["geometry"] for line in record["layouts"][selected]["lines"].values()]
    extent = np.concatenate(zoom_lines)
    lower, upper = extent.min(axis=0) - .008, extent.max(axis=0) + .008
    paper, ink = "#faf7ef", "#193742"
    color = {"M15": "#b54930", "M09": "#008377", "M16": "#5655a5"}
    blue, short, local = "#245bab", "#b07926", "#818b8c"
    figure, axes = plt.subplots(1, len(keys), squeeze=False, figsize=(16, 8.4) if len(keys) > 1 else (10, 8.5),
                                gridspec_kw={"left": .04, "right": .975, "bottom": .14, "top": .84, "wspace": .08})
    figure.patch.set_facecolor(paper)
    figure.text(.047, .946, "Baghdad’s suburban ring and through routes", color=ink, fontsize=26, weight="bold")
    figure.text(.047, .895, "Middle-ring coverage, direct interchanges and a network without short standalone routes",
                color="#465e68", fontsize=12)
    for axis, key in zip(axes[0], keys, strict=True):
        net, row = record["layouts"][key], record["summary"][key]
        axis.set_facecolor("#f0ece4")
        axis.add_collection(PatchCollection([Polygon(points, closed=True) for points in water], facecolor="#bed9df",
                                             edgecolor="none", zorder=1))
        axis.add_collection(LineCollection(rivers, colors="#80afbb", linewidths=1, zorder=1.2))
        axis.add_collection(LineCollection(roads, colors="#b2aa9a", linewidths=.30, alpha=.35, zorder=2))
        through = row["through_lines"] if key == "published" else row["middle_ring_through_lines"]
        for code, line in net["lines"].items():
            pts = np.asarray(line["geometry"]).T
            shade = color.get(code, blue if code in through else short if code in row["short_lines"] else local)
            emphasize = code in color or code in through
            if emphasize:
                axis.plot(*pts, color=paper, linewidth=4, zorder=4)
            axis.plot(*pts, color=shade, linewidth=2.25 if emphasize else 1.25 if shade == short else .75,
                      alpha=1 if emphasize or shade == short else .73, zorder=5 if emphasize else 3)
        interchange = {site for code in study.RINGS if code in net["lines"]
                       for site in net["lines"][code]["station_ids"] if len(net["stations"][site]["lines"]) > 1}
        pts = np.array([net["stations"][site]["coordinates"] for site in sorted(interchange)])
        if pts.size:
            axis.scatter(*pts.T, s=13, edgecolors=ink, facecolors=paper, linewidths=.58, zorder=6)
        for contact in row["orbital_metrics"].get("inter_ring_contacts", []):
            xy = net["stations"][contact["station_id"]]["coordinates"]
            axis.scatter(*xy, s=90, marker="D", facecolor="#fadc72", edgecolor=ink, linewidths=1.2, zorder=7)
            axis.annotate(contact["bank"], xy, xytext=(8, -10), textcoords="offset points", color=ink,
                          fontsize=9, bbox={"fc": paper, "ec": "none", "pad": .6}, zorder=8)
        cells = record["coverage"]["worldpop-2026"][key]["1300"]["short_route_catchments"]["largest_unserved_cells"]
        if cells:
            axis.scatter(*np.array([site["coordinates"] for site in cells]).T, s=38, color="#a12642",
                         marker="x", linewidths=1.5, zorder=8)
        axis.set(xlim=(lower[0], upper[0]), ylim=(lower[1], upper[1]), xticks=[], yticks=[],
                 aspect=holistic_network.LOCAL_METRES[1] / holistic_network.LOCAL_METRES[0])
        label = f"{name(key)}  ·  {row['short_count']} short lines"
        axis.set_title(label, loc="left", fontsize=12, weight="bold", color=ink, pad=9)
        for spine in axis.spines.values():
            spine.set_color("#c5beb0")
    legend = [Line2D([], [], color=shade, lw=2.5, label=label) for shade, label in (
        (color["M15"], "Inner ring"), (color["M09"], "Middle ring"), (color["M16"], "Outer ring"),
        (blue, "Straight cross-Tigris trunk"), (short, "Short route ≤8 km"), (local, "Other routes"))]
    legend.append(Line2D([], [], color="#a12642", marker="x", linestyle="none", label="Lost short-route access"))
    figure.legend(handles=legend, loc="lower center", bbox_to_anchor=(.5, .077), frameon=False, ncol=7,
                  labelcolor=ink, fontsize=10)
    figure.text(.047, .036, "Same scale. Circles mark orbital transfers and diamonds mark direct connections between rings. Basemap © OpenStreetMap contributors.",
                color="#465e68", fontsize=9.3)
    buffer = BytesIO()
    figure.savefig(buffer, dpi=155, format="png", facecolor=paper)
    plt.close(figure)
    return buffer.getvalue()


def outputs(record, context):
    selected = record["selection"]["illustrated_trial"] or "published"
    data = holistic_network.geojson(record["layouts"][selected])
    data.update(publication_id=record["publication_id"], trial=selected, study_status=record["study_status"])
    return {REPORT: report(record).encode(), DATA: gzip.compress(central_access.encode(record), mtime=0),
            MAP: draw(record, context), GEOJSON: central_access.encode(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--output", type=Path)
    parser.add_argument("--layout", type=Path, help="Compare a complete edited GeoJSON network")
    args = parser.parse_args()
    if args.layout is not None and args.output is None:
        parser.error("Use --output for the edited network comparison")
    target = args.output or study.CITY
    with disk_reservation(central_access.ROOT, target, "Baghdad three-ring comparison", 96 << 20):
        record, context = study.evaluate(layout=args.layout)
        for path, value in outputs(record, context).items():
            dest = target / path
            if args.check:
                current = dest.read_bytes()
                same = central_access.map_pixels_match(current, value) if path == MAP else current == value
                if not same:
                    raise SystemExit(f"Regenerate the three-ring comparison. {path} differs.")
            else:
                write(dest, value)
        print(record["publication_id"])


if __name__ == "__main__":
    main()
