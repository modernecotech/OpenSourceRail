#!/usr/bin/env python3
"""Fail closed unless a generated city has a complete planning package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BINARY_SUFFIXES = {".gz", ".gpkg", ".png"}
LOCAL_REPRODUCIBLE_SUFFIXES = {".gz", ".gpkg"}
LOCAL_PATH = re.compile(
    r"(?:/home/[^/]+/|/Users/[^/]+/|/tmp/|[A-Za-z]:[\\/](?:Users|Temp)[\\/])"
)
STABLING_DIAGNOSTICS = {"operating-screen", "service-cycle-screen", "redistribution-study"}


def is_stabling_diagnostic(relative: str) -> bool:
    path = Path(relative)
    return path.parent.as_posix() == "engineering/stabling" and path.stem in STABLING_DIAGNOSTICS


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stale_analysis_sources(city_dir: Path, slug: str, *, include_diagnostics: bool = False) -> list[dict[str, str | None]]:
    """A passing retained report cannot close a package against different inputs."""
    sources = {
        "design_sha256": city_dir / "design.toml",
        "scenario_sha256": city_dir / f"{slug}.toml",
    }
    families = {
        "depot-scope/summary.json": {
            **sources,
            "generator_sha256": REPO_ROOT / "tools/automation/generate-depot-scope.py",
            "scope_model_sha256": REPO_ROOT / "design/component-catalogue/src/osr_mech/depot/energy.py",
            "depot_template_sha256": REPO_ROOT / "lib/templates/depots.toml",
            "energy_template_sha256": REPO_ROOT / "lib/templates/energy-sites.toml",
            "cost_template_sha256": REPO_ROOT / "lib/templates/capex-costs.toml",
            "rolling_stock_template_sha256": REPO_ROOT / "lib/templates/rolling-stock.toml",
            "station_manifest_sha256": REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json",
            "simulator_source_sha256": REPO_ROOT / "crates/osr-sim/src/sim.rs",
        },
        "simulation/validation-summary.json": {
            **sources, "generator_sha256": REPO_ROOT / "tools/automation/validate-city-simulation.py",
        },
        "energy/summary.json": {
            **sources, "generator_sha256": REPO_ROOT / "engineering/analysis/city_microgrid.py",
            "climate_sha256": REPO_ROOT / "lib/templates/climate.toml",
        },
        "sumo/summary.json": {
            **sources, "generator_sha256": REPO_ROOT / "engineering/analysis/benchmarks/sumo/city_timetable.py",
            "corridor_sha256": city_dir / f"{slug}.corridor.geojson",
            "rolling_stock_sha256": REPO_ROOT / "lib/templates/rolling-stock.toml",
        },
        "simulation/native-timing-reference.json": {
            "generator_sha256": REPO_ROOT / "tools/automation/generate-deployment-evidence.py",
            **sources, "simulator_source_sha256": REPO_ROOT / "crates/osr-sim/src/sim.rs",
        },
        "gis/summary.json": {
            **sources, "generator_sha256": REPO_ROOT / "engineering/analysis/city_package.py",
            "corridor_sha256": city_dir / f"{slug}.corridor.geojson",
        },
    }
    findings = []
    for relative, inputs in families.items():
        path = city_dir / "engineering" / relative
        if not path.is_file():
            continue  # missing-artifact gate handles absent reports
        report = json.loads(path.read_text(encoding="utf-8"))
        for key, source in inputs.items():
            actual = sha256(source) if source.is_file() else None
            if actual is None or report.get(key) != actual:
                findings.append({
                    "artifact": f"engineering/{relative}", "source": key,
                    "expected_sha256": actual, "recorded_sha256": report.get(key),
                })
    for relative, generator in (
        ("soil/summary.json", "engineering/analysis/city_soils.py"),
        ("deployment/summary.json", "engineering/analysis/city_deployment.py"),
        ("delivery/summary.json", "engineering/analysis/city_delivery.py"),
        ("simulation/operations-crosscheck.json", "engineering/analysis/operations_crosscheck.py"),
    ):
        path = city_dir / "engineering" / relative
        if not path.is_file():
            continue
        report = json.loads(path.read_text())
        bindings = {"generator_sha256": REPO_ROOT / generator}
        if relative.startswith("delivery/"):
            for value, recorded in report.get("input_sha256", {}).items():
                source = REPO_ROOT / value
                if not source.is_file() or recorded != sha256(source):
                    findings.append({"artifact": "engineering/"+relative, "source": value,
                                     "expected_sha256": sha256(source) if source.is_file() else None,
                                     "recorded_sha256": recorded})
        if relative.startswith("soil/"):
            bindings.update({"samples_sha256": path.parent / "samples.csv", "source_receipt_sha256": path.parent / "source-receipt.json", "civil_plan_sha256": path.parent / "civil-investigation-plan.json", "sample_locations_sha256": path.parent / "sample-locations.geojson"})
            for key, value in report.get("source_paths", {}).items():
                source = REPO_ROOT / value
                if not source.is_file() or report.get("input_sha256", {}).get(key) != sha256(source):
                    findings.append({"artifact": "engineering/"+relative, "source": key, "expected_sha256": sha256(source) if source.is_file() else None, "recorded_sha256": report.get("input_sha256", {}).get(key)})
        if relative.startswith("deployment/"):
            for evidence, recorded in report.get("evidence_sha256", {}).items():
                source = city_dir / "engineering" / evidence
                if not source.is_file() or recorded != sha256(source):
                    findings.append({"artifact": "engineering/"+relative, "source": evidence, "expected_sha256": sha256(source) if source.is_file() else None, "recorded_sha256": recorded})
        if relative.startswith("simulation/"):
            for key, value in report.get("sources", {}).items():
                source = REPO_ROOT / value
                hash_key = "native_timing_reference_sha256" if key == "native_timing_reference" else key+"_sha256"
                if not source.is_file() or report.get("evidence_hashes", {}).get(hash_key) != sha256(source):
                    findings.append({"artifact": "engineering/"+relative, "source": key, "expected_sha256": sha256(source) if source.is_file() else None, "recorded_sha256": report.get("evidence_hashes", {}).get(hash_key)})
        for key, source in bindings.items():
            if not source.is_file() or report.get(key) != sha256(source):
                findings.append({"artifact": "engineering/"+relative, "source": key, "expected_sha256": sha256(source) if source.is_file() else None, "recorded_sha256": report.get(key)})
    stabling_path = city_dir / "engineering/stabling/summary.json"
    stabling_sources = {
        "design": city_dir / "design.toml", "scenario": city_dir / f"{slug}.toml",
        "generator": REPO_ROOT / "tools/automation/generate-stabling-plan.py",
        "allocation_model": REPO_ROOT / "design/city-generation/src/osr_scenario/stabling.py",
        "depot_policy": REPO_ROOT / "lib/templates/depots.toml",
        "simulator": REPO_ROOT / "crates/osr-sim/src/sim.rs",
        "loader": REPO_ROOT / "crates/osr-sim/src/scenario_file.rs",
        "schedule": REPO_ROOT / "crates/osr-sim/src/schedule.rs",
        "station_template": REPO_ROOT / "lib/templates/stations.toml",
        "rolling_stock_template": REPO_ROOT / "lib/templates/rolling-stock.toml",
        "train_model": REPO_ROOT / "crates/osr-sim/src/train.rs",
        "capacity_model": REPO_ROOT / "design/city-generation/src/osr_scenario/stabling_capacity.py",
        "hybrid_model": REPO_ROOT / "design/city-generation/src/osr_scenario/stabling_hybrid.py",
    }
    if stabling_path.is_file():
        report = json.loads(stabling_path.read_text())
        for key, source in stabling_sources.items():
            actual = sha256(source) if source.is_file() else None
            recorded = report.get("source_sha256", {}).get(key)
            if actual is None or recorded != actual:
                findings.append({"artifact": "engineering/stabling/summary.json", "source": key,
                                 "expected_sha256": actual, "recorded_sha256": recorded})
    for screen_name, generator, extra_sources in (
        ("operating-screen", "screen-stabling-plan.py", {}),
        ("service-cycle-screen", "screen-stabling-cycles.py", {
            "cycle_model": REPO_ROOT / "design/city-generation/src/osr_scenario/stabling_cycles.py",
        }),
        ("hybrid-cycle-screen", "screen-hybrid-stabling.py", {
            "hybrid_cycle_model": REPO_ROOT / "design/city-generation/src/osr_scenario/stabling_hybrid_cycles.py",
            "report_model": REPO_ROOT / "crates/osr-sim/src/report.rs",
        }),
        ("redistribution-study", "screen-stabling-cycles.py", {
            "cycle_model": REPO_ROOT / "design/city-generation/src/osr_scenario/stabling_cycles.py",
            "cycle_report": city_dir / "engineering/stabling/service-cycle-screen.json",
            "study_generator": REPO_ROOT / "tools/automation/study-stabling-redistribution.py",
            "redistribution_model": REPO_ROOT / "design/city-generation/src/osr_scenario/stabling_redistribution.py",
        }),
    ):
        if screen_name in STABLING_DIAGNOSTICS and not include_diagnostics:
            continue
        screen_path = city_dir / f"engineering/stabling/{screen_name}.json"
        if not screen_path.is_file():
            continue
        screen = json.loads(screen_path.read_text())
        for key, source in {
            **stabling_sources,
            "screen_generator": REPO_ROOT / "tools/automation" / generator,
            "energy_model": REPO_ROOT / "crates/osr-sim/src/energy.rs",
            "train_model": REPO_ROOT / "crates/osr-sim/src/train.rs",
            "physics_model": REPO_ROOT / "crates/osr-sim/src/physics.rs",
            **({"direction_model": REPO_ROOT / "design/city-generation/src/osr_scenario/stabling_evidence.py"}
               if screen_name != "hybrid-cycle-screen" else {}),
            **extra_sources,
        }.items():
            actual = sha256(source) if source.is_file() else None
            recorded = screen.get("source_sha256", {}).get(key)
            if actual is None or recorded != actual:
                findings.append({"artifact": f"engineering/stabling/{screen_name}.json", "source": key,
                                 "expected_sha256": actual, "recorded_sha256": recorded})
    return findings


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--city-dir", type=Path, required=True)
    args = parser.parse_args()
    city_dir = args.city_dir.resolve()
    design_path = city_dir / "design.toml"
    design = tomllib.loads(design_path.read_text(encoding="utf-8"))
    slug = str(design["city"]["slug"])

    required = [
        city_dir / "README.md",
        design_path,
        city_dir / f"{slug}.toml",
        city_dir / f"{slug}-network-map.png",
        city_dir / f"{slug}.corridor.geojson",
        city_dir / f"{slug}.stations.json",
        city_dir / f"{slug}.design-quality.yaml",
        city_dir / "engineering/alignment/README.md",
        city_dir / "engineering/soil/summary.json",
        city_dir / "engineering/soil/samples.csv",
        city_dir / "engineering/soil/source-receipt.json",
        city_dir / "engineering/soil/civil-investigation-plan.json",
        city_dir / "engineering/soil/sample-locations.geojson",
        city_dir / "engineering/soil/README.md",
        city_dir / "engineering/deployment/summary.json",
        city_dir / "engineering/delivery/summary.json",
        city_dir / "engineering/delivery/README.md",
        city_dir / "engineering/delivery/workforce.csv",
        city_dir / "engineering/deployment/README.md",
        city_dir / "engineering/simulation/native-timing-reference.json",
        city_dir / "engineering/energy/summary.json",
        city_dir / "engineering/depot-scope/summary.json",
        city_dir / "engineering/depot-scope/README.md",
        city_dir / "engineering/stabling/summary.json",
        city_dir / "engineering/stabling/README.md",
        city_dir / "engineering/finance/summary.json",
        city_dir / "engineering/project-twin/summary.json",
        city_dir / "engineering/gis/summary.json",
        city_dir / "engineering/ring-interchange-summary.json",
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
        city_dir / "engineering/survey/structural-release-input-manifest.csv",
        city_dir / "engineering/survey/structural-release-readiness.json",
        city_dir / "engineering/survey/structural-release-readiness.md",
        city_dir / "engineering/simulation/validation-summary.json",
        city_dir / "engineering/simulation/operations-crosscheck.json",
        city_dir / "engineering/simulation/operations-crosscheck.md",
        city_dir / "engineering/station-cluster-summary.json",
        city_dir / "engineering/station-product-map.json",
        city_dir / "engineering/sumo/summary.json",
        city_dir / "operations/acceptance-evidence-report.md",
        city_dir / "operations" / f"{slug}-operations-manifest.json",
    ]
    local_reproducible = [
        city_dir / "engineering/gis" / f"{slug}.gpkg",
        city_dir / "operations" / f"{slug}-acceptance-evidence-matrix.csv",
        city_dir / "operations" / f"{slug}-operations.json.gz",
        city_dir / "operations" / f"{slug}-construction-timeline.json",
        city_dir / "operations" / f"{slug}-procurement-plan.csv",
        city_dir / "operations" / f"{slug}-budget-work-packages.csv",
        city_dir / "operations" / f"{slug}-cashflow-requirements.csv",
    ]
    # The selected operating configuration is the line-local hybrid plan.
    # Superseded station-only experiments retain provenance below, not gates.
    for screen_name in ("hybrid-cycle-screen",):
        screen = city_dir / f"engineering/stabling/{screen_name}.json"
        if screen.is_file():
            required.extend([screen, screen.with_suffix(".md")])
    for line in design.get("lines", []):
        line_id = str(line.get("id") or line.get("name")).replace("-", "")
        required.append(city_dir / "engineering/alignment" / f"{slug}-{line_id}.aln.toml")

    missing = [str(path.relative_to(city_dir)) for path in required if not path.is_file()]
    failed_summaries: list[str] = []
    for path in required:
        if path.suffix != ".json" or not path.is_file():
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        if "passed" in value and not value["passed"]:
            failed_summaries.append(str(path.relative_to(city_dir)))
    simulation_summary = city_dir / "engineering/simulation/validation-summary.json"
    if simulation_summary.is_file():
        simulation = json.loads(simulation_summary.read_text(encoding="utf-8"))
        if not simulation.get("resilience_required") or not simulation.get("resilience_passed"):
            failed_summaries.append(
                "engineering/simulation/validation-summary.json: resilience suite not passed"
            )

    local_path_files: list[str] = []
    for root in (city_dir / "engineering", city_dir / "operations"):
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() in BINARY_SUFFIXES:
                continue
            if LOCAL_PATH.search(path.read_text(encoding="utf-8", errors="ignore")):
                local_path_files.append(str(path.relative_to(city_dir)))

    operations_manifest = city_dir / "operations" / f"{slug}-operations-manifest.json"
    operations_bundle = city_dir / "operations" / f"{slug}-operations.json.gz"
    operations_hash_current = True
    if operations_manifest.is_file() and operations_bundle.is_file():
        operations_hash_current = (
            json.loads(operations_manifest.read_text(encoding="utf-8")).get("compressed_sha256")
            == sha256(operations_bundle)
        )

    stale_sources = stale_analysis_sources(city_dir, slug)
    passed = not missing and not failed_summaries and not stale_sources and not local_path_files and operations_hash_current
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    ).stdout.strip()
    manifest = {
        "schema_version": "1.0",
        "city": slug,
        "package_status": "screening-passed" if passed else "incomplete",
        "passed": passed,
        "source_revision": revision or None,
        "generator": str(Path(__file__).relative_to(REPO_ROOT)),
        "generator_sha256": sha256(Path(__file__)),
        "artifacts": {
            str(path.relative_to(city_dir)): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(required)
            if path.is_file()
        },
        "local_reproducible_artifacts": {
            str(path.relative_to(city_dir)): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "required_in_git_checkout": False,
            }
            for path in sorted(local_reproducible)
            if path.is_file()
        },
        "missing_artifacts": missing,
        "failed_summaries": failed_summaries,
        "selected_stabling_configuration": "line-local-station-depot",
        "diagnostic_artifacts": {
            str(path.relative_to(city_dir)): {
                "sha256": sha256(path),
                "passed": json.loads(path.read_text()).get("passed"),
                "scope": "superseded station-only experiment; not selected-plan acceptance",
            }
            for name in sorted(STABLING_DIAGNOSTICS)
            if (path := city_dir / f"engineering/stabling/{name}.json").is_file()
        },
        "diagnostic_stale_sources": [
            row for row in stale_analysis_sources(city_dir, slug, include_diagnostics=True)
            if is_stabling_diagnostic(row["artifact"])
        ],
        "stale_analysis_sources": stale_sources,
        "absolute_local_path_artifacts": sorted(local_path_files),
        "operations_bundle_hash_current": operations_hash_current,
        "external_release_gates": [
            "surveyed alignment and property/utility control",
            "calibrated passenger demand and operator timetable",
            "geotechnical, drainage, structural and fire authority acceptance",
            "supplier-frozen battery, charger, traction and mechanical equipment",
            "independent safety assessment and construction release",
        ],
    }
    atomic_json(city_dir / "package-manifest.json", manifest)
    print(
        f"city-package {slug}: status={manifest['package_status']} "
        f"artifacts={len(manifest['artifacts'])} missing={len(missing)}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
