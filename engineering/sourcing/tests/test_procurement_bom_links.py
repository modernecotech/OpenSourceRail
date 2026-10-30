from engineering.sourcing.model import identity, record
from engineering.sourcing.procurement_bom import (
    _link_unlocated_obligations,
    _material_purchasing_rollup,
)


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
