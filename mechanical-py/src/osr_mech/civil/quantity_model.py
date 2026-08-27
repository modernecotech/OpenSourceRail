"""Canonical per-route-kilometre civil quantities derived from CAD geometry."""

from __future__ import annotations

from .at_grade import at_grade_method_quantities
from .continuity import semi_continuous_unit_plan
from .decked_pi import section_area_m2
from .slab import (
    PANEL_LENGTH_MM,
    at_grade_concrete_volume_m3,
    elevated_concrete_volume_m3,
)
from .substructure import (
    PIER_CAP_HEIGHT_MM,
    PIER_CAP_X_MM,
    PIER_CAP_Y_MM,
    PIER_COLUMN_X_MM,
    PIER_COLUMN_Y_MM,
)

ROUTE_M_PER_KM = 1_000.0
TRACKS = 2
PRIMARY_SPAN_M = 25.0
REFERENCE_PIER_HEIGHT_M = 8.0
FASTENER_PITCH_M = 0.650
WALKWAY_WIDTH_M = 1.0
WALKWAY_THICKNESS_M = 0.12


def structure_quantities_per_km() -> dict[str, dict[str, float | int | bool | str]]:
    """Return deterministic planning quantities; foundations stay zone-specific."""

    bays = int(ROUTE_M_PER_KM / PRIMARY_SPAN_M)
    beams = bays * TRACKS
    at_grade_panel_m = PANEL_LENGTH_MM / 1_000.0
    at_grade_methods = at_grade_method_quantities(ROUTE_M_PER_KM)
    continuity = semi_continuous_unit_plan(ROUTE_M_PER_KM)
    at_grade_concrete = (
        at_grade_concrete_volume_m3() / at_grade_panel_m * TRACKS * ROUTE_M_PER_KM
    )
    bare_beam_concrete = section_area_m2() * TRACKS * ROUTE_M_PER_KM
    elevated_trackform = (
        elevated_concrete_volume_m3() / at_grade_panel_m * TRACKS * ROUTE_M_PER_KM
    )
    walkway = WALKWAY_WIDTH_M * WALKWAY_THICKNESS_M * TRACKS * ROUTE_M_PER_KM
    cap_outer = (
        PIER_CAP_X_MM * PIER_CAP_Y_MM * PIER_CAP_HEIGHT_MM / 1_000_000_000.0
    )
    cap_void = 2.0 * 6.5 * 0.8
    cap_concrete = cap_outer - cap_void
    columns = (
        PIER_COLUMN_X_MM
        * PIER_COLUMN_Y_MM
        / 1_000_000.0
        * REFERENCE_PIER_HEIGHT_M
        * bays
    )
    seats = int(ROUTE_M_PER_KM / FASTENER_PITCH_M) + 1
    common = {
        "rail_kg_per_km": 240_000,
        "direct_fixation_seats_per_km": seats * 4,
    }
    return {
        "at-grade": {
            **common,
            "default_construction_method": "continuous-slipform",
            "slipformed_route_m_per_km": round(at_grade_methods.slipformed_route_m),
            "single_track_panels_per_km": at_grade_methods.single_track_precast_panels,
            "precast_panels_quantity_model": "constrained-zone-required",
            "slab_concrete_m3_per_km": round(at_grade_concrete, 1),
            "slab_rebar_kg_per_km": round(at_grade_concrete * 150.0),
        },
        "elevated": {
            **common,
            "structural_bays_per_km": bays,
            "single_track_girders_per_km": beams,
            "pier_count_per_km": bays,
            "expansion_unit_spans": continuity.unit_spans,
            "expansion_units_per_km": continuity.units,
            "link_slabs_per_km": continuity.link_slabs,
            "deck_gaps_per_km": continuity.deck_gaps,
            "bearings_per_km": continuity.bearings,
            "internal_support_bearings": continuity.internal_support_bearings,
            "expansion_support_bearings": continuity.expansion_support_bearings,
            "bare_beam_concrete_m3_per_km": round(bare_beam_concrete, 1),
            "trackform_concrete_m3_per_km": round(elevated_trackform, 1),
            "walkway_concrete_m3_per_km": round(walkway, 1),
            "pier_and_cap_concrete_m3_per_km": round(columns + cap_concrete * bays, 1),
            "foundation_quantity_model": "geotechnical-zone-required",
        },
    }


__all__ = ["structure_quantities_per_km"]
