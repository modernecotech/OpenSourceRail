"""Measure central Baghdad access from stations with scheduled calls."""

import argparse
from collections import Counter
from hashlib import sha256
from io import BytesIO
import gzip
import json
from math import cos, radians
from pathlib import Path

import numpy as np
from scipy.sparse import bmat, csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

from engineering.ferrite_maglev.pilot_corridor import walking_graph, xy
from engineering.performance import disk_reservation

from .airport_integration import write_atomic
from . import central_service_map

CITY = Path(__file__).resolve().parent
ROOT = CITY.parents[1]
MAP = ROOT / "cities/catalogue/west-asia/Iraq/Baghdad"
MAPPING = MAP / "engineering/mapping"
CORE = (44.35, 33.293, 44.43, 33.365)
WALK_M = (800, 1200)
SNAP_M = 100
INPUTS = (CITY / "service-diagrams.json", CITY / "citywide-service.json", CITY / "station-register.json",
          CITY / "maps/network-606km.geojson", MAP / "map-context.json.gz")
DISTRICTS = {
    17603710648571: "Al-Rasheed",
    17603710648581: "Al-Saadoun",
    17603713493166: "Karkh",
    17603710648572: "Al-Kilani",
    17603710648568: "Medical City area",
    17603710648567: "Bab al-Muadham",
    17603713493172: "Karradat Maryam",
    17603710648566: "Al-Mustansiriya",
}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as handle:
            return json.load(handle)
    return json.loads(path.read_bytes())


def encode(record):
    return (json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n").encode()


def add_records(records, stops):
    unknown = set(stops) - records.keys()
    if unknown:
        raise ValueError("Timetable stop missing from the station register: " + ", ".join(sorted(unknown)))
    return {code: records[code] for code in sorted(stops)}


def original_cases():
    diagrams, clockface, register, routes, context = map(read, INPUTS)
    if (clockface["source_diagram_evaluation_id"] != diagrams["evaluation_id"]
            or register["map_source_sha256"][INPUTS[3].relative_to(ROOT).as_posix()] != digest(INPUTS[3])):
        raise ValueError("The diagram, clockface and GIS sources are from different revisions")
    mapped = {row["id"]: row["longitude_latitude"] for row in
              register["networks"]["metropolitan"]["mapped_points"]}
    mapped |= {f["properties"]["anchor_id"]: f["geometry"]["coordinates"] for f in routes["features"]
               if f["geometry"]["type"] == "Point" and "anchor_id" in f["properties"]}
    metro = diagrams["networks"]["metropolitan"]
    base = {stop["id"] for group in metro["groups"].values() for stop in group["outward_stops"]}
    timed = {row[0].removesuffix("-lap") for group in clockface["timetable"]["groups"].values()
             for pattern in group["patterns"] for row in pattern}
    active = {code for sections in clockface["scope"]["group_sections"].values() for code in sections}
    deferred = set(clockface["scope"]["deferred_sections"])
    reserved = set(clockface["scope"]["reserved_sections"])
    if (active & (deferred | reserved)) or deferred & reserved:
        raise ValueError("Passenger, deferred and reserved guideway scopes overlap")
    section_status = {code: label for label, codes in (("clockface calls", active), ("deferred access", deferred),
                      ("reserved guideway", reserved)) for code in codes}
    lines = []
    for feature in routes["features"]:
        if feature["geometry"]["type"] != "LineString":
            continue
        code = feature["properties"]["route_id"]
        lines.append({"type": "Feature", "geometry": feature["geometry"],
                      "properties": {"section": code, "status": section_status.pop(code)}})
    if section_status:
        raise ValueError("Map missing a physical railway section from the service ledger")
    if not np.isclose(clockface["in_service_route_km"] + sum(row["km"] for row in clockface["deferred"].values())
                      + sum(clockface["reserved_sections_km"].values()), clockface["costed_route_km"]):
        raise ValueError("Citywide service and guideway length scopes do not reconcile")
    baseline = {
        "status": "Retained comparison. Passenger access and unresolved connections require design revision.",
        "physical_route_km": clockface["costed_route_km"],
        "connected_clockface_km": clockface["in_service_route_km"],
        "deferred_km": sum(row["km"] for row in clockface["deferred"].values()),
        "reserved_km": sum(clockface["reserved_sections_km"].values()),
        "original_diagrammed_km_year": clockface["original_connected_train_km_year"],
        "original_held_km_year": clockface["original_held_train_km_year"],
        "unresolved_groups": clockface["original_unresolved_group_reasons"],
        "deferred": clockface["deferred"],
        "clockface_headway_s": clockface["timetable"]["headway_s"],
        "clockface_trips_day": clockface["demand_and_resources"]["passenger_trips_day"],
        "clockface_sets": sum(group["sets"] for group in clockface["timetable"]["groups"].values()),
    }
    return baseline, lines, {"original": add_records(mapped, base),
                                "clockface": add_records(mapped, timed)}, context


def _points(coordinates):
    lon, lat = zip(*coordinates, strict=True)
    return xy(lat, lon)


def distances_from_stops(stops, graph):
    """One sparse shortest-path solve including the station-to-street snap distance."""
    _, matrix, active, tree, _ = graph
    snap, idx = tree.query(_points(list(stops.values())))
    station_nodes = {}
    for offset, point in zip(snap, active[idx], strict=True):
        if offset <= SNAP_M:
            station_nodes[point] = min(station_nodes.get(point, float("inf")), offset)
    n = matrix.shape[0]
    if not station_nodes:
        return np.full(n, np.inf), int(len(snap))
    # The graph is symmetric except for the virtual source edges. A single
    # source gives an exact minimum over every permitted station alternative.
    edge_costs = list(station_nodes.values())
    edge_targets = list(station_nodes)
    start = csr_matrix((edge_costs, (np.zeros(len(edge_targets), dtype=int), edge_targets)), shape=(1, n))
    combined = bmat([[matrix, csr_matrix((n, 1))], [start, csr_matrix((1, 1))]], format="csr")
    values = dijkstra(combined, directed=True, indices=n, limit=float(max(WALK_M) + 3_500))[:n]
    return values, int((snap > SNAP_M).sum())


def population_access(graph, distances):
    _, _, active, tree, _ = graph
    result, plot = {}, None
    for name in ("worldpop-2026", "ghsl-2025"):
        source = MAPPING / f"{name}-source.json"
        pixels = MAPPING / f"{name}-pixels.npz.gz"
        metadata = read(source)
        if metadata["retained_sha256"] != digest(pixels):
            raise ValueError(f"{name} population cells changed")
        with np.load(BytesIO(gzip.decompress(pixels.read_bytes())), allow_pickle=False) as grid:
            valid = (grid["valid"] & np.isfinite(grid["counts"]) & (grid["counts"] >= 0)
                     & (grid["lon"] >= CORE[0]) & (grid["lat"] >= CORE[1])
                     & (grid["lon"] <= CORE[2]) & (grid["lat"] <= CORE[3]))
            population = grid["counts"][valid].astype(float)
            coords = np.column_stack((grid["lon"][valid], grid["lat"][valid]))
        snap, idx = tree.query(_points(coords))
        distances_by_case = {key: np.where(snap <= SNAP_M, distance[active[idx]] + snap, np.inf)
                             for key, distance in distances.items()}
        total = float(population.sum())
        result[name] = {"basis": metadata["dataset"], "year": metadata["year"],
                        "attribution": metadata["attribution"], "source_url": metadata["documentation"],
                        "population": round(total), "populated_pixels": int((population > 0).sum()),
                        "cells_beyond_snap_limit": int((snap > SNAP_M).sum()),
                        "access": {key: {metres: {"people": round(float(population[walk <= metres].sum())),
                                                "share_pct": round(float(population[walk <= metres].sum()) / total * 100, 2)}
                                          for metres in WALK_M} for key, walk in distances_by_case.items()}}
        if name == "worldpop-2026":
            plot = (coords, population, distances_by_case)
    return result, plot


def landmark_access(context, stops_by_case, graph, distances):
    landmarks = {DISTRICTS[feature["id"]]: {"name": DISTRICTS[feature["id"]],
                 "coordinates": feature["geometry"]["coordinates"], "context_place_id": feature["id"]}
                 for feature in context["layers"]["places"] if feature["id"] in DISTRICTS}
    if len(landmarks) != len(DISTRICTS):
        raise ValueError("A retained district reference has changed")
    # Imported identifiers retain the current public map reference for the
    # destination, separate from any proposed station position.
    for name, coordinates, url in (
        ("Mutanabbi Street", [44.38884167, 33.34095278], "https://www.wikidata.org/wiki/Q2562384"),
        ("Al-Shorja market", [44.3971, 33.339], "https://ijs.uobaghdad.edu.iq/index.php/eijs/article/download/11263/6254/135730"),
        ("Tahrir Square", [44.4083281, 33.3277667], "https://www.openstreetmap.org/node/7894353482"),
    ):
        landmarks[name] = {"name": name, "coordinates": coordinates, "source_url": url}
    _, _, active, tree, _ = graph
    for row in landmarks.values():
        location = _points([row["coordinates"]])[0]
        offset, idx = tree.query(location)
        cases = {}
        for key, stops in stops_by_case.items():
            direct, nearest = cKDTree(_points(list(stops.values()))).query(location)
            path = distances[key][active[idx]] + offset
            cases[key] = {"air_distance_m": round(float(direct)), "nearest_air_stop": list(stops)[nearest],
                          "walk_m": round(float(path)) if offset <= SNAP_M and np.isfinite(path) else None}
        row["cases"] = cases
    return sorted(landmarks.values(), key=lambda row: row["name"])


def evaluate():
    from . import central_service

    baseline, lines, stops, context = original_cases()
    case = central_service.evaluate()
    stops["central"] = {name: item["coordinates"] for name, item in case["stations"].items()}
    graph = walking_graph()
    computed = {name: distances_from_stops(points, graph) for name, points in stops.items()}
    distances = {name: item[0] for name, item in computed.items()}
    population, plot = population_access(graph, distances)
    landmarks = landmark_access(context, stops, graph, distances)
    features = lines + [
        {"type": "Feature", "geometry": {"type": "LineString", "coordinates": line["geometry"]},
         "properties": {"line": name, "status": "central study line", "station_ids": line["station_ids"]}}
        for name, line in case["lines"].items()]
    for name in ("clockface", "central"):
        features.extend({"type": "Feature", "properties": {"stop": stop, "status": name + " stop"},
                         "geometry": {"type": "Point", "coordinates": coordinates}}
                        for stop, coordinates in stops[name].items())
    features.extend({"type": "Feature", "properties": {"name": row["name"], "status": "destination",
                                                        "cases": row["cases"]},
                     "geometry": {"type": "Point", "coordinates": row["coordinates"]}} for row in landmarks)
    sources = (Path(__file__), *INPUTS, Path(central_service.__file__), Path(central_service_map.__file__),
               Path(walking_graph.__code__.co_filename),
               *(MAPPING / name for name in ("walking-graph.npz.gz", "walking-streets.geojson.gz", "street-source.json",
                                             "worldpop-2026-source.json", "worldpop-2026-pixels.npz.gz",
                                             "ghsl-2025-source.json", "ghsl-2025-pixels.npz.gz")))
    record = {"schema": "osr-baghdad-central-access/1", "baseline": baseline, "central_study": case,
              "core_bounds_wsen": CORE, "snap_limit_m": SNAP_M, "walking_thresholds_m": WALK_M,
              "walk_graph": graph[4], "stop_counts": {name: len(s) for name, s in stops.items()},
              "stops_beyond_snap_limit": {name: item[1] for name, item in computed.items()},
              "population": population, "landmark_access": landmarks,
              "sources": {path.relative_to(ROOT).as_posix(): digest(path) for path in sources}}
    record["evaluation_id"] = sha256(encode(record)).hexdigest()
    geojson = {"type": "FeatureCollection", "evaluation_id": record["evaluation_id"], "features": features}
    return record, geojson, plot, context


def map_image(geojson, plot, context):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon, Rectangle

    outlines = [f for f in geojson["features"] if f["geometry"]["type"] == "LineString"]
    markers = [f for f in geojson["features"] if f["geometry"]["type"] == "Point"]
    water = []
    for feature in context["layers"]["water"]:
        shape = feature["geometry"]
        if shape["type"] == "Polygon":
            water.append(shape["coordinates"][0])
        elif shape["type"] == "MultiPolygon":
            water.extend(poly[0] for poly in shape["coordinates"])
    coords, population, distances = plot
    fig, panels = plt.subplots(1, 3, figsize=(15.8, 7.3), layout="constrained",
                               gridspec_kw={"width_ratios": (1.05, 1, 1)})
    fig.patch.set_facecolor("#fcfaf4")
    fig.suptitle("Baghdad rail routes and station access", fontsize=21, color="#173d40", fontweight="bold")
    colors = {"clockface calls": "#446897", "deferred access": "#a83b4a",
              "reserved guideway": "#948c82", "central study line": "#106e62"}
    styles = {"clockface calls": "-", "deferred access": "--", "reserved guideway": ":",
              "central study line": "-"}
    trunk_colors = central_service_map.COLORS
    for panel, title, case in zip(panels, ("605 km costed concept", "Central area · 14-line trial",
                                         "Central area · two-trunk study"), (None, "clockface", "central"), strict=True):
        panel.set_facecolor("#f7f5ed")
        panel.set_title(title, color="#132c31", fontsize=13, loc="left", fontweight="bold", pad=10)
        panel.add_collection(PatchCollection([Polygon(ring, closed=True) for ring in water],
                                              facecolor="#c6e2e9", edgecolor="none", zorder=1))
        if case:
            reach = distances[case] <= WALK_M[0]
            for covered, color in ((False, "#c5bbb0"), (True, "#63b29b")):
                keep = (population >= 1) & (reach == covered)
                panel.scatter(*coords[keep].T, c=color, s=5, marker="s", linewidths=0,
                              alpha=.7, zorder=2, rasterized=True)
        for status, color in colors.items():
            if status == "central study line" and case != "central":
                continue
            if status != "central study line" and case == "central":
                continue
            selected = [f for f in outlines if f["properties"]["status"] == status]
            segments = [f["geometry"]["coordinates"] for f in selected]
            line_colors = ([trunk_colors[f["properties"]["line"]] for f in selected]
                           if status == "central study line" else color)
            panel.add_collection(LineCollection(segments, colors=line_colors, linewidths=2.4 if case else 1.35,
                                                  linestyles=styles[status], zorder=3))
        show = "central stop" if case == "central" else "clockface stop"
        points = [f["geometry"]["coordinates"] for f in markers if f["properties"]["status"] == show]
        panel.scatter(*zip(*points, strict=True), s=26 if case else 4.5, c="#fcfaf4",
                      edgecolors=colors["central study line" if case == "central" else "clockface calls"],
                      linewidths=.85, zorder=4)
        if case:
            destination = [f for f in markers if f["properties"]["status"] == "destination"
                           and f["properties"]["name"] in ("Mutanabbi Street", "Al-Shorja market", "Tahrir Square")]
            for feature in destination:
                lon, lat = feature["geometry"]["coordinates"]
                panel.scatter(lon, lat, marker="D", s=29, c="#e0a548", edgecolors="#775012",
                              linewidths=.6, zorder=5)
                offsets = {"Mutanabbi Street": (-6, 9, "right"), "Al-Shorja market": (7, 11, "left"),
                           "Tahrir Square": (6, -12, "left")}
                label = feature["properties"]["name"]
                dx, dy, ha = offsets[label]
                panel.annotate(label, (lon, lat), xytext=(dx, dy), textcoords="offset points",
                               ha=ha, fontsize=8, color="#4c3510", zorder=6,
                               bbox=dict(boxstyle="round,pad=.18", facecolor="#fffcf4", edgecolor="none", alpha=.93))
            panel.set(xlim=(CORE[0], CORE[2]), ylim=(CORE[1], CORE[3]))
        else:
            x, y = np.concatenate([np.asarray(f["geometry"]["coordinates"]) for f in outlines]).T
            panel.set(xlim=(x.min() - .014, x.max() + .014), ylim=(y.min() - .014, y.max() + .014))
            panel.add_patch(Rectangle((CORE[0], CORE[1]), CORE[2] - CORE[0], CORE[3] - CORE[1],
                                      fill=False, edgecolor="#6e4a26", linewidth=1.35, zorder=6))
        panel.set_aspect(1 / cos(radians(33.3)))
        panel.set_xticks([])
        panel.set_yticks([])
        for spine in panel.spines.values():
            spine.set_color("#d5cfc1")
    panels[0].legend(handles=[Line2D([0], [0], c=colors[key], ls=styles[key], label=key)
                              for key in ("clockface calls", "deferred access", "reserved guideway")],
                     loc="lower right", fontsize=8, facecolor="#fcfaf4")
    panels[1].legend(handles=[Line2D([0], [0], ls="None", marker="s", color=color, label=label)
                              for color, label in (("#63b29b", "Within 800 m walk"), ("#c5bbb0", "Outside 800 m walk"))],
                     loc="lower left", fontsize=8, facecolor="#fcfaf4")
    panels[2].legend(handles=[Line2D([0], [0], c=trunk_colors[key], marker="o", markerfacecolor="#fcfaf4",
                                      label=label) for key, label in (("C1", "C1 · Cross-river trunk"),
                                                                     ("C2", "C2 · East-bank trunk"))],
                     loc="lower left", fontsize=8, facecolor="#fcfaf4")
    fig.supxlabel("Water and walking streets © OpenStreetMap contributors · WorldPop 2026 population cells · station and route concepts",
                  fontsize=10, color="#46514c")
    target = BytesIO()
    fig.savefig(target, dpi=135, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    return target.getvalue()


def fmt_walk(metres):
    return f"{metres:,} m" if metres is not None else "Outside graph screen"


def map_pixels_match(first, second):
    """Allow a one-level antialiasing difference while checking rendered geometry."""
    from PIL import Image

    with Image.open(BytesIO(first)) as old, Image.open(BytesIO(second)) as rebuilt:
        if old.size != rebuilt.size:
            return False
        old_values = np.asarray(old.convert("RGBA"), dtype=np.int16)
        new_values = np.asarray(rebuilt.convert("RGBA"), dtype=np.int16)
    return bool((np.abs(old_values - new_values) <= 1).all())


def report(record):
    baseline = record["baseline"]
    local = record["central_study"]
    sites = record["landmark_access"]
    lines = [
        "# Central Baghdad passenger access review",
        "",
        f"The {baseline['physical_route_km']:.3f} km citywide concept is a comparison case. "
        f"Only {baseline['connected_clockface_km']:.3f} km enters the connected clockface trial. "
        "The citywide map combines operating paths, disconnected branches and guideway reserved for future use. "
        "The central access review tests actual station calls and introduces a separate two-trunk concept.",
        "",
        "![Baghdad guideway status and central walking access from active and proposed stops](maps/baghdad-central-access.png)",
        "",
        "## Which routes run end to end?",
        "",
        "| Scope | Result |",
        "|---|---|",
        f"| Original 14-group estimate | {baseline['original_diagrammed_km_year']/1e6:.2f}m connected and "
        f"{baseline['original_held_km_year']/1e6:.2f}m unresolved train-km per year |",
        f"| 14-route clockface trial | {baseline['connected_clockface_km']:.3f} km, "
        f"{baseline['clockface_headway_s']/60:g}-minute headway, {baseline['clockface_trips_day']:,} booked "
        f"trips/day and {baseline['clockface_sets']} working sets |",
        f"| Track still costed outside that timetable | {baseline['deferred_km']:.3f} km deferred access and "
        f"{baseline['reserved_km']:.3f} km reserved across 11 sections |",
        "",
        "Both Sadr City branches on M04 miss their main line by 2.323 km and 2.710 km. "
        "The two Jadriya branches on M01 and M02 attach mid-line. The M09 access spur leaves the loop. "
        "The clockface trial keeps M05 to the airport and leaves those five access sections outside passenger service.",
        "",
        "## How far is central Baghdad from a station?",
        "",
        "Compare street-graph walks to a scheduled stop within the same central study window. The model tests "
        "800 m and 1,200 m, allowing up to 100 m at each street connection. The population is estimated from "
        "native grid cells, counted once per case. These are residential access estimates. The station markers, "
        "street crossings, steps and entrance details still affect the actual journey.",
        "",
        "The fixed comparison window runs from 44.350° to 44.430° E and 33.293° to 33.365° N. "
        "It includes parts of Karkh, Rusafa and Karrada on both banks. "
        "[OpenStreetMap extract](https://download.geofabrik.de/asia/iraq.html) · "
        "[WorldPop](https://hub.worldpop.org/geodata/summary?id=73856) · "
        "[JRC GHS-POP](https://human-settlement.emergency.copernicus.eu/downloadWizard.php)",
        "",
        "| Population layer | People in study window | Original connected groups · ≤800 m | "
        "14-line clockface · ≤800 m / ≤1,200 m | Two central trunks · ≤800 m / ≤1,200 m |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, dataset in record["population"].items():
        access = dataset["access"]
        def span(name, thresholds):
            return " / ".join(f"{access[name][metres]['share_pct']:.1f}%" for metres in thresholds)
        label = "WorldPop" if key == "worldpop-2026" else "JRC GHS-POP"
        lines.append(f"| {dataset['year']} {label} | {dataset['population']:,} | "
                     f"{span('original', WALK_M[:1])} | {span('clockface', WALK_M)} | {span('central', WALK_M)} |")
    lines.extend(["", "| Central destination | Walk to 14-line trial | Walk to central concept |",
                  "|---|---:|---:|"])
    for row in sites:
        links = f" [{row['name']}]({row['source_url']})" if "source_url" in row else f" {row['name']}"
        old, central = row["cases"]["clockface"], row["cases"]["central"]
        lines.append(f"|{links} | {fmt_walk(old['walk_m'])} | {fmt_walk(central['walk_m'])} |")
    lines.extend([
        "",
        "## Test a central service before extending the network",
        "",
        f"The {local['route_km']:.2f} km concept uses {len(local['stations'])} distinct stops, "
        f"a {local['headway_s']/60:g}-minute headway and {local['diagrammed_trainsets']} working trainsets. "
        f"The fleet allowance is {local['trainsets_with_reserve']} sets. The two services have independent tracks "
        f"and share a passenger interchange at {local['stations'][local['interchange_station_id']]['name']}.",
        "",
        "The 10-minute trial failed the conservative shared Tahrir conflict check. The 15-minute scenario "
        "cleared the modelled timing constraints. The cross-river alignment assumes an independent elevated "
        "rail crossing near the Republic Bridge corridor.",
        "",
        "| Line | End-to-end station sequence | One-way km | Booked one-way min |",
        "|---|---|---:|---:|",
    ])
    for name, route in local["lines"].items():
        names = " → ".join(local["stations"][stop]["name"] for stop in route["station_ids"])
        lines.append(f"| {name} | {names} | {route['one_way_km']:.2f} | {route['run_s']/60:g} |")
    lines.extend([
        "",
        "Take the two trunks forward for comparison with central station infill and an improved bus network. "
        "Check each crossing and interchange on the ground and retain through routes only where train and passenger "
        "paths work together. Compare passenger access, waits and total cost before extending the suburban network. "
        "The older 605 km construction and operating rates belong to their original scope.",
        "",
        "[Full-size central route map](maps/baghdad-central-service.png) · "
        "[Central routes GIS](maps/central-service.geojson) · [Citywide service comparison](maps/Baghdad-606km.png)",
        "",
        "[Connected 14-route timetable](CITYWIDE-SERVICE.md) · [Comparison GIS layers](maps/central-access.geojson) · "
        "[Timetables, walking metrics and source record](central-access.json)",
        "",
        "Reproduce this issue with `./osr design railway central-access --check`.",
        "",
        f"Evaluation `{record['evaluation_id']}`.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true")
    action.add_argument("--publish", action="store_true")
    options = parser.parse_args()
    with disk_reservation(ROOT, ROOT, "Baghdad central access review", 32 << 20):
        record, geojson, plot, context = evaluate()
        if options.publish or options.check:
            central = central_service_map.geojson(record)
            outputs = {CITY / "CENTRAL-ACCESS.md": report(record).encode(),
                       CITY / "central-access.json": encode(record),
                       CITY / "maps/central-access.geojson": encode(geojson),
                       CITY / "maps/baghdad-central-access.png": map_image(geojson, plot, context),
                       CITY / "maps/central-service.geojson": encode(central),
                       CITY / "maps/baghdad-central-service.png": central_service_map.image(record, central, context),
                       CITY / "maps/Baghdad-606km.png": central_service_map.citywide_image(record, geojson, context)}
            for path, data in outputs.items():
                if options.publish:
                    write_atomic(path, data)
                else:
                    existing = path.read_bytes()
                    if existing != data and (path.suffix != ".png" or not map_pixels_match(existing, data)):
                        raise SystemExit(f"Central access publication differs at {path.name}")
        else:
            print(report(record))
        if options.publish or options.check:
            print(record["evaluation_id"])


if __name__ == "__main__":
    main()
