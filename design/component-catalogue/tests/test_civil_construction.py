"""Resource-driven civil production schedule regressions."""

from __future__ import annotations

import pytest

from osr_mech.civil.construction import CivilProductionInputs, civil_production_plan


def test_one_kilometre_plan_is_calculated_from_quantities_and_resources() -> None:
    plan = civil_production_plan(
        CivilProductionInputs(route_m=1_000.0, elevated_m=500.0, at_grade_m=500.0)
    )
    assert plan.elevated_bays == 20
    assert plan.foundations == 21
    assert plan.primary_beams == 40
    assert plan.single_track_panels == 0
    assert plan.slipformed_route_m == 500.0
    assert plan.slipform_days == 3
    assert plan.beam_production_days == 40
    assert plan.foundation_days == 21
    assert plan.erection_days == 20
    assert plan.panel_placement_days == 0
    assert plan.foundations_ahead_bays == 12
    assert plan.programme_working_days == plan.elevated_critical_path_days


def test_more_resources_reduce_or_hold_the_critical_path() -> None:
    base = civil_production_plan(
        CivilProductionInputs(route_m=2_000.0, elevated_m=2_000.0, at_grade_m=0.0)
    )
    scaled = civil_production_plan(
        CivilProductionInputs(
            route_m=2_000.0,
            elevated_m=2_000.0,
            at_grade_m=0.0,
            beam_mould_count=4,
            piling_rig_count=2,
            gantry_count=2,
        )
    )
    assert scaled.programme_working_days < base.programme_working_days


def test_planner_rejects_invalid_catalogue_or_buffer_assumptions() -> None:
    with pytest.raises(ValueError, match="20 m or 25 m"):
        civil_production_plan(
            CivilProductionInputs(route_m=1_000.0, elevated_m=1_000.0, at_grade_m=0.0, primary_span_m=30.0)
        )
    with pytest.raises(ValueError, match="10-15 bays"):
        civil_production_plan(
            CivilProductionInputs(route_m=1_000.0, elevated_m=1_000.0, at_grade_m=0.0, foundations_ahead_bays=5)
        )


def test_constrained_at_grade_zone_uses_replaceable_st6_panels() -> None:
    plan = civil_production_plan(
        CivilProductionInputs(
            route_m=500.0,
            elevated_m=0.0,
            at_grade_m=500.0,
            constrained_at_grade_m=120.0,
        )
    )
    assert plan.slipformed_route_m == 380.0
    assert plan.single_track_panels == 40
    assert plan.panel_placement_days == 1
    assert plan.at_grade_critical_path_days == 3
