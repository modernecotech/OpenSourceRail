from __future__ import annotations

from osr_mech.civil.railway_interfaces import (
    approach_transition_interface,
    bearing_replacement_interface,
    deck_expansion_joint_interface,
    railway_interface_kit,
    walkway_service_cassette,
)


def test_reusable_civil_interfaces_are_positive_volume_and_labelled() -> None:
    interfaces = (
        bearing_replacement_interface(),
        deck_expansion_joint_interface(),
        walkway_service_cassette(),
        approach_transition_interface(),
    )
    assert all(item.volume > 0 for item in interfaces)
    assert all(item.children and all(child.label for child in item.children) for item in interfaces)
    assert any("clearance" in child.label.lower() for child in interfaces[0].children)
    assert any("drain" in child.label.lower() for child in interfaces[1].children)
    assert any("HV" in child.label for child in interfaces[2].children)
    assert any("survey datum" in child.label for child in interfaces[3].children)


def test_combined_interface_kit_contains_all_four_modules() -> None:
    kit = railway_interface_kit()
    assert len(kit.children) == 4
    assert kit.volume == sum(child.volume for child in kit.children)
