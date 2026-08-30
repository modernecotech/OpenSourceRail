from __future__ import annotations

import json
import zipfile

from osr_mech.trainset_manufacturing_methods import (
    JSON_OUTPUT,
    MARKDOWN_OUTPUT,
    load_and_validate,
    render_markdown,
)


def test_every_product_row_has_a_timed_manufacturing_method() -> None:
    data = load_and_validate()
    assert data["coverage"] == {
        "product_rows": 101,
        "covered_product_rows": 101,
        "method_count": 9,
        "tooling_count": 20,
        "uncovered_product_ids": [],
    }
    assert all(
        sum(step["planning_minutes"] for step in method["steps"])
        == method["planning_cycle_minutes"]
        for method in data["method"]
    )


def test_methods_cover_requested_mould_seal_floor_fixture_motor_and_coating_scope() -> None:
    data = load_and_validate()
    text = json.dumps(data).lower()
    for required in (
        "side-mould",
        "roof-mould",
        "cowl-mould",
        "seal compression",
        "water-ingress",
        "floor covering",
        "passenger-fixture",
        "motor/gearbox",
        "solar reflectance",
        "thermal emittance",
    ):
        assert required in text


def test_generated_method_artifacts_are_current() -> None:
    data = load_and_validate()
    assert json.loads(JSON_OUTPUT.read_text(encoding="utf-8")) == data
    assert MARKDOWN_OUTPUT.read_text(encoding="utf-8") == render_markdown(data)


def test_window_and_door_definitions_use_serviceable_interface_materials() -> None:
    root = JSON_OUTPUT.parent / "definitions/parts"
    window = json.loads((root / "LM3-WIN-P010.json").read_text(encoding="utf-8"))
    door = json.loads((root / "LM3-DOOR-P010.json").read_text(encoding="utf-8"))
    assert "aluminium" in window["material_spec"]["material_family"]
    assert "elastomer" in window["material_spec"]["material_family"]
    assert "structural steel" not in window["material_spec"]["material_family"]
    assert "adjustable" in door["material_spec"]["material_family"]
    assert "timed cassette removal/refit" in door["process_spec"]["inspection_methods"]


def test_interior_systems_are_independent_build_and_acceptance_rows() -> None:
    root = JSON_OUTPUT.parent / "definitions/parts"
    expected = {
        "LM3-EXT-P060": "floor-board",
        "LM3-EXT-P061": "floor-covering",
        "LM3-EXT-P062": "seat",
        "LM3-EXT-P063": "handrail",
        "LM3-EXT-P064": "passenger-information",
        "LM3-EXT-P065": "cctv",
        "LM3-EXT-P066": "prm",
    }
    for product_id, material_fragment in expected.items():
        payload = json.loads((root / f"{product_id}.json").read_text(encoding="utf-8"))
        assert material_fragment in payload["material_spec"]["material_family"].lower()
        assert len(payload["acceptance"]) >= 4


def test_freecad_tooling_is_selectable_and_carries_method_instructions() -> None:
    path = JSON_OUTPUT.parents[2] / "models/cad/lm3-manufacturing-tooling.FCStd"
    with zipfile.ZipFile(path) as archive:
        document = archive.read("Document.xml").decode("utf-8")
        assert all(info.date_time == (2000, 1, 1, 0, 0, 0) for info in archive.infolist())
    assert document.count('type="Part::Feature"') == 20
    assert document.count('name="OSRId"') == 20
    assert document.count('name="StepInstructionsJson"') == 20
    assert document.count('value="2000-01-01T00:00:00Z"') == 2
    for method_number in range(10, 100, 10):
        assert f"LM3-MFG-{method_number:03d}" in document
