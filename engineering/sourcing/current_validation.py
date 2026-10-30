"""Index current sourcing evidence without editing source-bound historical packets."""
import gzip
import hashlib
import json
from pathlib import Path
from decimal import Decimal

from .catalogue import load_catalogue
from .model import identity
from .iraq_logistics_scenarios import SEED as LOGISTICS_SEED
from .iraq_local_gfrp_cost_scenarios import LABOUR_SEED as HISTORICAL_LABOUR_SEED
from .iraq_local_gfrp_cost_scenarios import LOCAL_SEED as LOCAL_COMPOSITE_SEED


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/design-engine/sourcing/validation-current.json"
FRAME = "docs/design-engine/sourcing/packets/frame-vehicle-iraq-domestic-sources-v13"
FEDERATION = "docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v13"
LAMINATES = "docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v18"
REGIONAL = "docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json"
GFRP = "docs/design-engine/sourcing/domestic-fabrication/estimates/current/gfrp-laminate-local-2026-v19.json"
IMPORT_SCREEN = "docs/design-engine/sourcing/domestic-fabrication/cso-imported-aluminium-fabrication-sensitivity-2025-2026.json"
PROCUREMENT = "docs/design-engine/sourcing/procurement-bom/federated-v06-research-packages-v17.json.gz"
CONCRETE_RECIPE = "docs/design-engine/sourcing/domestic-fabrication/takeoff-recipes/concrete-material-inputs-2026-09.json"
LOGISTICS = "docs/design-engine/sourcing/domestic-fabrication/logistics-2026-september-v2/iraq-span-logistics-sensitivity.json"
LOGISTICS_MANIFEST = "docs/design-engine/sourcing/domestic-fabrication/logistics-2026-september-v2/manifest.json"
LOCAL_GFRP = "docs/design-engine/sourcing/domestic-fabrication/iraq-local-gfrp-retail-screen-2026-10-v1/iraq-local-gfrp-retail-screen.json"
LOCAL_GFRP_MANIFEST = "docs/design-engine/sourcing/domestic-fabrication/iraq-local-gfrp-retail-screen-2026-10-v1/manifest.json"
ADDITIONAL_MATERIAL_SOURCES = "engineering/sourcing/data/iraq-domestic-material-leads-2026-10.json"


def read_json(path):
    return json.loads((ROOT / path).read_text())


def read_gzip_json(path):
    with gzip.open(ROOT / path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def packet(path):
    summary = read_json(path + "/summary.json")
    manifest = read_json(path + "/manifest.json")
    return summary, manifest


def build_validation():
    records = load_catalogue()
    epoch_id = identity(records)
    sources = {row["source_key"]: row for row in records if row["kind"] == "source"}
    benchmarks = {row["benchmark_key"]: row for row in records if row["kind"] == "benchmark"}
    additional_material_records = load_catalogue([ROOT / ADDITIONAL_MATERIAL_SOURCES])
    additional_material_sources = {row["source_key"]: row for row in additional_material_records
                                   if row["kind"] == "source"}

    frame, frame_manifest = packet(FRAME)
    federation, federation_manifest = packet(FEDERATION)
    laminate_rows = []
    for recipe in ("solid-600gsm", "sandwich-600gsm", "higher-fibre-sandwich-600gsm"):
        path = f"{LAMINATES}/{recipe}"
        study = read_json(path + "/summary.json")
        manifest = read_json(path + "/manifest.json")
        with gzip.open(ROOT / path / "catalogue.json.gz", "rt", encoding="utf-8") as handle:
            catalogue = json.load(handle)
        result = study["summary"]
        laminate_rows.append({
            "recipe": recipe,
            "path": path + "/summary.json",
            "publication_id": manifest["publication_id"],
            "run_id": study["run_id"],
            "candidate_id": study["candidate_id"],
            "summary_id": study["summary_id"],
            "requirement_count": result["requirement_count"],
            "priced": result["priced_requirement_count"],
            "listed_extension_GBP": result["known_listed_extension_subtotal"],
            "compatible_matches": result["compatible_matches"],
            "held_price_observations": result["held_price_observations"],
            "unknown_quantity_requirements": result["unknown_quantity_requirements"],
            "catalogue_record_count": len(catalogue),
        })

    regional = read_json(REGIONAL)
    gfrp = read_json(GFRP)
    import_screen = read_json(IMPORT_SCREEN)
    procurement = read_gzip_json(PROCUREMENT)
    concrete_recipe = read_json(CONCRETE_RECIPE)
    concrete_source_recipe_path = concrete_recipe.get("source_recipe_path")
    concrete_source_recipe = read_json(concrete_source_recipe_path)
    concrete_takeoff = procurement.get("concrete_material_input_takeoff")
    concrete_packages = [row for row in procurement.get("packages", [])
                         if row.get("package_family") == "civil-concrete-stock-package"]
    expected_occurrences = sorted(occurrence_id for row in concrete_packages
                                  for occurrence_id in row.get("engineering_occurrence_ids", []))
    expected_groups = sorted(group_id for row in concrete_packages
                             for group_id in row.get("manufacturing_group_ids", []))
    benchmark_by_id = {row["record_id"]: row for row in records if row["kind"] == "benchmark"}
    if (procurement.get("packet_id") != identity({key: value for key, value in procurement.items()
                                                   if key != "packet_id"})
            or not isinstance(concrete_takeoff, dict)
            or concrete_takeoff.get("takeoff_id") != identity({key: value for key, value in concrete_takeoff.items()
                                                                if key != "takeoff_id"})
            or concrete_takeoff.get("recipe_id") != identity(concrete_recipe)
            or concrete_takeoff.get("recipe_file_sha256") != hashlib.sha256((ROOT / CONCRETE_RECIPE).read_bytes()).hexdigest()
            or concrete_takeoff.get("source_recipe_id") != identity({key: value for key, value in concrete_source_recipe.items()
                                                                        if key != "recipe_id"})
            or concrete_takeoff.get("source_recipe_sha256") != hashlib.sha256((ROOT / concrete_source_recipe_path).read_bytes()).hexdigest()
            or concrete_takeoff.get("candidate_id") != procurement.get("candidate_id")
            or concrete_takeoff.get("source_input_id") != procurement.get("source_input_id")
            or concrete_takeoff.get("source_recipe_id") != concrete_recipe.get("source_recipe_id")
            or concrete_takeoff.get("source_recipe_sha256") != concrete_recipe.get("source_recipe_sha256")
            or concrete_takeoff.get("package_count") != 81
            or concrete_takeoff.get("manufacturing_group_count") != 81
            or concrete_takeoff.get("engineering_occurrence_count") != 486
            or concrete_takeoff.get("ingredient_line_count") != 243
            or concrete_takeoff.get("covered_package_ids") != sorted(row["package_id"] for row in concrete_packages)
            or concrete_takeoff.get("covered_manufacturing_group_ids") != expected_groups
            or concrete_takeoff.get("covered_engineering_occurrence_ids") != expected_occurrences
            or set(expected_occurrences) & set(procurement.get("unlocated_obligation_ids", []))
            or concrete_takeoff.get("mix_design_approved") is not False
            or concrete_takeoff.get("conversion_yield_fraction") is not None
            or concrete_takeoff.get("commercial_order_quantities_known") is not False
            or concrete_takeoff.get("complete_process_cost") is not None
            or concrete_takeoff.get("complete_installed_cost") is not None
            or concrete_takeoff.get("physical_qualification") is not None
            or concrete_takeoff.get("unknown_is_zero") is not False
            or concrete_takeoff.get("non_additive_to_output_concrete_stock") is not True
            or procurement.get("located_stock_occurrence_count") != 27216
            or procurement.get("unlocated_obligation_count") != 4773
            or procurement.get("draft_package_count") != 191
            or procurement.get("priced_draft_packages") != 0):
        raise ValueError("Current concrete material-input takeoff is not bound to the exact span groups or open purchasing scope")
    source_evidence_hashes = procurement.get("source_sha256", {}).get("domestic_cost_evidence", {})
    if (source_evidence_hashes.get(CONCRETE_RECIPE) != hashlib.sha256((ROOT / CONCRETE_RECIPE).read_bytes()).hexdigest()
            or source_evidence_hashes.get(concrete_source_recipe_path)
            != hashlib.sha256((ROOT / concrete_source_recipe_path).read_bytes()).hexdigest()
            or source_evidence_hashes.get(ADDITIONAL_MATERIAL_SOURCES)
            != hashlib.sha256((ROOT / ADDITIONAL_MATERIAL_SOURCES).read_bytes()).hexdigest()):
        raise ValueError("Procurement takeoff omits exact concrete recipe source hashes")
    expected_source_registry = [row for row in records if row["kind"] == "source"] + list(additional_material_sources.values())
    if (procurement.get("source_registry_record_count") != len(expected_source_registry)
            or procurement.get("source_registry_record_set_id")
            != identity(sorted(expected_source_registry, key=lambda row: row["record_id"]))):
        raise ValueError("Procurement source registry differs from the current catalogue and supplemental Iraqi source set")
    if (abs(Decimal(concrete_takeoff["nominal_output_volume_m3"]) - Decimal("1804.8096")) > Decimal("0.00000001")
            or len(concrete_takeoff.get("material_inputs", [])) != len(concrete_recipe.get("material_inputs", []))):
        raise ValueError("Concrete material-input recipe volume or line count differs")
    expected_materials = {row["benchmark_id"]: row for row in concrete_recipe["material_inputs"]}
    for line in concrete_takeoff["material_inputs"]:
        recipe_line = expected_materials.get(line.get("benchmark_id"))
        benchmark = benchmark_by_id.get(line.get("benchmark_id"))
        if (recipe_line is None or benchmark is None
                or line.get("benchmark_key") != recipe_line.get("benchmark_key")
                or line.get("quantity_unit") != recipe_line.get("quantity_unit")
                or line.get("quantity_unit") != benchmark.get("quantity_unit")
                or line.get("benchmark_source_id") != benchmark.get("source_id")
                or Decimal(line.get("benchmark_unit_rate_iqd")) != Decimal(benchmark.get("unit_price"))
                or abs(Decimal(line.get("total_recipe_input_quantity"))
                       - Decimal(recipe_line["quantity"]) * Decimal(concrete_takeoff["nominal_output_volume_m3"])) > Decimal("0.00000001")
                or abs(Decimal(line.get("material_extension_iqd"))
                       - Decimal(line["total_recipe_input_quantity"]) * Decimal(line["benchmark_unit_rate_iqd"])) > Decimal("0.000001")
                or line.get("commercial_order_quantity") is not None
                or line.get("purchase_yield_fraction") is not None
                or line.get("supplier_product_match") is not False):
            raise ValueError("Concrete material-input line differs from its source recipe or benchmark")
    if any(row.get("package_id") != identity({key: value for key, value in row.items() if key != "package_id"})
           for row in procurement.get("packages", [])):
        raise ValueError("Procurement package identity differs after the concrete input takeoff")
    for row in concrete_packages:
        takeoff = row.get("manufacturing_input_takeoff")
        if (not isinstance(takeoff, dict)
                or takeoff.get("takeoff_id") != identity({key: value for key, value in takeoff.items()
                                                           if key != "takeoff_id"})
                or takeoff.get("candidate_id") != procurement.get("candidate_id")
                or takeoff.get("source_input_id") != procurement.get("source_input_id")
                or takeoff.get("manufacturing_group_ids") != row.get("manufacturing_group_ids")
                or takeoff.get("engineering_occurrence_ids") != row.get("engineering_occurrence_ids")
                or takeoff.get("non_additive_to_output_concrete_stock") is not True
                or len(takeoff.get("material_inputs", [])) != 3
                or takeoff.get("commercial_order_quantities_known") is not False
                or takeoff.get("complete_installed_cost") is not None):
            raise ValueError("Concrete span material takeoff lost package or source occurrence identity")
        if ({str(item.get("labour_hours_per_nominal_m3")) for item in row["domestic_cost_estimate_scenarios"]}
                != {"2", "4", "8"}
                or {item.get("region") for item in row["domestic_cost_estimate_scenarios"]}
                != {"Baghdad", "Al-Muthanna"}
                or any(Decimal(item.get("uplift_fraction")) != Decimal("0.20")
                       or item.get("supplier_quote") is not False
                       or item.get("commercial_order_quantity") is not None
                       or item.get("complete_installed_cost") is not None
                       for item in row["domestic_cost_estimate_scenarios"])):
            raise ValueError("Concrete labour/material/20% scenarios or purchase boundary differ")
        ingredient_extension = sum((Decimal(item["material_extension_iqd"])
                                    for item in takeoff["material_inputs"]), Decimal(0))
        if any(
                abs(Decimal(item["direct_material_cost"]) - ingredient_extension) > Decimal("0.000001")
                or abs(
                    Decimal(item["estimated_total_iqd"])
                    - (Decimal(item["direct_material_cost"]) + Decimal(item["direct_labor_cost"]))
                    * (Decimal(1) + Decimal(item["uplift_fraction"]))
                ) > Decimal("0.000001")
                for item in row["domestic_cost_estimate_scenarios"]):
            raise ValueError("Per-span ingredients do not reconcile with material + labour + 20% estimate")
    logistics = read_json(LOGISTICS)
    logistics_manifest = read_json(LOGISTICS_MANIFEST)
    logistics_records = load_catalogue([LOGISTICS_SEED])
    local_gfrp = read_json(LOCAL_GFRP)
    local_gfrp_manifest = read_json(LOCAL_GFRP_MANIFEST)
    local_composite_records = load_catalogue([LOCAL_COMPOSITE_SEED])
    historical_labour_records = load_catalogue([HISTORICAL_LABOUR_SEED])
    domestic_material_seed = ROOT / ADDITIONAL_MATERIAL_SOURCES
    domestic_material_records = additional_material_records
    domestic_material_sources = additional_material_sources
    import_source = sources["iraq.cosit.import-report-2025"]
    import_rows = []
    for hs_code in ("39073000", "70191200", "74081100", "76042100",
                    "76042900", "76069100", "76069200", "72141020"):
        iqd = benchmarks[f"cso-import-2025:hs{hs_code}:iqd-per-kg"]
        usd = benchmarks[f"cso-import-2025:hs{hs_code}:usd-per-kg"]
        import_rows.append({
            "hs_code": hs_code,
            "material_description": iqd["material_description"],
            "source_printed_page": iqd["source_printed_page"],
            "reported_total_value_iqd": iqd["source_reported_total_value_iqd"],
            "reported_total_value_usd": iqd["source_reported_total_value_usd"],
            "reported_weight_kg": iqd["source_reported_weight_kg"],
            "unit_value_iqd_per_kg": iqd["unit_price"],
            "unit_value_usd_per_kg": usd["unit_price"],
            "iqd_benchmark_id": iqd["record_id"],
            "usd_benchmark_id": usd["record_id"],
            "supplier_offer": False,
            "candidate_match": False,
        })

    direct_source_counts = {kind: sum(row["kind"] == kind for row in records)
                            for kind in ("benchmark", "fx", "offer", "product", "source")}
    if len(records) != 533 or direct_source_counts["benchmark"] != 426:
        raise ValueError("Current offline catalogue is not the declared 533-record epoch")
    if (logistics.get("packet_id") != identity({key: value for key, value in logistics.items()
                                                  if key != "packet_id"})
            or logistics_manifest.get("packet_id") != logistics.get("packet_id")
            or logistics_manifest.get("manifest_id") != identity({key: value for key, value in logistics_manifest.items()
                                                                   if key != "manifest_id"})
            or logistics.get("candidate_id") != procurement.get("candidate_id")
            or logistics.get("source_input_id") != procurement.get("source_input_id")
            or logistics.get("procurement_bom_packet_id") != procurement.get("packet_id")
            or logistics.get("regional_cost_packet_id") != regional.get("packet_id")
            or logistics.get("takeoff_id") != regional.get("takeoff_id")
            or logistics.get("rental_source_epoch_id") != identity(logistics_records)
            or logistics.get("input_sha256", {}).get("rental_seed") != hashlib.sha256(LOGISTICS_SEED.read_bytes()).hexdigest()
            or logistics.get("input_sha256", {}).get("procurement_bom") != hashlib.sha256((ROOT / PROCUREMENT).read_bytes()).hexdigest()
            or logistics.get("input_sha256", {}).get("regional_cost_reference") != hashlib.sha256((ROOT / REGIONAL).read_bytes()).hexdigest()
            or logistics_manifest.get("files_sha256", {}).get(Path(LOGISTICS).name) != hashlib.sha256((ROOT / LOGISTICS).read_bytes()).hexdigest()
            or logistics_manifest.get("files_sha256", {}).get("README.md") != hashlib.sha256((ROOT / LOGISTICS).with_name("README.md").read_bytes()).hexdigest()
            or len(logistics.get("logistics_scenarios", [])) != 4
            or logistics.get("span_package_count") != 81
            or logistics.get("engineering_occurrence_count") != 486):
        raise ValueError("Current Iraqi logistics packet identity or candidate binding differs")
    if (local_gfrp.get("packet_id") != identity({key: value for key, value in local_gfrp.items()
                                                   if key != "packet_id"})
            or local_gfrp_manifest.get("packet_id") != local_gfrp.get("packet_id")
            or local_gfrp_manifest.get("manifest_id") != identity({key: value for key, value in local_gfrp_manifest.items()
                                                                      if key != "manifest_id"})
            or local_gfrp.get("source_candidate_id") != procurement.get("candidate_id")
            or local_gfrp.get("catalogue_epoch_id") != epoch_id
            or local_gfrp.get("priced_material", {}).get("purchased_bag_count") != 89
            or [row.get("partial_fabric_plus_labour_plus_20_iqd_per_10m2")
                for row in local_gfrp.get("scenarios", [])] != ["463800.00", "553800.00", "733800.00"]
            or local_gfrp.get("complete_material_cost_iqd") is not None
            or local_gfrp.get("complete_fabrication_cost_iqd") is not None
            or local_gfrp.get("unknown_is_zero") is not False
            or len(local_gfrp.get("local_resin_price_leads_not_applied", [])) != 3
            or len(local_gfrp.get("historical_labour_references", [])) != 4
            or local_gfrp.get("input_sha256", {}).get("local_catalogue_seed") != hashlib.sha256(LOCAL_COMPOSITE_SEED.read_bytes()).hexdigest()
            or local_gfrp.get("input_sha256", {}).get("historical_labour_seed") != hashlib.sha256(HISTORICAL_LABOUR_SEED.read_bytes()).hexdigest()
            or local_gfrp_manifest.get("files_sha256", {}).get(Path(LOCAL_GFRP).name) != hashlib.sha256((ROOT / LOCAL_GFRP).read_bytes()).hexdigest()
            or local_gfrp_manifest.get("files_sha256", {}).get("README.md") != hashlib.sha256((ROOT / LOCAL_GFRP).with_name("README.md").read_bytes()).hexdigest()
            or len(local_composite_records) != 9
            or len(historical_labour_records) != 5):
        raise ValueError("Current Iraqi retail composite screen or source identities differ")
    if len(import_rows) != 8 or import_screen["scenario_count"] != 12:
        raise ValueError("Imported-material benchmark or estimate count differs")

    payload = {
        "schema": "osr-sourcing-current-validation/1",
        "snapshot_date": "2026-10-30",
        "source_epoch_definition": "identity() of engineering.sourcing.catalogue.load_catalogue() record list",
        "source_epoch_id": epoch_id,
        "catalogue": {
            "offline_seed_record_count": len(records),
            "counts": {**direct_source_counts, "total": len(records)},
            "source_observations_are_not_supplier_quotes": True,
        },
        "review_packets": {
            "frame_vehicle": {
                "path": FRAME + "/summary.json",
                "publication_id": frame_manifest["publication_id"],
                "run_id": frame["run_id"],
                "candidate_id": frame["candidate_id"],
                "summary_id": frame["summary_id"],
                "input_requirement_count": frame["summary"]["input_requirement_count"],
                "evaluated": frame["summary"]["requirement_count"],
                "pending": 0,
                "compatible_matches": frame["summary"]["compatible_matches"],
                "priced": frame["summary"]["priced_requirement_count"],
                "physical_scope_count": frame["summary"]["physical_scope_count"],
                "engineering_occurrence_count": frame["summary"]["engineering_occurrence_count"],
                "complete_installed_cost": None,
                "physical_qualification": None,
            },
            "federated_manufacturing_groups": {
                "path": FEDERATION + "/summary.json",
                "publication_id": federation_manifest["publication_id"],
                "run_id": federation["run_id"],
                "candidate_id": federation["candidate_id"],
                "summary_id": federation["summary_id"],
                "input_requirement_count": federation["summary"]["input_requirement_count"],
                "evaluated": federation["summary"]["requirement_count"],
                "pending": federation["summary"]["input_requirement_count"] - federation["summary"]["requirement_count"],
                "compatible_matches": federation["summary"]["compatible_matches"],
                "priced": federation["summary"]["priced_requirement_count"],
                "physical_scope_count": federation["summary"]["input_physical_scope_count"],
                "source_manufacturing_group_count": federation["summary"]["input_source_manufacturing_group_count"],
                "located_occurrence_count": federation["summary"]["input_source_manufacturing_group_occurrence_count"],
                "unlocated_account_count": federation["summary"]["input_unlocated_account_count"],
                "evaluated_group_unknown_quantities": federation["summary"]["unknown_quantity_requirements"],
                "RFQ_drafts": federation["summary"]["RFQ_drafts"],
                "balanced_budget": read_json(FEDERATION + "/request.json")["max_requirements_by_category"],
                "complete_installed_cost": None,
                "physical_qualification": None,
            },
            "laminate_material_studies": laminate_rows,
        },
        "domestic_fabrication": {
            "additional_local_material_leads": {
                "seed_path": "engineering/sourcing/data/iraq-domestic-material-leads-2026-10.json",
                "seed_sha256": hashlib.sha256(domestic_material_seed.read_bytes()).hexdigest(),
                "source_count": len(domestic_material_sources),
                "source_epoch_id": identity(domestic_material_records),
                "source_ids": {key: value["record_id"] for key, value in sorted(domestic_material_sources.items())},
                "product_count": sum(row["kind"] == "product" for row in domestic_material_records),
                "offer_count": sum(row["kind"] == "offer" for row in domestic_material_records),
                "benchmark_count": sum(row["kind"] == "benchmark" for row in domestic_material_records),
                "candidate_product_matches": 0,
                "priced_offers": 0,
                "lead_scope": "EPS panels; polyurethane foam; aluminium ingots/alloys/anode blocks; crushed aggregate production and Iraqi construction-material distribution",
                "structural_core_or_body_qualification": None,
            },
            "local_composite_retail_cost_screen": {
                "path": LOCAL_GFRP,
                "manifest_path": LOCAL_GFRP_MANIFEST,
                "packet_id": local_gfrp["packet_id"],
                "manifest_id": local_gfrp_manifest["manifest_id"],
                "source_candidate_id": local_gfrp["source_candidate_id"],
                "reference_laminate_sample_candidate_id": local_gfrp["reference_laminate_sample_candidate_id"],
                "material_hypothesis_id": local_gfrp["physical_hypothesis"]["material_hypothesis_id"],
                "supplier_source_id": local_gfrp["source_supplier_id"],
                "catalogue_product_count": sum(row["kind"] == "product" for row in local_composite_records),
                "catalogue_offer_count": sum(row["kind"] == "offer" for row in local_composite_records),
                "mass_equivalent_fabric_pack_count": local_gfrp["priced_material"]["purchased_bag_count"],
                "scenario_count": len(local_gfrp["scenarios"]),
                "partial_cost_iqd_per_10m2": [row["partial_fabric_plus_labour_plus_20_iqd_per_10m2"]
                                               for row in local_gfrp["scenarios"]],
                "resin_cost_included": False,
                "complete_material_cost_iqd": local_gfrp["complete_material_cost_iqd"],
                "complete_fabrication_cost_iqd": local_gfrp["complete_fabrication_cost_iqd"],
                "physical_qualification": local_gfrp["physical_qualification"],
            },
            "historical_labour_earnings_reference": {
                "seed_path": "engineering/sourcing/data/iraq-labour-force-survey-2021.json",
                "seed_sha256": hashlib.sha256(HISTORICAL_LABOUR_SEED.read_bytes()).hexdigest(),
                "source_id": next(row["record_id"] for row in historical_labour_records if row["kind"] == "source"),
                "benchmark_count": sum(row["kind"] == "benchmark" for row in historical_labour_records),
                "used_in_current_2025_2026_cost_scenarios": False,
                "reason_not_used": "2021 national employee earnings are historical, not regional or inflation-normalized employer charge-out rates.",
            },
            "regional_cost_reference_2026_09": {
                "path": REGIONAL,
                "packet_id": regional["packet_id"],
                "source_epoch_id": regional["source_epoch_id"],
                "candidate_id": regional["candidate_id"],
                "source_input_id": regional["source_input_id"],
                "takeoff_id": regional["takeoff_id"],
                "regional_unit_rate_scenario_count": len(regional["unit_rate_estimates"]),
                "candidate_takeoff_concrete_scenario_count": len(regional["regional_concrete_takeoff_estimates"]),
                "candidate_mapped_aluminium_stock_scenario_count": len(regional["candidate_mapped_aluminium_stock_scenarios"]),
                "mapped_concrete_groups": 81,
                "mapped_concrete_occurrences": 486,
                "complete_installed_cost": regional["complete_installed_cost"],
                "physical_qualification": regional["physical_qualification"],
            },
            "iraq_span_logistics_sensitivity": {
                "path": LOGISTICS,
                "manifest_path": LOGISTICS_MANIFEST,
                "packet_id": logistics["packet_id"],
                "manifest_id": logistics_manifest["manifest_id"],
                "candidate_id": logistics["candidate_id"],
                "source_input_id": logistics["source_input_id"],
                "takeoff_id": logistics["takeoff_id"],
                "procurement_bom_packet_id": logistics["procurement_bom_packet_id"],
                "rental_source_id": logistics["rental_source_id"],
                "rental_benchmark_ids": logistics["rental_benchmark_ids"],
                "span_package_count": logistics["span_package_count"],
                "engineering_occurrence_count": logistics["engineering_occurrence_count"],
                "scenario_count": len(logistics["logistics_scenarios"]),
                "one_trip_one_day_per_span_conditional_iqd": logistics["logistics_scenarios"][0]["conditional_logistics_subtotal_iqd"],
                "material_labour_20_scenario_count": len(logistics["separate_material_labour_20_scenarios"]),
                "combined_partial_subtotal_count": len(logistics["combined_partial_subtotals"]),
                "complete_installed_cost": logistics["complete_installed_cost"],
                "physical_qualification": logistics["physical_qualification"],
            },
            "gfrp_local_fabrication_screen": {
                "path": GFRP,
                "packet_id": gfrp["packet_id"],
                "catalogue_epoch_id": gfrp["catalogue_epoch_id"],
                "scenario_count": len(gfrp["studies"]) * len(gfrp["basis"]["labour_scenarios_hours_per_10m2"]),
                "regional_scenario_count": gfrp["basis"]["regional_scenario_count"],
                "regional_governorate_count": len(gfrp["basis"]["regional_governorates"]),
                "complete_fabrication_cost_iqd": gfrp["complete_fabrication_cost_iqd"],
                "physical_qualification": gfrp["physical_qualification"],
            },
            "imported_aluminium_fabrication_sensitivity": {
                "path": IMPORT_SCREEN,
                "packet_id": import_screen["packet_id"],
                "scenario_count": import_screen["scenario_count"],
                "screened_rate_iqd_per_tonne_range": [
                    format(min(Decimal(row["screened_rate_iqd_per_tonne"]) for row in import_screen["scenarios"]), "f"),
                    format(max(Decimal(row["screened_rate_iqd_per_tonne"]) for row in import_screen["scenarios"]), "f"),
                ],
                "candidate_bom_cost_changed": import_screen["release_boundary"]["candidate_bom_cost_changed"],
                "candidate_binding": import_screen["candidate_binding"],
            },
        },
        "procurement_package_bom": {
            "path": PROCUREMENT,
            "packet_id": procurement["packet_id"],
            "candidate_id": procurement["candidate_id"],
            "evaluation_id": procurement["evaluation_id"],
            "source_input_id": procurement["source_input_id"],
            "engineering_scope_count": procurement["engineering_scope_count"],
            "located_stock_occurrence_count": procurement["located_stock_occurrence_count"],
            "unlocated_obligation_count": procurement["unlocated_obligation_count"],
            "draft_package_count": procurement["draft_package_count"],
            "all_located_occurrences_assigned_exactly_once": procurement["all_located_occurrences_assigned_exactly_once"],
            "commercial_order_quantities_known": procurement["commercial_order_quantities_known"],
            "priced_draft_packages": procurement["priced_draft_packages"],
            "source_registry_record_count": procurement["source_registry_record_count"],
            "source_registry_record_set_id": procurement["source_registry_record_set_id"],
            "material_demand_line_count": procurement["summary"]["material_demand_line_count"],
            "material_demand_group_count": procurement["summary"]["material_demand_group_count"],
            "material_demand_occurrence_count": procurement["summary"]["material_demand_occurrence_count"],
            "material_demand_mass_reconciliation_residual_kg": procurement["summary"]["material_demand_mass_reconciliation_residual_kg"],
            "candidate_mapped_aluminium_sensitivity_scenario_count": procurement["candidate_mapped_aluminium_sensitivity_scenario_count"],
            "concrete_material_input_takeoff": {
                "recipe_path": CONCRETE_RECIPE,
                "recipe_id": concrete_takeoff["recipe_id"],
                "takeoff_id": concrete_takeoff["takeoff_id"],
                "package_count": concrete_takeoff["package_count"],
                "manufacturing_group_count": concrete_takeoff["manufacturing_group_count"],
                "engineering_occurrence_count": concrete_takeoff["engineering_occurrence_count"],
                "ingredient_line_count": concrete_takeoff["ingredient_line_count"],
                "nominal_output_volume_m3": concrete_takeoff["nominal_output_volume_m3"],
                "material_inputs": [
                    {key: row[key] for key in ("material_key", "quantity_unit", "total_recipe_input_quantity",
                                               "benchmark_id", "benchmark_source_id", "benchmark_unit_rate_iqd",
                                               "material_extension_iqd")}
                    for row in concrete_takeoff["material_inputs"]
                ],
                "labour_hours_per_nominal_m3": ["2", "4", "8"],
                "uplift_fraction_on_direct_material_plus_labour": "0.20",
                "scenario_count": procurement["domestic_cost_estimate_scenario_count"],
                "commercial_order_quantity_known": concrete_takeoff["commercial_order_quantities_known"],
                "mix_design_approved": concrete_takeoff["mix_design_approved"],
                "purchase_yield_fraction": concrete_takeoff["conversion_yield_fraction"],
                "complete_installed_cost": concrete_takeoff["complete_installed_cost"],
                "non_additive_to_output_concrete_stock": concrete_takeoff["non_additive_to_output_concrete_stock"],
            },
            "complete_installed_bom": procurement["complete_installed_bom"],
            "complete_installed_cost": procurement["complete_installed_cost"],
            "physical_qualification": procurement["physical_qualification"],
        },
        "cso_import_material_benchmarks": {
            "source_key": "iraq.cosit.import-report-2025",
            "source_id": import_source["record_id"],
            "source_url": import_source["url"],
            "document_sha256": import_source["document_sha256"],
            "benchmark_count": len(import_rows) * 2,
            "hs_group_count": len(import_rows),
            "unit_value_basis": "national Table 10 total value divided by reported Weight(K.G.), using CIF import value",
            "rows": import_rows,
            "supplier_offers_created": 0,
            "compatible_bom_matches": 0,
        },
        "release_boundary": {
            "supplier_communications_sent": 0,
            "supplier_quotes": 0,
            "candidate_bom_cost_changed": False,
            "installed_cost_complete": False,
            "engineering_approved": False,
            "procurement_approved": False,
            "physical_acceptance": False,
            "selected_reference_changed": False,
        },
    }
    payload["validation_id"] = identity(payload)
    return payload


def main():
    output = build_validation()
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(),
                      "validation_id": output["validation_id"],
                      "source_epoch_id": output["source_epoch_id"],
                      "record_count": output["catalogue"]["offline_seed_record_count"]}))


if __name__ == "__main__":
    main()
