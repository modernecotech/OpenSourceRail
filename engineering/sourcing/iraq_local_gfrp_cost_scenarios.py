"""Source-bound Iraqi retail material and labour screen for a 10 m2 GFRP sample.

This is a material-mass-equivalent purchasing sensitivity only. It prices a
locally listed generic 300 g/m2 reinforcement and reports both a conservative
fabric-only subtotal and separate conditional generic-resin sensitivities.
None is a compatible-product or complete-fabrication estimate.
"""
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_EVEN
import gzip
import hashlib
import json
from pathlib import Path

from . import catalogue, inputs
from .model import encoded, identity

ROOT = Path(__file__).resolve().parents[2]
LOCAL_SEED = ROOT / "engineering/sourcing/data/iraq-local-composite-retail-2026-10.json"
LABOUR_SEED = ROOT / "engineering/sourcing/data/iraq-labour-force-survey-2021.json"
PACKET_ROOT = ROOT / "docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v18/solid-600gsm"
OUTPUT_ROOT = Path("docs/design-engine/sourcing/domestic-fabrication/iraq-local-gfrp-retail-screen-2026-10-v2")
HOURS_PER_10M2 = (Decimal("8"), Decimal("16"), Decimal("32"))
UPLIFT = Decimal("0.20")
CENT = Decimal("0.01")


def _read(path):
    path = Path(path)
    raw = path.read_bytes()
    if path.name.endswith(".gz"):
        raw = gzip.decompress(raw)
    return json.loads(raw)


def _money(value):
    return str(Decimal(value).quantize(CENT, rounding=ROUND_HALF_EVEN))


def _conditional_resin_scenarios(*, product_keys, products, offers_by_product,
                                 source_id, fabric_offer_id, fabric_extension,
                                 modeled_matrix_mass_kg, hours_per_10m2,
                                 wage_benchmark_id, wage_per_hour, area_m2):
    """Extend listed resin prices as explicit, unqualified price sensitivities."""
    scenarios = []
    for product_key in product_keys:
        product = products[product_key]
        offer, = offers_by_product[product_key]
        unit_price = Decimal(offer["tiers"][0]["unit_price"])
        if offer["quantity_unit"] == "kg":
            quantity = modeled_matrix_mass_kg
            extension = quantity * unit_price
            pack_count = None
            purchased_mass = quantity
            quantity_basis = "modeled matrix mass extended at the listed per-kg price; sale increment and minimum quantity unknown"
        else:
            pack_mass = Decimal(product["specifications"]["nominal_pack_mass_kg"]["value"])
            pack_count = int((modeled_matrix_mass_kg / pack_mass).to_integral_value(rounding=ROUND_CEILING))
            quantity = Decimal(pack_count)
            purchased_mass = quantity * pack_mass
            extension = quantity * unit_price
            quantity_basis = "whole listed cans rounded up to cover modeled matrix mass; product chemistry and suitability unknown"
        for hours in hours_per_10m2:
            labour = hours * wage_per_hour
            direct = fabric_extension + extension + labour
            uplift = direct * UPLIFT
            total = direct + uplift
            scenarios.append({
                "resin_product_key": product_key,
                "resin_product_id": product["record_id"],
                "resin_offer_id": offer["record_id"],
                "resin_source_id": source_id,
                "resin_listed_description": product["description"],
                "resin_listed_unit_price": str(unit_price),
                "resin_price_currency": offer["currency"],
                "resin_price_quantity_unit": offer["quantity_unit"],
                "resin_required_modeled_matrix_mass_kg": str(modeled_matrix_mass_kg),
                "resin_quantity_for_extension": str(quantity),
                "resin_pack_count": pack_count,
                "resin_purchased_mass_kg": str(purchased_mass),
                "resin_quantity_basis": quantity_basis,
                "resin_material_extension_iqd": _money(extension),
                "fabric_offer_id": fabric_offer_id,
                "fabric_material_extension_iqd": _money(fabric_extension),
                "labour_hours_per_10m2": str(hours),
                "wage_benchmark_id": wage_benchmark_id,
                "wage_rate_iqd_per_person_hour": str(wage_per_hour),
                "direct_labour_iqd": _money(labour),
                "direct_material_plus_labour_iqd": _money(direct),
                "uplift_fraction": str(UPLIFT),
                "uplift_iqd": _money(uplift),
                "conditional_fabric_resin_labour_plus_20_iqd_per_10m2": _money(total),
                "partial_unit_cost_iqd_per_m2": _money(total / area_m2),
                "technical_compatibility": None,
                "resin_cure_system_included": None,
                "supplier_quote": False,
                "candidate_product_match": False,
                "complete_material_cost_iqd": None,
                "complete_fabrication_cost_iqd": None,
                "unknown_is_zero": False,
                "scenario_limit": "conditional listed-price arithmetic only; resin chemistry, cure system, product match, full material scope and production route are unresolved",
            })
    return scenarios


def _assert_publication(folder):
    folder = Path(folder).expanduser().resolve()
    if (folder.is_symlink() or not folder.is_dir()
            or (folder / "manifest.json").is_symlink()
            or not (folder / "manifest.json").is_file()):
        raise ValueError("Regular 10 m2 laminate publication required")
    manifest = _read(folder / "manifest.json")
    required = {"catalogue.json.gz", "erp-drafts.json.gz", "input.json.gz", "records.json.gz",
                "request.json", "result.json.gz", "sources.tar.gz", "summary.json"}
    if set(manifest.get("files", {})) != required:
        raise ValueError("Laminate publication file inventory differs")
    for name, item in manifest["files"].items():
        path = folder / name
        if (path.is_symlink() or not path.is_file() or path.stat().st_size != item.get("bytes")
                or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256")):
            raise ValueError("Laminate publication file hash/size differs: " + name)
    result = _read(folder / "result.json.gz")
    source_input = _read(folder / "input.json.gz")
    records = _read(folder / "records.json.gz")
    if (manifest.get("schema") != "osr-sourcing-publication/1"
            or manifest.get("execution") != "completed"
            or manifest.get("publication_id") != identity({k: v for k, v in manifest.items()
                                                               if k != "publication_id"})
            or result.get("record_id") != manifest.get("run_id")
            or result.get("candidate_id") != manifest.get("candidate_id")
            or source_input.get("payload", {}).get("candidate_id") != manifest.get("candidate_id")
            or records.get("run", {}).get("record_id") != manifest.get("run_id")
            or manifest.get("physical_accepted") is not False):
        raise ValueError("Laminate source publication identity or acceptance boundary differs")
    payload = source_input.get("payload", {})
    process = payload.get("process", {})
    physical = payload.get("physical_definition", {})
    if (process.get("area_m2") != "10" or process.get("dry_glass_net_kg") != "24"
            or process.get("mixed_matrix_net_kg") != "24"
            or process.get("scrap_fraction") != "0.1"
            or physical.get("ply", {}).get("count") != 4
            or physical.get("ply", {}).get("areal_weight_g_m2") != "600"
            or physical.get("fibre_mass_fraction") != "0.50"):
        raise ValueError("Expected exact 10 m2, four-ply, 600 g/m2 research reference")
    return folder, manifest, source_input, records


def build_packet(laminate_path=PACKET_ROOT, *, local_seed=LOCAL_SEED, labour_seed=LABOUR_SEED):
    folder, manifest, source_input, records_packet = _assert_publication(laminate_path)
    supplements = catalogue.load_catalogue([local_seed])
    historic_labour = catalogue.load_catalogue([labour_seed])
    current = catalogue.load_catalogue()
    by_kind = {}
    for row in supplements:
        by_kind.setdefault(row["kind"], []).append(row)
    sources = {row["source_key"]: row for row in by_kind.get("source", [])}
    products = {row["product_key"]: row for row in by_kind.get("product", [])}
    offers = [row for row in by_kind.get("offer", [])]
    offers_by_product = {products_key: [row for row in offers
                                        if row["product_id"] == product["record_id"]]
                         for products_key, product in products.items()}
    source_key = "iraq.tc-safa.fibreglass-retail"
    fabric_key = "TC-SAFA-FIB-300GSM-1M2"
    resin_kg_key = "TC-SAFA-RESIN-1KG"
    resin_tr_key = "TC-SAFA-RESIN-TR-18KG"
    resin_ir_key = "TC-SAFA-RESIN-IR-18KG"
    if (set(sources) != {source_key} or set(products) != {fabric_key, resin_kg_key, resin_tr_key, resin_ir_key}
            or any(len(offers_by_product[key]) != 1 for key in products)):
        raise ValueError("Exact supplementary TC-Safa catalogue observations required")

    wage_key = "iq-cso-2026-09:baghdad:wage:skilled:hour-8h-day"
    wages = [row for row in current if row["kind"] == "benchmark" and row.get("benchmark_key") == wage_key]
    if (len(wages) != 1 or wages[0].get("currency") != "IQD"
            or wages[0].get("quantity_unit") != "h" or wages[0].get("unit_price") != "9375"
            or wages[0].get("is_manufactured_product_price") is not False):
        raise ValueError("Exact September 2026 Baghdad CSO skilled base-wage benchmark required")
    wage = wages[0]

    process = source_input["payload"]["process"]
    parent_vehicle_candidate_id = source_input["payload"].get("parent_candidate_id")
    if not isinstance(parent_vehicle_candidate_id, str) or len(parent_vehicle_candidate_id) != 64:
        raise ValueError("Exact parent vehicle candidate identity required")
    rows = {row["material_key"]: row for row in process["material_rows"]}
    gross_reference_glass_kg = Decimal(rows["glass-ply-1"]["gross_mass_kg"])
    gross_reference_matrix_kg = Decimal(rows["mixed-resin-kit"]["gross_mass_kg"])
    area_m2 = Decimal(process["area_m2"])
    source_product = products[fabric_key]
    offer = offers_by_product[fabric_key][0]
    price = Decimal(offer["tiers"][0]["unit_price"])
    pack_area = Decimal(source_product["specifications"]["nominal_area_per_pack_m2"]["value"])
    local_areal_mass = Decimal(source_product["specifications"]["nominal_areal_weight_g_m2"]["value"]) / Decimal(1000)
    pack_count = int((gross_reference_glass_kg / local_areal_mass / pack_area)
                     .to_integral_value(rounding=ROUND_CEILING))
    purchased_area = Decimal(pack_count) * pack_area
    purchased_fabric_mass = purchased_area * local_areal_mass
    fabric_extension = Decimal(pack_count) * price
    wage_per_hour = Decimal(wage["unit_price"])

    historical_rows = sorted((row for row in historic_labour if row["kind"] == "benchmark"),
                             key=lambda row: row["benchmark_key"])
    if (len(historical_rows) != 4 or any(row.get("quantity_unit") != "h" or row.get("currency") != "IQD"
                                         or row.get("is_manufactured_product_price") is not False
                                         for row in historical_rows)):
        raise ValueError("Four exact ILO/CSO/KRSO 2021 hourly-earnings references required")

    resin_rows = []
    for product_key in (resin_kg_key, resin_tr_key, resin_ir_key):
        record_product = products[product_key]
        record_offer = offers_by_product[product_key][0]
        resin_rows.append({
            "product_key": product_key,
            "product_id": record_product["record_id"],
            "offer_id": record_offer["record_id"],
            "catalogue_item_number": record_product["part_number"],
            "listed_description": record_product["description"],
            "listed_price": record_offer["tiers"][0]["unit_price"],
            "currency": record_offer["currency"],
            "quantity_unit": record_offer["quantity_unit"],
            "compatibility": "not established; chemistry/cure system unavailable",
            "included_in_partial_fabric_material_subtotal": False,
            "reason_excluded": "The 10 m2 reference requires a mixed epoxy/hardener matrix; listing chemistry, cure-system content, structural compatibility and supplier confirmation are absent.",
        })

    scenarios = []
    for hours in HOURS_PER_10M2:
        direct_labour = hours * wage_per_hour
        direct_known = fabric_extension + direct_labour
        uplift = direct_known * UPLIFT
        subtotal = direct_known + uplift
        scenarios.append({
            "labour_hours_per_10m2": str(hours),
            "labour_hours_per_m2": str(hours / area_m2),
            "wage_benchmark_id": wage["record_id"],
            "wage_source_id": wage["source_id"],
            "wage_rate_iqd_per_person_hour": str(wage_per_hour),
            "labour_wage_basis": "CSO September 2026 Baghdad skilled construction-worker average normalized from 75,000 IQD per 8-hour day; base wage only, not a measured composite-shop charge-out rate",
            "direct_labour_iqd": _money(direct_labour),
            "priced_fabric_packs": pack_count,
            "fabric_pack_area_m2": str(pack_area),
            "fabric_purchased_area_m2": str(purchased_area),
            "fabric_purchased_mass_kg": str(purchased_fabric_mass),
            "fabric_offer_id": offer["record_id"],
            "fabric_unit_price_iqd_per_pack": str(price),
            "known_fabric_material_extension_iqd": _money(fabric_extension),
            "direct_known_fabric_plus_labour_iqd": _money(direct_known),
            "uplift_fraction": str(UPLIFT),
            "uplift_iqd": _money(uplift),
            "partial_fabric_plus_labour_plus_20_iqd_per_10m2": _money(subtotal),
            "partial_screen_iqd_per_m2": _money(subtotal / area_m2),
            "resin_and_cure_system_cost_iqd": None,
            "complete_material_cost_iqd": None,
            "complete_fabrication_cost_iqd": None,
            "unknown_is_zero": False,
        })

    conditional_resin_scenarios = _conditional_resin_scenarios(
        product_keys=(resin_kg_key, resin_tr_key, resin_ir_key),
        products=products,
        offers_by_product=offers_by_product,
        source_id=sources[source_key]["record_id"],
        fabric_offer_id=offer["record_id"],
        fabric_extension=fabric_extension,
        modeled_matrix_mass_kg=gross_reference_matrix_kg,
        hours_per_10m2=HOURS_PER_10M2,
        wage_benchmark_id=wage["record_id"],
        wage_per_hour=wage_per_hour,
        area_m2=area_m2,
    )

    local_definition = {
        "schema": "osr-local-composite-material-hypothesis/1",
        "parent_vehicle_candidate_id": parent_vehicle_candidate_id,
        "reference_laminate_sample_candidate_id": source_input["payload"]["candidate_id"],
        "reference_study_publication_id": manifest["publication_id"],
        "area_m2": str(area_m2),
        "construction": "Eight plies of the listed generic 300 g/m2 reinforcement over 10 m2, giving equal gross dry-fibre mass to the reference four-ply 600 g/m2 material schedule before architecture/property checks.",
        "reference_gross_dry_fibre_mass_kg": str(gross_reference_glass_kg),
        "reference_gross_matrix_mass_kg_unpriced": str(gross_reference_matrix_kg),
        "local_product_key": fabric_key,
        "local_areal_weight_g_m2": str(local_areal_mass * Decimal(1000)),
        "nominal_mass_equivalent_ply_count": 8,
        "scrap_fraction_inherited_for_material-quantity-screen-only": process["scrap_fraction"],
        "material_architecture_equivalence": False,
        "material_hypothesis_id": None,
        "same_physical_candidate_as_reference": False,
        "selected_or_qualified": False,
    }
    local_definition["material_hypothesis_id"] = identity(local_definition)
    current_wage_source = next((row for row in current if row["kind"] == "source"
                                and row["record_id"] == wage["source_id"]), None)
    if current_wage_source is None:
        raise ValueError("Current CSO wage source record not found")
    source_records = sorted(supplements + historic_labour + [wage, current_wage_source],
                           key=lambda row: row["record_id"])
    source_rows = {row["source_key"]: row for row in source_records if row["kind"] == "source"}
    historical_summary = [{
        "benchmark_id": row["record_id"],
        "benchmark_key": row["benchmark_key"],
        "unit_price_iqd_per_hour": row["unit_price"],
        "survey_period": row["observation_period"],
        "source_id": row["source_id"],
        "used_in_current_cost_scenarios": False,
        "exclusion_reason": "2021 employee earnings are historical, national and not normalized to 2026 or converted to employer charge-out rates.",
    } for row in historical_rows]
    packet = {
        "schema": "osr-iraq-local-gfrp-retail-cost-screen/1",
        "estimate_date": "2026-10-30",
        "source_candidate_id": parent_vehicle_candidate_id,
        "reference_laminate_sample_candidate_id": source_input["payload"]["candidate_id"],
        "reference_study_publication_id": manifest["publication_id"],
        "physical_hypothesis": local_definition,
        "source_supplier_id": sources[source_key]["record_id"],
        "source_supplier_key": source_key,
        "source_url": sources[source_key]["url"],
        "source_retrieved_at": sources[source_key]["retrieved_at"],
        "source_page_availability_note": "The retailer instructs users to reconfirm availability and lead time; observed listing prices can change.",
        "catalogue_epoch_id": identity(catalogue.load_catalogue()),
        "supplementary_price_source_record_ids": [row["record_id"] for row in supplements],
        "supplementary_historical_labour_source_ids": [row["record_id"] for row in historic_labour if row["kind"] == "source"],
        "historical_labour_references": historical_summary,
        "priced_material": {
            "product_id": source_product["record_id"],
            "product_key": fabric_key,
            "part_number": source_product["part_number"],
            "product_offer_id": offer["record_id"],
            "description": source_product["description"],
            "unit_price_iqd_per_1m2_bag": str(price),
            "price_type": "public distributor retail listing, not quotation",
            "gross_required_dry_fibre_mass_kg": str(gross_reference_glass_kg),
            "purchased_bag_count": pack_count,
            "purchased_area_m2": str(purchased_area),
            "purchased_mass_kg": str(purchased_fabric_mass),
            "net_reference_glass_mass_kg": str(Decimal(rows["glass-ply-1"]["net_mass_kg"])),
            "cutting_and_yield_confirmation": None,
            "technical_compatibility": "not established; no orientation, weave, fibre sizing or rail allowables published",
        },
        "local_resin_price_leads_not_applied": resin_rows,
        "conditional_local_resin_price_scenarios": conditional_resin_scenarios,
        "conditional_resin_scenario_method": "(listed local 300 g/m2 reinforcement extension + listed generic resin extension at the modeled gross matrix mass + assumed direct base-wage labour) x 1.20; resin identity and suitability are unqualified",
        "labour_rate": {
            "benchmark_id": wage["record_id"],
            "benchmark_key": wage_key,
            "source_id": wage["source_id"],
            "unit_price_iqd_per_person_hour": str(wage_per_hour),
            "observation_period": wage["observation_period"],
            "normalization": "Published skilled-worker day rate divided by the existing project assumption of 8 hours per workday.",
            "scope": "Construction-worker base-wage proxy for composite-shop labour; employer burden, supervision and overhead excluded.",
        },
        "labour_hour_basis": "8/16/32 assumed hours per 10 m2 copied from the existing comparative laminate labour sensitivity; not a measured route for this different eight-ply retail textile.",
        "scenarios": scenarios,
        "formula": "(89 listed 1 m2 fabric bags x IQD 3,500 per bag + assumed fabrication person-hours x IQD 9,375 per person-hour) x 1.20",
        "uplift_fraction": str(UPLIFT),
        "uplift_scope": "20% is an unallocated planning uplift applied only to the listed fabric purchase amount plus assumed direct base-wage labour in each scenario; it is not a verified overhead, profit, tax, contingency or shop charge-out rate.",
        "unpriced_or_unresolved": [
            {"item": "epoxy/mixed matrix", "required_gross_mass_kg": str(gross_reference_matrix_kg), "price_iqd": None,
             "reason": "The reference requires resin and included hardener. Local listed resin chemistry, cure system and compatibility are unspecified."},
            {"item": "hardener/catalyst", "required_mass_kg": None, "price_iqd": None,
             "reason": "Cure system, mix ratio and compatibility are unresolved; no quantity is inferred."},
            {"item": "adhesive, inserts, coatings, release materials and consumables", "required_mass": None, "price_iqd": None,
             "reason": "Not specified by the 10 m2 material hypothesis."},
            {"item": "mould/tooling, utilities, machine time, QA and rework", "required_mass": None, "price_iqd": None,
             "reason": "No local production route, timed operation or equipment quote is available."},
            {"item": "delivery, taxes and current stock", "required_mass": None, "price_iqd": None,
             "reason": "Retail page asks the buyer to reconfirm availability; tax and delivery basis are not stated."},
        ],
        "complete_material_cost_iqd": None,
        "complete_fabrication_cost_iqd": None,
        "complete_installed_cost_iqd": None,
        "whole_life_cost_iqd": None,
        "priced_candidate_requirement_count": 0,
        "technical_candidate_product_matches": 0,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_qualification": None,
        "selected_reference_changed": False,
        "unknown_is_zero": False,
        "input_sha256": {
            "laminate_study_manifest": inputs.digest(folder / "manifest.json"),
            "laminate_study_input": inputs.digest(folder / "input.json.gz"),
            "laminate_study_records": inputs.digest(folder / "records.json.gz"),
            "local_catalogue_seed": inputs.digest(local_seed),
            "historical_labour_seed": inputs.digest(labour_seed),
            "default_supplier_catalogue": inputs.digest(ROOT / "engineering/sourcing/data/supplier-catalogue.json"),
            "current_material_wage_seed": inputs.digest(ROOT / "engineering/sourcing/data/iraq-domestic-2026-july.json"),
        },
        "source_record_index": {
            key: {"record_id": row["record_id"], "publisher": row["publisher"], "url": row["url"]}
            for key, row in sorted(source_rows.items())
        },
    }
    packet["packet_id"] = identity(packet)
    return packet


def publish_packet(packet, output):
    destination = Path(output).expanduser().resolve()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Fresh local composite cost publication directory required")
    destination.mkdir(parents=True)
    packet_path = destination / "iraq-local-gfrp-retail-screen.json"
    packet_path.write_bytes(encoded(packet) + b"\n")
    scenarios = packet["scenarios"]
    lines = [
        "# Iraqi local GFRP retail material and labour screen",
        "",
        "This source-bound partial screen applies the current Mosul retail listing for generic 300 g/m2 fibreglass (IQD 3,500 per 1 m2 bag) to a 10 m2 mass-equivalent material takeoff. It uses 89 bags to cover the gross dry-fibre material quantity. Eight plies at 300 g/m2 match the reference 24 kg dry-fibre mass by arithmetic only; architecture, directionality and strength are not equivalent to the reference four-ply 600 g/m2 biaxial fabric.",
        "",
        "The wage basis is the September 2026 Baghdad skilled construction-worker average normalized to IQD 9,375 per person-hour. The 8/16/32 hours per 10 m2 are planning scenarios transferred from the existing laminate study, not a timed local shop route. Each partial total is (listed fabric purchase + direct base-wage labour) x 1.20.",
        "",
        "| Assumed labour | Listed fabric | Direct labour | 20% allowance | Partial total per 10 m2 |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in scenarios:
        lines.append(f"| {row['labour_hours_per_10m2']} h | IQD {row['known_fabric_material_extension_iqd']} | IQD {row['direct_labour_iqd']} | IQD {row['uplift_iqd']} | IQD {row['partial_fabric_plus_labour_plus_20_iqd_per_10m2']} |")
    lines += [
        "",
        "The fabric-only table remains the source-complete partial screen. A separate conditional sensitivity adds each local generic resin listing at the modelled matrix mass and applies the same assumed labour hours and 20% uplift. Resin chemistry, hardener/catalyst content, cure method and compatibility with the epoxy/hardener reference remain unknown, so this is unqualified listed-price arithmetic rather than an engineering cost estimate. Other required material, tooling and installation costs remain unknown, not zero. The public listing asks buyers to reconfirm availability and lead time. This is not an offer, compatible candidate price, selected body design, or physical qualification.",
        "",
        "The supplementary Iraq Labour Force Survey 2021 rates are included as historical employee-earnings references only. They are national, not inflation-adjusted, and are excluded from these 2026 scenarios.",
        "",
        "Source: https://tc-safa.com/category/080010000 · wage basis: CSO September 2026 governorate construction-material and worker-wage bulletin. Exact source record IDs and input hashes are in the JSON and manifest.",
        "",
        "## Conditional listed-resin sensitivity",
        "",
        "| Local resin listing | Assumed labour | Listed fabric + resin | Direct labour | 20% allowance | Conditional partial total per 10 m² |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in packet["conditional_local_resin_price_scenarios"]:
        material_sum = Decimal(row["fabric_material_extension_iqd"]) + Decimal(row["resin_material_extension_iqd"])
        lines.append(f"| {row['resin_product_key']} | {row['labour_hours_per_10m2']} h | IQD {_money(material_sum)} | IQD {row['direct_labour_iqd']} | IQD {row['uplift_iqd']} | IQD {row['conditional_fabric_resin_labour_plus_20_iqd_per_10m2']} |")
    lines += [
        "",
        "The 1 kg resin listing is extended by modelled matrix mass at its per-kg price; the 18 kg listings are rounded up to whole cans. This does not establish product compatibility or a purchase order. These conditional totals do not replace the unknown resin/cure-system cost in the engineering BOM.",
        "",
    ]
    readme = destination / "README.md"
    readme.write_text("\n".join(lines), encoding="utf-8")
    manifest = {
        "schema": "osr-iraq-local-gfrp-retail-screen-publication/1",
        "packet_id": packet["packet_id"],
        "files_sha256": {path.name: inputs.digest(path) for path in (packet_path, readme)},
        "material_hypothesis_id": packet["physical_hypothesis"]["material_hypothesis_id"],
        "parent_vehicle_candidate_id": packet["source_candidate_id"],
        "reference_study_publication_id": packet["reference_study_publication_id"],
        "complete_installed_cost_iqd": None,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_qualification": None,
        "selected_reference_changed": False,
        "conditional_resin_scenario_count": len(packet["conditional_local_resin_price_scenarios"]),
        "conditional_resin_price_sensitivity_only": True,
    }
    manifest["manifest_id"] = identity(manifest)
    (destination / "manifest.json").write_bytes(encoded(manifest) + b"\n")
    return {"path": str(destination), "packet_id": packet["packet_id"],
            "manifest_id": manifest["manifest_id"], "scenario_count": len(scenarios),
            "partial_cost_iqd": [row["partial_fabric_plus_labour_plus_20_iqd_per_10m2"] for row in scenarios],
            "conditional_resin_scenario_count": len(packet["conditional_local_resin_price_scenarios"]),
            "conditional_resin_partial_cost_iqd": [row["conditional_fabric_resin_labour_plus_20_iqd_per_10m2"] for row in packet["conditional_local_resin_price_scenarios"]],
            "complete_installed_cost_iqd": None, "physical_qualification": None}
