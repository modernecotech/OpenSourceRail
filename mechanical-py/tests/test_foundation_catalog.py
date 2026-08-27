"""Geotechnical-zone foundation catalogue regressions."""

from __future__ import annotations

import pytest

from osr_mech.civil.foundation import (
    foundation_catalog,
    foundation_concrete_m3,
    foundation_installed_record,
    select_geotechnical_system,
    select_ground_improvement,
    select_foundation,
)


def test_catalogue_has_interface_and_release_data_for_every_type() -> None:
    catalogue = foundation_catalog()
    assert len(catalogue["foundation_types"]) >= 5
    assert catalogue["release_gates"]["actual_length_and_cost_per_support_required"] is True
    assert catalogue["release_gates"]["foundations_ahead_of_erection_bays_min"] == 10
    for item in catalogue["foundation_types"]:
        assert item["interface"]
        assert item["cost_basis"]


@pytest.mark.parametrize(
    ("ground_class", "expected"),
    [
        ("rock", "shallow-spread"),
        ("urban-alluvium", "bored-shaft"),
        ("uniform-soft-ground", "driven-pile-bent"),
        ("weak-liquefiable", "pile-group"),
        ("viaduct-end", "reinforced-soil-abutment"),
    ],
)
def test_selection_is_deterministic_by_ground_and_access_class(
    ground_class: str, expected: str
) -> None:
    assert select_foundation(ground_class).id == expected


def test_deep_quantity_rejects_the_old_fixed_length_placeholder() -> None:
    with pytest.raises(ValueError, match="actual pile/shaft length"):
        foundation_concrete_m3("bored-shaft")
    assert foundation_concrete_m3("bored-shaft", actual_length_m=18.0) > 60.0
    with pytest.raises(ValueError, match="does not use"):
        foundation_concrete_m3("shallow-spread", actual_length_m=6.0)


def test_installed_record_carries_actual_length_time_test_and_cost() -> None:
    record = foundation_installed_record(
        "P-042",
        "bored-shaft",
        actual_length_m=18.0,
        actual_reinforcement_kg=8_400.0,
        installation_hours=22.5,
        actual_installed_cost_usd=48_600.0,
        test_result="representative zone load test passed",
    )
    assert record.actual_length_m == 18.0
    assert record.concrete_m3 > 60.0
    assert record.actual_installed_cost_usd == 48_600.0
    with pytest.raises(ValueError, match="actual installed cost"):
        foundation_installed_record(
            "P-043",
            "shallow-spread",
            installation_hours=4.0,
            actual_reinforcement_kg=2_500.0,
            actual_installed_cost_usd=0.0,
            test_result="inspection passed",
        )


def test_ground_supported_zones_select_improvement_not_foundation_concrete() -> None:
    rigid = select_ground_improvement("uniform-soft-ground")
    assert rigid.id == "rigid-inclusion-platform"
    assert "treated area" in rigid.design_measurement
    mixed = select_ground_improvement("uniform-soft-ground", strict_settlement_limit=False)
    assert mixed.id == "deep-soil-mixing"
    system = select_geotechnical_system(
        "uniform-soft-ground", structure="at-grade"
    )
    assert system.kind == "ground-improvement"
    assert system.id == "rigid-inclusion-platform"
    pier = select_geotechnical_system("uniform-soft-ground", structure="pier")
    assert pier.kind == "foundation"
    assert pier.id == "driven-pile-bent"
