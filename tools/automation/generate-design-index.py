#!/usr/bin/env python3
"""Generate the committed city-design catalogue index."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGNS = REPO_ROOT / "cities/catalogue"
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the tracked catalogue index is stale")
    args = parser.parse_args()
    public_rows: list[str] = []
    comparison_rows: list[str] = []
    complete_packages = 0
    planning_packages = 0
    energy_passes = 0
    energy_failed_sites = 0
    stale_packages = 0
    for design_path in sorted(DESIGNS.glob("*/*/*/design.toml")):
        design = tomllib.loads(design_path.read_text())
        manifest_path = design_path.parent / "package-manifest.json"
        manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
        if manifest.get("passed") is True:
            complete_packages += 1
        planning_packages += manifest.get('planning_example_complete') is True
        package_label='screening complete' if manifest.get('passed') else 'planning complete; acceptance open' if manifest.get('planning_example_complete') else 'incomplete'
        stale_count = len(manifest.get("stale_analysis_sources", []))
        stale_packages += stale_count > 0
        energy_path = design_path.parent / "engineering/energy/summary.json"
        energy = json.loads(energy_path.read_text()) if energy_path.is_file() else {}
        energy_passes += energy.get("passed") is True
        failed_sites = {
            row["station"] for row in energy.get("contingency_findings", [])
            if row.get("code") == "site-grid-connection-limit-exceeded"
        }
        energy_failed_sites += len(failed_sites)
        city = design.get("city", {})
        lines = design.get("lines", [])
        fleets = design.get("fleets", [])
        route_km = sum(float(line.get("length_m", 0)) for line in lines) / 1_000
        family = lines[0].get("rolling_stock", "?") if lines else "?"
        relative = design_path.parent.relative_to(DESIGNS)
        slug = str(city.get("slug", design_path.parent.name.lower().replace(" ", "-")))
        target = relative.as_posix() + "/"
        package_evidence = (f"[{package_label}; {stale_count} stale sources]({target}package-manifest.json)"
                            if manifest_path.is_file() else "incomplete; package evidence missing")
        depot_report='engineering/delivery-baseline/DEPOT-PACKAGE.md' if slug=='baghdad' else 'engineering/line-depots/README.md'
        row = (
            f"| [{city.get('name', design_path.parent.name)}]({target}) "
            f"| `{family}` | {len(lines)} | {len(design.get('stations', []))} | "
            f"{route_km:.1f} | {sum(int(item.get('trainset_count', 0)) for item in fleets)} "
            f"| [{_coverage(design_path.parent):.0%} routing demand; access report]({target}engineering/access/README.md) "
            f"| [{'pass' if energy.get('passed') else 'fail/missing'}; {len(failed_sites)} sites]({target}engineering/energy/summary.json) "
            f"| {package_evidence} |"
            f" [full-fleet depot planning]({target}{depot_report}); [station-stabling diagnostic]({target}engineering/stabling/README.md) |"
        )
        if relative.parts[0] == "europe":
            comparison_rows.append(row)
        else:
            public_rows.append(row)

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
        f"This directory retains {len(public_rows)} developing-world city planning models and",
        f"{len(comparison_rows)} technical comparison "
        f"model{'s' if len(comparison_rows) != 1 else ''} defined by",
        "`lib/city-batches/world-sample.toml`. These routed designs are retained",
        "because reproducing them can require external OSM and population inputs.",
        "",
        "Generated city READMEs contain local values and evidence only. Shared methodology",
        "and limitations live in the",
        "[deployment planning reference](../../docs/deployment-planning-reference.md).",
        "Population access and multi-hop transfer paths are reported separately in each city's `engineering/access/README.md`.",
        "The routing-demand column is a high-demand cell fraction near tracks, not population coverage. Do not multiply it by city population.",
        "Each city also retains a [beam/support/terrain clearance screen](../../docs/civil/viaduct-obstacle-clearance.md); unresolved mapping or height data blocks physical release.",
        "",
        "Every city retains its design, simulator scenario, map, engineering review layers,",
        "validation summaries, operations asset index, acceptance report, and integrity",
        "manifest in one city directory. Raw solver networks, GeoPackages, compressed event",
        "bundles, and exploded manufacturing CSVs remain reproducible local outputs so the",
        "Git repository stays usable. Mosul and Samawah carry the full pilot evidence scope.",
        "The [operating-readiness audit](../../docs/operating/readiness.md) uses tracked",
        f"asset registers, manifests and compact twins from all {len(expected)} cities to compile",
        "their ERP/component profiles and family-applicable supervision packages.",
        "Planning completeness does not imply operator configuration, physical",
        "commissioning or railway release.",
        "",
        "## Validation status",
        "",
        f"Current planning examples: **{planning_packages} complete and {len(actual) - planning_packages} requiring refresh**.",
        f"Full screening acceptance: **{complete_packages} pass and {len(actual) - complete_packages} retain open gates**. Complete documented planning examples can retain unaccepted depot/stabling requirements.",
        f"**{stale_packages} packages retain stale analysis sources** requiring solver-evidence refresh.",
        "Each city's `package-manifest.json` lists missing evidence, failed summaries and stale sources. Package completeness",
        "is separate from the topology checks below and is not engineering or deployment approval.",
        "See the [substance review](../../docs/substance-review-2026-09-09.md) for model limitations.",
        f"Solar/storage snapshot screens: **{energy_passes} pass, {len(actual) - energy_passes} fail/missing; {energy_failed_sites:,} sites have grid-only contingency exceedances**.",
        "The site count includes grid-only diagnostics with solar and storage disabled. It is not a grid-upgrade requirement; snapshot passes do not establish operating endurance.",
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
        "| City | Train family | Lines | Stations | Route km | Fleet | Routing demand / population access | Electrical screen | Planning package / open gates | Depot requirements |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|",
        *public_rows,
        "",
        "## Technical comparison model",
        "",
        "The model below is retained only for engineering comparison and regression",
        "inspection. It is excluded from the public programme, portfolio, national",
        "briefs, reader-book city evidence, and front-page examples.",
        "",
        "| City | Train family | Lines | Stations | Route km | Fleet | Routing demand / population access | Electrical screen | Planning package / open gates | Depot requirements |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|",
        *comparison_rows,
        "",
        "```bash",
        "tools/automation/regenerate-city.sh samawah",
        "```",
        "",
        "The command refreshes the full package in the canonical `cities/catalogue/` tree.",
    ]
    expected_text = "\n".join(content) + "\n"
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != expected_text:
            raise SystemExit(f"stale city catalogue index: {OUT.relative_to(REPO_ROOT)}")
        print(f"current: {OUT.relative_to(REPO_ROOT)}")
        return 0
    OUT.write_text(expected_text, encoding="utf-8")
    print(
        f"wrote {OUT.relative_to(REPO_ROOT)} "
        f"({len(public_rows)} public + {len(comparison_rows)} comparison city designs)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
