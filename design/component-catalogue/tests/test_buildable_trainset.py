from __future__ import annotations

import json

from osr_mech.buildable_trainset import (
    Layer,
    Route,
    buildable_trainset_design,
    critical_path_payload,
    factory_plan_payload,
    joint_control_rows,
    mass_budget_payload,
    product_mass_closure_payload,
    render_critical_path,
    render_factory_plan,
    render_joint_control_schedule,
    render_mass_budget,
    render_product_mass_closure,
    render_manifest,
    render_open_release_gaps,
    render_trainset_build_cost,
    render_review,
    render_small_component_standard,
    render_train_end_interface,
    train_end_interface_payload,
    trainset_build_cost_payload,
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
from osr_mech.rolling_stock.mass_closure import mass_properties_record_template


def test_buildable_trainset_has_full_product_tree() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    assert len(design.product_items) == 120
    assert len(design.assemblies) == 26
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
        "LM3-BDY-P021",
        "LM3-BDY-P061",
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
        "LM3-BDY-P131",
        "LM3-BDY-P132",
        "LM3-BDY-P133",
        "LM3-BDY-P140",
        "LM3-EXT-P080",
        "LM3-EXT-P090",
        "LM3-FIN-P010",
        "LM3-FIN-P020",
        "LM3-ROOF-P030",
        "LM3-ROOF-P040",
        "LM3-FAS-P010",
        "LM3-FAS-P020",
        "LM3-FAS-P030",
        "LM3-INT-P021",
        "LM3-INT-P022",
        "LM3-INT-P031",
        "LM3-INT-P032",
        "LM3-INT-P041",
        "LM3-INT-P051",
        "LM3-INT-P052",
        "LM3-AUX-P010",
        "LM3-CTRL-P020",
        "LM3-CTRL-P030",
        "LM3-CTRL-P040",
        "LM3-CTRL-P050",
        "LM3-END-P050",
        "LM3-END-P060",
        "LM3-END-P061",
        "LM3-END-P062",
        "LM3-ART-P040",
        "LM3-ART-P041",
        "LM3-FIX-P010",
        "LM3-FIX-P020",
        "LM3-FIX-P030",
        "LM3-WIN-P010",
        "LM3-DOOR-P010",
        "LM3-LGT-P010",
        "LM3-LGT-P020",
    }
    assert expected_items <= items.keys()
    assert {"LM3-BDY-P100", "LM3-EXT-P010"} <= set(assemblies["LM3-DOOR-SA310"].children)
    assert {"LM3-BDY-P110", "LM3-EXT-P020"} <= set(assemblies["LM3-WIN-SA320"].children)
    assert {"LM3-FIX-P010", "LM3-FIX-P020", "LM3-FIX-P030"} == set(assemblies["LM3-FIX-SA340"].children)
    assert {"LM3-LGT-P010", "LM3-LGT-P020"} == set(assemblies["LM3-LGT-SA350"].children)
    assert {"LM3-ROOF-P010", "LM3-ROOF-P020", "LM3-TRC-P050"} <= set(assemblies["LM3-ROOF-SA410"].children)
    assert {"LM3-HV-P010", "LM3-HV-P020", "LM3-HV-P030", "LM3-TRC-P060", "LM3-TRC-P070", "LM3-SAF-P010"} <= set(assemblies["LM3-HV-SA510"].children)
    assert {"LM3-BOG-SA611", "LM3-TRC-SA615", "LM3-BOG-P046", "LM3-BOG-P060"} <= set(assemblies["LM3-BOG-SA610"].children)
    assert {"LM3-BOG-P031", "LM3-BOG-SA621", "LM3-BOG-P047", "LM3-BOG-P061"} <= set(
        assemblies["LM3-BOG-SA620"].children
    )
    assert {"LM3-BOG-P040", "LM3-BOG-P042", "LM3-BOG-P044", "LM3-BOG-P048"} == set(
        assemblies["LM3-BOG-SA611"].children
    )
    assert {"LM3-TRC-P010", "LM3-TRC-P020", "LM3-BOG-P050"} == set(
        assemblies["LM3-TRC-SA615"].children
    )
    assert {"LM3-BOG-P041", "LM3-BOG-P043", "LM3-BOG-P045", "LM3-BOG-P049"} == set(
        assemblies["LM3-BOG-SA621"].children
    )
    assert {"LM3-ART-P010", "LM3-ART-P020", "LM3-ART-P021"} == set(
        assemblies["LM3-ART-SA810"].children
    )
    assert {"LM3-ART-P022", "LM3-ART-P023"} == set(assemblies["LM3-ART-SA820"].children)
    assert {"LM3-ART-P024", "LM3-ART-P030"} == set(assemblies["LM3-ART-SA830"].children)
    assert {"LM3-ART-SA810", "LM3-ART-SA820", "LM3-ART-SA830"} == set(
        assemblies["LM3-ART-SA800"].children
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
    assert {"LM3-BDY-P020", "LM3-BDY-P021"} <= set(assemblies["LM3-BDY-SA110"].children)
    assert {"LM3-BDY-P060", "LM3-BDY-P061"} <= set(assemblies["LM3-BDY-SA120"].children)
    assert {"LM3-BDY-P130", "LM3-BDY-P131", "LM3-BDY-P132", "LM3-BDY-P133", "LM3-BDY-P140", "LM3-EXT-P080", "LM3-EXT-P090", "LM3-FIN-P010"} <= set(
        assemblies["LM3-SHELL-A200"].children
    )
    assert {"LM3-ROOF-P030", "LM3-ROOF-P040", "LM3-FIN-P020"} <= set(assemblies["LM3-ROOF-SA410"].children)
    assert {"LM3-FAS-P010", "LM3-FAS-P020", "LM3-FAS-P030"} <= set(assemblies["LM3-CWL-SA710"].children)
    assert {"LM3-INT-P021", "LM3-INT-P022", "LM3-INT-P031", "LM3-INT-P032", "LM3-INT-P041", "LM3-INT-P051", "LM3-INT-P052"} <= set(assemblies["LM3-INT-SA330"].children)
    assert "LM3-AUX-P010" in assemblies["LM3-CAR-A900"].children
    assert {"LM3-CTRL-P010", "LM3-CTRL-P020", "LM3-CTRL-P030", "LM3-CTRL-P040", "LM3-CTRL-P050"} <= set(
        assemblies["LM3-SYS-SA900"].children
    )
    assert "LM3-END-P050" in assemblies["LM3-END-SA700"].children
    assert {"LM3-END-P060", "LM3-END-P061", "LM3-END-P062"} <= set(assemblies["LM3-EIF-SA650"].children)
    assert {"LM3-EIF-SA650", "LM3-ART-P040", "LM3-ART-P041"} <= set(
        assemblies["LM3-TTART-SA850"].children
    )
    assert "LM3-EIF-SA650" in assemblies["LM3-TRAINSET-A000"].children
    assert items["LM3-END-P061"].quantity_per_trainset == 2
    assert items["LM3-END-P062"].quantity_per_trainset == 0
    assert items["LM3-ART-P040"].quantity_per_trainset == 0


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


def test_product_mass_closure_maps_every_row_and_keeps_lightweight_option_unpromoted() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    payload = product_mass_closure_payload(design)
    coverage = payload["coverage"]
    assert coverage == {
        "product_rows": 120,
        "active_product_rows": 117,
        "mapped_product_rows": 120,
        "closed_active_product_rows": 0,
        "category_count": 9,
        "categories_reconciled_to_controlled_subtotal": True,
    }
    assert round(sum(row["modeled_planning_budget_kg"] for row in payload["categories"])) == 75_308
    assert {row["product_id"] for row in payload["product_rows"]} == {
        item.id for item in design.product_items
    }
    assert all(row["closed_mass_kg"] is None for row in payload["product_rows"])

    light = payload["lightweighting"]
    assert light["lightest_existing_feasible_modeled_mass_kg"] == 73_375.62
    assert light["modeled_saving_kg"] == 1_931.91
    assert light["lightest_candidate_with_unchanged_reserve_kg"] == 76_817.62
    assert "retain the 78,750 kg" in light["decision"]

    scenarios = {row["id"]: row for row in payload["recovery_load_case_link"]["scenarios"]}
    assert set(scenarios) == {
        "controlled-planning-tare",
        "lightest-existing-feasible-design-space-with-same-reserve",
        "tare-minus-10-percent",
        "tare-minus-20-percent",
    }
    assert all(
        case["passes_planning_envelope"]
        for scenario in scenarios.values()
        for case in scenario["load_cases"]
    )
    rendered = render_product_mass_closure(design)
    assert "product geometry is an envelope/representation set" in rendered
    assert "Automotive" not in rendered


def test_mass_properties_record_is_complete_but_cannot_claim_unmeasured_evidence() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    template = mass_properties_record_template(product_mass_closure_payload(design))
    assert template["template_status"] == "unfilled-not-evidence"
    assert template["evidence_package_id"] == "EVD-MASS-001"
    assert len(template["product_rows"]) == 120
    assert sum(row["active_in_reference_configuration"] for row in template["product_rows"]) == 117
    assert all(row["unit_mass_kg"] is None for row in template["product_rows"])
    assert all(row["installed_total_mass_kg"] is None for row in template["product_rows"])
    assert len(template["category_reconciliation"]) == 9
    assert len(template["individual_car_results"]) == 3
    assert all(len(car["axle_loads"]) == 4 for car in template["individual_car_results"])
    assert [row["load_case"] for row in template["complete_trainset_results"]["load_case_results"]] == [
        "AW0",
        "AW2",
        "AW3",
    ]
    assert all(
        len(row["axle_loads_kg"]) == 12
        for row in template["complete_trainset_results"]["load_case_results"]
    )
    assert template["complete_trainset_results"]["tare_mass_kg"] is None
    assert "cannot reduce the 78,750 kg" in template["closure_warning"]


def test_trainset_build_cost_uses_explicit_labor_and_unexpected_premium() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    payload = trainset_build_cost_payload(design)
    assert payload["direct_material_and_supplier_cost_usd"] == 682_431.18
    assert payload["labor_hours"] == 5_524.0
    assert payload["labor_rate_usd_per_hour"] == 10.0
    assert payload["labor_cost_usd"] == 55_240.0
    assert payload["unexpected_cost_premium_fraction"] == 0.20
    assert payload["unexpected_cost_premium_usd"] == 147_534.24
    assert payload["total_build_cost_usd"] == 885_205.42
    assert payload["rounded_local_owner_unit_usd"] == 900_000
    assert payload["included_fitout_doors_glazing_total_base_usd"] == 146_750.0
    included_scopes = {
        row["scope"] for row in payload["included_fitout_doors_glazing_scope"]  # type: ignore[index]
    }
    assert "seats, floors, grab rails, and interior lighting" in included_scopes
    assert "roof HVAC" in included_scopes
    rendered = render_trainset_build_cost(design)
    assert "$885,205" in rendered
    assert "5,524 h at $10/h" in rendered
    assert "20%" in rendered
    assert "$17,500" in rendered
    assert "$112,000" in rendered


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
    small_rows = {
        row["child_id"]: row
        for row in rows
        if row["child_id"] in {"LM3-FIX-P020", "LM3-LGT-P010", "LM3-WIN-P010", "LM3-DOOR-P010"}
    }
    assert "service-rail-captive-fastener" in small_rows["LM3-FIX-P020"]["join_classes"]
    assert "service-rail-captive-fastener" in small_rows["LM3-LGT-P010"]["join_classes"]
    assert "cassette-floating-fastener" in small_rows["LM3-WIN-P010"]["join_classes"]
    assert "cassette-floating-fastener" in small_rows["LM3-DOOR-P010"]["join_classes"]
    assert "bolted-structural-datum" not in small_rows["LM3-LGT-P010"]["join_classes"]


def test_write_outputs_emits_mass_and_joint_control_records(tmp_path) -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    write_outputs(design, tmp_path)
    assert (tmp_path / "mass-budget.json").exists()
    assert (tmp_path / "mass-budget.md").exists()
    assert (tmp_path / "mass-closure-ledger.json").exists()
    assert (tmp_path / "mass-closure-ledger.md").exists()
    assert (tmp_path / "evidence/mass-properties-record-template.json").exists()
    assert (tmp_path / "evidence/factory-release-record-template.json").exists()
    assert (tmp_path / "factory-release-readiness.md").exists()
    drawing_index = json.loads((tmp_path / "factory-drawings/index.json").read_text())
    assert drawing_index["drawing_count"] == 29
    assert drawing_index["controlled_product_count"] == 80
    assert len(list((tmp_path / "factory-drawings").glob("LM3-*.json"))) == 29
    assert len(list((tmp_path / "factory-drawings").glob("LM3-*.md"))) == 29
    assert (tmp_path / "trainset-build-cost.json").exists()
    assert (tmp_path / "trainset-build-cost.md").exists()
    assert (tmp_path / "joint-control-schedule.json").exists()
    assert (tmp_path / "joint-control-schedule.md").exists()
    assert (tmp_path / "critical-path.json").exists()
    assert (tmp_path / "critical-path.md").exists()
    assert (tmp_path / "factory-plan.json").exists()
    assert (tmp_path / "factory-plan.md").exists()
    assert (tmp_path / "train-end-interface.json").exists()
    assert (tmp_path / "train-end-interface.md").exists()
    assert (tmp_path / "small-component-standard.json").exists()
    assert (tmp_path / "small-component-standard.md").exists()
    standard = render_small_component_standard()
    assert "OSR-RAIL-42" in standard
    assert "Four fastener families" in standard
    assert "Twenty-two" not in standard
    assert "Main modules per car: `22`" in standard


def test_train_end_interface_models_panorama_or_open_mid_option() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    payload = train_end_interface_payload(design)
    options = {option["id"]: option for option in payload["options"]}  # type: ignore[index]
    assert payload["common_interface"]["assembly_id"] == "LM3-EIF-SA650"  # type: ignore[index]
    assert options["panoramic-glass-front-end"]["reference_quantity"] == 2
    assert options["mid-open-train-to-train-connection"]["reference_quantity"] == 0
    assert "LM3-TTART-SA850" == options["mid-open-train-to-train-connection"]["assembly_id"]
    rendered = render_train_end_interface(design)
    assert "panoramic glass front/end" in rendered
    assert "mid-train open connection" in rendered
    assert "Each end position must select one option only" in rendered


def test_train_end_options_are_exclusive_and_default_to_three_car_panorama() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    end_payload = train_end_interface_payload(design)
    options = {option["id"]: option for option in end_payload["options"]}  # type: ignore[index]
    common = end_payload["common_interface"]  # type: ignore[index]

    assert common["owned_item_ids"] == ["LM3-END-P060", "LM3-END-P061", "LM3-END-P062"]
    assert options["panoramic-glass-front-end"]["assembly_id"] == "LM3-END-SA700"
    assert options["mid-open-train-to-train-connection"]["assembly_id"] == "LM3-TTART-SA850"
    assert options["panoramic-glass-front-end"]["reference_quantity"] == 2
    assert options["mid-open-train-to-train-connection"]["reference_quantity"] == 0
    assert not set(options["panoramic-glass-front-end"]["uses"]) & set(
        options["mid-open-train-to-train-connection"]["uses"]
    )
    assert "panoramic glass" in options["mid-open-train-to-train-connection"]["omits"]
    assert "open passenger portal" in options["panoramic-glass-front-end"]["omits"]

    assemblies = {node.id: node for node in design.assemblies}
    trainset = assemblies["LM3-TRAINSET-A000"]
    assert "LM3-END-SA700" in trainset.children
    assert "LM3-TTART-SA850" in assemblies
    assert "LM3-TTART-SA850" not in trainset.children


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


def test_factory_plan_sizes_cells_machinery_and_parallel_assembly_times() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    payload = factory_plan_payload(design)
    size = payload["factory_size"]  # type: ignore[index]
    machinery_cost = payload["machinery_cost"]  # type: ignore[index]
    rollups = {row["id"]: row for row in payload["assembly_time_rollups"]}  # type: ignore[index]
    cells = {row["name"]: row for row in payload["process_cells"]}  # type: ignore[index]

    assert size["recommended_enclosed_factory_area_m2"] == 3515
    assert size["outside_yard_and_test_apron_m2"] == 2200
    assert cells["final assembly, bogie marriage, and static-test track"]["net_area_m2"] == 600
    assert rollups["chassis and painted carbody frame fabrication"]["elapsed_window_days"] == 13.0
    assert rollups["bogie build and bogie-to-carbody integration"]["touch_labor_hours"] == 760.0
    assert rollups["GFRP moulding and clip-on body installation"]["early_start_day"] == 2.0
    assert machinery_cost["rough_order_machinery_total_usd"] == 1021200
    rendered = render_factory_plan(design)
    assert "LM3 pilot factory sizing" in rendered
    assert "CNC press brake" in rendered
    assert "$1,021,200" in rendered


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
