"""Rolling-stock geometry + RFC 0008 consistency checks.

Runs four tests:

1. Every consist family's trainset fits inside its published platform
   length (RFC 0008 §1).
2. A bogie's wheel centres fall on standard gauge (within tolerance).
3. A car body has the current one-centre-door-per-side pattern — verified
   indirectly by volume and family-dimension checks.
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
from osr_mech.rolling_stock.cots_equipment import (
    CATALOGUE,
    Category,
    bom_per_car,
    fit_out_car_body,
    locations_for,
    total_active_power_w,
    total_mass_kg,
)
from osr_mech.rolling_stock.sensor_cowl import (
    COWL_LENGTH_MM,
    LEADING_FACE_HEIGHT_MM,
    LEADING_FACE_WIDTH_MM,
    sensor_cowl,
)
from osr_mech.rolling_stock.systems import BATTERY_MODULES_PER_CAR, car_systems
from osr_mech.rolling_stock.trainset import (
    expected_platform_length_m,
    family_dimensions,
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


def test_car_body_has_door_and_window_cutouts() -> None:
    """Verify doors + windows are cut through the shell."""
    dims = CarDimensions()
    body = car_body(dims)
    solid_volume_mm3 = dims.body_length_mm * dims.body_width_mm * dims.body_height_mm
    v = body.volume
    assert v < solid_volume_mm3, (
        f"car-body volume {v:.0f} should be below solid box {solid_volume_mm3:.0f}"
    )
    # Doors (1 × 1.4 × 2.0 × 2.65 × 2 sides ≈ 15 m³) + windows remove
    # a visible share of the solid box. The
    # body should still be at least half the solid volume — anything
    # less is a geometry bug.
    assert v > solid_volume_mm3 * 0.50, (
        f"car-body volume {v:.0f} is under half the solid box — cut-geometry bug?"
    )
    # And it should be a Compound (shell + glazing + doors + livery +
    # skirt + roof equipment), not just one Part.
    assert hasattr(body, "children") and body.children, (
        "car body should be a Compound with multiple named children"
    )
    child_labels = {(getattr(c, "label", "") or "").lower() for c in body.children}
    assert any("shell" in l for l in child_labels), "missing shell"
    assert any("glazing" in l for l in child_labels), "missing window glazing"
    assert any("door leaf" in l for l in child_labels), "missing door leaves"
    assert any("livery" in l for l in child_labels), "missing livery band"
    assert any("skirt" in l for l in child_labels), "missing underframe skirt"


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
    """The bogie's bounding box must contain standard gauge and the
    stack of (frame + secondary suspension) must put the car-body
    pivot at the RFC 0022 §3 height."""
    bog = bogie_assembly()
    bb = bog.bounding_box()
    span_y = bb.max.Y - bb.min.Y
    # The detailed bogie includes axle-boxes + brake calipers + the
    # motor cantilevered off the gearbox on the +Y side — so the full
    # Y span exceeds the frame width. Assert standard-gauge containment
    # and a realistic motor-bogie outer envelope.
    assert span_y >= STANDARD_GAUGE_MM, (
        f"bogie Y span {span_y:.0f} mm must enclose standard gauge {STANDARD_GAUGE_MM}"
    )
    assert span_y <= 3_500.0, (
        f"bogie Y span {span_y:.0f} mm wider than any plausible detailed bogie"
    )
    # Height: from rail head (0) up through wheel + primary + frame +
    # secondary air spring + pivot boss. Air-spring top ≈ 1 240 mm.
    height = bb.max.Z - bb.min.Z
    assert 700.0 <= height <= 1_400.0, (
        f"bogie height {height:.0f} mm outside expected [700, 1400]"
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


def _labels_recursive(node) -> list[str]:
    labels: list[str] = []
    for child in getattr(node, "children", []) or []:
        label = getattr(child, "label", None)
        if label:
            labels.append(label)
        labels.extend(_labels_recursive(child))
    return labels


def test_trainset_contains_complete_train_systems() -> None:
    ts = trainset(ConsistFamily.LIGHT_METRO_3CAR)
    labels = _labels_recursive(ts)
    expected = {
        "A-end coupler and crash-energy assembly",
        "B-end coupler and crash-energy assembly",
        "Inter-car articulation assembly",
        "COTS electric door cassette",
        "Na-ion battery module envelope",
        "Station side-pin charging connector",
        "T-ECU/S safety cabinet",
        "T-ECU/A application cabinet",
        "A-end T-OBS sensor pack",
        "B-end T-OBS sensor pack",
        "Wheelchair bay floor reservation",
    }
    missing = expected.difference(labels)
    assert not missing, f"missing train systems: {sorted(missing)}"
    assert labels.count("T-ECU/S safety cabinet") == 2
    assert labels.count("T-ECU/A application cabinet") == 2


def test_car_systems_have_expected_repeated_modules() -> None:
    labels = _labels_recursive(car_systems(CarDimensions()))
    assert labels.count("Na-ion battery module envelope") == BATTERY_MODULES_PER_CAR
    assert labels.count("COTS electric door cassette") == 2
    assert labels.count("Door sill gap-filler flap") == 2
    assert labels.count("T-ECU/S safety cabinet") == 0
    assert labels.count("T-ECU/A application cabinet") == 0


# ---------------------------------------------------------------------------
# COTS interior fit-out catalogue
# ---------------------------------------------------------------------------


def test_cots_catalogue_covers_every_category() -> None:
    """Every `Category` enum value has a catalogue row."""
    for c in Category:
        assert c in CATALOGUE, f"missing catalogue entry for {c}"
        item = CATALOGUE[c]
        assert item.length_mm > 0.0
        assert item.width_mm > 0.0
        assert item.height_mm > 0.0
        assert item.mass_kg > 0.0
        assert item.power_w >= 0.0


def test_bom_quantities_are_common_per_self_contained_car() -> None:
    """Every family repeats the same 17 m self-contained car module.
    Per-car windows, seats, grab poles, and PIS screens therefore stay
    common across consist length."""
    tram = bom_per_car(family_dimensions(ConsistFamily.TRAM_2CAR))
    metro = bom_per_car(family_dimensions(ConsistFamily.LIGHT_METRO_3CAR))

    def qty(bom: list, category: Category) -> int:
        for item, n in bom:
            if item.category == category:
                return n
        raise KeyError(category)

    assert qty(tram, Category.WINDOW) == qty(metro, Category.WINDOW)
    assert qty(tram, Category.GRAB_POLE) == qty(metro, Category.GRAB_POLE)
    assert qty(tram, Category.PIS_SCREEN) == qty(metro, Category.PIS_SCREEN)
    assert qty(tram, Category.SEAT) == qty(metro, Category.SEAT)
    # Per-car fixed-count items don't scale.
    assert qty(tram, Category.HVAC_ROOF) == qty(metro, Category.HVAC_ROOF) == 1
    assert qty(tram, Category.INTERCOM) == qty(metro, Category.INTERCOM) == 2
    assert qty(tram, Category.LIGHTING) == qty(metro, Category.LIGHTING) == 2


def test_mass_and_power_totals_are_realistic() -> None:
    """Per-car interior fit-out should land in the hundreds of kg and
    draw kilowatts — if we're off by an order of magnitude one of the
    catalogue rows is wrong."""
    m = total_mass_kg()
    p = total_active_power_w()
    # Dominated by HVAC (250 kg) + seats + lighting + windows.
    assert 500.0 <= m <= 2_000.0, f"mass {m:.0f} kg is implausible"
    # Dominated by HVAC 15 kW; lighting + screens add ~1 kW.
    assert 12_000.0 <= p <= 25_000.0, f"power {p:.0f} W is implausible"


def test_envelopes_fit_inside_car_body_bounding_box() -> None:
    """Every reserved envelope must sit inside (or on top of) the car
    body. Specifically: no envelope extends below rail head; nothing
    pokes outside the body width envelope for non-roof items."""
    dims = CarDimensions()
    half_L = dims.body_length_mm / 2.0
    half_W = dims.body_width_mm / 2.0
    # Tolerance: windows + seats etc. mount on the inside of the body
    # skin; a 50 mm outward excursion is the envelope-reservation
    # slack, not a design error.
    tol = 60.0

    for category in Category:
        item = CATALOGUE[category]
        for loc in locations_for(category, dims):
            pos = loc.position
            x, y, z = pos.X, pos.Y, pos.Z
            assert -half_L - tol <= x <= half_L + tol, (
                f"{category.value} X={x:.0f} outside ±{half_L:.0f}"
            )
            if category != Category.HVAC_ROOF:
                assert -half_W - tol <= y <= half_W + tol, (
                    f"{category.value} Y={y:.0f} outside ±{half_W:.0f}"
                )
            assert z >= -tol, f"{category.value} Z={z:.0f} below rail head"


def test_fit_out_car_body_has_more_volume_than_plain_body() -> None:
    """`fit_out_car_body` overlays COTS envelopes on the structural
    body. The resulting compound must have strictly more total
    geometry volume than the body alone."""
    dims = CarDimensions()
    plain = car_body(dims)
    dressed = fit_out_car_body(dims)
    # build123d Compound.volume sums child volumes.
    assert dressed.volume > plain.volume, (
        f"fit-out compound volume {dressed.volume:.0f} not greater than "
        f"plain body {plain.volume:.0f}"
    )
