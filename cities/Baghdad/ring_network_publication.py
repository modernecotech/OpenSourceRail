"""Publish the reworked Baghdad ring-and-through-line comparison."""

import argparse
from pathlib import Path

import numpy as np

from engineering.performance import disk_reservation
from engineering.station_rail.publication import write

from . import central_access, central_service_map, holistic_network, ring_network_study as study


def _name(record, code):
    return study.BASE_NAMES.get(code) or record["proposals"][code]["name"]


def _action_text(action):
    code = action["line_id"]
    kind = action["action"]
    if kind == "ring_turnback":
        return (f"**{code} terminates at M15.** The retained service still calls at M09. "
                f"The new common station closes {len(action['closed_stations'])} former sites and removes "
                f"{action['removed_route_km']:.2f} route-km. C1 remains on the eastern approach.")
    if kind == "walk_interchange":
        walk = action["walking_link"]
        return (f"**{action['connecting_line_id']} links to M15 by a street walk.** The new M15 platform connects "
                f"to the C1–M02 station. The longer direction of the mapped walk is {max(walk['walks_m']):.0f} m.")
    if kind == "through_pairing":
        return (f"**{code} becomes a west–southeast through service.** It takes over part of T19 at the mapped "
                "junction. The eastern branch keeps its calls and the two services account for the same track length.")
    if kind == "add_diameter":
        return f"**{code} is a {action['route_km']:.2f} km cross-city diameter.** It has a shared station on each of the two rings."
    if kind == "withdraw_line":
        return (f"**{code} is replaced in this trial.** The estimate removes {action['removed_route_km']:.2f} route-km "
                f"and closes {len(action['closed_stations'])} sites served only by this line.")
    raise ValueError(f"Describe unrecognized route action {kind}")


def report(record):
    rows = record["summary"]
    key = record["display_trial"]
    case, prior = rows[key], rows["wider"]
    service = record["ring_service"]
    train_km = service["variants"]["current"]["service"]["running_train_km_day"]
    priority = service["ring_priority_variants"]
    gap = record["ring_geometry"]["minimum_ring_separation_m"] / 1000
    lines = [
        "# Baghdad railway routes that serve both rings", "",
        f"**{_name(record, key)}** is the displayed redesign. It keeps the **22.36 km** inner ring and the same "
        f"outer ring, with **{gap:.2f} km** minimum mapped clearance. Routes "
        f"**{', '.join(case['direct_routes'])}** now call at both rings, compared with "
        f"**{', '.join(prior['direct_routes'])}** in the previous wider-ring layout.", "",
        "![Previous wider network, reworked routes and central detail](maps/baghdad-ring-network.png)", "",
        "[Network and interchange GIS](maps/baghdad-ring-network.geojson) · [Machine results](ring-network.json) · "
        "[Wider-ring comparison](WIDER-RING.md) · [Published city network](NETWORK.md)", "",
        "## Route changes", "",
    ]
    lines.extend(f"- {_action_text(action)}" for action in record["proposals"][key]["actions"])
    lines.extend(["", "The comparison also tests the M02 pedestrian connection alone, the M04–T19 through working, "
        "and combinations of those changes. New platforms follow the affected track alignments. Walking "
                  "links use the retained street network in both directions.", ""])
    if record["proposals"]["diameters"].get("pair_hold"):
        lines.extend(["Two axes passed individual screening. Their combined length and shallow intersection angle "
                      "held the two-line option before the shared-station check. The single east–west diameter "
                      "was tested separately at the earlier guideway budget.", ""])
    for code, reason in sorted(record["held_trials"].items()):
        lines.append(f"- {_name(record, code) if record['proposals'][code].get('name') else 'Direct cross-city trial'} was held. {reason}.")
    lines.extend([
        "## Network and journey comparison", "",
        f"All layouts share **{train_km:,.0f} daily running train-km** and the same population-based trip sample. "
        "The six-centre housing measure permits up to two changes. The wider inter-district sample groups trips "
        "between different sides of central Baghdad. Route overlap counts each pair of lines at close parallel "
        "separation. The 1.2 km access measure uses the street network.", "",
        "| Layout | Lines | Route km | Direct routes between rings | Close parallel pair-km | Station pairs within 280 m | Walk ≤1.2 km | Outer trips served | Housing to centre ≤2 changes |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for code, row in rows.items():
        lines.append(f"| {_name(record, code)} | {row['lines']} | {row['route_km']:.2f} | {len(row['direct_routes'])} | "
                     f"{row['parallel_pair_km']:.2f} | {row['close_site_pairs']} | {row['walk_1200_pct']:.2f}% | "
                     f"{row['wide_trips_pct']:.2f}% | {row['households_two_changes_pct']:.2f}% |")
    lines.extend(["", f"Displayed selection passed the **{record['selection']['basis']}** comparison tier. "
                  "The matched tier allows up to 2% more route-km, the same or fewer lines, and a drop of at most "
                  "0.5 percentage points in each reach measure before ranking by housing-to-centre reach, "
                  "outer-district reach, less parallel running, direct connections between the rings and transfers.", "",
                  "## How passengers use the rings", "",
                  "A journey counts toward a ring only when its assigned path rides a segment of that ring. "
                  "The two-ring column counts journeys riding both. The published city control has an open M09 service. "
                  "Only journeys served by both layouts enter the paired elapsed-time comparison.", "",
                  "| Layout | Served trips riding M09 | Served trips riding M15 | Served trips riding both | All modelled trips riding either | Outer trips assigned ≤2 changes | Paired outer P90, previous → trial |",
                  "|---|---:|---:|---:|---:|---:|---:|"])
    for code, row in rows.items():
        lines.append(f"| {_name(record, code)} | {row['outer_used_pct']:.2f}% | {row['inner_used_pct']:.2f}% | "
                     f"{row['both_used_pct']:.3f}% | {row['using_ring_pct']:.2f}% | {row['wide_two_changes_pct']:.2f}% | "
                     f"{row['wider_same_trip_p90_min']:.2f} → {row['wide_same_trip_p90_min']:.2f} min |")
    lines.extend(["", "The operating sensitivity increases frequency by 25% on M09 and M15 and reallocates those "
                  "train-kilometres from the other routes. The timetable and train capacity require further work.", "",
                  "| Layout with more frequent rings | Ring headway | All modelled trips riding either, uniform → priority | Outer trips assigned ≤2 changes, uniform → priority |",
                  "|---|---:|---:|---:|"])
    for code in ("wider", key):
        row = priority[code]
        headway = row["service"]["line_headways_s"]["M15"] / 60
        either = row["ring_use"]["either"]["share_of_all_pct"]
        wide = row["cohorts"][study.WIDE_COHORT]["journeys"]["at_most_two_transfers_share_of_all_pct"]
        lines.append(f"| {_name(record, code)} | {headway:.2f} min | {rows[code]['using_ring_pct']:.2f}% → "
                     f"{either:.2f}% | {rows[code]['wide_two_changes_pct']:.2f}% → {wide:.2f}% |")
    lines.extend(["", "## Construction and cost", "",
                  "The planning estimate prices the displayed layout and the tested physical alternative with the "
                  "least parallel overlap. It uses the six-minute costing basis and 2026 rates. The programme day "
                  "shows standard-deck handover from mobilisation.", "",
                  "| Layout | Track-km | Paid casting, haul and erection hours | Handover day | Installed US$bn | 30-year present US$bn |",
                  "|---|---:|---:|---:|---:|---:|"])
    for code, row in record["six_minute_delivery_and_cost"].items():
        base = row["cases"]["base"]
        lines.append(f"| {_name(record, code)} | {row['track_km']:,.2f} | {row['paid_casting_haul_and_erection_hours']:,.0f} | "
                     f"{row['standard_deck_handover_day']:,.0f} | {base['installed_planning_usd_m']/1000:.2f} | "
                     f"{base['whole_life_present_usd_m']/1000:.2f} |")
    lines.extend(["", "Rail curves, accessible interchange layouts, physical turnbacks, junction capacity, "
                  "and dedicated river crossing structures remain open. The estimates exclude special crossing premiums.", "",
                  "Reproduce with `tools/automation/osr-python -m cities.Baghdad.ring_network_publication --check`.", "",
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

    code = record["display_trial"]
    base, proposed = networks["wider"], networks[code]
    changes = record["route_revisions"][code]
    actions = record["proposals"][code]["actions"]
    changed = (set(changes["added_routes"]) | set(changes["realigned_routes"])
               | set(changes["withdrawn_routes"]))
    paper, ink, outer, inner, edit = "#f8f5ee", "#193742", "#087d77", "#b64b1e", "#5a469f"
    fig, axes = plt.subplots(1, 3, figsize=(16, 7.9),
                             gridspec_kw={"left": .038, "right": .979, "wspace": .085, "top": .825, "bottom": .16})
    fig.patch.set_facecolor(paper)
    water, rivers, roads = central_service_map.source_geometry(context)
    overview = np.concatenate([line["geometry"] for layout in (base, proposed) for line in layout["lines"].values()])
    centre = np.asarray(proposed["lines"]["M15"]["geometry"])
    colors = {"M09": outer, "M15": inner}
    for index, (ax, layout) in enumerate(zip(axes, (base, proposed, proposed), strict=True)):
        ax.set_facecolor("#f2ede2")
        ax.add_collection(PatchCollection([Polygon(points, closed=True) for points in water],
                                           facecolor="#bedbe1", edgecolor="none", zorder=1))
        ax.add_collection(LineCollection(rivers, colors="#81b3bc", linewidths=.94, zorder=1.1))
        ax.add_collection(LineCollection(roads, colors="#aea490", linewidths=.28, alpha=.4, zorder=2))
        for route, line in layout["lines"].items():
            xy = np.asarray(line["geometry"]).T
            color = colors.get(route, edit if route in changed else "#74868a")
            emphasis = route in (changed | set(colors))
            if emphasis:
                ax.plot(*xy, color=paper, linewidth=4.3, zorder=3.8)
            ax.plot(*xy, color=color, lw=2.45 if emphasis else .85,
                    linestyle="--" if route in changes["withdrawn_routes"] else "-",
                    alpha=1 if emphasis else .75, zorder=4.1 if emphasis else 3)
        if index == 2:
            for site in layout["lines"]["M15"]["station_ids"]:
                row = layout["stations"][site]
                ax.scatter(*row["coordinates"], s=20 if len(row["lines"]) > 1 else 8, facecolors=paper,
                           edgecolors=inner, linewidths=.88, zorder=5)
            for i, action in enumerate(actions):
                site = action.get("station_id")
                if action["action"] == "add_diameter":
                    spoke = layout["lines"][action["line_id"]]
                    common = sorted(set(spoke["station_ids"]) & set(layout["lines"]["M15"]["station_ids"]))
                    site = common[0]
                if site is None:
                    continue
                p = layout["stations"][site]["coordinates"]
                ax.scatter(*p, s=38, facecolors=paper, edgecolors=edit, linewidths=1.4, zorder=6)
                if action["action"] == "walk_interchange":
                    trace = np.asarray(action["walking_link"]["geometry"][0])
                    ax.plot(*trace.T, color=edit, linestyle=":", linewidth=1.7, zorder=5.9)
                    label = f"{action['connecting_line_id']} walking link"
                elif action["action"] == "add_diameter":
                    label = f"{action['line_id']} ↔ inner ring"
                else:
                    label = f"{action['line_id']} inner-ring terminus"
                left = p[0] > centre[:, 0].mean()
                ax.annotate(label, p, xytext=(-6 if left else 6, 9 + 9 * (i % 2)), textcoords="offset points",
                            ha="right" if left else "left",
                            fontsize=8, color=ink, weight="bold", zorder=7,
                            bbox={"boxstyle": "round,pad=.2", "fc": paper, "ec": "none"})
        coords, margin = (centre, .016) if index == 2 else (overview, .009)
        lo, hi = coords.min(axis=0) - margin, coords.max(axis=0) + margin
        ax.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), xticks=[], yticks=[],
               aspect=holistic_network.LOCAL_METRES[1] / holistic_network.LOCAL_METRES[0])
        for spine in ax.spines.values():
            spine.set_color("#d5cbb6")
    for ax, title in zip(axes, ("Previous wider network", "Reworked lines", "Inner-ring detail"), strict=True):
        ax.set_title(title, loc="left", fontsize=13, color=ink, weight="bold", pad=10)
    fig.text(.038, .94, "Baghdad | Routes serving both rings", fontsize=25, weight="bold", color=ink)
    fig.text(.039, .888, "Same ring alignments, new cross-city service pattern", fontsize=12, color="#405761")
    markers = [Line2D([], [], color=c, lw=w, label=label) for c, w, label in
               ((outer, 3, "Outer ring"), (inner, 3, "Inner ring"), (edit, 2.5, "Changed route"), ("#74868a", 1, "Other services"))]
    markers.append(Line2D([], [], color=edit, linestyle="--", label="Withdrawn route"))
    fig.legend(handles=markers, loc="lower center", bbox_to_anchor=(.5, .081), ncol=5,
               frameon=False, fontsize=10, labelcolor=ink)
    fig.text(.038, .04, "First two panels share a scale. Planning alignments and basemap © OpenStreetMap contributors.",
             fontsize=9, color="#405761")
    output = BytesIO()
    fig.savefig(output, format="png", dpi=150, facecolor=paper)
    plt.close(fig)
    return output.getvalue()


def outputs(record, networks, context):
    selected = record["display_trial"]
    geojson = holistic_network.geojson(networks[selected])
    geojson.update(comparison_id=record["comparison_id"], trial=selected)
    return {study.REPORT: report(record).encode(), study.RECORD: central_access.encode(record),
            study.FIGURE: draw(record, networks, context), study.GEOJSON: central_access.encode(geojson)}


def publish(record, networks, context, target, *, check=False):
    for path, content in outputs(record, networks, context).items():
        destination = target / path.relative_to(study.CITY)
        if check:
            actual = destination.read_bytes()
            equal = central_access.map_pixels_match(actual, content) if path == study.FIGURE else actual == content
            if not equal:
                raise SystemExit(f"Regenerate the ring network comparison. {path.name} differs.")
        else:
            write(destination, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--publish", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--output", type=Path)
    parser.add_argument("--baseline", default=study.wider.grid.BASELINE, type=Path)
    args = parser.parse_args()
    target = args.output or study.CITY
    with disk_reservation(central_access.ROOT, target, "Baghdad ring network and through lines", 96 << 20):
        record, networks, context = study.evaluate(args.baseline)
        publish(record, networks, context, target, check=args.check)
        print(record["comparison_id"])


if __name__ == "__main__":
    main()
