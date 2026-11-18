"""Candidate-bound project, procurement and workforce planning view."""

import argparse
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[3]


SCOPE_STAGE = {
    "rolling-stock-and-vehicle-interfaces": "stations-depot-power-controls",
    "guideway-beams-bearings-and-detail": "beam-factory",
    "piers-foundations-and-groundworks": "groundworks-supports",
    "span-haul-and-erection": "beam-erection",
    "rails-welding-and-protected-access": "rail-overhead",
    "stations-platforms-and-access": "stations-depot-power-controls",
    "traction-grid-and-protection": "stations-depot-power-controls",
    "auxiliary-charging-and-grid": "stations-depot-power-controls",
    "turnbacks-and-line-controls": "stations-depot-power-controls",
    "fleet-spares-and-recovery": "stations-depot-power-controls",
    "production-depot-land-and-utilities": "groundworks-supports",
    "prototypes-testing-and-tax": "integration-training-trials",
    "launch-machinery-and-converters": "stations-depot-power-controls",
}


def _money(value):
    amount = Decimal(str(value))
    if not amount.is_finite() or amount < 0:
        raise ValueError("Finite nonnegative planning amount required")
    return amount


def project(selection: dict, handoff: dict, *, loaded_workshop_rate_usd_per_hour=None) -> dict:
    """Compile a disabled business preview from one verified digital handoff."""
    body = {key: value for key, value in handoff.items() if key != "evaluation_id"}
    expected = sha256(json.dumps(body, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    if (selection.get("schema") != "opensourcerail.v07.digital-selection.1"
            or handoff.get("schema") != "osr-v07-digital-production-handoff/1"
            or handoff.get("evaluation_id") != expected
            or handoff.get("physical_candidate_id") != selection.get("physical_candidate_id")
            or handoff.get("selection_id") != selection.get("selection_id")
            or handoff.get("source_selection_evaluation_id") != selection.get("evaluation_id")):
        raise ValueError("Selected business handoff identity differs")
    counts = {row["assembly"]: row["quantity"]
              for row in handoff["erpnext_dry_run"]["item_groups"]}
    if len(counts) != len(handoff["erpnext_dry_run"]["item_groups"]):
        raise ValueError("Duplicate production assembly")
    production = handoff["production"]
    if (production["bom_row_count"] != len(production["bom_rows"])
            or production["routing_row_count"] != len(production["routing_rows"])):
        raise ValueError("Production row count differs")
    rfqs = []
    for row in production["bom_rows"]:
        if row["make_buy"] not in {"buy-qualified", "mixed"}:
            continue
        assembly = row["assembly"]
        if assembly not in counts:
            raise ValueError("Uncounted procurement assembly")
        quantity = _money(row["quantity_per_assembly"]) * counts[assembly]
        if quantity == 0:
            continue
        rfqs.append({"assembly": assembly, "item": row["item"],
                     "planning_quantity": str(quantity), "unit": row["unit"],
                     "make_buy": row["make_buy"], "supplier_quote_usd": None,
                     "candidate_id": handoff["physical_candidate_id"],
                     "rate_status": row["rate_status"]})
    known_hours = Decimal(0)
    unmeasured = []
    for row in production["routing_rows"]:
        assembly = row["assembly"]
        if assembly not in counts:
            raise ValueError("Uncounted workshop assembly")
        hours = row["direct_hours_per_unit"]
        if hours:
            known_hours += _money(hours) * counts[assembly]
        else:
            unmeasured.append({"assembly": assembly, "sequence": row["sequence"]})
    loaded_rate = (None if loaded_workshop_rate_usd_per_hour is None
                   else _money(loaded_workshop_rate_usd_per_hour))
    if loaded_rate is not None and loaded_rate <= 0:
        raise ValueError("Positive loaded workshop rate required")
    stages = {row["stage"]: row for row in handoff["schedule"]["stages"]}
    if set(SCOPE_STAGE.values()) - stages.keys():
        raise ValueError("Capital draw references absent construction stage")
    scopes = handoff["capital"]["scope_rows"]
    if {row["scope"] for row in scopes} != set(SCOPE_STAGE) | {"project-risk-contingency"}:
        raise ValueError("Capital draw must account for all fourteen scopes")
    draws = {month: Decimal(0) for month in range(handoff["schedule"]["total_months"])}
    by_stage = {name: Decimal(0) for name in stages}
    for row in scopes:
        if row["scope"] == "project-risk-contingency":
            continue
        name = SCOPE_STAGE[row["scope"]]
        stage = stages[name]
        amount = _money(row["amount_usd_m"])
        by_stage[name] += amount
        duration = stage["end_month"] - stage["start_month"]
        monthly = (amount / duration).quantize(Decimal("0.000001"))
        for month in range(stage["start_month"], stage["end_month"] - 1):
            draws[month] += monthly
        draws[stage["end_month"] - 1] += amount - monthly * (duration - 1)
    direct = _money(handoff["capital"]["direct_usd_m"])
    contingency = _money(handoff["capital"]["contingency_usd_m"])
    if sum(draws.values()) != direct or direct + contingency != _money(handoff["capital"]["installed_usd_m"]):
        raise ValueError("Project draw and contingency do not reconcile")
    return {"schema": "osr-v07-business-planning-view/1",
            "physical_candidate_id": handoff["physical_candidate_id"],
            "selection_id": handoff["selection_id"],
            "handoff_evaluation_id": handoff["evaluation_id"],
            "planning_basis": "Each direct capital scope spread evenly over its assigned construction stage; no supplier or financing dates",
            "direct_capital_usd_m": str(direct),
            "contingency_reserved_usd_m": str(contingency),
            "installed_funding_envelope_usd_m": str(direct + contingency),
            "stage_direct_usd_m": {key: str(value) for key, value in sorted(by_stage.items())},
            "monthly_direct_draw_usd_m": [str(draws[month]) for month in draws],
            "rfq_lines": rfqs, "purchase_orders_created": False,
            "known_direct_workshop_hours": str(known_hours),
            "unmeasured_workshop_steps": unmeasured,
            "planning_loaded_workshop_rate_usd_per_hour": None if loaded_rate is None else str(loaded_rate),
            "planning_known_hours_labour_usd_within_capital":
                None if loaded_rate is None else str(known_hours * loaded_rate),
            "payroll_usd": None, "payroll_basis": "Hourly rates, rosters, employer costs and actual time records required",
            "invoices_usd": None, "actual_cashflow_usd": None,
            "erp_transactions_created": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--loaded-workshop-rate-usd-per-hour", type=str)
    args = parser.parse_args(argv)
    selection = tomllib.loads((ROOT / "docs/reference-v07/digital/selected.toml").read_text())
    handoff = json.loads((ROOT / "docs/reference-v07/digital/production/handoff.json").read_text())
    result = project(selection, handoff,
                     loaded_workshop_rate_usd_per_hour=args.loaded_workshop_rate_usd_per_hour)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(f"wrote {args.output} with {len(result['rfq_lines'])} RFQ lines")


if __name__ == "__main__":
    main()
