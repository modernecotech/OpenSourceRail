"""Generated operations data exposes auditable rate-derived civil schedules."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "generate_qa_maintenance_data", ROOT / "scripts/generate-qa-maintenance-data.py"
)
assert SPEC and SPEC.loader
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


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
