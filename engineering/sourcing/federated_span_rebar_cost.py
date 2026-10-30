"""Candidate-bound domestic rebar material and labour planning screen.

The quantity is a declared preliminary 120 kg/m³ detailing allowance applied
to the exact nominal concrete spans in the current procurement packet. It is
not a bar schedule, purchase quantity, supplier offer or installed cost.
"""
from decimal import Decimal
from hashlib import sha256
import gzip
import json
from pathlib import Path

from engineering.station_rail import ROOT as REPOSITORY_ROOT
from .catalogue import load_catalogue
from .model import encoded, identity


PROCUREMENT = Path(
    "docs/design-engine/sourcing/procurement-bom/"
    "federated-v06-research-packages-v24.json.gz")
REGIONAL = Path(
    "docs/design-engine/sourcing/domestic-fabrication/"
    "regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json")
REGIONAL_MANIFEST = REGIONAL.with_name("manifest.json")
MATERIAL_LEADS = Path("engineering/sourcing/data/iraq-domestic-material-leads-2026-10.json")
OUTPUT_DIR = Path(
    "docs/design-engine/sourcing/domestic-fabrication/"
    "federated-span-rebar-screen-2026-10")
OUTPUT_FILE = "federated-span-rebar-screen.json"
ALLOWANCE_KG_PER_M3 = Decimal("120")
UPLIFT = Decimal("0.20")
HOURS_PER_TONNE = (Decimal("4"), Decimal("8"), Decimal("16"))
REGIONS = ("Baghdad", "Al-Muthanna")
REBAR_LEAD_KEYS = (
    "iraq.alpha-steel.rebar-range-2026",
    "iraq.hadeediraq.rebar-marketplace",
    "iraq-darin-steel-rebar",
    "iraq.al-anmaa-rebar",
    "iraq.qaiwan-steel-rebar",
)


def _read(path, *, compressed=False):
    path = Path(path)
    payload = path.read_bytes()
    return json.loads(gzip.decompress(payload) if compressed else payload)


def _hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _decimal(value, label):
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError("Invalid " + label)
    return result


def _engineering_quantity(value, label):
    """Drop insignificant float tails while preserving 12 significant digits."""
    return Decimal(format(float(_decimal(value, label)), ".12g"))


def _text(value):
    return format(value, "f")


def _regional_rates(regional):
    if (regional.get("schema") != "osr-iraq-domestic-cost-reference/2"
            or regional.get("candidate_takeoff_mapped_for_unit_rate_estimates") is not False
            or regional.get("unknown_is_zero") is not False):
        raise ValueError("Regional unit-rate packet scope differs")
    selected = {}
    for row in regional.get("unit_rate_estimates", []):
        if (row.get("family") != "rebar cut/bend"
                or row.get("region") not in REGIONS
                or str(row.get("labour_hours_per_output")) not in {"4", "8", "16"}):
            continue
        process = row.get("process", {})
        hours = Decimal(str(row["labour_hours_per_output"]))
        materials = process.get("material_lines", [])
        labour = process.get("labour_lines", [])
        if (process.get("candidate_id") != regional.get("candidate_id")
                or process.get("input_id") != regional.get("source_input_id")
                or process.get("application_scope") !=
                "digital-twin evaluation context; generic unit-rate recipe not mapped to candidate takeoff"
                or process.get("uplift_fraction") != "0.2"
                or len(materials) != 1 or len(labour) != 1
                or materials[0].get("quantity_unit") != "t"
                or materials[0].get("quantity") != "1"
                or materials[0].get("benchmark_id") is None
                or labour[0].get("quantity_unit") != "h"
                or labour[0].get("benchmark_id") is None
                or Decimal(str(labour[0].get("person_hours"))) != hours
                or Decimal(str(process.get("uplift_amount"))) !=
                (Decimal(str(process["direct_material_cost"]))
                 + Decimal(str(process["direct_labor_cost"]))) * UPLIFT):
            raise ValueError("Rebar unit-rate recipe differs from declared material/labour/uplift scope")
        if materials[0].get("material_key") != (
                "Iraqi-origin 2026-09 CSO reinforcing-bar statistic; grade/diameter unresolved"):
            raise ValueError("Rebar material rate is not the declared CSO statistical category")
        key = (row["region"], hours)
        if key in selected:
            raise ValueError("Duplicate rebar unit-rate scenario")
        selected[key] = {
            "material_rate_iqd_per_t": _decimal(materials[0]["unit_rate"], "rebar material rate"),
            "material_benchmark_id": materials[0]["benchmark_id"],
            "material_source_ids": list(process.get("source_ids", [])),
            "wage_rate_iqd_per_person_hour": _decimal(labour[0]["unit_rate"], "wage rate"),
            "wage_benchmark_id": labour[0]["benchmark_id"],
            "wage_basis": labour[0].get("wage_basis"),
            "wage_evidence_scope": labour[0].get("evidence_scope"),
        }
    expected = {(region, hours) for region in REGIONS for hours in HOURS_PER_TONNE}
    if set(selected) != expected:
        raise ValueError("Regional source does not contain the exact rebar cost scenario grid")
    return selected


def _local_rebar_leads(root):
    base = load_catalogue()
    extra = load_catalogue([Path(root) / MATERIAL_LEADS])
    records = {row["source_key"]: row for row in (*base, *extra) if row["kind"] == "source"}
    if len(REBAR_LEAD_KEYS) != len(set(REBAR_LEAD_KEYS)) or not set(REBAR_LEAD_KEYS) <= records.keys():
        raise ValueError("Local rebar discovery source registry is incomplete")
    return [{
        "source_key": key,
        "source_record_id": records[key]["record_id"],
        "source_url": records[key]["url"],
        "source_kind": records[key]["source_kind"],
        "discovery_only": True,
        "compatible_product_match": False,
        "supplier_offer": False,
        "price": None,
    } for key in REBAR_LEAD_KEYS]


def build_packet(root=REPOSITORY_ROOT, procurement_path=None, regional_path=None):
    root = Path(root).resolve()
    procurement_path = Path(procurement_path or (root / PROCUREMENT)).resolve()
    regional_path = Path(regional_path or (root / REGIONAL)).resolve()
    procurement = _read(procurement_path, compressed=procurement_path.suffix == ".gz")
    regional = _read(regional_path)
    regional_manifest_path = regional_path.with_name("manifest.json")
    regional_manifest = _read(regional_manifest_path)
    if (regional_manifest.get("schema") != "osr-iraq-regional-cost-reference-publication/1"
            or regional_manifest.get("manifest_id") != identity({
                key: value for key, value in regional_manifest.items() if key != "manifest_id"})
            or regional_manifest.get("packet_id") != regional.get("packet_id")
            or regional_manifest.get("file_sha256", {}).get(regional_path.name) != _hash(regional_path)):
        raise ValueError("Regional cost source manifest or packet binding differs")
    for relative, expected_hash in regional_manifest.get("file_sha256", {}).items():
        evidence = regional_manifest_path.parent / relative
        if not evidence.is_file() or _hash(evidence) != expected_hash:
            raise ValueError("Regional cost source file hash differs: " + relative)
    if (procurement.get("schema") != "osr-procurement-package-bom/1"
            or procurement.get("packet_id") != identity({
                key: value for key, value in procurement.items() if key != "packet_id"})
            or procurement.get("unknown_is_zero") is not False
            or procurement.get("selected_reference_changed") is not False
            or procurement.get("commercial_order_quantities_known") is not False
            or regional.get("packet_id") != identity({
                key: value for key, value in regional.items() if key != "packet_id"})
            or procurement.get("candidate_id") != regional.get("candidate_id")
            or procurement.get("source_input_id") != regional.get("source_input_id")):
        raise ValueError("Procurement and regional cost source identities differ")

    packages = [row for row in procurement.get("packages", [])
                if row.get("package_family") == "civil-concrete-stock-package"]
    by_key = {row.get("package_key"): row for row in packages}
    expected_keys = {f"span/{index}" for index in range(81)}
    if len(packages) != 81 or set(by_key) != expected_keys:
        raise ValueError("Exact federated civil candidate must contain 81 concrete span packages")
    obligations = set(procurement.get("unlocated_obligation_ids", []))
    links = procurement.get("unlocated_obligation_links", {}).get("links", [])
    links_by_scope = {row.get("scope_key"): row for row in links}
    rates = _regional_rates(regional)

    spans = []
    total_volume = Decimal(0)
    total_rebar = Decimal(0)
    for key in sorted(expected_keys, key=lambda item: int(item.split("/")[1])):
        package = by_key[key]
        index = int(key.split("/")[1])
        account_id = f"{key}/reinforcement_kg"
        link_scope = f"{key}/precast-reinforcement-and-prestress"
        link = links_by_scope.get(link_scope)
        package_id = package.get("package_id")
        volume = _engineering_quantity(package.get("nominal_stock_volume_m3"), "nominal concrete volume")
        if (not volume or package_id != identity({
                field: value for field, value in package.items() if field != "package_id"})
                or account_id not in obligations
                or link is None
                or account_id not in link.get("unlocated_obligation_ids", [])
                or package_id not in link.get("related_package_ids", [])
                or link.get("allocated_to_package_mass_or_quantity") is not False
                or link.get("association_is_package_membership") is not False):
            raise ValueError("Span rebar account lost its exact candidate/package association")
        occurrences = sorted(package.get("engineering_occurrence_ids", []))
        if len(occurrences) != 6 or any(not occurrence.startswith(key + "/") for occurrence in occurrences):
            raise ValueError("Concrete source occurrences are incomplete for " + key)
        rebar_kg = volume * ALLOWANCE_KG_PER_M3
        rebar_t = rebar_kg / Decimal(1000)
        span_scenarios = []
        for region in REGIONS:
            for hours in HOURS_PER_TONNE:
                rate = rates[(region, hours)]
                material = rebar_t * rate["material_rate_iqd_per_t"]
                labour_hours = rebar_t * hours
                labour = labour_hours * rate["wage_rate_iqd_per_person_hour"]
                uplift = (material + labour) * UPLIFT
                span_scenarios.append({
                    "region": region,
                    "hours_per_input_tonne": _text(hours),
                    "reinforcement_mass_proxy_t": _text(rebar_t),
                    "material_rate_iqd_per_t": _text(rate["material_rate_iqd_per_t"]),
                    "direct_material_cost_iqd": _text(material),
                    "assumed_person_hours": _text(labour_hours),
                    "base_wage_iqd_per_person_hour": _text(rate["wage_rate_iqd_per_person_hour"]),
                    "direct_labour_cost_iqd": _text(labour),
                    "direct_material_plus_labour_iqd": _text(material + labour),
                    "uplift_fraction": _text(UPLIFT),
                    "unallocated_uplift_iqd": _text(uplift),
                    "partial_material_labour_plus_20pct_iqd": _text(material + labour + uplift),
                    "material_benchmark_id": rate["material_benchmark_id"],
                    "material_source_ids": rate["material_source_ids"],
                    "wage_benchmark_id": rate["wage_benchmark_id"],
                    "wage_basis": rate["wage_basis"],
                    "wage_evidence_scope": rate["wage_evidence_scope"],
                    "supplier_offer": False,
                    "compatible_product_match": False,
                    "purchase_yield_fraction": None,
                    "purchase_order_quantity_t": None,
                    "complete_fabrication_cost_iqd": None,
                    "installed_cost_iqd": None,
                })
        spans.append({
            "span_index": index,
            "package_key": key,
            "package_id": package_id,
            "concrete_engineering_occurrence_ids": occurrences,
            "unlocated_reinforcement_obligation_id": account_id,
            "unlocated_scope_link_id": link["link_id"],
            "unlocated_scope_key": link_scope,
            "unlocated_scope_quantity": link.get("quantity"),
            "nominal_concrete_volume_m3": _text(volume),
            "reinforcement_basis": "120 kg/m3 declared preliminary rate in engineering/station_rail/civil.py; detailed bar schedule unknown",
            "reinforcement_mass_proxy_kg": _text(rebar_kg),
            "purchase_order_quantity_kg": None,
            "scenarios": span_scenarios,
        })
        total_volume += volume
        total_rebar += rebar_kg

    network_scenarios = []
    total_t = total_rebar / Decimal(1000)
    for region in REGIONS:
        for hours in HOURS_PER_TONNE:
            rate = rates[(region, hours)]
            material = total_t * rate["material_rate_iqd_per_t"]
            person_hours = total_t * hours
            labour = person_hours * rate["wage_rate_iqd_per_person_hour"]
            uplift = (material + labour) * UPLIFT
            network_scenarios.append({
                "region": region,
                "hours_per_input_tonne": _text(hours),
                "modeled_reinforcement_mass_proxy_t": _text(total_t),
                "direct_material_cost_iqd": _text(material),
                "assumed_person_hours": _text(person_hours),
                "direct_labour_cost_iqd": _text(labour),
                "direct_material_plus_labour_iqd": _text(material + labour),
                "uplift_fraction": _text(UPLIFT),
                "unallocated_uplift_iqd": _text(uplift),
                "partial_material_labour_plus_20pct_iqd": _text(material + labour + uplift),
                "material_benchmark_id": rate["material_benchmark_id"],
                "wage_benchmark_id": rate["wage_benchmark_id"],
                "supplier_offer": False,
                "compatible_product_match": False,
                "purchase_yield_fraction": None,
                "purchase_order_quantity_t": None,
                "complete_fabrication_cost_iqd": None,
                "installed_cost_iqd": None,
            })

    leads = _local_rebar_leads(root)
    input_paths = {
        "engineering/sourcing/federated_span_rebar_cost.py": root / "engineering/sourcing/federated_span_rebar_cost.py",
        "engineering/sourcing/cli.py": root / "engineering/sourcing/cli.py",
        "engineering/sourcing/model.py": root / "engineering/sourcing/model.py",
        "engineering/sourcing/catalogue.py": root / "engineering/sourcing/catalogue.py",
        "engineering/station_rail/civil.py": root / "engineering/station_rail/civil.py",
        PROCUREMENT.as_posix(): procurement_path,
        REGIONAL.as_posix(): regional_path,
        REGIONAL_MANIFEST.as_posix(): regional_manifest_path,
        MATERIAL_LEADS.as_posix(): root / MATERIAL_LEADS,
        "engineering/sourcing/data/supplier-catalogue.json": root / "engineering/sourcing/data/supplier-catalogue.json",
        "engineering/sourcing/data/public-feeds.json": root / "engineering/sourcing/data/public-feeds.json",
        "engineering/sourcing/data/iraq-domestic-2026-july.json": root / "engineering/sourcing/data/iraq-domestic-2026-july.json",
    }
    source_hashes = {relative: _hash(path) for relative, path in input_paths.items()}
    payload = {
        "schema": "osr-federated-span-domestic-rebar-screen/1",
        "candidate_id": procurement["candidate_id"],
        "evaluation_id": procurement["evaluation_id"],
        "selection_id": None,
        "selection_purpose": "Research-candidate cost estimate only; no design selection is asserted.",
        "source_input_id": procurement["source_input_id"],
        "procurement_bom_packet_id": procurement["packet_id"],
        "regional_cost_reference_packet_id": regional["packet_id"],
        "source_registry_record_set_id": procurement.get("source_registry_record_set_id"),
        "material_rate_period": "2026-09 CSO Iraqi-origin national reinforcing-bar statistic",
        "wage_period": "2026-09 CSO governorate monthly-average skilled base wage",
        "scope": "Rebar material mass proxy plus assumed cut/bend person-hours using published base wages, then one 20% unallocated planning uplift.",
        "reinforcement_basis": "120 kg/m3 preliminary declared detailing rate from engineering/station_rail/civil.py; exact candidate reinforcement account has no resolved commercial quantity or detailed bar schedule.",
        "reinforcement_rate_kg_per_m3": _text(ALLOWANCE_KG_PER_M3),
        "span_count": len(spans),
        "nominal_concrete_volume_m3": _text(total_volume),
        "reinforcement_mass_proxy_kg": _text(total_rebar),
        "reinforcement_mass_proxy_t": _text(total_t),
        "estimated_purchase_quantity_t": None,
        "purchase_yield_fraction": None,
        "span_packages": spans,
        "network_scenarios": network_scenarios,
        "domestic_supplier_discovery_leads": leads,
        "supplier_offers": 0,
        "compatible_priced_product_matches": 0,
        "direct_fasteners_included": False,
        "prestress_and_anchors_included": False,
        "concrete_ingredients_included": False,
        "formwork_moulds_qa_transport_erection_foundations_included": False,
        "employer_burden_tax_profit_or_contingency_included": False,
        "complete_fabrication_cost_iqd": None,
        "installed_cost_iqd": None,
        "whole_life_cost_iqd": None,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_accepted": False,
        "unknown_is_zero": False,
        "input_sha256": source_hashes,
    }
    payload["packet_id"] = identity(payload)
    return payload


def render_readme(packet):
    lines = [
        "# Federated candidate domestic rebar screen — October 2026",
        "",
        f"This research-only screen applies the declared 120 kg/m³ reinforcement allowance to {packet['span_count']} exact nominal concrete span packages in candidate `{packet['candidate_id']}` (evaluation `{packet['evaluation_id']}`). It estimates source-priced rebar mass plus assumed cut/bend labour and one 20% uplift. It is not a supplier quotation or a complete precast/fabrication estimate.",
        "",
        "## Network sensitivities",
        "",
        "| Wage region | Assumed hours/input tonne | Modeled mass proxy (t) | Direct material (IQD m) | Direct labour (IQD m) | +20% partial screen (IQD m) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in packet["network_scenarios"]:
        lines.append("| {region} | {hours} | {mass:.3f} | {material:.2f} | {labour:.2f} | {total:.2f} |".format(
            region=row["region"], hours=row["hours_per_input_tonne"],
            mass=float(row["modeled_reinforcement_mass_proxy_t"]),
            material=float(row["direct_material_cost_iqd"]) / 1e6,
            labour=float(row["direct_labour_cost_iqd"]) / 1e6,
            total=float(row["partial_material_labour_plus_20pct_iqd"]) / 1e6))
    lines += [
        "",
        "The calculation is `(modeled reinforcement mass × CSO material statistic + assumed person-hours × regional CSO skilled base wage) × 1.20`. The wage is a published base-wage proxy normalized from a daily value using an 8-hour day. It is not a factory charge-out rate. The 20% uplift is unallocated and is applied once to direct material plus labour.",
        "",
        "The 120 kg/m³ value is an explicit preliminary civil detailing rate, not a bar schedule. The modelled 216.577 t mass is a proxy for these 81 concrete packages; purchase yield, waste, bar diameters, grades, bending schedule, lap lengths, cages, welds, placing labour and commercial order quantity remain unknown. The rebar obligation IDs remain unlocated in the procurement BOM and are linked to their concrete packages for context only; this estimate does not turn those associations into package membership.",
        "",
        "Domestic leads include Alpha Steel, Hadeed Iraq, Darin Steel, Al-Anmaa and Qaiwan Steel. They are discovery leads only: no current offer, product specification match, available capacity, delivered price or order is present. The CSO statistical rate is not a supplier quote.",
        "",
        "Prestress, anchorages, direct fasteners, concrete ingredients, moulds, QA, utilities, employer burden, taxes, profit, transport, crane lifting, foundations, erection, maintenance and warranty are excluded. The report retains these as unknown rather than zero. It does not change the selected reference or the procurement BOM.",
        "",
        f"Source hashes, line-level span identities, account links and all six regional/hour cases per span are in [{OUTPUT_FILE}]({OUTPUT_FILE}). The exact source inputs are recorded in [manifest.json](manifest.json).",
        "",
    ]
    return "\n".join(lines)


def _write(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".pending")
    temp.write_bytes(payload)
    temp.replace(path)


def publish_packet(root=REPOSITORY_ROOT, output=None):
    root = Path(root).resolve()
    target = root / OUTPUT_DIR if output is None else Path(output).expanduser().resolve()
    if target.is_symlink():
        raise ValueError("Rebar screen output must not be a symlink")
    if target.exists() and any(target.iterdir()):
        manifest_path = target / "manifest.json"
        if not manifest_path.is_file():
            raise ValueError("Existing rebar output is not an owned publication")
        old = _read(manifest_path)
        if (old.get("schema") != "osr-federated-span-rebar-publication/1"
                or old.get("publication_id") != identity({
                    key: value for key, value in old.items() if key != "publication_id"})):
            raise ValueError("Existing rebar screen publication identity differs")
    packet = build_packet(root)
    readme = render_readme(packet)
    payload_bytes = encoded(packet)
    manifest = {
        "schema": "osr-federated-span-rebar-publication/1",
        "packet_id": packet["packet_id"],
        "input_sha256": packet["input_sha256"],
        "files_sha256": {
            "README.md": sha256(readme.encode("utf-8")).hexdigest(),
            OUTPUT_FILE: sha256(payload_bytes).hexdigest(),
        },
        "unknown_is_zero": False,
        "complete_fabrication_cost_iqd": None,
        "installed_cost_iqd": None,
        "whole_life_cost_iqd": None,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_accepted": False,
    }
    manifest["publication_id"] = identity(manifest)
    _write(target / "README.md", readme.encode("utf-8"))
    _write(target / OUTPUT_FILE, payload_bytes)
    _write(target / "manifest.json", encoded(manifest))
    return verify_packet(root=root, output=target)


def verify_packet(root=REPOSITORY_ROOT, output=None):
    root = Path(root).resolve()
    target = root / OUTPUT_DIR if output is None else Path(output).expanduser().resolve()
    manifest = _read(target / "manifest.json")
    if (manifest.get("schema") != "osr-federated-span-rebar-publication/1"
            or manifest.get("publication_id") != identity({
                key: value for key, value in manifest.items() if key != "publication_id"})):
        raise ValueError("Rebar screen publication identity differs")
    packet = build_packet(root)
    if (manifest.get("packet_id") != packet["packet_id"]
            or manifest.get("input_sha256") != packet["input_sha256"]
            or _read(target / OUTPUT_FILE) != packet
            or (target / "README.md").read_text() != render_readme(packet)
            or manifest.get("files_sha256") != {
                "README.md": _hash(target / "README.md"),
                OUTPUT_FILE: _hash(target / OUTPUT_FILE)}):
        raise ValueError("Rebar screen output does not reproduce from current sources")
    if (manifest.get("unknown_is_zero") is not False
            or any(manifest.get(key) is not False for key in
                   ("engineering_accepted", "procurement_approved", "physical_accepted"))):
        raise ValueError("Rebar screen cannot approve the railway")
    return {
        "verified": True,
        "publication_id": manifest["publication_id"],
        "packet_id": packet["packet_id"],
        "candidate_id": packet["candidate_id"],
        "span_count": packet["span_count"],
        "reinforcement_mass_proxy_t": packet["reinforcement_mass_proxy_t"],
        "scenario_count": len(packet["network_scenarios"]),
        "complete_fabrication_cost_iqd": None,
        "installed_cost_iqd": None,
        "physical_accepted": False,
    }
