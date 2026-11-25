"""Publish Baghdad's connected planning network and its street-walk coverage."""

import argparse
from contextlib import nullcontext
from hashlib import sha256
from io import BytesIO
from math import cos, radians
from pathlib import Path

import numpy as np

from engineering.performance import disk_reservation

from . import central_access, central_service_map, holistic_access, holistic_gaps, holistic_network
from .airport_integration import write_atomic


CITY = Path(__file__).resolve().parent
MAP = CITY / "maps"
ROOT = CITY.parents[1]
MAP_FILE = MAP / "baghdad-network.png"
DATA_FILE = MAP / "baghdad-network.geojson"
RECORD_FILE = CITY / "baghdad-network.json"
REPORT_FILE = CITY / "NETWORK.md"
PALETTE = ("#00766f", "#205ca7", "#a84a13", "#943a75", "#386f24", "#693fad", "#277d9a", "#8a6521",
           "#424c7c", "#aa3740", "#347e55", "#695243", "#156a95", "#53562b", "#096b43", "#8a1f58")


def evaluate(*, step_m=300, spacing_m=650, max_infill=None):
    _, _, historic, context = central_access.original_cases()
    graph = central_access.walking_graph()
    base = holistic_network.evaluate(graph=graph)
    network, access, cells = holistic_access.evaluate(
        base, holistic_network.insert_stations, historic["clockface"],
        graph=graph, context=context, step_m=step_m, spacing_m=spacing_m, max_infill=max_infill,
    )
    paths = (Path(__file__), Path(holistic_access.__file__), Path(holistic_gaps.__file__), Path(central_access.__file__),
             Path(central_service_map.__file__),
             *(central_access.MAPPING / name for name in (
                 "street-source.json", "walking-graph.npz.gz", "walking-streets.geojson.gz",
                 "worldpop-2026-source.json", "worldpop-2026-pixels.npz.gz",
                 "ghsl-2025-source.json", "ghsl-2025-pixels.npz.gz")),
             central_access.INPUTS[-1])
    record = {"network": network, "walking_access": access, "undercoverage_grid": cells,
              "coverage_gap_areas": holistic_gaps.prioritize(cells, network),
              "purpose": "Integrated metropolitan planning geometry and pedestrian coverage",
              "schema": "osr-baghdad-metropolitan-network-publication/1",
              "sources": {p.relative_to(ROOT).as_posix(): central_access.digest(p) for p in paths}}
    record["publication_id"] = sha256(central_access.encode(record)).hexdigest()
    return record, context


def transfer_points(network):
    stations = network["stations"]
    points = {key: row["coordinates"] for key, row in stations.items() if len(row["lines"]) > 1}
    for transfer in network["transfers"]:
        for station in transfer.get("station_ids", []):
            points[station] = stations[station]["coordinates"]
    return points


def image(record, context):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon

    network, access = record["network"], record["walking_access"]
    lines, stations = network["lines"], network["stations"]
    walks = access["population"]["worldpop-2026"]["metropolitan"]["cases"]["connected_network"]
    bgcolor, ink = "#f8f6ee", "#14383c"
    figure = plt.figure(figsize=(15, 12.8), facecolor=bgcolor)
    ax = figure.add_axes((.028, .095, .719, .798), facecolor="#f5f0e5")
    water, rivers, roads = central_service_map.source_geometry(context)
    ax.add_collection(PatchCollection([Polygon(poly, closed=True) for poly in water],
                                       facecolor="#b8dfe7", edgecolor="none", zorder=1))
    ax.add_collection(LineCollection(rivers, colors="#99ccd7", linewidths=1.25, zorder=1.1))
    ax.add_collection(LineCollection(roads, colors="#b6aa98", linewidths=.45, alpha=.41, zorder=2))
    cells = [cell for cell in record["undercoverage_grid"] if cell["beyond_1200_m"] > 0]
    xy = np.asarray([cell["coordinates"] for cell in cells])
    counts = np.asarray([cell["beyond_1200_m"] for cell in cells])
    if len(xy):
        ax.scatter(*xy.T, s=np.clip(counts / 135, .6, 88), c="#ce7a46", alpha=.25, lw=0, zorder=2.5)

    handles, all_points = [], []
    for i, (key, line) in enumerate(lines.items()):
        color = PALETTE[i % len(PALETTE)]
        points = np.array(line["geometry"])
        all_points.extend(points)
        ax.plot(*points.T, color=bgcolor, linewidth=3.7, solid_capstyle="round", zorder=3)
        ax.plot(*points.T, color=color, linewidth=2.05, solid_capstyle="round", zorder=4)
        stops = np.array([stations[stop]["coordinates"] for stop in line["station_ids"]])
        ax.scatter(*stops.T, s=9, c=bgcolor, edgecolors=color, lw=.62, zorder=5)
        handles.append(Line2D([0], [0], color=color, lw=2.8, label=key))

    transfers = transfer_points(network)
    if transfers:
        ax.scatter(*np.array(list(transfers.values())).T, s=25, c=bgcolor,
                   edgecolors=ink, linewidths=1.02, zorder=6)
    for row in network["transfers"]:
        path = row.get("geometry")
        if path:
            ax.plot(*np.array(path).T, ls=(0, (1.5, 1.5)), color=ink, lw=1.3, zorder=5.5)

    destinations = (
        ("Airport terminal", ("airport terminal", "airport-00"), (-8, -14)),
        ("Tahrir Square", ("tahrir",), (12, -12)),
        ("Al Mansour", ("mansour",), (-15, 12)),
        ("Al-Shorja", ("shorja",), (6, 16)),
        ("Zayouna", ("zayouna",), (10, 10)),
        ("University of Baghdad", ("university of baghdad",), (10, -14)),
    )
    for name, patterns, offset in destinations:
        match = next((row for key, row in stations.items()
                      if any(word in f"{key} {row['name']}".lower() for word in patterns)), None)
        if match:
            ax.annotate(name, match["coordinates"], xytext=offset, textcoords="offset points", ha="right" if offset[0]<0 else "left",
                        fontsize=8.5, color=ink, weight="bold", zorder=7,
                        bbox=dict(boxstyle="round,pad=.18", fc=bgcolor, ec="none", alpha=.93))
    # Label route termini with their service code. Fill the legend with the
    # full set so every coloured line is interpretable even where labels meet.
    for handle, line in zip(handles, lines.values(), strict=True):
        points = np.asarray(line["geometry"])
        pos = points[0]
        ax.annotate(handle.get_label(), pos, xytext=(3, 5), textcoords="offset points", fontsize=6.7,
                    color=handle.get_color(), weight="bold", clip_on=True, zorder=6.5,
                    bbox=dict(boxstyle="round,pad=.12", fc=bgcolor, ec="none", alpha=.93))
    for gap in record["coverage_gap_areas"][:6]:
        ax.annotate(str(gap["rank"]), gap["coordinates"], color="#8f3d15", fontsize=8,
                    weight="bold", ha="center", va="center", zorder=6.2,
                    bbox=dict(boxstyle="round,pad=.2", fc=bgcolor, ec="#b95f35", lw=.85))

    west, south = np.min(all_points, axis=0)
    east, north = np.max(all_points, axis=0)
    bounds = access["population"]["worldpop-2026"]["bbox"]
    ax.set(xlim=(min(west - .015, bounds["west"]), max(east + .015, bounds["east"])),
           ylim=(min(south - .015, bounds["south"]), max(north + .015, bounds["north"])),
           aspect=1 / cos(radians(33.3)), xticks=[], yticks=[])
    for spine in ax.spines.values():
        spine.set_color("#d7cbbc")
    ax.annotate("N", xy=(.963, .969), xytext=(.963, .927), xycoords="axes fraction",
                textcoords="axes fraction", ha="center", va="top", color=ink, weight="bold",
                arrowprops=dict(arrowstyle="-|>", color=ink))

    figure.text(.052, .968, "Baghdad metropolitan rail network", color=ink, fontsize=29, weight="bold", va="top")
    figure.text(.053, .921, f"{len(lines)} connected lines   ·   {len(stations)} proposed station points   ·   "
                f"{len(access['infill'])} selected infill stops", color="#445d59", fontsize=13, va="top")
    figure.text(.765, .876, "Line key", color=ink, fontsize=13.5, weight="bold")
    figure.legend(handles=handles, loc="upper left", bbox_to_anchor=(.752,.872), labelcolor=ink,
                  frameon=False, ncol=2, fontsize=9.5, columnspacing=.8, handlelength=1.7)
    figure.text(.765, .625, "How to read the map", color=ink, fontsize=12, weight="bold")
    figure.legend(handles=(
        Line2D([], [], marker="o", markerfacecolor=bgcolor, markeredgecolor=ink, ls="None", label="Station or interchange"),
        Line2D([], [], color="#bb6637", alpha=.55, marker="o", ls="None", label="People beyond a 1.2 km walk"),
    ), loc="upper left", bbox_to_anchor=(.752,.619), frameon=False, fontsize=9.3, labelcolor=ink)
    figure.text(.765, .505, "Estimated walking access", color=ink, fontsize=11.5, weight="bold")
    figure.text(.765, .475, f"{walks['800']['share_pct']:.1f}% within 800 m", color="#236b65", fontsize=13, weight="bold")
    figure.text(.765, .448, f"{walks['1200']['share_pct']:.1f}% within 1,200 m", color="#236b65", fontsize=13, weight="bold")
    figure.text(.765, .427, "WorldPop 2026 estimates\nMetropolitan study window\nWalks follow mapped streets",
                color="#53605b", fontsize=10, linespacing=1.5, va="top")
    figure.text(.765, .324, "Largest walking gaps", color=ink, fontsize=11.5, weight="bold")
    gaps = record["coverage_gap_areas"][:6]
    figure.text(.765, .307, "\n".join(f"{gap['rank']}.  {gap['beyond_1200_m']:,} residents" for gap in gaps),
                color="#8f3d15", fontsize=10, linespacing=1.45, va="top")
    figure.text(.765, .147, "Planning corridors and stops.\nProgramme and costs require\na matched service definition.",
                color="#53605b", fontsize=10, linespacing=1.4, va="top")
    figure.text(.053, .056, "Population dots are summed over 1 km cells. Dot area represents residents beyond a 1.2 km walk.",
                color="#53605b", fontsize=9.3)
    figure.text(.053, .032, "Basemap and walking streets © OpenStreetMap contributors   ·   Population © WorldPop / University of Southampton",
                color="#53605b", fontsize=8.7)
    output = BytesIO()
    figure.savefig(output, format="png", dpi=170)
    plt.close(figure)
    return output.getvalue()


def report(result):
    network, access = result["network"], result["walking_access"]
    lines, stations = network["lines"], network["stations"]
    out = [
        "# Baghdad metropolitan rail network", "",
        f"This is one connected planning network for Baghdad, with {len(lines)} lines and {len(stations)} station points. "
        "It includes the Airport terminal approach and the routes through central Baghdad, alongside the links to the outer districts. "
        "A station belongs to an ordered rail line, and transfers use explicit interchange records.", "",
        "![One connected map of Baghdad’s proposed railway and its walking coverage](maps/baghdad-network.png)", "",
        "[Open the full map](maps/baghdad-network.png) · [Rail lines, stations and transfers in GeoJSON](maps/baghdad-network.geojson) · "
        "[Engineering input, coverage and gap data](baghdad-network.json)", "",
        "## Walk to a station", "",
        "| Source and area | Estimated residents | Earlier trial within 800 m / 1,200 m | Integrated network before infill | Integrated network with infill |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, result_by_area in access["population"].items():
        for area in ("metropolitan", "central"):
            row = result_by_area[area]
            percentages = [" / ".join(f"{estimate[str(limit)]['share_pct']:g}%" for limit in access["walk_m"])
                           for case in ("earlier_clockface", "connected_before_infill", "connected_network")
                           for estimate in (row["cases"][case],)]
            out.append(f"| {name} · {area} | {row['population']:,} | " + " | ".join(percentages) + " |")
    out.extend([
        "",
        "The metropolitan denominator covers the retained study window from 44.20° to 44.75° E and 33.05° to 33.50° N, "
        "including outlying settlements. The central denominator uses the earlier walking study window. "
        "The two population grids estimate residents independently. Street snaps up to "
        f"{access['station_and_population_snap_m']} m are included in the walking distance. "
        f"{len(access['proposed_stops_without_a_street_snap'])} mapped station points have no street snap in that range. "
        "Land access, crossing safety and station entrance positions still require local verification.", "",
        "The orange population layer shows where the rail plan still leaves walks longer than 1,200 m or where the "
        "retained street data cannot establish a path. The geographic record provides the estimated remaining population by 1 km cell.", "",
        "## Largest remaining walking gaps", "",
        "The numbered areas on the map rank 4 × 4 km areas by the number of WorldPop residents beyond a 1,200 m walk. "
        "Nearby rail links are shown by straight-line proximity for alignment review.", "",
        "| Map rank | Approximate gap centre | Residents beyond 1,200 m | Nearest rail alignments |",
        "|---:|---|---:|---|",
    ])
    for gap in result["coverage_gap_areas"][:6]:
        lon, lat = gap["coordinates"]
        nearby = ", ".join(f"{link['line_id']} ({link['alignment_distance_m']:,} m)" for link in gap["nearby_rail"])
        out.append(f"| {gap['rank']} | {lat:.4f}° N, {lon:.4f}° E | {gap['beyond_1200_m']:,} | {nearby} |")
    out.extend(["",
        "## How the network is generated", "",
        "1. Assemble the timed alignments into ordered passenger lines. Incorporate the corrected geographic Airport approach "
        "and retain the central station calls as part of the same network. Show only lines with a complete route.",
        "2. Establish explicit transfer locations. A crossing on the map alone carries no transfer. Check that every line and "
        "station can be reached through a single passenger graph.",
        f"3. Test station locations along the rail lines every {access['candidate_step_m']} m. Screen new stops within "
        f"{access['minimum_infill_spacing_m']} m of another stop on the same line, over mapped water or beyond the street snap. "
        "The spacing and sampling interval are editable planning settings.",
        "4. Repeatedly choose the location that reaches the most additional WorldPop residents within 800 m over the street graph. "
        "Break ties by 1,200 m gain, then line and chainage. Continue while a feasible candidate can improve either distance or until an explicit cap is reached.",
        "5. Recalculate both thresholds against WorldPop and GHS-POP for the final locations, including the revised stops and transfers. "
        "Check each rail line's chainages and verify the network after infill.", "",
        "## End-to-end routes", "", "| Line | First stop | Last stop | Route km | Station points |", "|---|---|---|---:|---:|",
    ])
    for line, item in lines.items():
        ids = item["station_ids"]
        first = stations[ids[0]]["name"]
        last = "Returns to first stop" if item["loop"] else stations[ids[-1]]["name"]
        out.append(f"| {line} | {first} | {last} | {item['one_way_km']:.2f} | {len(ids)} |")
    out.extend(["", "The revised routes and stops need their own running times, depot and turnback design, protection, "
                "fleet and cost evaluation. The earlier budgets and timetables belong to their original studies.", "",
                "Run `./osr design railway baghdad-network --check` to reproduce the published map and coverage. "
                "Use `--output build/baghdad-network-trial` when testing other station spacing or candidate intervals.", "",
                f"Publication `{result['publication_id']}`.", ""])
    return "\n".join(out)


def outputs(record, context):
    geojson = holistic_network.geojson(record["network"])
    geojson["publication_id"] = record["publication_id"]
    unmatched = set(record["walking_access"]["proposed_stops_without_a_street_snap"])
    for feature in geojson["features"]:
        properties = feature["properties"]
        if "station_id" in properties:
            properties["street_snap_within_limit"] = properties["station_id"] not in unmatched
    geojson["features"].extend({"type": "Feature", "geometry": {"type": "Point", "coordinates": cell["coordinates"]},
                                "properties": {"kind": "walking-access", "estimated_residents": cell["people"],
                                               "residents_beyond_1200_m": cell["beyond_1200_m"]}}
                               for cell in record["undercoverage_grid"])
    for gap in record["coverage_gap_areas"]:
        west, south, east, north = gap["bounds_wsen"]
        ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
        geojson["features"].append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                                    "properties": {"kind": "coverage-gap-area", **gap}})
    return {RECORD_FILE: central_access.encode(record), DATA_FILE: central_access.encode(geojson),
            REPORT_FILE: report(record).encode(), MAP_FILE: image(record, context)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--publish", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--output", type=Path)
    parser.add_argument("--sample-step-m", type=int, default=300)
    parser.add_argument("--infill-spacing-m", type=int, default=650)
    parser.add_argument("--max-infill", type=int)
    args = parser.parse_args()
    if args.output is None and (args.sample_step_m, args.infill_spacing_m, args.max_infill) != (300, 650, None):
        parser.error("Use --output for an alternative planning scenario")
    reservation = (nullcontext() if args.check else
                   disk_reservation(ROOT, args.output or CITY, "Baghdad connected network and coverage", 96 << 20))
    with reservation:
        record, context = evaluate(step_m=args.sample_step_m, spacing_m=args.infill_spacing_m, max_infill=args.max_infill)
        for path, value in outputs(record, context).items():
            if args.check:
                current = path.read_bytes()
                matches = central_access.map_pixels_match(current, value) if path == MAP_FILE else current == value
                if not matches:
                    raise SystemExit(f"Run the Baghdad network generator again. {path.name} differs.")
            else:
                target = args.output / path.relative_to(CITY) if args.output else path
                target.parent.mkdir(parents=True, exist_ok=True)
                write_atomic(target, value)
        print(record["publication_id"])


if __name__ == "__main__":
    main()
