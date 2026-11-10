"""Price defensible Samawah candidate quantity fragments from a retained ratebook.

This is deliberately not a project estimator: inherited Class-C rates are
reapplied only to named, dimensionally matching quantities. The old physical
candidate is never carried into the new candidate record.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

from engineering.station_rail.common import digest, encoded, identity
from engineering.railway_project.city_recalculation import verify as verify_city

ROOT = Path(__file__).resolve().parents[2]
CITY_RESULT = Path("docs/design-engine/v06-design-closure/samawah-city-recalculation/result.json")
RATE_PACKET = Path("docs/design-engine/v06-design-closure/samawah-china-supply-cost-04")
CASES = ("low", "base", "high")

# These mappings retain both the rate source's engineering basis and the new
# quantity unit. They are scenario rates, not offers or locally verified data.
RATE_LINES = {
    "route-running-rails": ("guideway", "kg", "60E1 rail mass"),
    "route-complete-fasteners": ("guideway", "sets", "complete fastening sets"),
    "repeat-box-beams": ("guideway", "spans", "20 m repeat box beam units"),
    "bearing-pads": ("guideway", "spans", "beam units receiving bearing pads"),
    "beam-joints-drains-lifting": ("guideway", "spans", "beam units receiving joint/drain/lifting package"),
}


def _read_json(path: Path):
    return json.loads(path.read_bytes())


def _verify_packet(packet: Path, *, manifest_override: dict | None = None) -> dict:
    manifest = _read_json(packet / "manifest.json") if manifest_override is None else manifest_override
    if manifest.get("schema") != "osr-samawah-china-bulk-cost-packet/1":
        raise ValueError("Unexpected retained Samawah rate packet schema")
    expected = manifest.get("files_sha256", {})
    if len(expected) != manifest.get("file_count"):
        raise ValueError("Retained rate packet file count mismatch")
    for name, want in expected.items():
        rel = Path(name)
        if rel.is_absolute() or ".." in rel.parts or rel.as_posix() != name:
            raise ValueError("Unsafe retained packet path")
        if digest(packet / rel) != want:
            raise ValueError("Retained rate packet content hash mismatch: " + name)
    if manifest.get("manifest_id") != identity({k: v for k, v in manifest.items() if k != "manifest_id"}):
        raise ValueError("Retained rate packet manifest identity mismatch")
    return manifest


def build(city_result: dict, old_cost: dict, old_manifest: dict, *, source_sha256: dict) -> dict:
    verify_city(city_result)
    if old_cost.get("evaluation_id") != identity({k: v for k, v in old_cost.items() if k != "evaluation_id"}):
        raise ValueError("Retained ratebook cost identity mismatch")
    city_id = city_result["source_city_input_id"]
    if old_cost.get("city_input_id") != city_id:
        raise ValueError("Ratebook and candidate must share the exact authenticated city input")
    old_candidate_ids = old_manifest.get("candidate_ids", {})
    if old_candidate_ids.get("candidate_id") == city_result["candidate_id"] or old_candidate_ids.get("body_candidate_id") == city_result["body_candidate_id"]:
        raise ValueError("Ratebook candidate identity must remain distinct from the priced candidate")

    old_rows = {r.get("key"): r for r in old_cost.get("capital_lines", [])}
    current_q = city_result["quantities"]
    # 60E1 is the explicit source rail profile. The input route quantities are
    # four rail rows per mapped route metre (two tracks, two running rails).
    rail_length_m = current_q["running_rail_m"]
    rail_mass_kg = rail_length_m * 60.0
    quantities = {
        "route-running-rails": (rail_mass_kg, "kg"),
        "route-complete-fasteners": (current_q["running_fastening_sets"], "sets"),
        "repeat-box-beams": (current_q["standard_beams"], "spans"),
        "bearing-pads": (current_q["standard_beams"], "spans"),
        "beam-joints-drains-lifting": (current_q["standard_beams"], "spans"),
    }
    lines = []
    for key, (scope, unit, description) in RATE_LINES.items():
        row = old_rows.get(key)
        if row is None or row.get("scope") != scope or row.get("source_class") != "C":
            raise ValueError("Expected Class-C source row missing or changed: " + key)
        source_q = row.get("quantity", {}).get(unit)
        if type(source_q) not in (int, float) or source_q <= 0:
            raise ValueError("Source rate quantity is not a positive matching unit: " + key)
        quantity, current_unit = quantities[key]
        if current_unit != unit or type(quantity) not in (int, float) or quantity <= 0:
            raise ValueError("Candidate quantity/unit mismatch: " + key)
        costs = row.get("costs_usd", {})
        rates = {case: costs[case] / source_q for case in CASES}
        line_costs = {case: quantity * rates[case] for case in CASES}
        lines.append({
            "line_id": identity({"candidate_id": city_result["candidate_id"], "body_candidate_id": city_result["body_candidate_id"], "key": key, "quantity": quantity, "unit": unit, "ratebook_line_id": row["line_id"]}),
            "scope": scope,
            "key": key,
            "description": description,
            "candidate_id": city_result["candidate_id"],
            "body_candidate_id": city_result["body_candidate_id"],
            "body_evaluation_id": city_result["body_evaluation_id"],
            "quantity": quantity,
            "unit": unit,
            "ratebook_quantity": source_q,
            "rate_usd_per_unit": rates,
            "cost_usd": line_costs,
            "rate_source_line_id": row["line_id"],
            "rate_source_candidate_id": old_candidate_ids["candidate_id"],
            "rate_source_body_candidate_id": old_candidate_ids["body_candidate_id"],
            "rate_class": "C",
            "basis": row["basis"],
            "limitations": [
                "Historical unquoted scenario rate transferred by matching quantity unit; not a supplier offer or local valuation.",
                "The source beam section and load basis are not verified against this detailed body candidate.",
                "Rate multiplication prices this named fragment only; it does not complete the scope or city project.",
            ],
        })

    fragment_totals = {case: sum(line["cost_usd"][case] for line in lines) for case in CASES}
    bom = city_result["known_counted_BOM_process_subtotal_usd"]
    # Use the exact previously sealed per-train direct-BOM figure, rather than
    # deriving a cross-case average from a different scenario's train count.
    body_path = ROOT / "docs/design-engine/v06-design-closure/compact-drive-corridor/body.json.gz"
    body = json.loads(gzip.decompress(body_path.read_bytes()))
    if body.get("candidate_id") != city_result["body_candidate_id"] or body.get("evaluation_id") != city_result["body_evaluation_id"]:
        raise ValueError("Candidate BOM source does not match city recalculation body identity")
    direct_per_train = {case: body["direct_parts_process_usd"][case] for case in CASES}
    fleet = city_result["fleet_request_cases"]
    priced_scope_fragments = {
        "rolling-stock": {case: fleet[case]["active_trainsets"] * direct_per_train[case] for case in CASES},
        "fleet": {case: fleet[case]["spare_trainsets"] * direct_per_train[case] for case in CASES},
    }
    all_scope_status = {scope: "unpriced_or_incomplete" for scope in old_cost["scope_totals_usd"]}
    all_scope_status.update({"rolling-stock": "counted_BOM_process_subtotal_only", "fleet": "counted_BOM_process_subtotal_only", "guideway": "selected_quantity_fragments_only"})
    result = {
        "schema": "osr-samawah-candidate-cost-bridge/1",
        "city_candidate_id": city_result["candidate_id"],
        "body_candidate_id": city_result["body_candidate_id"],
        "body_evaluation_id": city_result["body_evaluation_id"],
        "city_input_id": city_id,
        "source_city_recalculation_evaluation_id": city_result["evaluation_id"],
        "ratebook_packet_id": old_manifest["manifest_id"],
        "ratebook_source_candidate_id": old_candidate_ids["candidate_id"],
        "ratebook_source_body_candidate_id": old_candidate_ids["body_candidate_id"],
        "ratebook_is_physical_parent": False,
        "currency": "USD",
        "price_class": "C historical transferred scenario rates; not local rates, quotes, or validated market prices",
        "quantity_basis": {
            "route_m": current_q["route_m"],
            "running_rail_m": rail_length_m,
            "rail_mass_kg_at_60E1_60kg_per_m": rail_mass_kg,
            "fastening_sets": current_q["running_fastening_sets"],
            "20m_beam_units": current_q["standard_beams"],
            "double_track_installation_track_m": 2.0 * current_q["route_m"],
            "trainsets_by_case": {case: city_result["fleet_request_cases"][case]["total_trainsets"] for case in CASES},
            "all_from_exact_candidate_recalculation": True,
        },
        "matched_rate_lines": lines,
        "known_candidate_bom_subtotal_usd": bom,
        "partial_matched_guideway_subtotal_usd": fragment_totals,
        "partial_priced_fragment_sum_usd": {case: bom[case] + fragment_totals[case] for case in CASES},
        "partial_scope_fragments_usd": priced_scope_fragments,
        "scope_status": all_scope_status,
        "installed_capex_usd": None,
        "whole_life_npv_usd": None,
        "cost_complete": False,
        "service_complete": False,
        "engineering_accepted": False,
        "physical_accepted": False,
        "manufacturing_release": False,
        "operating_release": False,
        "movement_authority": False,
        "unpriced_or_unresolved": [
            "Exact-body force/braking, grade, detailed civil loads and station geometry.",
            "Support, foundation, ground, land, utilities, depot, station access, power, charging and protection quantities.",
            "Local wage/material rates, import duties/customs, tax treatment, exchange rate and current supplier quotations.",
            "Production tooling/factory scale, final assembly, test/commissioning, staffing and construction programme.",
            "Traction energy, operations, maintenance, renewals, recovery, reliability, disposal and financing inputs.",
            "Potential mismatch between historical 20 m beam design and current body loads; the rate does not validate the beam selection.",
            "Construction haul/crane/erection rates are not transferred because the retained line mixes mainline and station track quantities absent from this candidate quantity set.",
        ],
        "source_sha256": dict(sorted(source_sha256.items())),
    }
    result["evaluation_id"] = identity(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    city_result = _read_json(ROOT / CITY_RESULT)
    packet = ROOT / RATE_PACKET
    manifest = _verify_packet(packet)
    old_cost = _read_json(packet / "cost-project-make-buy.json")
    sources = {
        CITY_RESULT.as_posix(): digest(ROOT / CITY_RESULT),
        (RATE_PACKET / "manifest.json").as_posix(): digest(packet / "manifest.json"),
        (RATE_PACKET / "cost-project-make-buy.json").as_posix(): digest(packet / "cost-project-make-buy.json"),
        "docs/design-engine/v06-design-closure/compact-drive-corridor/body.json.gz": digest(ROOT / "docs/design-engine/v06-design-closure/compact-drive-corridor/body.json.gz"),
        "engineering/railway_project/city_cost_bridge.py": digest(ROOT / "engineering/railway_project/city_cost_bridge.py"),
        "engineering/railway_project/city_recalculation.py": digest(ROOT / "engineering/railway_project/city_recalculation.py"),
        "engineering/station_rail/common.py": digest(ROOT / "engineering/station_rail/common.py"),
    }
    result = build(city_result, old_cost, manifest, source_sha256=sources)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as f:
        f.write(encoded(result))
    print(json.dumps({"evaluation_id": result["evaluation_id"], "city_candidate_id": result["city_candidate_id"],
        "matched_rate_lines": len(result["matched_rate_lines"]), "cost_complete": result["cost_complete"],
        "partial_priced_fragment_sum_usd": result["partial_priced_fragment_sum_usd"]}, sort_keys=True))


if __name__ == "__main__":
    main()
