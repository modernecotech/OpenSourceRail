"""Named suburban access anchors, separate from proposed station locations."""


import numpy as np

from . import central_access as access, holistic_network as rail

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


def terminal_candidates(graph, context, *, maximum_m=700):
    """Offer alternative dry streets around each fixed destination anchor."""
    street_tree = graph[3]
    candidates = {}
    for name, location in locations().items():
        xy = np.asarray(location) * rail.LOCAL_METRES
        nearby = street_tree.data[street_tree.query_ball_point(xy, maximum_m)]
        order = sorted(nearby.tolist(), key=lambda row: (np.linalg.norm(xy - row), tuple(row)))
        selected = []
        for point, dry in zip(order, rail.dry_points(np.asarray(order) / rail.LOCAL_METRES, context), strict=True):
            if dry and all(np.linalg.norm(np.asarray(point) - other) >= 180 for other in selected):
                selected.append(np.asarray(point))
            if len(selected) == 4:
                break
        candidates[name] = selected
    return candidates


def walking(network, graph):
    sites = {stop: row["coordinates"] for stop, row in network["stations"].items()}
    distances, _ = access.distances_from_stops(sites, graph)
    result = {}
    for name, location in locations().items():
        offset, index = graph[3].query(np.asarray(location) * rail.LOCAL_METRES)
        path = distances[graph[2][index]] + offset
        result[name] = round(float(path), 1) if offset <= access.SNAP_M and np.isfinite(path) else None
    return result
