"""Road-snapped routing for a city design.

Given a `design.toml` and an OSM road extract, route each line's
consecutive station pairs along real streets (weighted shortest path
favouring trunk/primary/secondary over residential). The output is a
`corridor.geojson` LineString per line suitable for embedding in
maps + consuming by `osr-alignment` as the horizontal-alignment
source for a surveyed track layout.

Overpass pulls are cached under `out_dir/.cache/` so re-running with
the same bbox doesn't re-hit the API.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# `networkx` is a heavier dep than the rest of `osr_scenario`, so we
# import it inside the functions that need it. This keeps `import
# osr_scenario` cheap for the read-only paths (scenario generation,
# stats, map rendering that doesn't route).


OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"

# Highway-class → routing-weight multiplier. Lower = more preferred.
# Urban rail RoW can only realistically be laid on arterials, never
# on residential grid streets (would require demolition + narrow-
# width track that doesn't exist). Residential + unclassified edges
# are EXCLUDED from the routing graph entirely — see
# `_ARTERIAL_CLASSES`. The weight table applies to the included
# classes only.
_HIGHWAY_WEIGHT = {
    "trunk":     0.5,
    "primary":   0.6,
    "secondary": 0.8,
    "tertiary":  1.1,
}

# Only these classes participate in the routing graph. Anything else
# (residential, service, unclassified, living_street, ...) is dropped
# so the shortest-path cannot zigzag through a residential grid.
_ARTERIAL_CLASSES = frozenset({"trunk", "primary", "secondary", "tertiary"})


@dataclass(frozen=True)
class BBox:
    south: float
    west: float
    north: float
    east: float

    @classmethod
    def from_design(cls, design: dict) -> "BBox":
        bb = design.get("location", {}).get("bbox")
        if bb:
            return cls(bb["south"], bb["west"], bb["north"], bb["east"])
        # Synthesize from station extents + 1 km padding.
        stations = design.get("stations", [])
        if not stations:
            raise ValueError("design has no bbox and no stations")
        las = [s["lat"] for s in stations]
        los = [s["lon"] for s in stations]
        return cls(min(las) - 0.015, min(los) - 0.015,
                   max(las) + 0.015, max(los) + 0.015)


def _haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    dla, dlo = la2 - la1, lo2 - lo1
    h = math.sin(dla / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlo / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def fetch_roads(bbox: BBox, cache_dir: Path) -> dict:
    """Fetch all routable highways inside `bbox` from Overpass. Cached
    by bbox hash so repeated calls are offline."""
    import requests

    key = hashlib.sha256(
        f"{bbox.south},{bbox.west},{bbox.north},{bbox.east}".encode()
    ).hexdigest()[:16]
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"roads-{key}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    q = f"""
    [out:json][timeout:180];
    (
      way["highway"~"^(trunk|primary|secondary|tertiary)$"]
          ({bbox.south},{bbox.west},{bbox.north},{bbox.east});
    );
    (._;>;);
    out body;
    """
    r = requests.post(
        OVERPASS_ENDPOINT,
        data=q,
        headers={"User-Agent": "OpenSourceRail-design/0.2"},
        timeout=240,
    )
    r.raise_for_status()
    data = r.json()
    cache_path.write_text(json.dumps(data))
    return data


def build_road_graph(osm_data: dict):
    """Return `(G, nodes)` where `G` is a `networkx.Graph` and
    `nodes` maps node-id → (lat, lon)."""
    import networkx as nx

    nodes = {
        e["id"]: (e["lat"], e["lon"]) for e in osm_data["elements"] if e["type"] == "node"
    }
    G = nx.Graph()
    for w in osm_data["elements"]:
        if w["type"] != "way":
            continue
        hw = (w.get("tags") or {}).get("highway", "")
        if hw not in _ARTERIAL_CLASSES:
            continue  # residential / service / unclassified dropped
        mult = _HIGHWAY_WEIGHT[hw]
        ns = w.get("nodes", [])
        for a, b in zip(ns, ns[1:]):
            if a in nodes and b in nodes:
                d = _haversine_m(nodes[a], nodes[b])
                if G.has_edge(a, b):
                    # Keep the cheaper of the two parallel roads.
                    if d * mult < G[a][b]["weight"]:
                        G[a][b]["weight"] = d * mult
                        G[a][b]["length_m"] = d
                else:
                    G.add_edge(a, b, weight=d * mult, length_m=d)
    return G, nodes


def _nearest_node(nodes: dict, lat: float, lon: float, candidates=None) -> int:
    """Brute-force nearest-neighbour among graph nodes."""
    best = None
    bd = float("inf")
    pool = candidates if candidates is not None else nodes.keys()
    for n in pool:
        p = nodes[n]
        d = (p[0] - lat) ** 2 + (p[1] - lon) ** 2
        if d < bd:
            bd, best = d, n
    return best


def route_lines(design: dict, cache_dir: Path) -> dict[str, list[dict]]:
    """For every line in `design`, return a list of segment dicts:

        { "from": station_id, "to": station_id,
          "coords": [(lon, lat), ...],   # road-snapped polyline
          "length_m": float }

    Road graph is fetched from Overpass (cached) and edge-weighted to
    favour bigger roads."""
    import networkx as nx

    bbox = BBox.from_design(design)
    osm = fetch_roads(bbox, cache_dir)
    G, nodes = build_road_graph(osm)
    largest_cc = max(nx.connected_components(G), key=len)
    cc_nodes = set(largest_cc)

    station_to_node: dict[str, int] = {}
    for s in design.get("stations", []):
        station_to_node[s["id"]] = _nearest_node(
            nodes, s["lat"], s["lon"], candidates=cc_nodes
        )

    routes: dict[str, list[dict]] = {}
    for line in design.get("lines", []):
        segs: list[dict] = []
        ids = [s["id"] for s in line.get("stations", [])]
        station_coords = {
            s["id"]: (s["lat"], s["lon"])
            for s in design.get("stations", [])
        }
        # If the planner committed a `track_polyline`, emit one
        # segment per station-pair by slicing the polyline between
        # the closest polyline vertices to each station. This
        # preserves the planner's route and avoids shortest-path
        # recomputation that can detour kilometres off-line.
        track = line.get("track_polyline")
        if track and len(track) >= 2:
            poly = [(lat, lon) for lat, lon in track]
            station_to_poly_idx: dict[str, int] = {}
            for sid in ids:
                if sid not in station_coords:
                    continue
                slat, slon = station_coords[sid]
                best_i, best_d = 0, float("inf")
                for i, (plat, plon) in enumerate(poly):
                    d = (plat - slat) ** 2 + (plon - slon) ** 2
                    if d < best_d:
                        best_d, best_i = d, i
                station_to_poly_idx[sid] = best_i
            for a, b in zip(ids, ids[1:]):
                ia = station_to_poly_idx.get(a, 0)
                ib = station_to_poly_idx.get(b, len(poly) - 1)
                lo, hi = (ia, ib) if ia <= ib else (ib, ia)
                sub = poly[lo: hi + 1]
                if ia > ib:
                    sub = list(reversed(sub))
                length = 0.0
                for u, v in zip(sub, sub[1:]):
                    length += _haversine_m(u, v)
                coords = [(lon, lat) for lat, lon in sub]
                segs.append({
                    "from": a, "to": b, "coords": coords, "length_m": length,
                })
            routes[line["id"]] = segs
            continue

        for a, b in zip(ids, ids[1:]):
            na, nb = station_to_node[a], station_to_node[b]
            try:
                path = nx.shortest_path(G, na, nb, weight="weight")
                coords = [(nodes[n][1], nodes[n][0]) for n in path]
                coords = _smooth_polyline(coords, max_heading_deg=15.0)
                length = sum(G[u][v]["length_m"] for u, v in zip(path, path[1:]))
            except nx.NetworkXNoPath:
                coords = [(nodes[na][1], nodes[na][0]), (nodes[nb][1], nodes[nb][0])]
                length = _haversine_m(nodes[na], nodes[nb])
            segs.append({
                "from": a, "to": b, "coords": coords, "length_m": length,
            })
        routes[line["id"]] = segs
    return routes


def _smooth_polyline(
    coords: list[tuple[float, float]],
    *, max_heading_deg: float = 15.0,
) -> list[tuple[float, float]]:
    """Remove intermediate vertices where the heading change from
    the previous segment is less than `max_heading_deg`. Preserves
    endpoints and significant corners."""
    if len(coords) < 3:
        return coords
    import math

    out = [coords[0]]
    for i in range(1, len(coords) - 1):
        prev = out[-1]
        cur = coords[i]
        nxt = coords[i + 1]
        h1 = math.atan2(cur[1] - prev[1], cur[0] - prev[0])
        h2 = math.atan2(nxt[1] - cur[1], nxt[0] - cur[0])
        d = abs((h2 - h1 + math.pi) % (2 * math.pi) - math.pi)
        if math.degrees(d) >= max_heading_deg:
            out.append(cur)
    out.append(coords[-1])
    return out


def routes_to_geojson(
    design: dict, routes: dict[str, list[dict]]
) -> dict:
    """Package routes + stations as a single GeoJSON FeatureCollection."""
    features = []
    for line in design.get("lines", []):
        if line["id"] not in routes:
            continue
        # Stitch segments into one MultiLineString per line.
        mls_coords = [seg["coords"] for seg in routes[line["id"]]]
        total_m = sum(seg["length_m"] for seg in routes[line["id"]])
        features.append({
            "type": "Feature",
            "properties": {
                "id": line["id"],
                "name": line.get("name", line["id"]),
                "length_m": round(total_m, 1),
                "feature_kind": "line",
            },
            "geometry": {
                "type": "MultiLineString",
                "coordinates": mls_coords,
            },
        })
    for s in design.get("stations", []):
        features.append({
            "type": "Feature",
            "properties": {
                "id": s["id"],
                "name": s.get("name"),
                "archetype": s.get("archetype"),
                "feature_kind": "station",
            },
            "geometry": {"type": "Point", "coordinates": [s["lon"], s["lat"]]},
        })
    return {"type": "FeatureCollection", "features": features}


def coverage_audit(
    design: dict,
    anchors: list[tuple[str, str, tuple[float, float]]],
    threshold_m: float = 1_000.0,
) -> list[tuple[float, str, float, float]]:
    """Return the list of (distance_m, name, lat, lon) for every
    `(neighbourhood|suburb)` anchor whose nearest station is more than
    `threshold_m` away. Sorted by distance (largest first)."""
    out: list[tuple[float, str, float, float]] = []
    stations = design.get("stations", [])
    for kind, name, (la, lo) in anchors:
        if kind not in ("neighbourhood", "suburb"):
            continue
        best = min(
            _haversine_m((la, lo), (s["lat"], s["lon"])) for s in stations
        )
        if best > threshold_m:
            out.append((best, name, la, lo))
    out.sort(reverse=True)
    return out


__all__ = [
    "BBox",
    "build_road_graph",
    "coverage_audit",
    "fetch_roads",
    "route_lines",
    "routes_to_geojson",
]
