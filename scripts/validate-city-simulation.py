#!/usr/bin/env python3
"""Run OSR simulation evidence and write a city-local validation summary."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
import tomllib
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys_path = REPO_ROOT / "design-py/src"
import sys
sys.path.insert(0, str(sys_path))

from osr_scenario.network_readme import (  # noqa: E402
    _scheduled_daily_train_km,
)


TRAINSET_MANIFEST = REPO_ROOT / "mechanical-py/catalog/buildable-trainset/buildable-trainset-manifest.json"
SMALL_COMPONENT_STANDARD = REPO_ROOT / "mechanical-py/catalog/buildable-trainset/small-component-standard.json"
ROLLING_STOCK_TEMPLATE = REPO_ROOT / "lib/templates/rolling-stock.toml"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_trainset_contract(doc: dict) -> dict:
    """Bind scenario quantities to the shared template and mechanical release."""
    systems = doc.get("consist", {}).get("systems", {})
    with ROLLING_STOCK_TEMPLATE.open("rb") as handle:
        expected = tomllib.load(handle).get("trainset_systems", {})
    standard = json.loads(SMALL_COMPONENT_STANDARD.read_text(encoding="utf-8"))
    manifest = json.loads(TRAINSET_MANIFEST.read_text(encoding="utf-8"))
    issues = []
    for name, value in expected.items():
        if systems.get(name) != value:
            issues.append(
                f"consist.systems.{name}={systems.get(name)!r}; expected {value!r}"
            )
    mechanical_expectations = {
        "mechanical_standard_revision": standard.get("document_revision"),
        "fastener_family_count": len(standard.get("fastener_families", [])),
        "connector_family_count": len(standard.get("connector_families", [])),
        "main_light_modules_per_car": standard.get("lighting", {}).get("main_modules_per_car"),
        "emergency_light_modules_per_car": standard.get("lighting", {}).get("emergency_modules_per_car"),
        "door_threshold_light_modules_per_car": standard.get("lighting", {}).get("door_threshold_modules_per_car"),
    }
    for name, value in mechanical_expectations.items():
        if systems.get(name) != value:
            issues.append(
                f"consist.systems.{name} does not match small-component standard ({value!r})"
            )
    return {
        "passed": not issues,
        "issues": issues,
        "system_configuration": systems,
        "rolling_stock_template": "lib/templates/rolling-stock.toml",
        "rolling_stock_template_sha256": sha256(ROLLING_STOCK_TEMPLATE),
        "small_component_standard": "mechanical-py/catalog/buildable-trainset/small-component-standard.json",
        "small_component_standard_sha256": sha256(SMALL_COMPONENT_STANDARD),
        "buildable_trainset_manifest": "mechanical-py/catalog/buildable-trainset/buildable-trainset-manifest.json",
        "buildable_trainset_manifest_sha256": sha256(TRAINSET_MANIFEST),
        "buildable_product_items": len(manifest.get("product_items", [])),
        "buildable_assemblies": len(manifest.get("assemblies", [])),
    }


def physical_cpu_groups() -> list[tuple[int, ...]]:
    """Return allowed logical CPUs grouped by physical core."""
    if hasattr(os, "sched_getaffinity"):
        allowed = sorted(os.sched_getaffinity(0))
    else:
        allowed = list(range(os.cpu_count() or 1))
    if not sys.platform.startswith("linux"):
        return [(cpu,) for cpu in allowed]

    grouped: dict[tuple[str, str], list[int]] = {}
    for cpu in allowed:
        topology = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology")
        try:
            package = (topology / "physical_package_id").read_text().strip()
            core = (topology / "core_id").read_text().strip()
        except OSError:
            return [(item,) for item in allowed]
        grouped.setdefault((package, core), []).append(cpu)
    return [tuple(cpus) for cpus in grouped.values()]


def event_name(kind: object) -> str:
    if isinstance(kind, str):
        return kind
    if isinstance(kind, dict) and kind:
        return str(next(iter(kind)))
    return "Unknown"


def run_sim(
    scenario: Path,
    duration_s: int,
    output: Path,
    *,
    cpu_set: tuple[int, ...] | None = None,
) -> dict:
    simulator = REPO_ROOT / "target/release/osr-sim"
    command = [
        str(simulator),
        "--config", str(scenario), "--duration", str(duration_s),
        "--status-every", "0", "--json-out", str(output), "--compact-json",
        "--ma-check-every", "0",
    ]
    if cpu_set and sys.platform.startswith("linux"):
        command = ["taskset", "--cpu-list", ",".join(map(str, cpu_set)), *command]
    subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return json.loads(output.read_text())


def scenario_variant(
    source: str,
    path: Path,
    *,
    battery_from: int | None = None,
    battery_to: int | None = None,
    energy_from: float | None = None,
    energy_to: float | None = None,
    contact_fraction: float | None = None,
    fault_toml: str = "",
) -> Path:
    value = source
    if battery_from is not None and battery_to is not None:
        old = f"battery_capacity_kwh = {battery_from}"
        if old not in value:
            raise ValueError(f"could not create battery variant: missing {old!r}")
        value = value.replace(
            old,
            f"battery_capacity_kwh = {battery_to}",
            1,
        )
    if energy_from is not None and energy_to is not None:
        old = f"energy_kwh_per_car_km = {energy_from:.1f}"
        if old not in value:
            raise ValueError(f"could not create energy variant: missing {old!r}")
        value = value.replace(
            old,
            f"energy_kwh_per_car_km = {energy_to:.1f}",
            1,
        )
    if contact_fraction is not None:
        value, replacements = re.subn(
            r"charger_contact_count = (\d+)",
            lambda match: f"charger_contact_count = {max(1, round(int(match.group(1)) * contact_fraction))}",
            value,
        )
        if replacements == 0:
            raise ValueError("could not create contact-loss variant: no charging contacts")
    if fault_toml:
        value = value.rstrip() + "\n\n" + fault_toml.strip() + "\n"
    path.write_text(value, encoding="utf-8")
    return path


def summarize_result(
    label: str, duration: int, result: dict, expected_habd_detectors: int
) -> dict:
    counts = {
        str(name): int(count)
        for name, count in result.get("event_counts", {}).items()
    }
    if not counts:
        for event in result.get("events", []):
            name = event_name(event.get("kind"))
            counts[name] = counts.get(name, 0) + 1
    socs = [float(row[3]) for row in result.get("per_train_final_soc", [])]
    vehicle_systems = result.get("vehicle_systems", {})
    habd_systems = result.get("habd_systems", {})
    habd_active_stop_orders = habd_systems.get("active_stop_orders", [])
    habd_active_speed_restrictions = habd_systems.get(
        "active_speed_restrictions", []
    )
    habd_systems_passed = (
        int(habd_systems.get("detector_count", 0)) == expected_habd_detectors
        and (
            expected_habd_detectors == 0
            or int(habd_systems.get("passages_evaluated", 0)) > 0
        )
        and int(habd_systems.get("warning_passages", 0)) == 0
        and int(habd_systems.get("speed_restrictions_issued", 0)) == 0
        and int(habd_systems.get("trip_passages", 0)) == 0
        and int(habd_systems.get("stop_orders_issued", 0)) == 0
        and len(habd_active_stop_orders) == 0
        and len(habd_active_speed_restrictions) == 0
    )
    balise_systems = result.get("balise_systems", {})
    balise_crossings = int(balise_systems.get("crossing_opportunities", 0))
    balise_audit_findings = sum(
        int(balise_systems.get(field, 0))
        for field in (
            "missed_sightings",
            "position_mismatches",
            "unknown_sightings",
            "stale_findings",
        )
    )
    balise_systems_passed = (
        int(balise_systems.get("registry_count", 0)) > 0
        and balise_crossings > 0
        and int(balise_systems.get("fixes_applied", 0)) == balise_crossings
        and balise_audit_findings == 0
    )
    return {
        "label": label,
        "duration_s": duration,
        "train_km": result["total_train_km"],
        "energy_consumed_kwh": result["total_energy_consumed_kwh"],
        "energy_charged_kwh": result["total_energy_charged_kwh"],
        "depot_services_completed": counts.get("DepotServiceComplete", 0),
        "depot_services_started": counts.get("DepotServiceStart", 0),
        "depot_services_active_at_cutoff": max(0, counts.get("DepotServiceStart", 0) - counts.get("DepotServiceComplete", 0)),
        "minimum_soc_percent": min(socs, default=1.0) * 100.0,
        "onboard_emergencies": int(result.get("onboard", {}).get("emergency_count", 0)),
        "vehicle_systems": vehicle_systems,
        "vehicle_systems_passed": (
            int(vehicle_systems.get("controller_ticks", 0)) > 0
            and int(vehicle_systems.get("door_controller_evaluations", 0)) > 0
            and int(vehicle_systems.get("aux_power_controller_ticks", 0)) > 0
            and int(vehicle_systems.get("hvac_controller_ticks", 0)) > 0
            and int(vehicle_systems.get("lighting_controller_ticks", 0)) > 0
            and int(vehicle_systems.get("pis_controller_ticks", 0)) > 0
            and int(vehicle_systems.get("door_interlock_violations", 0)) == 0
        ),
        "habd_systems": habd_systems,
        "habd_systems_passed": habd_systems_passed,
        "balise_systems": balise_systems,
        "balise_systems_passed": balise_systems_passed,
        "invariant_violations": len(result.get("invariant_violations", [])),
        "soc_warning_events": counts.get("SocWarning", 0),
        "energy_adaptive_dispatches": int(result.get("energy_adaptive_dispatches", 0)),
        "energy_adaptive_headway_added_hours": float(result.get("energy_adaptive_headway_added_s", 0)) / 3600.0,
        "maximum_effective_headway_min": int(result.get("maximum_effective_headway_s", 0)) // 60,
        "trackside_pv_generated_kwh": float(result.get("total_pv_generated_kwh", 0.0)),
        "trackside_grid_imported_kwh": float(result.get("total_grid_imported_kwh", 0.0)),
        "trackside_energy_delivered_kwh": float(result.get("total_delivered_to_trains_kwh", 0.0)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--screenshot-duration", type=int, default=7200)
    parser.add_argument(
        "--full-duration",
        type=int,
        default=90000,
        help="service window plus a 4.5-hour run-out for long ring/charging cycles",
    )
    parser.add_argument("--battery-kwh-override", type=int)
    parser.add_argument("--energy-kwh-per-car-km-override", type=float)
    parser.add_argument("--full-only", action="store_true", help="omit the short screenshot run for sensitivity studies")
    parser.add_argument(
        "--resilience",
        action="store_true",
        help="also require EOL battery, high-ambient duty, charger-contact loss, pad outage and grid outage cases",
    )
    args = parser.parse_args()
    source_scenario = args.scenario.resolve()
    with source_scenario.open("rb") as handle:
        doc = tomllib.load(handle)
    design_path = source_scenario.parent / "design.toml"
    with design_path.open("rb") as handle:
        design = tomllib.load(handle)
    scenario = source_scenario
    slug = source_scenario.stem
    city = str(doc.get("scenario", {}).get("name", slug.title()))
    output = args.output or source_scenario.parent / "engineering/simulation/validation-summary.json"
    resilience_basis: dict[str, object] = {}
    scheduled_train_km = _scheduled_daily_train_km(design, doc)
    fleet_count = sum(int(fleet.get("trainset_count", 0)) for fleet in doc.get("fleets", []))
    configured_habd_detector_count = len(doc.get("habd_detectors", []))
    trainset_contract = validate_trainset_contract(doc)
    subprocess.run(
        ["cargo", "build", "--release", "-p", "osr-sim", "--bin", "osr-sim"],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    core_groups = physical_cpu_groups()
    configured_workers = os.environ.get("OSR_RESILIENCE_JOBS")
    if configured_workers is not None:
        if not configured_workers.isdigit() or int(configured_workers) < 1:
            raise ValueError("OSR_RESILIENCE_JOBS must be a positive integer")
        internal_workers = int(configured_workers)
    else:
        internal_workers = 4
    pin_internal_workers = internal_workers > 1

    with tempfile.TemporaryDirectory() as temporary:
        temporary_path = Path(temporary)
        if args.battery_kwh_override or args.energy_kwh_per_car_km_override:
            source = source_scenario.read_text()
            if args.battery_kwh_override:
                old = f"battery_capacity_kwh = {int(doc['consist']['battery_capacity_kwh'])}"
                new = f"battery_capacity_kwh = {args.battery_kwh_override}"
                if old not in source:
                    raise ValueError(f"could not find {old!r} in {source_scenario}")
                source = source.replace(old, new, 1)
                doc["consist"]["battery_capacity_kwh"] = args.battery_kwh_override
            if args.energy_kwh_per_car_km_override:
                old = f"energy_kwh_per_car_km = {float(doc['consist']['energy_kwh_per_car_km']):.1f}"
                new = f"energy_kwh_per_car_km = {args.energy_kwh_per_car_km_override}"
                if old not in source:
                    raise ValueError(f"could not find {old!r} in {source_scenario}")
                source = source.replace(old, new, 1)
                doc["consist"]["energy_kwh_per_car_km"] = args.energy_kwh_per_car_km_override
            scenario = temporary_path / source_scenario.name
            scenario.write_text(source)
        source = scenario.read_text(encoding="utf-8")
        runs: list[dict] = []
        if not args.full_only:
            nominal_specs: list[tuple[str, int, Path, tuple[int, ...] | None]] = [
                (
                    "2-hour screenshot trace",
                    args.screenshot_duration,
                    temporary_path / "short.json",
                    core_groups[0] if pin_internal_workers else None,
                ),
                (
                    "Full 05:30–02:00 service plus run-out",
                    args.full_duration,
                    temporary_path / "full.json",
                    core_groups[min(1, len(core_groups) - 1)]
                    if pin_internal_workers
                    else None,
                ),
            ]

            def run_nominal(
                spec: tuple[str, int, Path, tuple[int, ...] | None],
            ) -> dict:
                label, duration, path, cpu_set = spec
                result = run_sim(scenario, duration, path, cpu_set=cpu_set)
                return summarize_result(
                    label, duration, result, configured_habd_detector_count
                )

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(2, internal_workers, len(core_groups))
            ) as executor:
                runs = list(executor.map(run_nominal, nominal_specs))
        else:
            result = run_sim(
                scenario,
                args.full_duration,
                temporary_path / "full.json",
                cpu_set=core_groups[0] if pin_internal_workers else None,
            )
            runs.append(
                summarize_result(
                    "Full 05:30–02:00 service plus run-out",
                    args.full_duration,
                    result,
                    configured_habd_detector_count,
                )
            )
            del result
        raw_resilience: list[tuple[str, int, dict, float]] = []
        if args.resilience:
            nominal_battery = int(doc["consist"]["battery_capacity_kwh"])
            nominal_energy = float(doc["consist"]["energy_kwh_per_car_km"])
            climate_name = str(
                design.get("climate", {}).get("preset", "temperate-continental")
            )
            with (REPO_ROOT / "lib/templates/climate.toml").open("rb") as handle:
                climate_presets = tomllib.load(handle).get("presets", {})
            climate_preset = climate_presets.get(climate_name, {})
            ambient_c = float(doc.get("climate", {}).get("ambient_c", 25.0))
            nominal_hvac_uplift = min(max((ambient_c - 25.0) / 25.0, 0.0), 0.25)
            maximum_hvac_uplift = max(
                nominal_hvac_uplift,
                float(climate_preset.get("hvac_uplift_summer_pct", 0.0)),
                float(climate_preset.get("hvac_uplift_winter_pct", 0.0)),
            )
            maximum_climate_energy = math.ceil(
                nominal_energy
                * (1.0 + maximum_hvac_uplift)
                / (1.0 + nominal_hvac_uplift)
                * 10.0
            ) / 10.0
            resilience_basis = {
                "battery_end_of_life_fraction": 0.80,
                "maximum_hvac_uplift_fraction": maximum_hvac_uplift,
                "maximum_climate_energy_kwh_per_car_km": maximum_climate_energy,
                "charging_contact_availability_fraction": 0.50,
                "fault_window": "07:00-17:00",
                "normal_and_single_site_outage_service_floor": 0.90,
                "all_site_grid_outage_emergency_service_floor": 0.60,
            }
            powered_station = next(
                (str(site["station"]) for site in doc.get("sites", []) if site.get("station")),
                None,
            )
            variants = [
                (
                    "80% end-of-life battery capacity",
                    scenario_variant(source, temporary_path / "eol.toml", battery_from=nominal_battery, battery_to=round(nominal_battery * 0.8)),
                    0.90,
                ),
                (
                    "maximum planning climate/HVAC duty",
                    scenario_variant(
                        source,
                        temporary_path / "high-ambient.toml",
                        energy_from=nominal_energy,
                        energy_to=maximum_climate_energy,
                    ),
                    0.90,
                ),
                (
                    "50% charging-contact availability",
                    scenario_variant(source, temporary_path / "contact-loss.toml", contact_fraction=0.5),
                    0.90,
                ),
                (
                    "ten-hour all-site grid outage",
                    scenario_variant(source, temporary_path / "grid-outage.toml", fault_toml='''
[[faults]]
name = "default-grid-outage"
kind = "grid_outage"
from = "07:00"
to = "17:00"
'''),
                    # A ten-hour loss of every grid connection is a network-
                    # wide emergency. Require safe controlled service rather
                    # than pretending storage can reproduce the timetable.
                    0.60,
                ),
            ]
            if powered_station is not None:
                variants.append(
                    (
                        "ten-hour single charging-pad outage",
                        scenario_variant(source, temporary_path / "pad-outage.toml", fault_toml=f'''
[[faults]]
name = "default-pad-outage"
kind = "charging_pad_outage"
from = "07:00"
to = "17:00"
station = "{powered_station}"
'''),
                        0.90,
                    )
                )
            def run_variant(
                assigned_variant: tuple[
                    int, tuple[str, Path, float], tuple[int, ...] | None
                ],
            ) -> tuple[str, int, dict, float]:
                index, (label, variant, minimum_service), cpu_set = assigned_variant
                print(f"resilience: running {label}", flush=True)
                result = run_sim(
                    variant,
                    args.full_duration,
                    temporary_path / f"resilience-{index}.json",
                    cpu_set=cpu_set,
                )
                summary = summarize_result(
                    label,
                    args.full_duration,
                    result,
                    configured_habd_detector_count,
                )
                del result
                print(f"resilience: completed {label}", flush=True)
                return label, args.full_duration, summary, minimum_service

            # Each case is independent. Compact result files remove the old
            # multi-gigabyte memory constraint, so allocate one physical core
            # (including its sibling logical CPUs) to each concurrent case.
            resilience_workers = min(
                internal_workers, len(core_groups), len(variants)
            )
            indexed_variants = list(enumerate(variants))
            for start in range(0, len(indexed_variants), resilience_workers):
                batch = indexed_variants[start:start + resilience_workers]
                assigned = [
                    (
                        index,
                        variant,
                        core_groups[offset] if pin_internal_workers else None,
                    )
                    for offset, (index, variant) in enumerate(batch)
                ]
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=len(assigned)
                ) as executor:
                    raw_resilience.extend(executor.map(run_variant, assigned))

    schedules = doc.get("fleets", [{}])[0].get("schedule", [])
    full_run = runs[-1]
    full_run["scheduled_train_km"] = scheduled_train_km
    full_run["raw_service_completion_ratio"] = full_run["train_km"] / scheduled_train_km
    full_run["service_completion_ratio"] = min(
        1.0, full_run["raw_service_completion_ratio"]
    )
    # The analytical schedule assumes exact line length for every departure;
    # the simulator measures actual motion and legitimately finishes short
    # where the final dispatched train is held by reserve/occupancy gates.
    # Ninety percent is the planning-screen floor; calibrated timetable
    # acceptance remains a later operator gate. A 0.2 percentage-point
    # numerical tolerance covers discrete one-second dispatch/arrival
    # boundaries at the 4.5-hour run-out cutoff.
    minimum_service_completion_ratio = 0.90
    service_completion_tolerance = 0.002
    resilience_cases = []
    for _label, _duration, summary, minimum_service in raw_resilience:
        case = dict(summary)
        case["scheduled_train_km"] = scheduled_train_km
        case["raw_service_completion_ratio"] = case["train_km"] / scheduled_train_km
        case["service_completion_ratio"] = min(
            1.0, case["raw_service_completion_ratio"]
        )
        case["minimum_service_completion_ratio"] = minimum_service
        case["passed"] = (
            case["minimum_soc_percent"] >= 20.0 - 1e-3
            and case["invariant_violations"] == 0
            and case["onboard_emergencies"] == 0
            and case["vehicle_systems_passed"]
            and case["habd_systems_passed"]
            and case["balise_systems_passed"]
            and case["service_completion_ratio"] + service_completion_tolerance >= minimum_service
        )
        resilience_cases.append(case)
    nominal_passed = all(
        run["minimum_soc_percent"] >= 20.0 - 1e-3
        and run["invariant_violations"] == 0
        and run["onboard_emergencies"] == 0
        and run["vehicle_systems_passed"]
        and run["habd_systems_passed"]
        and run["balise_systems_passed"]
        for run in runs
    ) and full_run["service_completion_ratio"] + service_completion_tolerance >= minimum_service_completion_ratio
    resilience_passed = bool(resilience_cases) and all(case["passed"] for case in resilience_cases)
    simulator_binary = REPO_ROOT / "target/release/osr-sim"
    model = {
        "schema_version": "1.5",
        "city": city,
        "validated_on": date.today().isoformat(),
        "generator": str(Path(__file__).resolve().relative_to(REPO_ROOT)),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "simulator_binary": "target/release/osr-sim",
        "simulator_sha256": sha256(simulator_binary),
        "design_sha256": sha256(design_path),
        "scenario": "../../../" + source_scenario.name,
        "scenario_sha256": sha256(source_scenario),
        "passed": trainset_contract["passed"] and nominal_passed and (not args.resilience or resilience_passed),
        "trainset_contract": trainset_contract,
        "model": {
            "trainsets": fleet_count,
            "battery_nameplate_kwh": int(doc["consist"]["battery_capacity_kwh"]),
            "protected_reserve_percent": 20,
            "nominal_energy_kwh_per_car_km_before_climate": float(doc["consist"]["energy_kwh_per_car_km"]),
            "depot_service_seconds": int(doc["scenario"]["depot_service_seconds"]),
            "minimum_service_completion_ratio": minimum_service_completion_ratio,
            "service_completion_numerical_tolerance": service_completion_tolerance,
            "energy_adaptive_service": bool(doc["scenario"].get("energy_adaptive_service", False)),
            "normal_service_soc_percent": float(doc["scenario"].get("normal_service_soc", 0.40)) * 100.0,
            "maximum_headway_multiplier": float(doc["scenario"].get("maximum_headway_multiplier", 3.0)),
            "protected_peak_headway_min": int(doc["scenario"].get("protected_peak_headway_min", 3)),
            "configured_habd_detector_count": configured_habd_detector_count,
        },
        "service_windows": [
            {"from": row["from"], "to": row["to"], "headway_min": row["headway_min"], "treatment": "peak quick turnaround" if (str(row["from"]) in {"07:00", "15:00"} and int(row["headway_min"]) == 3) else "off-peak depot service enabled"}
            for row in schedules
        ],
        "runs": runs,
        "resilience_required": args.resilience,
        "resilience_passed": resilience_passed if args.resilience else None,
        "resilience_basis": resilience_basis if args.resilience else None,
        "resilience_cases": resilience_cases,
        "interpretation": "The full-window run includes 4.5 hours after the 02:00 service close so long ring and charging cycles can finish. Door, auxiliary-power, HVAC, lighting and onboard PIS controllers execute for every train tick; their loads remain included in the calibrated aggregate kWh/car-km model and are not debited twice. Configured physical HABD sites must execute in every run without a nominal trip or latched stop. The topology-derived wayside balise registry must feed every expected crossing into onboard odometry with no nominal sighting-audit finding. Nominal and N-1/degraded screens protect 20% SoC and at least 90% of scheduled train-km. The ten-hour all-site grid outage is an emergency reduced-service case with a 60% floor. Energy-adaptive control may widen off-peak headways; calibrated timetable acceptance remains an operator gate.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(model, indent=2) + "\n")
    print(f"wrote {output} (passed={model['passed']})")
    return 0 if model["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
