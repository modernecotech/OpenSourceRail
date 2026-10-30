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
from .federated_span_rebar_cost import verify_packet as verify_federated_span_rebar_packet
from .station_drive_rfq import verify_packet as verify_station_drive_rfq_packet
from .sensitivity import candidate_sourcing_sensitivity, mass_account_reconciliation_priority
from engineering.mass_ledger_audit import verify as verify_mass_ledger


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/design-engine/sourcing/validation-current.json"
FRAME = "docs/design-engine/sourcing/packets/frame-vehicle-iraq-domestic-sources-v13"
FEDERATION = "docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v13"
LAMINATES = "docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v18"
REGIONAL = "docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json"
GFRP = "docs/design-engine/sourcing/domestic-fabrication/estimates/current/gfrp-laminate-local-2026-v19.json"
IMPORT_SCREEN = "docs/design-engine/sourcing/domestic-fabrication/cso-imported-aluminium-fabrication-sensitivity-2025-2026.json"
PROCUREMENT = "docs/design-engine/sourcing/procurement-bom/federated-v06-research-packages-v24.json.gz"
CONCRETE_RECIPE = "docs/design-engine/sourcing/domestic-fabrication/takeoff-recipes/concrete-material-inputs-2026-09.json"
LOGISTICS = "docs/design-engine/sourcing/domestic-fabrication/logistics-2026-september-v9/iraq-span-logistics-sensitivity.json"
LOGISTICS_MANIFEST = "docs/design-engine/sourcing/domestic-fabrication/logistics-2026-september-v9/manifest.json"
FEDERATED_REBAR = "docs/design-engine/sourcing/domestic-fabrication/federated-span-rebar-screen-2026-10/federated-span-rebar-screen.json"
FEDERATED_REBAR_MANIFEST = "docs/design-engine/sourcing/domestic-fabrication/federated-span-rebar-screen-2026-10/manifest.json"
LOCAL_GFRP = "docs/design-engine/sourcing/domestic-fabrication/iraq-local-gfrp-retail-screen-2026-10-v2/iraq-local-gfrp-retail-screen.json"
LOCAL_GFRP_MANIFEST = "docs/design-engine/sourcing/domestic-fabrication/iraq-local-gfrp-retail-screen-2026-10-v2/manifest.json"
ADDITIONAL_MATERIAL_SOURCES = "engineering/sourcing/data/iraq-domestic-material-leads-2026-10.json"
ADDITIONAL_FABRICATION_SOURCES = "engineering/sourcing/data/iraq-domestic-fabrication-discovery-2026-10.json"
CONSTRUCTION_WAGES_2024 = "engineering/sourcing/data/iraq-construction-wages-2024.json"
MASS_RECONCILIATION = "docs/design-engine/mass-reconciliation/current"
STATION_DRIVE_RFQ = "docs/design-engine/sourcing/rfq-drafts/station-drive-banks-2026-10"


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
    construction_wage_records = load_catalogue([ROOT / CONSTRUCTION_WAGES_2024])
    construction_wage_sources = {row["source_key"]: row for row in construction_wage_records
                                  if row["kind"] == "source"}
    construction_wage_benchmarks = {row["benchmark_key"]: row for row in construction_wage_records
                                    if row["kind"] == "benchmark"}
    construction_wage_source = construction_wage_sources.get("iraq.cso.construction-wages-2024")
    if (len(construction_wage_sources) != 1 or len(construction_wage_benchmarks) != 90
            or construction_wage_source is None
            or construction_wage_source.get("source_kind") != "national_statistic"
            or construction_wage_source.get("observation_period") != "2024 annual construction-worker wage table"
            or construction_wage_source.get("printed_page") != 9
            or "not used in current candidate cost estimates" not in construction_wage_source.get("methodology", "")):
        raise ValueError("Historical CSO 2024 construction-wage reference differs from its declared source scope")
    expected_wage_keys = {
        f"iq-cso-2024:{region}:wage:{category}:hour-8h-day"
        for region in ("nineveh", "kirkuk", "diyala", "anbar", "baghdad", "babil", "karbala",
                       "wasit", "salah-al-din", "najaf", "al-qadisiyyah", "al-muthanna",
                       "dhi-qar", "maysan", "basrah")
        for category in ("administrator", "engineer", "guard", "unskilled", "semi-skilled", "skilled")
    }
    if set(construction_wage_benchmarks) != expected_wage_keys:
        raise ValueError("Historical CSO 2024 wage table does not cover the declared 15 × 6 source grid")

    fabrication_discovery_path = ROOT / ADDITIONAL_FABRICATION_SOURCES
    fabrication_discovery_records = load_catalogue([fabrication_discovery_path])
    fabrication_discovery_sources = {row["source_key"]: row for row in fabrication_discovery_records
                                     if row["kind"] == "source"}
    expected_fabrication_discovery_keys = {
        "iraq.ms-cable-busbar",
        "iraq.asas-global-aluminium",
        "iraq.nubin-grp-facade",
    }
    if (set(fabrication_discovery_sources) != expected_fabrication_discovery_keys
            or len(fabrication_discovery_records) != 3
            or any(row["kind"] != "source" for row in fabrication_discovery_records)):
        raise ValueError("Supplemental Iraqi fabrication discovery seed must remain three source-only leads")
    for wage in construction_wage_benchmarks.values():
        daily = Decimal(wage["source_published_rate_iqd_per_work_day"])
        if (wage.get("source_id") != construction_wage_source["record_id"]
                or wage.get("quantity_unit") != "h"
                or wage.get("currency") != "IQD"
                or wage.get("employer_burden_included") is not False
                or wage.get("supplier_quote") is not False
                or wage.get("target_installed_rate") is not False
                or Decimal(wage["unit_price"]) != daily / Decimal(8)):
            raise ValueError("Historical CSO 2024 wage benchmark differs from its source or 8-hour normalization")
    baghdad_skilled_2024 = construction_wage_benchmarks[
        "iq-cso-2024:baghdad:wage:skilled:hour-8h-day"]
    if (baghdad_skilled_2024.get("source_published_rate_iqd_per_work_day") != 75000
            or baghdad_skilled_2024.get("unit_price") != "9375"):
        raise ValueError("Historical CSO 2024 Baghdad skilled-wage value differs from the published table")

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
    station_drive_rfq_verification = verify_station_drive_rfq_packet(root=ROOT)
    station_drive_rfq = read_json(STATION_DRIVE_RFQ + "/station-drive-rfq-scope.json")
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
    procurement_lead_associations = sum(
        row.get("domestic_fabrication_lead_count", 0)
        for row in procurement.get("material_purchasing_lines", []))
    if len(additional_material_sources) != 18:
        raise ValueError("Current supplementary Iraqi source set must contain 18 source-only records")
    lead_by_key = {
        (row["system"], row["material"]): {
            lead["source_key"]: lead
            for lead in row.get("domestic_fabrication_lead_sources", [])
        }
        for row in procurement.get("material_purchasing_lines", [])
    }
    expected_local_manufacturing_leads = {
        ("wayside/primary", "copper-conductor", "iraq.diwan-electrical-industries"),
        ("wayside/primary", "copper-conductor", "iraq.rs-alnajaf-electrical-factory"),
        ("wayside/primary", "copper-conductor", "iraq.erbil-copper-cable"),
        ("vehicle/passive-bogie-pair", "steel-reference", "iraq.ibn-majid-heavy-engineering"),
        ("wayside/primary", "linear-steel-hypothesis", "iraq.ibn-majid-heavy-engineering"),
        ("vehicle/body", "gfrp_skin_research", "iraq.haidar-ahmed-mousa.pur-pir-panels"),
        ("vehicle/body", "gfrp_skin_research", "iraq.kanza-iq.sandwich-panel-lines"),
    }
    local_manufacturing_leads = []
    for system, material, source_key in expected_local_manufacturing_leads:
        lead = lead_by_key.get((system, material), {}).get(source_key)
        if lead is None:
            raise ValueError("A new Iraqi electrical or heavy-fabrication lead is missing from its candidate scope")
        local_manufacturing_leads.append(lead)
    if any(lead.get("price_recorded") is not False
           or lead.get("supplier_quotation") is not False
           or lead.get("technical_compatibility") is not None
           or lead.get("procurement_approved") is not False
           for lead in local_manufacturing_leads):
        raise ValueError("Iraqi electrical/heavy-fabrication discoveries cannot become products, offers or approvals")
    concrete_lead_lines = [row for row in procurement.get("material_purchasing_lines", [])
                           if (row.get("system"), row.get("material"))
                           == ("civil/concrete", "concrete-hypothesis")]
    hadeed_leads = [lead for row in concrete_lead_lines
                    for lead in row.get("domestic_fabrication_lead_sources", [])
                    if lead.get("source_key") == "iraq.hadeediraq.rebar-marketplace"]
    if (procurement_lead_associations != 52 or len(concrete_lead_lines) != 1 or len(hadeed_leads) != 1
            or hadeed_leads[0].get("price_recorded") is not False
            or hadeed_leads[0].get("supplier_quotation") is not False
            or hadeed_leads[0].get("technical_compatibility") is not None
            or "rebar quantity is attached" not in hadeed_leads[0].get("relevance", "")
            or any(row.get("kind") in {"product", "offer", "benchmark"}
                   and row.get("source_id") == hadeed_leads[0].get("source_id")
                   for row in additional_material_records)):
        raise ValueError("Hadeed rebar directory must remain a source-only lead for unlocated reinforcement")
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
    copper_lines = [row for row in procurement.get("material_purchasing_lines", [])
                    if (row.get("system"), row.get("material"), row.get("stock_scope"))
                    == ("wayside/primary", "copper-conductor", "equivalent-volume-stock")]
    copper_benchmark = benchmarks["cso-import-2025:hs74081100:iqd-per-kg"]
    copper_wage = benchmarks["iq-cso-2026-09:baghdad:wage:skilled:hour-8h-day"]
    if len(copper_lines) != 1:
        raise ValueError("Current research procurement BOM must contain one exact copper conductor stock line")
    copper_line = copper_lines[0]
    copper_takeoff = {
        "candidate_id": procurement["candidate_id"],
        "source_input_id": procurement["source_input_id"],
        "system": copper_line["system"],
        "material": copper_line["material"],
        "stock_scope": copper_line["stock_scope"],
        "gross_stock_mass_kg": copper_line["modeled_gross_stock_mass_kg"],
        "engineering_group_ids": copper_line["engineering_group_ids"],
        "engineering_occurrence_ids": copper_line["engineering_occurrence_ids"],
        "related_package_ids": copper_line["related_package_ids"],
    }
    copper_scenarios = copper_line.get("copper_imported_raw_stock_sensitivity_scenarios", [])
    if (copper_line.get("material_line_id") != identity(
            {key: value for key, value in copper_line.items() if key != "material_line_id"})
            or copper_line.get("copper_imported_raw_stock_sensitivity_takeoff_id") != identity(copper_takeoff)
            or copper_line.get("engineering_group_count") != 5
            or copper_line.get("engineering_occurrence_count") != 10
            or copper_line.get("modeled_gross_stock_mass_kg") != "9354.240000000002"
            or len(copper_scenarios) != 3
            or procurement.get("candidate_mapped_copper_demand_line_count") != 1
            or procurement.get("candidate_mapped_copper_sensitivity_scenario_count") != 3
            or procurement.get("candidate_mapped_copper_sensitivity_scenario_count")
            != procurement.get("summary", {}).get("candidate_mapped_copper_sensitivity_scenario_count")):
        raise ValueError("Current copper cost sensitivity is not bound to the exact research stock takeoff")
    for hours, scenario in zip((8, 16, 32), copper_scenarios):
        material_cost = Decimal(copper_line["modeled_gross_stock_mass_kg"]) * Decimal(copper_benchmark["unit_price"])
        labour_cost = (Decimal(copper_line["modeled_gross_stock_mass_kg"]) / Decimal(1000)
                       * Decimal(hours) * Decimal(copper_wage["unit_price"]))
        material_cost = material_cost.quantize(Decimal("0.01"))
        labour_cost = labour_cost.quantize(Decimal("0.01"))
        direct = material_cost + labour_cost
        total = (direct * Decimal("1.20")).quantize(Decimal("0.01"))
        if (scenario.get("labour_hours_per_gross_stock_tonne") != hours
                or scenario.get("candidate_id") != procurement.get("candidate_id")
                or scenario.get("source_input_id") != procurement.get("source_input_id")
                or scenario.get("candidate_takeoff_id") != copper_line.get("copper_imported_raw_stock_sensitivity_takeoff_id")
                or scenario.get("material_benchmark_id") != copper_benchmark.get("record_id")
                or scenario.get("material_benchmark_source_id") != copper_benchmark.get("source_id")
                or scenario.get("wage_benchmark_id") != copper_wage.get("record_id")
                or scenario.get("wage_benchmark_source_id") != copper_wage.get("source_id")
                or Decimal(scenario.get("direct_material_cost_iqd")) != material_cost
                or Decimal(scenario.get("direct_labour_cost_iqd")) != labour_cost
                or Decimal(scenario.get("estimated_total_iqd")) != total
                or scenario.get("supplier_quote") is not False
                or scenario.get("compatible_product_match") is not False
                or scenario.get("commercial_order_quantity") is not None
                or scenario.get("purchase_yield_fraction") is not None
                or scenario.get("complete_process_cost") is not None
                or scenario.get("complete_installed_cost") is not None
                or scenario.get("engineering_approved") is not False
                or scenario.get("procurement_approved") is not False
                or scenario.get("unknown_is_zero") is not False):
            raise ValueError("Copper raw-stock plus labour estimate differs from its sources or limits")
    logistics = read_json(LOGISTICS)
    logistics_manifest = read_json(LOGISTICS_MANIFEST)
    federated_rebar = read_json(FEDERATED_REBAR)
    federated_rebar_manifest = read_json(FEDERATED_REBAR_MANIFEST)
    federated_rebar_verification = verify_federated_span_rebar_packet(root=ROOT)
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
    if (federated_rebar.get("packet_id") != identity({
                key: value for key, value in federated_rebar.items() if key != "packet_id"})
            or federated_rebar_manifest.get("packet_id") != federated_rebar.get("packet_id")
            or federated_rebar.get("candidate_id") != procurement.get("candidate_id")
            or federated_rebar.get("evaluation_id") != procurement.get("evaluation_id")
            or federated_rebar.get("selection_id") is not None
            or federated_rebar.get("procurement_bom_packet_id") != procurement.get("packet_id")
            or federated_rebar.get("regional_cost_reference_packet_id") != regional.get("packet_id")
            or federated_rebar.get("span_count") != 81
            or len(federated_rebar.get("network_scenarios", [])) != 6
            or len(federated_rebar.get("domestic_supplier_discovery_leads", [])) != 5
            or federated_rebar.get("supplier_offers") != 0
            or federated_rebar.get("compatible_priced_product_matches") != 0
            or federated_rebar.get("complete_fabrication_cost_iqd") is not None
            or federated_rebar.get("installed_cost_iqd") is not None
            or federated_rebar_verification.get("packet_id") != federated_rebar.get("packet_id")):
        raise ValueError("Federated candidate rebar estimate identity, scope or open-price boundary differs")
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
            or len(local_gfrp.get("conditional_local_resin_price_scenarios", [])) != 9
            or [row.get("conditional_fabric_resin_labour_plus_20_iqd_per_10m2")
                for row in local_gfrp.get("conditional_local_resin_price_scenarios", [])[:3]] != ["671800.00", "761800.00", "941800.00"]
            or any(row.get("candidate_product_match") is not False
                   or row.get("complete_fabrication_cost_iqd") is not None
                   or row.get("unknown_is_zero") is not False
                   for row in local_gfrp.get("conditional_local_resin_price_scenarios", []))
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
    sourcing_sensitivity = candidate_sourcing_sensitivity(procurement)
    mass_manifest = read_json(MASS_RECONCILIATION + "/manifest.json")
    mass_verify = verify_mass_ledger(root=ROOT)
    mass_worksheet = read_gzip_json(MASS_RECONCILIATION + "/mass-closure-worksheet.json.gz")
    selected_reference_mass_priority = mass_account_reconciliation_priority(mass_worksheet)
    if (mass_verify.get("manifest_id") != mass_manifest.get("manifest_id")
            or mass_worksheet.get("candidate_id") != mass_manifest.get("candidate_id")
            or mass_worksheet.get("evaluation_id") != mass_manifest.get("evaluation_id")
            or mass_worksheet.get("selection_id") != mass_manifest.get("selection_id")
            or mass_worksheet.get("worksheet_id") != mass_verify.get("closure_worksheet_id")
            or mass_worksheet.get("candidate_id") == procurement.get("candidate_id")):
        raise ValueError("Selected-reference mass priority must be verified and remain separate from the research BOM candidate")

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
                "lead_scope": "EPS panels; polyurethane and PIR foam; PU/PIR/rock-wool and EPS-cement building panels; aluminium ingots/alloys/anode blocks; crushed aggregate production and Iraqi construction-material distribution; cement product families; rebar; precast foundation piles; rebar marketplace/RFQ directory; composite raw-material distribution; copper rod/wire and cable manufacturers; electrical cables/transformers, station enclosures and panels; heavy steel/aluminium fabrication",
                "feeder_cable_quantity_unmapped_source_leads": ["iraq.alrowad-cables"],
                "feeder_cable_quantity_scope": "Al Rowad is already linked as a general wire/cable discovery lead. The current BOM has no separately reconciled feeder-cable line or exact cable quantity; no feeder-cable price or product match is created.",
                "structural_core_or_body_qualification": None,
            },
            "additional_manufacturing_discovery_leads": {
                "seed_path": ADDITIONAL_FABRICATION_SOURCES,
                "seed_sha256": hashlib.sha256(fabrication_discovery_path.read_bytes()).hexdigest(),
                "source_count": len(fabrication_discovery_sources),
                "source_epoch_id": identity(fabrication_discovery_records),
                "source_ids": {key: value["record_id"]
                               for key, value in sorted(fabrication_discovery_sources.items())},
                "product_count": 0,
                "offer_count": 0,
                "benchmark_count": 0,
                "candidate_product_matches": 0,
                "priced_offers": 0,
                "lead_scope": {
                    "iraq.ms-cable-busbar": "Iraqi solid/stranded/flexible bare-copper-conductor and cable lead; winding geometry/insulation/thermal class not matched",
                    "iraq.asas-global-aluminium": "Iraqi extrusion and finishing lead; alloy/temper, custom-profile envelope, capacity and price unverified",
                    "iraq.nubin-grp-facade": "Iraqi GRP/GFRP façade fabrication lead; passenger-vehicle body process and qualification not established",
                },
                "supplier_quotes": 0,
                "compatible_products": 0,
                "engineering_approval": False,
                "procurement_approval": False,
            },
            "construction_wage_history_2024": {
                "seed_path": CONSTRUCTION_WAGES_2024,
                "seed_sha256": hashlib.sha256((ROOT / CONSTRUCTION_WAGES_2024).read_bytes()).hexdigest(),
                "source_id": construction_wage_source["record_id"],
                "benchmark_count": len(construction_wage_benchmarks),
                "governorate_count": 15,
                "worker_category_count": 6,
                "hour_normalization": "Published daily rate divided by explicit 8 working hours/day",
                "baghdad_skilled_daily_iqd_per_workday": baghdad_skilled_2024["source_published_rate_iqd_per_work_day"],
                "baghdad_skilled_hourly_iqd_per_hour": baghdad_skilled_2024["unit_price"],
                "employer_burden_included": False,
                "used_in_current_2025_2026_cost_scenarios": False,
                "historical_only": True,
                "limitation": "Historical base-wage context only; not inflation-adjusted, not an employer charge-out rate, and the bulletin does not tabulate the Kurdistan Region.",
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
                "conditional_resin_scenario_count": len(local_gfrp["conditional_local_resin_price_scenarios"]),
                "conditional_resin_partial_cost_iqd_per_10m2": [
                    row["conditional_fabric_resin_labour_plus_20_iqd_per_10m2"]
                    for row in local_gfrp["conditional_local_resin_price_scenarios"]],
                "conditional_resin_costs_are_compatible_quotes": False,
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
            "federated_span_rebar_screen": {
                "path": FEDERATED_REBAR,
                "manifest_path": FEDERATED_REBAR_MANIFEST,
                "packet_id": federated_rebar["packet_id"],
                "publication_id": federated_rebar_manifest["publication_id"],
                "candidate_id": federated_rebar["candidate_id"],
                "evaluation_id": federated_rebar["evaluation_id"],
                "selection_id": federated_rebar["selection_id"],
                "procurement_bom_packet_id": federated_rebar["procurement_bom_packet_id"],
                "span_count": federated_rebar["span_count"],
                "reinforcement_mass_proxy_kg": federated_rebar["reinforcement_mass_proxy_kg"],
                "reinforcement_mass_proxy_t": federated_rebar["reinforcement_mass_proxy_t"],
                "rate_kg_per_m3": federated_rebar["reinforcement_rate_kg_per_m3"],
                "scenario_count": len(federated_rebar["network_scenarios"]),
                "local_discovery_lead_count": len(federated_rebar["domestic_supplier_discovery_leads"]),
                "supplier_offers": federated_rebar["supplier_offers"],
                "compatible_priced_product_matches": federated_rebar["compatible_priced_product_matches"],
                "partial_material_labour_plus_20_iqd": [
                    row["partial_material_labour_plus_20pct_iqd"]
                    for row in federated_rebar["network_scenarios"]],
                "purchase_order_quantity_t": federated_rebar["estimated_purchase_quantity_t"],
                "complete_fabrication_cost_iqd": federated_rebar["complete_fabrication_cost_iqd"],
                "installed_cost_iqd": federated_rebar["installed_cost_iqd"],
                "physical_accepted": federated_rebar["physical_accepted"],
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
            "domestic_source_lead_association_count": procurement_lead_associations,
            "source_registry_record_count": procurement["source_registry_record_count"],
            "source_registry_record_set_id": procurement["source_registry_record_set_id"],
            "material_demand_line_count": procurement["summary"]["material_demand_line_count"],
            "material_demand_group_count": procurement["summary"]["material_demand_group_count"],
            "material_demand_occurrence_count": procurement["summary"]["material_demand_occurrence_count"],
            "material_demand_mass_reconciliation_residual_kg": procurement["summary"]["material_demand_mass_reconciliation_residual_kg"],
            "candidate_mapped_aluminium_sensitivity_scenario_count": procurement["candidate_mapped_aluminium_sensitivity_scenario_count"],
            "candidate_mapped_copper_sensitivity_scenario_count": procurement["candidate_mapped_copper_sensitivity_scenario_count"],
            "copper_imported_raw_stock_sensitivity": {
                "candidate_takeoff_id": copper_line["copper_imported_raw_stock_sensitivity_takeoff_id"],
                "engineering_group_count": copper_line["engineering_group_count"],
                "engineering_occurrence_count": copper_line["engineering_occurrence_count"],
                "gross_stock_mass_kg": copper_line["modeled_gross_stock_mass_kg"],
                "scenario_totals_iqd": [row["estimated_total_iqd"] for row in copper_scenarios],
                "compatible_supplier_match": False,
                "complete_installed_cost": None,
            },
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
        "station_drive_rfq_scope": {
            "path": STATION_DRIVE_RFQ + "/station-drive-rfq-scope.json",
            "manifest_path": STATION_DRIVE_RFQ + "/manifest.json",
            "publication_id": station_drive_rfq_verification["publication_id"],
            "packet_id": station_drive_rfq_verification["packet_id"],
            "candidate_id": station_drive_rfq_verification["candidate_id"],
            "evaluation_id": station_drive_rfq["evaluation_id"],
            "bank_scope_count": station_drive_rfq_verification["bank_scope_count"],
            "located_primary_occurrence_count": station_drive_rfq_verification["primary_occurrence_count"],
            "non_additive_open_account_link_count": station_drive_rfq_verification["open_account_link_count"],
            "service_scenario_count": station_drive_rfq_verification["service_scenario_count"],
            "candidate_level_copper_material_labour_plus_20_iqd": [
                row["estimated_total"] for row in
                station_drive_rfq["existing_candidate_level_copper_material_labour_sensitivities"]],
            "air_gap_adapter_extension_required": True,
            "frequency_map_field_required": True,
            "supplier_offers": station_drive_rfq["supplier_offers"],
            "supplier_communications_sent": station_drive_rfq_verification["supplier_communications_sent"],
            "complete_drive_installed_cost": station_drive_rfq_verification["complete_drive_installed_cost"],
            "physical_accepted": station_drive_rfq_verification["physical_accepted"],
            "selected_reference_changed": station_drive_rfq["selected_reference_changed"],
        },
        "candidate_sourcing_sensitivity": sourcing_sensitivity,
        "selected_reference_mass_reconciliation_priority": selected_reference_mass_priority,
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
