"""CLI wrapper: pull OSM layers for a city, write JSON to stdout or file.

Usage:
    osr-osm-pull --slug samawah --bbox 31.26,45.23,31.36,45.33 \
                 --out cache/samawah.osm.json

The bbox is south,west,north,east decimal degrees (WGS84).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .fetcher import BBox, fetch_city


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pull OSM layers for a city bbox.")
    ap.add_argument("--slug", required=True, help="City slug (e.g. samawah).")
    ap.add_argument(
        "--bbox",
        required=True,
        help="south,west,north,east decimal degrees (WGS84).",
    )
    ap.add_argument("--out", type=Path, default=None, help="Output JSON path.")
    ap.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Cache root (default ~/.cache/osr-design/osm).",
    )
    ap.add_argument("--refresh", action="store_true", help="Bypass cache.")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    try:
        s, w, n, e = (float(x) for x in args.bbox.split(","))
    except ValueError:
        ap.error("bbox must be four comma-separated numbers: S,W,N,E")
        return 2

    bbox = BBox(south=s, west=w, north=n, east=e)
    city = fetch_city(bbox, args.slug, cache_dir=args.cache_dir, force_refresh=args.refresh)
    print(city.summary(), file=sys.stderr)

    payload = json.dumps(city.to_json(), indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload)
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
