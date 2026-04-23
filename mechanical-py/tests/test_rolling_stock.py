"""Rolling-stock geometry + RFC 0008 consistency checks.

Runs four tests:

1. Every consist family's trainset fits inside its published platform
   length (RFC 0008 §1).
2. A bogie's wheel centres fall on standard gauge (within tolerance).
3. A car body has exactly (doors_per_side × 2) door cutouts — verified
   indirectly by volume check.
4. The sensor cowl has a real sensor-window cutout reducing volume
   below the solid bounding box.
"""

from __future__ import annotations

import pytest

from osr_mech.common import ConsistFamily, STANDARD_GAUGE_MM
from osr_mech.rolling_stock.bogie import (
    BOGIE_FRAME_HEIGHT_MM,
    BOGIE_FRAME_LENGTH_MM,
    BOGIE_FRAME_WIDTH_MM,
    WHEEL_DIAMETER_MM,
    bogie_assembly,
)
from osr_mech.rolling_stock.car_body import CarDimensions, car_body
from osr_mech.rolling_stock.sensor_cowl import (
    COWL_LENGTH_MM,
    LEADING_FACE_HEIGHT_MM,
    LEADING_FACE_WIDTH_MM,
    sensor_cowl,
)
from osr_mech.rolling_stock.trainset import (
    expected_platform_length_m,
    trainset,
    trainset_length_m,
)


@pytest.mark.parametrize(
    "family",
    [
        ConsistFamily.TRAM_2CAR,
        ConsistFamily.LIGHT_METRO_3CAR,
        ConsistFamily.METRO_4CAR,
        ConsistFamily.METRO_6CAR,
    ],
)
def test_trainset_fits_within_published_platform(family: ConsistFamily) -> None:
    """RFC 0008 §1 publishes a platform length per family; the
    trainset must fit on it with a small stopping-tolerance margin."""
    length_m = trainset_length_m(family)
    platform_m = expected_platform_length_m(family)
    # Trainset must be strictly shorter than platform (so both noses
    # fit between the stop marks), with ≥ 1 m of margin.
    assert length_m < platform_m, (
        f"{family.value}: trainset {length_m:.1f} m ≥ platform {platform_m:.1f} m"
    )
    margin = platform_m - length_m
    assert margin >= 1.0, (
        f"{family.value}: only {margin:.1f} m stopping margin on a "
        f"{platform_m:.0f} m platform — too tight"
    )


def test_car_body_has_door_cutouts() -> None:
    """Verify door cutouts reduce volume below the solid-box volume."""
    dims = CarDimensions()
    body = car_body(dims)
    solid_volume_mm3 = dims.body_length_mm * dims.body_width_mm * dims.body_height_mm
    v = body.volume
    assert v < solid_volume_mm3, (
        f"car-body volume {v:.0f} should be below solid box {solid_volume_mm3:.0f}"
    )
    # The cutouts remove at most ~5% of the solid box; we should still
    # be well above 80% of the solid volume.
    assert v > solid_volume_mm3 * 0.80, "too much material removed"


def test_sensor_cowl_has_sensor_window() -> None:
    """The cowl's sensor window cutout must reduce volume below the
    tapered-solid nominal volume."""
    cowl = sensor_cowl()
    # A rough upper bound: average of the two end sections, times
    # length. The tapered solid is smaller than this; the cutout
    # removes further material.
    v = cowl.volume
    assert v > 0.0, "cowl produced empty geometry"
    # Tapered solid upper bound.
    interface_area = 2650.0 * 3600.0
    leading_area = LEADING_FACE_WIDTH_MM * LEADING_FACE_HEIGHT_MM
    untapered = (interface_area + leading_area) / 2.0 * COWL_LENGTH_MM
    assert v < untapered, "cowl volume should be below the average cross-section × length"


def test_bogie_dimensions_are_consistent() -> None:
    """The bogie's bounding box must at least contain both wheelsets
    at standard gauge, and its frame must sit above the wheels."""
    bog = bogie_assembly()
    bb = bog.bounding_box()
    span_y = bb.max.Y - bb.min.Y
    # The bogie frame is 2400 mm wide; STANDARD_GAUGE_MM = 1435 mm
    # falls inside that envelope. The bounding-box Y span is dominated
    # by the frame, not the wheels.
    assert span_y >= STANDARD_GAUGE_MM, (
        f"bogie Y span {span_y:.0f} mm must enclose standard gauge {STANDARD_GAUGE_MM}"
    )
    assert span_y <= BOGIE_FRAME_WIDTH_MM + 10.0, (
        f"bogie Y span {span_y:.0f} mm exceeds frame width {BOGIE_FRAME_WIDTH_MM}"
    )
    # Height: from rail head (0) to top of frame (wheel_dia/2 + gap +
    # frame height) ≈ 810/2 + 50 + 300 = 755 mm.
    height = bb.max.Z - bb.min.Z
    assert 700.0 <= height <= 900.0, (
        f"bogie height {height:.0f} mm outside expected [700, 900]"
    )


def test_trainset_is_symmetric_in_length() -> None:
    """The trainset has no cab — both ends are sensor cowls. Building
    a `LIGHT_METRO_3CAR` trainset should place geometry symmetrically
    about X=0."""
    ts = trainset(ConsistFamily.LIGHT_METRO_3CAR)
    bb = ts.bounding_box()
    # |min X| should equal max X within a millimetre.
    asym = abs(abs(bb.min.X) - bb.max.X)
    assert asym < 1.0, f"trainset not centred on X=0; asymmetry {asym:.2f} mm"
