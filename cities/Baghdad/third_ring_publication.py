"""Publish Baghdad’s population-fitted rings and cross-city trunk comparison."""

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
NAMES = {"published": "Two-ring reference", "custom-layout": "Edited network",
         "retained-spaced": "Retained spaced core", "retained-named": "Retained trunks with named connections",
         "retained-named-gap": "Retained trunks with named connections and urban gap line"}


def name(code):
    if code in NAMES:
        return NAMES[code]
    if code.endswith("-gap"):
        return "Named suburbs and urban gap line"
    if code.endswith("-regional"):
        return "Three rings with regional connections"
    if code.endswith("-extended"):
        return "Three rings with suburban extensions"
    if code.startswith("coverage-"):
        middle, outer = code.removeprefix("coverage-").split("-")
        return f"Three-ring core · {middle.upper()} / {outer.upper()}"
    return code.replace("-", " ").capitalize()


def _pct(value):
    return f"{value:.2f}%" if value is not None else "—"


def _money(value):
    return f"{value / 1000:.2f}"


def report(record):
    reference = record["summary"]["published"]
    selected = record["selection"]["illustrated_trial"]
    eligible = record["selection"]["eligible_replacement"]
    chosen = record["summary"][selected] if selected else reference
    text = ["# Baghdad · Population-led rings and cross-city trunks", "",
            "The central ring encloses the mapped central districts on a convex alignment. The middle and outer "
            "rings are each fitted to residential population and the mapped walking network. Their separation varies "
            "around the city. The trunk search compares direct cross-city alignments from opposite sides of the outer "
            "ring. It checks tagged bridge approaches and possible new crossings against mapped river geometry.", ""]
    if eligible:
        text += [f"**{name(eligible)}** clears the digital replacement screen. Site and operating approval remain open.", ""]
    else:
        text += ["The two-ring reference still supplies the proposal’s budget. The three-ring comparison shows the "
                 "benefits of a simpler network and the districts where its access or journeys still fall short.", ""]
    text += ["![Two Baghdad networks with full-colour lines, shared stations and cross-Tigris trunks](maps/baghdad-three-ring-comparison.png)", "",
             "[Current proposal](PROPOSAL.md) · [Two-ring reference](STRAIGHT-THROUGH-NETWORK.md) · "
             "[Editable trial GIS](maps/baghdad-three-ring-trial.geojson) · [Machine results](three-ring-study.json.gz)", "",
             "## Network and access", "",
             "| Layout | Rings | Services | Short services | Cross-city trunks | Route-km | Station sites | Shared sites | Pairs of sites within 750 m | Parallel pair-km |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for code, row in record["summary"].items():
        station_screen = row["station_screen"]
        text.append(f"| {name(code)} | {len(row['rings'])} | {row['lines']} | {row['short_count']} | "
                    f"{row['through_count']} | {row['route_km']:.2f} | {row['stations']} | {row['transfer_stations']} | "
                    f"{station_screen.get('pairs_closer_than_750_m', '—')} | {row['parallel_pair_km']:.2f} |")
    housing = record["housing"]["variants"]["published"]["service"]
    text += ["", f"The passenger comparisons hold running supply at **{housing['running_train_km_day']:,.0f} train-km/day**. "
             "The housing test searches journeys with up to two changes. The wider metropolitan test assigns "
             "least-generalised-cost trips, then reports the share using up to two changes. "
             "Both population layers use the same retained street graph and a 1.3 km maximum walk.", "",
             "| Layout | WorldPop within 1.3 km | GHSL within 1.3 km | WorldPop reached only via middle-ring sites | Housing ≤2 changes | Wider journeys ≤2 changes | Headway |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for code, row in record["summary"].items():
        reach = record["coverage"]["worldpop-2026"][code]["1300"]
        text.append(f"| {name(code)} | {_pct(row['worldpop_1300_pct'])} | {_pct(row['ghsl_1300_pct'])} | "
                    f"{reach['middle_only_people']:,} | {_pct(row['housing_two_changes_pct'])} | "
                    f"{_pct(row['wide_two_changes_pct'])} | {row['headway_s']/60:.2f} min |")
    if record.get("destinations"):
        text += ["", "## Named suburban destinations", "",
                 "The table gives the shortest mapped street walk from each fixed anchor to a station. "
                 "Nahrawan and Tajiyat use station locations retained from the earlier network. "
                 "The Basmaya anchor is in the residential estate, east of the earlier M02 approach.",
                 "An em dash means the mapped walking graph did not establish a path within its search distance.", "",
                 "| Layout | Basmaya | Nahrawan | Tajiyat |",
                 "|---|---:|---:|---:|"]
        for code, row in record["summary"].items():
            walks = row["destination_walk_m"]
            text.append(f"| {name(code)} | " + " | ".join(
                f"{walks[site]:,.0f} m" if walks[site] is not None else "—"
                for site in record["destinations"]) + " |")
        text.append("")
    if "retained-spaced" in record["layouts"]:
        text += ["The comparison tests two ways to reach the named suburbs. One redraws through trunks around "
                 "the destinations. The other keeps the previous spaced trunks and adds screened connections. "
                 "Both test one additional line for urban coverage.", ""]
    if selected:
        regional = record["layout_trials"].get(selected, {}).get("regional_access", {})
        if regional.get("selected"):
            text += ["The named connections share exact outer-ring stations. The 5 km check uses the end of a short connector if it finishes before the dotted measurement contour.", "",
                     "| Destination | Service | Ring interchange | Added km | New station sites |",
                     "|---|---|---|---:|---:|"]
            for site, row in regional["selected"].items():
                text.append(f"| {site} | {row['route']} | {row['ring_station']} | {row['route_km']:.2f} | "
                            f"{row['new_station_sites']} |")
            text.append("")
        urban_gap = record["layout_trials"].get(selected, {}).get("urban_gap", {}).get("selected")
        if urban_gap:
            text += ["## One line through the largest urban gaps", "",
                     f"**{urban_gap['line_id']}** adds **{urban_gap['route_km']:.2f} route-km** inside the outer ring and "
                     f"{urban_gap['new_station_sites']} new station sites. It shares stations with "
                     f"{', '.join(urban_gap['connected_route_ids'])} and adds 1.3 km walking access for "
                     f"**{urban_gap['newly_reached_inside_outer_ring']['worldpop-2026']:,} WorldPop residents** and "
                     f"**{urban_gap['newly_reached_inside_outer_ring']['ghsl-2025']:,} GHSL residents** inside the outer ring. "
                     "The zero-additional-line case shows the effect of the change.", ""]
    extended = next((key for key, row in record["layout_trials"].items()
                     if key.endswith("-extended") and "core_layout" in row), None)
    if extended:
        extension = record["layout_trials"][extended]["suburban_extensions"]
        core = record["layout_trials"][extended]["core_layout"]
        trunk_search = record["layout_trials"][core]["trunk_search"]
        cap = trunk_search["screen"]["ordinary_terminal_reach_beyond_outer_ring_m"][1] / 1000
        spacing = record["summary"][extended]["suburban"]["minimum_departure_spacing_m"]
        reach = max(distance for row in trunk_search["trunks"] for stop, distance in
                    zip(row["terminal_ids"], row["terminal_distance_beyond_outer_ring_m"], strict=True)
                    if stop != "Airport-00") / 1000
        text += ["", "## Suburban extensions on the through services", "",
                 f"The core search chose new termini within a {cap:g} km band beyond the outer ring. It also "
                 "discounted the approach score as length increased. The illustrated core's ordinary ends "
                 f"finished within {reach:.2f} km of the ring, leaving much of the suburban catchment unserved.", "",
                 f"The continuation search tests up to **{extension['maximum_km_per_end']:g} km per trunk end**. "
                 "It keeps the original stations and through services, screens new alignments for heading, "
                 "water, station spacing and parallel duplication, and ranks the options by additional "
                 "residents within a 1.3 km street walk on both population grids.", "",
                 "The diamonds mark former termini, which remain intermediate stops. "
                 f"The suburban screen checks routes running alongside each other within "
                 f"{record['rings']['suburban_parallel_separation_m']/1000:g} km outside the outer ring "
                 f"for at least {record['rings']['minimum_suburban_parallel_run_m']/1000:g} continuous km. "
                 "It checks the original approaches and added extensions together. "
                 f"Each trunk also crosses a contour {record['rings']['suburban_gate_offset_m']/1000:g} km beyond the ring "
                 f"at sites at least {record['rings']['suburban_parallel_separation_m']/1000:g} km from those of every other trunk. "
                 "This separates routes that fan out too late. The dense-city spacing checks still apply inside the ring.", "",
                 (f"The closest pair of suburban contour crossings in the extended trial is **{spacing/1000:.2f} km apart**."
                  if spacing is not None else "The trial needs at least two trunks to compare suburban departure spacing."), "",
                 f"The resulting package extends **{len(extension['extensions'])} trunk ends** by "
                 f"**{extension['route_km_added']:.2f} route-km** and adds **{extension['new_station_sites']} station sites**. "
                 f"It reaches **{extension['newly_reached']['worldpop-2026']:,} more WorldPop residents** and "
                 f"**{extension['newly_reached']['ghsl-2025']:,} more GHSL residents** than the same core. "
                 "Passengers stay on the same service to cross the river and reach the rings.", "",
                 "The suburban shares below use the same territory outside the three-ring outer alignment for every case.", "",
                 "| Layout | WorldPop suburban walk reach | GHSL suburban walk reach |",
                 "|---|---:|---:|"]
        for key in ("published", core, extended):
            shares = [record["coverage"][grid][key]["1300"]["outside_trial_outer_ring"]["access_pct"]
                      for grid in ("worldpop-2026", "ghsl-2025")]
            text.append(f"| {name(key)} | {_pct(shares[0])} | {_pct(shares[1])} |")
        text += ["", "| Trunk | From former terminus | New terminus (nearby mapped place) | Added km | New sites | New WorldPop reach |",
                 "|---|---|---|---:|---:|---:|"]
        for tail in extension["extensions"]:
            place = f" ({tail['nearby_place']})" if tail["nearby_place"] else ""
            text.append(f"| {tail['route']} | {tail['former_terminal']} | {tail['new_terminal']}{place} | "
                        f"{tail['route_km']:.2f} | {tail['new_sites']} | {tail['additional_reach']['worldpop-2026']:,} |")
        text += ["", "Per-extension gains are counted in selection order. The reported residents are unique across the package.", ""]
    text += ["", "A resident is counted in the middle-ring-only column if they lose their 1.3 km access when "
             "stations exclusive to that ring are removed. Shared stations stay available in this test.", "",
             "### Neighbourhoods previously served only by short routes", "",
             "| Layout | Population grid | Former catchment | Still within 1.3 km | Of those, served only by middle-ring sites | Lost access |",
             "|---|---|---:|---:|---:|---:|"]
    for code in record["summary"]:
        for dataset in ("worldpop-2026", "ghsl-2025"):
            row = record["coverage"][dataset][code]["1300"]["short_route_catchments"]
            original, reached, middle = (row[field] for field in ("baseline_short_only_people",
                "retained_access_people", "served_by_middle_only_sites_people"))
            text.append(f"| {name(code)} | {dataset} | {original:,} | {reached:,} | {middle:,} | {original - reached:,} |")
    text += ["", "The map marks the largest areas where the trial loses existing walking access. The machine record also contains "
             "overall access gains and losses, named destinations and the 1.2 km walking sensitivity.", ""]
    if selected and "middle_outer_gap_km" in chosen["orbital_metrics"]:
        metrics = chosen["orbital_metrics"]
        text += ["## Geometry and station placement", "",
                 "| Distance from inner alignment to next ring | 10th percentile | Median | 90th percentile |",
                 "|---|---:|---:|---:|"]
        for label, key in (("Central to middle", "inner_middle_gap_km"),
                           ("Middle to outer", "middle_outer_gap_km")):
            gap = metrics[key]
            text.append(f"| {label} | {gap['p10']:.2f} km | {gap['median']:.2f} km | {gap['p90']:.2f} km |")
        text += ["", f"The inner ring has **{metrics['inner_foldback_km']:.2f} km** of close non-adjacent alignment, "
                 f"down from **{reference['orbital_metrics']['inner_foldback_km']:.2f} km**. The screen counts reaches "
                 "within 850 m of another point at least 1.5 km away along the ring.", ""]
        if metrics["inter_ring_contacts"]:
            names = [f"{row['bank']} ({row['station_id']})" for row in metrics["inter_ring_contacts"]]
            text += ["Direct ring contacts use shared sites at " + ", ".join(names) + ".", ""]
        else:
            text += ["Shared trunk stations provide the ring connections in the illustrated layout.", ""]
        details = record["layout_trials"][selected]
        if search := details.get("trunk_search"):
            text += [f"The deterministic search generated {len(record['rings']['generated_orbital_shapes'])} nested "
                     f"orbital combinations and built {len(record['rings']['examined_layouts'])} complete-layout trials. "
                     f"For the illustrated fit, {search['pool_candidates']} cross-city alignments passed the geometric "
                     "pool screens. The planner prioritised the Airport, then added coverage while checking station "
                     "separation and parallel running. The full layouts are ranked on 1.3 km walking reach across "
                     "both population grids.", ""]
        text += ["| Trunk | Route-km | Route ÷ chord | Shared stations on the three rings |",
                 "|---|---:|---:|---|"]
        for code, row in sorted(chosen["through_lines"].items()):
            sites = ", ".join(f"{ring} ({len(ids)})" for ring, ids in row["ring_crossing_stations"].items())
            text.append(f"| {code} | {row['route_km']:.2f} | {row['detour_ratio']:.3f} | {sites} |")
        text += ["", "Trunks serve both sides of the outer ring with one Tigris crossing each. Shared station "
                 "sites are retained before adding local stops. Dedicated railway bridges, grades, junctions, "
                 "accessible station entrances and operating headways require site and engineering work.", ""]
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
    text += ["", "## Reuse in larger cities", "",
             "The shared metropolitan comparison checks named destinations and walking coverage, then compares "
             "installed and whole-life cost under matched service and price assumptions. It keeps research leads "
             "visible while adoption depends on the same access and engineering requirements. A city needs its own "
             "walkable streets, population grids, destinations and crossing constraints to run this search.", "",
             "[Shared metropolitan method](../../docs/design-engine/current/METROPOLITAN-NETWORKS.md)", "",
             "Reproduce with `OPENBLAS_NUM_THREADS=1 ./osr design railway baghdad-three-rings --check`.", "",
             f"Publication `{record['publication_id']}`.", ""]
    return "\n".join(text)


CENTRAL_COLOR = "#a33e23"
MIDDLE_COLOR = "#087867"
OUTER_COLOR = "#553b96"
SHORT_COLOR = "#ab4900"
GAP_COLOR = "#a91a59"
TRUNK_COLORS = ("#1b4e99", "#8f2662", "#005e82", "#526a13", "#236449", "#6a2384", "#96305b",
                "#265975", "#74452b", "#006777", "#782440", "#485691", "#27683d", "#612664")


def route_colors(layout, short_routes):
    colors = {"M15": CENTRAL_COLOR, "M09": MIDDLE_COLOR if "M16" in layout["lines"] else OUTER_COLOR,
              "M16": OUTER_COLOR}
    for index, code in enumerate(sorted(layout["lines"].keys() - colors.keys())):
        colors[code] = SHORT_COLOR if code in short_routes else TRUNK_COLORS[index % len(TRUNK_COLORS)]
    colors.update({code: GAP_COLOR for code, line in layout["lines"].items() if line.get("service_role") == "urban-gap"})
    return colors


def draw(record, context):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon

    selected = record["selection"]["illustrated_trial"] or "published"
    details = record["layout_trials"].get(selected, {})
    core = details.get("core_layout")
    keys = (core or "published", selected) if selected != "published" else ("published",)
    water, rivers, roads = central_service_map.source_geometry(context)
    extent = np.concatenate([
        *(line["geometry"] for key in keys for line in record["layouts"][key]["lines"].values()),
        *([list(record.get("destinations", {}).values())] if record.get("destinations") else []),
    ])
    lower, upper = extent.min(axis=0) - .008, extent.max(axis=0) + .008
    paper, ink = "#faf7ef", "#193742"
    comparison = len(keys) > 1
    figure, axes = plt.subplots(1, len(keys), squeeze=False, figsize=(16, 8.4) if comparison else (10, 8.5),
                                gridspec_kw={"left": .04, "right": .975, "bottom": .17, "top": .84, "wspace": .08})
    figure.patch.set_facecolor(paper)
    figure.text(.047, .946, "Baghdad’s rings and cross-city routes", color=ink, fontsize=26, weight="bold")
    subtitle = ("Core and extended network · filled triangles are named places within a 1.3 km street walk" if core else
                "Published layout and coverage-led trial on the same scale" if comparison else
                "Passenger services and shared interchanges in the published layout")
    figure.text(.047, .899, subtitle, color="#465e68", fontsize=12)
    for axis, key in zip(axes[0], keys, strict=True):
        net, row = record["layouts"][key], record["summary"][key]
        axis.set_facecolor("#f0ece4")
        axis.add_collection(PatchCollection([Polygon(points, closed=True) for points in water], facecolor="#bed9df",
                                             edgecolor="none", zorder=1))
        axis.add_collection(LineCollection(rivers, colors="#80afbb", linewidths=1, zorder=1.2))
        axis.add_collection(LineCollection(roads, colors="#b2aa9a", linewidths=.30, alpha=.35, zorder=2))
        if departures := row.get("suburban", {}).get("departures"):
            from shapely import Polygon as RingPolygon
            outer = holistic_network.Track(net["lines"][study.RINGS[-1]]["geometry"])
            contour = RingPolygon(outer.points).buffer(study.coverage_trunks.SUBURBAN_GATE_OFFSET_M)
            axis.plot(*(np.asarray(contour.exterior.coords) / holistic_network.LOCAL_METRES).T,
                      color="#9b8265", lw=.8, linestyle="--", zorder=2.2)
            gates = np.concatenate(list(departures.values()))
            axis.scatter(*gates.T, marker="o", s=17, color="#bd651b", edgecolor=paper, linewidth=.6, zorder=6.3)
        through = set(row["through_lines"])
        cross_river = through | set(row.get("middle_ring_through_lines", {}))
        rings = set(study.RINGS)
        short_routes = set(row["short_lines"])
        colors = route_colors(net, short_routes)
        terminals = []
        for code, line in sorted(net["lines"].items()):
            if code in rings:
                width, layer = 2.5, 4.
            elif code in short_routes:
                width, layer = 1.4, 3.
            else:
                width, layer = (2.35, 4.6) if code in cross_river else (1.55, 3.4)
            shade = colors[code]
            if line.get("service_role") == "urban-gap":
                width, layer = 3.1, 5.1
            points = np.asarray(line["geometry"])
            axis.plot(*points.T, color=paper, linewidth=width + .8, zorder=layer)
            axis.plot(*points.T, color=shade, linewidth=width, zorder=layer + .1,
                      linestyle=(0, (4.5, 2.5)) if code in short_routes else "-")
            if code in through:
                axis.scatter(*points[[0, -1]].T, marker="s", facecolor=shade, edgecolor=paper,
                             s=22, linewidths=.8, zorder=5.4)
            if code in cross_river or (code not in rings and len(net["lines"]) <= 13):
                terminals.append((code, shade, points[[0, -1]]))
        if core and key == selected:
            tails = details.get("suburban_extensions", {}).get("extensions", [])
            if key.startswith("retained-"):
                tails = []
            for tail in tails:
                coords = np.asarray(tail["geometry"])
                axis.plot(*coords.T, color=paper, lw=4.6, zorder=4.85)
                axis.plot(*coords.T, color=colors[tail["route"]], lw=3.3, zorder=4.9)
                axis.scatter(*coords[0], marker="D", facecolor=paper, edgecolor=ink,
                             s=24, linewidths=.85, zorder=6.5)
        interchange = {site for site, station in net["stations"].items() if len(station["lines"]) > 1}
        if key != "published":
            local_sites = np.array([site["coordinates"] for stop, site in sorted(net["stations"].items())
                                    if stop not in interchange])
            if local_sites.size:
                axis.scatter(*local_sites.T, s=4, edgecolors="#635b5e", facecolors=paper, linewidths=.35, zorder=5.5)
        pts = np.array([net["stations"][site]["coordinates"] for site in sorted(interchange)])
        if pts.size:
            axis.scatter(*pts.T, s=13, edgecolors=ink, facecolors=paper, linewidths=.58, zorder=6)
        if "Airport-00" in net["stations"]:
            airport = net["stations"]["Airport-00"]["coordinates"]
            axis.scatter(*airport, s=46, marker="*", facecolors="#e0ad39", edgecolors=ink, linewidths=.6, zorder=7)
            axis.annotate("Airport", airport, xytext=(-7, -7), textcoords="offset points", ha="right",
                          color=ink, fontsize=8, bbox={"fc": paper, "ec": "none", "pad": .5}, zorder=8)
        for contact in row.get("orbital_metrics", {}).get("inter_ring_contacts", []):
            xy = net["stations"][contact["station_id"]]["coordinates"]
            axis.scatter(*xy, s=90, marker="D", facecolor="#fadc72", edgecolor=ink, linewidths=1.2, zorder=7)
            axis.annotate(contact["bank"], xy, xytext=(8, -10), textcoords="offset points", color=ink,
                          fontsize=9, bbox={"fc": paper, "ec": "none", "pad": .6}, zorder=8)
        for label, point in record.get("destinations", {}).items():
            walk = row["destination_walk_m"][label]
            filled = walk is not None and walk <= study.WALK_M
            axis.scatter(*point, s=32, marker="^", facecolor="#124143" if filled else paper,
                         edgecolor="#124143", linewidths=.8, zorder=7)
            axis.annotate(label, point, xytext=(-5, 7), textcoords="offset points", ha="right",
                          color=ink, fontsize=8, bbox={"fc": paper, "ec": "none", "pad": .5}, zorder=8)
        cells = record["coverage"]["worldpop-2026"][key]["1300"].get("largest_formerly_served_cells", [])
        if cells:
            axis.scatter(*np.array([site["coordinates"] for site in cells]).T, s=38, color="#a12642",
                         marker="x", linewidths=1.5, zorder=8)
        axis.set(xlim=(lower[0], upper[0]), ylim=(lower[1], upper[1]), xticks=[], yticks=[],
                 aspect=holistic_network.LOCAL_METRES[1] / holistic_network.LOCAL_METRES[0])
        axis.apply_aspect()
        axis.set_title(name(key), loc="left", fontsize=12, weight="bold", color=ink, pad=17)
        counts = f"{len(net['lines'])} services · {row['short_count']} short lines"
        if row.get("worldpop_1300_pct") is not None:
            counts += f" · {row['worldpop_1300_pct']:.1f}% within a 1.3 km walk"
        axis.text(0, 1.015, counts,
                  transform=axis.transAxes, color="#465e68", fontsize=9, va="bottom")
        _label_routes(axis, terminals, paper)
        for spine in axis.spines.values():
            spine.set_color("#c5beb0")
    ring_styles = [(CENTRAL_COLOR, "Inner ring"), (OUTER_COLOR, "Outer ring")]
    if any("M16" in record["layouts"][key]["lines"] for key in keys):
        ring_styles.insert(1, (MIDDLE_COLOR, "Middle ring"))
    legend = [Line2D([], [], color=shade, lw=2.5, label=label) for shade, label in ring_styles]
    legend.append(Line2D([], [], color=TRUNK_COLORS[0], lw=2.35, label="Cross-Tigris trunk"))
    if core and not selected.startswith("retained-"):
        legend.append(Line2D([], [], color=TRUNK_COLORS[1], lw=3.3, label="Suburban extension"))
        legend.append(Line2D([], [], color=ink, marker="D", markerfacecolor=paper,
                             linestyle="none", label="Former terminus"))
    else:
        legend.append(Line2D([], [], color=TRUNK_COLORS[1], lw=1.55, label="Other passenger service"))
    if any(record["summary"][key]["short_count"] for key in keys):
        legend.append(Line2D([], [], color=SHORT_COLOR, lw=1.4, linestyle="--", label=f"Short route ≤{study.SHORT_KM:g} km"))
    if any(line.get("service_role") == "urban-gap" for line in record["layouts"][selected]["lines"].values()):
        legend.append(Line2D([], [], color=GAP_COLOR, lw=3.1, label="Urban gap line"))
    if comparison:
        legend.append(Line2D([], [], color="#a12642", marker="x", linestyle="none", label="Largest gaps vs reference"))
    figure.legend(handles=legend, loc="lower center", bbox_to_anchor=(.5, .077), frameon=False,
                  ncol=7 if comparison else 4,
                  labelcolor=ink, fontsize=10)
    figure.text(.047, .042, ("Orange dots mark spacing points. The dotted contour is 2.5 km beyond the outer ring. The star marks the Airport."
                             if core else "Open circles mark shared stations, squares mark through-route terminals and the star marks the Airport."),
                color="#465e68", fontsize=8.5)
    figure.text(.047, .022, "Basemap © OpenStreetMap contributors.", color="#465e68", fontsize=8.5)
    buffer = BytesIO()
    figure.savefig(buffer, dpi=155, format="png", facecolor=paper)
    plt.close(figure)
    return buffer.getvalue()


def _label_routes(axis, routes, paper):
    """Place one visible line identifier near either terminus when there is room."""
    renderer = axis.figure.canvas.get_renderer()
    occupied = []
    for code, shade, ends in routes:
        for xy in sorted(ends, key=lambda point: (-point[1], point[0])):
            for dx, dy in ((7, 7), (-7, 7), (7, -7), (-7, -7)):
                label = axis.annotate(code, xy, xytext=(dx, dy), textcoords="offset points", color=shade,
                                      ha="left" if dx > 0 else "right", va="center", fontsize=8,
                                      weight="bold", bbox={"fc": paper, "ec": "none", "pad": .8}, zorder=9)
                bounds = label.get_window_extent(renderer).padded(2.5)
                if not all(axis.bbox.contains(*corner) for corner in bounds.get_points()) or any(
                        bounds.overlaps(previous) for previous in occupied):
                    label.remove()
                    continue
                occupied.append(bounds)
                break
            else:
                continue
            break


def outputs(record, context):
    selected = record["selection"]["illustrated_trial"] or "published"
    layout = record["layouts"][selected]
    short_routes = set(record["summary"][selected]["short_lines"])
    colors = route_colors(layout, short_routes)
    data = holistic_network.geojson(layout)
    extensions = record["layout_trials"].get(selected, {}).get("suburban_extensions", {}).get("extensions", [])
    by_route = {}
    for tail in extensions:
        by_route.setdefault(tail["route"], []).append(tail["former_terminal"])
    for feature in data["features"]:
        props = feature["properties"]
        if props["kind"] == "line":
            code = props["line_id"]
            props.update(stroke=colors[code], **{"stroke-opacity": 1, "stroke-width": 3})
            if code in by_route:
                props["former_suburban_terminals"] = by_route[code]
    data.update(publication_id=record["publication_id"], trial=selected, study_status=record["study_status"],
                named_destinations={name: {"coordinates": position,
                    "walk_m": record["summary"][selected]["destination_walk_m"][name]}
                    for name, position in record.get("destinations", {}).items()})
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
