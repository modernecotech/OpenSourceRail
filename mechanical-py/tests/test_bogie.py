"""Tests for the detailed bogie component + assembly CAD (RFC 0022)."""

from __future__ import annotations

import pytest

from osr_mech.rolling_stock.bogie import (
    BOGIE_FRAME_HEIGHT_MM,
    BOGIE_FRAME_LENGTH_MM,
    BOGIE_FRAME_WIDTH_MM,
    BogieVariant,
    PIVOT_HEIGHT_MM,
    WHEEL_DIAMETER_MM,
    WHEEL_DIAMETER_WORN_MM,
    WHEELBASE_MM,
    bogie,
    bogie_assembly,
    bogie_frame,
    brake_unit,
    gearbox,
    motor_bogie,
    primary_suspension,
    secondary_suspension,
    traction_motor,
    trailer_bogie,
    wheelset,
)


# ---------------------------------------------------------------------------
# Individual components
# ---------------------------------------------------------------------------


def test_wheelset_has_two_wheels_one_disc() -> None:
    w = wheelset()
    labels = [c.label for c in w.children]
    treads = sum("Wheel tread" == (l or "") for l in labels)
    flanges = sum("Wheel flange" == (l or "") for l in labels)
    discs = sum("Brake disc" == (l or "") for l in labels)
    assert treads == 2, f"expected 2 wheel treads, labels: {labels}"
    assert flanges == 2, f"expected 2 wheel flanges, labels: {labels}"
    assert discs == 1, f"expected 1 brake disc, labels: {labels}"


def test_wheelset_on_standard_gauge() -> None:
    w = wheelset()
    bb = w.bounding_box()
    span = bb.max.Y - bb.min.Y
    # Span = gauge 1435 + 2×(tread + bearing-housing + margin) ~ 2150.
    assert 2_000.0 < span < 2_400.0, f"wheelset Y span {span} mm outside expected"
    # And it must be symmetric about Y=0 (axle centred on origin).
    assert abs(bb.min.Y + bb.max.Y) < 5.0, f"wheelset not centred on Y: [{bb.min.Y}, {bb.max.Y}]"


def test_worn_wheel_radius_smaller() -> None:
    # Worn wheels < new wheels.
    w_new = wheelset(wheel_diameter_mm=WHEEL_DIAMETER_MM)
    w_worn = wheelset(wheel_diameter_mm=WHEEL_DIAMETER_WORN_MM)
    bb_new = w_new.bounding_box()
    bb_worn = w_worn.bounding_box()
    assert (bb_worn.max.Z - bb_worn.min.Z) < (bb_new.max.Z - bb_new.min.Z)


def test_motor_has_shaft_and_terminal_box() -> None:
    m = traction_motor()
    labels = {c.label for c in m.children}
    assert any(l and "shaft" in l.lower() for l in labels)
    assert any(l and "terminal" in l.lower() for l in labels)
    assert any(l and "end-bell" in l.lower() for l in labels)


def test_gearbox_has_nonzero_volume() -> None:
    g = gearbox()
    # Gearbox is a Compound of Parts (housing + boss + filter) — children
    # are Parts, so .volume should sum correctly.
    assert g.volume > 0


def test_primary_suspension_sandwich() -> None:
    p = primary_suspension()
    labels = {c.label for c in p.children}
    assert any(l and "rubber" in l.lower() for l in labels)
    assert sum("plate" in (l or "").lower() for l in labels) >= 2


def test_secondary_suspension_has_bellows_and_damper() -> None:
    s = secondary_suspension()
    labels = {c.label for c in s.children}
    assert any(l and "bellows" in l.lower() for l in labels)
    assert any(l and "damper" in l.lower() for l in labels)


def test_brake_unit_has_caliper_and_actuator() -> None:
    b = brake_unit()
    labels = {c.label for c in b.children}
    assert any(l and "caliper" in l.lower() for l in labels)
    assert any(l and "actuator" in l.lower() for l in labels)


def test_frame_has_pivot_boss_and_bolster() -> None:
    f = bogie_frame()
    labels = {c.label for c in f.children}
    assert any(l and "pivot" in l.lower() for l in labels)
    assert any(l and "bolster" in l.lower() for l in labels)
    # Two side beams + two end cross-members + one bolster + one boss.
    assert len(f.children) >= 5


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def test_motor_bogie_has_more_children_than_trailer() -> None:
    m = motor_bogie()
    t = trailer_bogie()
    assert len(list(m.children)) > len(list(t.children))


def test_motor_bogie_contains_motor_and_gearbox() -> None:
    m = motor_bogie()
    labels = [c.label for c in m.children]
    assert any(l and "motor" in l.lower() for l in labels), labels
    assert any(l and "gearbox" in l.lower() for l in labels), labels


def test_bogie_primary_suspension_has_eight_packs() -> None:
    m = motor_bogie()
    labels = [c.label for c in m.children]
    primary = [l for l in labels if l and l.startswith("Primary suspension")]
    assert len(primary) == 8


def test_trailer_bogie_has_no_motor_or_gearbox() -> None:
    t = trailer_bogie()
    labels = [c.label for c in t.children]
    assert not any(l and "motor" in (l or "").lower() for l in labels), labels
    assert not any(l and "gearbox" in (l or "").lower() for l in labels), labels


def test_trailer_bogie_still_has_brake() -> None:
    t = trailer_bogie()
    labels = [c.label for c in t.children]
    assert any(l and "brake" in (l or "").lower() for l in labels)


def test_bogie_assembly_alias_returns_motor_variant() -> None:
    a = bogie_assembly()
    m = motor_bogie()
    assert len(list(a.children)) == len(list(m.children))


def test_bogie_variant_enum_wires_up() -> None:
    assert bogie(BogieVariant.MOTOR).label != bogie(BogieVariant.TRAILER).label


# ---------------------------------------------------------------------------
# Reference dimensions preserved (backwards compat)
# ---------------------------------------------------------------------------


def test_constants_within_rfc_bounds() -> None:
    assert WHEELBASE_MM == 2_100.0
    assert WHEEL_DIAMETER_MM == 760.0
    assert BOGIE_FRAME_LENGTH_MM == 3_500.0
    assert BOGIE_FRAME_WIDTH_MM == 2_400.0
    assert PIVOT_HEIGHT_MM == 580.0


# ---------------------------------------------------------------------------
# Trainset consumption
# ---------------------------------------------------------------------------


def test_trainset_consumes_both_variants_per_family() -> None:
    from osr_mech.rolling_stock.trainset import family_motorisation
    from osr_mech.common import ConsistFamily

    tram = family_motorisation(ConsistFamily.TRAM_2CAR)
    lm3 = family_motorisation(ConsistFamily.LIGHT_METRO_3CAR)
    m4 = family_motorisation(ConsistFamily.METRO_4CAR)
    m6 = family_motorisation(ConsistFamily.METRO_6CAR)

    assert all(tram), "tram should be all motor cars"
    # Each self-contained car now carries one powered bogie and one
    # trailer bogie, so every car is represented as motorised.
    assert all(lm3)
    assert all(m4)
    assert all(m6)
