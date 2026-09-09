import json
from pathlib import Path

from osr_mech.buildable_civil import (
    build_payload,
    civil_inspection_plan_payload,
    construction_control_record_template,
    construction_control_payload,
    drawing_definitions,
    release_packages,
)


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


def test_construction_controls_cover_execution_and_stop_conditions() -> None:
    controls = construction_control_payload()
    assert controls["control_count"] == 10
    assert all(row["sequence"] and row["hold"] and row["release_evidence"] for row in controls["controls"])
    text = json.dumps(controls).lower()
    for scope in ("precast mould", "transport", "girder erection", "at-grade", "track", "nonconformance"):
        assert scope in text
    assert "not-ifc-release" in controls["status"]
    record = construction_control_record_template(controls)
    assert record["template_status"] == "unfilled-not-construction-evidence"
    assert len(record["controls"]) == 10
    assert all(row["control_disposition"] == "open" for row in record["controls"])
    assert all(step["status"] == "not-performed" for row in record["controls"] for step in row["steps"])


def test_civil_itp_covers_packages_and_ifc_types_without_claiming_results() -> None:
    plan = civil_inspection_plan_payload(build_payload())
    assert plan["package_count"] == 6
    assert plan["characteristic_count"] == 114
    assert all(plan["validation"].values())
    assert all(package["package_disposition"] == "open" for package in plan["packages"])
    assert all(
        row["execution_status"] == "not-performed"
        for package in plan["packages"]
        for row in package["characteristics"]
    )


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
        "all_construction_controls_have_hold_and_handback": True,
        "all_packages_have_construction_control_routes": True,
    }
    assert all(row["reference_control_ids"] for row in tracked["release_packages"])
