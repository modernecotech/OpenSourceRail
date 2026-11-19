"""Assemble comparable buyer cash schedules in constant 2026 USD millions."""
import argparse
import json
import math
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "cities/Baghdad"))
from financing import CASES, cash_schedule


def schedules():
    core = tomllib.loads((ROOT / "docs/reference-v07/digital/selected.toml").read_text())
    cost = core["economics"]
    months = cost["delivery_months"]
    capital = cost["installed_capital_usd_m"]
    years = math.ceil(months / 12)
    # Provisional level monthly expenditure across the published delivery duration.
    draws = [dict(year=i + 1, capital_usd_m=capital * min(12, months - 12*i) / months)
             for i in range(years)]
    core_basis = dict(selected_construction_cashflow=dict(annual_capital_draw=draws,
                      full_service_start_year_assumption=years + 1),
                      selected_annual_opex_usd_m=dict(total=cost["annual_opex_usd_m"]),
                      selected_renewals_usd_m=[dict(year=15, usd_m=160), dict(year=25, usd_m=70)])
    cases = {k: cash_schedule(core_basis, *terms) for k, terms in CASES.items() if k != "export_slice"}
    data = {"core": dict(label="Core · 30 km", id=core["physical_candidate_id"], cases=cases)}
    city = json.loads((ROOT / "cities/Baghdad/financing-scenarios.json").read_text())
    for k, n in city["networks"].items():
        data[k] = dict(label={"first": "Baghdad · seven corridors", "metropolitan": "Baghdad · citywide"}[k],
                       id=n["candidate_id"], cases=n["cases"])
    for network in data.values():
        for case in network["cases"].values():
            rows = case["annual"]
            assert abs(sum(r["borrowing"] - r["principal"] for r in rows)) < 1e-7
            assert all(abs(r["buyer_cash"] - (r["capital"] - r["borrowing"] + r["principal"] +
                       r["interest"] + r["operations"] + r["renewals"])) < 1e-7 for r in rows)
            assert abs(rows[-1]["closing_debt"]) < 1e-7
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = HERE / "schedules.js"
    encoded = "const railwayFinance = " + json.dumps(schedules(), ensure_ascii=False, separators=(",", ":")) + ";\n"
    if args.check:
        if target.read_text() != encoded:
            raise SystemExit("Published schedules differ from inputs")
    else:
        target.write_text(encoded)
