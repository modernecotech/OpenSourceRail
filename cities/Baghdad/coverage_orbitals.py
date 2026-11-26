"""Fit nested Baghdad orbitals to central destinations and separate residential catchments."""

from itertools import product

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree
from shapely.geometry import MultiPoint, Polygon

from . import central_access, holistic_access, holistic_network


RING_IDS = ("M15", "M09", "M16")
WALK_M = 1300
MIN_RING_SEPARATION_M = 650
MIN_RING_STOP_SEPARATION_M = 1300
MIDDLE_OUTER_MEDIAN_TARGET_M = 2500
CONTROL_ANGLES = np.linspace(0, 2 * np.pi, 32, endpoint=False)
BEARINGS = np.column_stack((np.cos(CONTROL_ANGLES), np.sin(CONTROL_ANGLES)))
LOCAL_METRES = holistic_network.LOCAL_METRES

# Radial envelopes and radial preference weights are search settings. Their
# distance origin is the centroid of mapped central places.
# They constrain the search domain but do not dictate the radius by bearing.
MIDDLE_PROFILES_KM = ((5.5, 11.5, 7.5), (6.5, 13.5, 9.5), (6.0, 13.0, 8.25))
OUTER_PROFILES_KM = ((11.0, 21.0, 14.5), (12.5, 24.0, 17.5), (13.0, 25.0, 19.5), (10.0, 20.0, 12.5))


def central_destinations(context):
    west, south, east, north = central_access.CORE
    points = {}
    for feature in context["layers"]["places"]:
        geometry = feature["geometry"]
        if geometry["type"] != "Point":
            continue
        lon, lat = geometry["coordinates"]
        if (feature["id"] not in central_access.DISTRICTS
                and not (feature["properties"].get("kind_detail") == "quarter"
                         and west <= lon <= east and south <= lat <= north)):
            continue
        points[feature["id"]] = (lon, lat)
    if not central_access.DISTRICTS.keys() <= points.keys():
        raise ValueError("Mapped central Baghdad district geography is incomplete")
    return points


def _population_weights(points, population, capacity_m, *, radial_band=None, centre=None):
    """Use tapering straight-line reach for search. Check the finalist sites on streets."""
    eligible = population.offsets_m <= central_access.SNAP_M
    if radial_band is not None:
        distance = np.linalg.norm(population.xy - centre, axis=1)
        low, high = radial_band
        eligible &= (low <= distance) & (distance <= high)
    coordinates, counts = population.xy[eligible], population.counts[eligible]
    tree = cKDTree(coordinates)
    weights = np.zeros(len(points))
    for index, nearby in enumerate(tree.query_ball_point(points, capacity_m)):
        reach = np.linalg.norm(coordinates[nearby] - points[index], axis=1) / capacity_m
        weights[index] = counts[nearby] @ (1 - reach**2)
    return weights


def _smooth_profile(rewards, radii):
    """Solve the whole closed cycle, including the seam, with stable ties."""
    count, candidates = rewards.shape
    changes = np.abs(radii[:, None] - radii[None, :])
    # Discourage tight bends and long radial steps while allowing a ring to
    # follow separate neighborhoods over several angular controls.
    movement = np.where(changes <= 1500, .23 * (changes / 1000)**2, np.inf)
    solutions = []
    for first in range(candidates):
        values = np.full(candidates, -np.inf)
        values[first] = rewards[0, first]
        parents = []
        for reward in rewards[1:]:
            paths = values[:, None] - movement
            parent = paths.argmax(axis=0)
            parents.append(parent)
            values = reward + paths[parent, np.arange(candidates)]
        finish = values - movement[:, first]
        last = int(finish.argmax())
        trace = [last]
        for parent in reversed(parents):
            trace.append(int(parent[trace[-1]]))
        if len(trace) != count or trace[-1] != first:
            raise RuntimeError("Orbital dynamic-programming path did not close")
        solutions.append((float(finish[last]), tuple(reversed(trace))))
    _, path = max(solutions, key=lambda row: (row[0], tuple(-index for index in row[1])))
    return radii[list(path)]


def _fit_residential(centre, envelope, population, graph):
    low, high, preferred = np.asarray(envelope) * 1000
    radii = np.arange(low, high + 1, 500.)
    points = centre + BEARINGS[:, None, :] * radii[None, :, None]
    flattened = points.reshape(-1, 2)
    # Wide kernels capture residential axes even when the angular controls
    # are several km apart. Candidate stops use the smaller walk kernel.
    reward = _population_weights(flattened, population, 2000.,
                                 radial_band=(low - 600, high + 600), centre=centre)
    scale = max(float(np.percentile(reward, 80)), 1.)
    street_offset, _ = graph[3].query(flattened)
    reward = np.log1p(reward.reshape(points.shape[:2]) / scale)
    reward -= .022 * ((radii - preferred)[None, :] / 1000)**2
    reward -= .13 * np.minimum(street_offset.reshape(points.shape[:2]) / 500, 1)
    controls = _smooth_profile(reward, radii)
    spline = CubicSpline(np.r_[CONTROL_ANGLES, 2 * np.pi], np.r_[controls, controls[0]],
                         bc_type="periodic")
    angles = np.linspace(0, 2 * np.pi, 321)
    coordinates = centre + spline(angles)[:, None] * np.column_stack((np.cos(angles), np.sin(angles)))
    coordinates[-1] = coordinates[0]
    polygon = Polygon(coordinates)
    if not polygon.is_valid:
        raise ValueError("Radial orbital fit produced invalid geometry")
    return polygon


def _arc_clearance(polygon, *, sample_m=100, arc_m=1800, clearance_m=850):
    boundary = polygon.exterior
    chainages = np.arange(0., boundary.length, sample_m)
    coordinates = np.asarray([boundary.interpolate(km).coords[0] for km in chainages])
    pairs = cKDTree(coordinates).query_pairs(clearance_m, output_type="ndarray")
    gaps = np.diff(chainages[pairs], axis=1).ravel()
    close = (gaps >= arc_m) & (gaps <= boundary.length - arc_m)
    return {"sample_m": sample_m, "nonlocal_arc_m": arc_m, "clearance_m": clearance_m,
            "close_sample_pairs": int(np.count_nonzero(close))}


def ring_stations(polygon, graph, context, population, *, pitch_m=1900):
    """Find dry, walk-network-linked test stops spaced by chainage."""
    boundary = polygon.exterior
    count = max(3, round(boundary.length / pitch_m))
    step = boundary.length / count
    # Limiting local adjustments keeps sites separated even across the seam.
    if step < MIN_RING_STOP_SEPARATION_M:
        raise ValueError("Orbital is too short for three separated stations")
    adjustment = min((step - MIN_RING_STOP_SEPARATION_M) / 2, 400.)
    offsets = np.linspace(-adjustment, adjustment, 9)
    candidates = (np.arange(count)[:, None] * step + offsets) % boundary.length
    xy = np.asarray([boundary.interpolate(chainage).coords[0] for chainage in candidates.ravel()])
    legal = holistic_network.dry_points(xy / LOCAL_METRES, context)
    street_offset, _ = graph[3].query(xy)
    legal &= street_offset <= central_access.SNAP_M
    weights = _population_weights(xy, population, WALK_M)
    weights[~legal] = -np.inf
    weights = weights.reshape(candidates.shape)
    choice = weights.argmax(axis=1)
    return [xy[index * len(offsets) + option] / LOCAL_METRES
            for index, option in enumerate(choice) if np.isfinite(weights[index, option])]


def _separation(first, second):
    sample = np.arange(0., first.length, 250.)
    dist = np.asarray([second.distance(first.interpolate(metres)) for metres in sample])
    return {label: round(float(value), 1) for label, value in
            zip(("minimum_m", "p10_m", "median_m", "p90_m", "maximum_m"),
                np.percentile(dist, (0, 10, 50, 90, 100)), strict=True)}


def _walk_scope(polygon, graph, context, population):
    stations = ring_stations(polygon, graph, context, population)
    if len(stations) < 3:
        raise ValueError("Orbital geometry lacks three dry test stations linked to streets")
    walks, unmatched = holistic_access.walk_to_station(dict(enumerate(stations)), graph, population)
    if unmatched:
        raise ValueError("Orbital test sites do not match retained walking streets")
    return walks <= WALK_M, [station.tolist() for station in stations]


def fit_orbitals(graph, context, population):
    """Return deterministic nested alternatives plus reconciled street-walk evidence."""
    destinations = central_destinations(context)
    hull = MultiPoint(np.asarray(list(destinations.values())) * LOCAL_METRES).convex_hull
    centre = np.asarray(hull.centroid.coords[0])
    inner = hull.buffer(650., quad_segs=16)
    # The convex central envelope cannot contain the landward turn-back
    # seen on the previous Karkh orbital. Retain a sampled clearance check.
    inner_clearance = _arc_clearance(inner)
    if inner_clearance["close_sample_pairs"]:
        raise ValueError("Central orbital has nearby nonlocal reaches")
    middle = [_fit_residential(centre, profile, population, graph) for profile in MIDDLE_PROFILES_KM]
    outer = [_fit_residential(centre, profile, population, graph) for profile in OUTER_PROFILES_KM]
    inner_scope = _walk_scope(inner, graph, context, population)
    east, north = (population.xy - centre).T >= 0
    quadrants = {"northeast": north & east, "northwest": north & ~east,
                 "southeast": ~north & east, "southwest": ~north & ~east}
    alternatives = []
    middle_scopes, outer_scopes = {}, {}
    for number, outer_number in product(range(len(middle)), range(len(outer))):
        mid, out = middle[number], outer[outer_number]
        if not (mid.contains(inner.buffer(MIN_RING_SEPARATION_M))
                and out.contains(mid.buffer(MIN_RING_SEPARATION_M))):
            continue
        if number not in middle_scopes:
            middle_scopes[number] = _walk_scope(mid, graph, context, population)
        if outer_number not in outer_scopes:
            outer_scopes[outer_number] = _walk_scope(out, graph, context, population)
        scopes = (inner_scope, middle_scopes[number], outer_scopes[outer_number])
        masks = np.stack([mask for mask, _ in scopes])
        unique = masks.sum(axis=0) == 1
        coverage = masks.any(axis=0)
        polygons = dict(zip(RING_IDS, (inner, mid, out), strict=True))
        outer_gap = _separation(mid.exterior, out.exterior)
        audit = {
            "central_place_ids": sorted(destinations),
            "central_convex_hull": True,
            "inner_nonlocal_clearance": inner_clearance,
            "middle_profile_km": MIDDLE_PROFILES_KM[number],
            "outer_profile_km": OUTER_PROFILES_KM[outer_number],
            "inner_middle_separation": _separation(inner.exterior, mid.exterior),
            "middle_outer_separation": outer_gap,
            "middle_outer_median_planning_target_m": MIDDLE_OUTER_MEDIAN_TARGET_M,
            "middle_outer_median_target_difference_m": round(outer_gap["median_m"] - MIDDLE_OUTER_MEDIAN_TARGET_M, 1),
            "walk_limit_m": WALK_M,
            "residents_within_street_walk": round(float(population.counts[coverage].sum()), 2),
            "ring_walk_population": {key: round(float(population.counts[mask].sum()), 2)
                                     for key, mask in zip(RING_IDS, masks, strict=True)},
            "unique_ring_walk_population": {key: round(float(population.counts[unique & mask].sum()), 2)
                                             for key, mask in zip(RING_IDS, masks, strict=True)},
            "unique_middle_population_by_quadrant": {
                quadrant: round(float(population.counts[unique & masks[1] & sector].sum()), 2)
                for quadrant, sector in quadrants.items()
            },
            "test_stop_counts": {key: len(sites) for key, (_, sites) in
                                 zip(RING_IDS, scopes, strict=True)},
        }
        alternatives.append({"id": f"population-orbitals-m{number + 1}-o{outer_number + 1}",
                             "polygons": polygons, "audit": audit,
                             "test_stations": dict(zip(RING_IDS, (sites for _, sites in scopes), strict=True))})
    if not alternatives:
        raise ValueError("No independently fitted orbital profiles satisfy nested clearances")
    return sorted(alternatives, key=lambda row: (-row["audit"]["residents_within_street_walk"], row["id"]))
