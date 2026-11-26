"""Bridge-first Baghdad through-route trials on the retained central rings."""

from copy import deepcopy
from itertools import combinations, pairwise
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from shapely import LineString, Polygon, intersects_xy

from engineering.outline.network_policy import MAXIMUM_DETOUR_RATIO, crossing_failures

from . import central_access, central_parallel_routes, holistic_access, holistic_grid, holistic_network, holistic_through
from . import rail_consolidation, rail_duplication, residential_layouts, ring_diameter_layout


RINGS = frozenset(ring_diameter_layout.RINGS)
MIN_ROUTE_KM = 13
MAX_ROUTE_KM = 38
MAX_TURN_DEG = 35
MAX_NEAR_RAIL_SHARE = .65
CORE_EDGE_TOLERANCE_M = 20
DISTINCT_BRIDGES_M = 700
ENDPOINT_TRIALS_PER_APPROACH = 22
MAX_SCREENED_PER_BRIDGE = 180
MAX_ADMITTED_PER_BRIDGE = 3
MAX_PAIR_TRIALS = 36


def _tigris(context):
    named = [row for row in context["layers"]["water"] if
             row["properties"].get("name:en") == "Tigris River"]
    return holistic_through.WaterGeometry.from_context({"layers": {"water": named}})


def _bridge_sites(context, water, bridges, inner):
    river = _tigris(context)
    sites = []
    for reach in holistic_grid._bridge_reaches(context, water, bridges):
        if not any(len(hits) for hits in river.intersections(*reach)):
            continue
        midpoint = reach.mean(axis=0)
        if inner.contains(LineString(reach)) and all(
                np.linalg.norm(midpoint - old.mean(axis=0)) >= 150 for old in sites):
            sites.append(reach)
    return sorted(sites, key=lambda row: tuple(row.mean(axis=0)))


def _endpoint_paths(reach, points, demand, weights, outside):
    delta = reach[1] - reach[0]
    heading = delta / np.linalg.norm(delta)
    min_cos = np.cos(np.deg2rad(MAX_TURN_DEG))
    sides = []
    for landing, direction in zip(reach, (-heading, heading), strict=True):
        vectors = points - landing
        length = np.linalg.norm(vectors, axis=1)
        valid = (length >= 2500) & (length <= 23000) & (vectors @ direction >= length * min_cos)
        indexes = np.flatnonzero(valid)
        axes = vectors[indexes] / length[indexes, None]
        shifts = demand - landing
        alongside = axes @ shifts.T
        lateral = np.linalg.norm(shifts[None, :, :] - alongside[:, :, None] * axes[:, None, :], axis=2)
        score = np.sum(np.where(
            (alongside >= 0) & (alongside <= length[indexes, None]),
            np.maximum(0, 1 - lateral / 1400) * weights, 0,
        ), axis=1)
        order = sorted(zip(indexes, score, strict=True),
                       key=lambda entry: (-outside[entry[0]].item(), -entry[1], entry[0]))
        sides.append(order[:ENDPOINT_TRIALS_PER_APPROACH])
    paths = []
    for a, first_score in sides[0]:
        for b, last_score in sides[1]:
            route = np.array([points[a], *reach, points[b]])
            length = np.linalg.norm(np.diff(route, axis=0), axis=1).sum()
            chord = np.linalg.norm(route[-1] - route[0])
            if MIN_ROUTE_KM * 1000 <= length <= min(MAX_ROUTE_KM * 1000, MAXIMUM_DETOUR_RATIO * chord):
                paths.append((a, b, route, length / chord, first_score + last_score))
    return sorted(paths, key=lambda row: (-int(outside[row[0]]) - int(outside[row[1]]), -row[4],
                                         row[3], row[0], row[1]))


def _describe(network, track, graph, context, tracks, station_tree):
    rings = holistic_through._candidate_crossings(track, {line: tracks[line] for line in sorted(RINGS)},
                                                  network, graph, context)
    if {line for _, line, _ in rings} != RINGS:
        return None
    crossings = list(rings)
    for km, line, point in holistic_through._candidate_crossings(
            track, {code: base for code, base in tracks.items() if code not in RINGS}, network, graph, context):
        if all(abs(km - old) >= holistic_through.STOP_SPACING_M / 1000 for old, _, _ in crossings):
            crossings.append((km, line, point))
    crossings.sort()
    platforms = holistic_through._platforms(track, crossings, station_tree, graph, context)
    return (crossings, platforms) if platforms else None


def _corridor(path, context, roads, bridges, water, rail):
    """Evaluate mapped water geometry and record road and near-rail shares."""
    contacts = []
    chain_m = road_count = rail_count = count = 0
    for start, end in pairwise(path):
        length = np.linalg.norm(end - start)
        if any(len(hits) for hits in water.intersections(start, end)):
            crossings = holistic_through._water_screen(start, end, context, water, bridges)
            if crossings is None:
                return None
            contacts.extend(row | {"chainage_km": round(float(row["chainage_km"] + chain_m / 1000), 3)}
                            for row in crossings)
        samples = np.linspace(start, end, int(np.ceil(length / 125)) + 1)[1:-1]
        offsets = roads.nearby(samples, (end - start) / length, holistic_through.ROAD_CORRIDOR_M, 35)
        road_count += int(np.isfinite(offsets).sum())
        rail_count += int((rail.query(samples)[0] <= holistic_through.RAIL_DUPLICATION_M).sum())
        count += len(samples)
        chain_m += length
    if not contacts or rail_count / count > MAX_NEAR_RAIL_SHARE:
        return None
    return road_count / count, rail_count / count, contacts


def _screen(network, graph, context, population):
    scale = holistic_network.LOCAL_METRES
    roads, bridges = holistic_through._street_layers(context)
    water = holistic_through.WaterGeometry.from_context(context)
    tracks = {code: holistic_network.Track(row["geometry"]) for code, row in network["lines"].items()}
    inner, outer = [Polygon(tracks[line].coordinates * scale) for line in ("M15", "M09")]
    sites = {code: row["coordinates"] for code, row in sorted(network["stations"].items())}
    coords = np.asarray(list(sites.values()))
    station_tree = cKDTree(coords * scale)
    dry_streets = ((graph[3].query(coords * scale)[0] <= central_access.SNAP_M)
                   & holistic_network.dry_points(coords, context))
    points = (coords * scale)[dry_streets]
    ids = np.asarray(list(sites))[dry_streets]
    outside = ~intersects_xy(outer, points[:, 0], points[:, 1])
    cells = None
    if population is not None:
        distances = holistic_access.walk_to_station(sites, graph, population)[0]
        cells = holistic_access.coverage_cells(population, distances)
    demand, weights = holistic_through._demand_points(cells, graph)
    rail = cKDTree(np.concatenate([
        np.array([track.at(km) for km in np.linspace(0, track.km, int(np.ceil(track.km * 12)) + 1)])
        * scale for track in tracks.values()
    ]))
    pool, audits = [], []
    for bridge_id, reach in enumerate(_bridge_sites(context, water, bridges, inner), 1):
        count = 0
        audit = {"approaches": (reach / scale).tolist(), "endpoint_trials": 0, "admitted_axes": 0, "mapped_corridor_pass": 0, "station_pass": 0, "disjoint": 0, "beyond_core": 0}
        audits.append(audit)
        paths = _endpoint_paths(reach, points, demand, weights, outside)
        for a, b, path, detour, score in paths[:MAX_SCREENED_PER_BRIDGE]:
            audit["endpoint_trials"] += 1
            terminals = [str(ids[a]), str(ids[b])]
            if set(network["stations"][terminals[0]]["lines"]) & set(network["stations"][terminals[1]]["lines"]):
                continue
            audit["disjoint"] += 1
            if any(inner.covers(LineString(segment)) for segment in ((path[0], path[1]), (path[2], path[3]))):
                continue
            audit["beyond_core"] += 1
            screen = _corridor(path, context, roads, bridges, water, rail)
            if screen is None:
                continue
            audit["mapped_corridor_pass"] += 1
            road_share, duplicate_share, water_contacts = screen
            if not water_contacts:
                continue
            coords = (path / scale).tolist()
            coords[0], coords[-1] = (sites[stop] for stop in terminals)
            track = holistic_network.Track(coords)
            description = _describe(network, track, graph, context, tracks, station_tree)
            if description is None:
                continue
            audit["station_pass"] += 1
            crossings, platforms = description
            count += 1
            audit["admitted_axes"] += 1
            code = f"ST{bridge_id:02d}-{count:02d}"
            pool.append({
                "id": code, "name": f"Cross-city through service {code}", "geometry": coords,
                "basis": "Elevated planning centreline via mapped Tigris road-bridge approaches. "
                         "Dedicated river crossing structure, clearance, alignment curves and land require design.",
                "terminal_ids": terminals, "one_way_km": track.km,
                "required_interchanges": [{"line_id": line, "point": list(point)} for _, line, point in crossings],
                "stops": [{"id": f"{code}-S{i:02d}", "name": f"{code} · km {km:g}", "chainage_km": km}
                          for i, (km, _) in enumerate(platforms, 1)],
                "detour_ratio": round(float(detour), 4),
                "demand_proxy_score": round(float(score), 2),
                "mapped_bridge_approaches": (reach / scale).tolist(),
                "bridge_id": bridge_id,
                "water_crossings": water_contacts,
                "tigris_crossing_count": 1,
                "major_road_share": round(road_share, 4),
                "near_existing_rail_share": round(duplicate_share, 4),
                "terminals_outside_outer_ring": int(outside[a]) + int(outside[b]),
            })
            if count == MAX_ADMITTED_PER_BRIDGE:
                break
    return pool, audits


def _retained_axes(network, context):
    """Check existing routes against the same directness, water and ring obligations."""
    scale = holistic_network.LOCAL_METRES
    water = holistic_through.WaterGeometry.from_context(context)
    river = _tigris(context)
    _, bridges = holistic_through._street_layers(context)
    outer = Polygon(np.asarray(network["lines"]["M09"]["geometry"]) * scale)
    inner = _core_polygon(network)
    axes = []
    for code, line in sorted(network["lines"].items()):
        if line["loop"] or not _enters_ring(line, inner) or not (MIN_ROUTE_KM <= line["one_way_km"] <= MAX_ROUTE_KM):
            continue
        stops = set(line["station_ids"])
        if not all(stops & set(network["lines"][ring]["station_ids"]) for ring in RINGS):
            continue
        path = np.asarray(line["geometry"]) * scale
        detour = line["one_way_km"] * 1000 / np.linalg.norm(path[-1] - path[0])
        if detour > MAXIMUM_DETOUR_RATIO:
            continue
        central_water, water_crossings = [], []
        chain_m = 0.
        for a, b in pairwise(path):
            length = np.linalg.norm(b - a)
            if any(len(hits) for hits in water.intersections(a, b)):
                contacts = holistic_through._water_screen(a, b, context, water, bridges)
                if contacts is None:
                    break
                on_river = bool(len(river.intersections(a, b)[1]))
                for row in contacts:
                    chainage = row["chainage_km"]
                    water_crossings.append(row | {"chainage_km": round(float(chain_m / 1000 + chainage), 3)})
                    if on_river and row["mapped_wet_width_m"] > 30:
                        centre = a + (b - a) * chainage * 1000 / length
                        reach = row["mapped_wet_width_m"] / 2 + 60
                        approach = reach * (b - a) / length
                        central_water.append((centre, ((centre - approach) / scale).tolist(),
                                              ((centre + approach) / scale).tolist()))
            chain_m += length
        else:
            if central_water:
                _, before, after = central_water[0]
                axes.append({"id": code, "terminal_ids": [line["station_ids"][0], line["station_ids"][-1]],
                             "detour_ratio": round(float(detour), 4), "water_crossings": water_crossings,
                             "tigris_crossing_count": len(central_water),
                             "mapped_bridge_approaches": [before, after],
                             "terminals_outside_outer_ring": int(sum(
                                 not intersects_xy(outer, *point) for point in path[[0, -1]])),
                             "major_road_share": None, "near_existing_rail_share": None})
    return axes


def _through_certificate(network, axis):
    code = axis["id"]
    line = network["lines"][code]
    stops = set(line["station_ids"])
    ring_interchanges = {ring: sorted(stops & set(network["lines"][ring]["station_ids"]))
                         for ring in sorted(RINGS)}
    failures = crossing_failures(detour_ratio=axis["detour_ratio"], maximum_detour_ratio=MAXIMUM_DETOUR_RATIO,
                                 water_required=True, water_crossings=axis["tigris_crossing_count"],
                                 required_ring_ids=RINGS, ring_interchanges=ring_interchanges)
    if failures:
        raise ValueError(f"{code}: {', '.join(failures)}")
    return {key: axis[key] for key in (
        "id", "terminal_ids", "detour_ratio", "water_crossings", "tigris_crossing_count", "mapped_bridge_approaches",
        "terminals_outside_outer_ring", "major_road_share", "near_existing_rail_share",
    )} | {"route_km": line["one_way_km"], "ring_interchanges": ring_interchanges}


def _core_polygon(network):
    scale = holistic_network.LOCAL_METRES
    return Polygon(np.asarray(network["lines"]["M15"]["geometry"]) * scale).buffer(-CORE_EDGE_TOLERANCE_M)


def _enters_ring(line, polygon):
    points = np.asarray(line["geometry"]) * holistic_network.LOCAL_METRES
    return LineString(points).relate_pattern(polygon, "T********")


def _core_turnbacks(network, axes, protected):
    """Test keeping outer arms at inner-ring interchanges and all station sites."""
    fixed = RINGS | {"C1"} | {row["id"] for row in axes}
    inner = _core_polygon(network)
    candidates = [code for code, line in sorted(network["lines"].items())
                  if code not in fixed and _enters_ring(line, inner)]
    revised = network
    actions, holds = [], {}
    for code in candidates:
        line = revised["lines"][code]
        ids = line["station_ids"]
        ring = [stop for stop in ids if "M15" in revised["stations"][stop]["lines"]]
        if not ring:
            holds[code] = "No shared inner-ring station for an outer turnback."
            continue
        edits = []
        reason = "Turn the outer branch at its existing shared inner-ring station."
        if ring[0] != ids[0]:
            edits.append((code, residential_layouts.LineEdit(code, reason, end_station=ring[0])))
        if ring[-1] != ids[-1]:
            branch = code if not edits else f"{code}-outer"
            edits.append((branch, residential_layouts.LineEdit(code, reason, start_station=ring[-1])))
        if not edits or any(branch != code and branch in revised["lines"] for branch, _ in edits):
            holds[code] = "Unable to form distinct outer branches at existing rail interchanges."
            continue
        trial = deepcopy(revised)
        del trial["lines"][code]
        try:
            for branch, edit in edits:
                trial["lines"][branch], _ = residential_layouts._clip(line, edit, revised["stations"])
            if any(_enters_ring(trial["lines"][branch], inner) for branch, _ in edits):
                raise ValueError("One retained arm still enters the core.")
            residential_layouts._rebuild_memberships(trial)
            lost = revised["stations"].keys() - trial["stations"].keys()
            if lost:
                raise ValueError(f"{len(lost)} station sites would lose passenger service.")
            if not protected <= trial["stations"].keys():
                raise ValueError("A protected Airport or destination station would close.")
            trial["topology"] = holistic_network.validate(trial)
        except ValueError as error:
            holds[code] = str(error)
            continue
        actions.append({
            "action": "ring_turnback", "line_id": code, "reason": reason,
            "terminals": [edit.start_station or edit.end_station for _, edit in edits],
            "retained_branch_ids": [branch for branch, _ in edits],
            "removed_route_km": round(line["one_way_km"] - sum(
                trial["lines"][branch]["one_way_km"] for branch, _ in edits), 3),
            "closed_stations": [],
        })
        revised = trial
    return revised, actions, holds


def _hierarchy(network, certificates, holds):
    primary = {row["id"] for row in certificates}
    legacy_mains = sorted(code for code, line in network["lines"].items()
                          if code not in primary | RINGS | {"C1"} and line["one_way_km"] >= MIN_ROUTE_KM)
    feeders = sorted(network["lines"].keys() - primary - RINGS - {"C1"} - set(legacy_mains))
    inner = _core_polygon(network)
    exceptions = [{"line_id": code, "reason": holds.get(code, (
                      "The dedicated airport corridor is retained to preserve airport-to-city access."
                      if code == "C1" else "Existing city-centre corridor retained in the coverage comparison."
                  ))}
                  for code, line in sorted(network["lines"].items())
                  if code not in primary | RINGS and _enters_ring(line, inner)]
    return {
        "core_exceptions": exceptions,
        "primary_through": {"line_ids": sorted(primary),
                            "reason": "Passed the mapped Tigris approach, directness and shared ring station screens."},
        "rings": {"line_ids": sorted(RINGS), "reason": "Retained central and metropolitan orbital distribution."},
        "airport": {"line_ids": ["C1"], "reason": "Retained dedicated Airport–Zayouna access corridor."},
        "retained_corridors": {"line_ids": legacy_mains,
                               "reason": "Longer existing corridors retained for access and system connectivity. "
                                         "Their full alignments did not enter the new bridge-first trial."},
        "local_connectors": {"line_ids": feeders,
                             "reason": "Shorter retained links and branches feed nearby orbital and through services."},
    }


def _record(parent, network, axes, actions, audits, rejected, *, name, holds=None):
    certificates = [_through_certificate(network, axis) for axis in axes]
    hierarchy = _hierarchy(network, certificates, holds or {})
    network = deepcopy(network)
    network["straight_through_layout"] = {"parent_candidate_id": parent["candidate_id"],
                                          "certified_through": certificates,
                                          "hierarchy": hierarchy,
                                          "actions": actions}
    for relative_source in (__file__, holistic_grid.__file__, holistic_through.__file__, rail_duplication.__file__,
                            residential_layouts.__file__, central_parallel_routes.__file__,
                            "engineering/outline/network_policy.py"):
        source = (central_access.ROOT / relative_source).resolve()
        network.setdefault("source_sha256", {})[source.relative_to(central_access.ROOT).as_posix()] = (
            central_access.digest(source))
    revised = holistic_network._identity(rail_consolidation.refresh_interchange_names(network))
    return {"network": revised, "name": name, "certified_through": certificates,
            "hierarchy": hierarchy, "actions": actions, "bridge_trials": audits,
            "rejected_pairs": rejected, "rejection_reason": None}


def _trim_overlap(network, axes, protected):
    """Test a protected-site-preserving terminal cut within measured overlap."""
    new_codes = {row["id"] for row in axes}
    fixed = RINGS | {"C1"} | new_codes
    pairs = [(new, old) for new in sorted(new_codes) for old in sorted(network["lines"].keys() - fixed)]
    runs = rail_duplication.screen(network["lines"], pair_filter=pairs, nearby_m=450, min_run_m=1200)["runs"]
    cuts = []
    for run in runs:
        code, partner = sorted(run["lines"], key=lambda line: line in new_codes)
        line = network["lines"][code]
        ids = line["station_ids"]
        low, high = run["chainage_m"][code]
        for stop in ids[1:-1]:
            if partner not in network["stations"][stop]["lines"]:
                continue
            for first, last in ((ids[0], stop), (stop, ids[-1])):
                a, b = (line["station_chainage_km"][item] * 1000 for item in (first, last))
                overlap = max(0, min(high, b) - max(low, a))
                if overlap < 1200 or overlap < (b - a) * .70:
                    continue
                if first == ids[0]:
                    continue  # The current project trim helper retains a prefix.
                cuts.append((-overlap, {"line_id": code, "parallel": partner, "from": first, "to": last,
                                        "terminals": [stop],
                                        "reason": f"Turn {code} at {partner} to remove the screened overlapping tail."}))
    for _, cut in sorted(cuts, key=lambda row: (row[0], row[1]["line_id"], row[1]["from"])):
        try:
            path, actions = central_parallel_routes._apply(network, [cut], protected, runs)
        except ValueError:
            continue
        return path, actions
    return None, []


def _distinct_crossings(first, last):
    delta = np.mean(first["mapped_bridge_approaches"], axis=0) - np.mean(last["mapped_bridge_approaches"], axis=0)
    return np.linalg.norm(delta * holistic_network.LOCAL_METRES) >= DISTINCT_BRIDGES_M


def alternatives(network, graph, context, *, population, protected_stations):
    """Generate planning layouts with distinct, physically linked Tigris axes."""
    holistic_network.validate(network)
    for ring in RINGS:
        if not network["lines"].get(ring, {}).get("loop"):
            raise ValueError("The bridge-first study requires the retained closed central and metropolitan rings")
    existing = _retained_axes(network, context)
    axes, audits = _screen(network, graph, context, population)
    pairs = [(a, b) for a, b in combinations(axes, 2) if _distinct_crossings(a, b)]
    pairs.sort(key=lambda pair: (-sum(row["terminals_outside_outer_ring"] for row in pair),
                                 sum(row["near_existing_rail_share"] * row["one_way_km"] for row in pair),
                                 -sum(row["demand_proxy_score"] for row in pair),
                                 tuple(row["id"] for row in pair)))
    rejected = []
    result = {}
    hybrids = [(old, new) for old in existing for new in axes if _distinct_crossings(old, new)]
    hybrids.sort(key=lambda pair: (-pair[1]["terminals_outside_outer_ring"],
                                  pair[1]["one_way_km"] * pair[1]["near_existing_rail_share"],
                                  -pair[1]["demand_proxy_score"], pair[0]["id"], pair[1]["id"]))
    hybrid_holds = []
    for old, new in hybrids[:MAX_PAIR_TRIALS]:
        try:
            hybrid = holistic_network.insert_through_lines(network, [new], graph=graph, context=context)
        except ValueError as error:
            hybrid_holds.append({"lines": [old["id"], new["id"]], "reason": str(error)})
            continue
        actions = [{"action": "add_through", "line_id": new["id"], "route_km": new["one_way_km"]}]
        result["hybrid-through-pair"] = _record(network, hybrid, (old, new), actions, audits, hybrid_holds,
                                               name="New Tigris service and retained cross-city axis")
        break
    for a, b in combinations(existing, 2):
        if not _distinct_crossings(a, b):
            continue
        result["retained-through-pair"] = _record(
            network, network, (a, b), [], audits, [], name="Retained Tigris services with both-ring interchanges")
        turned, actions, held = _core_turnbacks(network, (a, b), set(protected_stations))
        if actions:
            result["retained-through-pair-turnbacks"] = _record(
                network, turned, (a, b), actions, audits, [], name="Retained Tigris services with inner-ring turnbacks",
                holds=held)
        else:
            result["retained-through-pair-turnbacks"] = {
                "network": None, "name": "Retained Tigris services with inner-ring turnbacks", "actions": [],
                "certified_through": [], "hierarchy": _hierarchy(
                    network, [_through_certificate(network, axis) for axis in (a, b)], held),
                "rejection_reason": "The tested turnbacks would remove station coverage or lack a usable interchange.",
            }
        break
    for pair in pairs[:MAX_PAIR_TRIALS]:
        codes = [axis["id"] for axis in pair]
        try:
            revised = holistic_network.insert_through_lines(network, pair, graph=graph, context=context,
                                                            connect_through_lines=True)
            if not set(protected_stations) <= revised["stations"].keys():
                raise ValueError("A protected Airport or destination station would be removed")
        except ValueError as error:
            rejected.append({"lines": codes, "reason": str(error)})
            continue
        actions = [{"action": "add_through", "line_id": axis["id"], "route_km": axis["one_way_km"]}
                   for axis in pair]
        result["bridge-first-pair"] = _record(network, revised, pair, actions, audits, rejected,
                                             name="Two Tigris through services with retained coverage")
        trimmed, trims = _trim_overlap(revised, pair, set(protected_stations))
        if trimmed is not None:
            result["bridge-first-pair-trimmed"] = _record(network, trimmed, pair, [*actions, *trims], audits,
                                                         rejected, name="Two Tigris through services with overlap trim")
        turned, turnbacks, held = _core_turnbacks(revised, pair, set(protected_stations))
        if turnbacks:
            result["bridge-first-pair-turnbacks"] = _record(
                network, turned, pair, [*actions, *turnbacks], audits, rejected,
                name="Two Tigris through services with inner-ring turnbacks", holds=held)
        else:
            result["bridge-first-pair-turnbacks"] = {
                "network": None, "name": "Inner-ring turnbacks", "actions": [],
                "certified_through": [], "hierarchy": _hierarchy(revised, [_through_certificate(revised, axis) for axis in pair], held),
                "rejection_reason": "The retained inner-ring turnbacks would remove station coverage "
                                    "or lack a usable shared railway interchange.",
            }
        break
    if "bridge-first-pair" not in result:
        result["bridge-first-pair"] = {"network": None, "name": "Two Tigris through services",
                                       "bridge_trials": audits, "rejected_pairs": rejected, "actions": [],
                                       "certified_through": [], "hierarchy": {},
                                       "rejection_reason": "No connected pair passed the bounded approach and station trials."}
    return result
