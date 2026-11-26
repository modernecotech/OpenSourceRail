"""Publish the centre-serving Baghdad ring, junctions and route comparison."""

import argparse
from collections import Counter
from pathlib import Path

import numpy as np

from engineering.performance import disk_reservation
from engineering.station_rail.publication import write

from . import central_access, central_ring_study as study, central_service_map, holistic_network


def _name(record, code):
    return study.NAMES.get(code) or record["layout_actions"][code]["name"]


def _metres(value):
    return f"{value:,.0f} m" if value is not None else "—"


def _pct(value):
    return f"{value:.2f}%" if value is not None else "—"


def report(record):
    key = record["display_trial"]
    case, old = (record["summary"][code] for code in (key, "prior"))
    current = record["coverage"]["worldpop-2026"]
    landmarks = current[key]["destinations_on_foot_to_ring"]
    via = current[key]["destinations_with_at_most_one_change_from_ring"]
    layout = record["layout_actions"][key]
    audit = layout.get("junction_audit", {})
    changes = Counter(row["kind"] for row in audit.get("actions", []))
    inner = case["rings"]["M15"]
    source = record["geometry_search"]["evidence"][layout["ring_source"]]
    alternate = min((code for code in record["layout_actions"] if code in record["summary"] and code != key),
                    key=lambda code: (record["summary"][code]["parallel_pair_km"],
                                      record["summary"][code]["close_site_pairs"], code), default=None)
    common = record["ring_service"]["variants"]["current"]["service"]["running_train_km_day"]
    count = len(landmarks)
    west, south, east, north = record["central_area_wsen"]
    lines = [
        "# Baghdad central ring, junctions and parallel routes", "",
        f"The **{inner['route_km']:.2f} km** inner ring puts **{case['central_ring_named_centres']} of {count}** named "
        f"central destinations and **{case['inner_walk_1300_pct']:.2f}%** of the central study population within a "
        f"**1.3 km street walk** of an inner-ring station. The previous wider ring reaches "
        f"{old['central_ring_named_centres']} destinations and {old['inner_walk_1300_pct']:.2f}% of central residents.", "",
        f"**{case['central_centres_via_connection']} of {count}** named destinations lie within a 1.3 km walk of "
        "the ring or a line that directly interchanges with it.", "",
        f"In the least-served central sector, walking coverage using any line rises from "
        f"**{old['worst_central_sector_pct']:.2f}% to {case['worst_central_sector_pct']:.2f}%**. "
        f"In the southern sector it changes from {current['prior']['sectors']['South']['network']['1300']['pct']:.2f}% "
        f"to {current[key]['sectors']['South']['network']['1300']['pct']:.2f}%.", "",
        f"The inner ring follows mapped road corridors at {' and '.join(source['bridges'])}. It has "
        f"{inner['stations']} station sites, including {inner['interchanges']} shared interchanges, and the direct "
        f"services joining both rings are **{', '.join(case['direct_routes'])}**. The minimum mapped gap is "
        f"**{case['minimum_ring_separation_m']/1000:.2f} km**. The alignment search uses the central catchment, "
        "mapped crossings and connections. The two ring traces are simple, nested and disjoint.", "",
        "![Previous and proposed central inner rings with their six study destinations](maps/baghdad-central-ring-network.png)", "",
        "[Full route and station GIS](maps/baghdad-central-ring-network.geojson) · [Machine results](central-ring-network.json) · "
        "[Previous wider-rings network](RING-NETWORK.md) · [Published city network](NETWORK.md)", "",
        "## Central destinations and districts", "",
        f"The retained central study area spans {west:g}° to {east:g}° E and {south:g}° to {north:g}° N. "
        "The six named destinations are reported separately, including those beyond the box. The nine-sector screen "
        "uses the same central bounds and the WorldPop population cells in each sector.", "",
        "| Destination | Previous walk to inner ring | Proposed walk to inner ring | Proposed walk to ring or connecting line |",
        "|---|---:|---:|---:|",
    ]
    for name, access in landmarks.items():
        before = current["prior"]["destinations_on_foot_to_ring"][name]
        lines.append(f"| {access['name']} | {_metres(before['metres'])} | {_metres(access['metres'])} | "
                     f"{_metres(via[name]['metres'])} |")
    lines.extend(["", "| Central sector | Inner-ring walk coverage, previous → proposed | Proposed coverage using any line |",
                  "|---|---:|---:|"])
    for name in study.SECTORS:
        before, after = (current[code]["sectors"][name] for code in ("prior", key))
        lines.append(f"| {name} | {_pct(before['ring']['1300']['pct'])} → {_pct(after['ring']['1300']['pct'])} | "
                     f"{_pct(after['network']['1300']['pct'])} |")
    lines.extend(["",
                  "Distances follow retained mapped paths and station-to-street connections. "
                  "The machine results also contain the GHSL population check, the number of residents in each sector "
                  "and the 1.2 km sensitivity.", ""])
    if alternate:
        alt_south = current[alternate]["sectors"]["South"]["network"]["1300"]["pct"]
        alt = record["summary"][alternate]
        lines.extend([f"The alternative **{_name(record, alternate)}** reduces parallel running to "
                      f"{alt['parallel_pair_km']:.2f} pair-km, with {alt_south:.2f}% southern-sector coverage. "
                      "The displayed alignment gives more even central access.", ""])
    lines.extend(["## Station consolidation and line changes", "",
                  f"The displayed layout has **{case['stations']} station sites** and **{case['close_site_pairs']} pairs "
                  f"within 280 m**, compared with {old['stations']} sites and {old['close_site_pairs']} close pairs "
                  f"on the previous layout. Screened close parallel running changes from **{old['parallel_pair_km']:.2f} "
                  f"to {case['parallel_pair_km']:.2f} pair-km**.", ""])
    if audit:
        limits = audit["bounds"]
        lines.extend([f"The junction pass takes the same route layout from {audit['station_sites_before']} to "
                      f"{audit['station_sites_after']} station sites, using replacement walks up to "
                      f"{limits['replacement_m']:g} m. Its audit records "
                      f"{changes.get('shared_site', 0)} shared-site merges, "
                      f"{changes.get('retire_adjacent_call', 0)} adjacent calls removed and "
                      f"{len(audit.get('links', []))} mapped walking interchanges.", ""])
    if named_calls := layout.get("named_centre_ring_calls"):
        lines.extend([f"The consolidation retains the inner-ring calls that provide the shortest qualifying "
                      f"street walks for {len(named_calls)} named destinations.", ""])
    for action in layout.get("actions", []):
        terminals = " and ".join(action["terminals"])
        lines.append(f"- **{action['line_id']}** changes at {terminals}, removing "
                     f"{action['removed_route_km']:.2f} route-km and {len(action['closed_stations'])} unique station sites.")
    if layout.get("actions"):
        lines.append("")
    holds = sorted(set(record["held_trials"].values()))
    if holds:
        lines.extend(["The following constraints held part of the search.", "",
                      *(f"- {reason.rstrip('.')}." for reason in holds), ""])
    lines.extend(["Shared junctions use common physical station coordinates on the affected alignments. Separate platforms "
                  "keep their own site and a measured pedestrian interchange when mapped paths support it. The line cuts "
                  "retain interchange terminuses. Turnbacks and accessible platform structures require design.", "",
                  "## Matched passenger and efficiency comparison", "",
                  f"Every journey model uses **{common:,.0f} daily running train-km**, the same synthetic trip weights "
                  "and walks of up to 1.3 km at each end. Housing journeys can use up to two changes. The route-km "
                  "and station registers use the same geometry as the cost model.", "",
                  "| Layout | Lines | Route km | Close station pairs | Parallel pair-km | Metropolitan walk 1.2 km / 1.3 km | Central ring walk 1.3 km | Outer trips served | Housing to centre ≤2 changes |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for code, row in record["summary"].items():
        name = f"**{_name(record, code)}**" if code == key else _name(record, code)
        lines.append(f"| {name} | {row['lines']} | {row['route_km']:.2f} | {row['close_site_pairs']} | "
                     f"{row['parallel_pair_km']:.2f} | {row['metro_walk_1200_pct']:.2f}% / {row['metro_walk_1300_pct']:.2f}% | "
                     f"{row['inner_walk_1300_pct']:.2f}% | {row['wide_trips_pct']:.2f}% | {row['housing_two_changes_pct']:.2f}% |")
    selection = record["selection"]
    admitted = key in selection["preserves_reach_and_improves_network"]
    lines.extend(["",
                  ("The displayed layout clears the matched-access screen and improves inner-ring reach and overlap."
                   if admitted else "The displayed layout is the best of the remaining comparison cases. "
                                    "The machine record retains which candidates met the matched-access and improvement screens."),
                  "Among candidates that preserve network reach and reduce both the station count and parallel running, "
                  "the selection favours coverage in the least-served central sector.",
                  f"The screen allows drops of up to {selection['allowed_walking_loss_pp']:g} points in central and metropolitan walk coverage, "
                  f"{selection['allowed_housing_loss_pp']:g} points in housing reach and "
                  f"{selection['allowed_wide_trip_loss_pp']:g} points in outer-district reach.", "",
                  "## Delivery and cost", "",
                  "The selected layout and the greatest parallel-cut alternative are priced at the same six-minute costing basis "
                  "with 2026 unit rates. Track-km count both tracks. The programme reports standard-deck handover from mobilisation.", "",
                  "| Layout | Track-km | Paid casting, haul and erection hours | Deck handover day | Installed US$bn | 30-year present US$bn |",
                  "|---|---:|---:|---:|---:|---:|"])
    for code, row in record["six_minute_delivery_and_cost"].items():
        base = row["cases"]["base"]
        lines.append(f"| {_name(record, code)} | {row['track_km']:,.2f} | {row['paid_casting_haul_and_erection_hours']:,.0f} | "
                     f"{row['standard_deck_handover_day']:,.0f} | {base['installed_planning_usd_m']/1000:.2f} | "
                     f"{base['whole_life_present_usd_m']/1000:.2f} |")
    lines.extend(["", "Rail curves, grades, junction capacities, step-free station routes and river structures remain open. "
                  "Estimates exclude special river-crossing premiums.", "",
                  "Reproduce with `OPENBLAS_NUM_THREADS=1 tools/automation/osr-python -m cities.Baghdad.central_ring_publication --check`.", "",
                  f"Comparison `{record['comparison_id']}`.", ""])
    return "\n".join(lines)


def draw(record, networks, context):
    from io import BytesIO

    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon, Rectangle

    code = record["display_trial"]
    old, chosen = networks["prior"], networks[code]
    old_lines, lines = old["lines"], chosen["lines"]
    edits = {key for key in old_lines.keys() & lines.keys()
             if key not in study.RINGS and old_lines[key]["geometry"] != lines[key]["geometry"]}
    edits |= (old_lines.keys() ^ lines.keys()) - set(study.RINGS)
    views = ("prior", code, code)
    paper, ink, outer, inner, edit = "#f8f5ee", "#183742", "#087d77", "#b14d20", "#59459a"
    fig, axes = plt.subplots(1, 3, figsize=(16.6, 7.9),
                             gridspec_kw={"left": .037, "right": .979, "wspace": .08, "top": .82, "bottom": .165})
    fig.patch.set_facecolor(paper)
    water, rivers, roads = central_service_map.source_geometry(context)
    all_routes = np.concatenate([line["geometry"] for line in lines.values()])
    west, south, east, north = record["central_area_wsen"]
    core = np.array([[west, south], [east, north]])
    landmarks = record["coverage"]["worldpop-2026"][code]["destinations_on_foot_to_ring"]
    central = np.concatenate((core, old_lines["M15"]["geometry"], lines["M15"]["geometry"],
                              [row["coordinates"] for row in landmarks.values()]))
    colors = {"M09": outer, "M15": inner}
    short_names = {"tahrir": "Tahrir", "shorja": "Shorja", "medical-city": "Medical City",
                   "karkh": "Karkh", "mansour": "Mansour", "jadriya": "Jadriya"}
    for index, (ax, case) in enumerate(zip(axes, views, strict=True)):
        network = networks[case]
        ax.set_facecolor("#f3ede3")
        ax.add_collection(PatchCollection([Polygon(points, closed=True) for points in water],
                                           facecolor="#bedde2", edgecolor="none", zorder=1))
        ax.add_collection(LineCollection(rivers, colors="#77adba", linewidths=.93, zorder=1.1))
        ax.add_collection(LineCollection(roads, colors="#ada394", linewidths=.31, alpha=.43, zorder=2))
        if index < 2:
            sectors = record["coverage"]["worldpop-2026"][case]["sectors"]
            dx, dy = (east - west) / 3, (north - south) / 3
            for i, name in enumerate(study.SECTORS):
                share = sectors[name]["ring"]["1300"]["pct"] or 0.
                ax.add_patch(Rectangle((west + (i % 3) * dx, south + (i // 3) * dy), dx, dy,
                                       linewidth=.35, edgecolor="#968e81",
                                       facecolor=(.05, .48, .45, share / 420), zorder=2.4))
            ax.add_patch(Rectangle(core[0], east - west, north - south, linewidth=.7,
                                   linestyle="--", edgecolor="#737f80", facecolor="none", zorder=2.5))
        for route, line in network["lines"].items():
            trace = np.asarray(line["geometry"]).T
            emphasize = route in colors or index == 2 and route in edits
            color = colors.get(route, edit if index == 2 and route in edits else "#79888a")
            if emphasize:
                ax.plot(*trace, color=paper, linewidth=4.4, zorder=4)
            ax.plot(*trace, color=color, linewidth=2.6 if emphasize else .78,
                    alpha=1 if emphasize else .62, zorder=5 if emphasize else 3)
        for station in network["lines"]["M15"]["station_ids"]:
            stop = network["stations"][station]
            ax.scatter(*stop["coordinates"], s=30 if len(stop["lines"]) > 1 else 9,
                       facecolors=paper, edgecolors=inner, linewidths=.89, zorder=6)
        if index < 2:
            rows = record["coverage"]["worldpop-2026"][case]["destinations_on_foot_to_ring"]
            for label, row in rows.items():
                point = row["coordinates"]
                reached = row["within_1300_m"]
                ax.scatter(*point, marker="D", s=26, facecolors="#29465b" if reached else paper,
                           edgecolors="#29465b", linewidths=.9, zorder=7)
                left = label in {"karkh", "mansour"}
                ax.annotate(short_names.get(label, row["name"]), point, xytext=(-5 if left else 5, 5),
                            textcoords="offset points", ha="right" if left else "left",
                            fontsize=8, color=ink, zorder=8,
                            bbox={"boxstyle": "round,pad=.17", "fc": paper, "ec": "none", "alpha": .93})
        bounds, margin = (central, .008) if index < 2 else (all_routes, .008)
        lo, hi = bounds.min(axis=0) - margin, bounds.max(axis=0) + margin
        ax.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), xticks=[], yticks=[],
               aspect=holistic_network.LOCAL_METRES[1] / holistic_network.LOCAL_METRES[0])
        for spine in ax.spines.values():
            spine.set_color("#d6cbb7")
    for ax, title in zip(axes, ("Previous inner ring", "Proposed central inner ring", "Reworked city network"), strict=True):
        ax.set_title(title, loc="left", pad=10, fontsize=13, color=ink, weight="bold")
    fig.text(.038, .941, "Baghdad | A ring for the centre", color=ink, fontsize=25, weight="bold")
    fig.text(.039, .886, "Central destinations, shared junctions and route overlap",
             color="#405761", fontsize=12)
    legend = [Line2D([], [], color=outer, lw=3, label="Outer ring"),
              Line2D([], [], color=inner, lw=3, label="Inner ring"),
              Line2D([], [], color=edit, lw=2, label="Changed route"),
              Line2D([], [], color="#29465b", marker="D", linestyle="None", label="Destination within 1.3 km"),
              Line2D([], [], color="#29465b", marker="D", markerfacecolor=paper, linestyle="None",
                     label="Destination beyond 1.3 km")]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(.5, .086),
               frameon=False, ncol=5, labelcolor=ink, fontsize=9.4)
    fig.text(.038, .042, "Central panels share a scale. Shading shows inner-ring walk coverage by sector. Basemap © OpenStreetMap contributors.",
             color="#405761", fontsize=9)
    output = BytesIO()
    fig.savefig(output, format="png", dpi=150, facecolor=paper)
    plt.close(fig)
    return output.getvalue()


def outputs(record, networks, context):
    code = record["display_trial"]
    geojson = holistic_network.geojson(networks[code])
    geojson.update(comparison_id=record["comparison_id"], trial=code,
                   central_area_wsen=record["central_area_wsen"], walking_threshold_m=study.WALK_NEW)
    access = record["coverage"]["worldpop-2026"][code]["destinations_on_foot_to_ring"]
    geojson["features"].extend({"type": "Feature", "geometry": {"type": "Point", "coordinates": row["coordinates"]},
                                "properties": {"kind": "central-destination", "destination_id": key,
                                               "name": row["name"], "walk_to_inner_ring_m": row["metres"],
                                               "within_1300_m": row["within_1300_m"]}}
                               for key, row in access.items())
    return {study.REPORT: report(record).encode(), study.RECORD: central_access.encode(record),
            study.FIGURE: draw(record, networks, context), study.GEOJSON: central_access.encode(geojson)}


def publish(record, networks, context, target, *, check=False):
    for path, content in outputs(record, networks, context).items():
        destination = target / path.relative_to(study.CITY)
        if check:
            actual = destination.read_bytes()
            equal = central_access.map_pixels_match(actual, content) if path == study.FIGURE else actual == content
            if not equal:
                raise SystemExit(f"Regenerate the central ring comparison. {path.name} differs.")
        else:
            write(destination, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--output", type=Path)
    parser.add_argument("--baseline", default=study.previous.wider.grid.BASELINE, type=Path)
    args = parser.parse_args()
    target = args.output or study.CITY
    with disk_reservation(central_access.ROOT, target, "Baghdad central ring and junctions", 128 << 20):
        record, networks, context = study.evaluate(args.baseline)
        publish(record, networks, context, target, check=args.check)
        print(record["comparison_id"])


if __name__ == "__main__":
    main()
