#!/usr/bin/env python3
"""Repository health checks for OSR source and compact reference fixtures.

The checks here are deliberately boring: they catch drift between the
current concept, the generated city artefacts, and the CAPEX formulas.
Run from the repository root:

    python3 tools/automation/repo-health.py
"""

from __future__ import annotations

import argparse
import csv
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

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[2]
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
BOM_EXPORTER = REPO_ROOT / "tools/automation/export-light-metro-bom.py"
STATION_CATALOG = REPO_ROOT / "design/component-catalogue/catalog/buildable-stations"
SAMAWAH_DESIGN_DIR = REPO_ROOT / "cities/catalogue/west-asia/Iraq/Samawah"
SAMAWAH_ALN_DIR = SAMAWAH_DESIGN_DIR / "engineering/alignment"
SAMAWAH_ALN_DESIGN_DATE = "2026-08-12"
STATION_CLUSTER_VALIDATOR = REPO_ROOT / "tools/automation/validate-station-clusters.py"
STATION_CLUSTER_REPORT = REPO_ROOT / "cities/catalogue/station-cluster-validation.json"
RING_INTERCHANGE_VALIDATOR = REPO_ROOT / "tools/automation/validate-ring-interchanges.py"
RING_INTERCHANGE_REPORT = REPO_ROOT / "cities/catalogue/ring-interchange-validation.json"
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
    design_paths = sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml"))
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
            REPO_ROOT / "cities/catalogue",
            f"committed city core differs from source catalogue; missing={sorted(expected_slugs - actual_slugs)}, "
            f"unexpected={sorted(actual_slugs - expected_slugs)}",
        ))

    for design_path in design_paths:
        city_dir = design_path.parent
        design = _load_toml(design_path)
        slug = str(design.get("city", {}).get("slug", city_dir.name.lower().replace(" ", "-")))
        actual_continent = design_path.relative_to(REPO_ROOT / "cities/catalogue").parts[0]
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
            if "| Charging microgrids |" not in text:
                findings.append(Finding(readme, "missing station/depot charging microgrid cost row"))
            if "[deployment planning reference]" not in text:
                findings.append(Finding(readme, "missing canonical common-planning reference"))
            if "Imported / external capital" not in text:
                findings.append(Finding(readme, "missing imported/external capital requirement"))
            if "External capital saved vs default turnkey sensitivity" not in text:
                findings.append(Finding(readme, "missing foreign-turnkey capital comparison"))
            if actual_continent != "europe":
                if "> **Foreign-capital advantage:**" not in text:
                    findings.append(Finding(readme, "missing headline foreign-capital advantage"))
                if "Capital plus saved interest totals" not in text:
                    findings.append(Finding(readme, "missing lifetime capital-and-interest saving"))
            elif "Technical comparison only" not in text:
                findings.append(Finding(readme, "comparison-only scope is not explicit"))
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
                "generator_sha256": REPO_ROOT / "tools/automation/generate-city-finance.py",
                "capital_model_sha256": REPO_ROOT
                / "design/city-generation/src/osr_scenario/capital.py",
                "network_finance_model_sha256": REPO_ROOT
                / "design/city-generation/src/osr_scenario/network_readme.py",
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
                city_dir / "engineering/project-twin/summary.json",
                city_dir / "engineering/gis/summary.json",
                city_dir / "engineering/ring-interchange-summary.json",
                city_dir / "engineering/station-cluster-summary.json",
                city_dir / "engineering/station-product-map.json",
                city_dir / "engineering/screenshots/manifest.json",
                city_dir / "engineering/screenshots" / f"{slug}-network-visualizer.png",
                city_dir / "engineering/screenshots" / f"{slug}-simulation-dashboard.png",
                city_dir / "engineering/survey/field-evidence-brief.json",
                city_dir / "engineering/survey/field-evidence-brief.md",
                city_dir / "engineering/survey/survey-input-manifest.csv",
                city_dir / "engineering/survey/control-processing-readiness.json",
                city_dir / "engineering/survey/control-processing-readiness.md",
                city_dir / "engineering/survey/ground-model-readiness.json",
                city_dir / "engineering/survey/ground-model-readiness.md",
                city_dir / "engineering/survey/surveyed-alignment-input-manifest.csv",
                city_dir / "engineering/survey/surveyed-alignment-readiness.json",
                city_dir / "engineering/survey/surveyed-alignment-readiness.md",
                city_dir / "engineering/survey/route-station-fit-input-manifest.csv",
                city_dir / "engineering/survey/route-station-fit-readiness.json",
                city_dir / "engineering/survey/route-station-fit-readiness.md",
                city_dir / "engineering/survey/drainage-ground-input-manifest.csv",
                city_dir / "engineering/survey/drainage-ground-readiness.json",
                city_dir / "engineering/survey/drainage-ground-readiness.md",
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
                    (REPO_ROOT / "tools/automation/validate-city-simulation.py").read_bytes()
                ).hexdigest():
                    findings.append(Finding(simulation_path, "simulation validator hash is stale"))
                trainset_contract = simulation.get("trainset_contract", {})
                for key, relative in (
                    ("rolling_stock_template_sha256", "lib/templates/rolling-stock.toml"),
                    (
                        "small_component_standard_sha256",
                        "design/component-catalogue/catalog/buildable-trainset/small-component-standard.json",
                    ),
                    (
                        "buildable_trainset_manifest_sha256",
                        "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json",
                    ),
                ):
                    source = REPO_ROOT / relative
                    if trainset_contract.get(key) != hashlib.sha256(source.read_bytes()).hexdigest():
                        findings.append(
                            Finding(
                                simulation_path,
                                f"simulation trainset contract is stale for {relative}",
                            )
                        )

            survey_brief_path = city_dir / "engineering/survey/field-evidence-brief.json"
            survey_manifest_path = city_dir / "engineering/survey/survey-input-manifest.csv"
            survey_control_path = city_dir / "engineering/survey/control-processing-readiness.json"
            ground_model_path = city_dir / "engineering/survey/ground-model-readiness.json"
            alignment_receipt_path = city_dir / "engineering/survey/surveyed-alignment-input-manifest.csv"
            alignment_gate_path = city_dir / "engineering/survey/surveyed-alignment-readiness.json"
            route_fit_receipt_path = city_dir / "engineering/survey/route-station-fit-input-manifest.csv"
            route_fit_gate_path = city_dir / "engineering/survey/route-station-fit-readiness.json"
            drainage_ground_receipt_path = city_dir / "engineering/survey/drainage-ground-input-manifest.csv"
            drainage_ground_gate_path = city_dir / "engineering/survey/drainage-ground-readiness.json"
            if survey_brief_path.is_file():
                survey = json.loads(survey_brief_path.read_text())
                survey_generator = REPO_ROOT / "engineering/analysis/survey_package.py"
                survey_requirements = REPO_ROOT / "lib/templates/field-evidence.toml"
                expected_design_hash = hashlib.sha256(design_path.read_bytes()).hexdigest()
                if survey.get("generator_sha256") != hashlib.sha256(survey_generator.read_bytes()).hexdigest():
                    findings.append(Finding(survey_brief_path, "field-evidence generator hash is stale"))
                if survey.get("requirements_sha256") != hashlib.sha256(survey_requirements.read_bytes()).hexdigest():
                    findings.append(Finding(survey_brief_path, "field-evidence requirements hash is stale"))
                if survey.get("project_input_sha256") != expected_design_hash:
                    findings.append(Finding(survey_brief_path, "field-evidence design hash is stale"))
                if not survey.get("brief_ready_for_approval") or survey.get("brief_findings"):
                    findings.append(Finding(survey_brief_path, "field-evidence brief is incomplete"))
                if "survey authority to confirm or replace" not in str(survey.get("candidate_horizontal_crs", "")):
                    findings.append(Finding(survey_brief_path, "candidate CRS lacks its approval boundary"))
                if survey_manifest_path.is_file():
                    with survey_manifest_path.open(newline="", encoding="utf-8") as handle:
                        survey_rows = list(csv.DictReader(handle))
                    if {row.get("dataset_id") for row in survey_rows} != {
                        row.get("id") for row in survey.get("datasets", [])
                    }:
                        findings.append(Finding(survey_manifest_path, "survey receipt rows do not match brief datasets"))
                    if "file_role" not in (survey_rows[0] if survey_rows else {}):
                        findings.append(Finding(survey_manifest_path, "survey receipt manifest lacks file_role"))

            if survey_control_path.is_file():
                control = json.loads(survey_control_path.read_text())
                control_generator = REPO_ROOT / "engineering/analysis/survey_control.py"
                control_requirements = REPO_ROOT / "lib/templates/survey-control-processing.toml"
                if control.get("generator_sha256") != hashlib.sha256(control_generator.read_bytes()).hexdigest():
                    findings.append(Finding(survey_control_path, "survey-control generator hash is stale"))
                if control.get("requirements_sha256") != hashlib.sha256(control_requirements.read_bytes()).hexdigest():
                    findings.append(Finding(survey_control_path, "survey-control requirements hash is stale"))
                if control.get("receipt_manifest_sha256") != hashlib.sha256(survey_manifest_path.read_bytes()).hexdigest():
                    findings.append(Finding(survey_control_path, "survey-control receipt hash is stale"))
                if not control.get("report_valid"):
                    findings.append(Finding(survey_control_path, "survey-control receipt is invalid"))
                if control.get("status") == "awaiting-field-data" and (
                    control.get("processing_completed")
                    or control.get("technical_screen_passed")
                    or control.get("authority_accepted")
                ):
                    findings.append(Finding(survey_control_path, "pending control report claims completed gates"))

            if ground_model_path.is_file():
                ground = json.loads(ground_model_path.read_text())
                ground_generator = REPO_ROOT / "engineering/analysis/ground_model.py"
                ground_requirements = REPO_ROOT / "lib/templates/ground-model-processing.toml"
                receipt_validator = REPO_ROOT / "engineering/analysis/survey_control.py"
                if ground.get("generator_sha256") != hashlib.sha256(ground_generator.read_bytes()).hexdigest():
                    findings.append(Finding(ground_model_path, "ground-model generator hash is stale"))
                if ground.get("requirements_sha256") != hashlib.sha256(ground_requirements.read_bytes()).hexdigest():
                    findings.append(Finding(ground_model_path, "ground-model requirements hash is stale"))
                if ground.get("receipt_validator_sha256") != hashlib.sha256(receipt_validator.read_bytes()).hexdigest():
                    findings.append(Finding(ground_model_path, "ground-model receipt validator hash is stale"))
                if ground.get("receipt_manifest_sha256") != hashlib.sha256(survey_manifest_path.read_bytes()).hexdigest():
                    findings.append(Finding(ground_model_path, "ground-model receipt hash is stale"))
                if not ground.get("report_valid"):
                    findings.append(Finding(ground_model_path, "ground-model receipt is invalid"))
                if ground.get("status") == "awaiting-ground-model-data" and (
                    ground.get("technical_screen_passed") or ground.get("authority_accepted")
                ):
                    findings.append(Finding(ground_model_path, "pending ground-model report claims completed gates"))

            if alignment_gate_path.is_file():
                alignment = json.loads(alignment_gate_path.read_text())
                alignment_generator = REPO_ROOT / "engineering/analysis/surveyed_alignment.py"
                alignment_requirements = REPO_ROOT / "lib/templates/surveyed-alignment-processing.toml"
                alignment_validator = REPO_ROOT / "tools/osr-aln-convert/src/osr_aln/validate.py"
                landxml_converter = REPO_ROOT / "tools/osr-aln-convert/src/osr_aln/landxml_to_osr_aln.py"
                expected_lines = [str(line.get("name")) for line in design.get("lines", [])]
                if alignment.get("generator_sha256") != hashlib.sha256(alignment_generator.read_bytes()).hexdigest():
                    findings.append(Finding(alignment_gate_path, "surveyed-alignment generator hash is stale"))
                if alignment.get("requirements_sha256") != hashlib.sha256(alignment_requirements.read_bytes()).hexdigest():
                    findings.append(Finding(alignment_gate_path, "surveyed-alignment requirements hash is stale"))
                if alignment.get("design_sha256") != hashlib.sha256(design_path.read_bytes()).hexdigest():
                    findings.append(Finding(alignment_gate_path, "surveyed-alignment design hash is stale"))
                if alignment.get("receipt_manifest_sha256") != hashlib.sha256(alignment_receipt_path.read_bytes()).hexdigest():
                    findings.append(Finding(alignment_gate_path, "surveyed-alignment receipt hash is stale"))
                if alignment.get("osr_aln_validator_sha256") != hashlib.sha256(alignment_validator.read_bytes()).hexdigest():
                    findings.append(Finding(alignment_gate_path, "surveyed-alignment validator hash is stale"))
                if alignment.get("landxml_converter_sha256") != hashlib.sha256(landxml_converter.read_bytes()).hexdigest():
                    findings.append(Finding(alignment_gate_path, "LandXML converter hash is stale"))
                if alignment.get("line_ids") != expected_lines:
                    findings.append(Finding(alignment_gate_path, "surveyed-alignment line set is stale"))
                if not alignment.get("report_valid"):
                    findings.append(Finding(alignment_gate_path, "surveyed-alignment receipt is invalid"))
                if alignment.get("status") == "awaiting-surveyed-alignments" and (
                    alignment.get("technical_screen_passed") or alignment.get("authority_accepted")
                ):
                    findings.append(Finding(alignment_gate_path, "pending surveyed-alignment report claims completed gates"))

            if route_fit_gate_path.is_file():
                route_fit = json.loads(route_fit_gate_path.read_text())
                route_fit_generator = REPO_ROOT / "engineering/analysis/route_station_fit.py"
                route_fit_requirements = REPO_ROOT / "lib/templates/route-station-fit-processing.toml"
                expected_lines = [str(line.get("name")) for line in design.get("lines", [])]
                expected_stations = [str(station.get("id")) for station in design.get("stations", [])]
                if route_fit.get("generator_sha256") != hashlib.sha256(route_fit_generator.read_bytes()).hexdigest():
                    findings.append(Finding(route_fit_gate_path, "route-fit generator hash is stale"))
                if route_fit.get("requirements_sha256") != hashlib.sha256(route_fit_requirements.read_bytes()).hexdigest():
                    findings.append(Finding(route_fit_gate_path, "route-fit requirements hash is stale"))
                if route_fit.get("design_sha256") != hashlib.sha256(design_path.read_bytes()).hexdigest():
                    findings.append(Finding(route_fit_gate_path, "route-fit design hash is stale"))
                if route_fit.get("receipt_manifest_sha256") != hashlib.sha256(route_fit_receipt_path.read_bytes()).hexdigest():
                    findings.append(Finding(route_fit_gate_path, "route-fit receipt hash is stale"))
                if route_fit.get("line_ids") != expected_lines or route_fit.get("station_ids") != expected_stations:
                    findings.append(Finding(route_fit_gate_path, "route-fit line/station scope is stale"))
                if not route_fit.get("report_valid"):
                    findings.append(Finding(route_fit_gate_path, "route-fit receipt is invalid"))
                if route_fit.get("status") == "awaiting-route-fit-evidence" and (
                    route_fit.get("technical_screen_passed") or route_fit.get("authority_accepted")
                ):
                    findings.append(Finding(route_fit_gate_path, "pending route-fit report claims completed gates"))

            if drainage_ground_gate_path.is_file():
                drainage_ground = json.loads(drainage_ground_gate_path.read_text())
                dg_generator = REPO_ROOT / "engineering/analysis/drainage_ground_design.py"
                dg_requirements = REPO_ROOT / "lib/templates/drainage-ground-design-processing.toml"
                expected_lines = [str(line.get("name")) for line in design.get("lines", [])]
                expected_stations = [str(station.get("id")) for station in design.get("stations", [])]
                for key, source, label in (
                    ("generator_sha256", dg_generator, "generator"),
                    ("requirements_sha256", dg_requirements, "requirements"),
                    ("design_sha256", design_path, "design"),
                    ("receipt_manifest_sha256", drainage_ground_receipt_path, "receipt"),
                ):
                    if drainage_ground.get(key) != hashlib.sha256(source.read_bytes()).hexdigest():
                        findings.append(Finding(drainage_ground_gate_path, f"drainage/ground {label} hash is stale"))
                if drainage_ground.get("line_ids") != expected_lines or drainage_ground.get("station_ids") != expected_stations:
                    findings.append(Finding(drainage_ground_gate_path, "drainage/ground line/station scope is stale"))
                if not drainage_ground.get("report_valid"):
                    findings.append(Finding(drainage_ground_gate_path, "drainage/ground receipt is invalid"))
                if drainage_ground.get("status") == "awaiting-drainage-ground-evidence" and (
                    drainage_ground.get("technical_screen_passed") or drainage_ground.get("authority_accepted")
                ):
                    findings.append(Finding(drainage_ground_gate_path, "pending drainage/ground report claims completed gates"))

            package_manifest_path = city_dir / "package-manifest.json"
            if package_manifest_path.is_file():
                package_manifest = json.loads(package_manifest_path.read_text())
                if not package_manifest.get("passed"):
                    findings.append(Finding(package_manifest_path, "city package manifest is not passed"))
                manifest_generator = REPO_ROOT / "tools/automation/generate-city-package-manifest.py"
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
    for design_path in sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
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
    generator = REPO_ROOT / "tools/automation/generate-national-briefs.py"
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
    design_paths = sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml"))
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
            "report is stale; run tools/automation/validate-station-clusters.py --all",
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
        REPO_ROOT / "design/city-generation" / "src",
        REPO_ROOT / "design/component-catalogue" / "src",
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
    findings = check_rolling_stock_bom_markdown_summaries(module)
    bom_ids = {str(row["line_id"]) for row in module["export_rows"](BOM_SOURCE)}
    schedule_path = REPO_ROOT / "lib/templates/manufacturing-schedule.toml"
    schedule = tomllib.loads(schedule_path.read_text(encoding="utf-8"))
    scheduled_ids = {
        ref.split(":", 1)[1]
        for package in schedule.get("manufacturing_package", [])
        for ref in package.get("bom_refs", [])
        if str(ref).startswith("rolling_stock_bom:")
    }
    if missing := sorted(bom_ids - scheduled_ids):
        findings.append(
            Finding(schedule_path, f"rolling-stock manufacturing schedule omits BOM rows: {', '.join(missing)}")
        )
    if unknown := sorted(scheduled_ids - bom_ids):
        findings.append(
            Finding(schedule_path, f"rolling-stock manufacturing schedule has unknown BOM rows: {', '.join(unknown)}")
        )
    return findings


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
    mech_src = REPO_ROOT / "design/component-catalogue/src"
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
                and path.name not in {
                    "station-product-reconciliation.json",
                    "station-product-reconciliation.md",
                }
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
                        Finding(actual, "generated station artifact is stale; run tools/automation/buildable-stations.sh")
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
    civil_generator = REPO_ROOT / "tools/automation/generate-civil-cost-model.py"
    civil_module = runpy.run_path(str(civil_generator))
    expected_civil = civil_module["render"](civil_module["build_model"]())
    civil_path = REPO_ROOT / "lib/templates/civil-cost-model.toml"
    if civil_path.read_text() != expected_civil:
        findings.append(
            Finding(
                civil_path,
                "generated civil cost contract is stale; run tools/automation/generate-civil-cost-model.py",
            )
        )
    path = REPO_ROOT / "docs/cost-model.md"
    generator = REPO_ROOT / "tools/automation/generate-cost-model.py"
    module = runpy.run_path(str(generator))
    expected = module["render_cost_model"]()
    actual = path.read_text()
    if actual != expected:
        findings.append(Finding(path, "generated cost model is stale; run tools/automation/generate-cost-model.py"))
    return findings


def check_generated_portfolio_summary() -> list[Finding]:
    path = REPO_ROOT / "docs/portfolio-summary.md"
    generator = REPO_ROOT / "tools/automation/generate-portfolio-summary.py"
    module = runpy.run_path(str(generator))
    expected = module["build_summary"]()
    findings: list[Finding] = []
    if not path.is_file() or path.read_text() != expected:
        findings.append(
            Finding(
                path,
                "generated portfolio summary is stale; run tools/automation/generate-portfolio-summary.py",
            )
        )
    _, _, capital, _ = module["portfolio_metrics"]()
    expected_readme_values = (
        f"about ${float(capital['local']) / 1_000_000_000:.0f}B",
        f"roughly {float(capital['local']) / float(capital['total']):.0%}",
        "portfolio calculation",
    )
    readme = REPO_ROOT / "README.md"
    readme_text = readme.read_text(encoding="utf-8")
    for value in expected_readme_values:
        if value not in readme_text:
            findings.append(
                Finding(readme, f"front-page economic value is stale or missing: {value}")
            )
    return findings


def check_generated_public_overview() -> list[Finding]:
    path = REPO_ROOT / "docs/open-source-rail-overview.html"
    generator = REPO_ROOT / "tools/automation/generate-public-overview.py"
    module = runpy.run_path(str(generator))
    expected = module["render"]()
    if not path.is_file() or path.read_text() != expected:
        return [
            Finding(
                path,
                "generated public overview is stale; run "
                "tools/automation/generate-public-overview.py",
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
        "## Feature Highlights",
        "README is missing the front-page feature highlights",
    )
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

    common = REPO_ROOT / "docs/deployment-planning-reference.md"
    common_text = common.read_text()
    common_rates = CIVIL_COST_MODEL["civil_usd_per_km"]
    _require_text(
        findings,
        common,
        common_text,
        (
            f"{float(common_rates['at_grade']) / 1_000_000:g} M USD/route-km "
            f"at-grade, {float(common_rates['elevated']) / 1_000_000:g} M USD/route-km "
            f"elevated\nand {float(common_rates['bridge']) / 1_000_000:g} M USD/route-km "
            "for bridges"
        ),
        "common deployment reference civil rates are stale",
    )

    rfc = REPO_ROOT / "docs/rfcs/0011-civil-infrastructure-design-standard.md"
    rfc_text = rfc.read_text()
    for key, value in CIVIL_COST_MODEL["civil_usd_per_km"].items():
        label = key.replace("_", "-")
        benchmark = CIVIL_COST_MODEL["benchmark_civil_usd_per_km"][key]
        _require_text(
            findings,
            rfc,
            rfc_text,
            f"| {label} | {_space_int(float(value))} / route-km | {_space_int(float(benchmark))} / route-km |",
            "RFC 0011 civil target/benchmark table is stale",
        )
    _require_text(
        findings,
        rfc,
        rfc_text,
        f"| elevated-interchange premium | {_space_int(float(CAPEX_COSTS['junctions']['elevated_interchange_premium_usd']))} / site | — |",
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
        f"Active design target: **{int(CIVIL_COST_MODEL['civil_usd_per_km']['at_grade']):,} USD per route-km**. Retained marketplace",
        "civil marketplace at-grade target is stale",
    )
    _require_text(
        findings,
        civil,
        civil_text,
        f"benchmark: **{int(CIVIL_COST_MODEL['benchmark_civil_usd_per_km']['at_grade']):,} USD per route-km**.",
        "civil marketplace at-grade benchmark is stale",
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
        REPO_ROOT / "docs" / "deployment-planning-reference.md",
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


def check_public_bim_review_set() -> list[Finding]:
    """Require one inspectable, validated IFC/IDS/BCF package in Git."""

    root = REPO_ROOT / "engineering/models/bim/reference"
    required = (
        "README.md",
        "civil-coordination.ifc",
        "civil-coordination.index.json",
        "civil-coordination.validation.json",
        "civil-information-requirements.ids",
        "civil-information-requirements.report.json",
        "civil-coordination-issues.bcf",
        "civil-coordination-issues.index.json",
        "civil-construction-sequence.json",
        "civil-coordination.blend",
        "civil-construction-sequence.mp4",
        "civil-construction-sequence.gif",
    )
    tracked = set(
        subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT, text=True).splitlines()
    )
    findings: list[Finding] = []
    for name in required:
        path = root / name
        if not path.is_file():
            findings.append(Finding(path, "public BIM review artifact is missing"))
        elif path.relative_to(REPO_ROOT).as_posix() not in tracked:
            findings.append(Finding(path, "public BIM review artifact is not tracked"))
    validation_path = root / "civil-coordination.validation.json"
    if validation_path.is_file():
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        if not validation.get("passed"):
            findings.append(Finding(validation_path, "public IFC validation did not pass"))
    ids_path = root / "civil-information-requirements.report.json"
    if ids_path.is_file():
        ids_report = json.loads(ids_path.read_text(encoding="utf-8"))
        if not ids_report.get("status"):
            findings.append(Finding(ids_path, "public IDS requirements did not pass"))
    return findings


def check_public_animation_set() -> list[Finding]:
    """Reject short, static, missing, untracked, or oversized review media."""

    assembly_root = REPO_ROOT / "engineering/models/digital-twins/fabrication-assembly"
    assembly_gif = assembly_root / "fabrication-assembly-digital-twin.gif"
    assembly_mp4 = assembly_root / "fabrication-assembly-digital-twin.mp4"
    civil_root = REPO_ROOT / "engineering/models/bim/reference"
    civil_gif = civil_root / "civil-construction-sequence.gif"
    civil_mp4 = civil_root / "civil-construction-sequence.mp4"
    civil_blend = civil_root / "civil-coordination.blend"
    operations_gif = REPO_ROOT / "docs/assets/digital-twin-animation.gif"
    city_gif = (
        REPO_ROOT
        / "cities/catalogue/west-asia/Iraq/Samawah/engineering/digital-twin"
        / "samawah-line1-digital-twin.gif"
    )
    manifest_path = assembly_root / "fabrication-assembly-digital-twin.json"
    tracked = set(
        subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT, text=True).splitlines()
    )
    findings: list[Finding] = []
    milestone_paths = (
        REPO_ROOT / "docs/screenshots/assembly/trainset-assembly-parts-staged.png",
        REPO_ROOT / "docs/screenshots/assembly/trainset-assembly-subassemblies.png",
        REPO_ROOT / "docs/screenshots/assembly/trainset-assembly-complete.png",
        REPO_ROOT / "docs/screenshots/civil/civil-assembly-substructure.png",
        REPO_ROOT / "docs/screenshots/civil/civil-assembly-superstructure.png",
        REPO_ROOT / "docs/screenshots/civil/civil-assembly-track-station.png",
    )
    for path in (assembly_gif, assembly_mp4, civil_gif, civil_mp4, civil_blend, operations_gif, city_gif, manifest_path, *milestone_paths):
        relative = path.relative_to(REPO_ROOT).as_posix()
        if not path.is_file():
            findings.append(Finding(path, "public animation artifact is missing"))
        elif relative not in tracked:
            findings.append(Finding(path, "public animation artifact is not tracked"))
        elif path.stat().st_size >= 20_000_000:
            findings.append(Finding(path, "public animation artifact reaches the 20 MB limit"))

    gif_contracts = (
        (assembly_gif, 250, 80_000, (640, 360)),
        (civil_gif, 180, 45_000, (640, 360)),
        (operations_gif, 150, 18_000, (800, 450)),
        (city_gif, 180, 40_000, (640, 360)),
    )
    for path, minimum_frames, minimum_duration_ms, minimum_size in gif_contracts:
        if not path.is_file():
            continue
        try:
            with Image.open(path) as animation:
                frames = int(getattr(animation, "n_frames", 1))
                size = animation.size
                duration_ms = 0
                unique_frames: set[bytes] = set()
                for frame in range(frames):
                    animation.seek(frame)
                    duration_ms += int(animation.info.get("duration", 0))
                    unique_frames.add(hashlib.sha256(animation.convert("RGB").tobytes()).digest())
        except (OSError, EOFError) as error:
            findings.append(Finding(path, f"animation cannot be decoded: {error}"))
            continue
        if frames < minimum_frames:
            findings.append(Finding(path, f"animation has only {frames} frames"))
        if duration_ms < minimum_duration_ms:
            findings.append(
                Finding(path, f"animation duration is only {duration_ms / 1000:.1f} seconds")
            )
        if len(unique_frames) < int(frames * 0.8):
            findings.append(
                Finding(path, f"only {len(unique_frames)} of {frames} frames are visually distinct")
            )
        if size[0] < minimum_size[0] or size[1] < minimum_size[1]:
            findings.append(
                Finding(path, f"animation dimensions are {size}, below minimum {minimum_size}")
            )

    if assembly_mp4.is_file():
        header = assembly_mp4.read_bytes()[:32]
        if b"ftyp" not in header or assembly_mp4.stat().st_size < 1_000_000:
            findings.append(Finding(assembly_mp4, "primary MP4 is missing a valid media header"))
    if civil_mp4.is_file():
        header = civil_mp4.read_bytes()[:32]
        if b"ftyp" not in header or civil_mp4.stat().st_size < 500_000:
            findings.append(Finding(civil_mp4, "civil MP4 is missing a valid media header"))
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("visual_tour", {}).get("duration_s") != 88.0:
            findings.append(Finding(manifest_path, "visual tour duration is not the 88-second contract"))
        graph = manifest.get("trainset_assembly_graph", {})
        if graph.get("animated_node_count") != 127 or not graph.get("dependency_timing_valid"):
            findings.append(Finding(manifest_path, "complete dependency-timed LM3 product graph is missing"))
    return findings


def check_trainset_manufacturing_package() -> list[Finding]:
    """Require the timed product/method graph and public CAD/IFC tooling views."""

    paths = {
        "source": REPO_ROOT / "lib/templates/trainset-manufacturing-methods.toml",
        "methods": REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/manufacturing-methods.json",
        "instructions": REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/manufacturing-methods.md",
        "supplier_source": REPO_ROOT / "lib/templates/trainset-supplier-anchors.toml",
        "supplier_register": REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/supplier-anchors.json",
        "supplier_guide": REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/supplier-anchors.md",
        "cots_source": REPO_ROOT / "lib/templates/trainset-cots-candidates.toml",
        "cots_register": REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/cots-candidates.json",
        "cots_guide": REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/cots-candidates.md",
        "execution_pack": REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/first-article-execution-pack.md",
        "freecad": REPO_ROOT / "design/component-catalogue/models/cad/lm3-manufacturing-tooling.FCStd",
        "ifc": REPO_ROOT / "engineering/models/bim/reference/lm3-manufacturing-reference.ifc",
        "ifc_index": REPO_ROOT / "engineering/models/bim/reference/lm3-manufacturing-reference.index.json",
        "ifc_library_index": REPO_ROOT / "engineering/models/bim/reference/lm3-product-library.index.json",
        "freecad_library_index": REPO_ROOT / "design/component-catalogue/models/cad/lm3-product-library.index.json",
        "product_manifest": REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json",
    }
    tracked = set(
        subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT, text=True).splitlines()
    )
    findings: list[Finding] = []
    for path in paths.values():
        relative = path.relative_to(REPO_ROOT).as_posix()
        if not path.is_file():
            findings.append(Finding(path, "LM3 manufacturing artifact is missing"))
        elif relative not in tracked:
            findings.append(Finding(path, "LM3 manufacturing artifact is not tracked"))
    if paths["methods"].is_file():
        methods = json.loads(paths["methods"].read_text(encoding="utf-8"))
        coverage = methods.get("coverage", {})
        if coverage.get("covered_product_rows") != coverage.get("product_rows"):
            findings.append(Finding(paths["methods"], "manufacturing methods do not cover every LM3 product row"))
        if coverage.get("product_rows") != 101 or coverage.get("tooling_count") != 20:
            findings.append(Finding(paths["methods"], "LM3 method/tooling coverage changed without review"))
    if paths["supplier_register"].is_file():
        supplier = json.loads(paths["supplier_register"].read_text(encoding="utf-8"))
        coverage = supplier.get("coverage", {})
        expected_supplier = {
            "external_product_rows": 54,
            "covered_external_product_rows": 54,
            "anchor_count": 25,
            "uncovered_product_ids": [],
        }
        if coverage != expected_supplier:
            findings.append(Finding(paths["supplier_register"], f"LM3 supplier-anchor coverage changed: {coverage}"))
    if paths["cots_register"].is_file():
        cots = json.loads(paths["cots_register"].read_text(encoding="utf-8"))
        coverage = cots.get("coverage", {})
        if coverage.get("external_product_rows") != 54 or coverage.get("covered_external_product_rows") != 54:
            findings.append(Finding(paths["cots_register"], f"LM3 COTS/RFQ coverage is incomplete: {coverage}"))
        if coverage.get("candidate_count", 0) < 30 or coverage.get("uncovered_product_ids"):
            findings.append(Finding(paths["cots_register"], f"LM3 COTS/RFQ register is incomplete: {coverage}"))
    if paths["ifc_index"].is_file():
        index = json.loads(paths["ifc_index"].read_text(encoding="utf-8"))
        if not index.get("passed"):
            findings.append(Finding(paths["ifc_index"], "LM3 manufacturing IFC validation did not pass"))
        expected = {
            "product_item_count": 101,
            "product_geometry_count": 101,
            "product_representation_part_count": 523,
            "method_count": 9,
            "tooling_count": 20,
            "task_count": 59,
        }
        observed = {key: index.get(key) for key in expected}
        if observed != expected:
            findings.append(Finding(paths["ifc_index"], f"LM3 manufacturing IFC counts changed: {observed}"))
        if index.get("supplier_anchor_count") != 25 or index.get("supplier_anchored_external_product_count") != 54:
            findings.append(Finding(paths["ifc_index"], "LM3 IFC supplier-anchor coverage is incomplete"))
    if paths["product_manifest"].is_file():
        product_manifest = json.loads(paths["product_manifest"].read_text(encoding="utf-8"))
        base = paths["product_manifest"].parent
        expected_ids = {
            row["id"] for key in ("product_items", "assemblies")
            for row in product_manifest[key]
        }
        definition_ids = {
            path.stem for path in (base / "definitions").glob("*/*.json")
        }
        traveler_ids = {
            path.stem for path in (base / "travelers").glob("*/*.json")
        }
        if definition_ids != expected_ids:
            findings.append(Finding(base / "definitions", "GitHub part/assembly definitions do not match the 127-node product tree"))
        if traveler_ids != expected_ids:
            findings.append(Finding(base / "travelers", "GitHub part/assembly travelers do not match the 127-node product tree"))

        expected_products = {str(row["id"]) for row in product_manifest["product_items"]}
        expected_assemblies = {str(row["id"]) for row in product_manifest["assemblies"]}
        library_specs = (
            (
                paths["ifc_library_index"],
                REPO_ROOT / "engineering/models/bim/reference/lm3-parts",
                REPO_ROOT / "engineering/models/bim/reference/lm3-assemblies",
                ".ifc",
                "all_active_products_reach_final_assembly",
            ),
            (
                paths["freecad_library_index"],
                REPO_ROOT / "design/component-catalogue/models/cad/lm3-parts",
                REPO_ROOT / "design/component-catalogue/models/cad/lm3-assemblies",
                ".FCStd",
                "all_active_products_reach_root",
            ),
        )
        for index_path, parts_dir, assemblies_dir, suffix, reachability_key in library_specs:
            if not index_path.is_file():
                continue
            library = json.loads(index_path.read_text(encoding="utf-8"))
            if (
                not library.get("passed")
                or library.get("product_count") != 101
                or library.get("assembly_count") != 26
                or not library.get(reachability_key)
            ):
                findings.append(Finding(index_path, "LM3 split part/assembly library validation did not pass"))
            observed_parts = {path.stem for path in parts_dir.glob(f"*{suffix}")}
            observed_assemblies = {path.stem for path in assemblies_dir.glob(f"*{suffix}")}
            if observed_parts != expected_products:
                findings.append(Finding(parts_dir, "split LM3 part files do not exactly match the 101 product rows"))
            if observed_assemblies != expected_assemblies:
                findings.append(Finding(assemblies_dir, "split LM3 assembly files do not exactly match the 26 assembly nodes"))
            for entry in [*library.get("parts", []), *library.get("assemblies", [])]:
                artifact = REPO_ROOT / str(entry.get("file", ""))
                if not artifact.is_file():
                    findings.append(Finding(artifact, "indexed LM3 CAD/IFC artifact is missing"))
                    continue
                digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
                if digest != entry.get("sha256"):
                    findings.append(Finding(artifact, "indexed LM3 CAD/IFC hash is stale"))
        public_files = [
            *list((base / "definitions").glob("*/*.*")),
            *list((base / "travelers").glob("*/*.*")),
            *list((REPO_ROOT / "design/component-catalogue/models/cad").glob("*.FCStd")),
            *list((REPO_ROOT / "design/component-catalogue/models/cad/lm3-parts").glob("*.FCStd")),
            *list((REPO_ROOT / "design/component-catalogue/models/cad/lm3-assemblies").glob("*.FCStd")),
            *list((REPO_ROOT / "engineering/models/bim/reference/lm3-parts").glob("*.ifc")),
            *list((REPO_ROOT / "engineering/models/bim/reference/lm3-assemblies").glob("*.ifc")),
        ]
        for path in public_files:
            if path.relative_to(REPO_ROOT).as_posix() not in tracked:
                findings.append(Finding(path, "public LM3 part/assembly artifact is not tracked"))
    return findings


def check_readme_corpus() -> list[Finding]:
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools/automation/check-readmes.py")],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        message = (completed.stdout + completed.stderr).strip()
        return [Finding(REPO_ROOT, message)]
    return []


def check_simulation_component_coverage() -> list[Finding]:
    """Keep the complete software inventory classification reproducible."""
    report_path = REPO_ROOT / "engineering/assurance/simulation-component-coverage.json"
    validator_path = REPO_ROOT / "tools/automation/validate-simulation-components.py"
    if not report_path.is_file():
        return [Finding(report_path, "simulation component coverage report is missing")]
    module = runpy.run_path(str(validator_path))
    expected = module["build_report"]()
    actual = json.loads(report_path.read_text())
    if actual != expected:
        return [Finding(report_path, "simulation component coverage report is stale")]
    if not actual.get("passed"):
        return [Finding(report_path, "simulation component coverage is not passed")]
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
    findings.extend(check_generated_public_overview())
    findings.extend(check_cost_reference_tables())
    findings.extend(check_readme_corpus())
    findings.extend(check_simulation_component_coverage())
    findings.extend(check_public_bim_review_set())
    findings.extend(check_public_animation_set())
    findings.extend(check_trainset_manufacturing_package())
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
        city_count = len(list((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml")))
        print(f"repo-health: ok ({city_count} city designs checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
