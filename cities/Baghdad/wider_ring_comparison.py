"""Compare a wider inner ring with the published compact Baghdad ring."""

import argparse
from hashlib import sha256
from pathlib import Path
import tomllib

import numpy as np
from shapely.geometry import Polygon

from engineering.performance import disk_reservation
from engineering.station_rail.publication import write

from . import (
    central_access, holistic_network, network_station_sites, residential_planning,
    ring_corridors, ring_grid_comparison as grid, spaced_ring_comparison as compact,
    spaced_ring_geometry, spaced_ring_layouts as layouts, wider_ring_geometry,
)


REPORT = grid.CITY / "WIDER-RING.md"
RECORD = grid.CITY / "wider-ring.json"
FIGURE = grid.CITY / "maps/baghdad-wider-ring.png"
GEOJSON = grid.CITY / "maps/baghdad-wider-ring.geojson"
TRIALS = {"footprint": ("east-south-trunks", "outer-east-transfer", "fewer-radials"),
          "spokes": ("east-south-trunks", "outer-east-transfer")}
NAMES = {"current": "Published city network", "compact": "Previous compact dual ring",
         "east-south-trunks": "Wider ring with the same east–south trunk pattern",
         "outer-east-transfer": "Wider ring with an eastern transfer terminus",
         "fewer-radials": "Wider ring with fewer radial services"}


def _lines_from_map(path):
    return {entry["properties"]["line_id"]: entry["geometry"]["coordinates"]
            for entry in central_access.read(path)["features"] if entry["properties"]["kind"] == "line"}


def _footprint(coordinates):
    polygon = Polygon(np.asarray(coordinates) * holistic_network.LOCAL_METRES)
    west, south, east, north = polygon.bounds
    return {"area_km2": polygon.area / 1e6,
            "width_east_west_km": (east - west) / 1000, "width_north_south_km": (north - south) / 1000}


def _name(code):
    shape, _, layout = code.partition("/")
    return f"{NAMES[layout]} · {shape} route" if layout else NAMES[code]


def _pick(summary, preferred):
    best = summary["current"]
    candidates = [code for code in summary if "/" in code]
    simplified = [code for code in candidates if summary[code]["lines"] < best["lines"]
                  and summary[code]["parallel_pair_km"] < best["parallel_pair_km"]
                  and summary[code]["close_site_pairs"] < best["close_site_pairs"]]
    comparable = [code for code in simplified if summary[code]["route_km"] <= best["route_km"] * 1.01]
    choices = comparable or simplified or candidates
    matched = [code for code in choices if code.endswith(f"/{preferred}")]
    return max(matched or choices, key=lambda code: (summary[code]["housing_two_changes_pct"],
                                                     summary[code]["wide_angle_served_pct"],
                                                     summary[code]["walk_worldpop_pct"],
                                                     -summary[code]["parallel_pair_km"]))


def _trials(outer, graph, context, search, screen):
    networks, evidence, rejections = {}, {}, {}
    for shape, option in (("footprint", search["selected"]), ("spokes", search["connectivity_alternative"])):
        if option is None:
            continue
        overlay, inner = spaced_ring_geometry.insert(outer, option, graph, context)
        overlay["lines"]["M15"]["name"] = "Baghdad wider inner orbital"
        inner["status"] = "Wider GIS corridor and access screen passed"
        source = Path(wider_ring_geometry.__file__)
        overlay["source_sha256"][compact._file_id(source)] = central_access.digest(source)
        overlay["wider_inner_ring"] = {"enclosed_area_km2": option["enclosed_area_km2"],
                                        "bridge_ways": option["bridge_ways"]}
        overlay = holistic_network._identity(overlay)
        alternatives = layouts.alternatives(overlay, graph=graph, context=context,
                                            protected_stations=grid.PROTECTED, screen=screen)
        footprint = _footprint(option["geometry"])
        for code in TRIALS[shape]:
            trial = alternatives[code]
            key = f"{shape}/{code}"
            net = trial.get("network")
            if net is None:
                rejections[key] = trial["rejection_reason"]
                continue
            if any(net["lines"][ring]["geometry"] != overlay["lines"][ring]["geometry"]
                   for ring in ("M09", "M15")):
                raise ValueError("Service simplification changed a screened ring geometry")
            gap = compact._screen_rings(net)
            if len(gap["direct_spokes"]) < spaced_ring_geometry.MIN_DIRECT_SPOKES:
                rejections[key] = "Too few passenger services joining both rings following route simplification"
                continue
            networks[key] = net
            evidence[key] = gap | footprint | {"close_site_pairs": trial["metrics"]["close_site_pairs"],
                                                "bridges": option["bridges"], "inner": inner,
                                                "changes": trial["actions"], "station_audit": trial["station_audit"]}
    return networks, evidence, rejections


def evaluate(baseline_path):
    baseline = central_access.read(baseline_path)
    current = baseline["network"]
    previous = central_access.read(compact.RECORD)
    if (current["candidate_id"] != grid.REFERENCE_ID
            or previous["reference_packet_sha256"] != central_access.digest(baseline_path)):
        raise ValueError("Wider and compact rings must use the same published city network")
    graph = central_access.walking_graph()
    context = central_access.original_cases()[3]
    outer, outer_evidence = ring_corridors.evaluate_rings(current, graph, context, include_inner=False)
    search = wider_ring_geometry.evaluate(outer, graph, context)
    if search["selected"] is None:
        raise ValueError("Wider inner ring search exhausted its mapped corridor candidates")
    screen = tomllib.loads(residential_planning.POLICY.read_text())["corridor_screen"]
    trials, network_evidence, rejections = _trials(outer, graph, context, search, screen)
    networks = {"current": current} | trials
    old_routes = _lines_from_map(compact.GEOJSON)
    if old_routes["M09"] != outer["lines"]["M09"]["geometry"]:
        raise ValueError("The widened comparison changes the previous outer ring")
    old_footprint = _footprint(old_routes["M15"])
    if len(networks) < 2:
        raise ValueError(f"No simplified wider network passed direct transfer screening. {rejections}")

    actual = grid.assess(networks, graph, baseline_record=baseline, trials={}, ring_evidence={})
    for metric in ("same_train_km_housing", "same_train_km_metropolitan"):
        section = actual[metric]
        prior = previous[metric]
        if (section["demand_sample"]["sample_id"] != prior["demand_sample"]["sample_id"]
                or section["variants"]["current"]["service"]["running_train_km_day"]
                != prior["variants"]["current"]["service"]["running_train_km_day"]):
            raise ValueError(f"Compact and wider rings differ in {metric} demand or running train-km")
    previous_key = previous["display_trial"]
    summary = {"current": compact._summary(actual, "current") | {
        "close_site_pairs": len(network_station_sites._nearby(current["stations"], layouts.CLOSE_SITE_M))},
        "compact": previous["summary"][previous_key] | old_footprint}
    for code, evidence in network_evidence.items():
        if evidence["area_km2"] <= old_footprint["area_km2"]:
            raise ValueError("Widened ring must occupy a larger footprint than the compact ring")
        summary[code] = compact._summary(actual, code) | {
            key: evidence[key] for key in ("minimum_ring_separation_m", "direct_spokes", "close_site_pairs",
                                           "area_km2", "width_east_west_km", "width_north_south_km",
                                           "nearest_inner_coordinates", "nearest_outer_coordinates")}
    picked = _pick(summary, previous_key)
    inputs = (Path(__file__), Path(wider_ring_geometry.__file__), Path(grid.__file__),
              Path(compact.__file__), compact.RECORD, compact.GEOJSON, residential_planning.POLICY)
    sources = baseline["sources"] | networks[picked]["source_sha256"]
    sources.update({compact._file_id(path): central_access.digest(path) for path in inputs})
    record = actual | {"schema": "osr-baghdad-wider-ring/1", "sources": sources,
                       "reference_packet_sha256": central_access.digest(baseline_path),
                       "compact_comparison_id": previous["comparison_id"], "compact_trial": previous_key,
                       "display_trial": picked, "summary": summary, "search": search,
                       "ring_evidence": {"outer": outer_evidence,
                                         "networks": network_evidence, "rejected_networks": rejections}}
    record["comparison_id"] = sha256(central_access.encode(record)).hexdigest()
    return record, networks[picked], context


def report(record):
    rows = record["summary"]
    key = record["display_trial"]
    wider, previous = rows[key], rows["compact"]
    loop, old_loop = (row["rings"]["M15"] for row in (wider, previous))
    bridges = " and ".join(record["ring_evidence"]["networks"][key]["bridges"])
    service = record["same_train_km_metropolitan"]["variants"]["current"]["service"]["running_train_km_day"]
    minimum = wider["minimum_ring_separation_m"] / 1000
    text = [
        "# Baghdad wider inner ring", "",
        f"The inner ring runs **{loop['route_km']:.2f} km**, compared with **{old_loop['route_km']:.2f} km** "
        f"in the compact trial. It spans **{wider['width_east_west_km']:.1f} km east–west × "
        f"{wider['width_north_south_km']:.1f} km north–south**, and encloses **{wider['area_km2']:.1f} km²**, "
        f"up from **{previous['area_km2']:.1f} km²**. The minimum distance to the same outer ring is **{minimum:.2f} km**, "
        "measured between the complete alignments.", "",
        f"The widened loop crosses the Tigris at the mapped {bridges} road corridors. It has {loop['stations']} "
        f"station sites and {loop['interchanges']} shared interchanges. Direct routes between the rings are "
        f"{', '.join(wider['direct_spokes'])}.", "",
        "![Compact and wider Baghdad inner rings at the same map scales](maps/baghdad-wider-ring.png)", "",
        "[Wider ring GIS and network](maps/baghdad-wider-ring.geojson) · [Compact ring study](SPACED-RINGS.md) · "
        "[Published city network](NETWORK.md) · [Full model results](wider-ring.json)", "",
        "## Coverage and journeys", "",
        f"All journey cases use **{service:,.0f} daily running train-km** and the same synthetic demand. "
        "Access is a street walk of up to 1.2 km. The housing sample measures journeys to six central destinations "
        "with a maximum of two changes. The outer-district sample counts journeys between different sides of the city.", "",
        "| Layout | Lines | Route km | Sites within 280 m, pairs | Close parallel pair-km | Walk ≤1.2 km | Outer trips served | Housing to centre ≤2 changes |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in rows.items():
        text.append(f"| {_name(name)} | {row['lines']} | {row['route_km']:.2f} | {row['close_site_pairs']} | "
                    f"{row['parallel_pair_km']:.2f} | {row['walk_worldpop_pct']:.2f}% | "
                    f"{row['wide_angle_served_pct']:.2f}% | {row['housing_two_changes_pct']:.2f}% |")
    text.extend(["", f"Relative to the compact ring, the displayed wider layout changes 1.2 km walk coverage by "
                 f"{wider['walk_worldpop_pct'] - previous['walk_worldpop_pct']:+.2f} percentage points and "
                 f"housing-to-centre reach by {wider['housing_two_changes_pct'] - previous['housing_two_changes_pct']:+.2f} points. "
                 "The through-route trials reuse the compact study's line plans and screen station sites on the new alignment.", "",
                 "The footprint route favours a broad area with fewer sharp turns. The spokes route connects to more existing lines "
                 "in its initial interchange screen. The displayed layout favours fewer lines, less parallel running and fewer "
                 "close station pairs within 1% of the published route length where possible. Within that group the comparison "
                 "favours retaining the east–south trunk pattern and reaching more central destinations.", "",
                 "## Delivery and planning cost", "",
                 "Delivery uses common 2026 unit rates and a six-minute directional service. The model schedules standard-deck "
                 "handover from mobilisation. Opening also depends on stations, equipment, commissioning and special works.", "",
                 "| Layout | Track-km | Paid casting, haul and erection hours | Deck handover day | Trainsets with spares | Installed US$bn | 30-year present US$bn |",
                 "|---|---:|---:|---:|---:|---:|---:|"])
    for name, row in rows.items():
        text.append(f"| {_name(name)} | {row['track_km']:,.2f} | {row['paid_crew_hours']:,.0f} | "
                    f"{row['standard_deck_handover_day']:,.0f} | {row['fleet_trainsets']} | "
                    f"{row['installed_usd_bn']:.2f} | {row['whole_life_usd_bn']:.2f} |")
    text.extend(["", "The 5 km clearance is a horizontal GIS screen. Rail curves, grades, interchange layouts and dedicated "
                 "river crossings require design. Outer-ring restoration still has two mapped wet reaches beyond the "
                 "550 m screen. The estimate excludes special crossing premiums.", "",
                 "Verify with `tools/automation/osr-python -m cities.Baghdad.wider_ring_comparison --check`.", "",
                 f"Comparison `{record['comparison_id']}`.", ""])
    return "\n".join(text)


def draw(record, network, context):
    from io import BytesIO

    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon as PlotPolygon

    from . import central_service_map

    previous = _lines_from_map(compact.GEOJSON)
    wider = {code: line["geometry"] for code, line in network["lines"].items()}
    selection = record["summary"][record["display_trial"]]
    paper, ink, outer, inner = "#f8f5ee", "#193741", "#087d77", "#af4820"
    fig, axes = plt.subplots(1, 3, figsize=(16, 7.5),
                             gridspec_kw={"left": .04, "right": .975, "top": .82, "bottom": .158, "wspace": .08})
    fig.patch.set_facecolor(paper)
    water, rivers, roads = central_service_map.source_geometry(context)
    central = np.concatenate([previous["M15"], wider["M15"]])
    overview = np.asarray(wider["M09"])
    for index, (ax, routes) in enumerate(zip(axes, (previous, wider, wider), strict=True)):
        ax.set_facecolor("#f3eee3")
        ax.add_collection(PatchCollection([PlotPolygon(points, closed=True) for points in water],
                                           facecolor="#bbdce4", edgecolor="none", zorder=1))
        ax.add_collection(LineCollection(rivers, colors="#83b3be", linewidths=1, zorder=1.1))
        ax.add_collection(LineCollection(roads, colors="#aca497", linewidths=.38, alpha=.42, zorder=2))
        ax.add_collection(LineCollection([points for code, points in routes.items() if code not in {"M09", "M15"}],
                                         colors="#627b86", linewidths=.88, alpha=.72, zorder=3))
        for code, color in (("M09", outer), ("M15", inner)):
            coords = np.asarray(routes[code]).T
            ax.plot(*coords, color=paper, linewidth=5.1, zorder=4)
            ax.plot(*coords, color=color, linewidth=2.8, zorder=5)
        if index > 0:
            for stop in network["lines"]["M15"]["station_ids"]:
                site = network["stations"][stop]
                interchange = len(site["lines"]) > 1
                ax.scatter(*site["coordinates"], s=26 if interchange else 12, facecolors=paper,
                           edgecolors=inner, linewidths=1., zorder=6)
        if index == 2:
            a, b = np.asarray([selection["nearest_inner_coordinates"], selection["nearest_outer_coordinates"]])
            ax.plot(*np.stack([a, b]).T, color=ink, linestyle=(0, (3, 2)), linewidth=1.45, zorder=7)
            ax.annotate(f"{selection['minimum_ring_separation_m']/1000:.2f} km", (a + b) / 2,
                        xytext=(5, 6), textcoords="offset points", fontsize=9, weight="bold", color=ink, zorder=8,
                        bbox={"boxstyle": "round,pad=.23", "fc": paper, "ec": "none"})
        bounds, margin = (overview, .007) if index == 2 else (central, .008)
        lo, hi = bounds.min(axis=0) - margin, bounds.max(axis=0) + margin
        ax.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), xticks=[], yticks=[],
               aspect=holistic_network.LOCAL_METRES[1] / holistic_network.LOCAL_METRES[0])
        for spine in ax.spines.values():
            spine.set_color("#d3c8b4")
    compact_km = record["summary"]["compact"]["rings"]["M15"]["route_km"]
    wider_km = selection["rings"]["M15"]["route_km"]
    titles = (f"Compact inner ring · {compact_km:.2f} km", f"Wider inner ring · {wider_km:.2f} km",
              "Clearance to outer ring")
    for ax, title in zip(axes, titles, strict=True):
        ax.set_title(title, fontsize=13, weight="bold", color=ink, loc="left", pad=10)
    fig.text(.04, .941, "Baghdad | A wider inner ring", color=ink, size=25, weight="bold")
    fig.text(.041, .889, "Same outer ring, larger central footprint", color="#405761", size=12)
    handles = [Line2D([], [], color=color, lw=width, label=label) for color, width, label in
               ((outer, 3, "Outer ring"), (inner, 3, "Inner ring"), ("#627b86", 1.5, "Other services"))]
    handles.append(Line2D([], [], color=ink, linestyle="--", label="Closest approach"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .09), ncol=4, frameon=False,
               fontsize=10, labelcolor=ink)
    fig.text(.04, .048, "Central panels share a scale. Planning corridors and basemap © OpenStreetMap contributors.",
             color="#405761", size=9)
    output = BytesIO()
    fig.savefig(output, format="png", dpi=150, facecolor=paper)
    plt.close(fig)
    return output.getvalue()


def outputs(record, network, context):
    key = record["display_trial"]
    gap = record["summary"][key]
    gis = holistic_network.geojson(network)
    gis.update(comparison_id=record["comparison_id"], trial=key)
    gis["features"].append({
        "type": "Feature",
        "geometry": {"type": "LineString",
                     "coordinates": [gap["nearest_inner_coordinates"], gap["nearest_outer_coordinates"]]},
        "properties": {"kind": "minimum-ring-clearance", "minimum_separation_m": gap["minimum_ring_separation_m"]},
    })
    return {REPORT: report(record).encode(), RECORD: central_access.encode(record),
            FIGURE: draw(record, network, context), GEOJSON: central_access.encode(gis)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--publish", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--output", type=Path)
    parser.add_argument("--baseline", default=grid.BASELINE, type=Path)
    args = parser.parse_args()
    out = args.output or grid.CITY
    with disk_reservation(central_access.ROOT, out, "Baghdad wider inner ring", 96 << 20):
        record, network, context = evaluate(args.baseline)
        for path, content in outputs(record, network, context).items():
            target = out / path.relative_to(grid.CITY)
            if args.check:
                actual = target.read_bytes()
                same = central_access.map_pixels_match(actual, content) if path == FIGURE else actual == content
                if not same:
                    raise SystemExit(f"Regenerate the wider ring study. {target.name} differs.")
            else:
                write(target, content)
        print(record["comparison_id"])


if __name__ == "__main__":
    main()
