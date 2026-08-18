from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from osr_mech.civil.viaduct import (
    ViaductEnvelopeCheck,
    assert_viaduct_envelope,
    required_end_support_bearing_count,
    required_interior_bearing_count,
    straight_span_chord_offset_m,
    viaduct_envelope_issues,
)
from osr_mech.civil.slab import PANEL_LENGTH_MM, elevated_concrete_volume_m3
from osr_mech.civil.ugirder import section_area_m2


def test_standard_u25_broad_curve_passes_planning_gates() -> None:
    assert_viaduct_envelope(ViaductEnvelopeCheck())
    assert required_interior_bearing_count(2) == 8
    assert required_end_support_bearing_count(2) == 4


def test_90_m_curve_rejects_25_m_straight_full_span() -> None:
    check = ViaductEnvelopeCheck(curve_radius_m=90.0)
    issues = viaduct_envelope_issues(check)
    assert any("chord offset" in issue for issue in issues)
    assert straight_span_chord_offset_m(25.0, 90.0) == pytest.approx(0.8723, rel=1e-3)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"internal_width_mm": 3_500.0}, "internal width"),
        ({"interior_bearing_count": 4}, "bearing count"),
        ({"parapet_height_above_walkway_mm": 1_200.0}, "parapet height"),
        ({"transport_mass_kg": 150_000.0}, "transport mass"),
        ({"transport_width_mm": 5_300.0}, "transport width"),
    ],
)
def test_automated_gates_reject_invalid_envelopes(
    overrides: dict[str, float | int], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        assert_viaduct_envelope(ViaductEnvelopeCheck(**overrides))


def test_u30_requires_larger_approved_transport_and_erection_envelope() -> None:
    issues = viaduct_envelope_issues(ViaductEnvelopeCheck(span_m=30.0, curve_radius_m=400.0))
    assert any("transport mass" in issue for issue in issues)


def test_curve_chord_cannot_spend_protected_sway_tolerance_reserve() -> None:
    issues = viaduct_envelope_issues(
        ViaductEnvelopeCheck(internal_width_mm=4_500.0, curve_radius_m=300.0)
    )
    assert any("chord offset" in issue for issue in issues)
    assert_viaduct_envelope(ViaductEnvelopeCheck(curve_radius_m=300.0))


def test_machine_readable_viaduct_packages_parse_and_control_axle_train() -> None:
    root = Path(__file__).resolve().parents[2]
    with (root / "docs/civil/viaduct-load-model.toml").open("rb") as handle:
        loads = tomllib.load(handle)
    with (root / "docs/civil/viaduct-quantity-cost-model.toml").open("rb") as handle:
        costs = tomllib.load(handle)
    assert loads["reference_train"]["axles"] == 12
    assert len(loads["reference_train"]["axle_positions_m"]) == 12
    assert loads["design_axle_allowance_t"] == 16.0
    assert costs["geometry"]["single_track_girders_per_route_km"] == 80
    bare_m3_per_km = section_area_m2() * 2.0 * 1_000.0
    trackform_m3_per_km = (
        elevated_concrete_volume_m3() / (PANEL_LENGTH_MM / 1_000.0) * 2.0 * 1_000.0
    )
    assert costs["quantities"]["bare_precast_girder_concrete_m3_per_km"] == pytest.approx(
        bare_m3_per_km
    )
    assert costs["quantities"][
        "thin_alignment_layer_and_plinth_concrete_m3_per_km"
    ] == pytest.approx(trackform_m3_per_km)
    assert costs["estimate"]["project_estimate_required"] is True
