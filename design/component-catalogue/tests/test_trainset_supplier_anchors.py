from __future__ import annotations

import json
import zipfile

from osr_mech.trainset_supplier_anchors import (
    JSON_OUTPUT,
    MARKDOWN_OUTPUT,
    load_and_validate,
    render_markdown,
)


def test_every_bought_in_product_has_one_real_supplier_anchor() -> None:
    data = load_and_validate()
    assert data["coverage"] == {
        "external_product_rows": 56,
        "covered_external_product_rows": 56,
        "anchor_count": 27,
        "uncovered_product_ids": [],
    }
    assert len(data["product_to_anchor"]) == 56
    assert all(anchor["manufacturer_url"].startswith("https://") for anchor in data["anchor"])
    assert all(anchor["localisation"] and anchor["fit_gaps"] for anchor in data["anchor"])


def test_critical_running_gear_and_articulation_anchors_are_explicit() -> None:
    data = load_and_validate()
    expected = {
        "LM3-TRC-P010": "OSR-ANC-MOTOR-ABB-AMXM",
        "LM3-TRC-P020": "OSR-ANC-GEAR-VOITH-SE",
        "LM3-BOG-P040": "OSR-ANC-WHEELSET-GHH",
        "LM3-BOG-P042": "OSR-ANC-AXLEBOX-SKF",
        "LM3-BOG-P046": "OSR-ANC-SUSPENSION-CONTI",
        "LM3-BOG-P048": "OSR-ANC-BRAKE-KNORR",
        "LM3-ART-P020": "OSR-ANC-JOINT-SCHAEFFLER",
        "LM3-ART-P022": "OSR-ANC-GANGWAY-HUBNER",
    }
    assert {key: data["product_to_anchor"][key] for key in expected} == expected


def test_definitions_embed_anchor_and_controlled_equivalence_rules() -> None:
    root = JSON_OUTPUT.parent / "definitions/parts"
    motor = json.loads((root / "LM3-TRC-P010.json").read_text(encoding="utf-8"))
    assert motor["parent"] == "LM3-TRC-SA615"
    assert motor["supplier_anchor"]["manufacturer"] == "ABB"
    assert motor["supplier_anchor"]["local_equivalent_allowed"] is True
    assert len(motor["supplier_anchor"]["mandatory_equivalence"]) >= 6


def test_generated_supplier_register_is_current() -> None:
    data = load_and_validate()
    assert json.loads(JSON_OUTPUT.read_text(encoding="utf-8")) == data
    assert MARKDOWN_OUTPUT.read_text(encoding="utf-8") == render_markdown(data)


def test_freecad_review_model_carries_assembly_and_anchor_metadata() -> None:
    path = JSON_OUTPUT.parents[2] / "models/cad/chassis-bogie-assembly-states.FCStd"
    with zipfile.ZipFile(path) as archive:
        document = archive.read("Document.xml").decode("utf-8")
    for required in (
        "LM3-BDY-SA110",
        "LM3-BOG-SA611",
        "LM3-TRC-SA615",
        "LM3-BOG-P046 | LM3-BOG-P047",
        "OSR-ANC-MOTOR-ABB-AMXM | OSR-ANC-GEAR-VOITH-SE",
    ):
        assert required in document
