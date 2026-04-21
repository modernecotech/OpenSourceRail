"""Generate a cities.toml from a GeoNames-style CSV.

The GeoNames `cities500.txt` file (tab-separated, public domain) lists
every populated place ≥ 500 inhabitants. A filter + bbox synthesis turns
it into an input for the batch driver.

Usage:
    osr-cities-scan --geonames cities500.txt \
                    --min-pop 200000 \
                    --max-cities 500 \
                    --out designs/cities/batch-500.toml

The bbox is derived from the centroid + a rule-of-thumb size based on
population — 8 km per side for 100k cities, scaling up to ~20 km for
multi-million cities. A city can override this in the generated TOML
after one production run identifies coverage gaps.
"""

from __future__ import annotations

import argparse
import csv
import logging
import math
import sys
from dataclasses import dataclass
from pathlib import Path

from osr_batch.existing_transit import has_existing_transit

log = logging.getLogger(__name__)

# Continent mapping is derived from feature class + country; we attach
# the bucket our composition profiles expect (middle-east, east-africa,
# etc.) with a small table. Unknowns fall back to 'unknown'.
COUNTRY_CONTINENT = {
    # Middle East + North Africa
    "IQ": "middle-east", "SA": "middle-east", "EG": "middle-east",
    "SD": "middle-east", "MA": "north-africa", "LY": "north-africa",
    "DZ": "north-africa", "TN": "north-africa", "JO": "middle-east",
    "SY": "middle-east", "IR": "middle-east", "YE": "middle-east",
    "OM": "middle-east", "AE": "middle-east", "KW": "middle-east",
    "QA": "middle-east", "BH": "middle-east", "IL": "middle-east",
    "LB": "middle-east", "PS": "middle-east", "TR": "middle-east",
    # Sub-Saharan Africa
    "KE": "east-africa", "TZ": "east-africa", "UG": "east-africa",
    "RW": "east-africa", "ET": "east-africa", "ZM": "east-africa",
    "MW": "east-africa", "SO": "east-africa", "SS": "east-africa",
    "ER": "east-africa", "NG": "west-africa", "GH": "west-africa",
    "CI": "west-africa", "SN": "west-africa", "ML": "west-africa",
    "BF": "west-africa", "NE": "west-africa", "TD": "west-africa",
    "MR": "west-africa", "CM": "west-africa", "ZA": "south-africa",
    "ZW": "south-africa", "MZ": "south-africa", "AO": "south-africa",
    "CD": "central-africa", "CG": "central-africa", "CF": "central-africa",
    # South Asia
    "IN": "south-asia", "BD": "south-asia", "PK": "south-asia",
    "LK": "south-asia", "NP": "south-asia",
    # East + SE Asia
    "CN": "east-asia", "JP": "east-asia", "KR": "east-asia",
    "MY": "southeast-asia", "ID": "southeast-asia", "TH": "southeast-asia",
    "VN": "southeast-asia", "PH": "southeast-asia", "KH": "southeast-asia",
    "LA": "southeast-asia", "MM": "southeast-asia",
    # Europe
    "FR": "europe", "DE": "europe", "IT": "europe", "ES": "europe",
    "PT": "europe", "GB": "europe", "IE": "europe", "NL": "europe",
    "BE": "europe", "DK": "europe", "SE": "europe", "NO": "europe",
    "FI": "europe", "PL": "europe", "CZ": "europe", "SK": "europe",
    "HU": "europe", "AT": "europe", "CH": "europe", "GR": "europe",
    "RO": "europe", "BG": "europe", "HR": "europe", "SI": "europe",
    # Latin America
    "MX": "latin-america", "BR": "latin-america", "AR": "latin-america",
    "CL": "latin-america", "CO": "latin-america", "PE": "latin-america",
    "EC": "latin-america", "BO": "latin-america", "UY": "latin-america",
    "PY": "latin-america", "VE": "latin-america", "CR": "latin-america",
    "PA": "latin-america", "GT": "latin-america", "CU": "latin-america",
    "DO": "latin-america", "HT": "latin-america",
    # North America + Oceania
    "US": "north-america", "CA": "north-america",
    "AU": "oceania", "NZ": "oceania",
}


@dataclass
class GeonamesRow:
    name: str
    country: str
    lat: float
    lon: float
    population: int
    feature: str
    asciiname: str


def _iter_geonames(path: Path) -> list[GeonamesRow]:
    """GeoNames is tab-separated with 19 columns, no header.

    Columns (selected):
        0  geonameid
        1  name
        2  asciiname
        4  latitude
        5  longitude
        6  feature class (P = populated place)
        7  feature code (PPLC, PPLA...)
        8  country code
        14 population
    """
    rows: list[GeonamesRow] = []
    with path.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for r in reader:
            if len(r) < 15 or r[6] != "P":
                continue
            try:
                rows.append(
                    GeonamesRow(
                        name=r[1],
                        asciiname=r[2],
                        lat=float(r[4]),
                        lon=float(r[5]),
                        feature=r[7],
                        country=r[8],
                        population=int(r[14] or "0"),
                    )
                )
            except ValueError:
                continue
    return rows


def _bbox_for(pop: int, lat: float, lon: float) -> tuple[float, float, float, float]:
    """Heuristic: small cities get ~8 km boxes, megacities ~20 km."""
    side_km = 8.0 + 6.0 * min(1.0, math.log10(max(pop, 1)) - 4.0)
    side_km = max(6.0, min(22.0, side_km))
    dlat = (side_km / 2.0) / 111.0
    dlon = (side_km / 2.0) / (111.0 * max(0.1, math.cos(math.radians(lat))))
    return (lat - dlat, lon - dlon, lat + dlat, lon + dlon)


def _slugify(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Filter GeoNames CSV into an OSR cities.toml.")
    ap.add_argument("--geonames", type=Path, required=True, help="cities500.txt from geonames.org")
    ap.add_argument("--min-pop", type=int, default=200_000)
    ap.add_argument("--max-cities", type=int, default=500)
    ap.add_argument("--countries", nargs="*", help="Limit to ISO-2 country codes.")
    ap.add_argument("--features", nargs="*", default=["PPLC", "PPLA", "PPLA2", "PPLA3"],
                    help="GeoNames feature codes to keep (default: capitals + admin seats).")
    ap.add_argument("--include-existing-transit", action="store_true",
                    help="Keep cities that already run metro/tram/LRT. Default excludes them.")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    rows = _iter_geonames(args.geonames)
    log.info("loaded %d rows from %s", len(rows), args.geonames)

    prelim = [
        r
        for r in rows
        if r.population >= args.min_pop
        and r.feature in args.features
        and (not args.countries or r.country in args.countries)
    ]
    prelim.sort(key=lambda r: r.population, reverse=True)

    keep: list[GeonamesRow] = []
    skipped_transit: list[GeonamesRow] = []
    for r in prelim:
        if not args.include_existing_transit and has_existing_transit(
            r.country, r.asciiname, r.name
        ):
            skipped_transit.append(r)
            continue
        keep.append(r)
    keep = keep[: args.max_cities]

    if skipped_transit:
        log.info(
            "excluded %d cities with existing metro/tram/LRT", len(skipped_transit)
        )
        for r in skipped_transit[:20]:
            log.debug("  excluded: %s (%s, pop=%d)", r.asciiname, r.country, r.population)
    log.info("kept %d cities", len(keep))

    lines: list[str] = []
    lines.append("# Auto-generated from GeoNames by osr-cities-scan.")
    lines.append("# Re-run with the same filters to reproduce exactly.")
    lines.append("# Bounding boxes are heuristic; refine by hand after a first\n# pipeline run if coverage metrics are low for a specific city.\n")
    seen_slugs: set[str] = set()
    for r in keep:
        base = _slugify(r.asciiname or r.name)
        slug = base
        i = 2
        while slug in seen_slugs:
            slug = f"{base}-{i}"
            i += 1
        seen_slugs.add(slug)
        s, w, n, e = _bbox_for(r.population, r.lat, r.lon)
        continent = COUNTRY_CONTINENT.get(r.country, "unknown")
        lines.append("[[cities]]")
        lines.append(f'slug        = "{slug}"')
        lines.append(f'country     = "{r.country}"')
        lines.append(f'continent   = "{continent}"')
        lines.append(f"population  = {r.population}")
        lines.append(
            f"bbox        = {{ south = {s:.4f}, west = {w:.4f}, north = {n:.4f}, east = {e:.4f} }}"
        )
        lines.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines))
    log.info("wrote %s", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
