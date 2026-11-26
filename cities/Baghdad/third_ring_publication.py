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
NAMES = {"published": "Published two rings", "two-rings-trimmed": "Two rings, short lines tested",
         "ring-only": "Compact third ring with existing lines", "wider-ring": "Wider third ring with existing lines",
         "road-assisted-ring": "Road-assisted third ring", "retained-through": "Third ring with extended trunks",
         "added-through": "Third ring with additional trunks", "shifted-ring-through": "Third ring with G09 extension",
         "realigned-inner-ring": "Replaced inner ring", "from-empty-three": "29-line portfolio, three rings",
         "from-empty-optional": "29-line portfolio, rings optional", "custom-layout": "Edited network"}


def name(code):
    base = code.removesuffix("-trimmed")
    if code == "two-rings-trimmed":
        return NAMES[code]
    suffix = " and short lines tested" if code != base else ""
    return NAMES.get(base, base.replace("-", " ").capitalize()) + suffix


def _pct(value):
    return f"{value:.2f}%" if value is not None else "—"


def _money(value):
    return f"{value / 1000:.2f}"


def report(record):
    reference = record["summary"]["published"]
    selected = record["selection"]["illustrated_trial"]
    eligible = record["selection"]["eligible_replacement"]
    chosen = record["summary"][selected] if selected else reference
    ring = record["rings"]["selected"]
    text = ["# Baghdad · Three rings and through routes", "",
            "Test a third orbital outside M09, longer cross-city services and the removal of short routes. "
            "All alternatives use the same GIS, demand samples and running train-km.", ""]
    if selected:
        intro = (f"**{name(selected)}** is the illustrated trial. It has **{chosen['short_count']} "
                 f"routes up to {study.SHORT_KM:g} km** and **{chosen['through_count']} qualifying through services**. "
                 f"The published two-ring network has {reference['short_count']} short routes and "
                 f"{reference['through_count']} through services under the same definition, applied to its two rings.")
        text += [intro, ""]
    else:
        text += ["No tested third ring supplied the required mapped interchanges.", ""]
    if eligible:
        text += [f"**{name(eligible)}** clears the digital replacement screen. Its land, bridges and physical interfaces remain open.", ""]
    else:
        text += ["The combined simplification and passenger-access screen holds the tested three-ring designs.", ""]
    text += ["![Baghdad network comparison with ring transfers and cross-Tigris services](maps/baghdad-three-ring-comparison.png)", "",
             "[Current proposal](PROPOSAL.md) · [Published two-ring study](STRAIGHT-THROUGH-NETWORK.md) · "
             "[Three-ring trial GIS](maps/baghdad-three-ring-trial.geojson) · [Simulation and source record](three-ring-study.json.gz)", "",
             "## Network and access", "",
             "| Layout | Rings | Services | Short lines ≤8 km | Qualifying through lines | Route-km | Sites | Parallel pair-km |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for code, row in record["summary"].items():
        text.append(f"| {name(code)} | {len(row['rings'])} | {row['lines']} | {row['short_count']} | {row['through_count']} | "
                    f"{row['route_km']:.2f} | {row['stations']} | {row['parallel_pair_km']:.2f} |")
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
    text += ["", "| Layout | WorldPop gained access | WorldPop lost access | GHSL gained access | GHSL lost access |",
             "|---|---:|---:|---:|---:|"]
    for code in record["summary"]:
        rows = [record["coverage"][source][code]["1300"] for source in ("worldpop-2026", "ghsl-2025")]
        values = [row[key] for row in rows for key in ("newly_served_people", "formerly_served_people_losing_access")]
        text.append(f"| {name(code)} | {' | '.join(f'{value:,}' for value in values)} |")
    text += ["", "Both population datasets use mapped street paths from the same regional window. The machine results "
             "include the 1.2 km sensitivity, named-centre access, trip and crowding diagnostics, actual removed-stop walks "
             "and the whole-route withdrawal assessments. Walking coverage and passenger weights are planning estimates.", ""]
    if ring is not None:
        row = record["summary"]["ring-only"]["rings"]["M16"]
        bridge = record["layout_trials"]["ring-only"]["new_tigris_crossings"]
        text += ["## Third ring geometry", "",
                 f"The buffered M16 candidate is **{row['route_km']:.2f} km** long with a **{ring['minimum_ring_separation_m']/1000:.2f} km** "
                 f"minimum gap to M09, {row['stations']} station sites and {row['interchanges']} shared passenger sites before "
                 "the through-service edits. The search tests different setbacks and curve simplifications. It checks nesting, "
                 "dry shared stations, mapped road proximity and potential water crossings.", "",
                 f"The compact candidate calls for {len(bridge)} new Tigris crossings. Major-road proximity supports part of the "
                 f"trace ({ring['major_road_support_share']*100:.1f}% under the directional screen). Land alignment, "
                 "clearances, public access, hydraulic design and construction costs need route-level development.", ""]
        text += ["| Orbital trace | Nominal setback | Minimum gap | Length | Distinct transfer lines | Major-road proximity | Provisional water contacts |",
                 "|---|---:|---:|---:|---:|---:|---:|"]
        for key in ("ring-only", "wider-ring", "road-assisted-ring"):
            if key in record["summary"]:
                option = record["layout_trials"][key]
                text.append(f"| {name(key)} | {option['target_setback_m']/1000:.2f} km | "
                            f"{option['minimum_ring_separation_m']/1000:.2f} km | {option['one_way_km']:.2f} km | "
                            f"{len(option['screened_transfer_lines'])} | {option['major_road_support_share']*100:.1f}% | "
                            f"{option['provisional_crossing_count']} |")
        text.append("")
    text += ["## Rerouting and route withdrawal", "",
             "The published plan is a comparator and an alignment library. The portfolio search starts with an empty set, "
             "then chooses connected routes by measured walking coverage and useful connections. It tests a three-ring requirement "
             "and a separate run with every ring optional. Named destinations, including the Airport terminal, need a street path "
             "to the proposed service. A route may serve that need under any geometry or identifier.", "",
             "To evaluate a fully edited layout, export the current or trial GeoJSON and edit its line and station features. "
             "Omit any line to withdraw it. Give a rerouted line its new WGS84 path and ordered station IDs, with an individual point "
             "for each station. The evaluator rebuilds station memberships, shared transfers and route chainage. It prices the "
             "edited network alongside the published reference.", "",
             "`./osr design railway baghdad-three-rings --layout revised.geojson --output build/baghdad-layout-trial`", "",
             "A qualifying through route starts and ends beyond the outermost ring, crosses the mapped Tigris centreline, "
             "has actual shared passenger stations where it crosses all its rings and stays within 1.10 times its end-to-end chord. "
             "A qualifying crossing uses a shared platform site. Added routes use the existing bridge-approach and water screen.", ""]
    for code in dict.fromkeys(("published", selected)):
        if code is None:
            continue
        routes = record["summary"][code]["through_lines"]
        text.append(f"- **{name(code)}** qualifies {', '.join(routes) if routes else 'no routes'} under the full through-route definition.")
    text += ["", "| Withdrawal trial | Removed routes | Station sites taken out of service |",
             "|---|---|---:|"]
    for code, audit in record["layout_trials"].items():
        if "cumulative_station_replacement_paths" not in audit:
            continue
        actions = audit["actions"]
        removed = ", ".join(row["line_id"] for row in actions)
        closed = sum(len(row["closed_stations"]) for row in actions)
        text.append(f"| {name(code)} | {removed or 'None passed this access screen'} | {closed} |")
    for code in ("from-empty-three", "from-empty-optional"):
        audit = record["layout_trials"].get(code, {})
        if audit.get("chosen"):
            keep = set(record["layouts"][code]["lines"])
            discarded = sorted(record["layouts"]["published"]["lines"].keys() - keep)
            text += ["", f"**{name(code)}** omits {len(discarded)} published routes ({', '.join(discarded)})."]
    text += ["", "A short route can be withdrawn only if the passenger graph remains connected, the protected lines and calls "
             "survive and each closed station has a mapped street walk to a remaining station within 1.3 km. Gross lost access "
             "is capped at 0.5% of the study population independently in each dataset before checking passenger journeys.", "",
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
    figure.text(.047, .946, "Could a third ring simplify Baghdad’s railway?", color=ink, fontsize=26, weight="bold")
    figure.text(.047, .895, "Three orbital routes, cross-river through services and tested short-line withdrawals",
                color="#465e68", fontsize=12)
    for axis, key in zip(axes[0], keys, strict=True):
        net, row = record["layouts"][key], record["summary"][key]
        axis.set_facecolor("#f0ece4")
        axis.add_collection(PatchCollection([Polygon(points, closed=True) for points in water], facecolor="#bed9df",
                                             edgecolor="none", zorder=1))
        axis.add_collection(LineCollection(rivers, colors="#80afbb", linewidths=1, zorder=1.2))
        axis.add_collection(LineCollection(roads, colors="#b2aa9a", linewidths=.30, alpha=.35, zorder=2))
        through = row["through_lines"]
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
        axis.set(xlim=(lower[0], upper[0]), ylim=(lower[1], upper[1]), xticks=[], yticks=[],
                 aspect=holistic_network.LOCAL_METRES[1] / holistic_network.LOCAL_METRES[0])
        label = f"{name(key)}  ·  {row['short_count']} short lines"
        axis.set_title(label, loc="left", fontsize=12, weight="bold", color=ink, pad=9)
        for spine in axis.spines.values():
            spine.set_color("#c5beb0")
    legend = [Line2D([], [], color=shade, lw=2.5, label=label) for shade, label in (
        (color["M15"], "Inner ring"), (color["M09"], "Middle ring"), (color["M16"], "Third ring"),
        (blue, "Full through route"), (short, "Short route ≤8 km"), (local, "Other routes"))]
    figure.legend(handles=legend, loc="lower center", bbox_to_anchor=(.5, .077), frameon=False, ncol=6,
                  labelcolor=ink, fontsize=10)
    figure.text(.047, .036, "Same scale in both views. Open circles mark orbital transfers. Basemap © OpenStreetMap contributors.",
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
