"""Phase the connected seven-corridor Baghdad timetable against the Iraqi market budget."""

import argparse
from hashlib import sha256
from html import escape
import json
from math import isclose, isfinite
from pathlib import Path
import tomllib

from cities.Baghdad import airport_opening, financing, iraq_budget
from engineering.outline.baghdad_system import _id
from engineering.performance import check_disk_reservation, disk_reservation

CITY = Path(__file__).resolve().parent
ROOT = CITY.parents[1]
CONFIG = CITY / "phased-service.toml"
GUIDE = ROOT / "docs/operator-review/finance/phased-first.html"


def build(config=None):
    assumptions = tomllib.loads(CONFIG.read_text()) if config is None else config
    cfg, report, network = airport_opening.opening_inputs()
    diagrams = report["networks"]["first"]
    staffing = json.loads(iraq_budget.WORKFORCE.read_bytes())["studies"]["first"]
    if (
        not diagrams["all_groups_diagrammed"]
        or diagrams["held_service_group_ids"]
        or staffing["source_physical_id"] != diagrams["selected_candidate_id"]
        or staffing["source_diagram_evaluation_id"] != report["evaluation_id"]
        or staffing["source_evaluation_id"] != network["selected_evaluation_id"]
    ):
        raise ValueError("Phasing requires one source-bound, fully diagrammed first programme")
    full = iraq_budget.funding_cases()["first"]["full"]["central"]
    schedule = network["selected_construction_cashflow"]
    start = schedule["annual_capital_draw"][0]["year"]
    groups = diagrams["groups"]
    days = cfg["vehicle"]["service_days_per_year"]
    km = {name: row["one_way_km"] * row["scheduled_trips"] * days for name, row in groups.items()}
    total_km = sum(km.values())
    if not isclose(total_km, diagrams["annual_diagrammed_train_km"]) or not isclose(
        total_km, network["selected_service_allowance"]["annual_train_km"]
    ):
        raise ValueError("Every priced train-km must belong to an included working")
    ramp = assumptions["demand_fraction_by_service_half_year"]
    if (
        not ramp
        or any(type(value) not in (int, float) or not isfinite(value) or not 0 <= value <= 1 for value in ramp)
        or sorted(ramp) != list(ramp)
        or ramp[-1] != 1
    ):
        raise ValueError("Demand ramp must increase to the full-service demand assumption")
    opening = {}
    for stage in assumptions["openings"]:
        y, m = stage["construction_year"], stage["month"]
        if (
            type(y) is not int
            or not 1 <= y <= len(schedule["annual_capital_draw"]) + 1
            or type(m) is not int
            or not 1 <= m <= 12
            or not stage["groups"]
        ):
            raise ValueError("Specify a valid opening month relative to the construction programme")
        for name in stage["groups"]:
            if name not in groups or name in opening:
                raise ValueError("Each connected first-programme group must have one opening")
            opening[name] = 12 * (y - 1) + m - 1
    if opening.keys() != groups.keys():
        raise ValueError("Missing connected line opening")
    full_start = schedule["full_service_start_year_assumption"]
    if max(opening.values()) > (full_start - start) * 12:
        raise ValueError("All corridors must open by the assumed full service/debt repayment year")

    # Break down the central Iraqi OPEX without counting embedded payroll twice.
    envelopes = staffing["opex"]["eligible_envelopes_usd_m_year"]
    credits = staffing["iraq_payroll"]["estimated_credit_by_envelope_usd_m_year"]
    station = envelopes["Station operations"] - credits["Station operations"]
    line = envelopes["Power maintenance"] - credits["Power maintenance"]
    train = full["power_m"] + envelopes["Non-energy train operations"] - credits["Non-energy train operations"]
    fixed = full["payroll_m"]
    if not isclose(station + line + train + fixed, full["opex_m"]):
        raise ValueError("Staged operating scopes do not close to the Iraqi operating budget")

    # Keep the parent draw timing. Assign the Iraqi central installed price to those draws exactly once.
    cash_draws = [
        {"year": r["year"], "capital_usd_m": r["capital_usd_m"] * full["capital_factor"]}
        for r in schedule["annual_capital_draw"]
    ]
    profile = {**network, "selected_construction_cashflow": {**schedule, "annual_capital_draw": cash_draws}}
    debt = financing.cash_schedule(profile, *financing.CASES["mixed_debt"])
    if not isclose(sum(row["capital"] for row in debt["annual"]), full["installed_m"]):
        raise ValueError("Iraqi construction draws do not equal the central installed price")
    total_stops = sum(len(row["outward_stops"]) for row in groups.values())
    length = sum(row["one_way_km"] for row in groups.values())
    fleet = sum(row["diagrammed_sets"] for row in groups.values())
    if fleet != diagrams["diagrammed_sets"]:
        raise ValueError("Line workings must account for the parent diagrammed fleet")
    lines, renewal_by_year = {}, {}
    for name, month in sorted(opening.items(), key=lambda item: (item[1], item[0])):
        data = groups[name]
        line_share = data["one_way_km"] / length
        stop_share = len(data["outward_stops"]) / total_stops
        offer_share = km[name] / total_km
        lines[name] = {
            "month_index": month,
            "opening": f"{start+month//12}-{month%12+1:02}",
            "annual_train_km": km[name],
            "diagrammed_sets": data["diagrammed_sets"],
            "station_occurrences": len(data["outward_stops"]),
            "route_km": data["one_way_km"],
            "line_and_station_running_m": station * stop_share + line * line_share,
            "train_running_m": train * offer_share,
            "annual_mature_paid_m": full["paid_m"] * offer_share,
        }
        for event in network["selected_renewals_usd_m"]:
            share = data["diagrammed_sets"] / fleet if event["component"] == "fleet_major_renewal" else line_share
            due = start + (month + event["year"] * 12 - 1) // 12
            renewal_by_year[due] = renewal_by_year.get(due, 0.0) + event["usd_m"] * share
    annual = []
    for item in debt["annual"]:
        year = item["year"]
        monthly = {
            "train_km": 0.0,
            "fixed_payroll_m": 0.0,
            "line_and_station_running_m": 0.0,
            "train_running_m": 0.0,
            "paid_journeys_m": 0.0,
        }
        for m in range(12 * (year - start), 12 * (year - start + 1)):
            if m >= min(opening.values()):
                monthly["fixed_payroll_m"] += fixed / 12
            for name, row in lines.items():
                age = m - opening[name]
                if age < 0:
                    continue
                monthly["train_km"] += row["annual_train_km"] / 12
                for scope in ("train_running_m", "line_and_station_running_m"):
                    monthly[scope] += row[scope] / 12
                demand = ramp[min(age // 6, len(ramp) - 1)]
                monthly["paid_journeys_m"] += row["annual_mature_paid_m"] * demand / 12
        opex = sum(monthly[k] for k in ("train_running_m", "line_and_station_running_m", "fixed_payroll_m"))
        fares = monthly["paid_journeys_m"] * full["net_usd"]
        renewal = renewal_by_year.get(year, 0.0)
        buyer = item["capital"] - item["borrowing"] + item["principal"] + item["interest"] + opex + renewal
        annual.append(
            {
                "year": year,
                **monthly,
                "capital_m": item["capital"],
                "borrowing_m": item["borrowing"],
                "interest_m": item["interest"],
                "principal_m": item["principal"],
                "closing_debt_m": item["closing_debt"],
                "operations_m": opex,
                "net_fares_m": fares,
                "renewals_m": renewal,
                "public_cash_m": buyer - fares,
            }
        )
    if not isclose(
        sum(r["renewals_m"] for r in annual), sum(e["usd_m"] for e in network["selected_renewals_usd_m"])
    ):
        raise ValueError("Staging must retain the complete parent renewal allowances")
    result = {
        "physical_candidate_id": network["selected_candidate_id"],
        "network_evaluation_id": network["selected_evaluation_id"],
        "diagram_evaluation_id": report["evaluation_id"],
        "assumptions": assumptions,
        "central_iraq_full_service": full,
        "source_sha256": {
            str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
            for p in (
                Path(__file__),
                Path(financing.__file__),
                Path(iraq_budget.__file__),
                iraq_budget.WORKFORCE,
                CITY / "iraq-capital.toml",
                CITY / "iraq-market.toml",
                CITY / "iraq-power.toml",
            )
        },
        "full_service_start": full_start,
        "annual": annual,
        "groups": lines,
        "full_annual_train_km": total_km,
        "physical_accepted": False,
        "opening_dates_committed": False,
    }
    result["evaluation_id"] = _id(result)
    return result


def guide(data):
    lines = data["groups"]
    annual = data["annual"]
    full = data["central_iraq_full_service"]
    heading = "<tr><th>Year</th><th>Capital</th><th>Borrowed</th><th>Interest</th><th>Principal</th><th>Train-km (m)</th><th>OPEX</th><th>Paid journeys (m)</th><th>Net fares</th><th>Renewals</th><th>Public cash</th></tr>"
    rows = []
    for row in annual:
        values = [row[k] for k in ("capital_m", "borrowing_m", "interest_m", "principal_m")]
        values.extend(
            [
                row["train_km"] / 1e6,
                *[
                    row[k]
                    for k in ("operations_m", "paid_journeys_m", "net_fares_m", "renewals_m", "public_cash_m")
                ],
            ]
        )
        rows.append(
            "<tr><th>" + str(row["year"]) + "</th>" + "".join(f"<td>{v:,.2f}</td>" for v in values) + "</tr>"
        )
    stage_rows = "".join(
        f'<tr><th>{escape(name)}</th><td>{row["opening"]}</td><td>{row["annual_train_km"]:,.0f}</td><td>{row["diagrammed_sets"]}</td></tr>'
        for name, row in lines.items()
    )
    ramp = ", ".join(f"{v:.0%}" for v in data["assumptions"]["demand_fraction_by_service_half_year"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="finance.css"><title>Phased Baghdad service and public cash</title></head>
<body><main><a href="index.html">Railway finance</a><h1>Seven corridors in three openings</h1>
<p>The seven connected first-programme workings reach {data['full_annual_train_km']/1e6:.2f} million train-km per year. This illustration opens the Airport and Green lines first, while other lines are still under construction. Each line uses its full booked timetable from its assumed first month.</p>
<section class="panel"><h2>Assumed opening months</h2><div class="scroll"><table><thead><tr><th>Line</th><th>First service</th><th>Full annual train-km</th><th>Working sets</th></tr></thead><tbody>{stage_rows}</tbody></table></div>
<p>Months represent equal twelfths of a planning year. The order assumes completed common depot, control, grid and access facilities. Each stage requires an operational interface review and availability of sufficient fleet. The Airport line here runs its original network timetable and uses shared network assets. The standalone Airport investment is a separate scenario.</p></section>
<section class="panel"><h2>Who pays before the whole network opens</h2>
<p>The central Iraqi capital allowance is ${full['installed_m']/1000:,.3f} billion in constant 2026 USD. Apply the original annual construction draw weights once. Half the capital comes from debt at 4% real. Construction interest is on midyear draws and principal repayment starts in {data['full_service_start']} over 20 years.</p>
<p>Retain the full ${full['payroll_m']:,.2f}m annual payroll from the first passenger opening as a conservative mobilisation assumption. Remove payroll already embedded in train, station and maintenance allowances. Scale energy and other train costs by connected train-km, line maintenance by open length, and station running by named stop occurrences. The 64-station cost allowance needs an agreed assignment across the 52 named occurrences. Pre-opening staff mobilisation needs a separate commissioning estimate.</p>
<p>Allocate mature paid journeys by offered train-km pending line-specific counts. New lines take {ramp} of that demand in successive six-month periods and retain the last value. Full-network annual OPEX reaches ${full['opex_m']:,.2f}m and mature net fares reach ${full['farebox_m']:,.2f}m. This assumes comparable passenger trip lengths and transfer rates across stages. Interchanges, mode share and peak loading require survey.</p>
<p>Age each parent renewal from the month that line enters service. Allocate fleet renewals by diagrammed sets and infrastructure renewals by route length. Price these renewals at the retained engineering allowances until contracts establish Iraqi replacement costs. The cash horizon ends after 30 years from the original full-service year. Earlier lines operate for additional months within that horizon.</p></section>
<section class="panel"><h2>Annual cash requirement</h2><p>Amounts are millions of constant 2026 USD. Public cash is construction and operation plus interest, principal and renewals less borrowing and collected fares.</p><div class="scroll"><table><thead>{heading}</thead><tbody>{''.join(rows)}</tbody></table></div></section>
<p>Reproduce using <code>python3 -m cities.Baghdad.phased_finance --json</code>. Adjust <code>cities/Baghdad/phased-service.toml</code> with a revised sequence. The mixed-debt full-service control remains in the finance planner. This scenario includes the seven connected first-programme lines only.</p>
</main></body></html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    for k in ("json", "publish", "check"):
        mode.add_argument("--" + k, action="store_true")
    parser.add_argument("--assumptions", type=Path, help="Read a separate phasing scenario for JSON output")
    args = parser.parse_args()
    if args.assumptions and not args.json:
        parser.error("The published guide uses phased-service.toml")
    result = build(tomllib.loads(args.assumptions.read_text()) if args.assumptions else None)
    if args.json:
        print(json.dumps(result, indent=2, allow_nan=False))
    elif args.check:
        if GUIDE.read_text() != guide(result):
            raise SystemExit("Refresh the first-programme phased cashflow")
    else:
        with disk_reservation(ROOT, GUIDE.parent, "First-programme phased finance guide", 65536) as lease:
            check_disk_reservation(lease)
            GUIDE.write_text(guide(result), encoding="utf-8")


if __name__ == "__main__":
    main()
