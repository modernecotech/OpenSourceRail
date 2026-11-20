"""Price Baghdad passenger service at Iraqi wages, tariffs and illustrative fares."""
import json
from math import isclose
from pathlib import Path
import tomllib

if __package__:
    from .iraq_capital import build as capital_estimates
    from .iraq_power import rates
else:
    from iraq_capital import build as capital_estimates
    from iraq_power import rates

CITY = Path(__file__).resolve().parent
WORKFORCE = CITY.parents[1] / "docs/operator-review/delivery/quantities.json"
# A downside pairs low ticket income with expensive labour and electricity.
SCENARIOS = (("downside", 0, "high"), ("central", 1, "base"), ("upside", 2, "low"))


def funding_cases():
    market = tomllib.loads((CITY / "iraq-market.toml").read_text())
    ledger = json.loads((CITY / "system-results.json").read_bytes())["networks"]
    staffing = json.loads(WORKFORCE.read_bytes())
    energy = rates()
    capital = capital_estimates()["networks"]
    fx = market["currency"]["iqd_per_usd"]
    cfg = tomllib.loads((CITY / "system.toml").read_text())
    deflator = 1 + cfg["discount_rate_real"]
    years = cfg["comparison_years"]
    operating_factor = sum(deflator ** -year for year in range(1, years + 1))
    result = {}
    for network, row in ledger.items():
        reference = sum(draw["capital_usd_m"] for draw in row["selected_construction_cashflow"]["annual_capital_draw"])
        renewal_pv = sum(event["usd_m"] * deflator ** -event["year"]
                         for event in row["selected_renewals_usd_m"] if event["year"] <= years)
        service = row["selected_service_allowance"]
        supply = row["power_cases"]["protected_conductor"]
        if row["selected_candidate_id"] != supply["physical_candidate_id"]:
            raise ValueError("Reprice delivered energy for the selected power design")
        demand = market["demand"]
        trip = demand[network]
        offers = {"full": (service["annual_train_km"], supply["annual_grid_gwh"],
                           row["selected_annual_opex_usd_m"]["energy"], staffing["studies"][network])}
        if network == "metropolitan":
            key = "metropolitan-mainlines"
            option = staffing["operating_options"][key]
            offers[key] = (option["annual_train_km"], option["annual_grid_gwh"],
                           option["opex"]["other_costs_usd_m_year"], option)
        result[network] = {}
        for offer, (km, gwh, old_energy, study) in offers.items():
            if (study["source_physical_id"] != row["selected_candidate_id"] or
                    study["source_evaluation_id"] != row["selected_evaluation_id"]):
                raise ValueError("Service staffing and electricity must price the same railway evaluation")
            if not isclose(old_energy / gwh, row["selected_annual_opex_usd_m"]["energy"] / supply["annual_grid_gwh"]):
                raise ValueError("Electricity credit must match the chosen service")
            cases = {}
            for name, index, cost_case in SCENARIOS:
                pay = study["iraq_payroll"]["cases"][cost_case]["goa4"]
                occupancy = demand["occupancy"][index]
                passenger_km = km * service["normal_places_per_train"] * occupancy
                paid_m = (passenger_km / trip["average_rail_leg_km"] / trip["legs_per_linked_journey"]
                          * demand["paying_share_of_linked_journeys"] / 1e6)
                posted = market["fare"]["posted_iqd"][index]
                net_iqd = posted * market["fare"]["receipt_fraction"][index]
                energy_cost = gwh * energy[cost_case]["delivered_usd_per_kwh"]
                opex = pay["annual_opex_usd_m_year"] - old_energy + energy_cost
                installed = capital[network]["cases"][cost_case]["installed_capital_usd_m"]
                cases[name] = dict(installed_m=installed, capital_factor=installed / reference, paid_m=paid_m, occupancy=occupancy, posted_iqd=posted,
                                   whole_life_m=installed + opex * operating_factor + renewal_pv,
                                   net_iqd=net_iqd, net_usd=net_iqd / fx, farebox_m=paid_m * net_iqd / fx,
                                   opex_m=opex, power_m=energy_cost, payroll_m=pay["payroll_usd_m_year"])
            result[network][offer] = cases
    return result


def report(cases):
    finance = json.loads((CITY / "financing-scenarios.json").read_bytes())["networks"]
    market = tomllib.loads((CITY / "iraq-market.toml").read_text())
    fare, demand = market["fare"], market["demand"]
    first, metro = demand["first"], demand["metropolitan"]
    fx = market["currency"]["iqd_per_usd"]
    central = cases["first"]["full"]["central"]
    daily = round(central["paid_m"] * 1e6 / 365 / 1000) * 1000
    lines = ["# What Baghdad would pay to run the railway", "",
             f"The central planning case assumes a flat IQD {central['posted_iqd']:,} ticket. For the seven corridors it puts the first full year at "
             f"about {daily:,} paid journeys a day. The funding table uses annual average traffic, Iraqi pay and electricity rates, "
             "and 50% borrowing at 4% real over 20 years. Each network is a separate investment. Amounts are millions of constant 2026 US dollars.", "",
             "| Network and service | Funding case | Construction | Paid journeys/year (m) | Wage bill | Electricity | Total operations | Fare receipts | Public funding incl. debt |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for network, offers in cases.items():
        scenario = finance[network]["cases"]["mixed_debt"]
        opening = next(row for row in scenario["annual"] if row["operations"] > 0)
        for offer, values in offers.items():
            title = "Seven corridors" if network == "first" else ("Citywide, full offer" if offer == "full" else "Citywide, main routes")
            for name, case in values.items():
                gap = ((opening["interest"] + opening["principal"]) * case["capital_factor"]
                       + opening["renewals"] + case["opex_m"] - case["farebox_m"])
                lines.append(f"| {title} | {name.title()} | {case['installed_m']:,.0f} | {case['paid_m']:,.1f} | {case['payroll_m']:,.1f} | "
                             f"{case['power_m']:,.1f} | {case['opex_m']:,.1f} | {case['farebox_m']:,.1f} | {gap:,.1f} |")
    citywide = cases["metropolitan"]["full"]["central"]
    lines += ["", f"Over 30 years the central present cost is **${central['whole_life_m']/1000:.2f}bn** for the seven corridors "
              f"and **${citywide['whole_life_m']/1000:.2f}bn** for full citywide service. This comparison takes construction at face value "
              "and discounts annual operations and the original scheduled renewal allowances by 4% real from service opening. "
              "Interest and fares are accounted for in the buyer cash comparison above.", "", "## How to read the estimates", "",
              f"Iraq’s 2024 land transport statistics report an average IQD {fare['bus_comparator_iqd']:,} ticket for internal Baghdad government bus services (table 7). "
              f"The downside, central and upside posted rail tickets are {', '.join(f'IQD {p:,}' for p in fare['posted_iqd'])}. "
              f"After paid discounts and collection costs the operator retains {', '.join(f'{p:.0%}' for p in fare['receipt_fraction'])} respectively. "
              f"At IQD {fx:,} per US dollar the central net receipt is IQD {central['net_iqd']:g}, or ${central['net_usd']:.3f}. "
              f"[Iraqi transport statistics]({market['fare']['source']}) · [Central Bank selling rate to banks, October 2026]({market['currency']['source']})",
              "", f"Assumed all-day occupancy is {', '.join(f'{p:.0%}' for p in demand['occupancy'])} of the scheduled place-kilometres. "
              f"The seven-corridor estimate assumes {first['average_rail_leg_km']} km per rail leg and {first['legs_per_linked_journey']} legs per linked journey. "
              f"Citywide assumes {metro['average_rail_leg_km']} km and {metro['legs_per_linked_journey']} legs. "
              f"A passenger changing trains counts once towards fare revenue. An assumed {demand['paying_share_of_linked_journeys']:.0%} of linked journeys pay. "
              "These are opening-year planning judgements. Baghdad origin–destination research on earlier proposed lines gives local demand context. "
              f"Station catchment counts, measured trip lengths and a fare survey would allow the operator to refine the figures. [Baghdad transport study]({market['demand']['baghdad_comparator']})",
              "", "Operations include the estimated unattended-service wage bill once. The model replaces the payroll already allowed in train, station and power maintenance costs and replaces the original electricity allowance for the same mileage. "
              "The downside combines higher construction, recruitment and power costs with weaker fare income. The upside combines lower costs with stronger income. These are joint sensitivities, with no assigned probabilities. "
              "The main-route service defers five access sections while retaining the cost of the full citywide infrastructure. [Pay and staffing](../../docs/operator-review/delivery/README.md) · [Power prices and local supply](IRAQ-POWER.md)",
              "", "The public funding column covers operations and scheduled debt payments less collected fares in the first full service year. "
              "The loan share applies to each construction estimate, using the original timing of annual draws. The buyer also funds its construction share and later renewals. Iraq’s $930m World Bank national railway project is a precedent for seeking multilateral finance. The metro rates and terms here are assumptions awaiting lender offers. "
              "[Construction prices for both networks](IRAQ-CAPITAL.md) · [Iraq railway investment](https://www.worldbank.org/en/news/press-release/2025/06/25/iraq-new-us-930-million-project-to-extend-and-modernize-railways-promote-regional-connectivity-and-boost-growth) · [Change terms and fares](../../docs/operator-review/finance/index.html) · [Airport opening construction estimate](AIRPORT-OPENING.md)", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = CITY / "IRAQ-ESTIMATES.md"
    content = report(funding_cases())
    if args.check:
        if output.read_text() != content:
            raise SystemExit("Refresh the Baghdad funding estimates")
    else:
        output.write_text(content)
