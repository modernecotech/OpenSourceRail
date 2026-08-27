#!/usr/bin/env python3
"""Resynthesise designs and refresh complete canonical city packages."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGN_PY = REPO_ROOT / "design-py"
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
    for path in sorted((REPO_ROOT / "designs").glob("*/*/*/design.toml")):
        with path.open("rb") as handle:
            design = tomllib.load(handle)
        slug = str(design.get("city", {}).get("slug", "")).strip()
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
        engineering / "gis/summary.json",
        engineering / "ring-interchange-summary.json",
        engineering / "screenshots/manifest.json",
        engineering / "simulation/validation-summary.json",
        engineering / "station-cluster-summary.json",
        engineering / "station-product-map.json",
        engineering / "sumo/summary.json",
        operations / "acceptance-evidence-report.md",
        operations / f"{slug}-assets.csv",
        operations / f"{slug}-operations-manifest.json",
    ]
    artifacts.extend(sorted((engineering / "alignment").glob("*.aln.toml")))
    artifacts.extend(sorted((engineering / "gis/layers").glob("*.geojson")))
    artifacts.extend(sorted((engineering / "screenshots").glob("*.png")))
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
    if from_scratch or not raster_path.is_file():
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
    }


def finish_city(slug: str, design_path: Path, resilience_jobs: int) -> dict[str, object]:
    started = time.monotonic()
    city_dir = design_path.parent
    scenario_path = city_dir / f"{slug}.toml"
    operations_dir = city_dir / "operations"
    log_path = LOG_ROOT / f"package-{slug}.log"
    commands = [
        [
            sys.executable,
            str(REPO_ROOT / "scripts/validate-city-simulation.py"),
            "--scenario",
            str(scenario_path),
            "--resilience",
        ],
        [
            sys.executable,
            str(REPO_ROOT / "scripts/render-sim-screenshots.py"),
            "--scenario",
            str(scenario_path),
        ],
        [
            sys.executable,
            str(REPO_ROOT / "scripts/generate-qa-maintenance-data.py"),
            "--design",
            str(design_path),
            "--scenario",
            str(scenario_path),
            "--out-dir",
            str(operations_dir),
        ],
        [
            sys.executable,
            str(REPO_ROOT / "scripts/generate-acceptance-evidence-report.py"),
            "--bundle",
            str(operations_dir / f"{slug}-operations.json.gz"),
        ],
        [
            sys.executable,
            "-m",
            "osr_scenario.network_readme",
            "--design",
            str(design_path),
            "--scenario",
            str(scenario_path),
            "--out",
            str(city_dir / "README.md"),
        ],
        [
            sys.executable,
            str(REPO_ROOT / "scripts/generate-city-package-manifest.py"),
            "--city-dir",
            str(city_dir),
        ],
    ]
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
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")

    available = discover_designs()
    requested = {slug.strip() for slug in args.only.split(",") if slug.strip()}
    unknown = sorted(requested - set(available))
    if unknown:
        parser.error(f"no canonical design for: {', '.join(unknown)}")
    selected = {slug: available[slug] for slug in sorted(requested)}
    full_catalog_run = requested == set(available)
    with CATALOG.open("rb") as handle:
        catalog = tomllib.load(handle)
    catalog_cities = {
        str(city["slug"]): city for city in catalog.get("cities", [])
    }
    started = time.monotonic()
    SUMMARY_PATH.unlink(missing_ok=True)

    cost_model_return_code = run_logged(
        [sys.executable, str(REPO_ROOT / "scripts/generate-civil-cost-model.py")],
        LOG_ROOT / "package-civil-cost-model.log",
    )
    if cost_model_return_code:
        print(f"FAIL civil cost model — see {LOG_ROOT / 'package-civil-cost-model.log'}")
        return 1

    build_return_code = run_logged(
        ["cargo", "build", "--release", "--bin", "osr-design"],
        LOG_ROOT / "package-design-build.log",
    )
    if build_return_code:
        print(f"FAIL design generator build — see {LOG_ROOT / 'package-design-build.log'}")
        return 1

    prepared = run_parallel(
        selected,
        args.jobs,
        lambda slug, path: prepare_city(
            slug,
            path,
            catalog_cities[slug],
            args.from_scratch,
            args.resynthesise_corridors,
        ),
    )
    ready = {
        slug: selected[slug] for slug, result in prepared.items() if result["passed"]
    }

    catalog_validation_return_codes: dict[str, int] = {}
    if full_catalog_run:
        catalog_validation_return_codes = {
            "station_clusters": run_logged(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts/validate-station-clusters.py"),
                    "--all",
                ],
                LOG_ROOT / "package-catalog-station-validation.log",
            ),
            "ring_interchanges": run_logged(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts/validate-ring-interchanges.py"),
                    "--all",
                ],
                LOG_ROOT / "package-catalog-ring-validation.log",
            ),
        }

    engineering_return_code = 1
    engineering_ok: set[str] = set()
    if ready:
        ENGINEERING_SUMMARY.unlink(missing_ok=True)
        command = [
            str(REPO_ROOT / "scripts/engineering-toolchain.sh"),
            "--cities",
            "--city",
            ",".join(sorted(ready)),
            "--jobs",
            str(args.jobs),
            "--resume",
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
        lambda slug, path: finish_city(slug, path, resilience_jobs),
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
    index_return_code = 0
    if full_catalog_run:
        index_return_code = run_logged(
            [sys.executable, str(REPO_ROOT / "scripts/generate-design-index.py")],
            LOG_ROOT / "package-design-index.log",
        )
    summary = {
        "schema_version": "1.0",
        "city_count": len(selected),
        "complete_city_count": len(complete),
        "complete_cities": sorted(complete),
        "catalog_validation_return_codes": catalog_validation_return_codes,
        "design_index_passed": index_return_code == 0,
        "duration_seconds": round(time.monotonic() - started, 3),
        "engineering_return_code": engineering_return_code,
        "failed_cities": failures,
        "ignored_repository_artifacts": ignored_artifacts,
        "passed": (
            not failures
            and drift_return_code == 0
            and not any(catalog_validation_return_codes.values())
            and index_return_code == 0
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
