import json
from pathlib import Path

from osr_mech.buildable_civil import build_payload, drawing_definitions, release_packages


ROOT = Path(__file__).resolve().parents[3]


def test_every_ifc_type_has_exact_release_assignment() -> None:
    payload = build_payload()
    source = json.loads(
        (ROOT / "engineering/models/bim/reference/civil-coordination.index.json").read_text()
    )
    assert {row["type_id"] for row in payload["type_register"]} == {
        row["type_id"] for row in source["types"]
    }
    assert payload["summary"] == {
        "ifc_reusable_types": 19,
        "ifc_occurrences": 138,
        "civil_owned_types": 9,
        "controlled_interface_types": 10,
        "release_packages": 6,
        "drawing_definition_briefs": 9,
        "tooling_and_gauge_families": 17,
    }


def test_drawing_briefs_cover_all_types() -> None:
    payload = build_payload()
    registered = {row["type_id"] for row in payload["type_register"]}
    covered = {type_id for drawing in drawing_definitions() for type_id in drawing.type_ids}
    assert covered == registered
    assert all(drawing.frozen_inputs and drawing.verification for drawing in drawing_definitions())


def test_packages_have_real_hold_points_and_tools() -> None:
    drawings = {drawing.id for drawing in drawing_definitions()}
    assert all(package.hold_points and package.tooling_ids for package in release_packages())
    assert {drawing for package in release_packages() for drawing in package.drawing_ids} == drawings


def test_tracked_generated_register_matches_generator() -> None:
    tracked = json.loads(
        (ROOT / "design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json").read_text()
    )
    assert tracked == build_payload()
    assert tracked["validation"] == {
        "all_ifc_types_classified_once": True,
        "all_ifc_types_have_drawing_coverage": True,
        "all_packages_have_hold_points": True,
        "site_specific_evidence_remains_open": True,
    }
