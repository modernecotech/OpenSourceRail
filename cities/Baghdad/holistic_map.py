"""Publish Baghdad's connected planning network and its street-walk coverage."""

import argparse
from contextlib import nullcontext
from hashlib import sha256
from io import BytesIO
from math import cos, radians
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

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
DELIVERY_FILE = CITY / "NETWORK-DELIVERY.md"
PALETTE = ("#00766f", "#205ca7", "#a84a13", "#943a75", "#386f24", "#693fad", "#277d9a", "#8a6521",
           "#424c7c", "#aa3740", "#347e55", "#695243", "#156a95", "#53562b", "#096b43", "#8a1f58")
DEFAULT_THROUGH_ROUTES = 16
GRID_SPINE_LIMIT = 8
LOCAL_COVERAGE_LINK_LIMIT = 8
LOCAL_COVERAGE_ROUTE_KM = 88
LAYOUT_NAMES = {"short_links": "Previous short-link map", "one_ring": "Grid with outer ring",
                "two_rings": "Grid with two rings", "mixed_one_ring": "Grid and local links with outer ring",
                "mixed_two_rings": "Grid and local links with two rings",
                "targeted_relief": "Grid with targeted relief link",
                "inner_ring_overlay": "Inner ring added to the same mixed grid"}


def route_samples(geometry):
    track = holistic_network.Track(geometry)
    return np.asarray([track.at(km) for km in np.linspace(.001, track.km - .001, max(2, int(track.km * 10)))]) * (
        holistic_network.LOCAL_METRES)


def layout_rank(candidate, reference, walking_shortfall, route_km):
    trips, prior = candidate["journeys"], reference["journeys"]
    paired = candidate["paired_journeys"]
    ratios = (
        prior["at_most_one_transfer_share_of_all_pct"] /
        max(trips["at_most_one_transfer_share_of_all_pct"], 1e-12),
        (paired["candidate_elapsed_p90_min"] or float("inf")) /
        (paired["reference_elapsed_p90_min"] or 1.),
        candidate["concentration"]["busiest_directed_segment_share_of_served_pct"] /
        max(reference["concentration"]["busiest_directed_segment_share_of_served_pct"], 1e-12),
    )
    return round(walking_shortfall, 3), round(max(ratios), 8), round(sum(ratios), 8), route_km


def add_direct_routes(network, population, baseline_walk, graph, context, limit, *, candidates=None,
                      route_km_cap=None, balance_axes=False, coverage_goal=None):
    if candidates is None:
        from . import holistic_through

        planning_cells = holistic_access.coverage_cells(population, baseline_walk)
        candidates = holistic_through.generate(network, context, graph, coverage_cells=planning_cells)
    remaining = baseline_walk > 1200
    pending, comparisons = {}, {}
    for candidate in candidates:
        code = candidate["id"]
        track = holistic_network.Track(candidate["geometry"])
        proposed = {stop["id"]: track.at(stop["chainage_km"]) for stop in candidate["stops"]}
        proposed.update({f"transfer-{i}": item["point"] for i, item in enumerate(candidate["required_interchanges"])})
        access, _ = holistic_access.walk_to_station(proposed, graph, population)
        pixels = np.flatnonzero((access <= 1200) & remaining)
        comparisons[code] = {**candidate, "one_way_km": track.km,
                             "initial_additional_worldpop": round(float(population.counts[pixels].sum())),
                             "status": "available for comparison"}
        pending[code] = pixels

    chosen, total_km = [], 0.
    axis_counts = {}
    while pending and len(chosen) < limit:
        if coverage_goal is not None and population.counts[~remaining].sum() >= coverage_goal:
            break
        ranks = []
        for code, pixels in pending.items():
            gain = round(float(population.counts[pixels[remaining[pixels]]].sum()), 3)
            km = comparisons[code]["one_way_km"]
            if not gain or (route_km_cap is not None and total_km + km > route_km_cap + 1e-7):
                continue
            axis = comparisons[code]["screening"].get("orientation")
            rank = axis_counts.get(axis, 0) if balance_axes else 0
            ranks.append((rank, -round(gain / km, 4), -gain, km, code))
        if not ranks:
            break
        _, _, _, km, code = min(ranks)
        pending.pop(code)
        option = comparisons[code]
        try:
            revised = holistic_network.insert_through_lines(network, [option], graph=graph, context=context)
        except ValueError as error:
            option.update(status="rejected", reason=str(error))
            continue
        stations = {key: stop["coordinates"] for key, stop in revised["stations"].items()}
        actual, _ = holistic_access.walk_to_station(stations, graph, population)
        new_remaining = actual > 1200
        gain = round(float(population.counts[remaining & ~new_remaining].sum()))
        if not gain or np.any(new_remaining & ~remaining):
            option.update(status="rejected", reason="Applied stations must improve coverage and retain previous access")
            continue
        option.update(status="included in planning map", marginal_additional_worldpop=gain)
        chosen.append(code)
        total_km += km
        axis = option["screening"].get("orientation")
        axis_counts[axis] = axis_counts.get(axis, 0) + 1
        network, remaining = revised, new_remaining
    if limit and route_km_cap is None and not chosen:
        raise ValueError("No screened through route could improve the connected network")
    network = holistic_network.insert_through_lines(network, [], graph=graph, context=context, connect_through_lines=True)
    return network, {"selected": chosen, "max_through_routes": limit, "comparisons": comparisons,
                     "objective": "Additional 1,200 m WorldPop residents per route-km, then residents, route-km and ID"}


def compare_layouts(network, population, baseline_walk, graph, context):
    from . import holistic_grid, holistic_journeys, holistic_orbitals
    from .holistic_through import MAX_DUPLICATION_SHARE, RAIL_DUPLICATION_M

    short_links, short_choices = add_direct_routes(network, population, baseline_walk, graph, context, DEFAULT_THROUGH_ROUTES)
    base_km = network["topology"]["route_km"]
    added_km = sum(short_choices["comparisons"][code]["one_way_km"] for code in short_choices["selected"])
    cells = holistic_access.coverage_cells(population, baseline_walk)
    candidates = holistic_grid.generate(network, context, graph, coverage_cells=cells)
    one_ring, one_choices = add_direct_routes(network, population, baseline_walk, graph, context, GRID_SPINE_LIMIT,
                                              candidates=candidates, route_km_cap=added_km, balance_axes=True)
    if len({one_choices["comparisons"][code]["screening"]["orientation"] for code in one_choices["selected"]}) < 2:
        raise ValueError("A cross-city grid requires screened spines in both directions")
    layouts = {"short_links": short_links, "one_ring": one_ring}
    choices = {"one_ring": one_choices}
    ring_only, orbit_evidence = holistic_orbitals.add_inner_orbit(network, graph, context)
    extra_rings = sorted(set(ring_only["lines"]) - set(network["lines"]))
    if extra_rings:
        loop_km = sum(ring_only["lines"][code]["one_way_km"] for code in extra_rings)
        smaller, small_choices = add_direct_routes(network, population, baseline_walk, graph, context, GRID_SPINE_LIMIT,
                                                   candidates=candidates, route_km_cap=added_km - loop_km, balance_axes=True)
        if len({small_choices["comparisons"][code]["screening"]["orientation"] for code in small_choices["selected"]}) == 2:
            two_ring, orbit_evidence = holistic_orbitals.add_inner_orbit(
                smaller, graph, context, southern_way=orbit_evidence["southern_way"])
            if set(two_ring["lines"]) - set(smaller["lines"]):
                if two_ring["topology"]["route_km"] <= base_km + added_km + .02:
                    layouts["two_rings"] = two_ring
                    choices["two_rings"] = small_choices

    def walking_distances(variant):
        sites = {key: row["coordinates"] for key, row in variant["stations"].items()}
        return holistic_access.walk_to_station(sites, graph, population)[0]

    walks = {label: walking_distances(variant) for label, variant in layouts.items()}
    coverage_goal = float(population.counts[walks["short_links"] <= 1200].sum())
    # Compare the same grid structures with only the local links needed to
    # recover walking access on the earlier map. Keep their added route-km explicit.
    for label, grid_choices in list(choices.items()):
        corridors = cKDTree(np.concatenate([route_samples(layouts[label]["lines"][code]["geometry"])
                                            for code in grid_choices["selected"]]))
        local_candidates = [row for row in short_choices["comparisons"].values()
                            if (corridors.query(route_samples(row["geometry"]))[0] <= RAIL_DUPLICATION_M).mean()
                            <= MAX_DUPLICATION_SHARE]
        variant, local = add_direct_routes(layouts[label], population, walks[label], graph, context,
                                           LOCAL_COVERAGE_LINK_LIMIT,
                                           candidates=local_candidates,
                                           route_km_cap=LOCAL_COVERAGE_ROUTE_KM, coverage_goal=coverage_goal)
        if local["selected"]:
            mixed = "mixed_" + label
            layouts[mixed], walks[mixed] = variant, walking_distances(variant)
            choices[mixed] = {**grid_choices, "spines": grid_choices["selected"], "local_links": local["selected"],
                              "selected": [*grid_choices["selected"], *local["selected"]],
                              "comparisons": {**grid_choices["comparisons"], **local["comparisons"]}}

    journeys = holistic_journeys.compare(layouts, graph=graph, population=population, match_service_to="short_links")

    def rank(label):
        result = journeys["variants"][label]
        shortfall = max(0., coverage_goal - float(population.counts[walks[label] <= 1200].sum()))
        return (*layout_rank(result, journeys["variants"]["short_links"], shortfall,
                             layouts[label]["topology"]["route_km"]), label)

    selected = min(choices, key=rank)
    pre_relief = selected
    initial = layouts[selected]
    initial_choices = choices[selected]
    experiments = {"short_links": short_links, selected: initial}
    rejected = {}
    if len(initial_choices.get("local_links", [])) < LOCAL_COVERAGE_LINK_LIMIT:
        for code in short_choices["selected"]:
            option = short_choices["comparisons"][code]
            if code in initial["lines"] or option["one_way_km"] < 9:
                continue
            try:
                experiments[code] = holistic_network.insert_through_lines(
                    initial, [option], graph=graph, context=context, connect_through_lines=True)
            except ValueError as error:
                rejected[code] = str(error)
    if "two_rings" in layouts and "M15" not in initial["lines"]:
        overlay, overlay_evidence = holistic_orbitals.add_inner_orbit(
            initial, graph, context, southern_way=orbit_evidence["southern_way"])
        if "M15" in overlay["lines"]:
            experiments["inner_ring_overlay"] = overlay

    relief = holistic_journeys.compare(experiments, graph=graph, population=population, match_service_to="short_links")
    if relief["demand_sample"]["sample_id"] != journeys["demand_sample"]["sample_id"]:
        raise ValueError("Relief tests must use the original origin–destination sample")
    profile = relief["variants"]
    reference = profile["short_links"]
    reference_pressure = profile[selected]["concentration"]["peak_load_per_departure_index"]
    targets = {}
    for label, variant in experiments.items():
        if label in ("short_links", selected):
            continue
        candidate = profile[label]
        distances = walking_distances(variant)
        shortfall = max(0., coverage_goal - float(population.counts[distances <= 1200].sum()))
        if candidate["concentration"]["peak_load_per_departure_index"] < reference_pressure:
            targets[label] = (*layout_rank(candidate, reference, shortfall, variant["topology"]["route_km"]), label)
        if label == "inner_ring_overlay":
            layouts[label], walks[label], choices[label] = variant, distances, initial_choices
            journeys["variants"][label] = candidate
    initial_rank = (*layout_rank(profile[selected], reference, max(0., coverage_goal - float(
        population.counts[walks[selected] <= 1200].sum())), initial["topology"]["route_km"]), selected)
    added_relief = min(targets, key=targets.get) if targets else None
    if added_relief is not None and targets[added_relief] < initial_rank:
        trial = experiments[added_relief]
        if added_relief == "inner_ring_overlay":
            selected = added_relief
            orbit_evidence = overlay_evidence
        else:
            selected = "targeted_relief"
            layouts[selected], walks[selected] = trial, walking_distances(trial)
            option = short_choices["comparisons"][added_relief] | {
                "basis_for_selection": "Lower peak demand per departure on the same synthetic trips and running train-km",
                "marginal_additional_worldpop": round(float(population.counts[
                    (walks[selected] <= 1200) & (walking_distances(initial) > 1200)].sum())),
            }
            choices[selected] = {**initial_choices,
                                 "selected": [*initial_choices["selected"], added_relief],
                                 "spines": initial_choices.get("spines", initial_choices["selected"]),
                                 "local_links": [*initial_choices.get("local_links", []), added_relief],
                                 "comparisons": initial_choices["comparisons"] | {added_relief: option}}
            journeys["variants"][selected] = profile[added_relief]
    else:
        added_relief = None

    best = layouts[selected]
    sensitivity = holistic_journeys.compare({"short_links": short_links, selected: best}, graph=graph,
                                            population=population, match_service_to="short_links",
                                            balance_frequencies=True)
    if sensitivity["demand_sample"]["sample_id"] != journeys["demand_sample"]["sample_id"]:
        raise ValueError("Headway comparisons must use the same origin–destination sample")
    record = {**choices[selected], "layout": selected, "tested_layouts": {
        key: {"candidate_id": item["candidate_id"], **item["topology"],
              "new_spines": metadata.get("spines", metadata["selected"] if key != "short_links" else []),
              "local_links": metadata.get("local_links", metadata["selected"] if key == "short_links" else []),
              "added_route_km": round(item["topology"]["route_km"] - base_km, 2),
              "rings": [code for code, line in item["lines"].items() if line["loop"]]}
        for key, item in layouts.items() for metadata in (choices.get(key, short_choices),)},
        "matched_added_route_km": round(added_km, 2), "orbital_evidence": orbit_evidence, "journeys": journeys,
        "headway_sensitivity": sensitivity["variants"], "accepted_relief": added_relief, "pre_relief_layout": pre_relief,
        "relief_tests": {label: {"concentration": profile[label]["concentration"],
                                 "journeys": profile[label]["journeys"], "service": profile[label]["service"]}
                         for label in experiments if label != "short_links"},
        "rejected_relief": rejected,
        "layout_rule": "Recover earlier 1,200 m walking access, then minimise the worst relative change in the shares of OD "
                       "served with at most one transfer and trips on the busiest segment, and in paired p90 journey time"}
    return best, record, {name: variant["stations"] for name, variant in layouts.items()}


def evaluate(*, step_m=300, spacing_m=650, max_infill=None, max_through_routes=None):
    from . import residential_planning, residential_systems

    _, _, historic, context = central_access.original_cases()
    graph = central_access.walking_graph()
    base = holistic_network.evaluate(graph=graph)
    extend = lambda network, population, walk, graph, context: residential_planning.evaluate(
        network, population, walk, graph, context, build_reference=compare_layouts,
        enforce_reference=(step_m, spacing_m, max_infill) == (300, 650, None))
    if max_through_routes is not None:
        extend = (lambda network, population, walk, graph, context:
                  (*add_direct_routes(network, population, walk, graph, context, max_through_routes), {})) if max_through_routes else None
    network, access, cells = holistic_access.evaluate(
        base, holistic_network.insert_stations, historic["clockface"],
        graph=graph, context=context, step_m=step_m, spacing_m=spacing_m, max_infill=max_infill, add_through_routes=extend,
    )
    paths = (Path(__file__), Path(holistic_access.__file__), Path(holistic_gaps.__file__), Path(central_access.__file__),
             Path(central_service_map.__file__), *(CITY / name for name in (
                 "holistic_through.py", "holistic_grid.py", "holistic_journeys.py", "holistic_orbitals.py",
                 "holistic_pathways.py", "residential_layouts.py", "residential_planning.py", "residential_delivery.py",
                 "residential_systems.py", "residential_report.py", "residential-access.toml", "central-access.json",
                 *residential_systems.SOURCES)),
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


def line_style(record):
    selection = record["walking_access"]["through_route_selection"] or {}
    selected = set(selection.get("selected", []))
    local = set(selection.get("local_links", []))
    axis_counts = {"east–west": 0, "north–south": 0}
    axis_colors = {"east–west": ("#176292", "#007488", "#2353a3", "#267f99"),
                   "north–south": ("#a54021", "#934e15", "#ba5829", "#813621")}
    style = {}
    for i, (code, line) in enumerate(record["network"]["lines"].items()):
        if line["loop"]:
            style[code] = ("orbital", "#7b4694" if code == "M09" else "#962f79", 2.9)
        elif code in local:
            style[code] = ("local coverage", PALETTE[i % len(PALETTE)], 1.65)
        elif code in selected:
            role = selection["comparisons"][code]["screening"].get("orientation", "direct cross-city")
            colors = axis_colors.get(role, PALETTE)
            index = axis_counts.get(role, 0)
            style[code] = (role, colors[index % len(colors)], 2.8)
            axis_counts[role] = index + 1
        else:
            style[code] = ("retained", PALETTE[i % len(PALETTE)], 1.4)
    return style


def image(record, context):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon

    network, access = record["network"], record["walking_access"]
    lines, stations = network["lines"], network["stations"]
    cases = access["population"]["worldpop-2026"]["metropolitan"]["cases"]
    walks = cases["connected_network"]
    selection = access["through_route_selection"] or {}
    residential = selection.get("residential")
    through = selection.get("selected", [])
    spine_ids = selection.get("spines", through)
    style = line_style(record)
    rings = [code for code, item in lines.items() if item["loop"]]
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

    handles, all_points = {}, []
    for key, line in lines.items():
        role, color, width = style[key]
        prominent = role not in ("retained", "local coverage")
        points = np.array(line["geometry"])
        all_points.extend(points)
        z = 4.3 if prominent else 3.8
        ax.plot(*points.T, color=bgcolor, linewidth=width + 1.6, solid_capstyle="round", zorder=z - .15)
        ax.plot(*points.T, color=color, linewidth=width, solid_capstyle="round", zorder=z)
        stops = np.array([stations[stop]["coordinates"] for stop in line["station_ids"]])
        ax.scatter(*stops.T, s=10 if prominent else 6, c=bgcolor, edgecolors=color, lw=.62, zorder=5)
        handles[key] = Line2D([0], [0], color=color, lw=width, label=key)

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
    if residential:
        locations = np.asarray([row["coordinates"] for row in residential["destinations"]])
        ax.scatter(*locations.T, marker="*", s=115, facecolors="#e4a735", edgecolors=ink, lw=.7, zorder=7.2)
    # Label route termini with their service code. Fill the legend with the
    # full set so every coloured line is interpretable even where labels meet.
    for key, line in lines.items():
        handle = handles[key]
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
    description = (f"{len(lines)} connected lines   ·   {len(stations)} station sites   ·   {len(transfers)} interchanges"
                   if residential else f"{len(lines)} connected lines   ·   {len(spine_ids)} cross-city spines   ·   "
                   f"{len(rings)} orbital {'line' if len(rings) == 1 else 'lines'}   ·   {len(transfers)} interchanges")
    figure.text(.053, .921, description, color="#445d59", fontsize=12, va="top")
    is_grid = "layout" in selection
    legend_title = ("Main housing routes" if residential else "Grid spines and orbitals" if is_grid
                    else "Cross-city additions and orbitals")
    figure.text(.765, .876, legend_title,
                color=ink, fontsize=12.2, weight="bold")
    figure.legend(handles=[handles[code] for code in [*spine_ids, *rings]], loc="upper left",
                  bbox_to_anchor=(.752,.867), labelcolor=ink, frameon=False, ncol=4, fontsize=8.6,
                  columnspacing=.55, handlelength=1.4)
    figure.text(.765, .755, "Other passenger routes", color=ink, fontsize=11.5, weight="bold")
    figure.legend(handles=[handle for code, handle in handles.items() if style[code][0] in ("retained", "local coverage")],
                  loc="upper left", bbox_to_anchor=(.752,.744), labelcolor=ink, frameon=False, ncol=4,
                  fontsize=8.1, columnspacing=.85, handlelength=1.4)
    figure.text(.765, .625, "How to read the map", color=ink, fontsize=12, weight="bold")
    symbols = [Line2D([], [], marker="o", markerfacecolor=bgcolor, markeredgecolor=ink, ls="None", label="Station or interchange"),
               Line2D([], [], color="#bb6637", alpha=.55, marker="o", ls="None", label="People beyond a 1.2 km walk")]
    if residential:
        symbols.append(Line2D([], [], marker="*", markerfacecolor="#e4a735", markeredgecolor=ink,
                              ls="None", label="Journey test destination"))
    figure.legend(handles=symbols, loc="upper left", bbox_to_anchor=(.752,.619), frameon=False, fontsize=9.3, labelcolor=ink)
    figure.text(.765, .505, "Estimated walking access", color=ink, fontsize=11.5, weight="bold")
    figure.text(.765, .471, f"{walks['1200']['share_pct']:.1f}% within 1,200 m", color="#236b65", fontsize=14, weight="bold")
    earlier = cases.get("grid_reference", cases.get("short_links", cases["previous_network"]))
    figure.text(.765, .448, f"Previous map {earlier['1200']['share_pct']:.1f}%", color="#53605b", fontsize=10)
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
    selection = access["through_route_selection"]
    layouts = selection.get("tested_layouts") if selection else None
    residential = selection.get("residential") if selection else None
    out = [
        "# Baghdad metropolitan rail network", "",
        f"This is one connected planning network for Baghdad, with {len(lines)} lines and {len(stations)} station points. "
        "It includes the Airport terminal approach and the routes through central Baghdad, alongside the links to the outer districts. "
        f"The passenger graph has {network['topology']['transfer_stations']} proposed interchanges. "
        "A station belongs to an ordered rail line, and transfers use explicit interchange records.", "",
        "![One connected map of Baghdad’s proposed railway and its walking coverage](maps/baghdad-network.png)", "",
        "[Open the full map](maps/baghdad-network.png) · [Rail lines, stations and transfers in GeoJSON](maps/baghdad-network.geojson) · "
        "[Engineering input, coverage and gap data](baghdad-network.json)", "",
        "## Walk to a station", "",
        "The primary planning measure is a 1,200 m walk along the mapped street network. The 800 m result shows shorter access.", "",
        "| Source and area | Estimated residents | Previous map within 1,200 m | Retained routes with infill | Revised network within 1,200 m | Revised network within 800 m |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, result_by_area in access["population"].items():
        for area in ("metropolitan", "central"):
            row = result_by_area[area]
            percentages = [f"{row['cases'][case][limit]['share_pct']:g}%" for case, limit in (
                ("grid_reference" if residential else "short_links" if layouts else "previous_network", "1200"),
                ("infill_1200_priority", "1200"), ("connected_network", "1200"),
                ("connected_network", "800"))]
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
    ])
    if layouts:
        comparison = selection["journeys"]
        walks = access["population"]["worldpop-2026"]["metropolitan"]["cases"]
        out.extend([
            "## Network patterns and point-to-point trips", "",
            "The earlier short-link map, the east–west and north–south grid, and the inner-ring alternative use the same "
            "synthetic origin–destination demand. The first grid trials use the earlier map’s added route length as a ceiling. "
            "The mixed grids keep selected short links to recover access where the longer routes leave gaps.", "",
            "| Pattern | Spines / local links / rings | Added route-km | Within 1.2 km | All OD served | All OD with zero or one transfer | P90 elapsed (min) | Busiest line share | Busiest directed segment share |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for label, layout in layouts.items():
            assigned = comparison["variants"][label]
            stats, load = assigned["journeys"], assigned["concentration"]
            name = LAYOUT_NAMES[label]
            if label == selection["layout"]:
                name = f"**{name}**"
            out.append(f"| {name} | {len(layout['new_spines'])} / {len(layout['local_links'])} / {len(layout['rings'])} | "
                       f"{layout['added_route_km']:.1f} | {walks[label]['1200']['share_pct']:.2f}% | {stats['served_share_pct']:.2f}% | "
                       f"{stats['at_most_one_transfer_share_of_all_pct']:.2f}% | {stats['elapsed_p90_min']:.1f} | "
                       f"{load['busiest_line_boarding_share_pct']:.2f}% | {load['busiest_directed_segment_share_of_served_pct']:.2f}% |")
        if selection["accepted_relief"] and selection["layout"] == "targeted_relief":
            out.extend(["", f"The planning map retains **{selection['accepted_relief']}** as a relief link. Adding it to the best initial grid "
                        "lowered the peak demand per departure and improved the combined journey and load comparison. "
                        "The two-ring overlay tests the same initial grid with the inner ring added."])
        paired = comparison["variants"][selection["layout"]]["paired_journeys"]
        samples = comparison["demand_sample"]
        out.extend(["",
            f"The map shows **{LAYOUT_NAMES[selection['layout']]}**. The selection rule first seeks to restore the previous 1.2 km access. "
            "It then compares each grid’s one-transfer journey share, 90th-percentile time on matched journeys and busiest segment share "
            "with the earlier map, choosing the grid with the smallest worst relative change. If none restore coverage, the rule "
            "minimises the walking-access shortfall first.", "",
            f"For journeys served in both the selected and earlier networks, the weighted mean elapsed-time change is "
            f"**{paired['candidate_minus_reference_elapsed_mean_min']:+.2f} minutes**. The assignment holds daily train-km equal to "
            "the previous map’s service scenario. It includes walking, in-vehicle time, stops, waiting and a transfer penalty. "
            "The busiest-line share is a share of boardings. The busiest-segment share is a share of served journeys. "
            "These loads screen transfer pressure. Passenger counts, timetables and train capacities remain open.", "",
            str(samples["status"]) + ". " + samples["method"], "",
        ])
        if "two_rings" not in layouts:
            out.append("The inner orbital did not form a comparable two-ring grid within the screened route-length allowance.")
            out.append("")
        else:
            out.extend(["The inner orbital trial follows the retained road corridors across the Tigris at Al-A’imma and Al-Jadriya. "
                        "Its stations and interchanges support a planning comparison. Rail curves, bridge structures and grades require design.", ""])
        out.extend([
            "### Managing the busiest line at equal service effort", "",
            "The sensitivity redistributes departures toward busy sections within the same daily train-km. "
            "Both networks start with uniform headways and may vary each line’s frequency between half and twice that starting value. "
            "The assignment recalculates journeys after each frequency change. The peak index scales the maximum share of all sampled trips "
            "on a directed segment by its headway relative to six minutes. It compares expected demand per departure under the same synthetic trip volume.", "",
            "| Layout and frequency trial | M09 headway (min) | One-transfer-or-better share | Peak demand per departure index |",
            "|---|---:|---:|---:|",
        ])
        for label in ("short_links", selection["layout"]):
            for mode, assigned in (("uniform", comparison["variants"][label]),
                                   ("load-based", selection["headway_sensitivity"][label])):
                headway = assigned["service"]["line_headways_s"]["M09"] / 60
                direct = assigned["journeys"]["at_most_one_transfer_share_of_all_pct"]
                pressure = assigned["concentration"]["peak_load_per_departure_index"]
                out.append(f"| {LAYOUT_NAMES[label]}, {mode} | {headway:.2f} | {direct:.2f}% | {pressure:.3f} |")
        out.append("")
    if residential:
        from . import residential_report

        out.extend(residential_report.pathway_sections(residential, stations))
        out.extend(residential_report.delivery_summary(residential))
    else:
        out.extend(["## Cross-city additions", ""])
    if selection and not residential:
        added_km = sum(selection["comparisons"][code]["one_way_km"] for code in selection["selected"])
        out.extend([
            f"The generator compared {len(selection['comparisons'])} screened alignments. The selected layout "
            f"adds {len(selection['selected'])} through routes totalling {added_km:.1f} route-km, before any inner orbital. "
            "Every through route has an interchange at both termini. "
            "Intermediate interchanges are included where the geometry and station screens allow them. The coverage gain in each row is measured "
            "after the routes above it are added.", "",
            "| Line | Role | First interchange | Last interchange | Length | Interchanges | Additional residents within 1,200 m |",
            "|---|---|---|---|---:|---:|---:|",
        ])
        for code in selection["selected"]:
            row = selection["comparisons"][code]
            start, finish = [stations[key]["name"] for key in row["terminal_ids"]]
            count = network["through_lines"][code]["transfer_count"]
            role = row["screening"].get("orientation", "Local gap link")
            out.append(f"| {code} | {role} | {start} | {finish} | {row['one_way_km']:.2f} km | {count} | {row['marginal_additional_worldpop']:,} |")
        out.extend(["", "The centre lines are direct planning alignments. Detailed vertical profiles, curve design, property access, "
                    "bridge clearances and platform layouts still need engineering. The GeoJSON and JSON retain the tested geometry and source evidence.", ""])
    if not residential:
        out.extend([
        "## How the network is generated", "",
        "1. Assemble the timed alignments into ordered passenger lines. Incorporate the corrected geographic Airport approach "
        "and retain the central station calls as part of the same network. Show only lines with a complete route.",
        "2. Establish explicit transfer locations. A crossing on the map alone carries no transfer. Check that every line and "
        "station can be reached through a single passenger graph.",
        f"3. Test station locations along the rail lines every {access['candidate_step_m']} m. Screen new stops within "
        f"{access['minimum_infill_spacing_m']} m of another stop on the same line, over mapped water or beyond the street snap. "
        "The spacing and sampling interval are editable planning settings.",
        "4. Repeatedly choose the location that reaches the most additional WorldPop residents within 1,200 m over the street graph. "
        "Break ties by 800 m gain, then line and chainage.",
        "5. Generate direct routes anchored at stations on the retained network. Check dry street-accessible stations, mapped water crossings "
        "and intermediate interchange geometry. Rank tested routes by marginal residents within 1,200 m per added route-km. "
        "Recalculate coverage after each addition so overlapping catchments receive credit once.",
        "6. Recalculate both walking thresholds against WorldPop and GHS-POP for the final stations. Verify the connected passenger graph, "
        "all route termini and intermediate transfer locations.", "",
        ])
    out.extend(["## End-to-end routes", "", "| Line | First stop | Last stop | Route km | Station points |", "|---|---|---|---:|---:|"])
    for line, item in lines.items():
        ids = item["station_ids"]
        first = stations[ids[0]]["name"]
        last = "Returns to first stop" if item["loop"] else stations[ids[-1]]["name"]
        out.append(f"| {line} | {first} | {last} | {item['one_way_km']:.2f} | {len(ids)} |")
    out.extend(["", "The route and service allowances need a timetable, turnback, depot, protection and operating verification. "
                "The earlier published budgets and timetables belong to their original studies.", "",
                "Run `./osr design railway baghdad-network --check` to reproduce the published map and coverage. "
                "Use `--output build/baghdad-network-trial --max-through-routes 0` to compare revised station siting on the earlier routes.", "",
                f"Publication `{result['publication_id']}`.", ""])
    return "\n".join(out)


def outputs(record, context, *, refresh_readers=False):
    geojson = holistic_network.geojson(record["network"])
    geojson["publication_id"] = record["publication_id"]
    unmatched = set(record["walking_access"]["proposed_stops_without_a_street_snap"])
    style = line_style(record)
    for feature in geojson["features"]:
        properties = feature["properties"]
        if "station_id" in properties:
            properties["street_snap_within_limit"] = properties["station_id"] not in unmatched
            properties["marker-size"] = "small"
        if properties["kind"] == "line":
            role, color, width = style[properties["line_id"]]
            properties.update({"route_role": role, "stroke": color, "stroke-width": round(width * 1.5, 1)})
    geojson["features"].extend({"type": "Feature", "geometry": {"type": "Point", "coordinates": cell["coordinates"]},
                                "properties": {"kind": "walking-access", "estimated_residents": cell["people"],
                                               "residents_beyond_1200_m": cell["beyond_1200_m"]}}
                               for cell in record["undercoverage_grid"])
    for gap in record["coverage_gap_areas"]:
        west, south, east, north = gap["bounds_wsen"]
        ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
        geojson["features"].append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                                    "properties": {"kind": "coverage-gap-area", "stroke": "#ce7a46",
                                                   "stroke-opacity": .16, "fill-opacity": 0, **gap}})
    selection = record["walking_access"]["through_route_selection"] or {}
    residential = selection.get("residential")
    if residential:
        for destination in residential["destinations"]:
            geojson["features"].append({"type": "Feature", "geometry": {"type": "Point", "coordinates": destination["coordinates"]},
                                        "properties": {"kind": "journey-destination", **destination}})
    generated = {RECORD_FILE: central_access.encode(record), DATA_FILE: central_access.encode(geojson),
                 REPORT_FILE: report(record).encode(), MAP_FILE: image(record, context)}
    if residential:
        from .residential_report import delivery_report, refresh_headline

        generated[DELIVERY_FILE] = delivery_report(record).encode()
        if refresh_readers:
            for path in (CITY / "README.md", CITY / "PROPOSAL.md"):
                generated[path] = refresh_headline(path, residential)
    return generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--publish", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--output", type=Path)
    parser.add_argument("--sample-step-m", type=int, default=300)
    parser.add_argument("--infill-spacing-m", type=int, default=650)
    parser.add_argument("--max-infill", type=int)
    parser.add_argument("--max-through-routes", type=int, help="Replay the earlier short-link concept")
    args = parser.parse_args()
    if args.max_through_routes is not None and not 0 <= args.max_through_routes <= 20:
        parser.error("Use between zero and twenty through routes for a bounded planning comparison")
    if args.output is None and (args.sample_step_m, args.infill_spacing_m, args.max_infill, args.max_through_routes) != (
            300, 650, None, None):
        parser.error("Use --output for an alternative planning scenario")
    reservation = (nullcontext() if args.check else
                   disk_reservation(ROOT, args.output or CITY, "Baghdad connected network and coverage", 96 << 20))
    with reservation:
        record, context = evaluate(step_m=args.sample_step_m, spacing_m=args.infill_spacing_m, max_infill=args.max_infill,
                                   max_through_routes=args.max_through_routes)
        for path, value in outputs(record, context, refresh_readers=args.output is None).items():
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
