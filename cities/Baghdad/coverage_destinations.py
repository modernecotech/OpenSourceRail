"""Named suburban access anchors, separate from proposed station locations."""


import numpy as np
from shapely import distance, intersects_xy, points

from . import central_access as access, holistic_network as rail
from .coverage_orbitals import WALK_M

REFERENCE_GIS = access.CITY / "maps/baghdad-straight-through-network.geojson"
ANCHORS = {
    # Centre of the residential development, east of the old M02 approach.
    "Basmaya": (44.62071, 33.19302),
    "Nahrawan": "M-089",
    "Tajiyat": "M04-infill-08700",
}


def locations():
    points = {row["properties"]["station_id"]: row["geometry"]["coordinates"]
              for row in access.read(REFERENCE_GIS)["features"]
              if "station_id" in row["properties"] and row["geometry"]["type"] == "Point"}
    return {name: list(points[anchor] if isinstance(anchor, str) else anchor) for name, anchor in ANCHORS.items()}


def terminal_candidates(graph, context, *, outer_ring=None, departure_offset_m=None):
    """Offer dry street sites with verified walks, including alternatives beyond the contour."""
    if (outer_ring is None) != (departure_offset_m is None):
        raise ValueError("The outer ring and departure offset must be provided together")
    street_tree = graph[3]
    candidates = {}
    for name, location in locations().items():
        xy = np.asarray(location) * rail.LOCAL_METRES
        nearby = np.asarray(street_tree.query_ball_point(xy, 700), dtype=np.intp)
        if not nearby.size:
            candidates[name] = []
            continue
        distances, _ = access.distances_from_stops({name: location}, graph)
        walked = distances[graph[2][nearby]]
        nearby = nearby[walked <= WALK_M]
        order = np.asarray(sorted(street_tree.data[nearby].tolist(),
                                  key=lambda row: (np.linalg.norm(xy - row), tuple(row))))
        if not order.size:
            candidates[name] = []
            continue
        legal = rail.dry_points(order / rail.LOCAL_METRES, context)
        if outer_ring is not None:
            legal &= ~intersects_xy(outer_ring, *order.T)
        order = order[legal]
        selected = _spaced(order, 4)
        if (outer_ring is not None and order.size
                and not (distance(outer_ring, points(np.asarray(selected))) > departure_offset_m).any()):
            exterior = order[distance(outer_ring, points(order)) > departure_offset_m]
            selected.extend(_spaced(exterior, 3))
        candidates[name] = selected
    return candidates


def _spaced(points, count):
    selected = []
    for point in points:
        if all(np.linalg.norm(point - other) >= 180 for other in selected):
            selected.append(point)
        if len(selected) == count:
            break
    return selected


def walking(network, graph):
    sites = {stop: row["coordinates"] for stop, row in network["stations"].items()}
    distances, _ = access.distances_from_stops(sites, graph)
    result = {}
    for name, location in locations().items():
        offset, index = graph[3].query(np.asarray(location) * rail.LOCAL_METRES)
        path = distances[graph[2][index]] + offset
        result[name] = round(float(path), 1) if offset <= access.SNAP_M and np.isfinite(path) else None
    return result
