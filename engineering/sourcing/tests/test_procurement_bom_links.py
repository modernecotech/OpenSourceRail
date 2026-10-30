from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

from engineering.sourcing.catalogue import load_catalogue
from engineering.sourcing.model import identity, record
import pytest
from engineering.sourcing.procurement_bom import (
    _DOMESTIC_LEAD_RULES,
    _attach_domestic_aluminium_sensitivities,
    _attach_imported_copper_sensitivities,
    _attach_concrete_material_input_takeoff,
    _link_unlocated_obligations,
    _material_purchasing_rollup,
)

ROOT = Path(__file__).resolve().parents[3]


def _package(family, key):
    return {"package_family": family, "package_key": key,
            "package_id": identity({"family": family, "key": key})}


def test_unlocated_obligations_link_to_related_scopes_without_becoming_package_content():
    packages = [
        _package("vehicle-body-stock-kit", "car/0"),
        _package("vehicle-bogie-stock-package", "car/0/bogie/0"),
        _package("vehicle-bogie-stock-package", "car/0/bogie/1"),
        _package("vehicle-secondary-stock-kit", "car/0/station-secondary"),
        _package("civil-rail-stock-pair", "span/0"),
        _package("civil-concrete-stock-package", "span/0"),
        _package("wayside-lim-primary-material-set", "bank/0"),
    ]
    obligations = [
        "car/0/weld-interface/abc123",
        "car/0/passive-bogie-pair/residual",
        "car/0/passive-secondary/residual",
        "car/0/retained-comfort/HVAC/residual",
        "span/0/direct_fastener_kg",
        "span/0/reinforcement_kg",
        "bank/0/cooling-and-services",
        "infrastructure/foundations-ground-site",
    ]

    result = _link_unlocated_obligations(obligations, packages)
    links = {row["scope_key"]: row for row in result["links"]}

    assert result["source_obligation_count"] == 8
    assert result["linked_unique_obligation_count"] == 7
    assert result["unlinked_obligation_count"] == 1
    assert result["unlinked_obligation_ids"] == ["infrastructure/foundations-ground-site"]
    assert links["car/0/passive-bogie-pair"]["related_package_ids"] == sorted(
        row["package_id"] for row in packages
        if row["package_family"] == "vehicle-bogie-stock-package")
    assert links["span/0/track-fastening"]["related_package_ids"] == [
        next(row["package_id"] for row in packages if row["package_family"] == "civil-rail-stock-pair")]
    assert links["span/0/precast-reinforcement-and-prestress"]["related_package_ids"] == [
        next(row["package_id"] for row in packages if row["package_family"] == "civil-concrete-stock-package")]
    assert links["bank/0/cooling-and-services"]["related_package_ids"] == [
        next(row["package_id"] for row in packages if row["package_family"] == "wayside-lim-primary-material-set")]
    assert all(row["association_is_package_membership"] is False for row in links.values())
    assert all(row["allocated_to_package_mass_or_quantity"] is False for row in links.values())
    assert result["links_are_non_additive"] is True


def test_material_purchase_demand_lines_use_physical_units_and_retain_occurrences():
    aluminum_group_ids = ["a" * 64, "b" * 64]
    concrete_group_id = "c" * 64
    occurrence_rows = [
        {"id": "car/0/body/aluminum/0", "system": "vehicle/body",
         "material": "aluminium_reference", "scope": "nominal-stock",
         "accounted_mass_kg": "6", "nominal_stock_volume_m3": "0.002"},
        {"id": "car/0/body/aluminum/1", "system": "vehicle/body",
         "material": "aluminium_reference", "scope": "nominal-stock",
         "accounted_mass_kg": "4", "nominal_stock_volume_m3": "0.001"},
        {"id": "span/0/concrete/0", "system": "civil/concrete",
         "material": "concrete-hypothesis", "scope": "nominal-stock",
         "accounted_mass_kg": "1200", "nominal_stock_volume_m3": "0.5"},
    ]
    groups = [
        {"group_id": aluminum_group_ids[0], "engineering_occurrence_ids": [occurrence_rows[0]["id"]],
         "known_gross_stock_mass_kg": "6", "labour_h": None},
        {"group_id": aluminum_group_ids[1], "engineering_occurrence_ids": [occurrence_rows[1]["id"]],
         "known_gross_stock_mass_kg": "4", "labour_h": None},
        {"group_id": concrete_group_id, "engineering_occurrence_ids": [occurrence_rows[2]["id"]],
         "known_gross_stock_mass_kg": "1200", "labour_h": None},
    ]
    body_package = {
        "package_id": "1" * 64, "manufacturing_group_ids": aluminum_group_ids,
        "engineering_occurrence_ids": [row["id"] for row in occurrence_rows[:2]],
        "procurement_task_ids": ["p1", "p2"], "manufacturing_operation_ids": ["m1", "m2"],
        "domestic_cost_estimate_scenarios": [],
    }
    concrete_package = {
        "package_id": "2" * 64, "manufacturing_group_ids": [concrete_group_id],
        "engineering_occurrence_ids": [occurrence_rows[2]["id"]],
        "procurement_task_ids": ["p3"], "manufacturing_operation_ids": ["m3"],
        "domestic_cost_estimate_scenarios": [{
            "labour_hours_per_nominal_m3": "4", "direct_material_cost": "100",
            "direct_labor_cost": "50", "uplift_amount": "30",
            "estimated_total_iqd": "180", "nominal_stock_volume_m3": "0.5",
            "source_estimate_packet_id": "d" * 64, "source_process_record_id": "e" * 64,
            "basis": "declared concrete recipe and 4 assumed labour h/m3; material + labour + 20%",
        }],
    }
    task_by_group = {row["group_id"]: {"id": "task-" + row["group_id"]} for row in groups}
    ops_by_group = {row["group_id"]: [{"id": "op-" + row["group_id"]}] for row in groups}
    links = {"links_are_non_additive": True, "links": [{
        "link_id": "f" * 64, "related_package_ids": [body_package["package_id"]],
    }]}
    aluminum_source = record(
        "source", source_key="iraq.asia-aluminium", publisher="Local aluminium lead",
        url="https://example.com/aluminium", retrieved_at="2026-10-30",
        access="Lead only; alloy, temper, price and compatibility unverified",
        source_kind="factory_catalogue")

    rows = _material_purchasing_rollup(
        [body_package, concrete_package], occurrence_rows, groups,
        task_by_group, ops_by_group, links,
        {"iraq.asia-aluminium": aluminum_source})
    by_material = {row["material"]: row for row in rows}

    aluminum = by_material["aluminium_reference"]
    assert aluminum["request_unit"] == "kg"
    assert aluminum["modeled_material_demand"] == "10"
    assert aluminum["engineering_group_count"] == 2
    assert aluminum["engineering_occurrence_ids"] == [row["id"] for row in occurrence_rows[:2]]
    assert aluminum["context_only_unlocated_link_count"] == 1
    assert aluminum["commercial_order_quantity"] is None
    assert aluminum["purchase_yield_fraction"] is None
    assert aluminum["complete_installed_cost"] is None
    lead, = aluminum["domestic_fabrication_lead_sources"]
    assert lead["source_id"] == aluminum_source["record_id"]
    assert lead["technical_compatibility"] is None
    assert lead["price_recorded"] is False
    assert aluminum["domestic_fabrication_leads_are_supplier_matches"] is False

    concrete = by_material["concrete-hypothesis"]
    assert concrete["request_unit"] == "m3"
    assert concrete["modeled_material_demand"] == "0.5"
    scenario, = concrete["domestic_fabrication_estimate_scenarios"]
    assert scenario["estimated_total_iqd"] == "180"
    assert scenario["estimated_unit_cost_iqd_per_nominal_m3"] == "360"
    assert scenario["supplier_quote"] is False
    assert scenario["complete_process_cost"] is None
    assert set(concrete["engineering_occurrence_ids"]) == {occurrence_rows[2]["id"]}


def test_additional_iraqi_fabrication_leads_are_linked_only_to_relevant_stock_families():
    concrete = _DOMESTIC_LEAD_RULES[("civil/concrete", "concrete-hypothesis")]
    body = _DOMESTIC_LEAD_RULES[("vehicle/body", "gfrp_skin_research")]
    bogie = _DOMESTIC_LEAD_RULES[("vehicle/passive-bogie-pair", "steel-reference")]

    assert "iraq.al-burhan-sleeper-factory" in concrete
    assert "iraq.karbala-precast-bridge-beams" in concrete
    assert "iraq.ncpi-chemical-plastic-industries" in body
    assert "iraq.scosi.foundry-forging" in bogie
    assert "iraq.al-qader-steel-supply" in bogie
    assert "compatibility unassessed" in concrete["iraq.karbala-precast-bridge-beams"]
    assert "qualification unassessed" in body["iraq.ncpi-chemical-plastic-industries"]
    assert "fatigue" in bogie["iraq.scosi.foundry-forging"]


def test_concrete_recipe_takeoff_is_exact_candidate_linked_and_non_purchasable():
    recipe_path = ROOT / "docs/design-engine/sourcing/domestic-fabrication/takeoff-recipes/concrete-material-inputs-2026-09.json"
    recipe = json.loads(recipe_path.read_text())
    records = load_catalogue()
    benchmarks = [row for row in records if row["kind"] == "benchmark"]
    sources = [row for row in records if row["kind"] == "source"]
    package = {
        "package_id": "f" * 64,
        "package_family": "civil-concrete-stock-package",
        "package_key": "span/0",
        "manufacturing_group_ids": ["a" * 64],
        "engineering_occurrence_ids": ["span/0/concrete/0", "span/0/concrete/1"],
        "nominal_stock_volume_m3": "1",
        "domestic_cost_estimate_scenarios": [
            {"direct_material_cost": "75900", "labour_hours_per_nominal_m3": "2"},
            {"direct_material_cost": "75900", "labour_hours_per_nominal_m3": "8"},
        ],
    }
    result = _attach_concrete_material_input_takeoff(
        [package], recipe, sha256(recipe_path.read_bytes()).hexdigest(),
        benchmarks, sources, recipe["candidate_id"], recipe["input_id"])

    assert result["package_count"] == 1
    assert result["manufacturing_group_count"] == 1
    assert result["engineering_occurrence_count"] == 2
    assert result["ingredient_line_count"] == 3
    assert [row["total_recipe_input_quantity"] for row in result["material_inputs"]] == ["0.35", "0.5", "0.8"]
    assert [row["material_extension_iqd"] for row in result["material_inputs"]] == ["46200", "10500", "19200"]
    assert result["non_additive_to_output_concrete_stock"] is True
    assert result["commercial_order_quantities_known"] is False
    assert result["complete_installed_cost"] is None
    attached = package["manufacturing_input_takeoff"]
    assert attached["material_cost_reconciles_to_existing_cost_scenarios"] is True
    assert all(row["commercial_order_quantity"] is None
               and row["purchase_yield_fraction"] is None
               and row["product_compatibility"] is None
               and row["supplier_product_match"] is False
               for row in attached["material_inputs"])
    assert package["package_id"] != "f" * 64
    assert package["package_id"] == identity({key: value for key, value in package.items() if key != "package_id"})


def test_concrete_recipe_rejects_mixed_candidate_and_recipe_benchmark():
    recipe_path = ROOT / "docs/design-engine/sourcing/domestic-fabrication/takeoff-recipes/concrete-material-inputs-2026-09.json"
    recipe = json.loads(recipe_path.read_text())
    records = load_catalogue()
    benchmarks = [row for row in records if row["kind"] == "benchmark"]
    sources = [row for row in records if row["kind"] == "source"]
    with pytest.raises(ValueError, match="candidate-bound illustrative concrete material recipe"):
        _attach_concrete_material_input_takeoff([], {**recipe, "candidate_id": "0" * 64},
            "a" * 64, benchmarks, sources, recipe["candidate_id"], recipe["input_id"])


def test_aluminium_raw_stock_sensitivities_attach_to_exact_candidate_material_lines():
    candidate_id, input_id, takeoff_id = "a" * 64, "b" * 64, "c" * 64
    forms = [
        "Non-oxidized aluminium profiles", "Oxidized aluminium profiles",
        "Spray-painted aluminium profiles", "Hard aluminium sheet, 0.6–0.9 mm",
        "Hard aluminium sheet, 1 mm and above", "Annealed aluminium sheet, 0.6–0.9 mm",
        "Annealed aluminium sheet, 1 mm and above",
    ]
    scopes = [
        ("vehicle/body", "aluminium_reference", "nominal-stock", "10", 2, 3),
        ("vehicle/passive-secondary", "6082-T6-proposed", "nominal-stock", "4", 1, 2),
    ]
    rows = []
    for system, material, stock_scope, mass_kg, group_count, occurrence_count in scopes:
        for form in forms:
            for hours in ("8", "16", "32"):
                selector = {"system": system, "material": material, "stock_scope": stock_scope}
                process = record(
                    "process", candidate_id=candidate_id, input_id=input_id,
                    candidate_takeoff_id=takeoff_id, candidate_takeoff_scope=selector,
                    candidate_takeoff_group_count=group_count,
                    candidate_takeoff_occurrence_count=occurrence_count,
                    candidate_takeoff_gross_mass_kg=mass_kg,
                    candidate_takeoff_mass_reconciliation_residual_kg="0",
                    candidate_takeoff_mapped=True, candidate_takeoff_quantity_basis="gross stock mass",
                    output_quantity=str(Decimal(mass_kg) / Decimal(1000)), output_unit="t",
                    material_lines=[], labour_lines=[], direct_material_cost="100",
                    direct_labor_cost="50", uplift_fraction="0.2", uplift_amount="30",
                    estimated_total="180", estimated_unit_cost="1800",
                    complete_process_cost=None, complete_installed_cost=None,
                    whole_life_cost=None, unknown_is_zero=False)
                rows.append({"material": material, "material_form": form,
                             "family": "aluminium profile" if "profile" in form else "aluminium sheet",
                             "labour_hours_per_stock_tonne": hours,
                             "input_gross_stock_mass_kg": mass_kg,
                             "input_stock_tonnes": process["output_quantity"],
                             "estimated_total_iqd": "180",
                             "estimated_unit_cost_iqd_per_tonne": "1800", "process": process})
    reference = {"candidate_id": candidate_id, "source_input_id": input_id,
                 "takeoff_id": takeoff_id, "packet_id": "d" * 64,
                 "candidate_mapped_aluminium_stock_scenarios": rows}
    material_lines = [{"system": system, "material": material, "stock_scope": stock_scope,
                       "modeled_gross_stock_mass_kg": mass_kg,
                       "engineering_group_count": group_count,
                       "engineering_occurrence_count": occurrence_count,
                       "material_line_id": "e" * 64}
                      for system, material, stock_scope, mass_kg, group_count, occurrence_count in scopes]

    line_count, scenario_count = _attach_domestic_aluminium_sensitivities(
        material_lines, reference, candidate_id, input_id)

    assert (line_count, scenario_count) == (2, 42)
    assert [row["domestic_raw_stock_sensitivity_count"] for row in material_lines] == [21, 21]
    assert all(len(row["domestic_raw_stock_sensitivity_scenarios"]) == 21 for row in material_lines)
    assert all(row["domestic_raw_stock_sensitivities_are_compatible_quotes"] is False
               for row in material_lines)
    assert all(row["material_line_id"] == identity(
        {key: value for key, value in row.items() if key != "material_line_id"})
        for row in material_lines)


def test_imported_copper_sensitivity_is_candidate_bound_and_formula_reconciles():
    candidate_id, input_id = "a" * 64, "b" * 64
    records = [row for row in load_catalogue()
               if row.get("benchmark_key") in {
                   "cso-import-2025:hs74081100:iqd-per-kg",
                   "iq-cso-2026-09:baghdad:wage:skilled:hour-8h-day",
               }]
    line = {
        "system": "wayside/primary", "material": "copper-conductor",
        "stock_scope": "equivalent-volume-stock", "request_unit": "kg",
        "modeled_gross_stock_mass_kg": "9354.240000000002",
        "engineering_group_count": 5, "engineering_group_ids": [str(i) for i in range(5)],
        "engineering_occurrence_count": 10, "engineering_occurrence_ids": [str(i) for i in range(10)],
        "related_package_ids": [str(i) for i in range(5)],
        "missing_gross_mass_group_count": 0, "missing_member_mass_group_count": 0,
        "missing_demand_group_count": 0, "material_line_id": "c" * 64,
    }

    line_count, scenario_count = _attach_imported_copper_sensitivities(
        [line], records, candidate_id, input_id)

    assert (line_count, scenario_count) == (1, 3)
    assert line["copper_imported_raw_stock_sensitivity_count"] == 3
    assert line["copper_sensitivity_is_compatible_quote"] is False
    assert line["material_line_id"] == identity(
        {key: value for key, value in line.items() if key != "material_line_id"})
    takeoff_id = line["copper_imported_raw_stock_sensitivity_takeoff_id"]
    scenarios = line["copper_imported_raw_stock_sensitivity_scenarios"]
    assert [row["labour_hours_per_gross_stock_tonne"] for row in scenarios] == [8, 16, 32]
    for row in scenarios:
        assert row["candidate_id"] == candidate_id
        assert row["source_input_id"] == input_id
        assert row["candidate_takeoff_id"] == takeoff_id
        assert row["engineering_group_count"] == 5
        assert row["engineering_occurrence_count"] == 10
        assert row["candidate_bom_price"] is False
        assert row["supplier_quote"] is False
        assert row["compatible_product_match"] is False
        assert row["commercial_order_quantity"] is None
        assert row["purchase_yield_fraction"] is None
        assert row["complete_process_cost"] is None
        assert row["complete_installed_cost"] is None
        assert row["unknown_is_zero"] is False
        direct = Decimal(row["direct_material_cost_iqd"]) + Decimal(row["direct_labour_cost_iqd"])
        assert Decimal(row["estimated_total_iqd"]) == (direct * Decimal("1.20")).quantize(Decimal("0.01"))
        assert row["scenario_id"] == identity(
            {key: value for key, value in row.items() if key != "scenario_id"})


def test_imported_copper_sensitivity_rejects_wrong_source_and_incomplete_takeoff():
    candidate_id, input_id = "a" * 64, "b" * 64
    records = [row for row in load_catalogue()
               if row.get("benchmark_key") in {
                   "cso-import-2025:hs74081100:iqd-per-kg",
                   "iq-cso-2026-09:baghdad:wage:skilled:hour-8h-day",
               }]
    line = {
        "system": "wayside/primary", "material": "copper-conductor",
        "stock_scope": "equivalent-volume-stock", "request_unit": "kg",
        "modeled_gross_stock_mass_kg": "10", "engineering_group_count": 1,
        "engineering_group_ids": ["g"], "engineering_occurrence_count": 1,
        "engineering_occurrence_ids": ["o"], "related_package_ids": ["p"],
        "missing_gross_mass_group_count": 0, "missing_member_mass_group_count": 0,
        "missing_demand_group_count": 0, "material_line_id": "c" * 64,
    }
    bad_records = [dict(row) for row in records]
    copper = next(row for row in bad_records if row.get("benchmark_key", "").startswith("cso-import"))
    copper["source_id"] = "d" * 64
    copper["record_id"] = identity({key: value for key, value in copper.items() if key != "record_id"})
    with pytest.raises(ValueError, match="benchmark scope or source"):
        _attach_imported_copper_sensitivities([line], bad_records, candidate_id, input_id)
    line["missing_member_mass_group_count"] = 1
    with pytest.raises(ValueError, match="exact, fully quantified members"):
        _attach_imported_copper_sensitivities([line], records, candidate_id, input_id)
