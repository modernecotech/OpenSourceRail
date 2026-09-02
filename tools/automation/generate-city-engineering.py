#!/usr/bin/env python3
"""Generate GIS, SUMO, energy and product-map packages for OSR cities."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "engineering/analysis/benchmarks/sumo/city_timetable.py"
GIS_RUNNER = REPO_ROOT / "engineering/analysis/city_package.py"
ENERGY_RUNNER = REPO_ROOT / "engineering/analysis/city_microgrid.py"
VISUAL_RUNNER = REPO_ROOT / "tools/automation/render-city-engineering.py"
RING_INTERCHANGE_RUNNER = REPO_ROOT / "tools/automation/validate-ring-interchanges.py"
STATION_CLUSTER_RUNNER = REPO_ROOT / "tools/automation/validate-station-clusters.py"
CLIMATE_PRESETS = REPO_ROOT / "lib/templates/climate.toml"
FINANCE_RUNNER = REPO_ROOT / "tools/automation/generate-city-finance.py"
ALIGNMENT_SOURCE = REPO_ROOT / "tools/osr-aln-convert/src"
ALIGNMENT_DESIGN_DATE = "2026-08-12"
STATION_IFC_RUNNER = REPO_ROOT / "engineering/interchange/station_ifc.py"
PEDESTRIAN_RUNNER = REPO_ROOT / "engineering/analysis/benchmarks/jupedsim/station-corridor.py"
STATION_SYSTEMS_RUNNER = REPO_ROOT / "engineering/analysis/stations/station_systems.py"
STATION_MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
SHARED_OUTPUT_ROOT = REPO_ROOT / "build/engineering/shared"
BATCH_SUMMARY = REPO_ROOT / "build/engineering/cities/batch-summary.json"
LOG_ROOT = REPO_ROOT / "build/engineering/cities"


def city_output_root(design_path: Path) -> Path:
    """Keep every city-specific engineering artifact beside its design."""

    return design_path.resolve().parent / "engineering"


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def discover_designs() -> dict[str, Path]:
    designs: dict[str, Path] = {}
    for path in sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        slug = str(data.get("city", {}).get("slug", "")).strip()
        if not slug:
            raise RuntimeError(f"{path}: missing city.slug")
        if slug in designs:
            raise RuntimeError(f"duplicate city slug {slug}: {designs[slug]} and {path}")
        designs[slug] = path
    return designs


def write_station_product_map(slug: str, design_path: Path) -> dict[str, object]:
    design = tomllib.loads(design_path.read_text(encoding="utf-8"))
    manifest = json.loads(STATION_MANIFEST.read_text(encoding="utf-8"))
    variants = {variant["archetype"]: variant for variant in manifest["variants"]}
    open_items: dict[str, int] = {}
    for item in manifest.get("open_release_items", []):
        archetype = str(item["archetype"])
        open_items[archetype] = open_items.get(archetype, 0) + 1
    station_rows: list[dict[str, object]] = []
    missing_variants: list[dict[str, str]] = []
    for station in design.get("stations", []):
        archetype = str(station.get("archetype", ""))
        variant = variants.get(archetype)
        if variant is None:
            missing_variants.append({"station_id": str(station.get("id")), "archetype": archetype})
            continue
        station_rows.append(
            {
                "archetype": archetype,
                "assembly_count": len(variant["assemblies"]),
                "line": station["line"],
                "open_release_item_count": open_items.get(archetype, 0),
                "platform_length_m": station.get("platform_length_m"),
                "product_item_count": len(variant["product_items"]),
                "s_m": station["s_m"],
                "shared_ifc_template": f"build/engineering/interchange/stations/station-{archetype}.ifc",
                "site_specific_ifc_status": "placement-and-geometry-pending",
                "station_id": station["id"],
            }
        )
    report = {
        "city": slug,
        "design_sha256": hashlib.sha256(design_path.read_bytes()).hexdigest(),
        "manifest": str(STATION_MANIFEST.relative_to(REPO_ROOT)),
        "manifest_sha256": hashlib.sha256(STATION_MANIFEST.read_bytes()).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "mapped_station_count": len(station_rows),
        "missing_variants": missing_variants,
        "passed": not missing_variants and len(station_rows) == len(design.get("stations", [])),
        "stations": station_rows,
    }
    atomic_json(city_output_root(design_path) / "station-product-map.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="process every design.toml")
    selection.add_argument("--city", action="append", help="city slug; repeat or use commas")
    selection.add_argument(
        "--design",
        type=Path,
        help="process one design.toml directly, including generated designs under build/",
    )
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--generate-only", action="store_true")
    parser.add_argument("--allow-input-gaps", action="store_true")
    parser.add_argument("--services-per-direction", type=int, default=2)
    parser.add_argument("--skip-shared-models", action="store_true")
    parser.add_argument("--skip-gis", action="store_true")
    parser.add_argument("--skip-energy", action="store_true")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    if args.services_per_direction < 1:
        parser.error("--services-per-direction must be positive")
    if args.retries < 0:
        parser.error("--retries cannot be negative")

    available = discover_designs()
    if args.design:
        design_path = args.design.resolve()
        if not design_path.is_file():
            parser.error(f"design file not found: {design_path}")
        design = tomllib.loads(design_path.read_text(encoding="utf-8"))
        slug = str(design.get("city", {}).get("slug", "")).strip()
        if not slug:
            parser.error(f"{design_path}: missing city.slug")
        selected = {slug: design_path}
    elif args.all:
        selected = available
    else:
        requested = {slug for value in args.city for slug in value.split(",") if slug}
        unknown = sorted(requested - set(available))
        if unknown:
            parser.error(f"unknown city slug(s): {', '.join(unknown)}")
        selected = {slug: available[slug] for slug in sorted(requested)}

    shared_models: dict[str, object] = {"status": "skipped"}
    if not args.skip_shared_models:
        commands = {
            "station_ifc": [sys.executable, str(STATION_IFC_RUNNER), "--all-variants"],
            "pedestrian": [sys.executable, str(PEDESTRIAN_RUNNER)],
            "station_systems": [sys.executable, str(STATION_SYSTEMS_RUNNER)],
        }
        shared_results: dict[str, int] = {}
        for name, command in commands.items():
            completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            log = SHARED_OUTPUT_ROOT / f"{name}.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(completed.stdout, encoding="utf-8")
            shared_results[name] = completed.returncode
            if completed.returncode:
                print(f"FAIL shared {name} — see {log}", file=sys.stderr)
                return 1
        shared_models = {"results": shared_results, "status": "generated-and-checked"}

    def run_one(item: tuple[str, Path], attempt: int) -> dict[str, object]:
        slug, design_path = item
        output_root = city_output_root(design_path)
        log_root = LOG_ROOT / slug
        city_output = output_root / "sumo"
        sumo_command = [
            sys.executable,
            str(RUNNER),
            "--design",
            str(design_path),
            "--output-dir",
            str(city_output),
            "--services-per-direction",
            str(args.services_per_direction),
        ]
        if args.generate_only:
            sumo_command.append("--generate-only")
        if args.allow_input_gaps:
            sumo_command.append("--allow-input-gaps")
        commands: list[tuple[str, list[str]]] = [
            (
                "station_clusters",
                [
                    sys.executable,
                    str(STATION_CLUSTER_RUNNER),
                    "--design",
                    str(design_path),
                    "--output",
                    str(output_root / "station-cluster-summary.json"),
                ],
            ),
            (
                "ring_interchanges",
                [
                    sys.executable,
                    str(RING_INTERCHANGE_RUNNER),
                    "--design",
                    str(design_path),
                    "--output",
                    str(output_root / "ring-interchange-summary.json"),
                ],
            ),
            ("sumo", sumo_command),
        ]
        commands.extend(
            [
                (
                    "alignment",
                    [
                        sys.executable,
                        "-m",
                        "osr_aln.current_network",
                        "--design",
                        str(design_path),
                        "--geojson",
                        str(design_path.parent / f"{slug}.corridor.geojson"),
                        "--output-dir",
                        str(output_root / "alignment"),
                        "--design-date",
                        ALIGNMENT_DESIGN_DATE,
                    ],
                ),
                (
                    "finance",
                    [
                        sys.executable,
                        str(FINANCE_RUNNER),
                        "--design",
                        str(design_path),
                        "--scenario",
                        str(design_path.parent / f"{slug}.toml"),
                    ],
                ),
            ]
        )
        if not args.skip_gis:
            gis_command = [
                sys.executable,
                str(GIS_RUNNER),
                "--design",
                str(design_path),
                "--output-dir",
                str(output_root / "gis"),
            ]
            if args.allow_input_gaps:
                gis_command.append("--allow-input-gaps")
            commands.append(("gis", gis_command))
        if not args.skip_energy:
            commands.append(
                (
                    "energy",
                    [
                        sys.executable,
                        str(ENERGY_RUNNER),
                        "--design",
                        str(design_path),
                        "--output-dir",
                        str(output_root / "energy"),
                    ],
                )
            )
        if not args.generate_only and not args.skip_gis and not args.skip_energy:
            commands.append(
                (
                    "visuals",
                    [sys.executable, str(VISUAL_RUNNER), "--design", str(design_path)],
                )
            )
        outputs: list[str] = []
        tool_return_codes: dict[str, int] = {}
        for name, command in commands:
            environment = os.environ.copy()
            if name == "alignment":
                environment["PYTHONPATH"] = str(ALIGNMENT_SOURCE)
            completed = subprocess.run(
                command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                env=environment,
            )
            tool_return_codes[name] = completed.returncode
            outputs.append(f"===== {name} =====\n{completed.stdout}")
            tool_log = log_root / f"{name}.log"
            tool_log.parent.mkdir(parents=True, exist_ok=True)
            tool_log.write_text(completed.stdout, encoding="utf-8")
            if completed.returncode:
                break
        combined_output = "\n".join(outputs)
        log_root.mkdir(parents=True, exist_ok=True)
        log = log_root / "generation.log"
        log.write_text(combined_output, encoding="utf-8")
        (log_root / f"generation-attempt-{attempt}.log").write_text(
            combined_output, encoding="utf-8"
        )
        summary_path = city_output / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
        gis_summary_path = output_root / "gis/summary.json"
        energy_summary_path = output_root / "energy/summary.json"
        visual_manifest_path = output_root / "screenshots/manifest.json"
        ring_summary_path = output_root / "ring-interchange-summary.json"
        station_cluster_summary_path = output_root / "station-cluster-summary.json"
        gis_summary = (
            json.loads(gis_summary_path.read_text(encoding="utf-8"))
            if gis_summary_path.is_file() and not args.skip_gis
            else {}
        )
        energy_summary = (
            json.loads(energy_summary_path.read_text(encoding="utf-8"))
            if energy_summary_path.is_file() and not args.skip_energy
            else {}
        )
        station_map = write_station_product_map(slug, design_path)
        return_code = 0 if all(code == 0 for code in tool_return_codes.values()) and station_map["passed"] else 1
        return {
            "attempts": attempt,
            "city": slug,
            "input_issue_count": len(summary.get("input_issues", [])),
            "gis_generation_passed": True if args.skip_gis else bool(gis_summary.get("generation_passed")),
            "energy_solver_passed": True if args.skip_energy else bool(energy_summary.get("solver_passed")),
            "energy_finding_count": len(energy_summary.get("design_findings", [])),
            "line_count": summary.get("line_count", 0),
            "return_code": return_code,
            "simulation_status": summary.get("simulation_status", "failed-before-summary"),
            "station_product_map_passed": station_map["passed"],
            "station_count": summary.get("station_count", 0),
            "tool_return_codes": tool_return_codes,
        }

    def run_round(
        items: list[tuple[str, Path]], workers: int, attempt: int
    ) -> list[dict[str, object]]:
        round_results: list[dict[str, object]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(run_one, item, attempt): item[0] for item in items}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                round_results.append(result)
                state = "OK" if result["return_code"] == 0 else "FAIL"
                print(
                    f"{state:4} {result['city']} ({result['line_count']} lines, "
                    f"{result['station_count']} stations, {result['input_issue_count']} input issues, "
                    f"attempt {attempt})"
                )
        return round_results

    results_by_city: dict[str, dict[str, object]] = {}
    pending_items: list[tuple[str, Path]] = []
    for slug, design_path in selected.items():
        output_root = city_output_root(design_path)
        summary_path = output_root / "sumo/summary.json"
        station_map_path = output_root / "station-product-map.json"
        gis_summary_path = output_root / "gis/summary.json"
        energy_summary_path = output_root / "energy/summary.json"
        visual_manifest_path = output_root / "screenshots/manifest.json"
        ring_summary_path = output_root / "ring-interchange-summary.json"
        station_cluster_summary_path = output_root / "station-cluster-summary.json"
        if args.resume and not args.generate_only and summary_path.is_file():
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            current_hash = hashlib.sha256(design_path.read_bytes()).hexdigest()
            corridor_path = design_path.parent / f"{slug}.corridor.geojson"
            scenario_path = design_path.parent / f"{slug}.toml"
            corridor_hash = hashlib.sha256(corridor_path.read_bytes()).hexdigest()
            scenario_hash = hashlib.sha256(scenario_path.read_bytes()).hexdigest()
            if (
                summary.get("simulation_passed")
                and summary.get("design_sha256") == current_hash
                and summary.get("corridor_sha256") == corridor_hash
                and summary.get("generator_sha256")
                == hashlib.sha256(RUNNER.read_bytes()).hexdigest()
            ):
                station_map_passed = False
                if station_map_path.is_file():
                    station_map_summary = json.loads(
                        station_map_path.read_text(encoding="utf-8")
                    )
                    station_map_passed = bool(station_map_summary.get("passed")) and (
                        station_map_summary.get("design_sha256") == current_hash
                    ) and (
                        station_map_summary.get("manifest_sha256")
                        == hashlib.sha256(STATION_MANIFEST.read_bytes()).hexdigest()
                    ) and (
                        station_map_summary.get("generator_sha256")
                        == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
                    )
                gis_current = args.skip_gis
                if gis_summary_path.is_file() and not args.skip_gis:
                    gis_summary = json.loads(gis_summary_path.read_text(encoding="utf-8"))
                    gis_current = bool(gis_summary.get("generation_passed")) and (
                        gis_summary.get("design_sha256") == current_hash
                    ) and (gis_summary.get("corridor_sha256") == corridor_hash) and (
                        gis_summary.get("scenario_sha256") == scenario_hash
                    ) and (
                        gis_summary.get("generator_sha256")
                        == hashlib.sha256(GIS_RUNNER.read_bytes()).hexdigest()
                    )
                energy_current = args.skip_energy
                if energy_summary_path.is_file() and not args.skip_energy:
                    energy_summary = json.loads(energy_summary_path.read_text(encoding="utf-8"))
                    energy_current = bool(energy_summary.get("solver_passed")) and (
                        energy_summary.get("design_sha256") == current_hash
                    ) and (energy_summary.get("scenario_sha256") == scenario_hash)
                    energy_current = energy_current and (
                        energy_summary.get("climate_sha256")
                        == hashlib.sha256(CLIMATE_PRESETS.read_bytes()).hexdigest()
                    ) and (
                        energy_summary.get("generator_sha256")
                        == hashlib.sha256(ENERGY_RUNNER.read_bytes()).hexdigest()
                    )
                ring_current = False
                if ring_summary_path.is_file():
                    ring_report = json.loads(ring_summary_path.read_text(encoding="utf-8"))
                    ring_results = ring_report.get("results", [])
                    ring_result = ring_results[0] if len(ring_results) == 1 else {}
                    ring_current = bool(ring_report.get("passed")) and (
                        ring_result.get("design_sha256") == current_hash
                    ) and (
                        ring_result.get("corridor_sha256") == corridor_hash
                    ) and (
                        ring_result.get("generator_sha256")
                        == hashlib.sha256(RING_INTERCHANGE_RUNNER.read_bytes()).hexdigest()
                    )
                station_clusters_current = False
                if station_cluster_summary_path.is_file():
                    cluster_report = json.loads(
                        station_cluster_summary_path.read_text(encoding="utf-8")
                    )
                    cluster_results = cluster_report.get("results", [])
                    cluster_result = cluster_results[0] if len(cluster_results) == 1 else {}
                    station_clusters_current = bool(cluster_report.get("passed")) and (
                        cluster_result.get("design_sha256") == current_hash
                    ) and (
                        cluster_result.get("generator_sha256")
                        == hashlib.sha256(STATION_CLUSTER_RUNNER.read_bytes()).hexdigest()
                    )
                visuals_current = args.generate_only or args.skip_gis or args.skip_energy
                if visual_manifest_path.is_file() and not visuals_current:
                    visual_manifest = json.loads(visual_manifest_path.read_text(encoding="utf-8"))
                    visual_sources = visual_manifest.get("sources", {})
                    visuals_current = bool(visual_manifest.get("passed")) and (
                        visual_manifest.get("generator_sha256")
                        == hashlib.sha256(VISUAL_RUNNER.read_bytes()).hexdigest()
                    ) and (
                        visual_sources.get("design_sha256") == current_hash
                    ) and (
                        visual_sources.get("scenario_sha256") == scenario_hash
                    ) and all(
                        (output_root / "screenshots" / item.get("path", "")).is_file()
                        and hashlib.sha256(
                            (output_root / "screenshots" / item.get("path", "")).read_bytes()
                        ).hexdigest() == item.get("sha256")
                        for item in visual_manifest.get("screenshots", {}).values()
                    )
                if station_map_passed and gis_current and energy_current and visuals_current and ring_current and station_clusters_current:
                    results_by_city[slug] = {
                        "attempts": 0,
                        "city": slug,
                        "input_issue_count": len(summary.get("input_issues", [])),
                        "gis_generation_passed": True,
                        "energy_solver_passed": True,
                        "energy_finding_count": (
                            0 if args.skip_energy else len(energy_summary.get("design_findings", []))
                        ),
                        "line_count": summary.get("line_count", 0),
                        "return_code": 0,
                        "simulation_status": summary.get("simulation_status"),
                        "station_product_map_passed": True,
                        "station_count": summary.get("station_count", 0),
                        "tool_return_codes": {},
                    }
                    continue
        pending_items.append((slug, design_path))
    if results_by_city:
        print(f"resume: reusing {len(results_by_city)} current successful city summaries")
    for result in run_round(pending_items, args.jobs, 1):
        results_by_city[str(result["city"])] = result
    if not args.generate_only:
        for retry_index in range(1, args.retries + 1):
            failed_slugs = sorted(
                slug for slug, result in results_by_city.items() if result["return_code"] != 0
            )
            if not failed_slugs:
                break
            retry_workers = 2 if retry_index == 1 else 1
            print(
                f"retry {retry_index}/{args.retries}: {len(failed_slugs)} cities "
                f"with jobs={retry_workers}"
            )
            retry_items = [(slug, selected[slug]) for slug in failed_slugs]
            for result in run_round(retry_items, retry_workers, retry_index + 1):
                results_by_city[str(result["city"])] = result

    results = sorted(results_by_city.values(), key=lambda result: str(result["city"]))
    failures = [result for result in results if result["return_code"] != 0]
    aggregate = {
        "city_count": len(results),
        "cities": results,
        "failed_cities": [result["city"] for result in failures],
        "generate_only": args.generate_only,
        "input_issue_count": sum(int(result["input_issue_count"]) for result in results),
        "energy_finding_count": sum(int(result["energy_finding_count"]) for result in results),
        "gis_enabled": not args.skip_gis,
        "energy_enabled": not args.skip_energy,
        "line_count": sum(int(result["line_count"]) for result in results),
        "shared_models": shared_models,
        "execution_passed": not failures,
        "input_quality_passed": sum(int(result["input_issue_count"]) for result in results) == 0,
        "passed": not failures and sum(int(result["input_issue_count"]) for result in results) == 0,
        "station_count": sum(int(result["station_count"]) for result in results),
    }
    atomic_json(BATCH_SUMMARY, aggregate)
    print(
        f"cities={aggregate['city_count']} lines={aggregate['line_count']} "
        f"stations={aggregate['station_count']} input_issues={aggregate['input_issue_count']} "
        f"failures={len(failures)}"
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
