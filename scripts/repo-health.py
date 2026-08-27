#!/usr/bin/env python3
"""Repository health checks for OSR source and compact reference fixtures.

The checks here are deliberately boring: they catch drift between the
current concept, the generated city artefacts, and the CAPEX formulas.
Run from the repository root:

    python3 scripts/repo-health.py
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import runpy
import re
import subprocess
import sys
import tempfile
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CAPEX_COSTS = tomllib.loads((REPO_ROOT / "lib/templates/capex-costs.toml").read_text())
CIVIL_COST_MODEL = tomllib.loads(
    (REPO_ROOT / "lib/templates/civil-cost-model.toml").read_text()
)
USD_TO_EUR = float(CAPEX_COSTS["schema"]["usd_to_eur"])
TRAINSET_COST_USD = {
    str(k): float(v) for k, v in CAPEX_COSTS["trainset_unit_usd"].items()
}
PRODUCTION_PLANT_PER_VEHICLE_USD = float(CAPEX_COSTS["production_plant"]["per_vehicle_usd"])
ROLLING_STOCK_ASSEMBLY_FRACTION = float(
    CAPEX_COSTS["trainset_cost_basis"]["local_assembly_fraction"]
)
FAMILY_CAR_COUNT = {
    "urban-shuttle-1car": 1,
    "tram-2car": 2,
    "light-metro-3car": 3,
    "metro-4car": 4,
    "metro-6car": 6,
}
CHARGING_MICROGRID_EUR = {
    str(k): float(v) * USD_TO_EUR
    for k, v in CAPEX_COSTS["charging_microgrid_unit_usd"].items()
}
SIGNALLING_EUR_PER_KM = float(CAPEX_COSTS["systems"]["signalling_usd_per_km"]) * USD_TO_EUR
EPC_OVERHEAD_FRAC = float(CAPEX_COSTS["overhead"]["epc_fraction"])
BOM_SOURCE = REPO_ROOT / "docs/rolling-stock/light-metro-3car/bom-skeleton.md"
BOM_EXPORTER = REPO_ROOT / "scripts/export-light-metro-bom.py"
STATION_CATALOG = REPO_ROOT / "mechanical-py/catalog/buildable-stations"
SAMAWAH_DESIGN_DIR = REPO_ROOT / "designs/west-asia/Iraq/Samawah"
SAMAWAH_ALN_DIR = SAMAWAH_DESIGN_DIR / "engineering/alignment"
SAMAWAH_ALN_DESIGN_DATE = "2026-08-12"
STATION_CLUSTER_VALIDATOR = REPO_ROOT / "scripts/validate-station-clusters.py"
STATION_CLUSTER_REPORT = REPO_ROOT / "designs/station-cluster-validation.json"
RING_INTERCHANGE_VALIDATOR = REPO_ROOT / "scripts/validate-ring-interchanges.py"
RING_INTERCHANGE_REPORT = REPO_ROOT / "designs/ring-interchange-validation.json"
REVIEWED_CITY_SLUGS = {"basra", "mosul", "samawah"}
FULL_ACCEPTANCE_CITY_SLUGS = {"mosul", "samawah"}


@dataclass
class Finding:
    path: Path
    message: str

    def render(self) -> str:
        try:
            rel = self.path.relative_to(REPO_ROOT)
        except ValueError:
            rel = self.path
        return f"{rel}: {self.message}"


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def _route_km(design: dict) -> float:
    return sum(float(line.get("length_m", 0.0)) for line in design.get("lines", [])) / 1000.0


def _family(design: dict) -> str:
    families = {
        line.get("rolling_stock")
        for line in design.get("lines", [])
        if line.get("rolling_stock")
    }
    if not families:
        return "light-metro-3car"
    if len(families) != 1:
        return "<mixed>"
    return next(iter(families))


def _fleet_total(design: dict) -> int:
    return sum(int(fleet.get("trainset_count", 0)) for fleet in design.get("fleets", []))


def _charging_microgrid_total(design: dict) -> int:
    technology = design.get("costs", {}).get("technology_basis", {})
    multiplier = int(
        technology.get(
            "station_charging_cabinet_count",
            2 if _family(design) == "metro-6car" else 1,
        )
    )
    return multiplier * sum(
        CHARGING_MICROGRID_EUR.get(station.get("archetype", "standard"), 250_000)
        for station in design.get("stations", [])
    )


def _almost_equal(a: float, b: float, tolerance: float = 2.0) -> bool:
    return abs(a - b) <= tolerance


def _space_int(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", " ")


def _compact_money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}k"
    return f"${value:.0f}"


def _compact_million_money(value: float) -> str:
    return f"${value / 1_000_000:.1f}M"


def _markdown_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _markdown_money(value: str) -> int:
    cleaned = (
        value.replace("*", "")
        .replace("USD", "")
        .replace("$", "")
        .replace(",", "")
        .replace(" ", "")
        .strip()
    )
    return int(float(cleaned))


def _require_text(
    findings: list[Finding],
    path: Path,
    text: str,
    expected: str,
    message: str,
) -> None:
    if expected not in text:
        findings.append(Finding(path, f"{message}: missing {expected!r}"))


def _check_usd_mirror(
    findings: list[Finding],
    design_path: Path,
    costs: dict,
    stem: str,
    tolerance: float = 2.0,
) -> None:
    usd_key = f"{stem}_usd"
    eur_key = f"{stem}_eur"
    if usd_key not in costs or eur_key not in costs:
        return
    expected_eur = float(costs[usd_key]) * USD_TO_EUR
    if not _almost_equal(expected_eur, float(costs[eur_key]), tolerance):
        findings.append(Finding(design_path, f"{eur_key} does not match {usd_key} × usd_to_eur"))


def check_city_artifacts() -> list[Finding]:
    findings: list[Finding] = []
    design_paths = sorted((REPO_ROOT / "designs").glob("*/*/*/design.toml"))
    catalog = _load_toml(REPO_ROOT / "lib/city-batches/world-sample.toml")
    expected_slugs = {str(city["slug"]) for city in catalog.get("cities", [])}
    expected_continents = {
        str(city["slug"]): str(city["continent"]) for city in catalog.get("cities", [])
    }
    actual_slugs = {
        str(_load_toml(path).get("city", {}).get("slug", ""))
        for path in design_paths
    }
    if actual_slugs != expected_slugs:
        findings.append(Finding(
            REPO_ROOT / "designs",
            f"committed city core differs from source catalogue; missing={sorted(expected_slugs - actual_slugs)}, "
            f"unexpected={sorted(actual_slugs - expected_slugs)}",
        ))

    for design_path in design_paths:
        city_dir = design_path.parent
        design = _load_toml(design_path)
        slug = str(design.get("city", {}).get("slug", city_dir.name.lower().replace(" ", "-")))
        actual_continent = design_path.relative_to(REPO_ROOT / "designs").parts[0]
        if expected_continents.get(slug) != actual_continent:
            findings.append(Finding(
                design_path,
                f"catalogue continent is {expected_continents.get(slug)!r}, not {actual_continent!r}",
            ))
        required = [
            city_dir / f"{slug}.toml",
            city_dir / f"{slug}.corridor.geojson",
            city_dir / f"{slug}.stations.json",
            city_dir / f"{slug}.design-quality.yaml",
        ]
        if slug in REVIEWED_CITY_SLUGS:
            required.extend([city_dir / "README.md", city_dir / f"{slug}-network-map.png"])
        for path in required:
            if not path.exists():
                findings.append(Finding(path, "missing generated city artifact"))

        scenario_path = city_dir / f"{slug}.toml"
        if scenario_path.exists():
            scenario = _load_toml(scenario_path)
            family = _family(design)
            expected_consists = {
                "urban-shuttle-1car": (34_000, 225, 500),
                "tram-2car": (68_000, 450, 500),
                "light-metro-3car": (78_750, 675, 500),
                "metro-4car": (136_000, 900, 500),
                "metro-6car": (204_000, 1_350, 1_000),
            }
            if family in expected_consists:
                expected_mass, expected_battery, expected_charge = expected_consists[family]
                technology = design.get("costs", {}).get("technology_basis", {})
                expected_charge = 500 * int(
                    technology.get(
                        "station_charging_cabinet_count",
                        {"metro-4car": 3, "metro-6car": 4}.get(family, 1),
                    )
                )
                consist = scenario.get("consist", {})
                if int(consist.get("mass_kg", 0)) != expected_mass:
                    findings.append(Finding(scenario_path, f"stale {family} consist mass"))
                if int(consist.get("battery_capacity_kwh", 0)) != expected_battery:
                    findings.append(Finding(scenario_path, f"stale {family} gross battery capacity"))
                charge_powers = {
                    int(station.get("charging_power_kw", 0))
                    for station in scenario.get("stations", [])
                    if int(station.get("charging_power_kw", 0)) > 0
                }
                if charge_powers != {expected_charge}:
                    findings.append(
                        Finding(
                            scenario_path,
                            f"charging powers {sorted(charge_powers)} do not match current {family} module policy",
                        )
                    )

        readme = city_dir / "README.md"
        if readme.exists():
            text = readme.read_text()
            if "Station/depot charging microgrids" not in text:
                findings.append(Finding(readme, "missing station/depot charging microgrid cost row"))
            if "Shared national railway production plant" not in text:
                findings.append(Finding(readme, "missing shared national railway production plant section"))
            if "External capital for imported components / machinery" not in text:
                findings.append(Finding(readme, "missing imported/external capital requirement"))
            if "Foreign-company turnkey comparison" not in text:
                findings.append(Finding(readme, "missing foreign-turnkey capital comparison"))
            if "> **Foreign-capital advantage:**" not in text:
                findings.append(Finding(readme, "missing headline foreign-capital advantage"))
            if "Capital plus saved interest totals" not in text:
                findings.append(Finding(readme, "missing lifetime capital-and-interest saving"))
            for stale in ("Traction power", "€0.8 M/km", "Residual train-control wayside + power"):
                if stale in text:
                    findings.append(Finding(readme, f"stale generated README wording: {stale!r}"))

        finance_path = city_dir / "engineering/finance/summary.json"
        if not finance_path.is_file():
            findings.append(Finding(finance_path, "missing city finance summary"))
        else:
            finance = json.loads(finance_path.read_text())
            sources = finance.get("sources", {})
            expected_sources = {
                "design_sha256": design_path,
                "scenario_sha256": scenario_path,
                "generator_sha256": REPO_ROOT / "scripts/generate-city-finance.py",
                "capital_model_sha256": REPO_ROOT
                / "design-py/src/osr_scenario/capital.py",
                "network_finance_model_sha256": REPO_ROOT
                / "design-py/src/osr_scenario/network_readme.py",
                "capex_costs_sha256": REPO_ROOT / "lib/templates/capex-costs.toml",
                "civil_cost_model_sha256": REPO_ROOT
                / "lib/templates/civil-cost-model.toml",
                "country_finance_sha256": REPO_ROOT
                / "lib/templates/country-finance.toml",
            }
            if finance.get("schema_version") != 4 or not finance.get("passed"):
                findings.append(Finding(finance_path, "city finance summary is not a passing schema-v4 result"))
            for key, source_path in expected_sources.items():
                expected_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
                if sources.get(key) != expected_hash:
                    findings.append(Finding(finance_path, f"stale finance source hash: {key}"))
            if "foreign_turnkey_comparator" not in finance:
                findings.append(Finding(finance_path, "missing foreign-turnkey comparator"))

        if slug in REVIEWED_CITY_SLUGS and slug not in FULL_ACCEPTANCE_CITY_SLUGS:
            technology = design.get("costs", {}).get("technology_basis", {})
            if not technology:
                findings.append(Finding(design_path, "missing RFC 0021 800 V cost basis"))
            else:
                expected_cabinets = {
                    "metro-4car": 3,
                    "metro-6car": 4,
                }.get(_family(design), 1)
                if int(technology.get("station_charging_cabinet_count", 0)) != expected_cabinets:
                    findings.append(
                        Finding(
                            design_path,
                            "station charging-module count does not match the rolling-stock family",
                        )
                    )

        if slug in FULL_ACCEPTANCE_CITY_SLUGS:
            technology = design.get("costs", {}).get("technology_basis", {})
            expected_car_count = FAMILY_CAR_COUNT.get(_family(design), 0)
            if not technology:
                findings.append(Finding(design_path, "missing RFC 0021 800 V cost basis"))
            else:
                if "650-700 V" not in str(technology.get("onboard_architecture", "")):
                    findings.append(Finding(design_path, "onboard cost basis is not the 650-700 V nominal architecture"))
                if int(technology.get("car_count", 0)) != expected_car_count:
                    findings.append(Finding(design_path, "800 V cost-basis car count does not match rolling-stock family"))
                if float(technology.get("gross_battery_kwh_per_car", 0)) != 225.0:
                    findings.append(Finding(design_path, "800 V cost basis must allocate 225 gross kWh per car"))
                expected_core = (
                    float(technology.get("core_electrical_usd_per_car", 0))
                    * expected_car_count
                )
                if not _almost_equal(
                    expected_core,
                    float(technology.get("core_electrical_usd_per_trainset", 0)),
                ):
                    findings.append(Finding(design_path, "800 V trainset core-electrical subtotal does not reconcile"))
                if expected_core >= TRAINSET_COST_USD.get(_family(design), 0):
                    findings.append(Finding(design_path, "800 V core electrical exceeds delivered trainset planning unit"))
                if float(technology.get("station_equipment_total_usd", 0)) != 65_000.0:
                    findings.append(Finding(design_path, "500 kWh / 500 kW station equipment basis is not $65k"))
                if float(technology.get("normal_integrated_charging_site_usd", 0)) != 100_000.0:
                    findings.append(Finding(design_path, "normal integrated charging-site planning unit is not $100k"))
                expected_cabinets = {
                    "metro-4car": 3,
                    "metro-6car": 4,
                }.get(_family(design), 1)
                if int(technology.get("station_charging_cabinet_count", 0)) != expected_cabinets:
                    findings.append(
                        Finding(
                            design_path,
                            "station charging-module count does not match the rolling-stock family",
                        )
                    )

            required_acceptance = [
                city_dir / "engineering/alignment/README.md",
                city_dir / "engineering/energy/summary.json",
                city_dir / "engineering/finance/summary.json",
                city_dir / "engineering/gis/summary.json",
                city_dir / "engineering/ring-interchange-summary.json",
                city_dir / "engineering/station-cluster-summary.json",
                city_dir / "engineering/station-product-map.json",
                city_dir / "engineering/screenshots/manifest.json",
                city_dir / "engineering/screenshots" / f"{slug}-network-visualizer.png",
                city_dir / "engineering/screenshots" / f"{slug}-simulation-dashboard.png",
                city_dir / "engineering/simulation/validation-summary.json",
                city_dir / "engineering/sumo/summary.json",
                city_dir / "operations/acceptance-evidence-report.md",
                city_dir / "operations" / f"{slug}-operations-manifest.json",
                city_dir / "package-manifest.json",
            ]
            for line in design.get("lines", []):
                line_id = str(line.get("id") or line.get("name")).replace("-", "")
                required_acceptance.append(
                    city_dir / "engineering/alignment" / f"{slug}-{line_id}.aln.toml"
                )
            for path in required_acceptance:
                if not path.is_file():
                    findings.append(Finding(path, "missing full acceptance-reference artifact"))

            binary_acceptance_suffixes = {".gz", ".gpkg", ".png"}
            local_path_pattern = re.compile(
                r"(?:/home/[^/]+/|/Users/[^/]+/|/tmp/|[A-Za-z]:[\\/](?:Users|Temp)[\\/])"
            )
            for evidence_root in (city_dir / "engineering", city_dir / "operations"):
                if not evidence_root.is_dir():
                    continue
                for path in evidence_root.rglob("*"):
                    if not path.is_file() or path.suffix.lower() in binary_acceptance_suffixes:
                        continue
                    if local_path_pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
                        findings.append(
                            Finding(path, "acceptance-reference artifact contains an absolute local path")
                        )

            for relative in (
                "engineering/energy/summary.json",
                "engineering/finance/summary.json",
                "engineering/ring-interchange-summary.json",
                "engineering/station-cluster-summary.json",
                "engineering/station-product-map.json",
                "engineering/screenshots/manifest.json",
                "engineering/simulation/validation-summary.json",
                "engineering/sumo/summary.json",
            ):
                path = city_dir / relative
                if path.is_file() and not json.loads(path.read_text()).get("passed", False):
                    findings.append(Finding(path, "acceptance-reference analysis is not passed"))

            simulation_path = city_dir / "engineering/simulation/validation-summary.json"
            if simulation_path.is_file():
                simulation = json.loads(simulation_path.read_text())
                if not simulation.get("resilience_required") or not simulation.get("resilience_passed"):
                    findings.append(Finding(simulation_path, "default resilience suite is not passed"))
                if simulation.get("design_sha256") != hashlib.sha256(design_path.read_bytes()).hexdigest():
                    findings.append(Finding(simulation_path, "simulation design hash is stale"))
                if simulation.get("scenario_sha256") != hashlib.sha256(scenario_path.read_bytes()).hexdigest():
                    findings.append(Finding(simulation_path, "simulation scenario hash is stale"))
                if simulation.get("generator_sha256") != hashlib.sha256(
                    (REPO_ROOT / "scripts/validate-city-simulation.py").read_bytes()
                ).hexdigest():
                    findings.append(Finding(simulation_path, "simulation validator hash is stale"))

            package_manifest_path = city_dir / "package-manifest.json"
            if package_manifest_path.is_file():
                package_manifest = json.loads(package_manifest_path.read_text())
                if not package_manifest.get("passed"):
                    findings.append(Finding(package_manifest_path, "city package manifest is not passed"))
                manifest_generator = REPO_ROOT / "scripts/generate-city-package-manifest.py"
                if package_manifest.get("generator_sha256") != hashlib.sha256(
                    manifest_generator.read_bytes()
                ).hexdigest():
                    findings.append(Finding(package_manifest_path, "city package generator hash is stale"))
                for relative, record in package_manifest.get("artifacts", {}).items():
                    artifact = city_dir / relative
                    if not artifact.is_file():
                        findings.append(Finding(artifact, "manifested city-package artifact is missing"))
                    elif record.get("sha256") != hashlib.sha256(artifact.read_bytes()).hexdigest():
                        findings.append(Finding(artifact, "city-package artifact hash is stale"))

            manifest_path = city_dir / "operations" / f"{slug}-operations-manifest.json"
            bundle_path = city_dir / "operations" / f"{slug}-operations.json.gz"
            if manifest_path.is_file() and bundle_path.is_file():
                manifest = json.loads(manifest_path.read_text())
                if manifest.get("compressed_sha256") != hashlib.sha256(bundle_path.read_bytes()).hexdigest():
                    findings.append(Finding(manifest_path, "operations bundle hash is stale"))

    try:
        ring_report = json.loads(RING_INTERCHANGE_REPORT.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(Finding(RING_INTERCHANGE_REPORT, f"missing or invalid report: {exc}"))
        return findings
    ring_results = {str(result.get("city")): result for result in ring_report.get("results", [])}
    if set(ring_results) != expected_slugs:
        findings.append(Finding(RING_INTERCHANGE_REPORT, "ring report city coverage is stale"))
    validator_hash = hashlib.sha256(RING_INTERCHANGE_VALIDATOR.read_bytes()).hexdigest()
    for design_path in design_paths:
        design = _load_toml(design_path)
        slug = str(design.get("city", {}).get("slug", ""))
        result = ring_results.get(slug)
        if result is None:
            continue
        corridor_path = design_path.parent / f"{slug}.corridor.geojson"
        if result.get("design_sha256") != hashlib.sha256(design_path.read_bytes()).hexdigest():
            findings.append(Finding(RING_INTERCHANGE_REPORT, f"stale design hash for {slug}"))
        if result.get("corridor_sha256") != hashlib.sha256(corridor_path.read_bytes()).hexdigest():
            findings.append(Finding(RING_INTERCHANGE_REPORT, f"stale corridor hash for {slug}"))
        if result.get("generator_sha256") != validator_hash:
            findings.append(Finding(RING_INTERCHANGE_REPORT, f"stale validator hash for {slug}"))
        if slug in REVIEWED_CITY_SLUGS and not result.get("passed", False):
            findings.append(Finding(design_path, "reviewed city fails ring-interchange validation"))
    failed_cities = [
        result.get("city") for result in ring_report.get("results", []) if not result.get("passed", False)
    ]
    review_count = sum(
        len(result.get("review_findings", [])) for result in ring_report.get("results", [])
    )
    if ring_report.get("failed_cities") != failed_cities:
        findings.append(Finding(RING_INTERCHANGE_REPORT, "failed_cities does not match results"))
    if ring_report.get("passed") != (not failed_cities):
        findings.append(Finding(RING_INTERCHANGE_REPORT, "passed flag does not match results"))
    if ring_report.get("review_finding_count") != review_count:
        findings.append(Finding(RING_INTERCHANGE_REPORT, "review_finding_count does not match results"))
    return findings


def check_city_costs() -> list[Finding]:
    findings: list[Finding] = []
    for design_path in sorted((REPO_ROOT / "designs").glob("*/*/*/design.toml")):
        design = _load_toml(design_path)
        costs = design.get("costs")
        if not costs:
            findings.append(Finding(design_path, "missing [costs] block"))
            continue
        schema = design.get("schema", {})
        if int(schema.get("version", 0)) < 2:
            findings.append(Finding(design_path, "missing [schema] version = 2"))

        civil = (
            int(costs.get("at_grade_eur", 0))
            + int(costs.get("elevated_eur", 0))
            + int(costs.get("bridge_eur", 0))
            + int(costs.get("junction_premium_eur", 0))
        )
        if not _almost_equal(civil, float(costs.get("civil_subtotal_eur", 0))):
            findings.append(Finding(design_path, "civil_subtotal_eur does not equal civil component sum"))

        family = _family(design)
        if family == "<mixed>":
            findings.append(Finding(design_path, "mixed rolling_stock families are not supported by health check"))
        else:
            expected_rolling = (
                _fleet_total(design)
                * TRAINSET_COST_USD.get(family, TRAINSET_COST_USD["light-metro-3car"])
                * USD_TO_EUR
            )
            if not _almost_equal(expected_rolling, float(costs.get("rolling_stock_eur", 0))):
                findings.append(Finding(design_path, "rolling_stock_eur does not match local-owner trainset family cost"))
            if not _almost_equal(0.0, float(costs.get("production_plant_eur", 0))):
                findings.append(Finding(
                    design_path,
                    "production_plant_eur must be zero; the factory is a shared national asset",
                ))

        # osr-design computes signalling from emitted civil segment length.
        # The line headline length can differ slightly after station/segment
        # rounding, so keep this check tight but not single-metre brittle.
        expected_signalling = round(_route_km(design) * SIGNALLING_EUR_PER_KM)
        signalling_tolerance = max(2.0, expected_signalling * 0.05)
        if not _almost_equal(
            expected_signalling,
            float(costs.get("signalling_eur", 0)),
            tolerance=signalling_tolerance,
        ):
            findings.append(Finding(
                design_path,
                "signalling_eur does not match residual wayside rate converted to EUR",
            ))

        expected_charging = _charging_microgrid_total(design)
        actual_charging = float(costs.get("charging_microgrid_eur", 0))
        if not _almost_equal(expected_charging, actual_charging):
            findings.append(Finding(design_path, "charging_microgrid_eur does not match station/depot charging microgrid total"))

        pre_epc = (
            civil
            + int(costs.get("stations_eur", 0))
            + int(costs.get("depots_eur", 0))
            + int(costs.get("rolling_stock_eur", 0))
            + int(costs.get("production_plant_eur", 0))
            + int(costs.get("signalling_eur", 0))
            + int(round(actual_charging))
        )
        expected_epc = round(pre_epc * EPC_OVERHEAD_FRAC)
        expected_total = pre_epc + expected_epc
        if not _almost_equal(expected_epc, float(costs.get("epc_overhead_eur", 0))):
            findings.append(Finding(design_path, "epc_overhead_eur does not equal 7% of subtotal"))
        if not _almost_equal(expected_total, float(costs.get("total_eur", 0))):
            findings.append(Finding(design_path, "total_eur does not equal subtotal + EPC overhead"))

        for stem in (
            "at_grade",
            "elevated",
            "bridge",
            "junction_premium",
            "civil_subtotal",
            "stations",
            "depots",
            "rolling_stock",
            "production_plant",
            "signalling",
            "charging_microgrid",
            "epc_overhead",
            "total",
        ):
            _check_usd_mirror(findings, design_path, costs, stem)
    return findings


def check_procurement_origin() -> list[Finding]:
    findings: list[Finding] = []
    imported = {
        str(key): float(value)
        for key, value in CAPEX_COSTS["procurement_origin"]["imported_share"].items()
    }
    benefits = _load_toml(REPO_ROOT / "lib/templates/economic-benefits.toml")
    local = benefits["local_recirculation"]["capex_local_share"]
    for bucket, imported_share in imported.items():
        if not 0.0 <= imported_share <= 1.0:
            findings.append(Finding(
                REPO_ROOT / "lib/templates/capex-costs.toml",
                f"{bucket} imported share is outside 0..1",
            ))
        local_share = float(local.get(bucket, -1.0))
        if not _almost_equal(imported_share + local_share, 1.0, 1e-9):
            findings.append(Finding(
                REPO_ROOT / "lib/templates/economic-benefits.toml",
                f"{bucket} local share is not one minus the canonical imported share",
            ))
    comparator = CAPEX_COSTS.get("foreign_turnkey_comparator", {})
    external_share = float(comparator.get("external_capital_share", -1.0))
    multipliers = comparator.get("cost_multiplier", {})
    ordered = [float(multipliers.get(case, -1.0)) for case in ("low", "default", "high")]
    if not 0.0 <= external_share <= 1.0:
        findings.append(Finding(
            REPO_ROOT / "lib/templates/capex-costs.toml",
            "foreign-turnkey external-capital share is outside 0..1",
        ))
    if ordered[0] < 1.0 or not ordered[0] <= ordered[1] <= ordered[2]:
        findings.append(Finding(
            REPO_ROOT / "lib/templates/capex-costs.toml",
            "foreign-turnkey multipliers must satisfy 1 <= low <= default <= high",
        ))
    return findings


def check_national_briefs() -> list[Finding]:
    generator = REPO_ROOT / "scripts/generate-national-briefs.py"
    completed = subprocess.run(
        [sys.executable, str(generator), "--check"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode:
        return [Finding(generator, completed.stdout.strip() or "national briefs are stale")]
    return []


def check_station_clusters() -> list[Finding]:
    """Bind the known catalogue backlog to source hashes and gate reviewed cities."""

    spec = importlib.util.spec_from_file_location(
        "osr_validate_station_clusters", STATION_CLUSTER_VALIDATOR
    )
    if spec is None or spec.loader is None:
        return [Finding(STATION_CLUSTER_VALIDATOR, "could not load station-cluster validator")]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    findings: list[Finding] = []
    design_paths = sorted((REPO_ROOT / "designs").glob("*/*/*/design.toml"))
    results = [module.validate(design_path) for design_path in design_paths]
    report_results = [
        module._report_result(result, include_review_findings=False)
        for result in results
    ]
    expected_report = {
        "city_count": len(report_results),
        "failed_cities": [result["city"] for result in report_results if not result["passed"]],
        "failure_count": sum(len(result["failures"]) for result in report_results),
        "passed": all(result["passed"] for result in report_results),
        "results": report_results,
        "review_finding_count": sum(result["review_finding_count"] for result in report_results),
    }
    try:
        actual_report = json.loads(STATION_CLUSTER_REPORT.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(Finding(STATION_CLUSTER_REPORT, f"missing or invalid report: {exc}"))
        actual_report = None
    if actual_report != expected_report:
        findings.append(Finding(
            STATION_CLUSTER_REPORT,
            "report is stale; run scripts/validate-station-clusters.py --all",
        ))
    path_by_slug = {
        str(_load_toml(path).get("city", {}).get("slug", "")): path for path in design_paths
    }
    for result in results:
        if result["city"] not in REVIEWED_CITY_SLUGS:
            continue
        for failure in result["failures"]:
            findings.append(Finding(
                path_by_slug[result["city"]],
                f"reviewed city fails station clustering: {failure['code']}",
            ))
    return findings


def check_stale_terms() -> list[Finding]:
    findings: list[Finding] = []
    roots = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs",
        REPO_ROOT / "lib",
        REPO_ROOT / "crates",
        REPO_ROOT / "design-py" / "src",
        REPO_ROOT / "mechanical-py" / "src",
    ]
    patterns = {
        r"\b4 trainset families\b": "rolling-stock catalogue now has five families",
        r"\b360 kWh/trainset\b": "3-car battery basis is now 540 kWh/trainset",
        r"\b240 kWh battery\b": "tram battery basis is now 300 kWh",
        r"€0\.8 M/km": "charging microgrids are costed per stop, not per route-km",
        r"marketplace-BOM rolling stock": "city CAPEX rolling-stock cost must use trainset-family local-owner units",
        r"\$\d+(?:\.\d+)?\s*(?:M|k) per self-contained car": "city CAPEX rolling-stock cost is now trainset-family based",
        r"outside the city CAPEX": "QA and acceptance remain in train CAPEX; warranty, spares, and routine commissioning support are OPEX",
        r"\bTraction power\s*\(": "use station/depot charging microgrids or onboard motor output",
        r"car-body-22m": "car-body artifact name should match the promoted 16.5 m module",
        r"Secondary coil spring": "rolling-stock secondary suspension is twin-bellows air spring",
        r"\bno air spring\b": "rolling-stock secondary suspension is twin-bellows air spring",
        r"\b3\.8:1 ratio\b": "rolling-stock reduction gear ratio is 6.5:1",
        r"single-stage 3\.8:1": "rolling-stock reduction gear ratio is 6.5:1",
        r"hydraulic piston": "rolling-stock brake actuator is electromagnetic",
        r"\bbrake-release line\b": "rolling-stock brake has no pneumatic/hydraulic release line",
        r"one T-ECU/A per trainset": "standard trainset fit carries two T-ECU/A units",
    }
    text_suffixes = {".md", ".py", ".rs", ".toml", ".yaml", ".yml", ".txt"}

    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.exists():
            files.extend(p for p in root.rglob("*") if p.is_file() and p.suffix in text_suffixes)

    for path in files:
        text = path.read_text(errors="ignore")
        for pattern, message in patterns.items():
            if re.search(pattern, text):
                findings.append(Finding(path, message))
    return findings


def check_rolling_stock_bom() -> list[Finding]:
    module = runpy.run_path(str(BOM_EXPORTER))
    # Rendering validates the source schema without requiring build output in Git.
    module["render_csv"](BOM_SOURCE)
    return check_rolling_stock_bom_markdown_summaries(module)


def check_rolling_stock_bom_markdown_summaries(module: dict) -> list[Finding]:
    findings: list[Finding] = []
    rows = module["export_rows"](BOM_SOURCE)
    bucket_totals: dict[str, int] = defaultdict(int)
    for row in rows:
        bucket_totals[str(row["bucket"])] += int(row["base_usd"])

    low_direct = sum(int(row["cost_low_usd"]) for row in rows)
    base_direct = sum(int(row["base_usd"]) for row in rows)
    high_direct = sum(int(row["cost_high_usd"]) for row in rows)
    expected_bands = {
        "Low": (low_direct, round(low_direct * ROLLING_STOCK_ASSEMBLY_FRACTION), low_direct + round(low_direct * ROLLING_STOCK_ASSEMBLY_FRACTION)),
        "Base": (base_direct, round(base_direct * ROLLING_STOCK_ASSEMBLY_FRACTION), base_direct + round(base_direct * ROLLING_STOCK_ASSEMBLY_FRACTION)),
        "High": (high_direct, round(high_direct * ROLLING_STOCK_ASSEMBLY_FRACTION), high_direct + round(high_direct * ROLLING_STOCK_ASSEMBLY_FRACTION)),
    }

    seen_buckets: set[str] = set()
    seen_bands: set[str] = set()
    total_direct_seen = False
    for raw in BOM_SOURCE.read_text().splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = _markdown_cells(line)
        if not cells:
            continue
        label = cells[0].replace("*", "").strip()
        if label in bucket_totals and len(cells) >= 2:
            actual = _markdown_money(cells[1])
            expected = bucket_totals[label]
            seen_buckets.add(label)
            if actual != expected:
                findings.append(Finding(BOM_SOURCE, f"BOM bucket subtotal for {label!r} should be {expected}"))
        if label == "Total direct-material consist" and len(cells) >= 2:
            total_direct_seen = True
            actual = _markdown_money(cells[1])
            if actual != base_direct:
                findings.append(Finding(BOM_SOURCE, f"BOM direct-material total should be {base_direct}"))
        if label in expected_bands and len(cells) >= 4:
            seen_bands.add(label)
            actual = tuple(_markdown_money(cell) for cell in cells[1:4])
            if actual != expected_bands[label]:
                findings.append(Finding(BOM_SOURCE, f"BOM {label.lower()} cost band should be {expected_bands[label]}"))

    missing_buckets = sorted(set(bucket_totals) - seen_buckets)
    for bucket in missing_buckets:
        findings.append(Finding(BOM_SOURCE, f"missing BOM subtotal row for {bucket!r}"))
    if not total_direct_seen:
        findings.append(Finding(BOM_SOURCE, "missing total direct-material consist row"))
    for case in sorted(set(expected_bands) - seen_bands):
        findings.append(Finding(BOM_SOURCE, f"missing generated cost-band row for {case!r}"))
    return findings


def check_station_build_package() -> list[Finding]:
    """Regenerate the tracked station catalogue in a temp tree and compare."""

    findings: list[Finding] = []
    mech_src = REPO_ROOT / "mechanical-py/src"
    if str(mech_src) not in sys.path:
        sys.path.insert(0, str(mech_src))
    from osr_mech.buildable_stations import write_outputs

    with tempfile.TemporaryDirectory(prefix="osr-station-check-") as tmp:
        root = Path(tmp)
        expected_catalog = root / "catalog"
        expected_boms = root / "bom"
        write_outputs(catalog_dir=expected_catalog, bom_dir=expected_boms)
        for expected_root, actual_root in ((expected_catalog, STATION_CATALOG),):
            expected_files = {
                path.relative_to(expected_root): path
                for path in expected_root.rglob("*")
                if path.is_file()
            }
            actual_files = {
                path.relative_to(actual_root): path
                for path in actual_root.rglob("*")
                if path.is_file()
            } if actual_root.exists() else {}
            for relative in sorted(expected_files.keys() | actual_files.keys()):
                actual = actual_files.get(relative)
                expected = expected_files.get(relative)
                if actual is None:
                    findings.append(Finding(actual_root / relative, "missing generated station artifact"))
                elif expected is None:
                    findings.append(Finding(actual, "unexpected generated station artifact"))
                elif actual.read_bytes() != expected.read_bytes():
                    findings.append(
                        Finding(actual, "generated station artifact is stale; run scripts/buildable-stations.sh")
                    )
    return findings


def check_current_network_osr_aln() -> list[Finding]:
    """Regenerate the current Samawah OSR-ALN package and compare in place."""

    tool_src = REPO_ROOT / "tools/osr-aln-convert/src"
    if str(tool_src) not in sys.path:
        sys.path.insert(0, str(tool_src))
    from osr_aln.current_network import export_network

    try:
        export_network(
            SAMAWAH_DESIGN_DIR / "design.toml",
            SAMAWAH_DESIGN_DIR / "samawah.corridor.geojson",
            SAMAWAH_ALN_DIR,
            design_date=SAMAWAH_ALN_DESIGN_DATE,
            check=True,
        )
    except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError) as error:
        return [Finding(SAMAWAH_ALN_DIR, str(error))]
    return []


def check_generated_cost_model() -> list[Finding]:
    findings: list[Finding] = []
    civil_generator = REPO_ROOT / "scripts/generate-civil-cost-model.py"
    civil_module = runpy.run_path(str(civil_generator))
    expected_civil = civil_module["render"](civil_module["build_model"]())
    civil_path = REPO_ROOT / "lib/templates/civil-cost-model.toml"
    if civil_path.read_text() != expected_civil:
        findings.append(
            Finding(
                civil_path,
                "generated civil cost contract is stale; run scripts/generate-civil-cost-model.py",
            )
        )
    path = REPO_ROOT / "docs/cost-model.md"
    generator = REPO_ROOT / "scripts/generate-cost-model.py"
    module = runpy.run_path(str(generator))
    expected = module["render_cost_model"]()
    actual = path.read_text()
    if actual != expected:
        findings.append(Finding(path, "generated cost model is stale; run scripts/generate-cost-model.py"))
    return findings


def check_generated_portfolio_summary() -> list[Finding]:
    path = REPO_ROOT / "docs/portfolio-summary.md"
    generator = REPO_ROOT / "scripts/generate-portfolio-summary.py"
    module = runpy.run_path(str(generator))
    expected = module["build_summary"]()
    if not path.is_file() or path.read_text() != expected:
        return [
            Finding(
                path,
                "generated portfolio summary is stale; run scripts/generate-portfolio-summary.py",
            )
        ]
    return []


def check_cost_reference_tables() -> list[Finding]:
    findings: list[Finding] = []
    light_unit = TRAINSET_COST_USD["light-metro-3car"]
    plant_base = PRODUCTION_PLANT_PER_VEHICLE_USD
    plant_high = float(CAPEX_COSTS["production_plant"]["high_sensitivity_per_vehicle_usd"])

    readme = REPO_ROOT / "README.md"
    readme_text = readme.read_text()
    _require_text(
        findings,
        readme,
        readme_text,
        f"about **{_compact_million_money(light_unit)} per 3-car light-metro trainset**",
        "README rolling-stock headline is out of sync with capex-costs.toml",
    )
    _require_text(
        findings,
        readme,
        readme_text,
        f"**{_compact_money(plant_base)} per supported vehicle/car module**",
        "README production-plant headline is out of sync with capex-costs.toml",
    )

    rfc = REPO_ROOT / "docs/rfcs/0011-civil-infrastructure-design-standard.md"
    rfc_text = rfc.read_text()
    for key, value in CAPEX_COSTS["civil_benchmark_usd_per_km"].items():
        label = key.replace("_", "-")
        _require_text(findings, rfc, rfc_text, f"| {label} | {_space_int(float(value))} / route-km |", "RFC 0011 civil unit table is stale")
    _require_text(
        findings,
        rfc,
        rfc_text,
        f"| elevated-interchange premium | {_space_int(float(CAPEX_COSTS['junctions']['elevated_interchange_premium_usd']))} / site |",
        "RFC 0011 junction premium table is stale",
    )
    for key, value in CAPEX_COSTS["station_unit_usd"].items():
        _require_text(findings, rfc, rfc_text, f"| `{key}` | {_space_int(float(value))} |", "RFC 0011 station unit table is stale")
    for key, value in CAPEX_COSTS["depot_unit_usd"].items():
        _require_text(findings, rfc, rfc_text, f"| `{key}` | {_space_int(float(value))} |", "RFC 0011 depot unit table is stale")
    for key, value in TRAINSET_COST_USD.items():
        _require_text(findings, rfc, rfc_text, f"| `{key}` | {_space_int(value)} |", "RFC 0011 trainset unit table is stale")
    _require_text(findings, rfc, rfc_text, f"| Base local plant setup | {_space_int(plant_base)} USD / vehicle-car module |", "RFC 0011 production-plant base is stale")
    _require_text(findings, rfc, rfc_text, f"| High sensitivity check | {_space_int(plant_high)} USD / vehicle-car module |", "RFC 0011 production-plant high case is stale")
    _require_text(
        findings,
        rfc,
        rfc_text,
        f"| Residual train-control wayside (RFC 0015 GoA 4) | {_space_int(float(CAPEX_COSTS['systems']['signalling_usd_per_km']))} USD / route-km |",
        "RFC 0011 residual wayside rate is stale",
    )

    civil = REPO_ROOT / "docs/civil/marketplace-cost-anchors.md"
    civil_text = civil.read_text()
    _require_text(
        findings,
        civil,
        civil_text,
        f"Base unit: **{int(CAPEX_COSTS['civil_benchmark_usd_per_km']['at_grade']):,} USD per route-km**.",
        "civil marketplace at-grade anchor is stale",
    )
    for value in CAPEX_COSTS["station_unit_usd"].values():
        _require_text(findings, civil, civil_text, _marketplace_cost_anchor_value(float(value)), "civil marketplace station table is stale")
    for value in CAPEX_COSTS["depot_unit_usd"].values():
        _require_text(findings, civil, civil_text, _marketplace_cost_anchor_value(float(value)), "civil marketplace depot table is stale")
    for value in CAPEX_COSTS["charging_microgrid_unit_usd"].values():
        _require_text(findings, civil, civil_text, _marketplace_cost_anchor_value(float(value)), "civil marketplace charging table is stale")

    return findings


def _marketplace_cost_anchor_value(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f} M USD"
    return f"{value / 1_000:.0f} k USD"


def check_repository_hygiene() -> list[Finding]:
    """Check repository-wide release metadata and tracked-file policy."""

    findings: list[Finding] = []
    required = (
        REPO_ROOT / "LICENSE.md",
        REPO_ROOT / "LICENSES" / "Apache-2.0.txt",
        REPO_ROOT / "LICENSES" / "CERN-OHL-S-2.0.txt",
        REPO_ROOT / "LICENSES" / "CC-BY-SA-4.0.txt",
        REPO_ROOT / ".github" / "workflows" / "ci.yml",
        REPO_ROOT / "docs" / "repository-artifact-policy.md",
    )
    for path in required:
        if not path.exists():
            findings.append(Finding(path, "missing repository release-control artifact"))

    tracked = subprocess.check_output(
        ["git", "ls-files"], cwd=REPO_ROOT, text=True
    ).splitlines()
    for relative in tracked:
        path = Path(relative)
        if ".cache" in path.parts:
            findings.append(Finding(REPO_ROOT / path, "cache file must not be tracked"))
        if path.parts[:2] == ("build", "doc-book-assets"):
            findings.append(Finding(REPO_ROOT / path, "doc-book intermediate must not be tracked"))
        if path.name == "spooles.out" and (REPO_ROOT / path).stat().st_size == 0:
            findings.append(Finding(REPO_ROOT / path, "empty solver scratch file must not be tracked"))

    # Build this from fragments so the health checker does not match itself.
    stale_url = "github.com/" + "OpenSourceRail/OpenSourceRail"
    stale_paths = subprocess.run(
        ["git", "grep", "-Il", stale_url, "--", "."],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if stale_paths.returncode not in (0, 1):
        findings.append(Finding(REPO_ROOT, "could not scan tracked files for stale repository URLs"))
    else:
        for relative in stale_paths.stdout.splitlines():
            findings.append(Finding(REPO_ROOT / relative, "stale non-canonical repository URL"))
    return findings


def check_readme_corpus() -> list[Finding]:
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/check-readmes.py")],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        message = (completed.stdout + completed.stderr).strip()
        return [Finding(REPO_ROOT, message)]
    return []


def run_checks() -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_city_artifacts())
    findings.extend(check_city_costs())
    findings.extend(check_procurement_origin())
    findings.extend(check_national_briefs())
    findings.extend(check_station_clusters())
    findings.extend(check_stale_terms())
    findings.extend(check_rolling_stock_bom())
    findings.extend(check_station_build_package())
    findings.extend(check_current_network_osr_aln())
    findings.extend(check_generated_cost_model())
    findings.extend(check_generated_portfolio_summary())
    findings.extend(check_cost_reference_tables())
    findings.extend(check_readme_corpus())
    findings.extend(check_repository_hygiene())
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OSR generated artifacts and concept invariants.")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    args = parser.parse_args(argv)

    findings = run_checks()
    if findings:
        print(f"repo-health: {len(findings)} finding(s)", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding.render()}", file=sys.stderr)
        return 1
    if not args.quiet:
        city_count = len(list((REPO_ROOT / "designs").glob("*/*/*/design.toml")))
        print(f"repo-health: ok ({city_count} city designs checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
