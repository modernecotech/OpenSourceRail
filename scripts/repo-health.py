#!/usr/bin/env python3
"""Repository health checks for generated OSR catalogue artifacts.

The checks here are deliberately boring: they catch drift between the
current concept, the generated city artefacts, and the CAPEX formulas.
Run from the repository root:

    python3 scripts/repo-health.py
"""

from __future__ import annotations

import argparse
import runpy
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
USD_TO_EUR = 0.92

TRAINSET_COST_EUR = {
    "urban-shuttle-1car": 245_436,
    "tram-2car": 490_872,
    "light-metro-3car": 736_308,
    "metro-4car": 981_744,
    "metro-6car": 1_472_616,
}

CHARGING_MICROGRID_EUR = {
    "halt": 69_000,
    "standard": 138_000,
    "major": 230_000,
    "terminal": 230_000,
    "interchange": 322_000,
    "interchange-elevated": 322_000,
    "depot-terminal": 414_000,
}

SIGNALLING_EUR_PER_KM = 13_800
EPC_OVERHEAD_FRAC = 0.07


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
    return sum(
        CHARGING_MICROGRID_EUR.get(station.get("archetype", "standard"), 250_000)
        for station in design.get("stations", [])
    )


def _almost_equal(a: float, b: float, tolerance: float = 2.0) -> bool:
    return abs(a - b) <= tolerance


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
    if not design_paths:
        return [Finding(REPO_ROOT / "designs", "no city design.toml files found")]

    for design_path in design_paths:
        city_dir = design_path.parent
        slug = city_dir.name.lower().replace(" ", "-")
        required = [
            city_dir / "README.md",
            city_dir / f"{slug}.toml",
            city_dir / f"{slug}-network-map.png",
            city_dir / f"{slug}.design-quality.yaml",
        ]
        for path in required:
            if not path.exists():
                findings.append(Finding(path, "missing generated city artifact"))

        readme = city_dir / "README.md"
        if readme.exists():
            text = readme.read_text()
            if "Station/depot charging microgrids" not in text:
                findings.append(Finding(readme, "missing station/depot charging microgrid cost row"))
            for stale in ("Traction power", "€0.8 M/km", "Residual train-control wayside + power"):
                if stale in text:
                    findings.append(Finding(readme, f"stale generated README wording: {stale!r}"))
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
            expected_rolling = _fleet_total(design) * TRAINSET_COST_EUR.get(family, 736_308)
            if not _almost_equal(expected_rolling, float(costs.get("rolling_stock_eur", 0))):
                findings.append(Finding(design_path, "rolling_stock_eur does not match marketplace-BOM family cost"))

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
            findings.append(Finding(design_path, "signalling_eur does not match $15k/km residual wayside rate converted to EUR"))

        expected_charging = _charging_microgrid_total(design)
        actual_charging = float(costs.get("charging_microgrid_eur", costs.get("power_eur", 0)))
        if not _almost_equal(expected_charging, actual_charging):
            findings.append(Finding(design_path, "charging_microgrid_eur does not match station/depot charging microgrid total"))
        if "power_eur" in costs and not _almost_equal(actual_charging, float(costs.get("power_eur", 0))):
            findings.append(Finding(design_path, "deprecated power_eur alias does not match charging_microgrid_eur"))

        pre_epc = (
            civil
            + int(costs.get("stations_eur", 0))
            + int(costs.get("depots_eur", 0))
            + int(costs.get("rolling_stock_eur", 0))
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
            "signalling",
            "charging_microgrid",
            "epc_overhead",
            "total",
        ):
            _check_usd_mirror(findings, design_path, costs, stem)
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
        r"\b900 kWh/trainset\b": "3-car battery basis is now 360 kWh/trainset",
        r"\b450 kWh battery\b": "tram battery basis is now 240 kWh",
        r"€0\.8 M/km": "charging microgrids are costed per stop, not per route-km",
        r"\bTraction power\s*\(": "use station/depot charging microgrids or onboard motor output",
        r"car-body-22m": "car-body artifact name should match the 17 m module",
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
    findings: list[Finding] = []
    source = REPO_ROOT / "docs/rolling-stock/light-metro-3car/bom-skeleton.md"
    csv_path = REPO_ROOT / "build/bom/rolling_stock_bom.csv"
    exporter = REPO_ROOT / "scripts/export-light-metro-bom.py"
    if not csv_path.exists():
        return [Finding(csv_path, "missing generated rolling-stock BOM CSV")]
    module = runpy.run_path(str(exporter))
    expected = module["render_csv"](source)
    actual = csv_path.read_text()
    if actual != expected:
        findings.append(
            Finding(
                csv_path,
                "generated BOM CSV is stale; run scripts/export-light-metro-bom.py",
            )
        )
    return findings


def run_checks() -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_city_artifacts())
    findings.extend(check_city_costs())
    findings.extend(check_stale_terms())
    findings.extend(check_rolling_stock_bom())
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
