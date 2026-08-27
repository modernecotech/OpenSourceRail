#!/usr/bin/env python3
"""Generate the committed city-design catalogue index."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGNS = REPO_ROOT / "designs"
OUT = DESIGNS / "README.md"
CATALOG = REPO_ROOT / "lib" / "city-batches" / "world-sample.toml"
RING_VALIDATION = DESIGNS / "ring-interchange-validation.json"
STATION_VALIDATION = DESIGNS / "station-cluster-validation.json"


def _coverage(city_dir: Path) -> float:
    quality = next(city_dir.glob("*.design-quality.yaml"), None)
    if quality is None:
        return 0.0
    match = re.search(r"(?:high_demand_coverage|coverage_score|coverage):\s*([0-9.]+)", quality.read_text())
    return float(match.group(1)) if match else 0.0


def main() -> int:
    rows: list[str] = []
    for design_path in sorted(DESIGNS.glob("*/*/*/design.toml")):
        design = tomllib.loads(design_path.read_text())
        city = design.get("city", {})
        lines = design.get("lines", [])
        fleets = design.get("fleets", [])
        route_km = sum(float(line.get("length_m", 0)) for line in lines) / 1_000
        family = lines[0].get("rolling_stock", "?") if lines else "?"
        relative = design_path.parent.relative_to(DESIGNS)
        slug = str(city.get("slug", design_path.parent.name.lower().replace(" ", "-")))
        target = relative.as_posix() + "/"
        rows.append(
            f"| [{city.get('name', design_path.parent.name)}]({target}) "
            f"| `{family}` | {len(lines)} | {len(design.get('stations', []))} | "
            f"{route_km:.1f} | {sum(int(item.get('trainset_count', 0)) for item in fleets)} "
            f"| {_coverage(design_path.parent):.0%} |"
        )

    source = tomllib.loads(CATALOG.read_text())
    expected = {str(city["slug"]) for city in source.get("cities", [])}
    actual = {
        str(tomllib.loads(path.read_text()).get("city", {}).get("slug", ""))
        for path in DESIGNS.glob("*/*/*/design.toml")
    }
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise SystemExit(f"city core mismatch; missing={missing}, unexpected={unexpected}")

    expected_continents = {
        str(city["slug"]): str(city["continent"]) for city in source.get("cities", [])
    }
    for design_path in sorted(DESIGNS.glob("*/*/*/design.toml")):
        slug = str(tomllib.loads(design_path.read_text()).get("city", {}).get("slug", ""))
        actual_continent = design_path.relative_to(DESIGNS).parts[0]
        if actual_continent != expected_continents[slug]:
            raise SystemExit(
                f"city path mismatch for {slug}: expected {expected_continents[slug]}, "
                f"found {actual_continent}"
            )

    ring_validation = json.loads(RING_VALIDATION.read_text())
    ring_cities = {str(result["city"]) for result in ring_validation.get("results", [])}
    if ring_cities != expected:
        missing = sorted(expected - ring_cities)
        unexpected = sorted(ring_cities - expected)
        raise SystemExit(
            f"ring-validation coverage mismatch; missing={missing}, unexpected={unexpected}"
        )
    ring_failed_count = len(ring_validation.get("failed_cities", []))
    ring_passed_count = len(expected) - ring_failed_count

    station_validation = json.loads(STATION_VALIDATION.read_text())
    station_cities = {
        str(result["city"]) for result in station_validation.get("results", [])
    }
    if station_cities != expected:
        missing = sorted(expected - station_cities)
        unexpected = sorted(station_cities - expected)
        raise SystemExit(
            f"station-validation coverage mismatch; missing={missing}, unexpected={unexpected}"
        )
    station_failed_count = len(station_validation.get("failed_cities", []))
    station_passed_count = len(expected) - station_failed_count

    content = [
        "# City Design Catalogue",
        "",
        f"This directory retains the compact machine-readable result set for all {len(rows)} cities",
        "defined by `lib/city-batches/world-sample.toml`. These routed designs are retained",
        "because reproducing them can require external OSM and population inputs.",
        "",
        "Generated city READMEs contain local values and evidence only. Shared methodology",
        "and limitations live in the",
        "[deployment planning reference](../docs/deployment-planning-reference.md).",
        "",
        "Every city retains its design, simulator scenario, map, engineering review layers,",
        "validation summaries, operations asset index, acceptance report, and integrity",
        "manifest in one city directory. Raw solver networks, GeoPackages, compressed event",
        "bundles, and exploded manufacturing CSVs remain reproducible local outputs so the",
        "Git repository stays usable. Mosul and Samawah remain the full acceptance references.",
        "",
        "## Validation status",
        "",
        "The retained",
        "[`ring-interchange-validation.json`](ring-interchange-validation.json) report checks",
        f"all {len(expected)} cities: **{ring_passed_count} pass and {ring_failed_count} require ring/topology review",
        "or rerouting** under the current validator. A retained failed design is a",
        "recoverable planning input, not a deployment-ready reference; Mosul and Samawah",
        "remain the primary full-payload worked examples.",
        "",
        "The stricter",
        "[`station-cluster-validation.json`](station-cluster-validation.json) report records",
        f"**{station_passed_count} passing cities, {station_failed_count} cities requiring review, and",
        f"{int(station_validation.get('failure_count', 0)):,} station/interchange findings**.",
        "Its hashes bind each finding set to the retained design and validator.",
        "Basra, Mosul, and Samawah pass both catalogue validators.",
        "",
        "The historical",
        "[`engineering-batch-summary-aleppo-amman.json`](engineering-batch-summary-aleppo-amman.json)",
        "is explicitly scoped to those two cities and is not catalogue-wide evidence.",
        "",
        "| City | Train family | Lines | Stations | Route km | Fleet | High-demand coverage |",
        "|---|---|---:|---:|---:|---:|---:|",
        *rows,
        "",
        "```bash",
        "scripts/regenerate-city.sh samawah",
        "```",
        "",
        "The command refreshes the full package in the canonical `designs/` tree.",
    ]
    OUT.write_text("\n".join(content) + "\n")
    print(f"wrote {OUT.relative_to(REPO_ROOT)} ({len(rows)} city designs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
