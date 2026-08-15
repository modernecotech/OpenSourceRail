"""Render the network-map PNG for a city design.toml.

Consumes the same design.toml the scenario generator does, so as soon
as coordinates / lines / stations change in the design, regenerating
the maps is one command. No hand-edits to the image metadata, no
copied station lists.

Usage:
    python -m osr_scenario.render_map \\
        --design designs/west-asia/Iraq/Samawah/design.toml \\
        --out-dir docs/screenshots/

If called without `--design`, defaults to Samawah.
"""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path


# Line-colour palette — cycles by index so additional lines get
# distinct colours automatically. Chosen for high contrast on
# OpenStreetMap's beige / pale-gray tile background, where the
# tile itself already renders motorways in pink/orange and rivers
# in light-blue. Each hue is saturated and ≥ 30 % darker than
# the tile roads so they read clearly on top.
_LINE_COLORS = [
    "#0033cc",  # deep blue      L1
    "#cc0000",  # strong red     L2
    "#006600",  # forest green   L3
    "#663399",  # royal purple   L4
    "#ff6600",  # vivid orange   L5
    "#009999",  # dark teal      L6
    "#cc0099",  # magenta-pink   L7
    "#666600",  # olive-dark     L8
    "#000099",  # navy           L9 (rare — cycle wraps)
    "#990000",  # maroon         L10
]

_ARCH_COLOR = {
    "terminal":              "#d0382b",
    "depot-terminal":        "#8a2a62",
    "major":                 "#2b6fd0",
    "interchange":           "#e8a63a",
    # Auto-gen planner emits a junction variant when the crossing was
    # forced to elevation (one line lifted ±1 km around the interchange).
    # Distinct purple so it reads differently from the amber at-grade one.
    "interchange-elevated":  "#7a3fb8",
    # Brighter halt — original #3f9b5b vanished against thick black
    # ring lines on the full-network zoom.
    "halt":                  "#21c267",
    "standard":              "#ffffff",
}


def render_city(
    design_path: Path,
    out_dir: Path,
    *,
    route_on_roads: bool = True,
    cache_dir: Path | None = None,
) -> list[Path]:
    """Render the city + detail maps.

    Default: route along the OSM **arterial** graph between adjacent
    stations — residential / unclassified streets are excluded from
    the graph (see `osr_scenario.routing._ARTERIAL_CLASSES`) so the
    rendered line traces real trunk / primary / secondary / tertiary
    roads and cannot zigzag through a residential grid. A
    `corridor.geojson` is emitted alongside the PNGs.

    With `route_on_roads=False`, draws straight segments between
    stations — useful for debugging the raw station layout.
    """
    from staticmap import StaticMap, CircleMarker, Line

    doc = tomllib.loads(design_path.read_text())
    by_id = {s["id"]: s for s in doc["stations"]}
    lines = doc["lines"]
    interchanges = list(doc.get("interchanges", []))
    if not interchanges:
        # Compatibility for designs generated before interchange complexes
        # became explicit. Newly generated designs are required to carry the
        # records and the repository validator rejects omissions.
        grouped: dict[int, list[dict]] = {}
        for station in doc.get("stations", []):
            if station.get("junction_group") is not None:
                grouped.setdefault(int(station["junction_group"]), []).append(station)
        interchanges = [
            {
                "id": f"interchange-{group:03d}",
                "junction_group": group,
                "lat": sum(float(member["lat"]) for member in members) / len(members),
                "lon": sum(float(member["lon"]) for member in members) / len(members),
            }
            for group, members in sorted(grouped.items())
            if len({str(member["line"]) for member in members}) >= 2
        ]
    # Lowercase the city component for filename stability. Hand-authored
    # designs carry `[design].id = "west-asia/Iraq/Samawah"`; auto-gen
    # designs carry `[city].slug = "samawah"`. Fall through both.
    slug = (
        doc.get("design", {}).get("id")
        or doc.get("city", {}).get("slug")
        or "city"
    ).rsplit("/", 1)[-1].lower()

    # Auto-gen pipeline emits per-line geometry into a sidecar
    # `{slug}.corridor.geojson` instead of `track_polyline` inside
    # the TOML. Pick that up so we can render lines straight from
    # the planner output without round-tripping through routing.py.
    sidecar_geoms = _load_sidecar_geoms(design_path, slug)

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    # Try to compute road-snapped routes (+ save the GeoJSON artefact).
    # Skip when the planner already produced a sidecar — its geometry
    # is the authoritative one (includes parallel-track offsets for
    # shared trunks, anti-loop penalty masks, etc.) and shouldn't be
    # second-guessed by a re-snap pass.
    routes: dict | None = None
    if route_on_roads and not sidecar_geoms:
        try:
            from .routing import route_lines, routes_to_geojson

            # OSM cache sits at `docs/screenshots/.cache/osm/` (shared
            # across cities). out_dir used to be the one-folder-for-all
            # `docs/screenshots/`, so `out_dir.parent / ".cache"` found
            # it. Now that out_dir is the design folder, we search up
            # for the repo root instead.
            cdir = cache_dir or _find_osm_cache(out_dir)
            routes = route_lines(doc, cdir)
            geojson = routes_to_geojson(doc, routes)
            corridor_path = out_dir / f"{slug}-corridor.geojson"
            corridor_path.write_text(json.dumps(geojson))
            print(f"wrote {corridor_path}  ({corridor_path.stat().st_size // 1024} KB)")
            written.append(corridor_path)
        except Exception as e:
            print(f"warning: road routing failed, falling back to straight segments: {e}")
            routes = None

    # One map per city: the full network at auto-fit zoom, sized large
    # enough that every suburban terminus is visible at readable scale.
    # Earlier we shipped a separate detail PNG for the central core; the
    # 2400×2000 single render reads that fine on its own and avoids
    # having two near-duplicate images in each city folder.
    net_south, net_west, net_north, net_east = _network_bbox(doc, sidecar_geoms)
    img_w, img_h = 2400, 2000
    full_zoom = _fit_zoom(
        net_south, net_west, net_north, net_east,
        img_w=img_w, img_h=img_h,
    )
    full_zoom = max(6, min(17, full_zoom))

    renders: list[tuple[str, int, tuple[int, int], tuple[float, float] | None, float | None]] = [
        ("network-map.png", full_zoom, (img_w, img_h), None, None),
    ]
    for (suffix, zoom, wh, center_filter, radius_km) in renders:
        m = StaticMap(
            *wh,
            url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            tile_request_timeout=10,
        )
        import math as _math

        def _in_range(lat: float, lon: float) -> bool:
            if center_filter is None or radius_km is None:
                return True
            # Fast equirect distance approximation (fine at mid-latitudes).
            dlat = (lat - center_filter[0]) * 111.0
            dlon = (
                (lon - center_filter[1])
                * 111.0 * _math.cos(_math.radians(center_filter[0]))
            )
            return (dlat * dlat + dlon * dlon) <= radius_km * radius_km

        def _line_in_range(coords: list[tuple[float, float]]) -> bool:
            # Keep the segment if any vertex falls inside the detail
            # circle. Lines passing through the core still render
            # their approach even when their termini are well outside.
            return any(_in_range(lat, lon) for lon, lat in coords) \
                if center_filter is not None else True

        # Draw lines. Priority: (a) `track_polyline` committed by
        # the planner into design.toml is the authoritative geometry
        # — drawing it avoids renderer-side shortest-path detours
        # between consecutive stations. (b) routed shortest-paths
        # between station pairs. (c) straight segments as a last
        # resort.
        line_stroke = 7 if zoom <= 13 else 10
        # Ring line rendering: distinct bold black with a white
        # halo, +4 px thicker than radials, so it stands out from
        # the multi-coloured radial fan and is visually obvious as
        # the "goes around, not through the hub" topology.
        ring_stroke = line_stroke + 4
        ring_color = "#000000"
        ring_halo = "#ffffff"

        def _draw_line(line_key: str, is_ring: bool, coords: list, color: str) -> None:
            if is_ring:
                # White halo first (draws under), then black ring on top.
                m.add_line(Line(coords, ring_halo, ring_stroke + 4))
                m.add_line(Line(coords, ring_color, ring_stroke))
            else:
                m.add_line(Line(coords, color, line_stroke))

        for idx, line in enumerate(lines):
            color = _LINE_COLORS[idx % len(_LINE_COLORS)]
            # Auto-gen lines key on `name`; hand-authored use `id`.
            line_key = line.get("id") or line.get("name") or f"line-{idx}"
            # Ring detection: hand-authored uses the literal `line-ring`
            # id; auto-gen marks the topology shape per-line.
            is_ring = (line_key == "line-ring") or (line.get("shape") == "ring")
            track = line.get("track_polyline")
            if track and len(track) >= 2:
                coords = [(p[1], p[0]) for p in track]  # (lon, lat)
                if _line_in_range(coords):
                    _draw_line(line_key, is_ring, coords, color)
            elif sidecar_geoms.get(line_key):
                for seg in sidecar_geoms[line_key]:
                    if len(seg) >= 2 and _line_in_range(seg):
                        _draw_line(line_key, is_ring, seg, color)
            elif routes is not None and line_key in routes:
                for seg in routes[line_key]:
                    if _line_in_range(seg["coords"]):
                        _draw_line(line_key, is_ring, seg["coords"], color)
            else:
                coords = [
                    (by_id[s["id"]]["lon"], by_id[s["id"]]["lat"])
                    for s in line.get("stations", [])
                ]
                if len(coords) >= 2 and _line_in_range(coords):
                    _draw_line(line_key, is_ring, coords, color)
        # Draw ordinary stations individually, but render each transfer group
        # once at its explicit interchange-complex centroid. Per-line platform
        # records remain in design.toml for routing and simulation.
        big = zoom >= 13
        for s in doc.get("stations", []):
            if s.get("junction_group") is not None:
                continue
            if not _in_range(float(s["lat"]), float(s["lon"])):
                continue
            arch = s.get("archetype", "standard")
            # Junction-group membership is the transfer role, including when
            # the physical product is still a standard terminal/depot shell.
            outer = "#7a3fb8" if s.get("junction_group") is not None else _ARCH_COLOR.get(arch, "#3f9b5b")
            if arch in ("terminal", "depot-terminal"):
                outer_r = 30 if big else 22
                inner_r = 12 if big else 9
            else:
                outer_r = 22 if big else 16
                inner_r = 9 if big else 7
            # 3-layer marker: black outline (largest) → archetype colour
            # → white centre. The black outline is what makes halt /
            # standard markers visible on top of the heavy black ring
            # line stroke, where a colour-only marker disappears into
            # the line's halo.
            m.add_marker(CircleMarker((s["lon"], s["lat"]), "#000000", outer_r + 3))
            m.add_marker(CircleMarker((s["lon"], s["lat"]), outer, outer_r))
            m.add_marker(CircleMarker((s["lon"], s["lat"]), "#ffffff", inner_r))
        for interchange in interchanges:
            if not _in_range(float(interchange["lat"]), float(interchange["lon"])):
                continue
            point = (float(interchange["lon"]), float(interchange["lat"]))
            outer_r = 32 if big else 24
            inner_r = 12 if big else 9
            m.add_marker(CircleMarker(point, "#000000", outer_r + 4))
            m.add_marker(CircleMarker(point, "#7a3fb8", outer_r))
            m.add_marker(CircleMarker(point, "#ffffff", inner_r))
        img = m.render(zoom=zoom)
        out = out_dir / f"{slug}-{suffix}"
        img.save(out)
        print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
        written.append(out)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="osr_scenario.render_map",
        description="Render OSM-backed network maps from a design.toml.",
    )
    ap.add_argument("--design", type=Path, default=None)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="output directory (default: docs/screenshots/)",
    )
    args = ap.parse_args(argv)

    repo_root = _find_repo_root()
    if args.design is None:
        args.design = repo_root / "designs/west-asia/Iraq/Samawah/design.toml"
    if args.out_dir is None:
        # Write map artefacts alongside the design file — each city's
        # outputs live in one folder. `docs/screenshots/` is reserved
        # for general UI screenshots (sim-gui.png, occ-gui.png, etc.).
        args.out_dir = args.design.resolve().parent

    render_city(args.design, args.out_dir)
    return 0


def _find_repo_root() -> Path:
    cur = Path(__file__).resolve()
    for parent in cur.parents:
        if (parent / "Cargo.toml").exists():
            return parent
    return Path.cwd()


def _network_bbox(
    doc: dict,
    sidecar_geoms: dict[str, list[list[tuple[float, float]]]] | None = None,
) -> tuple[float, float, float, float]:
    """Return (south, west, north, east) covering every station
    coord and every polyline vertex in the design — used to pick a
    zoom that fits the whole network in the rendered image."""
    lats: list[float] = []
    lons: list[float] = []
    for s in doc.get("stations", []):
        lats.append(float(s["lat"]))
        lons.append(float(s["lon"]))
    for L in doc.get("lines", []):
        for lat, lon in L.get("track_polyline", ()) or ():
            lats.append(float(lat))
            lons.append(float(lon))
    if sidecar_geoms:
        for segs in sidecar_geoms.values():
            for seg in segs:
                for lon, lat in seg:
                    lats.append(float(lat))
                    lons.append(float(lon))
    if not lats:
        # Fallback to the design's input bbox.
        bb = (
            doc.get("location", {}).get("bbox")
            or doc.get("city", {}).get("bbox", {})
        )
        return (
            float(bb.get("south", 0.0)),
            float(bb.get("west", 0.0)),
            float(bb.get("north", 0.0)),
            float(bb.get("east", 0.0)),
        )
    # Tiny padding (0.005° ≈ 500 m) so markers aren't clipped at the edges.
    return (
        min(lats) - 0.005,
        min(lons) - 0.005,
        max(lats) + 0.005,
        max(lons) + 0.005,
    )


def _fit_zoom(
    south: float, west: float, north: float, east: float,
    *, img_w: int, img_h: int,
) -> int:
    """Return the largest OSM tile zoom where the bbox fits inside
    the image. Uses Web-Mercator-style math: one tile is 256 px,
    world-width at zoom z is 256 · 2^z pixels."""
    import math
    lat_c_rad = math.radians((south + north) / 2.0)
    lon_span = max(east - west, 1e-6)
    lat_span = max(north - south, 1e-6)
    for z in range(17, 5, -1):
        world_px = 256 * (2 ** z)
        # Horizontal span in pixels at zoom z.
        w_px = lon_span / 360.0 * world_px
        # Vertical span (Mercator compresses toward equator — close
        # enough for mid-latitudes without full merc math):
        h_px = lat_span / 360.0 * world_px / max(math.cos(lat_c_rad), 0.1)
        if w_px <= img_w and h_px <= img_h:
            return z
    return 6


def _load_sidecar_geoms(
    design_path: Path, slug: str,
) -> dict[str, list[list[tuple[float, float]]]]:
    """Pick up `{slug}.corridor.geojson` (auto-gen layout) or
    `{slug}-corridor.geojson` (hand-authored layout) sitting next
    to the design.toml. Returns `{line_name: [seg_coords, ...]}`,
    where each seg_coords is a list of `(lon, lat)` tuples. Empty
    dict if no sidecar exists or it has no `kind: line` features.
    """
    candidates = [
        design_path.parent / f"{slug}.corridor.geojson",
        design_path.parent / f"{slug}-corridor.geojson",
    ]
    sidecar = next((p for p in candidates if p.exists()), None)
    if sidecar is None:
        return {}
    try:
        geo = json.loads(sidecar.read_text())
    except (OSError, ValueError):
        return {}
    out: dict[str, list[list[tuple[float, float]]]] = {}
    for ft in geo.get("features", []):
        props = ft.get("properties", {}) or {}
        if props.get("kind") != "line":
            continue
        # Auto-gen tags features with `name`; hand-authored with `id`.
        name = props.get("id") or props.get("name")
        if not name:
            continue
        coords = ft.get("geometry", {}).get("coordinates") or []
        if len(coords) < 2:
            continue
        out.setdefault(name, []).append(
            [(float(lon), float(lat)) for lon, lat in coords]
        )
    return out


def _find_osm_cache(start: Path) -> Path:
    """Search up from `start` for the shared OSM cache directory
    (`docs/screenshots/.cache/osm`). Falls back to a local
    `.cache/osm` sibling so standalone runs still work."""
    cur = Path(start).resolve()
    for parent in [cur, *cur.parents]:
        shared = parent / "docs" / "screenshots" / ".cache" / "osm"
        if shared.exists():
            return shared
        if (parent / "Cargo.toml").exists():
            return parent / "docs" / "screenshots" / ".cache" / "osm"
    return cur / ".cache" / "osm"


if __name__ == "__main__":
    raise SystemExit(main())
