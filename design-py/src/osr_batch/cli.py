"""CLI: run the OSR design pipeline over a cities.toml file."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .runner import run_batch


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run the OSR design pipeline over a list of cities.")
    ap.add_argument("--cities", type=Path, required=True, help="cities.toml file")
    ap.add_argument("--cache", type=Path, required=True, help="cache root (OSM + rasters)")
    ap.add_argument("--out", type=Path, required=True, help="design output root")
    ap.add_argument(
        "--osr-design",
        type=Path,
        required=True,
        help="path to the osr-design binary (e.g. target/debug/osr-design)",
    )
    ap.add_argument("--cell-m", type=float, default=20.0)
    ap.add_argument("--summary-csv", type=Path, default=None)
    ap.add_argument("--only", nargs="*", default=None, help="slugs to include (default all)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    rows = run_batch(
        cities_toml=args.cities,
        cache_root=args.cache,
        out_root=args.out,
        osr_design_bin=args.osr_design,
        cell_m=args.cell_m,
        summary_csv=args.summary_csv,
        only=args.only,
    )

    n = len(rows)
    passed = sum(1 for r in rows if r.get("pass"))
    print(f"batch complete: {passed}/{n} passed", file=sys.stderr)
    for r in rows:
        status = "PASS" if r.get("pass") else "FAIL"
        extra = r.get("error", "")
        print(
            f"  {status} {r['slug']:20s} stations={r.get('n_stations', '-')} "
            f"length_m={r.get('total_route_m', '-')} {extra}",
            file=sys.stderr,
        )
    return 0 if passed == n else 1


if __name__ == "__main__":
    raise SystemExit(main())
