"""CLI + batch driver for `osr_planner`.

Single-city mode (for Samawah or any other bbox):

    python -m osr_planner \\
        --slug west-asia/Iraq/Samawah \\
        --country IQ \\
        --city "As-Samawah" \\
        --bbox 31.265,45.200,31.360,45.340 \\
        --center 31.308,45.283 \\
        --population 220000 \\
        --climate hot-desert \\
        --peak-sun 6.0 \\
        --out cities/catalogue/west-asia/Iraq/Samawah/design.toml

Batch mode (500-city run from a CSV):

    python -m osr_planner --batch cities.csv --out-root cities/catalogue/

CSV columns (header row required):

    slug,country,city,center_lat,center_lon,south,west,north,east,
    population,climate,peak_sun_hours,max_lines
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from .planner import CityInputs, plan_city


def _parse_force_anchors(raw: list[str]) -> tuple:
    """Parse `--force-anchor name:lat,lon[:weight]` specs into the
    (name, lat, lon, weight) tuple form `CityInputs.force_anchors`
    expects. Default weight is 95 (→ must-cover)."""
    out: list[tuple[str, float, float, float]] = []
    for spec in raw or ():
        # Format: "Name:lat,lon" or "Name:lat,lon:weight"
        head, _, tail = spec.partition(":")
        name = head.strip()
        if not tail:
            raise ValueError(
                f"--force-anchor '{spec}' missing coords; "
                "use 'Name:lat,lon[:weight]'"
            )
        coords, _, wstr = tail.partition(":")
        lat, lon = [float(x) for x in coords.split(",")]
        weight = float(wstr) if wstr else 95.0
        out.append((name, lat, lon, weight))
    return tuple(out)


def _run_single(args: argparse.Namespace) -> int:
    south, west, north, east = map(float, args.bbox.split(","))
    clat, clon = map(float, args.center.split(","))
    inputs = CityInputs(
        slug=args.slug,
        country_iso=args.country,
        city_name=args.city,
        center_lat=clat,
        center_lon=clon,
        bbox=(south, west, north, east),
        population=args.population,
        climate_preset=args.climate,
        peak_sun_hours=args.peak_sun,
        max_lines=args.max_lines,
        force_anchors=_parse_force_anchors(args.force_anchor),
        ring_line=args.ring_line,
    )
    plan = plan_city(inputs, cache_dir=args.cache_dir)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(plan.to_design_toml())
    print(f"wrote {out_path}  ({out_path.stat().st_size} bytes)")
    print()
    print(plan.metrics_summary())
    return 0


def _run_batch(args: argparse.Namespace) -> int:
    csv_path = Path(args.batch)
    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    summary_rows = [
        ("slug", "stations", "lines", "coverage", "transfer_reachability", "max_curvature_rad")
    ]
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                inputs = CityInputs(
                    slug=row["slug"],
                    country_iso=row.get("country", "XX"),
                    city_name=row.get("city", row["slug"]),
                    center_lat=float(row["center_lat"]),
                    center_lon=float(row["center_lon"]),
                    bbox=(
                        float(row["south"]),
                        float(row["west"]),
                        float(row["north"]),
                        float(row["east"]),
                    ),
                    population=int(row["population"]),
                    climate_preset=row.get("climate", "temperate"),
                    peak_sun_hours=float(row.get("peak_sun_hours", "5.0")),
                    max_lines=int(row["max_lines"]) if row.get("max_lines") else None,
                )
                plan = plan_city(inputs, cache_dir=args.cache_dir)
                out_path = out_root / inputs.slug / "design.toml"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(plan.to_design_toml())
                max_curv = max(plan.curvatures.values(), default=0.0)
                summary_rows.append((
                    inputs.slug,
                    len(plan.stations),
                    len(plan.lines),
                    f"{plan.coverage:.3f}",
                    f"{plan.transfer_reachability:.3f}",
                    f"{max_curv:.3f}",
                ))
                print(f"OK   {inputs.slug:<40}  {len(plan.stations):2d} stations, "
                      f"cov {plan.coverage:.1%}, xfer {plan.transfer_reachability:.0%}")
            except Exception as e:
                print(f"FAIL {row.get('slug', '?'):<40}  {e}", file=sys.stderr)
                summary_rows.append((row.get("slug", "?"), "FAIL", str(e), "", "", ""))

    # Write summary.csv at out_root.
    with (out_root / "summary.csv").open("w") as f:
        writer = csv.writer(f)
        writer.writerows(summary_rows)
    print(f"\nwrote {out_root / 'summary.csv'}  ({len(summary_rows) - 1} cities)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="osr_planner")
    ap.add_argument("--slug", help="e.g. west-asia/Iraq/Samawah")
    ap.add_argument("--country", default="XX", help="ISO 2-letter")
    ap.add_argument("--city", help="human-readable city name")
    ap.add_argument(
        "--bbox",
        help="south,west,north,east (degrees)",
    )
    ap.add_argument("--center", help="lat,lon (degrees)")
    ap.add_argument("--population", type=int, default=100_000)
    ap.add_argument("--climate", default="temperate")
    ap.add_argument("--peak-sun", type=float, default=5.0)
    ap.add_argument("--max-lines", type=int, default=None)
    ap.add_argument(
        "--ring-line", action="store_true",
        help="add a suburban ring line at ~70 %% of the farthest "
             "radial endpoint distance. Intersects every radial, "
             "so outer-to-outer trips avoid the central hub — "
             "standard pattern for metros over ~3 M population.",
    )
    ap.add_argument(
        "--force-anchor", action="append", default=[],
        metavar="NAME:LAT,LON[:WEIGHT]",
        help="inject an extra high-weight anchor the planner must "
             "treat as present (for under-construction suburbs / new "
             "developments with sparse OSM tagging). Default weight "
             "is 95 (triggers must-cover endpoint rule). Repeat for "
             "multiple anchors, e.g. "
             "--force-anchor 'Basmaya:33.275,44.570' "
             "--force-anchor 'Madinat Al Ward:33.270,44.600'",
    )
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/osm"))
    ap.add_argument("--batch", type=str, default=None)
    ap.add_argument("--out-root", type=Path, default=Path("cities/catalogue"))
    args = ap.parse_args(argv)

    if args.batch:
        return _run_batch(args)
    if not (args.slug and args.city and args.bbox and args.center and args.out):
        ap.error("single-city run needs --slug --city --bbox --center --out")
    return _run_single(args)


if __name__ == "__main__":
    raise SystemExit(main())
