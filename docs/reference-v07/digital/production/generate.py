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
    "generator": "docs/reference-v07/digital/production/generate.py",
}
D = Decimal


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
    bom, routing, cost = read_csv("bom"), read_csv("routing"), read_csv("cost_basis")
    assert joined["physical_candidate_id"] == lifecycle["joined_physical_candidate_id"]
    assert joined["evaluation_id"] == lifecycle["joined_interface_evaluation_id"]
    assert joined["selection_id"] == lifecycle["joined_quotation_selection_id"]
    assert joined["ancestry"]["planning_configuration_id"] == concept["configuration_id"]
    assert len(bom) == 41 and len(routing) == 18
    assert sum(int(row["quantity_per_assembly"]) for row in bom
               if row["assembly"] == "door-opening" and row["item"] != "door-parts-research-count") == 694
    assert sum(int(row["direct_hours_per_unit"]) for row in routing
               if row["assembly"] == "17m-powered-car" and row["direct_hours_per_unit"]) == 720
    assert not any(lifecycle[k] for k in ("posted", "external_transactions_performed", "physical_accepted", "manufacturing_release", "ready_for_import"))

    scope_names = {row["scope"] for row in cost}
    assert len(scope_names) == 14
    direct = sum(D(row["amount_usd_m"]) for row in cost if row["scope"] != "project-risk-contingency")
    contingency = sum(D(row["amount_usd_m"]) for row in cost if row["scope"] == "project-risk-contingency")
    total = direct + contingency
    assert direct == D("852.916") and contingency == direct * D("0.2")
    assert total == D(str(concept["economics"]["installed_capital_usd_m"]))
    local = sum(D(row["amount_usd_m"]) * D(row["local_work_fraction"]) for row in cost)
    assert local == D("410.8278")

    # Child prices are inclusive budgeting references, never addends to a capital scope.
    for row in bom:
        row["capital_scope"] = scope_for(row)
        assert row["capital_scope"] in scope_names
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
    assert schedule_pairs == [(0, 6), (6, 24), (8, 31), (15, 35), (26, 38), (29, 40), (40, 43)]
    assert max(end for _, end in schedule_pairs) == concept["economics"]["delivery_months"]
    stages = ["survey-design", "groundworks-supports", "beam-factory", "beam-erection",
              "rail-overhead", "stations-depot-power-controls", "integration-training-trials"]
    schedule = [dict(stage=name, start_month=start, end_month=end,
                     duration_months=end-start, overlaps_other_stages=True)
                for name, (start, end) in zip(stages, schedule_pairs)]
    assert D("6000") / D("16") == D("375")
    assert D("375") <= D((31-8)*20) and D("375") <= D((35-15)*20)

    six_car_sets = int(concept["service"]["fleet_active"] + concept["service"]["fleet_reserve"])
    assert six_car_sets == 51 and int(concept["civil"]["beam_lifts"]) == 6000
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
