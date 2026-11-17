#!/usr/bin/env python3
"""Compile the v0.7 joined candidate's bounded digital production handoff."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCES = {
    "joined_candidate": "docs/reference-v07/integration/candidate.toml",
    "planning_concept": "docs/reference-v07/concept.toml",
    "bom": "docs/reference-v07/manufacturing/bom.csv",
    "routing": "docs/reference-v07/manufacturing/routing.csv",
    "lifecycle": "docs/reference-v07/manufacturing/lifecycle-draft.json",
    "cost_basis": "docs/reference-v07/cost/basis.csv",
    "cost_programme": "docs/reference-v07/cost/README.md",
    "digital_vehicle_input": "docs/reference-v07/digital/vehicle/input.json",
    "digital_vehicle_result": "docs/reference-v07/digital/vehicle/result.json",
    "digital_civil_input": "docs/reference-v07/digital/civil/input.json",
    "digital_civil_result": "docs/reference-v07/digital/civil/result.json",
    "generator": "docs/reference-v07/digital/production/generate.py",
}
D = Decimal


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / SOURCES[name]).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def scope_for(row: dict[str, str]) -> str:
    assembly, item = row["assembly"], row["item"]
    if assembly in {"17m-powered-car", "door-opening"}:
        return "rolling-stock-and-vehicle-interfaces"
    if assembly == "10m-beam":
        if item == "haul-lift-placement":
            return "span-haul-and-erection"
        if item == "ordinary-pier-footing-position":
            return "piers-foundations-and-groundworks"
        return "guideway-beams-bearings-and-detail"
    if assembly == "station-power-site":
        if item == "station-auxiliary-grid-feed":
            return "auxiliary-charging-and-grid"
        if item == "independent-safety-brake":
            return "launch-machinery-and-converters"
        return "traction-grid-and-protection"
    raise ValueError(f"Unmapped BOM assembly {assembly}/{item}")


def compile_handoff() -> dict:
    joined = tomllib.loads((ROOT / SOURCES["joined_candidate"]).read_text())
    concept = tomllib.loads((ROOT / SOURCES["planning_concept"]).read_text())
    lifecycle = json.loads((ROOT / SOURCES["lifecycle"]).read_text())
    vehicle_input = json.loads((ROOT / SOURCES["digital_vehicle_input"]).read_text())
    vehicle_result = json.loads((ROOT / SOURCES["digital_vehicle_result"]).read_text())
    civil_input = json.loads((ROOT / SOURCES["digital_civil_input"]).read_text())
    civil_result = json.loads((ROOT / SOURCES["digital_civil_result"]).read_text())
    bom, routing, cost = read_csv("bom"), read_csv("routing"), read_csv("cost_basis")
    require(joined["physical_candidate_id"] == lifecycle["joined_physical_candidate_id"], "joined candidate differs from manufacturing lifecycle")
    require(joined["evaluation_id"] == lifecycle["joined_interface_evaluation_id"], "joined evaluation differs from manufacturing lifecycle")
    require(joined["selection_id"] == lifecycle["joined_quotation_selection_id"], "joined selection differs from manufacturing lifecycle")
    require(joined["ancestry"]["planning_configuration_id"] == concept["configuration_id"], "planning configuration differs from joined candidate")
    require(len(bom) == 41 and len(routing) == 18, "manufacturing BOM or routing row count changed")
    require(sum(int(row["quantity_per_assembly"]) for row in bom
                if row["assembly"] == "door-opening" and row["item"] != "door-parts-research-count") == 694,
            "door piece count differs from controlled manufacturing handoff")
    require(sum(int(row["direct_hours_per_unit"]) for row in routing
                if row["assembly"] == "17m-powered-car" and row["direct_hours_per_unit"]) == 720,
            "car direct assembly hours differ from quoted route")
    require(not any(lifecycle[k] for k in ("posted", "external_transactions_performed", "physical_accepted", "manufacturing_release", "ready_for_import")),
            "manufacturing lifecycle unexpectedly claims native import or acceptance")
    joined_id = joined["physical_candidate_id"]
    joined_sha = sha256((ROOT / SOURCES["joined_candidate"]).read_bytes()).hexdigest()
    require(vehicle_input["source_sha256"][SOURCES["joined_candidate"]] == joined_sha,
            "digital vehicle input did not consume the exact joined candidate")
    require(vehicle_input["joined_physical_candidate_id"] == joined_id and
            vehicle_result["joined_physical_candidate_id"] == joined_id and
            vehicle_result["selection_id"] == joined["selection_id"],
            "digital vehicle input/result belongs to another joined candidate or selection")
    require(vehicle_result["input_id"] == vehicle_input["input_id"],
            "digital vehicle result belongs to another input")
    require(civil_input["physical_candidate_id"] == joined_id and
            civil_result["physical_candidate_id"] == joined_id,
            "digital civil input/result belongs to another joined candidate")
    require(civil_input["source_sha256"][SOURCES["joined_candidate"]] == joined_sha,
            "digital civil input did not consume the exact joined candidate")
    require(civil_result["input_evaluation_id"] == civil_input["evaluation_id"],
            "digital civil result belongs to another input evaluation")
    vehicle_sha = sha256((ROOT / SOURCES["digital_vehicle_result"]).read_bytes()).hexdigest()
    require(civil_input["source_sha256"][SOURCES["digital_vehicle_result"]] == vehicle_sha,
            "digital civil input did not consume the exact vehicle result")
    require(D(str(civil_result["quantity_context"]["bare_beam_mass_t"])) ==
            D(str(joined["civil"]["bare_beam_mass_t"])),
            "civil digital result changed the baseline beam mass without a new cost basis")
    revision = civil_result.get("digital_civil_revision_option")
    if revision and D(str(revision.get("additional_counted_steel_kg_per_beam", 0))) > 0:
        require(revision.get("physical_revision_required") is True and
                revision.get("revised_joined_physical_candidate_id") != joined_id,
                "civil reinforcement change lacks a distinct unpriced physical revision")
    require(not vehicle_result["physical_accepted"] and not vehicle_result["fabrication_release"] and
            not civil_result["site_or_physical_accepted"],
            "digital analyses unexpectedly claim physical or fabrication acceptance")

    scope_names = {row["scope"] for row in cost}
    require(len(scope_names) == 14, "capital scope count differs from fourteen-scope estimate")
    direct = sum(D(row["amount_usd_m"]) for row in cost if row["scope"] != "project-risk-contingency")
    contingency = sum(D(row["amount_usd_m"]) for row in cost if row["scope"] == "project-risk-contingency")
    total = direct + contingency
    require(direct == D("852.916") and contingency == direct * D("0.2"), "direct capital or single contingency no longer reconciles")
    require(total == D(str(concept["economics"]["installed_capital_usd_m"])), "installed capital differs from planning concept")
    local = sum(D(row["amount_usd_m"]) * D(row["local_work_fraction"]) for row in cost)
    require(local == D("410.8278"), "local-work planning allowance differs from cost basis")

    # Child prices are inclusive budgeting references, never addends to a capital scope.
    for row in bom:
        row["capital_scope"] = scope_for(row)
        require(row["capital_scope"] in scope_names, "BOM maps to an absent capital scope")
        row["cost_treatment"] = "included-in-scope; do-not-sum-child-rows"
    costs = []
    for scope in sorted(scope_names):
        rows = [row for row in cost if row["scope"] == scope]
        costs.append({
            "scope": scope,
            "amount_usd_m": str(sum(D(row["amount_usd_m"]) for row in rows)),
            "basis_lines": rows,
            "mapped_bom_rows": sum(row["capital_scope"] == scope for row in bom),
            "coverage": "assembly-quote-route" if any(row["capital_scope"] == scope for row in bom)
                        else "cost-ledger-only",
        })

    programme = (ROOT / SOURCES["cost_programme"]).read_text()
    schedule_pairs = [(int(a), int(b)) for a, b in re.findall(r"Month\s+(\d+)[–-](\d+)", programme)]
    require(schedule_pairs == [(0, 6), (6, 24), (8, 31), (15, 35), (26, 38), (29, 40), (40, 43)], "cost programme stage windows changed")
    require(max(end for _, end in schedule_pairs) == concept["economics"]["delivery_months"], "delivery month differs from planning concept")
    stages = ["survey-design", "groundworks-supports", "beam-factory", "beam-erection",
              "rail-overhead", "stations-depot-power-controls", "integration-training-trials"]
    schedule = [dict(stage=name, start_month=start, end_month=end,
                     duration_months=end-start, overlaps_other_stages=True)
                for name, (start, end) in zip(stages, schedule_pairs)]
    require(D("6000") / D("16") == D("375"), "beam rate arithmetic changed")
    require(D("375") <= D((31-8)*20) and D("375") <= D((35-15)*20), "beam factory or erection rate exceeds schedule window")

    six_car_sets = int(concept["service"]["fleet_active"] + concept["service"]["fleet_reserve"])
    require(six_car_sets == 51 and int(concept["civil"]["beam_lifts"]) == 6000, "fleet or span count differs from cost take-off")
    dry_run = {
        "mode": "ERPNext-shaped preview only; no import, API call or transaction",
        "admitted_to_native_adapter": False,
        "item_groups": [
            {"item_code": "OSR-V07-PLAN-POWERED-CAR", "assembly": "17m-powered-car", "quantity": six_car_sets*6},
            {"item_code": "OSR-V07-PLAN-DOOR-OPENING", "assembly": "door-opening", "quantity": six_car_sets*12},
            {"item_code": "OSR-V07-PLAN-10M-BEAM", "assembly": "10m-beam", "quantity": 6000},
            {"item_code": "OSR-V07-PLAN-POWER-SITE", "assembly": "station-power-site", "quantity": 6},
        ],
        "bom_source": SOURCES["bom"], "routing_source": SOURCES["routing"],
        "proposed_documents": ["Item", "BOM", "Routing", "Request for Quotation", "Quality Inspection"],
        "withheld_documents": ["Purchase Order", "Purchase Receipt", "Work Order", "Stock Entry", "Installation Record", "Asset Repair"],
        "reason": "Joined planning ID is not the existing adapter's sealed 13-hash proposal; child specifications, approved limits, suppliers, native masters and authenticated reviews are absent",
    }
    return {
        "schema": "osr-v07-digital-production-handoff/1",
        "physical_candidate_id": joined["physical_candidate_id"],
        "evaluation_id": joined["evaluation_id"],
        "selection_id": joined["selection_id"],
        "configuration_id": concept["configuration_id"],
        "source_sha256": {key: sha256((ROOT / path).read_bytes()).hexdigest() for key, path in SOURCES.items()},
        "digital_analysis": {
            "vehicle_input_id": vehicle_input["input_id"],
            "vehicle_evaluation_id": vehicle_result["evaluation_id"],
            "vehicle_result_sha256": vehicle_sha,
            "civil_input_evaluation_id": civil_input["evaluation_id"],
            "civil_evaluation_id": civil_result["evaluation_id"],
            "civil_result_sha256": sha256((ROOT / SOURCES["digital_civil_result"]).read_bytes()).hexdigest(),
            "civil_revision_option": revision,
            "civil_revision_option_transferred_into_cost_or_bom": False,
            "baseline_parent_price_and_10m_beam_preserved": True,
        },
        "capital": {"currency": "USD", "price_year": 2026, "direct_usd_m": str(direct),
                    "contingency_usd_m": str(contingency), "installed_usd_m": str(total),
                    "local_work_allowance_usd_m": str(local), "scope_count": len(costs),
                    "scope_rows": costs},
        "production": {"bom_row_count": len(bom), "routing_row_count": len(routing),
                       "full_car_direct_assembly_hours_allowance": 720,
                       "fleet_cars": six_car_sets*6, "fleet_doors": six_car_sets*12,
                       "beam_count": 6000, "bearing_count": int(concept["civil"]["bearings"]),
                       "factory_and_erection_workdays_at_16_beams_per_day_each": 375,
                       "bom_rows": bom, "routing_rows": routing},
        "schedule": {"total_months": 43, "stages": schedule,
                     "logic": "support access → beam erection → rail/overhead → power/stopping integration → trials"},
        "erpnext_dry_run": dry_run,
        "release_status": {"digital_quote_build_plan": "compiled", "physical_acceptance": False,
                           "fabrication_release": False, "supplier_quote_received": False,
                           "native_erp_transaction": False},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare with the published handoff")
    args = parser.parse_args()
    raw = (json.dumps(compile_handoff(), sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
    target = HERE / "handoff.json"
    if args.check:
        if target.read_bytes() != raw:
            raise SystemExit("digital production handoff is stale")
        print("digital production handoff current", sha256(raw).hexdigest())
    else:
        target.write_bytes(raw)
        print("wrote", target, sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
