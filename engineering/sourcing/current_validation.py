"""Index the current 529-record sourcing evidence without editing source receipts."""
import gzip
import json
from pathlib import Path
from decimal import Decimal

from .catalogue import load_catalogue
from .model import identity


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/design-engine/sourcing/validation-current.json"
FRAME = "docs/design-engine/sourcing/packets/frame-vehicle-iraq-domestic-sources-v13"
FEDERATION = "docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v13"
LAMINATES = "docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v16"
REGIONAL = "docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v5/iraq-domestic-cost-reference-2026-09.json"
GFRP = "docs/design-engine/sourcing/domestic-fabrication/estimates/current/gfrp-laminate-local-2026-v16.json"
IMPORT_SCREEN = "docs/design-engine/sourcing/domestic-fabrication/cso-imported-aluminium-fabrication-sensitivity-2025-2026.json"
PROCUREMENT = "docs/design-engine/sourcing/procurement-bom/federated-v06-research-packages-v14.json.gz"


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
    if len(records) != 529 or direct_source_counts["benchmark"] != 426:
        raise ValueError("Current offline catalogue is not the declared 529-record epoch")
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
