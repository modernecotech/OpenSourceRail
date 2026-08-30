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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        city_dir / "engineering/energy/summary.json",
        city_dir / "engineering/finance/summary.json",
        city_dir / "engineering/project-twin/summary.json",
        city_dir / "engineering/gis/summary.json",
        city_dir / "engineering/ring-interchange-summary.json",
        city_dir / "engineering/screenshots/manifest.json",
        city_dir / "engineering/screenshots" / f"{slug}-network-visualizer.png",
        city_dir / "engineering/screenshots" / f"{slug}-simulation-dashboard.png",
        city_dir / "engineering/simulation/validation-summary.json",
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

    passed = not missing and not failed_summaries and not local_path_files and operations_hash_current
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
