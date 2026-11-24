"""Compare all already-priced civil/supply combinations on one first-programme service."""
import argparse
import json
from itertools import product

from engineering.outline import baghdad_system as system

SUPPLIES = ("protected_conductor", "overhead", "limited_conductor_battery", "station_battery")
SERVICE = ("route_km", "stations", "line_count", "annual_train_km", "active_trainsets",
           "fleet_trainsets", "normal_places_per_train", "offered_places_per_hour_direction")


def evaluate():
    common_service = None
    rows = []
    for span, shared, supply in product(system.SUPPORTED_SPANS_M, (False, True), SUPPLIES):
        case = system.evaluate("first", supply, span_m=span, common_pier=shared)
        service = {name: case["service"][name] for name in SERVICE}
        if common_service is None:
            common_service = service
        elif service != common_service:
            raise ValueError("Alternatives differ in passenger service or fleet scope")
        rows.append({
            "span_m": span, "pier": "shared" if shared else "separate", "supply": supply,
            "physical_id": case["physical_candidate_id"], "evaluation_id": case["evaluation_id"],
            "installed_capital_usd_m": case["capital_usd_m"]["installed"],
            "priced_30y_pv_usd_m": case["whole_life_30y_present_usd_m"],
            "site_or_physical_accepted": case["site_or_physical_accepted"],
        })
    if len({r["physical_id"] for r in rows}) != len(rows):
        raise ValueError("A supply or civil change failed to receive a distinct physical identity")
    return {"service": common_service, "cases": rows, "audit_id": system._id(rows)}


def price_table(rows):
    lines = [
        "| Span and piers | Protected conductor | Overhead | Partial conductor and battery | Station charging and battery |",
        "|---|---:|---:|---:|---:|",
    ]
    amounts = {(r["span_m"], r["pier"], r["supply"]): r["priced_30y_pv_usd_m"] for r in rows}
    for span, pier in product(system.SUPPORTED_SPANS_M, ("separate", "shared")):
        prices = [f"{amounts[span, pier, supply]:,.0f}" for supply in SUPPLIES]
        lines.append("| " + " | ".join([f"{span} m {pier}", *prices]) + " |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="verify the published decision table")
    modes.add_argument("--json", action="store_true", help="include identities and prices for each case")
    args = parser.parse_args()
    result = evaluate()
    if args.json:
        print(json.dumps(result, indent=2))
        return
    table = price_table(result["cases"])
    if args.check:
        if table not in (system.ROOT / "docs/DESIGN-DECISIONS.md").read_text():
            raise SystemExit("The decision table differs from the current network comparison")
    else:
        print("First programme, 30-year priced present value in USD millions.")
        print(table)
        print("All figures are planning estimates. Site and physical acceptance remain open.")
    print("Audit ID", result["audit_id"])


if __name__ == "__main__":
    main()
