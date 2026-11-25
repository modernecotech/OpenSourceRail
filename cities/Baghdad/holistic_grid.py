"""Screen long Baghdad grid services between retained stations."""

from collections import defaultdict
from itertools import chain, pairwise

import numpy as np
from scipy.spatial import cKDTree

from .central_access import SNAP_M, read
from .holistic_network import LOCAL_METRES, MAJOR_ROADS, STREETS, Track, dry_points
from .holistic_through import (
    DEMAND_RADIUS_M, MAX_DUPLICATION_SHARE, MIN_MAJOR_ROAD_SHARE, RAIL_DUPLICATION_M,
    ROAD_CORRIDOR_M, STOP_SPACING_M, WaterGeometry, _candidate_crossings,
    _demand_points, _platforms, _street_layers, _water_screen,
)

MIN_LENGTH_M = 13_000
PREFERRED_LENGTH_M = 16_000
MAX_LENGTH_M = 32_000
MAX_BEARING_DEVIATION = 25
MAX_TURN_DEGREES = 35
MAX_DIRECTNESS_RATIO = 1.10
MAX_TRANSVERSE_BRIDGE_OFFSET_M = 3_300
MIN_INTERMEDIATE_TRANSFERS = 2
MAX_CANDIDATES = 52
MAX_TRIALS_PER_ZONE = 60
MAX_ACCEPTED_PER_ZONE = 10
ORIENTATIONS = ("east–west", "north–south")
# Published Baghdad through-route comparison at dc79af2bc4. The terminal
# identities refer to the same retained GIS stations on the 1.2 km infill case.
EXTENSION_SOURCE = "dc79af2bc42622f1a445ccc7b81c05ac5cec4c49"
EXTENSION_SEEDS = (
    ("T01", "C1-infill-31200", "M-172"),
    ("T02", "M09-infill-07800", "M11-infill-00900"),
    ("T05", "M-218", "M05-infill-23700"),
)
MAX_EXTENSION_TRIALS_PER_SEED = 100


def _pair_groups(points, line_sets, demand, weights):
    """Rank terminal pairs within each orientation and transverse strip."""
    pairs = cKDTree(points).query_pairs(MAX_LENGTH_M, output_type="ndarray")
    pairs = np.asarray(sorted((a, b) for a, b in pairs
                              if line_sets[a].isdisjoint(line_sets[b])), dtype=int).reshape((-1, 2))
    groups = defaultdict(list)
    for offset in range(0, len(pairs), 600):
        indexes = pairs[offset:offset + 600]
        start, end = points[indexes[:, 0]], points[indexes[:, 1]]
        deltas = end - start
        lengths = np.linalg.norm(deltas, axis=1)
        axes = np.argmax(np.abs(deltas), axis=1)
        valid = ((lengths >= MIN_LENGTH_M)
                 & (np.max(np.abs(deltas), axis=1) >= lengths * np.cos(np.deg2rad(MAX_BEARING_DEVIATION))))
        indexes, start, end, deltas, lengths, axes = (item[valid] for item in
                                                     (indexes, start, end, deltas, lengths, axes))
        direction = deltas / lengths[:, None]
        shifts = demand[None, :, :] - start[:, None, :]
        along = np.sum(shifts * direction[:, None, :], axis=2)
        lateral = np.abs(shifts[:, :, 0] * direction[:, None, 1] - shifts[:, :, 1] * direction[:, None, 0])
        contribution = np.where(
            (along >= STOP_SPACING_M) & (along <= lengths[:, None] - STOP_SPACING_M),
            np.maximum(1 - lateral / DEMAND_RADIUS_M, 0) * weights, 0,
        )
        for i in np.flatnonzero((contribution > 0).sum(axis=1) >= 2):
            axis, length = int(axes[i]), float(lengths[i])
            a, b = map(int, indexes[i][::1 if deltas[i, axis] > 0 else -1])
            centre = (start[i] + end[i]) / 2
            zone = (axis, int(centre[1 - axis] // 3700), int(centre[axis] // 9400))
            priority = float(contribution[i].sum()) * min(length / PREFERRED_LENGTH_M, 1.0)
            groups[zone].append((priority, a, b, length))
    return {zone: sorted(pairs, key=lambda row: (-row[0], row[1], row[2]))
            for zone, pairs in groups.items()}


def _bridge_reaches(context, water, bridges):
    """Keep dry-ended straight reaches corroborated by mapped bridge tags."""
    if "roads" not in context["layers"]:
        return []
    reaches = {}
    for feature in read(STREETS)["features"]:
        tags = feature["properties"]
        kind = (tags.get("highway") or "").removesuffix("_link")
        if (tags.get("bridge") != "yes" or tags.get("tunnel") not in (None, "no")
                or kind not in MAJOR_ROADS.keys() | {"residential", "unclassified", "service"}):
            continue
        start, end = np.asarray(feature["geometry"]["coordinates"])[[0, -1]] * LOCAL_METRES
        delta = end - start
        length = np.linalg.norm(delta)
        if not 24 <= length <= 1_100:
            continue
        centre = (start + end) / 2
        reach = max(length / 2 + 110, 240) * delta / length
        candidate = np.asarray([centre - reach, centre + reach])
        if not any(len(hits) for hits in water.intersections(*candidate)):
            continue
        if not dry_points(candidate / LOCAL_METRES, context).all():
            continue
        if not _water_screen(*candidate, context, water, bridges):
            continue
        # Adjacent one-way bridge decks often describe the same crossing.
        key = tuple(np.floor(centre / 120).astype(int))
        reaches.setdefault(key, candidate)
    return list(reaches.values())


def _bridge_paths(start, end, axis, reaches):
    straight = end - start
    length = np.linalg.norm(straight)
    direction = straight / length
    minimum_heading = np.cos(np.deg2rad(MAX_TURN_DEGREES))
    options = []
    for reach in reaches:
        centre = reach.mean(axis=0)
        along = np.dot(centre - start, direction)
        if not 1_400 <= along <= length - 1_400:
            continue
        lateral = np.linalg.norm(centre - start - along * direction)
        if lateral > MAX_TRANSVERSE_BRIDGE_OFFSET_M:
            continue
        ordered = reach if reach[1, axis] >= reach[0, axis] else reach[::-1]
        route = np.asarray([start, *ordered, end])
        deltas = np.diff(route, axis=0)
        lengths = np.linalg.norm(deltas, axis=1)
        if (np.any(lengths < 300) or lengths.sum() > MAX_LENGTH_M
                or lengths.sum() / length > MAX_DIRECTNESS_RATIO):
            continue
        headings = deltas / lengths[:, None]
        turns = np.sum(headings[:-1] * headings[1:], axis=1)
        if np.all(headings[:, axis] > 0) and np.all(turns >= minimum_heading):
            options.append((float(lengths.sum()), lateral, route))
    yield from (route for _, _, route in sorted(options, key=lambda row: row[:2])[:4])


def _extension_trials(first, last, points, line_sets, demand, weights):
    """Try modest bends to extend an earlier local alignment past both ends."""
    seed = points[[first, last]]
    direction = seed[1] - seed[0]
    axis = int(np.argmax(np.abs(direction)))
    if direction[axis] < 0:
        seed = seed[::-1]
        direction = -direction
    reach = np.linalg.norm(direction)
    direction /= reach
    before, after = (points - seed[0]) @ direction, (points - seed[1]) @ direction
    starts = np.flatnonzero((before < -STOP_SPACING_M) & (before > -13_000))
    ends = np.flatnonzero((after > STOP_SPACING_M) & (after < 13_000))
    minimum_heading = np.cos(np.deg2rad(MAX_TURN_DEGREES))
    options = []
    for a in starts:
        for b in ends:
            if not line_sets[a].isdisjoint(line_sets[b]):
                continue
            direct = points[b] - points[a]
            chord = float(np.linalg.norm(direct))
            if (not MIN_LENGTH_M <= chord <= MAX_LENGTH_M
                    or direct[axis] < chord * np.cos(np.deg2rad(MAX_BEARING_DEVIATION))):
                continue
            route = np.asarray([points[a], *seed, points[b]])
            deltas = np.diff(route, axis=0)
            lengths = np.linalg.norm(deltas, axis=1)
            if lengths.sum() > min(MAX_LENGTH_M, chord * MAX_DIRECTNESS_RATIO):
                continue
            heading = deltas / lengths[:, None]
            if np.any(heading[:, axis] <= 0) or np.any(heading[[0, 2]] @ direction < minimum_heading):
                continue
            shifts = demand[None, :, :] - route[:-1, None, :]
            along = np.clip(np.sum(shifts * heading[:, None, :], axis=2), 0, lengths[:, None])
            lateral = np.linalg.norm(shifts - along[:, :, None] * heading[:, None, :], axis=2)
            proxy = float((np.maximum(1 - lateral.min(axis=0) / DEMAND_RADIUS_M, 0) * weights).sum())
            score = proxy * min(chord / PREFERRED_LENGTH_M, 1.0)
            options.append(((score, int(a), int(b), chord), route))
    return axis, sorted(options, key=lambda row: (-row[0][0], row[0][1], row[0][2]))


def _screen_geometry(geometry, context, roads, bridges, water, rail):
    road_valid = rail_close = count = 0
    for start, end in pairwise(geometry):
        length = np.linalg.norm(end - start)
        samples = np.linspace(start, end, int(np.ceil(length / 125)) + 1)[1:-1]
        offsets = roads.nearby(samples, (end - start) / length, ROAD_CORRIDOR_M, 35)
        road_valid += int(np.isfinite(offsets).sum())
        rail_close += int((rail.query(samples)[0] <= RAIL_DUPLICATION_M).sum())
        count += len(samples)
    road_share, duplicate_share = road_valid / count, rail_close / count
    if road_share < MIN_MAJOR_ROAD_SHARE or duplicate_share > MAX_DUPLICATION_SHARE:
        return None

    chain_m = 0.0
    water_contacts = []
    for start, end in pairwise(geometry):
        # All path vertices were screened for dry land before this call.
        if any(len(hits) for hits in water.intersections(start, end)):
            crossings = _water_screen(start, end, context, water, bridges)
            if crossings is None:
                return None
            water_contacts.extend(
                {**row, "chainage_km": round(row["chainage_km"] + chain_m / 1000, 3)}
                for row in crossings
            )
        chain_m += float(np.linalg.norm(end - start))
    return road_share, duplicate_share, water_contacts


def _descriptor(terminals, track, geometry_type, trial, axis, network, tracks,
                stations, graph, context, screen):
    crossings = _candidate_crossings(track, tracks, network, graph, context)
    if len(crossings) < MIN_INTERMEDIATE_TRANSFERS:
        return None
    # Keep transfers distributed along the route.
    if crossings[-1][0] - crossings[0][0] < .20 * track.km:
        return None
    platforms = _platforms(track, crossings, stations, graph, context)
    if not platforms:
        return None
    proxy, _, _, length = trial
    vector = track.points[-1] - track.points[0]
    bearing = float(np.degrees(np.arctan2(vector[1], vector[0])) % 180)
    orientation = ORIENTATIONS[axis]
    names = [network["stations"][stop].get("name") or stop for stop in terminals]
    road_share, duplicate_share, water_contacts = screen
    return {
        "key": f"G-{terminals[0]}--{terminals[1]}-{geometry_type}",
        "name": "–".join(names),
        "geometry": track.coordinates.tolist(),
        "terminal_ids": terminals,
        "one_way_km": track.km,
        "directness": track.km * 1_000 / length,
        "basis": f"Preliminary {orientation} cross-city elevated planning alignment",
        "terminal_link_only": False,
        "stops": [
            {"name": f"New station · km {km:g}", "chainage_km": km, "coordinates": track.at(km),
             "street_offset_m": round(snap, 1),
             "basis": "Dry alignment position near a retained pedestrian graph node"}
            for km, snap in platforms
        ],
        "required_interchanges": [
            {"line_id": line, "point": list(point), "chainage_km": km}
            for km, line, point in crossings
        ],
        "screening": {
            "orientation": orientation,
            "axis_bearing_degrees": round(bearing, 2),
            "geometry_type": geometry_type,
            "distance_proxy_score": round(proxy, 2),
            "major_surface_road_share": round(road_share, 3),
            "major_surface_road_test": "125 m axis samples within 150 m and 35° of a mapped major road",
            "near_existing_rail_share": round(duplicate_share, 3),
            "mapped_water_contacts": water_contacts,
            "alignment_limits": "Survey, curve geometry, guideway and water crossing clearance, "
                                "land take, entrances and pedestrian accessibility require verification.",
        },
    }


def _screen_trial(trial, axis, points, ids, network, tracks, stations, graph,
                  context, roads, bridges, water, rail, reaches):
    _, a, b, _ = trial
    start, end = points[a], points[b]
    terminals = [ids[a], ids[b]]
    direct = [("straight", np.asarray([start, end]))]
    bridge_paths = (("bridge approach", path) for path in _bridge_paths(start, end, axis, reaches))
    paths = chain(direct, bridge_paths)
    for kind, geometry in paths:
        screen = _screen_geometry(geometry, context, roads, bridges, water, rail)
        if screen is None:
            continue
        coords = (geometry / LOCAL_METRES).tolist()
        coords[0], coords[-1] = (network["stations"][stop]["coordinates"] for stop in terminals)
        row = _descriptor(terminals, Track(coords), kind, trial, axis, network, tracks,
                          stations, graph, context, screen)
        if row is not None:
            return row
    return None


def generate(network, context, graph, coverage_cells=None):
    """Return a geographically distributed shortlist for exact access and trip scoring."""
    demand, weights = _demand_points(coverage_cells, graph)
    if len(demand) < 2 or len(network["stations"]) < 2:
        return []
    ids = sorted(network["stations"])
    coords = np.asarray([network["stations"][key]["coordinates"] for key in ids])
    points = coords * LOCAL_METRES
    stations = cKDTree(points)
    eligible = (graph[3].query(points)[0] <= SNAP_M) & dry_points(coords, context)
    ids = [key for key, keep in zip(ids, eligible, strict=True) if keep]
    points = points[eligible]
    line_sets = [set(network["stations"][key]["lines"]) for key in ids]
    groups = _pair_groups(points, line_sets, demand, weights)
    if not groups:
        return []

    tracks = {code: Track(line["geometry"]) for code, line in sorted(network["lines"].items())}
    rail = cKDTree(np.concatenate([
        np.asarray([track.at(x) for x in np.linspace(0, track.km, int(np.ceil(track.km * 12)) + 1)])
        * LOCAL_METRES for track in tracks.values()
    ]))
    roads, bridges = _street_layers(context)
    water = WaterGeometry.from_context(context)
    reaches = _bridge_reaches(context, water, bridges)
    eligible_rows = {}
    for zone, trials in sorted(groups.items(), key=lambda item: (-item[1][0][0], item[0])):
        accepted = []
        for trial in trials[:MAX_TRIALS_PER_ZONE]:
            _, a, b, length = trial
            # Suppress only near-identical corridors within each zone. Long
            # variants can reach different retained lines at their ends.
            if any(np.linalg.norm(points[a] - points[i]) < 1250 and np.linalg.norm(points[b] - points[j]) < 1250
                   and abs(length - previous) < 1800 for _, i, j, previous in accepted):
                continue
            row = _screen_trial(trial, zone[0], points, ids, network, tracks, stations, graph,
                                context, roads, bridges, water, rail, reaches)
            if row is None:
                continue
            eligible_rows.setdefault(zone, []).append(row)
            accepted.append(trial)
            if len(accepted) >= MAX_ACCEPTED_PER_ZONE:
                break
    extensions = defaultdict(list)
    id_index = {station: index for index, station in enumerate(ids)}
    for earlier, first, last in EXTENSION_SEEDS:
        if first not in id_index or last not in id_index:
            continue
        axis, options = _extension_trials(id_index[first], id_index[last], points, line_sets, demand, weights)
        for trial, geometry in options[:MAX_EXTENSION_TRIALS_PER_SEED]:
            _, a, b, _ = trial
            terminals = [ids[a], ids[b]]
            if any(row["terminal_ids"] == terminals for row in extensions[axis]):
                continue
            screen = _screen_geometry(geometry, context, roads, bridges, water, rail)
            if screen is None:
                continue
            alignment = [network["stations"][ids[a]]["coordinates"],
                         (geometry[1] / LOCAL_METRES).tolist(), (geometry[2] / LOCAL_METRES).tolist(),
                         network["stations"][ids[b]]["coordinates"]]
            row = _descriptor(terminals, Track(alignment), "local alignment extension", trial, axis,
                              network, tracks, stations, graph, context, screen)
            if row is None:
                continue
            row["screening"]["seed_basis"] = f"Maintains the earlier {earlier} central alignment"
            row["screening"]["seed_source_revision"] = EXTENSION_SOURCE
            extensions[axis].append(row)
            if sum(r["screening"]["seed_basis"] == row["screening"]["seed_basis"] for r in extensions[axis]) >= 3:
                break
    orientation_rows = []
    for axis, _ in enumerate(ORIENTATIONS):
        orientation_rows.append(extensions[axis] + [
            rows[i] for i in range(MAX_ACCEPTED_PER_ZONE) for zone, rows in eligible_rows.items()
            if zone[0] == axis and i < len(rows)
        ])
    # Share the shortlist between both headings. Round-robin within each
    # heading so high-demand strips do not exhaust the geography budget.
    pool = [rows[i] for i in range(max(map(len, orientation_rows))) for rows in orientation_rows if i < len(rows)]
    for i, row in enumerate(pool[:MAX_CANDIDATES], 1):
        code = f"G{i:02d}"
        row["id"] = code
        row["screening"]["demand_proxy_basis"] = ("Uncovered people in 1 km cells" if coverage_cells is not None
                                                  else "Density of mapped pedestrian street tiles")
        for j, stop in enumerate(row["stops"], 1):
            stop["id"] = f"{code}-S{j:02d}"
    return pool[:MAX_CANDIDATES]
