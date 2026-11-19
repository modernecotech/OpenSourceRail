"""Build constant-price buyer cash sensitivities from the Baghdad programme draws."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Debt share of installed capital. The 20% export target applies before allowance.
EXPORT_CEILING = 0.85 * 0.20 / 1.20
CASES = {
    "budget_only": (0, 0, 0),
    "export_slice": (EXPORT_CEILING, 0.04, 15),
    "mixed_debt": (0.50, 0.04, 20),
    "shorter_costlier_mixed_debt": (0.50, 0.07, 12),
}


def cash_schedule(network, share, rate, tenor):
    """Interest paid from budget, midyear construction draws, year-end amortisation."""
    schedule = network["selected_construction_cashflow"]
    rows = []
    balance = 0.0
    for draw in schedule["annual_capital_draw"]:
        capital = draw["capital_usd_m"]
        borrowing = capital * share
        interest = (balance + borrowing / 2) * rate
        balance += borrowing
        rows.append(dict(year=draw["year"], capital=capital, borrowing=borrowing,
                         interest=interest, principal=0.0, operations=0.0, renewals=0.0,
                         closing_debt=balance, buyer_cash=capital - borrowing + interest))

    payment = balance * rate / (1 - (1 + rate) ** -tenor) if rate else (
        balance / tenor if tenor else 0.0)
    for year in range(1, 31):
        interest = balance * rate
        principal = (balance if year == tenor else payment - interest) if year <= tenor else 0.0
        balance -= principal
        operations = network["selected_annual_opex_usd_m"]["total"]
        renewals = sum(event["usd_m"] for event in network["selected_renewals_usd_m"]
                       if event["year"] == year)
        rows.append(dict(year=schedule["full_service_start_year_assumption"] + year - 1,
                         capital=0.0, borrowing=0.0, interest=interest, principal=principal,
                         operations=operations, renewals=renewals, closing_debt=balance,
                         buyer_cash=operations + renewals + principal + interest))
    return dict(debt_share_of_installed=share, real_rate=rate, repayment_years=tenor,
                annual_debt_service=payment, construction_interest=sum(
                    row["interest"] for row in rows if row["capital"]), annual=rows)


def build():
    results = json.loads((HERE / "system-results.json").read_text())
    return dict(source_evaluation_id=results["evaluation_id"], unit="million constant 2026 USD",
                scope="Illustrative gross buyer cash before receipts, financing fees, tax and FX.",
                networks={key: dict(candidate_id=value["selected_candidate_id"],
                                    evaluation_id=value["selected_evaluation_id"],
                                    cases={case: cash_schedule(value, *terms)
                                           for case, terms in CASES.items()})
                          for key, value in results["networks"].items()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = HERE / "financing-scenarios.json"
    data = json.dumps(build(), sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.check:
        if data != output.read_text():
            raise SystemExit("Financing schedule differs from published inputs")
    else:
        output.write_text(data)
