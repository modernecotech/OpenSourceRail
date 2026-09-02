"""Regression checks for the tracked station-system screening package."""

from __future__ import annotations

import importlib.util
import json
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "engineering/analysis/stations/station_systems.py"
SUMMARY_PATH = MODULE_PATH.with_name("screening-summary.json")
SPEC = importlib.util.spec_from_file_location("station_systems", MODULE_PATH)
assert SPEC and SPEC.loader
station_systems = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(station_systems)


def test_station_screening_summary_is_current_and_explicitly_not_released() -> None:
    report = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    assert report["schema_version"] == 1
    assert report["variant_count"] == 7
    assert report["generator_sha256"] == station_systems.sha256(MODULE_PATH)
    assert report["manifest_sha256"] == station_systems.sha256(station_systems.MANIFEST)
    assert report["screening_execution_passed"] is True
    assert report["deployment_release_ready"] is False


def test_solver_backed_station_domains_pass_all_catalogue_variants() -> None:
    report = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    assert report["structural"]["passed"] is True
    assert set(report["structural"]["cases"]) == {"gravity", "wind_uplift"}
    assert report["passenger"]["passed"] is True
    assert len(report["passenger"]["variants"]) == 7
    assert all(
        set(variant["scenarios"]) == {"normal", "degraded", "egress"}
        and variant["passed"]
        for variant in report["passenger"]["variants"].values()
    )
    assert report["drainage"]["passed"] is True
    assert len(report["drainage"]["variants"]) == 7
    assert all(
        variant["passed"] and variant["drainage_outlet_count"] > 0
        for variant in report["drainage"]["variants"].values()
    )


def test_energy_and_fire_baselines_fail_while_proposed_layout_screens_pass() -> None:
    report = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    for name in ("energyplus", "fds"):
        result = report["optional_solver_inputs"][name]
        for case in result["cases"].values():
            path = REPO_ROOT / case["input_path"]
            assert path.is_file()
            assert case["input_sha256"] == station_systems.sha256(path)
        if not result["solver_available"]:
            assert result["status"] == "input-prepared"
            assert result["passed"] is False

    energy = report["optional_solver_inputs"]["energyplus"]
    fire = report["optional_solver_inputs"]["fds"]
    assert energy["solver_completed"] is True
    assert energy["screening_passed"] is True
    energy_baseline = energy["cases"]["baseline_ventilation_only"]
    energy_proposed = energy["cases"]["proposed_separated_cooled_controls"]
    assert energy_baseline["passed"] is False
    assert energy_baseline["max_zone_air_temperature_c"] > energy["screening_limit_max_zone_air_temperature_c"]
    assert energy_proposed["passed"] is True
    assert energy_proposed["max_zone_air_temperature_c"] <= energy["screening_limit_max_zone_air_temperature_c"] + 1e-9
    assert 0 < energy_proposed["max_ideal_cooling_load_kw"] <= 30.0
    assert fire["solver_completed"] is True
    assert fire["screening_passed"] is True
    fire_baseline = fire["cases"]["baseline_enclosed_room"]
    fire_proposed = fire["cases"]["proposed_separated_open_compound"]
    assert fire_baseline["passed"] is False
    assert fire_baseline["max_room_device_temperature_c"] > fire["screening_limits"]["room_temperature_max_c"]
    assert fire_baseline["min_door_visibility_m"] < fire["screening_limits"]["door_visibility_min_m"]
    assert fire_proposed["passed"] is True
    assert fire_proposed["max_room_device_temperature_c"] <= fire["screening_limits"]["room_temperature_max_c"]
    assert fire_proposed["min_door_visibility_m"] >= fire["screening_limits"]["door_visibility_min_m"]
    for case in (energy_baseline, energy_proposed):
        trace = REPO_ROOT / case["result_trace_path"]
        assert trace.is_file()
        assert case["result_trace_sha256"] == station_systems.sha256(trace)
    for case in (fire_baseline, fire_proposed):
        for path_text in case["result_trace_paths"]:
            path = REPO_ROOT / path_text
            assert path.is_file()
            assert case["result_trace_sha256"][path.name] == station_systems.sha256(path)


def test_station_drainage_input_uses_one_repeatable_branch() -> None:
    deck = station_systems.swmm_input("test", 65.0)

    assert "Roof Gage1 Inlet 0.006500" in deck
    assert "Drain Inlet Outfall 40 0.013" in deck
    assert "Drain CIRCULAR 0.300" in deck
    assert "Storm 01/01/2020 00:05 75" in deck


def test_depot_mitigation_work_packages_are_actionable_and_reference_real_products() -> None:
    source = MODULE_PATH.with_name("mitigation-work-packages.toml")
    register = tomllib.loads(source.read_text(encoding="utf-8"))
    manifest = json.loads(station_systems.MANIFEST.read_text(encoding="utf-8"))
    depot = next(row for row in manifest["variants"] if row["archetype"] == "depot-terminal")
    valid_ids = {row["id"] for row in depot["product_items"]} | {
        row["id"] for row in depot["assemblies"]
    }
    packages = register["work_package"]

    assert register["schema_version"] == 1
    assert len(packages) == 6
    assert len({row["id"] for row in packages}) == len(packages)
    assert all(row["owner_role"] and row["evidence_required"] for row in packages)
    assert all(row["closure_state"] == "open-deployment" for row in packages)
    assert all(set(row["related_product_ids"]) <= valid_ids for row in packages)
    markdown = source.with_suffix(".md")
    assert markdown.is_file()
    assert markdown.read_text(encoding="utf-8") == station_systems.render_work_packages(register)
