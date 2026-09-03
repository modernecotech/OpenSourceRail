"""Tests for the independent operations-model cross-check gate."""

from __future__ import annotations

import json
from pathlib import Path

from engineering.analysis import operations_crosscheck


def inputs(tmp_path: Path, osr_time: float = 1000.0, sumo_time: float = 1050.0) -> tuple[Path, Path, Path]:
    design = tmp_path / "design.toml"
    design.write_text('[city]\nslug="test-city"\n[[lines]]\nid="line-1"\nname="line-1"\n')
    sumo = tmp_path / "sumo.json"
    sumo.write_text(json.dumps({"passed": True, "lines": [{"line": "line-1", "mean_trip_duration_s": sumo_time}]}))
    simulation = tmp_path / "simulation.json"
    simulation.write_text(json.dumps({"passed": True, "runs": [{"per_line_reference_trip_time_s": [["line-1", osr_time]]}]}))
    return design, sumo, simulation


def test_automatic_comparison_passes_but_external_gates_remain(tmp_path: Path) -> None:
    design, sumo, simulation = inputs(tmp_path)
    report = operations_crosscheck.build_report(design, sumo, simulation)
    assert report["automatic_crosscheck_passed"] is True
    assert report["junction_occupancy_passed"] is False
    assert report["authority_accepted"] is False
    assert report["status"] == "running-time-screen-passed-awaiting-junction-evidence"


def test_timing_divergence_fails_closed(tmp_path: Path) -> None:
    design, sumo, simulation = inputs(tmp_path, osr_time=1000.0, sumo_time=1400.0)
    report = operations_crosscheck.build_report(design, sumo, simulation)
    assert report["automatic_crosscheck_passed"] is False
    assert report["line_comparisons"][0]["passed"] is False
    assert report["status"] == "automatic-crosscheck-failed"


def test_missing_osr_reference_is_not_silently_accepted(tmp_path: Path) -> None:
    design, sumo, simulation = inputs(tmp_path)
    simulation.write_text(json.dumps({"passed": True, "runs": [{}]}))
    report = operations_crosscheck.build_report(design, sumo, simulation)
    assert report["line_scope_matches"] is False
    assert report["automatic_crosscheck_passed"] is False
