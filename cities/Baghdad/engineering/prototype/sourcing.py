"""Review the Airport procurement estimate or replay a clearly labelled quotation example."""
import argparse
import json
from pathlib import Path

from deployment.erpnext.apps.osr_erpnext.osr_erpnext.sourcing_comparison import compare_lot


def _money(value):
    return "open" if value is None else f"${value:,.2f}"


def _short_money(value):
    if value is None:
        return "open"
    return f"${value:,.0f}" if value >= 1 else _money(value)


def demonstration(packet, lot_id):
    if lot_id is None:
        lot_id = next(row["lot_id"] for row in packet["lots"]
                      if row["price_period"] == "one-time" and row.get("base_usd", 0) and row["base_usd"] > 0)
    lot = next((row for row in packet["lots"] if row["lot_id"] == lot_id), None)
    if lot is None or lot["price_period"] != "one-time" or not lot.get("base_usd"):
        raise ValueError("The example needs a one-time lot with a positive central estimate")
    offers = []
    # Two fully scoped offers exercise the effect of upkeep; a third excludes a required scope.
    for letter, direct_factor, upkeep_factor, terms in (
            ("A", .96, .02, []), ("B", 1.02, .01, []), ("C", .85, .01, ["Delivery excluded"])):
        offers.append(dict(candidate_id=packet["candidate_id"], evaluation_id=packet["evaluation_id"],
                           supplier=f"Fixture supplier {letter}", quotation=f"EXAMPLE-{letter}", lot_id=lot_id,
                           quantity=lot["quantity"], unit=lot["unit"], currency="USD", evidence_kind="software-fixture",
                           direct_usd=round(lot["base_usd"] * direct_factor, 2),
                           annual_upkeep_usd=round(lot["base_usd"] * upkeep_factor, 2), renewals_usd={}, exclusions=terms))
    return compare_lot(packet, lot_id, offers)


def _summary(packet, lots):
    print("Baghdad Airport procurement estimate • constant 2026 USD")
    opening = packet["subtotal_opening_priced_allowances"]
    annual = packet["additive_groups"]["first-full-year-operations"]
    print(f"Construction allowance {_short_money(opening['base_usd'])} "
          f"({_short_money(opening['low_usd'])} to {_short_money(opening['high_usd'])})")
    print(f"First full operating year {_short_money(annual['base_usd'])} "
          f"({_short_money(annual['low_usd'])} to {_short_money(annual['high_usd'])})")
    print(f"Physical candidate {packet['candidate_id']}\nCommercial estimate {packet['evaluation_id']}\n")
    print(f"{'Lot':30} {'Quantity':>11}  {'Unit':18} {'Period':10} {'Low':>17} {'Central':>17} {'High':>17}")
    for row in lots:
        print(f"{row['lot_id']:30} {row['quantity']:>11,.2f}  {row['unit']:18} {row['price_period']:10} "
              + " ".join(f"{_short_money(row.get(k)):>17}" for k in ("low_usd", "base_usd", "high_usd")))
    print("\nAmounts are extended by price period. Some low and high scenarios vary the quantity. Parent and alternative scopes overlap.")
    print("Use --lot LOT --json for scope, sources, priced deliverables and exclusions.")


def main(argv=None):
    from .sourcing_estimates import estimate_lots
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="Rebuild and check the published buyer estimate")
    modes.add_argument("--publish", action="store_true", help="Replace the canonical estimate after reserving disk space")
    modes.add_argument("--json", action="store_true", help="Write machine-readable output to stdout")
    parser.add_argument("--lot", help="Select one lot by exact ID")
    parser.add_argument("--packet", type=Path, help="Read a specific published Airport prototype ZIP")
    parser.add_argument("--demo", action="store_true", help="Compare three invented offers for a priced one-time lot")
    args = parser.parse_args(argv)
    if (args.check or args.publish) and (args.lot or args.packet or args.demo):
        parser.error("The published estimate uses the complete registered Airport configuration")
    try:
        packet = estimate_lots(args.packet) if args.packet else estimate_lots()
        if args.check or args.publish:
            from cities.Baghdad.airport_integration import write_atomic
            from engineering.performance import check_disk_reservation, disk_reservation
            path = Path(__file__).resolve().with_name("sourcing-estimate.json")
            content = (json.dumps(packet, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
            if args.check:
                if path.read_bytes() != content:
                    raise ValueError("Published Airport sourcing estimate differs from its registered sources")
            else:
                with disk_reservation(path.parents[4], path.parent, "Baghdad Airport sourcing estimate", 2 << 20) as lease:
                    check_disk_reservation(lease)
                    write_atomic(path, content)
            print(f"Verified Airport sourcing estimate {packet['evaluation_id']}")
            return
        lots = [row for row in packet["lots"] if args.lot is None or row["lot_id"] == args.lot]
        if not lots:
            raise ValueError("Unknown estimate lot")
        if args.demo:
            output = demonstration(packet, args.lot)
            if not args.json:
                print(f"Software fixture • {output['lot_id']} • {len(output['offers'])} synthetic offers")
                for row in output["offers"]:
                    print(f"{row['supplier']}   quoted {_money(row['direct_usd'])}   30-year PV {_money(row['pv_30y_4pct_usd'])}"
                          + ("   " + ", ".join(row["holds"]) if row["holds"] else ""))
                print(f"Comparable direct spread {_money(output['direct_spread_usd'])}. 30-year PV spread {_money(output['pv_spread_usd'])}.")
                return
        elif args.lot:
            output = dict(candidate_id=packet["candidate_id"], evaluation_id=packet["evaluation_id"],
                          lot=lots[0], sources={key: packet["sources"][key] for key in lots[0]["sources"]})
        else:
            output = packet
        if args.json:
            print(json.dumps(output, sort_keys=True, indent=2, allow_nan=False))
        else:
            _summary(packet, lots)
    except (OSError, ValueError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    main()
