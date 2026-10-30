"""Source-bound local-labour GFRP material cost screens.

The packet combines the listed GBP material extensions from three exact 10 m²
laminate studies with a dated CBI GBP/IQD reference rate and an explicit CSO
Baghdad base wage.  Unpriced core/adhesive and other process scope remain open;
the resulting amount is a partial scenario, never a complete fabrication cost.
"""
from argparse import ArgumentParser
from decimal import Decimal, ROUND_HALF_EVEN
import gzip
import hashlib
import json
from pathlib import Path

from . import catalogue, inputs
from .model import encoded, identity

ROOT = Path(__file__).resolve().parents[2]
HOURS = ("8", "16", "32")
RECIPES = ("solid-600gsm", "sandwich-600gsm", "higher-fibre-sandwich-600gsm")
PACKET_PATHS = {key: Path("docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v2") / key
                for key in RECIPES}
CENT = Decimal("0.01")


def _read(path):
    path = Path(path)
    raw = path.read_bytes()
    if path.name.endswith(".gz"):
        raw = gzip.decompress(raw)
    return json.loads(raw)


def _packet(path, current_base_records, expected_study_candidates):
    folder = Path(path)
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Regular source-bound laminate publication required: " + str(folder))
    manifest = _read(folder / "manifest.json")
    expected_files = set(manifest.get("files", {}))
    required_files = {"catalogue.json.gz", "erp-drafts.json.gz", "input.json.gz", "records.json.gz",
                      "request.json", "result.json.gz", "sources.tar.gz", "summary.json"}
    if expected_files != required_files:
        raise ValueError("Laminate publication file inventory differs")
    for name, descriptor in manifest["files"].items():
        file = folder / name
        if file.is_symlink() or not file.is_file() or file.stat().st_size != descriptor["bytes"]:
            raise ValueError("Laminate publication file size/type differs: " + name)
        if hashlib.sha256(file.read_bytes()).hexdigest() != descriptor["sha256"]:
            raise ValueError("Laminate publication file hash differs: " + name)
    summary = _read(folder / "summary.json")
    result = _read(folder / "result.json.gz")
    records = _read(folder / "records.json.gz")
    source_snapshot = _read(folder / "catalogue.json.gz")
    current_by_id = {row["record_id"]: row for row in current_base_records}
    saved_rows = source_snapshot.get("records", [])
    saved_by_id = {row.get("record_id"): row for row in saved_rows}
    extra_rows = [row for record_id, row in saved_by_id.items() if record_id not in current_by_id]
    expected_process_ids = {row.get("process_id") for row in records.get("requirements", [])}
    extra_candidates = {row.get("candidate_id") for row in extra_rows}
    if (source_snapshot.get("schema") != "osr-sourcing-input-catalogue/1"
            or source_snapshot.get("snapshot_id") != identity({k: v for k, v in source_snapshot.items()
                                                                 if k != "snapshot_id"})
            or any(saved_by_id.get(record_id) != row for record_id, row in current_by_id.items())
            or len(extra_rows) != len(expected_study_candidates)
            or extra_candidates != set(expected_study_candidates)
            or any(row.get("kind") != "process"
                   or row.get("process_key") != "laminate-material-requirements"
                   or row.get("complete_installed_cost") is not None
                   or row.get("unknown_is_zero") is not False
                   for row in extra_rows)
            or any(record_id != next(row["record_id"] for row in extra_rows
                                     if row.get("candidate_id") == manifest.get("candidate_id"))
                   for record_id in expected_process_ids)
            or source_snapshot.get("snapshot_id") != identity(dict(
                schema="osr-sourcing-input-catalogue/1",
                records=sorted(current_base_records + extra_rows, key=lambda row: row["record_id"])) )):
        raise ValueError("Laminate study does not use the current exact source observation epoch")
    if (manifest.get("schema") != "osr-sourcing-publication/1"
            or manifest.get("execution") != "completed"
            or manifest.get("publication_id") != identity({k: v for k, v in manifest.items()
                                                             if k != "publication_id"})
            or summary.get("run_id") != manifest.get("run_id")
            or summary.get("candidate_id") != manifest.get("candidate_id")
            or result.get("record_id") != manifest.get("run_id")
            or result.get("candidate_id") != manifest.get("candidate_id")
            or records.get("run", {}).get("record_id") != manifest.get("run_id")
            or summary.get("complete_installed_cost") is not None
            or summary.get("unknown_is_zero") is not False
            or manifest.get("complete_installed_cost") is not None
            or manifest.get("physical_accepted") is not False):
        raise ValueError("Laminate study identity or release boundary differs")
    return dict(path=folder, manifest=manifest, summary=summary, result=result, records=records)


def _money(value):
    return str(Decimal(value).quantize(CENT, rounding=ROUND_HALF_EVEN))


def _build(records, packet_root, *, labour_hours=HOURS):
    by_kind = {}
    for record in records:
        by_kind.setdefault(record["kind"], []).append(record)
    benchmarks = {row["benchmark_key"]: row for row in by_kind.get("benchmark", [])}
    source_keys = {row["record_id"]: row["source_key"] for row in by_kind.get("source", [])}
    base_records = sorted((row for row in records if row["kind"] in
                           {"source", "product", "offer", "fx", "benchmark", "process"}),
                          key=lambda row: row["record_id"])
    packet_root = Path(packet_root)
    expected_study_candidates = {
        _read(packet_root / recipe / "manifest.json")["candidate_id"] for recipe in RECIPES
    }
    fx_rows = [row for row in by_kind.get("fx", [])
               if source_keys.get(row.get("source_id")) == "iraq-cbi-daily-fx"
               and row.get("base_currency") == "GBP" and row.get("quote_currency") == "IQD"
               and row.get("rate_date") == "2026-10-29"]
    if len(fx_rows) != 1 or fx_rows[0].get("executable_transaction_rate") is not False:
        raise ValueError("Exact dated non-executable CBI GBP/IQD reference is required")
    fx = fx_rows[0]
    wage_key = "iq-cso-2025-regional:baghdad:wage:skilled:hour-8h-day"
    wage = benchmarks.get(wage_key)
    if wage is None or wage.get("is_manufactured_product_price") is not False:
        raise ValueError("Exact CSO Baghdad skilled-worker wage benchmark required")
    if wage.get("currency") != "IQD" or wage.get("quantity_unit") != "h":
        raise ValueError("Wage benchmark must be normalized to IQD/person-hour")

    studies = []
    for recipe in RECIPES:
        study = _packet(packet_root / recipe, base_records, expected_study_candidates)
        if study["manifest"].get("source_sha256") != study["result"].get("source_sha256"):
            raise ValueError("Laminate publication source revision differs")
        requirements = {row["record_id"]: row for row in study["records"].get("requirements", [])}
        assessments = study["records"].get("price_assessments", [])
        by_requirement = {}
        for row in assessments:
            if row.get("listed_extension_usable_for_candidate_scope") is True:
                by_requirement.setdefault(row["requirement_id"], []).append(row)
        priced = []
        unresolved = []
        for requirement in requirements.values():
            rows = by_requirement.get(requirement["record_id"], [])
            if len(rows) > 1:
                raise ValueError("More than one listed price extension applies to a laminate requirement")
            if rows:
                assessment = rows[0]
                if (assessment.get("listed_extension_is_order_cost") is not False
                        or assessment.get("listed_extension_is_cost_bound") is not False
                        or assessment.get("listed_extension_currency") != "GBP"
                        or assessment.get("listed_extension_at_requested_quantity") is None):
                    raise ValueError("Expected a non-order listed material extension in GBP")
                priced.append(dict(
                    requirement_id=requirement["record_id"],
                    requirement_key=requirement["requirement_key"],
                    material_key=requirement.get("process_material_key"),
                    quantity=requirement.get("quantity"), quantity_unit=requirement.get("quantity_unit"),
                    product_key=assessment.get("product_key"), product_id=assessment.get("product_id"),
                    offer_id=assessment.get("offer_id"), price_source_id=assessment.get("source_id"),
                    price_date=assessment.get("source_price_date"),
                    listed_extension_gbp=assessment["listed_extension_at_requested_quantity"],
                    usable_as_order_cost=False, cost_bound=False,
                ))
            else:
                unresolved.append(dict(
                    requirement_id=requirement["record_id"],
                    requirement_key=requirement["requirement_key"],
                    material_key=requirement.get("process_material_key"),
                    quantity=requirement.get("quantity"), quantity_unit=requirement.get("quantity_unit"),
                    reason=("quantity-unresolved" if requirement.get("quantity") is None
                            else "no-compatible-priced-offer"),
                    known_material_mass_kg=requirement.get("net_quantity")
                    if requirement.get("quantity_unit") == "kg" else None,
                ))
        listed_gbp = sum((Decimal(row["listed_extension_gbp"]) for row in priced), Decimal(0))
        material_iqd = listed_gbp * Decimal(fx["rate"])
        per_hour = Decimal(wage["unit_price"])
        source_ids = sorted({fx["source_id"], wage["source_id"],
                             *(row["price_source_id"] for row in priced)})
        studies.append(dict(
            recipe=recipe,
            publication_id=study["manifest"]["publication_id"],
            run_id=study["manifest"]["run_id"],
            candidate_id=study["manifest"]["candidate_id"],
            parent_candidate_id=study["records"]["requirements"][0].get("parent_candidate_id"),
            input_payload_id=study["result"].get("input_payload_id"),
            listed_materials=priced,
            unresolved_materials=unresolved,
            listed_material_subtotal_gbp=str(listed_gbp),
            cbi_conversion_rate_iqd_per_gbp=fx["rate"],
            known_listed_material_subtotal_iqd=_money(material_iqd),
            scenarios=[dict(
                labour_hours_per_10m2=str(hours),
                base_wage_iqd_per_hour=str(per_hour),
                direct_labour_iqd=_money(Decimal(hours) * per_hour),
                direct_known_materials_plus_labour_iqd=_money(material_iqd + Decimal(hours) * per_hour),
                uplift_fraction="0.20",
                unallocated_uplift_iqd=_money((material_iqd + Decimal(hours) * per_hour) * Decimal("0.20")),
                partial_screen_iqd=_money((material_iqd + Decimal(hours) * per_hour) * Decimal("1.20")),
                complete_material_cost_iqd=None,
                complete_fabrication_cost_iqd=None,
                unknown_is_zero=False,
            ) for hours in labour_hours],
            source_ids=source_ids,
            complete_material_cost_iqd=None,
            complete_fabrication_cost_iqd=None,
            physical_qualification=None,
            engineering_accepted=False, procurement_approved=False,
            unknown_is_zero=False,
        ))

    source_hashes = {
        "engineering/sourcing/iraq_gfrp_cost_scenarios.py": inputs.digest(Path(__file__)),
        "engineering/sourcing/model.py": inputs.digest(ROOT / "engineering/sourcing/model.py"),
        "engineering/sourcing/catalogue.py": inputs.digest(ROOT / "engineering/sourcing/catalogue.py"),
        "engineering/sourcing/data/supplier-catalogue.json": inputs.digest(ROOT / "engineering/sourcing/data/supplier-catalogue.json"),
        "engineering/sourcing/data/public-feeds.json": inputs.digest(ROOT / "engineering/sourcing/data/public-feeds.json"),
    }
    for recipe in RECIPES:
        folder = packet_root / recipe
        for name in ("manifest.json", "summary.json", "result.json.gz", "records.json.gz",
                     "input.json.gz", "catalogue.json.gz", "request.json"):
            source_hashes[f"{recipe}/{name}"] = inputs.digest(folder / name)
    payload = dict(
        schema="osr-iraq-gfrp-local-fabrication-cost-screens/1",
        basis=dict(
            study_area_m2="10",
            material_basis="listed Easy Composites price extensions at each exact laminate requirement's requested quantity; order multiples and supplier order totals are not established",
            material_currency="GBP",
            fx_source_id=fx["source_id"], fx_record_id=fx["record_id"], fx_date=fx["rate_date"],
            fx_rate=fx["rate"], executable_fx=False,
            wage_source_id=wage["source_id"], wage_benchmark_id=wage["record_id"],
            wage_basis="2025 CSO Baghdad skilled-worker average normalized from a reported 8-hour day; base wage only, no employer burden",
            labour_scenarios_hours_per_10m2=list(labour_hours),
            formula="(known listed material extensions GBP × dated CBI GBP/IQD reference + assumed local base-wage labour hours × CSO hourly wage) × 1.20",
            uplift_fraction="0.20", uplift_scope="known listed materials plus assumed direct base-wage labour only; allowance allocation is unspecified",
        ),
        studies=studies,
        source_sha256=source_hashes,
        complete_material_cost_iqd=None, complete_fabrication_cost_iqd=None,
        complete_installed_cost_iqd=None, whole_life_cost_iqd=None,
        physical_qualification=None, engineering_accepted=False,
        procurement_approved=False, selected_reference_changed=False,
        unknown_is_zero=False,
        limitations=[
            "All three 10 m² laminate recipes are research material hypotheses, not roof CAD takeoffs or accepted vehicle structures.",
            "Listed supplier material extensions are not order totals, executable quotes or Iraq-delivered prices; FX uses the CBI dated selling reference and excludes channel spreads, fees, freight, insurance, customs and taxes.",
            "Local fabrication hours are declared sensitivity assumptions, not measured routes. The CSO wage is a base-wage benchmark and omits employer burden, supervision, utilities, equipment, tooling, moulds, consumables, scrap beyond the study takeoff, QA, rework and factory overhead.",
            "Core and adhesive requirements remain unpriced or unresolved and are not assigned zero cost. The 20% allowance applies only to listed materials plus assumed base wages and is not a verified markup.",
            "No rail fire/smoke/toxicity, fatigue, hot-wet, structural, manufacturing or physical qualification is implied; this packet cannot select or rank complete vehicle candidates.",
        ],
    )
    payload["catalogue_epoch_id"] = identity(records)
    payload["packet_id"] = identity(payload)
    return payload


def build(packet_root=None):
    root = ROOT if packet_root is None else Path(packet_root).resolve()
    records = catalogue.load_catalogue()
    return _build(records, root / "docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v2")


def main(argv=None):
    parser = ArgumentParser(description="Build partial Iraqi local-labour GFRP material cost screens")
    parser.add_argument("--packet-root", type=Path, required=True,
                        help="Directory containing the three exact laminate publication folders")
    parser.add_argument("--output", type=Path, required=True,
                        help="Fresh JSON output path")
    args = parser.parse_args(argv)
    records = catalogue.load_catalogue()
    payload = _build(records, args.packet_root.expanduser().resolve())
    path = args.output.expanduser().resolve()
    if path.exists() or path.is_symlink():
        raise ValueError("Fresh GFRP cost-screen output required: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(payload) + b"\n")
    print(json.dumps(dict(output=str(path), packet_id=payload["packet_id"],
                          scenarios=sum(len(row["scenarios"]) for row in payload["studies"]),
                          complete_fabrication_cost_iqd=None, physical_qualification=None), indent=2))


if __name__ == "__main__":
    main()
