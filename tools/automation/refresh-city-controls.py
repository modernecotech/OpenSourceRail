#!/usr/bin/env python3
"""Refresh finance, project controls and documentation without reattesting solvers."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def refresh(path: Path, documentation_only: bool = False) -> dict:
    design = tomllib.loads(path.read_text())
    slug = design["city"]["slug"]
    directory = path.parent
    logs = ROOT / ".cache/osr-pipeline/logs"
    logs.mkdir(parents=True, exist_ok=True)
    finance = [sys.executable, str(ROOT / "tools/automation/generate-city-finance.py"), "--design", str(path)]
    operations = [sys.executable, str(ROOT / "tools/automation/generate-qa-maintenance-data.py"), "--design", str(path), "--out-dir", str(directory / "operations")]
    commands = [] if documentation_only else [finance, operations]
    if design["city"]["country"] == "IQ" and not documentation_only:
        commands += [finance, operations]
    if not documentation_only:
        commands += [[sys.executable, str(ROOT / "tools/automation/generate-acceptance-evidence-report.py"), "--bundle", str(directory / f"operations/{slug}-operations.json.gz")]]
    commands += [[sys.executable, "-m", "osr_scenario.network_readme", "--design", str(path), "--scenario", str(directory / f"{slug}.toml"), "--out", str(directory / "README.md"), "--allow-stale-evidence"]]
    with (logs / f"controls-{slug}.log").open("w") as handle:
        for command in commands:
            result = subprocess.run(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT)
            if result.returncode:
                return {"city": slug, "controls_refreshed": False, "failed_command": command}
        result = subprocess.run([sys.executable, str(ROOT / "tools/automation/generate-city-package-manifest.py"), "--city-dir", str(directory)], cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT)
        if result.returncode not in (0, 1):
            return {"city": slug, "controls_refreshed": False, "error": "manifest generation error"}
    manifest = json.loads((directory / "package-manifest.json").read_text())
    return {"city": slug, "controls_refreshed": True, "planning_example_complete": manifest["planning_example_complete"],
            "retained_solver_sources_current": not manifest["stale_analysis_sources"], "operational_release": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default="")
    parser.add_argument("--skip", default="")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--documentation-only", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    paths = []
    for path in sorted((ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
        slug = tomllib.loads(path.read_text())["city"]["slug"]
        if slug in args.skip.split(",") or (args.only and slug not in args.only.split(",")):
            continue
        paths.append(path)
    if not paths:
        parser.error("no matching cities")
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for row in pool.map(lambda path: refresh(path, args.documentation_only), paths):
            rows.append(row)
            print(f"{'OK' if row['controls_refreshed'] else 'FAIL'} {row['city']}", flush=True)
    output = ROOT / "build/engineering/cities/controls-refresh-summary.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"cities": rows, "passed": all(r["controls_refreshed"] for r in rows)}, indent=2)+"\n")
    return 0 if all(r["controls_refreshed"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
