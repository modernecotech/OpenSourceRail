from __future__ import annotations

import json

from engineering.design_detail_register import (
    DEFAULT_JSON,
    DEFAULT_MD,
    build_register,
    render_markdown,
    write,
)


def test_design_detail_register_covers_redesign_bim_and_mechanical_controls() -> None:
    register = build_register()
    assert register["passed"]
    assert register["schema"] == "org.opensourcerail.design-detail-register.v1"
    assert register["summary"] == {
        "bim_asset_types": 5,
        "controlled_lm3_ids": 39,
        "datum_systems": 9,
        "design_impacts": 6,
        "load_cases": 10,
        "mechanical_interfaces": 12,
        "route_compatibility_gates": 7,
        "verification_rows": 9,
    }
    dispositions = {row["id"]: row["disposition"] for row in register["design_impacts"]}
    assert dispositions["OSR-IMP-WATER-002"] == "bridge-or-reroute-required"
    assert dispositions["OSR-IMP-LM3-005"] == "compatibility-requalification-before-vehicle-redesign"
    assert set(register["change_policy"]["not_automatically_changed"]) >= {
        "LM3 three-car architecture",
        "bogie and articulation concept",
    }


def test_every_mechanical_interface_is_traceable_and_honest_about_release() -> None:
    register = build_register()
    known_datums = {row["id"] for row in register["datum_systems"]}
    controlled = set(register["controlled_lm3_ids"])
    for interface in register["mechanical_interfaces"]:
        assert {interface["parent_datum"], interface["child_datum"]} <= known_datums
        assert interface["source_product_ids"]
        assert set(interface["source_product_ids"]) <= controlled
        assert interface["verification"]
        assert interface["route_requalification_gate"]
        assert interface["tolerance_status"] == "allocation-open-until-stack-and-supplier-freeze"
        assert "release-evidence-open" in interface["evidence_status"]


def test_design_detail_outputs_are_deterministic_and_checkable(tmp_path) -> None:
    first_json = tmp_path / "first.json"
    first_md = tmp_path / "first.md"
    second_json = tmp_path / "second.json"
    second_md = tmp_path / "second.md"
    write(first_json, first_md)
    write(second_json, second_md)
    assert first_json.read_bytes() == second_json.read_bytes()
    assert first_md.read_bytes() == second_md.read_bytes()
    assert json.loads(first_json.read_text())["passed"] is True
    assert "All five steps are implemented" in render_markdown(build_register())


def test_tracked_design_detail_outputs_match_the_generator() -> None:
    register = build_register()
    assert DEFAULT_JSON.read_text(encoding="utf-8") == json.dumps(
        register, indent=2, sort_keys=True
    ) + "\n"
    assert DEFAULT_MD.read_text(encoding="utf-8") == render_markdown(register)
