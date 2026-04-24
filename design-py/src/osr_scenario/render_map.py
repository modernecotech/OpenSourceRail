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
# distinct colours automatically.
_LINE_COLORS = [
    "#2b6fd0",  # blue
    "#e8a63a",  # orange
    "#3f9b5b",  # green
    "#b544a0",  # magenta
    "#46c2c9",  # teal
    "#8a5cd2",  # purple
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

            cdir = cache_dir or (out_dir.parent / ".cache" / "osm")
            routes = route_lines(doc, cdir)
            geojson = routes_to_geojson(doc, routes)
            corridor_path = out_dir / f"{slug}-corridor.geojson"
            corridor_path.write_text(json.dumps(geojson))
            print(f"wrote {corridor_path}  ({corridor_path.stat().st_size // 1024} KB)")
            written.append(corridor_path)
        except Exception as e:
            print(f"warning: road routing failed, falling back to straight segments: {e}")
            routes = None

    for (suffix, zoom, wh) in [
        ("network-map.png", 13, (1600, 1400)),
        ("network-map-detail.png", 14, (1800, 1600)),
    ]:
        m = StaticMap(
            *wh,
            url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        )
        # Draw lines. Priority: (a) `track_polyline` committed by
        # the planner into design.toml is the authoritative geometry
        # — drawing it avoids renderer-side shortest-path detours
        # between consecutive stations. (b) routed shortest-paths
        # between station pairs. (c) straight segments as a last
        # resort.
        for idx, line in enumerate(lines):
            color = _LINE_COLORS[idx % len(_LINE_COLORS)]
            track = line.get("track_polyline")
            if track and len(track) >= 2:
                coords = [(p[1], p[0]) for p in track]  # (lon, lat) for staticmap
                m.add_line(Line(coords, color, 7 if zoom == 13 else 10))
            elif routes is not None and line["id"] in routes:
                for seg in routes[line["id"]]:
                    m.add_line(Line(seg["coords"], color, 7 if zoom == 13 else 10))
            else:
                coords = [
                    (by_id[s["id"]]["lon"], by_id[s["id"]]["lat"])
                    for s in line.get("stations", [])
                ]
                if len(coords) >= 2:
                    m.add_line(Line(coords, color, 7 if zoom == 13 else 10))
        # Draw stations. Terminals get an oversized marker so the
        # red dot definitively dominates any line stroke at the tip;
        # otherwise a thick line reads as "extending past" the
        # station even when its geometry stops exactly at the
        # station's centre.
        seen: set[str] = set()
        for s in doc.get("stations", []):
            if s["id"] in seen:
                continue
            seen.add(s["id"])
            arch = s.get("archetype", "standard")
            outer = _ARCH_COLOR.get(arch, "#3f9b5b")
            if arch in ("terminal", "depot-terminal"):
                outer_r = 22 if zoom == 13 else 30
                inner_r = 9 if zoom == 13 else 12
            else:
                outer_r = 16 if zoom == 13 else 22
                inner_r = 7 if zoom == 13 else 9
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
        args.out_dir = repo_root / "docs/screenshots"

    render_city(args.design, args.out_dir)
    return 0


def _find_repo_root() -> Path:
    cur = Path(__file__).resolve()
    for parent in cur.parents:
        if (parent / "Cargo.toml").exists():
            return parent
    return Path.cwd()


if __name__ == "__main__":
    raise SystemExit(main())
