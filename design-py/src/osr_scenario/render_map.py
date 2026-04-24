"""Render the two network-map PNGs for a city design.toml.

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
    "terminal":        "#d0382b",
    "depot-terminal":  "#8a2a62",
    "major":           "#2b6fd0",
    "interchange":     "#e8a63a",
    "standard":        "#ffffff",
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
    # Lowercase the city component for filename stability — the
    # design slug uses human casing (`west-asia/Iraq/Samawah`) but
    # README + scripts reference `samawah-network-map.png`.
    slug = doc.get("design", {}).get("id", "city").rsplit("/", 1)[-1].lower()

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    # Try to compute road-snapped routes (+ save the GeoJSON artefact).
    routes: dict | None = None
    if route_on_roads:
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

    # Two maps per city:
    #  1. `network-map.png`        — the FULL network, auto-fit zoom
    #                                so every suburban line is visible
    #                                even for metros like Baghdad.
    #  2. `network-map-detail.png` — central-city zoom, filtering
    #                                features to those within
    #                                `detail_radius_km` of the design
    #                                centre so the urban core is
    #                                legible.
    net_south, net_west, net_north, net_east = _network_bbox(doc)
    full_zoom = _fit_zoom(
        net_south, net_west, net_north, net_east,
        img_w=1600, img_h=1400,
    )
    full_zoom = max(6, min(17, full_zoom))

    loc = doc.get("location", {})
    detail_center = (
        float(loc.get("center_lat", (net_south + net_north) / 2)),
        float(loc.get("center_lon", (net_west + net_east) / 2)),
    )
    detail_radius_km = 8.0  # central-city footprint

    renders: list[tuple[str, int, tuple[int, int], tuple[float, float] | None, float | None]] = [
        ("network-map.png", full_zoom, (1600, 1400), None, None),
        ("network-map-detail.png", 13, (1800, 1600), detail_center, detail_radius_km),
    ]
    for (suffix, zoom, wh, center_filter, radius_km) in renders:
        m = StaticMap(
            *wh,
            url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
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

        def _draw_line(line_id: str, coords: list, color: str) -> None:
            is_ring = line_id == "line-ring"
            if is_ring:
                # White halo first (draws under), then black ring on top.
                m.add_line(Line(coords, ring_halo, ring_stroke + 4))
                m.add_line(Line(coords, ring_color, ring_stroke))
            else:
                m.add_line(Line(coords, color, line_stroke))

        for idx, line in enumerate(lines):
            color = _LINE_COLORS[idx % len(_LINE_COLORS)]
            track = line.get("track_polyline")
            if track and len(track) >= 2:
                coords = [(p[1], p[0]) for p in track]  # (lon, lat)
                if _line_in_range(coords):
                    _draw_line(line["id"], coords, color)
            elif routes is not None and line["id"] in routes:
                for seg in routes[line["id"]]:
                    if _line_in_range(seg["coords"]):
                        _draw_line(line["id"], seg["coords"], color)
            else:
                coords = [
                    (by_id[s["id"]]["lon"], by_id[s["id"]]["lat"])
                    for s in line.get("stations", [])
                ]
                if len(coords) >= 2 and _line_in_range(coords):
                    _draw_line(line["id"], coords, color)
        # Draw stations — filtered to the detail circle when present.
        seen: set[str] = set()
        big = zoom >= 13
        for s in doc.get("stations", []):
            if s["id"] in seen:
                continue
            seen.add(s["id"])
            if not _in_range(float(s["lat"]), float(s["lon"])):
                continue
            arch = s.get("archetype", "standard")
            outer = _ARCH_COLOR.get(arch, "#3f9b5b")
            if arch in ("terminal", "depot-terminal"):
                outer_r = 30 if big else 22
                inner_r = 12 if big else 9
            else:
                outer_r = 22 if big else 16
                inner_r = 9 if big else 7
            m.add_marker(CircleMarker((s["lon"], s["lat"]), outer, outer_r))
            m.add_marker(CircleMarker((s["lon"], s["lat"]), "#ffffff", inner_r))
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


def _network_bbox(doc: dict) -> tuple[float, float, float, float]:
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
    if not lats:
        # Fallback to the design's input bbox.
        bb = doc.get("location", {}).get("bbox", {})
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
