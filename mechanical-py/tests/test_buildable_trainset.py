from __future__ import annotations

import json

from osr_mech.buildable_trainset import (
    Layer,
    Route,
    buildable_trainset_design,
    critical_path_payload,
    joint_control_rows,
    mass_budget_payload,
    render_critical_path,
    render_joint_control_schedule,
    render_mass_budget,
    render_manifest,
    render_open_release_gaps,
    render_review,
    write_definition_pack,
    write_shop_traveler_pack,
    write_outputs,
)
from osr_mech.common import ConsistFamily
from osr_mech.rolling_stock.bom_trace import (
    PROCUREMENT_BOM_ENGINEERING_IDS,
    bom_line_ids_for_engineering_id,
    bom_scope,
)


def test_buildable_trainset_has_full_product_tree() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    assert len(design.product_items) >= 69
    assert len(design.assemblies) >= 16
    assert any(item.route is Route.MAKE for item in design.product_items)
    assert any(item.route is Route.BID for item in design.product_items)
    assert any(item.route is Route.SOURCE for item in design.product_items)
    assert any(node.layer is Layer.TRAINSET for node in design.assemblies)
    assembly_ids = {node.id for node in design.assemblies}
    item_ids = {item.id for item in design.product_items}
    for item in design.product_items:
        assert item.parent in assembly_ids, f"{item.id} parent {item.parent} is not an assembly node"
        assert item.acceptance, f"{item.id} has no acceptance route"
        assert item.source_refs, f"{item.id} is not traceable to a source"
    for node in design.assemblies:
        assert node.hold_points, f"{node.id} has no assembly hold point"
        for child in node.children:
            assert child in assembly_ids | item_ids, f"{node.id} has dangling child {child}"

    ownership_rows = [
        (child, node.id)
        for node in design.assemblies
        for child in node.children
        if child in item_ids
    ]
    owners = dict(ownership_rows)
    assert len(ownership_rows) == len(item_ids), "a product item occurs in more than one assembly BOM"
    assert len(owners) == len(item_ids), "each product item must occur in exactly one assembly BOM"
    for item in design.product_items:
        assert owners[item.id] == item.parent, f"{item.id} is not owned by its declared parent"


def test_every_procurement_bom_line_resolves_to_the_engineering_tree() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    engineering_ids = {item.id for item in design.product_items} | {
        node.id for node in design.assemblies
    }
    expected_bom_ids = {
        *(f"B{i}" for i in range(1, 30)),
        *(f"G{i}" for i in range(1, 22)),
        *(f"T{i}" for i in range(1, 24)),
        *(f"E{i}" for i in range(1, 24)),
        *(f"A{i}" for i in range(1, 5)),
    }
    assert set(PROCUREMENT_BOM_ENGINEERING_IDS) == expected_bom_ids
    for line_id, linked_ids in PROCUREMENT_BOM_ENGINEERING_IDS.items():
        assert linked_ids, f"{line_id} has no engineering assignment"
        assert set(linked_ids) <= engineering_ids, f"{line_id} has an unresolved engineering ID"
        assert bom_scope(line_id) in {
            "component-or-kit",
            "material-or-consumable",
            "manufacturing-process",
        }

    for item in design.product_items:
        assert bom_line_ids_for_engineering_id(item.id), f"{item.id} is absent from the procurement BOM crosswalk"


def test_fabricated_parts_have_make_routes_and_final_trainset_assembles() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    make_items = [item for item in design.product_items if item.route is Route.MAKE]
    assert make_items, "no fabricated MAKE items are present"
    assert all(item.layer is Layer.FABRICATED_PART for item in make_items)
    assert all(item.make_or_buy_basis for item in make_items)
    assert all(item.acceptance for item in make_items)

    assemblies = {node.id: node for node in design.assemblies}
    trainset = assemblies["LM3-TRAINSET-A000"]
    assert trainset.layer is Layer.TRAINSET
    assert {
        "LM3-CAR-A900",
        "LM3-ART-SA800",
        "LM3-END-SA700",
        "LM3-SYS-SA900",
    } <= set(trainset.children)
    assert assemblies["LM3-CAR-A900"].quantity_per_trainset == 3


def test_added_component_gaps_are_integrated_into_expected_subassemblies() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    items = {item.id: item for item in design.product_items}
    assemblies = {node.id: node for node in design.assemblies}
    expected_items = {
        "LM3-BDY-P100",
        "LM3-BDY-P110",
        "LM3-ROOF-P010",
        "LM3-ROOF-P020",
        "LM3-HV-P010",
        "LM3-HV-P020",
        "LM3-HV-P030",
        "LM3-TRC-P050",
        "LM3-TRC-P060",
        "LM3-TRC-P070",
        "LM3-SAF-P010",
        "LM3-BOG-P050",
        "LM3-BOG-P060",
        "LM3-BOG-P061",
        "LM3-BOG-P031",
        "LM3-BOG-P041",
        "LM3-END-P030",
        "LM3-END-P040",
        "LM3-ART-P030",
        "LM3-INT-P010",
        "LM3-CWL-P011",
        "LM3-CWL-P012",
        "LM3-CWL-P013",
        "LM3-CWL-P014",
        "LM3-CWL-P015",
        "LM3-CWL-P016",
        "LM3-INT-P020",
        "LM3-INT-P030",
        "LM3-INT-P040",
        "LM3-INT-P050",
        "LM3-BDY-P120",
        "LM3-BDY-P130",
        "LM3-BDY-P140",
        "LM3-EXT-P080",
        "LM3-EXT-P090",
        "LM3-AUX-P010",
        "LM3-CTRL-P020",
        "LM3-CTRL-P030",
        "LM3-CTRL-P040",
        "LM3-CTRL-P050",
        "LM3-END-P050",
    }
    assert expected_items <= items.keys()
    assert {"LM3-BDY-P100", "LM3-EXT-P010"} <= set(assemblies["LM3-DOOR-SA310"].children)
    assert {"LM3-BDY-P110", "LM3-EXT-P020"} <= set(assemblies["LM3-WIN-SA320"].children)
    assert {"LM3-ROOF-P010", "LM3-ROOF-P020", "LM3-TRC-P050"} <= set(assemblies["LM3-ROOF-SA410"].children)
    assert {"LM3-HV-P010", "LM3-HV-P020", "LM3-HV-P030", "LM3-TRC-P060", "LM3-TRC-P070", "LM3-SAF-P010"} <= set(assemblies["LM3-HV-SA510"].children)
    assert {"LM3-BOG-P050", "LM3-BOG-P060"} <= set(assemblies["LM3-BOG-SA610"].children)
    assert {"LM3-BOG-P031", "LM3-BOG-P041", "LM3-BOG-P061"} <= set(
        assemblies["LM3-BOG-SA620"].children
    )
    assert {
        "LM3-CWL-P010",
        "LM3-CWL-P011",
        "LM3-CWL-P012",
        "LM3-CWL-P013",
        "LM3-CWL-P014",
        "LM3-CWL-P015",
        "LM3-CWL-P016",
    } <= set(assemblies["LM3-CWL-SA710"].children)
    assert "LM3-CWL-SA710" in assemblies["LM3-END-SA700"].children
    assert {"LM3-INT-P020", "LM3-INT-P030", "LM3-INT-P040", "LM3-INT-P050"} <= set(
        assemblies["LM3-INT-SA330"].children
    )
    assert "LM3-BDY-P120" in assemblies["LM3-BDY-SA110"].children
    assert {"LM3-BDY-P130", "LM3-BDY-P140", "LM3-EXT-P080", "LM3-EXT-P090"} <= set(
        assemblies["LM3-SHELL-A200"].children
    )
    assert "LM3-AUX-P010" in assemblies["LM3-CAR-A900"].children
    assert {"LM3-CTRL-P010", "LM3-CTRL-P020", "LM3-CTRL-P030", "LM3-CTRL-P040", "LM3-CTRL-P050"} <= set(
        assemblies["LM3-SYS-SA900"].children
    )
    assert "LM3-END-P050" in assemblies["LM3-END-SA700"].children


def test_buildable_trainset_links_optimizer_target_to_current_review() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    assert design.candidate.feasible
    assert design.target_candidate["motor"] == design.candidate.parameters.motor_id
    findings = {finding.id: finding for finding in design.review_findings}
    assert findings["BDR-003"].status == "green"
    assert "matches the optimizer target" in findings["BDR-003"].finding
    assert "250 kW continuous / 350 kW peak" in findings["BDR-003"].action
    assert "180 kWh usable / 225 kWh gross" in findings["BDR-003"].action


def test_mass_budget_reconciles_optimizer_subtotal_and_controlled_tare() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    payload = mass_budget_payload(design)
    assert payload["modeled_subtotal_kg"] == 75_308
    assert payload["engineering_reserve_kg"] == 3_442
    assert payload["controlled_planning_tare_kg"] == 78_750
    assert sum(design.candidate.mass_breakdown_kg.values()) == 75_307.53
    assert "Controlled planning tare" in render_mass_budget(design)


def test_every_integration_joint_has_machine_readable_join_and_torque_control() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    rows = joint_control_rows(design)
    assert rows
    assert len({row["joint_id"] for row in rows}) == len(rows)
    assert all(row["join_classes"] for row in rows)
    assert all(row["torque_authority"] for row in rows)
    assert all(row["release_status"] for row in rows)
    schedule = render_joint_control_schedule(design)
    assert "Numeric" in schedule and "torques are intentionally prohibited" in schedule


def test_write_outputs_emits_mass_and_joint_control_records(tmp_path) -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    write_outputs(design, tmp_path)
    assert (tmp_path / "mass-budget.json").exists()
    assert (tmp_path / "mass-budget.md").exists()
    assert (tmp_path / "joint-control-schedule.json").exists()
    assert (tmp_path / "joint-control-schedule.md").exists()
    assert (tmp_path / "critical-path.json").exists()
    assert (tmp_path / "critical-path.md").exists()


def test_critical_path_models_parallel_train_fabrication() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    payload = critical_path_payload(design)
    tasks = {task["id"]: task for task in payload["tasks"]}
    assert payload["project_duration_days"] == 35.0
    assert payload["total_labor_hours"] > 5_000
    assert payload["minimum_space_model"]["long_train_bays"] == 1
    assert tasks["CP-060"]["early_start_day"] == tasks["CP-020"]["early_start_day"]
    assert tasks["CP-060"]["total_float_days"] > 0
    assert tasks["CP-110"]["critical"]
    assert tasks["CP-150"]["critical"]
    assert "internal furnishings" in tasks["CP-110"]["title"]
    rendered = render_critical_path(design)
    assert "Critical-path table" in rendered
    assert "Space and parallelism" in rendered
    assert "55 m final assembly track" in rendered


def test_buildable_manifest_and_review_render_key_sections() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    manifest = render_manifest(design)
    review = render_review(design)
    gaps = render_open_release_gaps(design)
    assert "Assembly tree" in manifest
    assert "Product items" in manifest
    assert "LM3-TRAINSET-A000" in manifest
    assert "Immediate build-package work" in review
    assert "BDR-005" in review
    assert "Trainset open release gap register" in gaps
    assert "LM3-BOG-P041" in gaps
    assert "Non-product release gates" in gaps


def test_definition_pack_generates_every_part_subassembly_assembly_and_trainset(tmp_path) -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    pack = write_definition_pack(design, tmp_path / "definitions")

    expected_ids = {item.id for item in design.product_items} | {node.id for node in design.assemblies}
    generated_ids = {
        path.stem
        for path in pack.definition_files
        if path.suffix == ".json" and path.name != "index.json"
    }
    assert generated_ids == expected_ids
    assert pack.index_json.exists()
    assert pack.index_md.exists()

    for definition_id in expected_ids:
        matches = [path for path in pack.definition_files if path.stem == definition_id]
        suffixes = {path.suffix for path in matches}
        assert {".json", ".md"} <= suffixes, f"{definition_id} is missing json/md definitions"

    assert (tmp_path / "definitions/parts/LM3-BDY-P010.md").exists()
    assert (tmp_path / "definitions/subassemblies/LM3-BDY-SA110.md").exists()
    assert (tmp_path / "definitions/assemblies/LM3-CAR-A900.md").exists()
    assert (tmp_path / "definitions/trainsets/LM3-TRAINSET-A000.md").exists()

    car_definition = json.loads((tmp_path / "definitions/assemblies/LM3-CAR-A900.json").read_text())
    assert car_definition["integration_steps"]
    assert car_definition["material_spec"]["material_family"]
    assert car_definition["process_spec"]["primary_processes"]
    assert all(step["placement_zone"] for step in car_definition["integration_steps"])
    assert all(step["interface_classes"] for step in car_definition["integration_steps"])
    assert all(step["verification"] for step in car_definition["integration_steps"])

    make_definition = json.loads((tmp_path / "definitions/parts/LM3-BDY-P010.json").read_text())
    assert make_definition["material_spec"]["grade_or_part_class"]
    assert make_definition["material_spec"]["evidence_required"]
    assert make_definition["process_spec"]["inspection_methods"]
    assert "WPS" in " ".join(make_definition["process_spec"]["special_process_controls"])

    source_definition = json.loads((tmp_path / "definitions/parts/LM3-EXT-P050.json").read_text())
    assert source_definition["material_spec"]["traceability"]
    assert source_definition["process_spec"]["release_level"].startswith("SOURCE supplier-controlled")

    cowl_definition = json.loads((tmp_path / "definitions/parts/LM3-CWL-P011.json").read_text())
    assert "fiberglass" in cowl_definition["material_spec"]["material_family"]
    assert "lay up" in " ".join(cowl_definition["process_spec"]["primary_processes"])

    cabin_definition = json.loads((tmp_path / "definitions/parts/LM3-INT-P020.json").read_text())
    assert "cabin" in cabin_definition["material_spec"]["material_family"]
    assert "fire-material certificate" in cabin_definition["material_spec"]["evidence_required"]

    side_material_definition = json.loads((tmp_path / "definitions/parts/LM3-EXT-P080.json").read_text())
    assert "material pack" in side_material_definition["material_spec"]["material_family"]
    assert "1,000 mm side-module mould pitch" in side_material_definition["material_spec"]["nominal_section"]
    assert "bonded to the released side-frame" not in side_material_definition["make_or_buy_basis"]

    hv_definition = json.loads((tmp_path / "definitions/subassemblies/LM3-HV-SA510.json").read_text())
    hv_children = {step["child_id"]: step for step in hv_definition["integration_steps"]}
    assert "high-voltage electrical" in hv_children["LM3-TRC-P070"]["interface_classes"]
    assert "fluid/thermal" in hv_children["LM3-SAF-P010"]["interface_classes"]


def test_shop_travelers_generate_labor_tooling_revision_and_signoff_blocks(tmp_path) -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    pack = write_shop_traveler_pack(design, tmp_path / "travelers")
    expected_ids = {item.id for item in design.product_items} | {node.id for node in design.assemblies}
    generated_ids = {
        path.stem
        for path in pack.traveler_files
        if path.suffix == ".json" and path.name != "index.json"
    }
    assert generated_ids == expected_ids
    assert pack.index_json.exists()
    assert pack.index_md.exists()

    hv_traveler = json.loads((tmp_path / "travelers/subassemblies/LM3-HV-SA510.json").read_text())
    assert hv_traveler["release_status"] == "unsigned-template"
    assert hv_traveler["estimated_labor_hours"] > 0
    assert hv_traveler["material_spec"]["evidence_required"]
    assert hv_traveler["process_spec"]["special_process_controls"]
    assert hv_traveler["revision_approvals"]
    assert {approval["role"] for approval in hv_traveler["revision_approvals"]} >= {
        "manufacturing engineering",
        "quality",
        "design authority",
    }
    assert hv_traveler["signoff_blocks"]
    assert all(block["signature"] == "" for block in hv_traveler["signoff_blocks"])
    assert all(operation["tooling_ids"] for operation in hv_traveler["operations"])
    assert any("LM3-TRC-P070" in operation["title"] for operation in hv_traveler["operations"])

    make_part = json.loads((tmp_path / "travelers/parts/LM3-BDY-P100.json").read_text())
    assert make_part["route"] == "MAKE"
    assert make_part["material_spec"]["governing_standard"]
    assert make_part["process_spec"]["tooling_basis"]
    assert any("cut, form, machine" in operation["title"] for operation in make_part["operations"])

    body_module = json.loads((tmp_path / "travelers/parts/LM3-BDY-P130.json").read_text())
    body_module_operations = " ".join(operation["title"] for operation in body_module["operations"]).lower()
    assert "inspect mould" in body_module_operations
    assert "lay up glass-fibre" in body_module_operations
    assert "demould" in body_module_operations
    assert "cnc trim" in body_module_operations
    assert not any("cut, form, machine" in operation["title"] for operation in body_module["operations"])

    assert (tmp_path / "travelers/trainsets/LM3-TRAINSET-A000.md").exists()


def test_every_definition_and_traveler_has_structured_material_and_process_specs(tmp_path) -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    definition_pack = write_definition_pack(design, tmp_path / "definitions")
    traveler_pack = write_shop_traveler_pack(design, tmp_path / "travelers")

    required_material_keys = {
        "material_family",
        "grade_or_part_class",
        "governing_standard",
        "form_factor",
        "nominal_section",
        "finish_or_protection",
        "traceability",
        "evidence_required",
    }
    required_process_keys = {
        "primary_processes",
        "joining_methods",
        "special_process_controls",
        "inspection_methods",
        "tooling_basis",
        "release_level",
    }

    generated_payloads = [
        path
        for path in (*definition_pack.definition_files, *traveler_pack.traveler_files)
        if path.suffix == ".json" and path.name != "index.json"
    ]
    assert generated_payloads
    for path in generated_payloads:
        payload = json.loads(path.read_text())
        assert required_material_keys <= payload["material_spec"].keys(), path
        assert required_process_keys <= payload["process_spec"].keys(), path
        assert all(payload["material_spec"][key] for key in required_material_keys), path
        assert all(payload["process_spec"][key] for key in required_process_keys), path
