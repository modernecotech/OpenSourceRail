"""Construction-system selection and semi-continuity regressions."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from osr_mech.civil.approach import reinforced_soil_approach_plan
from osr_mech.civil.at_grade import at_grade_method_quantities, select_at_grade_method
from osr_mech.civil.continuity import semi_continuous_unit_plan


def test_four_span_units_reduce_interfaces_deterministically() -> None:
    plan = semi_continuous_unit_plan(1_000.0)
    assert plan.spans == 40
    assert plan.units == 10
    assert plan.link_slabs == 30
    assert plan.deck_gaps == 10
    assert plan.bearings == 200
    assert plan.internal_support_bearings == 4
    assert plan.expansion_support_bearings == 8
    assert plan.maximum_unit_length_m == 100.0
    assert len(plan.release_gates) >= 6


def test_at_grade_method_defaults_to_slipform_but_retains_constrained_panels() -> None:
    assert select_at_grade_method(1_000.0).method == "continuous-slipform"
    assert (
        select_at_grade_method(80.0, utility_crossings=True).method
        == "single-track-precast-st6"
    )
    quantities = at_grade_method_quantities(1_000.0, constrained_route_m=120.0)
    assert quantities.slipformed_route_m == 880.0
    assert quantities.single_track_precast_panels == 40


def test_reinforced_soil_approach_enforces_exclusions() -> None:
    accepted = reinforced_soil_approach_plan(4.0, 125.0)
    assert accepted.eligible is True
    assert accepted.potentially_avoided_spans == 5
    rejected = reinforced_soil_approach_plan(4.0, 125.0, flood_or_scour=True)
    assert rejected.eligible is False
    assert "flood or scour" in rejected.reason
    with pytest.raises(ValueError):
        reinforced_soil_approach_plan(0.0, 100.0)


def test_machine_readable_construction_system_keeps_cost_baseline_unvalidated() -> None:
    root = Path(__file__).resolve().parents[2]
    with (root / "lib/templates/civil-construction-systems.toml").open("rb") as handle:
        config = tomllib.load(handle)
    assert config["viaduct"]["expansion_unit_spans"] == 4
    assert config["at_grade"]["long_open_run_method"] == "continuous_slipform"
    assert config["route_optimization"]["compare_road_grade_separation"] is True
    assert config["preliminary_combined_civil_saving_target_percent"] == [15, 30]
    assert "unchanged" in config["cost_baseline_rule"]
