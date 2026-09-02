"""Regression checks for the tracked station-system screening package."""

from __future__ import annotations

import importlib.util
import json
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


def test_pending_energy_and_fire_decks_are_tracked_and_honest() -> None:
    report = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    for name in ("energyplus", "fds"):
        result = report["optional_solver_inputs"][name]
        path = REPO_ROOT / result["input_path"]
        assert path.is_file()
        assert result["input_sha256"] == station_systems.sha256(path)
        if not result["solver_available"]:
            assert result["status"] == "input-prepared"
            assert result["passed"] is False


def test_station_drainage_input_uses_one_repeatable_branch() -> None:
    deck = station_systems.swmm_input("test", 65.0)

    assert "Roof Gage1 Inlet 0.006500" in deck
    assert "Drain Inlet Outfall 40 0.013" in deck
    assert "Drain CIRCULAR 0.300" in deck
    assert "Storm 01/01/2020 00:05 75" in deck

