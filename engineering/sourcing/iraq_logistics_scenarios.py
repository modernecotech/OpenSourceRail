"""Source-bound Iraqi rental-cost sensitivities for concrete span packages.

The output is a conditional cost screen only. It preserves source package and
occurrence identities, never assumes transport or crane capacity, and keeps the
rental subtotal separate from domestic material + labour + 20% estimates.
"""
from argparse import ArgumentParser
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_EVEN
import json
from pathlib import Path

from . import catalogue, inputs
from .model import encoded, identity

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "engineering/sourcing/data/iraq-transport-rental-2026-09.json"
CENT = Decimal("0.01")
SCENARIOS = (
    ("screen-one-trip-one-day-per-span", 1, 1),
    ("screen-two-trips-one-day-per-span", 2, 1),
    ("screen-one-trip-two-days-per-span", 1, 2),
    ("screen-two-trips-two-days-per-span", 2, 2),
)


def _read(path):
    return inputs.read_json(path)


def build_packet(source_records, procurement, regional_cost, *,
                 procurement_path, regional_cost_path, source_seed_path=SEED):
    if not isinstance(procurement, dict) or procurement.get("schema") != "osr-procurement-package-bom/1":
        raise ValueError("Exact current procurement BOM packet required")
    if not isinstance(regional_cost, dict) or regional_cost.get("schema") != "osr-iraq-domestic-cost-reference/2":
        raise ValueError("Exact current regional domestic-cost packet required")
    if procurement.get("candidate_id") != regional_cost.get("candidate_id"):
        raise ValueError("Procurement and regional cost candidates differ")
    if procurement.get("source_input_id") != regional_cost.get("source_input_id"):
        raise ValueError("Procurement and regional cost inputs differ")
    if procurement.get("complete_installed_cost") is not None or regional_cost.get("complete_installed_cost") is not None:
        raise ValueError("Complete installed cost must remain unresolved")

    concrete = [row for row in procurement.get("packages", [])
                if row.get("package_family") == "civil-concrete-stock-package"]
    if len(concrete) != 81 or any(row.get("candidate_id") != procurement["candidate_id"]
                                  or row.get("source_input_id") != procurement["source_input_id"]
                                  for row in concrete):
        raise ValueError("Expected 81 concrete packages from one candidate/input")
    if len({row.get("package_key") for row in concrete}) != len(concrete):
        raise ValueError("Concrete package keys must be unique")
    occurrence_ids = [oid for row in concrete for oid in row.get("engineering_occurrence_ids", [])]
    if len(occurrence_ids) != 486 or len(set(occurrence_ids)) != 486:
        raise ValueError("Concrete package occurrences must preserve the exact 486 source IDs")
    if len({row.get("engineering_occurrence_count") for row in concrete}) != 1 or concrete[0]["engineering_occurrence_count"] != 6:
        raise ValueError("Concrete package occurrence count differs from the declared twin inventory")

    sources = {row["source_key"]: row for row in source_records if row["kind"] == "source"}
    benchmarks = {row["benchmark_key"]: row for row in source_records if row["kind"] == "benchmark"}
    source = sources.get("iraq.fao.contracts-rental-2026-09")
    trailer = benchmarks.get("iraq-fao-contract-2026-09:trailer-trip")
    crane = benchmarks.get("iraq-fao-contract-2026-09:crane-day")
    if (source is None or source.get("source_kind") != "awarded_bid"
            or trailer is None or crane is None
            or trailer.get("source_id") != source["record_id"]
            or crane.get("source_id") != source["record_id"]
            or trailer.get("currency") != "IQD" or crane.get("currency") != "IQD"
            or trailer.get("quantity_unit") != "each" or crane.get("quantity_unit") != "each"
            or trailer.get("is_manufactured_product_price") is not False
            or crane.get("is_manufactured_product_price") is not False):
        raise ValueError("The exact two Iraqi rental benchmark records are required")

    trip_rate = Decimal(trailer["unit_price"])
    crane_rate = Decimal(crane["unit_price"])
    span_count = len(concrete)
    scenario_rows = []
    for scenario_key, trips_per_package, crane_days_per_package in SCENARIOS:
        trips = span_count * trips_per_package
        crane_days = span_count * crane_days_per_package
        trailer_extension = trip_rate * trips
        crane_extension = crane_rate * crane_days
        scenario_rows.append({
            "scenario_key": scenario_key,
            "assumption_scope": "conditional arithmetic scale check; trips and crane-days are not an approved transport/erection plan",
            "trailer_trips_per_span_package": trips_per_package,
            "crane_days_per_span_package": crane_days_per_package,
            "span_package_count": span_count,
            "assumed_trailer_trip_count": trips,
            "assumed_crane_day_count": crane_days,
            "trailer_rate_benchmark_id": trailer["record_id"],
            "trailer_unit_rate_iqd_per_trip": str(trip_rate),
            "trailer_extension_iqd": str(trailer_extension),
            "crane_rate_benchmark_id": crane["record_id"],
            "crane_unit_rate_iqd_per_day": str(crane_rate),
            "crane_extension_iqd": str(crane_extension),
            "conditional_logistics_subtotal_iqd": str(trailer_extension + crane_extension),
            "uplift_fraction": "0",
            "uplift_reason": "Rental rates are treated as observed operation-rate benchmarks; no domestic fabrication 20% allowance is applied to these separate rates.",
            "complete_transport_or_erection_cost": None,
            "physical_lift_capacity_verified": False,
            "route_distance_verified": False,
            "availability_confirmed": False,
        })

    material_labour_rows = []
    for row in regional_cost.get("regional_concrete_takeoff_estimates", []):
        material_labour_rows.append({
            "region": row["region"],
            "labour_hours_per_nominal_m3": row["labour_hours_per_nominal_m3"],
            "material_labour_plus_20_iqd": row["estimated_total_iqd"],
            "estimate_packet_id": row["estimate_packet_id"],
            "scope": "separate existing material + assumed direct labour + 20% sensitivity; not a guideway beam price",
        })
    if len(material_labour_rows) != 6:
        raise ValueError("Six regional material + labour estimates required for the separated subtotal")

    payload = {
        "schema": "osr-iraq-span-logistics-sensitivity/1",
        "candidate_id": procurement["candidate_id"],
        "source_input_id": procurement["source_input_id"],
        "evaluation_id": procurement.get("evaluation_id"),
        "takeoff_id": regional_cost.get("takeoff_id"),
        "procurement_bom_packet_id": procurement.get("packet_id"),
        "regional_cost_packet_id": regional_cost.get("packet_id"),
        "regional_source_epoch_id": regional_cost.get("source_epoch_id"),
        "rental_source_epoch_id": identity(source_records),
        "rental_source_id": source["record_id"],
        "rental_benchmark_ids": [trailer["record_id"], crane["record_id"]],
        "rental_rate_evidence": {
            "contract_number": "18",
            "contract_date": "2026-09-27",
            "source_url": source["url"],
            "trailers_listed": 6,
            "crane_count_listed": 1,
            "trailer_rate_iqd_per_trip": str(trip_rate),
            "crane_rate_iqd_per_day": str(crane_rate),
            "not_a_quote_or_capacity_proof": True,
        },
        "span_package_count": span_count,
        "span_package_keys": sorted(row["package_key"] for row in concrete),
        "engineering_occurrence_count": len(occurrence_ids),
        "engineering_occurrence_ids": sorted(occurrence_ids),
        "logistics_scenarios": scenario_rows,
        "separate_material_labour_20_scenarios": material_labour_rows,
        "combined_partial_subtotals": [
            {
                "region": material["region"],
                "material_labour_hours_per_nominal_m3": material["labour_hours_per_nominal_m3"],
                "material_labour_plus_20_iqd": material["material_labour_plus_20_iqd"],
                "logistics_scenario_key": logistics["scenario_key"],
                "conditional_logistics_subtotal_iqd": logistics["conditional_logistics_subtotal_iqd"],
                "conditional_partial_subtotal_iqd": str(Decimal(material["material_labour_plus_20_iqd"])
                                                          + Decimal(logistics["conditional_logistics_subtotal_iqd"])),
                "scope": "conditional sum of partial concrete material/labour screen and assumed trailer/crane rentals only; not complete beam, civil or installed cost",
            }
            for material in material_labour_rows for logistics in scenario_rows
        ],
        "package_trace": [
            {
                "package_key": row["package_key"],
                "package_id": row["package_id"],
                "engineering_occurrence_ids": sorted(row["engineering_occurrence_ids"]),
                "engineering_occurrence_count": row["engineering_occurrence_count"],
            }
            for row in sorted(concrete, key=lambda value: value["package_key"])
        ],
        "assumptions_and_open_scope": [
            "One nominal concrete stock package is not proof of one transportable beam or lift.",
            "Trip counts and crane-day counts are declared sensitivities, not quantities from a transport plan.",
            "The source does not publish trailer payload/dimensions, route distance, crane model/capacity/radius, mobilisation, fuel, tax or current availability.",
            "No crane load-chart check, foundation design, erection method, traffic control, utility relocation, installation crew, QA or maintenance is included.",
            "The 20% uplift remains applied only to the separate material + assumed direct labour screen; it is not re-applied to trailer/crane rental rates.",
        ],
        "complete_procurement_cost": None,
        "complete_process_cost": None,
        "complete_installed_cost": None,
        "whole_life_cost": None,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_qualification": None,
        "selected_reference_changed": False,
        "unknown_is_zero": False,
        "input_sha256": {
            "rental_seed": inputs.digest(source_seed_path),
            "procurement_bom": inputs.digest(procurement_path),
            "regional_cost_reference": inputs.digest(regional_cost_path),
        },
    }
    payload["packet_id"] = identity(payload)
    return payload


def publish_packet(packet, output):
    destination = Path(output).expanduser().resolve()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Fresh logistics sensitivity output directory required: " + str(destination))
    destination.mkdir(parents=True)
    path = destination / "iraq-span-logistics-sensitivity.json"
    path.write_bytes(encoded(packet) + b"\n")
    lines = [
        "# Iraqi span logistics sensitivity",
        "",
        "This packet links the Fa'o General Engineering contract-row rental observations to the exact 81 concrete stock packages and 486 engineering occurrence IDs in one research candidate.",
        "",
        "It is a conditional arithmetic sensitivity. A nominal stock package is not an approved beam, one-trip load or one-day lift. The source gives no trailer payload, route distance, crane configuration, load chart, mobilisation, fuel, taxes or availability.",
        "",
        "The first scenario assumes one trailer trip and one crane rental day per nominal span package: 81 trips × IQD 1,150,000 + 81 days × IQD 500,000 = IQD 133,650,000. This is not a verified transport/erection plan.",
        "",
        "The separate material + assumed direct labour + 20% estimates remain separate. The 20% is not applied to the rental rates. Combined partial subtotals include only those declared scopes and do not represent a guideway-beam, complete civil or installed cost.",
        "",
        "Complete procurement and installed cost remain unknown; no equipment or physical qualification is approved.",
        "",
        "See `iraq-span-logistics-sensitivity.json` and `manifest.json` for source and candidate identities.",
        "",
    ]
    (destination / "README.md").write_text("\n".join(lines), encoding="utf-8")
    files = {item.name: inputs.digest(item) for item in (path, destination / "README.md")}
    manifest = {
        "schema": "osr-iraq-span-logistics-sensitivity-publication/1",
        "packet_id": packet["packet_id"],
        "candidate_id": packet["candidate_id"],
        "source_input_id": packet["source_input_id"],
        "takeoff_id": packet["takeoff_id"],
        "procurement_bom_packet_id": packet["procurement_bom_packet_id"],
        "regional_cost_packet_id": packet["regional_cost_packet_id"],
        "rental_source_id": packet["rental_source_id"],
        "rental_benchmark_ids": packet["rental_benchmark_ids"],
        "files_sha256": files,
        "complete_installed_cost": None,
        "physical_qualification": None,
        "unknown_is_zero": False,
    }
    manifest["manifest_id"] = identity(manifest)
    (destination / "manifest.json").write_bytes(encoded(manifest) + b"\n")
    return {"output": str(destination), "packet_id": packet["packet_id"],
            "manifest_id": manifest["manifest_id"],
            "span_package_count": packet["span_package_count"],
            "scenario_count": len(packet["logistics_scenarios"]),
            "complete_installed_cost": None}


def main(argv=None):
    parser = ArgumentParser(description="Build an Iraqi trailer/crane rental sensitivity over exact concrete stock packages")
    parser.add_argument("--procurement-bom", type=Path, required=True)
    parser.add_argument("--regional-cost-reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Fresh output directory")
    args = parser.parse_args(argv)
    procurement = _read(args.procurement_bom)
    regional = _read(args.regional_cost_reference)
    source_records = catalogue.load_catalogue([SEED])
    packet = build_packet(source_records, procurement, regional,
                          procurement_path=args.procurement_bom,
                          regional_cost_path=args.regional_cost_reference)
    print(json.dumps(publish_packet(packet, args.output), indent=2))
    return 0


if __name__ == "__main__":
    main()
