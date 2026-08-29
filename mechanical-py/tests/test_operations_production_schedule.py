"""Generated operations data exposes auditable rate-derived civil schedules."""

from __future__ import annotations

import importlib.util
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "generate_qa_maintenance_data", ROOT / "scripts/generate-qa-maintenance-data.py"
)
assert SPEC and SPEC.loader
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


def _load_toml(relative: str) -> dict:
    with (ROOT / relative).open("rb") as handle:
        return tomllib.load(handle)


def test_track_section_duration_is_calculated_from_length_and_resources() -> None:
    asset = {"km_start": "1.000", "km_end": "2.260"}
    days, basis = GENERATOR._manufacturing_duration(
        {
            "id": "trk-rate-test",
            "duration_model": "route-metres",
            "route_metres_per_resource_day": 200.0,
            "resource_count": 2,
        },
        asset,
    )
    assert days == 4
    assert "1260.0 route m" in basis
    panel_days, panel_basis = GENERATOR._manufacturing_duration(
        {
            "id": "trk-panel-test",
            "duration_model": "single-track-panels",
            "panel_length_m": 6.0,
            "track_count": 2,
            "panels_per_resource_day": 40.0,
            "resource_count": 1,
        },
        asset,
    )
    assert panel_days == 11
    assert "420 ST6 panels" in panel_basis


def test_line_schedule_uses_civil_segment_mix() -> None:
    plans = GENERATOR._civil_production_by_line(
        design={
            "lines": [{"name": "red", "length_m": 1_000.0}],
            "civil_segments": [
                {"line": "red", "from_station_m": 0.0, "to_station_m": 500.0, "class": "at-grade"},
                {"line": "red", "from_station_m": 500.0, "to_station_m": 1_000.0, "class": "elevated"},
            ],
        },
        controls={"foundations_ahead_bays": 12},
    )
    assert len(plans) == 1
    assert plans[0]["line"] == "red"
    assert plans[0]["elevated_bays"] == 20
    assert plans[0]["primary_beams"] == 40
    assert plans[0]["single_track_panels"] == 0
    assert plans[0]["slipformed_route_m"] == 500.0


def test_line_schedule_persists_explicit_constrained_trackform_method() -> None:
    plans = GENERATOR._civil_production_by_line(
        design={
            "lines": [{"name": "red", "length_m": 300.0}],
            "civil_segments": [
                {
                    "line": "red",
                    "from_station_m": 0.0,
                    "to_station_m": 120.0,
                    "class": "at-grade",
                    "construction_method": "single-track-precast",
                },
                {
                    "line": "red",
                    "from_station_m": 120.0,
                    "to_station_m": 300.0,
                    "class": "at-grade",
                },
            ],
        },
        controls={"foundations_ahead_bays": 12},
    )
    assert plans[0]["single_track_panels"] == 40
    assert plans[0]["slipformed_route_m"] == 180.0


def test_scheduler_respects_predecessors_and_one_rate_resource() -> None:
    rows = [
        {
            "manufacturing_uid": "a:p",
            "asset_id": "a",
            "package_id": "p",
            "duration_days": 4,
            "duration_model": "route-metres",
            "resource_count": 1,
            "planned_start_day": 10,
            "planned_finish_day": 13,
            "predecessor_uids": "",
        },
        {
            "manufacturing_uid": "b:p",
            "asset_id": "b",
            "package_id": "p",
            "duration_days": 3,
            "duration_model": "route-metres",
            "resource_count": 1,
            "planned_start_day": 11,
            "planned_finish_day": 13,
            "predecessor_uids": "",
        },
        {
            "manufacturing_uid": "b:q",
            "asset_id": "b",
            "package_id": "q",
            "duration_days": 2,
            "duration_model": "fixed-days",
            "resource_count": "",
            "planned_start_day": 12,
            "planned_finish_day": 13,
            "predecessor_uids": "b:p",
        },
    ]
    GENERATOR._schedule_manufacturing_tasks(rows)
    assert rows[1]["planned_start_day"] == 14
    assert rows[1]["planned_finish_day"] == 16
    assert rows[2]["planned_start_day"] == 17
    assert rows[2]["planned_start_basis"] == "project_day_17"


def test_configured_habd_sites_enter_operations_qa_and_maintenance() -> None:
    design_path = ROOT / "designs/west-asia/Iraq/Samawah/design.toml"
    scenario_path = ROOT / "designs/west-asia/Iraq/Samawah/samawah.toml"
    bundle = GENERATOR.build_bundle(
        design=_load_toml("designs/west-asia/Iraq/Samawah/design.toml"),
        scenario=_load_toml("designs/west-asia/Iraq/Samawah/samawah.toml"),
        qa_template=_load_toml("lib/templates/construction-qa.toml"),
        maint_template=_load_toml("lib/templates/maintenance-schedule.toml"),
        manufacturing_template=_load_toml(
            "lib/templates/manufacturing-schedule.toml"
        ),
        bom_catalog={},
        design_path=design_path,
        scenario_path=scenario_path,
    )

    detector_assets = [
        asset
        for asset in bundle["assets"]
        if asset["asset_type"] == "hot-axle-detector"
    ]
    assert bundle["totals"]["hot_axle_detectors"] == 3
    assert len(detector_assets) == 3
    assert all(asset["parent_asset"].startswith("SAM-TRK-") for asset in detector_assets)
    assert all(asset["km_start"] == asset["km_end"] for asset in detector_assets)

    detector_ids = {asset["asset_id"] for asset in detector_assets}
    detector_maintenance = [
        task
        for task in bundle["maintenance_tasks"]
        if task["asset_id"] in detector_ids
    ]
    detector_qa = [
        action for action in bundle["qa_actions"] if action["asset_id"] in detector_ids
    ]
    assert {task["task_id"] for task in detector_maintenance} == {
        "systems-daily",
        "systems-monthly",
        "systems-quarterly",
    }
    assert {action["gate_id"] for action in detector_qa} == {
        "qa-26-wayside-comms-safety"
    }
