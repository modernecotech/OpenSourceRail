"""Render the two network-map PNGs for a city design.toml.

Consumes the same design.toml the scenario generator does, so as soon
as coordinates / lines / stations change in the design, regenerating
the maps is one command. No hand-edits to the image metadata, no
copied station lists.

Usage:
    python -m osr_scenario.render_map \\
        --design designs/middle-east/iraq/samawah/design.toml \\
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

    If `route_on_roads` is True (default), lines are drawn along the
    shortest-path through the OSM road graph between stations — a
    `corridor.geojson` is emitted alongside the PNGs. Falls back to
    straight segments if the road fetch fails or `networkx` is
    unavailable. Returns the list of written artefact paths.
    """
    from staticmap import StaticMap, CircleMarker, Line

    doc = tomllib.loads(design_path.read_text())
    by_id = {s["id"]: s for s in doc["stations"]}
    lines = doc["lines"]
    slug = doc.get("design", {}).get("id", "city").rsplit("/", 1)[-1]

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
        # Draw lines — road-snapped if available, straight otherwise.
        for idx, line in enumerate(lines):
            color = _LINE_COLORS[idx % len(_LINE_COLORS)]
            if routes is not None and line["id"] in routes:
                for seg in routes[line["id"]]:
                    m.add_line(Line(seg["coords"], color, 7 if zoom == 13 else 10))
            else:
                coords = [
                    (by_id[s["id"]]["lon"], by_id[s["id"]]["lat"])
                    for s in line.get("stations", [])
                ]
                if len(coords) >= 2:
                    m.add_line(Line(coords, color, 7 if zoom == 13 else 10))
        # Draw stations.
        seen: set[str] = set()
        for s in doc.get("stations", []):
            if s["id"] in seen:
                continue
            seen.add(s["id"])
            outer = _ARCH_COLOR.get(s.get("archetype", "standard"), "#3f9b5b")
            m.add_marker(CircleMarker((s["lon"], s["lat"]), outer, 16 if zoom == 13 else 22))
            m.add_marker(CircleMarker((s["lon"], s["lat"]), "#ffffff", 7 if zoom == 13 else 9))
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
        args.design = repo_root / "designs/middle-east/iraq/samawah/design.toml"
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
