"""Ballastless slab-trackform geometry regressions."""

from __future__ import annotations

from osr_mech.civil.slab import (
    AT_GRADE_PANEL_WIDTH_MM,
    BASEPLATE_PAD_HEIGHT_MM,
    ELEVATED_BASE_THICKNESS_MM,
    ELEVATED_PANEL_WIDTH_MM,
    ELEVATED_PLINTH_HEIGHT_MM,
    FASTENER_PITCH_MM,
    PANEL_LENGTH_MM,
    at_grade_concrete_volume_m3,
    at_grade_rail_y_positions,
    at_grade_slab_panel,
    direct_fixation_seat_count,
    elevated_concrete_volume_m3,
    elevated_deck_slab_panel,
    elevated_rail_y_positions,
    elevated_service_trough_y_positions,
)
from osr_mech.civil.ugirder import INTERNAL_WIDTH_MM
from osr_mech.track.panel import track_panel


def test_at_grade_panel_carries_double_track_direct_fixation() -> None:
    rails = at_grade_rail_y_positions()
    assert len(rails) == 4
    assert min(rails) > -AT_GRADE_PANEL_WIDTH_MM / 2.0
    assert max(rails) < AT_GRADE_PANEL_WIDTH_MM / 2.0
    assert direct_fixation_seat_count(PANEL_LENGTH_MM, len(rails)) == 40


def test_elevated_panel_fits_inside_u_girder_trough() -> None:
    rails = elevated_rail_y_positions()
    assert len(rails) == 2
    assert ELEVATED_PANEL_WIDTH_MM <= INTERNAL_WIDTH_MM
    assert max(abs(y) for y in rails) < ELEVATED_PANEL_WIDTH_MM / 2.0
    assert direct_fixation_seat_count(PANEL_LENGTH_MM, len(rails)) == 20
    assert elevated_service_trough_y_positions() == (1920.0,)


def test_slab_concrete_volumes_are_planning_envelopes() -> None:
    at_grade = at_grade_concrete_volume_m3()
    elevated = elevated_concrete_volume_m3()
    assert 12.0 <= at_grade <= 13.0
    assert 1.6 <= elevated <= 1.9


def test_cad_parts_build_with_expected_children() -> None:
    at_grade = at_grade_slab_panel()
    elevated = elevated_deck_slab_panel()
    assert "At-grade" in at_grade.label
    assert "Elevated" in elevated.label
    assert len(at_grade.children) == 1 + 4 + 2 + 40
    assert len(elevated.children) == 1 + 2 + 1 + 20
    service_parts = [
        child for child in elevated.children if child.label == "Elevated cable and drainage trough"
    ]
    assert len(service_parts) == 1
    assert service_parts[0].bounding_box().min.Y > 0.0
    assert ELEVATED_BASE_THICKNESS_MM + ELEVATED_PLINTH_HEIGHT_MM + BASEPLATE_PAD_HEIGHT_MM > 0
    assert FASTENER_PITCH_MM == 650.0


def test_track_panel_is_centred_on_shared_transverse_axis() -> None:
    box = track_panel().bounding_box()
    assert box.min.Y == -box.max.Y
    assert box.max.X > box.max.Y
