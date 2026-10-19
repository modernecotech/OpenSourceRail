#!/usr/bin/env python3
"""Refresh current-source city packages; replace controlled layouts explicitly."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogue_designs import city_slug


REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN_PY = REPO_ROOT / "design/city-generation"
CATALOG = REPO_ROOT / "lib/city-batches/world-sample.toml"
CACHE_ROOT = REPO_ROOT / ".cache/osr-pipeline"
OSM_CACHE = CACHE_ROOT / "osm"
RASTER_CACHE = CACHE_ROOT / "rasters"
LOG_ROOT = REPO_ROOT / ".cache/osr-pipeline/logs"
SUMMARY_PATH = REPO_ROOT / "build/engineering/cities/package-summary.json"
ENGINEERING_SUMMARY = REPO_ROOT / "build/engineering/cities/batch-summary.json"
OSM_FETCH_LOCK = threading.Lock()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, delete=False, encoding="utf-8"
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def discover_designs() -> dict[str, Path]:
    designs: dict[str, Path] = {}
    for path in sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
        slug = city_slug(path)
        if not slug:
            raise RuntimeError(f"{path}: missing city.slug")
        if slug in designs:
            raise RuntimeError(f"duplicate city slug {slug}: {designs[slug]} and {path}")
        designs[slug] = path
    return designs


def python_environment() -> dict[str, str]:
    environment = os.environ.copy()
    source = str(DESIGN_PY / "src")
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = source if not existing else f"{source}{os.pathsep}{existing}"
    return environment


def run_logged(
    command: list[str],
    log_path: Path,
    *,
    cwd: Path = REPO_ROOT,
    environment_overrides: dict[str, str] | None = None,
) -> int:
    environment = python_environment()
    if environment_overrides:
        environment.update(environment_overrides)
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"$ {' '.join(command)}\n")
        handle.write(completed.stdout)
        if completed.stdout and not completed.stdout.endswith("\n"):
            handle.write("\n")
        handle.write(f"[exit {completed.returncode}]\n\n")
    return completed.returncode


def source_artifacts(slug: str, design_path: Path) -> list[Path]:
    city_dir = design_path.parent
    return [
        design_path,
        city_dir / f"{slug}.corridor.geojson",
        city_dir / f"{slug}.stations.json",
        city_dir / f"{slug}.design-quality.yaml",
    ]


def repository_review_artifacts(slug: str, design_path: Path) -> list[Path]:
    """Return generated city evidence that must remain publishable through Git."""

    city_dir = design_path.parent
    engineering = city_dir / "engineering"
    operations = city_dir / "operations"
    artifacts = [
        engineering / "alignment/README.md",
        engineering / "energy/summary.json",
        engineering / "finance/summary.json",
        engineering / "project-twin/summary.json",
        engineering / "gis/summary.json",
        engineering / "ring-interchange-summary.json",
        engineering / "screenshots/manifest.json",
        engineering / "simulation/validation-summary.json",
        engineering / "station-cluster-summary.json",
        engineering / "station-product-map.json",
        engineering / "sumo/summary.json",
        engineering / "design-system/summary.json",
        engineering / "design-system/index.html",
        engineering / "federation/summary.json",
        engineering / "federation/index.html",
        engineering / "federation/model.ifc",
        engineering / "federation/layout.geojson",
        engineering / "federation/instances.json",
        engineering / "federation/layout.png",
        operations / "acceptance-evidence-report.md",
        operations / f"{slug}-assets.csv",
        operations / f"{slug}-operations-manifest.json",
    ]
    artifacts.extend(sorted((engineering / "alignment").glob("*.aln.toml")))
    artifacts.extend(sorted((engineering / "gis/layers").glob("*.geojson")))
    artifacts.extend(sorted((engineering / "screenshots").glob("*.png")))
    artifacts.extend(engineering / 'alignment' / name for name in (
        'planning-grid.json','planning-water-mask.bin.gz','water-source-receipt.json',
        'independent-landcover-samples.bin.gz','planning-water-features.json.gz',
        'planning-buildability-mask.bin.gz','planning-terrain-slope.f32.gz',
        'planning-terrain-source.json'))
    return artifacts


def ignored_review_artifacts(selected: dict[str, Path]) -> dict[str, list[str]]:
    """Detect publication drift before a successful generation run is reported."""

    ignored: dict[str, list[str]] = {}
    for slug, design_path in selected.items():
        paths = repository_review_artifacts(slug, design_path)
        relative = [str(path.relative_to(REPO_ROOT)) for path in paths]
        completed = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin"],
            cwd=REPO_ROOT,
            input="\n".join(relative) + "\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode not in (0, 1):
            raise RuntimeError(completed.stderr.strip() or "git check-ignore failed")
        matches = [line for line in completed.stdout.splitlines() if line]
        if matches:
            ignored[slug] = matches
    return ignored


def prepare_city(
    slug: str,
    design_path: Path,
    catalog_city: dict[str, object],
    from_scratch: bool,
    resynthesise_corridors: bool,
    resynthesise_design: bool = False,
    current_design_logic: bool = True,
    reuse_planned_corridors: bool = False,
) -> dict[str, object]:
    started = time.monotonic()
    city_dir = design_path.parent
    log_path = LOG_ROOT / f"package-{slug}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("", encoding="utf-8")
    (city_dir / "package-manifest.json").unlink(missing_ok=True)

    raster_path = RASTER_CACHE / f"{slug}.grid.json"
    corridor_cache = city_dir / "corridors.json"
    commands: list[list[str]] = []
    existing_design = design_path.is_file()
    replace_layout = not existing_design or from_scratch or resynthesise_corridors or resynthesise_design
    if (replace_layout or reuse_planned_corridors) and (from_scratch or not raster_path.is_file()):
        bbox = catalog_city.get("bbox", {})
        bbox_text = ",".join(
            str(bbox[key]) for key in ("south", "west", "north", "east")
        )
        commands.extend(
            [
                [
                    sys.executable,
                    "-m",
                    "osr_osm.cli",
                    "--slug",
                    slug,
                    f"--bbox={bbox_text}",
                    "--out",
                    str(OSM_CACHE / f"{slug}.json"),
                ],
                [
                    sys.executable,
                    "-m",
                    "osr_geo.cli",
                    "--slug",
                    slug,
                    "--osm-json",
                    str(OSM_CACHE / f"{slug}.json"),
                    "--out-dir",
                    str(RASTER_CACHE),
                    "--country",
                    str(catalog_city["country"]),
                ],
            ]
        )
    design_command = [
        str(REPO_ROOT / "target/release/osr-design"),
        "--slug",
        slug,
        "--sidecar",
        str(raster_path),
        "--out-dir",
        str(city_dir),
    ]
    if (
        not from_scratch
        and not resynthesise_corridors
        and raster_path.is_file()
        and corridor_cache.is_file()
    ):
        design_command.extend(
            ["--design-only", "--corridor-cache", str(corridor_cache)]
        )
    if reuse_planned_corridors:
        # A station-rule iteration may reuse only the current source-bound
        # controlled plan, never an unrelated legacy local corridor cache.
        reports={}
        for name in ('core-realignment.json','residential-line-expansion.json'):
            report_path=city_dir/'engineering/alignment'/name
            report=json.loads(report_path.read_text())
            reports[name]=report
            for source,digest in report['sources_sha256'].items():
                if hashlib.sha256((REPO_ROOT/source).read_bytes()).hexdigest()!=digest:
                    raise ValueError('Stale planned corridor input: '+source)
        if not corridor_cache.is_file():raise ValueError('Missing controlled corridor cache: '+slug)
        cached=json.loads(corridor_cache.read_text())
        expansion=reports['residential-line-expansion.json']
        if expansion['city']!=slug or expansion['final_line_count']!=len(cached['lines']) or {
            line['name'] for line in cached['lines']}!={row['line'] for row in reports['core-realignment.json']['lines']}:
            raise ValueError('Corridor cache differs from the controlled line inventory: '+slug)
        if '--design-only' not in design_command:design_command.append('--design-only')
        commands.append(design_command)
    elif not replace_layout:
        # Current-source refresh is the default, including cities with an
        # adopted alignment policy. Layout changes require a separate explicit
        # request; a stale local corridor cache cannot overwrite tracked intent.
        commands.append([sys.executable, str(REPO_ROOT / "tools/automation/refresh-city-design-costs.py"), "--design", str(design_path)])
    elif slug != 'baghdad' and (current_design_logic or (city_dir/'alignment-policy.toml').is_file()):
        if not existing_design:
            # The city-specific planner needs the initial native geometry and
            # design inventory. Never substitute Baghdad's controlled seed.
            initial_command = [value for value in design_command if value != '--design-only']
            if '--corridor-cache' in initial_command:
                index = initial_command.index('--corridor-cache')
                del initial_command[index:index + 2]
            commands.append(initial_command)
        commands.append([sys.executable,str(REPO_ROOT/'tools/automation/rework-city-alignment.py'),'--design',str(design_path),'--prepare-inputs'])
        if not (city_dir/'engineering/alignment/water-source-receipt.json').is_file():
            commands.append([sys.executable,str(REPO_ROOT/'tools/automation/refresh-city-water-evidence.py'),'--design',str(design_path)])
        commands.append([sys.executable,str(REPO_ROOT/'tools/automation/rework-city-alignment.py'),'--design',str(design_path)])
        commands.append([sys.executable,str(REPO_ROOT/'tools/automation/generate-station-water-screen.py'),'--design',str(design_path),'--prepare-grid'])
        if '--design-only' not in design_command:design_command.append('--design-only')
        commands.append(design_command)
    elif slug == 'baghdad':
        commands.append([sys.executable,str(REPO_ROOT/'tools/automation/rework-baghdad-alignment.py')])
        commands.append([sys.executable,str(REPO_ROOT/'tools/automation/generate-station-water-screen.py'),'--design',str(design_path),'--prepare-grid'])
        if '--design-only' not in design_command:design_command.append('--design-only')
        commands.append(design_command)
    else:
        commands.append(design_command)
    for command in commands:
        if "osr_osm.cli" in command:
            with OSM_FETCH_LOCK:
                return_code = run_logged(command, log_path)
        else:
            return_code = run_logged(command, log_path)
        if return_code:
            return {
                "city": slug,
                "duration_seconds": round(time.monotonic() - started, 3),
                "passed": False,
                "phase": "design-synthesis",
                "return_code": return_code,
            }

    missing = [
        str(path.relative_to(city_dir))
        for path in source_artifacts(slug, design_path)
        if not path.is_file()
    ]
    if missing:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"missing source artifacts: {', '.join(missing)}\n")
        return {
            "city": slug,
            "duration_seconds": round(time.monotonic() - started, 3),
            "missing_source_artifacts": missing,
            "passed": False,
            "phase": "prepare",
        }

    commands = [
        [sys.executable, str(REPO_ROOT / "tools/automation/apply-city-overrides.py"), "--design", str(design_path)],
        [
            sys.executable,
            "-m",
            "osr_scenario",
            "--design",
            str(design_path),
            "--out",
            str(city_dir / f"{slug}.toml"),
        ],
        [
            sys.executable,
            "-m",
            "osr_scenario.render_map",
            "--design",
            str(design_path),
        ],
    ]
    if slug != 'baghdad' and (city_dir/'alignment-policy.toml').is_file():
        commands.insert(1,[sys.executable,str(REPO_ROOT/'tools/automation/apply-city-depot-scope.py'),'--design',str(design_path)])
        commands.insert(2,[sys.executable,str(REPO_ROOT/'tools/automation/generate-station-water-screen.py'),'--design',str(design_path)])
    if (city_dir/'station-infill-policy.toml').is_file():
        infill_command=[sys.executable,str(REPO_ROOT/'tools/automation/apply-city-station-infill.py'),'--design',str(design_path)]
        commands.insert(1,infill_command)
        commands.insert(3,infill_command)  # Bind the final depot-priced design.
    # Native final endpoint restoration can alter local curve/product intervals.
    # Reprice the final controlled inventory before emitting operating inputs;
    # validation receipts must be generated only after these edits are complete.
    scenario_index=next(i for i,command in enumerate(commands) if 'osr_scenario' in command)
    # CAPEX reads the scenario's repeated charging-module power. Emit the
    # adopted operating override before repricing so an older scenario cannot
    # silently restore the previous cabinet count. Emit again after pricing
    # to bind the final quantities and source hashes.
    commands.insert(scenario_index, commands[scenario_index].copy())
    scenario_index += 1
    commands.insert(scenario_index,[sys.executable,str(REPO_ROOT/'tools/automation/refresh-local-civil-costs.py'),'--city',slug])
    for command in commands:
        return_code = run_logged(command, log_path)
        if return_code:
            return {
                "city": slug,
                "duration_seconds": round(time.monotonic() - started, 3),
                "passed": False,
                "phase": "prepare",
                "return_code": return_code,
            }
    return {
        "city": slug,
        "duration_seconds": round(time.monotonic() - started, 3),
        "passed": True,
        "phase": "prepare",
        "design_approach": "current-source-controlled-layout-v1",
        "layout_action": "verified-planned-corridor-reuse" if reuse_planned_corridors else "resynthesised" if replace_layout else "retained-controlled-layout",
    }


def finish_city(slug: str, design_path: Path, resilience_jobs: int,
                ci_directory: Path | None = None, ci_commit: str | None = None,
                *, publish_proposal: bool = True) -> dict[str, object]:
    started = time.monotonic()
    city_dir = design_path.parent
    scenario_path = city_dir / f"{slug}.toml"
    operations_dir = city_dir / "operations"
    log_path = LOG_ROOT / f"package-{slug}.log"
    clearance = [sys.executable, str(REPO_ROOT / "tools/automation/audit-viaduct-clearance.py"), "--city", slug]
    if not all((city_dir/'engineering/clearance'/name).is_file() for name in (
            'building-footprints.json.gz', 'building-source.json',
            'terrain-elevation.f32.gz', 'terrain-source.json')):
        clearance += ['--retain-inputs', '--fetch-terrain']
    if (ci_directory is None)!=(ci_commit is None):
        raise ValueError('CI evidence requires its artifact directory and exact commit')
    if ci_directory is not None:
        spec=importlib.util.spec_from_file_location('package_ci',REPO_ROOT/'tools/automation/city-planning-ci.py')
        ci=importlib.util.module_from_spec(spec);spec.loader.exec_module(ci)
        ci.verify(ci_directory,design_path,ci_commit)
        if (city_dir/'engineering/simulation/validation-summary.json').read_bytes()!=(ci_directory/'validation.json').read_bytes():
            raise ValueError('Canonical operating evidence differs from the verified CI artifact: '+slug)
        with log_path.open('a',encoding='utf-8') as handle:
            handle.write(f'Using verified full-day CI planning evidence from {ci_commit}; actual receipts retained.\n')
    commands = [
        [
            sys.executable,
            str(REPO_ROOT / "tools/automation/validate-city-simulation.py"),
            "--scenario",
            str(scenario_path),
            "--resilience",
        ],
        [
            sys.executable,
            str(REPO_ROOT / "tools/automation/render-sim-screenshots.py"),
            "--scenario",
            str(scenario_path),
        ],
        [
            sys.executable,
            str(REPO_ROOT / "tools/automation/generate-qa-maintenance-data.py"),
            "--design",
            str(design_path),
            "--scenario",
            str(scenario_path),
            "--out-dir",
            str(operations_dir),
        ],
        [
            sys.executable,
            str(REPO_ROOT / "tools/automation/generate-acceptance-evidence-report.py"),
            "--bundle",
            str(operations_dir / f"{slug}-operations.json.gz"),
        ],
        [sys.executable, str(REPO_ROOT / "tools/automation/generate-deployment-evidence.py"), "--design", str(design_path), "--reuse-sumo", "--fetch-soils"],
        [sys.executable, str(REPO_ROOT / "engineering/analysis/city_delivery.py"), "--design", str(design_path)],
        [sys.executable, str(REPO_ROOT / "engineering/analysis/city_deployment.py"), "--design", str(design_path)],
        [sys.executable, str(REPO_ROOT / "tools/automation/audit-city-access.py"), "--city", slug, "--fetch-population"],
        [sys.executable, str(REPO_ROOT / "tools/automation/evaluate-residential-expansion.py"), "--design", str(design_path)],
        clearance,
        [
            sys.executable,
            str(REPO_ROOT / "tools/automation/publish-city-summary.py"),
            "--design",
            str(design_path),
            "--scenario",
            str(scenario_path),
            "--out",
            str(city_dir / "README.md"),
        ],
        [
            sys.executable,
            str(REPO_ROOT / "tools/automation/generate-city-federation.py"),
            "--design",
            str(design_path),
        ],
        [
            sys.executable,
            str(REPO_ROOT / "tools/automation/generate-city-design-status.py"),
            "--design",
            str(design_path),
        ],
        [
            sys.executable,
            str(REPO_ROOT / "tools/automation/generate-city-package-manifest.py"),
            "--city-dir",
            str(city_dir),
            "--planning-example",
        ],
    ]
    if slug=='baghdad':
        # The proposal and archives consume the final package manifest. Build
        # them after it so the prominent downloadable views share this run.
        if publish_proposal:
            commands.append([sys.executable,str(REPO_ROOT/'tools/automation/build-baghdad-proposal.py')])
        position=next(i for i,cmd in enumerate(commands) if any('publish-city-summary.py' in part for part in cmd))
        commands[position:position]=[
            [sys.executable,str(REPO_ROOT/'tools/automation/render-baghdad-alignment-review.py')],
            [sys.executable,str(REPO_ROOT/'tools/automation/regenerate-baghdad-studies.py'),'--skip-portfolio']]
    elif (city_dir/'alignment-policy.toml').is_file():
        position=next(i for i,cmd in enumerate(commands) if any('publish-city-summary.py' in part for part in cmd))
        commands[position:position]=[
            [sys.executable,str(REPO_ROOT/'tools/automation/apply-city-depot-scope.py'),'--design',str(design_path),'--report-only'],
            [sys.executable,str(REPO_ROOT/'tools/automation/apply-city-station-infill.py'),'--design',str(design_path),'--report-only'],
            [sys.executable,str(REPO_ROOT/'tools/automation/generate-station-water-screen.py'),'--design',str(design_path)],
            [sys.executable,str(REPO_ROOT/'tools/automation/generate-city-factory-plan.py'),'--design',str(design_path)],
            [sys.executable,str(REPO_ROOT/'tools/automation/render-baghdad-alignment-review.py'),'--design',str(design_path)]]
    # Funding reads deterministic procurement CSVs. Refresh it after operations
    # have produced the current schedule, then bind the twin to final finance.
    commands[3:3] = [
        [sys.executable, str(REPO_ROOT / "tools/automation/generate-city-finance.py"), "--design", str(design_path)],
        [sys.executable, str(REPO_ROOT / "tools/automation/generate-qa-maintenance-data.py"), "--design", str(design_path), "--scenario", str(scenario_path), "--out-dir", str(operations_dir)],
        [sys.executable, str(REPO_ROOT / "tools/automation/generate-city-finance.py"), "--design", str(design_path)],
        [sys.executable, str(REPO_ROOT / "tools/automation/generate-qa-maintenance-data.py"), "--design", str(design_path), "--scenario", str(scenario_path), "--out-dir", str(operations_dir)],
    ]
    commands[2:2] = [
        [sys.executable, str(REPO_ROOT / "tools/automation/generate-depot-scope.py"), "--design", str(design_path)],
        [sys.executable, str(REPO_ROOT / "tools/automation/generate-stabling-plan.py"), "--design", str(design_path)],
    ]
    if ci_directory is not None:
        commands=commands[1:]  # The actual native suite is already verified above.
    for command in commands:
        return_code = run_logged(
            command,
            log_path,
            environment_overrides={"OSR_RESILIENCE_JOBS": str(resilience_jobs)},
        )
        if return_code:
            return {
                "city": slug,
                "duration_seconds": round(time.monotonic() - started, 3),
                "passed": False,
                "phase": "complete-package",
                "return_code": return_code,
            }
    return {
        "city": slug,
        "duration_seconds": round(time.monotonic() - started, 3),
        "passed": True,
        "phase": "complete-package",
    }


def run_parallel(
    selected: dict[str, Path], jobs: int, worker
) -> dict[str, dict[str, object]]:
    results: dict[str, dict[str, object]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {
            executor.submit(worker, slug, design_path): slug
            for slug, design_path in selected.items()
        }
        for future in concurrent.futures.as_completed(futures):
            slug = futures[future]
            try:
                result = future.result()
            except Exception as error:  # keep the remaining cities running
                result = {
                    "city": slug,
                    "error": f"{type(error).__name__}: {error}",
                    "passed": False,
                    "phase": "internal",
                }
            results[slug] = result
            print(f"{'OK' if result['passed'] else 'FAIL':4} {slug} ({result['phase']})", flush=True)
    return results


def finalize_publication(slug: str, design_path: Path) -> dict[str, object]:
    """Reseal presentation after aggregate documents, preserving solver gates."""
    city = design_path.parent
    manifest = [sys.executable, str(REPO_ROOT/'tools/automation/generate-city-package-manifest.py'),
                '--city-dir', str(city), '--planning-example']
    commands = [manifest,
        [sys.executable, str(REPO_ROOT/'tools/automation/publish-city-summary.py'), '--design', str(design_path)],
        [sys.executable, str(REPO_ROOT/'tools/automation/generate-city-federation.py'), '--design', str(design_path)],
        [sys.executable, str(REPO_ROOT/'tools/automation/generate-city-design-status.py'), '--design', str(design_path)],
        manifest]
    if slug == 'baghdad':
        commands.append([sys.executable, str(REPO_ROOT/'tools/automation/build-baghdad-proposal.py')])
    log = LOG_ROOT/f'publication-{slug}.log'
    for command in commands:
        code = run_logged(command, log)
        if code:
            return dict(city=slug, passed=False, phase='final-publication', return_code=code,
                        failed_command=command, manufacturing_release=False)
    return dict(city=slug, passed=True, phase='final-publication', return_code=0,
                manufacturing_release=False)


def engineering_results(selected: set[str]) -> tuple[int, set[str]]:
    if not ENGINEERING_SUMMARY.is_file():
        return 1, set()
    report = json.loads(ENGINEERING_SUMMARY.read_text(encoding="utf-8"))
    rows = {
        str(row.get("city")): row
        for row in report.get("cities", [])
        if str(row.get("city")) in selected
    }
    successful = {
        slug for slug, row in rows.items() if int(row.get("return_code", 1)) == 0
    }
    return (0 if successful == selected else 1), successful


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--only", required=True, help="comma-separated city slugs")
    parser.add_argument(
        "--from-scratch",
        action="store_true",
        help="rebuild OSM/raster/corridor inputs even when caches exist",
    )
    parser.add_argument(
        "--resynthesise-corridors",
        action="store_true",
        help="reroute corridors from cached rasters instead of reusing corridors.json",
    )
    parser.add_argument("--resynthesise-design", action="store_true", help="explicitly replace existing controlled layout from corridor inputs; default refreshes the current design")
    parser.add_argument('--current-design-logic',action='store_true',default=True,help='compatibility flag: current-source generation is the default; replacing an existing layout requires an explicit resynthesis flag')
    parser.add_argument('--prepare-only',action='store_true',help='regenerate layouts/scenarios/maps; retain an explicit incomplete batch receipt until engineering is refreshed')
    parser.add_argument('--finish-only',action='store_true',help='preserve frozen layouts/scenarios and refresh engineering and dependent packages')
    parser.add_argument('--publication-only', action='store_true',
                        help='verify existing planning evidence and reseal presentation after aggregate documents; does not rerun solvers')
    parser.add_argument('--reuse-planned-corridors',action='store_true',help='verify retained plan source hashes and regenerate stations without rerouting')
    parser.add_argument('--native-ci-root',type=Path,help='verified native artifact root containing one folder per city')
    parser.add_argument('--native-ci-commit',help='exact source commit of imported native artifacts')
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    if args.prepare_only and args.finish_only:parser.error('prepare-only and finish-only are mutually exclusive')
    if args.publication_only and any((args.prepare_only, args.finish_only, args.from_scratch,
                                     args.resynthesise_corridors, args.resynthesise_design, args.reuse_planned_corridors)):
        parser.error('publication-only cannot replace or regenerate engineering inputs')
    if args.reuse_planned_corridors and (args.finish_only or args.from_scratch or args.resynthesise_corridors or args.resynthesise_design):
        parser.error('Reusing a controlled plan cannot be combined with route replacement or finish-only')
    if (args.native_ci_root is None)!=(args.native_ci_commit is None):parser.error('native artifact root and exact commit are required together')

    available = discover_designs()
    requested = {slug.strip() for slug in args.only.split(",") if slug.strip()}
    unknown = sorted(requested - set(available))
    if unknown:
        parser.error(f"no canonical design for: {', '.join(unknown)}")
    selected = {slug: available[slug] for slug in sorted(requested)}
    if args.publication_only:
        results = run_parallel(selected, args.jobs, finalize_publication)
        passed = all(row['passed'] for row in results.values())
        atomic_json(SUMMARY_PATH.parent/'publication-summary.json', dict(
            schema_version='1.0', phase='final-publication', passed=passed,
            results=results, manufacturing_release=False, operational_release=False))
        return 0 if passed else 1
    with CATALOG.open("rb") as handle:
        catalog = tomllib.load(handle)
    catalog_cities = {
        str(city["slug"]): city for city in catalog.get("cities", [])
    }
    started = time.monotonic()
    SUMMARY_PATH.unlink(missing_ok=True)

    cost_model_return_code = 0 if args.finish_only else run_logged(
        [sys.executable, str(REPO_ROOT / "tools/automation/generate-civil-cost-model.py")],
        LOG_ROOT / "package-civil-cost-model.log",
    )
    if cost_model_return_code:
        print(f"FAIL civil cost model — see {LOG_ROOT / 'package-civil-cost-model.log'}")
        return 1

    build_return_code = 0 if args.finish_only else run_logged(
        ["cargo", "build", "--release", "--bin", "osr-design"],
        LOG_ROOT / "package-design-build.log",
    )
    if build_return_code:
        print(f"FAIL design generator build — see {LOG_ROOT / 'package-design-build.log'}")
        return 1

    prepared = {slug:dict(city=slug,passed=True,phase='frozen-layout-reuse') for slug in selected} if args.finish_only else run_parallel(
        selected,
        args.jobs,
        lambda slug, path: prepare_city(
            slug,
            path,
            catalog_cities[slug],
            args.from_scratch,
            args.resynthesise_corridors,
            args.resynthesise_design,
            args.current_design_logic,
            args.reuse_planned_corridors,
        ),
    )
    ready = {
        slug: selected[slug] for slug, result in prepared.items() if result["passed"]
    }

    if args.prepare_only:
        atomic_json(SUMMARY_PATH,dict(schema_version='2.0',phase='layouts-only-engineering-refresh-required',
            passed=False,planning_example_complete=False,prepare_results=prepared,
            failed_cities=sorted(set(selected)-set(ready)),prepared_city_count=len(ready),city_count=len(selected)))
        return 0 if len(ready)==len(selected) else 1

    catalog_validation_return_codes: dict[str, int] = {}
    if ready:
        validation_selection = ['--all'] if set(ready) == set(available) else [
            argument for path in ready.values() for argument in ('--design', str(path))]
        catalog_validation_return_codes = {
            "station_clusters": run_logged(
                [
                    sys.executable,
                    str(REPO_ROOT / "tools/automation/validate-station-clusters.py"),
                    *validation_selection,
                ],
                LOG_ROOT / "package-catalog-station-validation.log",
            ),
            "ring_interchanges": run_logged(
                [
                    sys.executable,
                    str(REPO_ROOT / "tools/automation/validate-ring-interchanges.py"),
                    *validation_selection,
                ],
                LOG_ROOT / "package-catalog-ring-validation.log",
            ),
        }

    engineering_return_code = 1
    engineering_ok: set[str] = set()
    if ready:
        ENGINEERING_SUMMARY.unlink(missing_ok=True)
        command = [
            str(REPO_ROOT / "tools/automation/engineering-toolchain.sh"),
            "--cities",
            "--city",
            ",".join(sorted(ready)),
            "--jobs",
            str(args.jobs),
            "--skip-shared-models",
        ]
        engineering_return_code = run_logged(
            command, LOG_ROOT / "package-engineering.log"
        )
        summary_state, engineering_ok = engineering_results(set(ready))
        engineering_return_code = engineering_return_code or summary_state

    resilience_jobs = 4 if args.jobs == 1 else 1
    finished = run_parallel(
        {slug: ready[slug] for slug in sorted(engineering_ok)},
        args.jobs,
        lambda slug, path: finish_city(slug, path, resilience_jobs,
            args.native_ci_root/slug if args.native_ci_root is not None else None,args.native_ci_commit,
            publish_proposal=False),
    )

    drift_return_code = run_logged(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_osr_scenario.py",
            "tests/test_population_drift.py",
            "-q",
        ],
        LOG_ROOT / "package-drift-tests.log",
        cwd=DESIGN_PY,
    )
    complete = {slug for slug, result in finished.items() if result["passed"]}
    ignored_artifacts = ignored_review_artifacts(
        {slug: selected[slug] for slug in sorted(complete)}
    )
    failures = sorted((set(selected) - complete) | set(ignored_artifacts))
    portfolio_return_codes = {}
    if not failures:
        for name in ('generate-national-briefs.py', 'generate-portfolio-summary.py', 'generate-access-clearance-review.py'):
            portfolio_return_codes[name] = run_logged(
                [sys.executable, str(REPO_ROOT / 'tools/automation' / name)],
                LOG_ROOT / ('package-' + name.removesuffix('.py') + '.log'),
            )
            if portfolio_return_codes[name]:
                break
    index_return_code = 0
    if ready:
        index_return_code = run_logged(
            [sys.executable, str(REPO_ROOT / "tools/automation/generate-design-index.py")],
            LOG_ROOT / "package-design-index.log",
        )
    publication_return_codes = {}
    if 'baghdad' in complete and not failures and not any(portfolio_return_codes.values()) and index_return_code == 0:
        # The proposal also archives country briefs and other Iraqi city
        # READMEs, so a batch must finish those dependencies before publication.
        publication_return_codes['baghdad_proposal'] = finalize_publication('baghdad', selected['baghdad'])['return_code']
    summary = {
        "schema_version": "1.0",
        "city_count": len(selected),
        "complete_city_count": len(complete),
        "complete_cities": sorted(complete),
        "catalog_validation_return_codes": catalog_validation_return_codes,
        "design_index_passed": index_return_code == 0,
        "duration_seconds": round(time.monotonic() - started, 3),
        "engineering_return_code": engineering_return_code,
        "portfolio_return_codes": portfolio_return_codes,
        "publication_return_codes": publication_return_codes,
        "failed_cities": failures,
        "ignored_repository_artifacts": ignored_artifacts,
        "passed": (
            not failures
            and drift_return_code == 0
            and not any(catalog_validation_return_codes.values())
            and index_return_code == 0
            and not any(portfolio_return_codes.values())
            and not any(publication_return_codes.values())
        ),
        "prepare_results": prepared,
        "package_results": finished,
        "design_drift_tests_passed": drift_return_code == 0,
    }
    atomic_json(SUMMARY_PATH, summary)
    print(
        f"packages={len(selected)} complete={len(complete)} failed={len(failures)} "
        f"drift_tests={'passed' if drift_return_code == 0 else 'failed'}"
    )
    print(f"summary: {SUMMARY_PATH}")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
