from __future__ import annotations

import pytest

from osr_mech.freecad_sources import SOURCE_BUILDERS
from osr_mech.maintenance_interface import (
    lm3_bogie_change_datum,
    lm3_field_recovery_datum,
)
from osr_mech.rolling_stock.recovery import (
    RecoveryLoadCase,
    controlled_recovery_capacity_checks,
    field_recovery_load_cases,
    portable_field_rerailing_kit,
    recovery_mass_scenarios,
)
from osr_mech.recovery_interface import wayside_rerailing_access_interface


def test_field_recovery_datum_inherits_vehicle_jack_positions() -> None:
    depot = lm3_bogie_change_datum()
    field = lm3_field_recovery_datum()

    assert field.jack_positions_mm == depot.jack_positions_mm
    assert field.rail_gauge_mm == depot.rail_gauge_mm
    assert field.portable_cylinder_min_capacity_kn == 200.0
    assert field.portable_cylinder_max_unit_mass_kg <= 30.0


def test_mass_sensitivity_is_explicit_and_monotonic() -> None:
    controlled, minus_10, minus_20 = recovery_mass_scenarios()

    assert controlled.train_mass_kg == 78_750.0
    assert controlled.car_mass_kg == 26_250.0
    assert controlled.ideal_four_point_reaction_kn == pytest.approx(64.356, abs=0.001)
    assert minus_10.train_mass_kg == pytest.approx(70_875.0)
    assert minus_20.train_mass_kg == pytest.approx(63_000.0)
    assert controlled.train_mass_kg > minus_10.train_mass_kg > minus_20.train_mass_kg
    assert (
        controlled.ideal_four_point_reaction_kn
        > minus_10.ideal_four_point_reaction_kn
        > minus_20.ideal_four_point_reaction_kn
    )


def test_controlled_tare_portable_capacity_screen_passes_both_permitted_cases() -> None:
    checks = controlled_recovery_capacity_checks()
    assert {check.load_case.id for check in checks} == {
        "full-car-four-point",
        "one-end-two-point",
    }
    assert all(check.passes for check in checks)
    assert all(check.margin_kn > 0.0 for check in checks)
    assert max(check.required_point_capacity_kn for check in checks) < 160.0


def test_invalid_unilateral_or_nonphysical_load_case_is_rejected() -> None:
    unilateral = RecoveryLoadCase(
        id="unilateral",
        description="prohibited single-point lift",
        supported_car_mass_fraction=0.5,
        active_lift_points=1,
    )
    with pytest.raises(ValueError, match="at least two"):
        unilateral.maximum_point_reaction_kn(26_250.0)

    with pytest.raises(ValueError, match="positive"):
        field_recovery_load_cases()[0].maximum_point_reaction_kn(0.0)


def test_portable_rerailing_assembly_is_rail_specific_and_pad_aligned() -> None:
    kit = portable_field_rerailing_kit()
    labels = [child.label for child in kit.children]

    assert kit.volume > 0.0
    assert labels.count("Portable rail-rated 200 kN telescopic rerailing cylinder envelope") == 4
    assert labels.count("Wide-area cylinder baseplate and ground spreader") == 4
    assert labels.count("Tilting jack head and keyed LM3 pad adapter") == 4
    assert labels.count("Transverse aluminium rerailing bridge") == 2
    assert labels.count("Mechanical cribbing and secondary retention pack") == 4
    assert not any("scissor" in label.lower() for label in labels)

    cylinder_centres = {
        (
            (child.bounding_box().min.X + child.bounding_box().max.X) / 2.0,
            (child.bounding_box().min.Y + child.bounding_box().max.Y) / 2.0,
        )
        for child in kit.children
        if child.label == "Portable rail-rated 200 kN telescopic rerailing cylinder envelope"
    }
    assert cylinder_centres == set(lm3_field_recovery_datum().jack_positions_mm)


def test_wayside_interface_reserves_bearing_staging_and_handling_routes() -> None:
    interface = wayside_rerailing_access_interface()
    labels = [child.label for child in interface.children]

    assert interface.volume > 0.0
    assert labels.count("Field rerailing bridge placement and bearing zone") == 2
    assert labels.count("Unobstructed cross-track equipment handling route") == 2
    assert "Recovery vehicle offload and hydraulic-equipment staging interface" in labels
    assert "Temporary incident exclusion and controlled-access zone" in labels


def test_recovery_assemblies_are_registered_as_freecad_sources() -> None:
    assert "portable-field-rerailing-kit" in SOURCE_BUILDERS
    assert "civil-wayside-rerailing-access-interface" in SOURCE_BUILDERS
