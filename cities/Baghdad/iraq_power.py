"""Price Baghdad's published operating duty and traction supply sites for an Iraqi buyer."""
import argparse
from hashlib import sha256
import json
from math import isclose
from pathlib import Path
import sys
import tomllib

CITY = Path(__file__).resolve().parent
ROOT = CITY.parents[1]
sys.path.insert(0, str(ROOT))

from engineering.performance import check_disk_reservation, disk_reservation

CASES = ("low", "base", "high")


def read_toml(name):
    with (CITY / name).open("rb") as source:
        return tomllib.load(source)


def rates():
    assumptions = read_toml("iraq-power.toml")["energy"]
    exchange = read_toml("iraq-market.toml")["currency"]["iqd_per_usd"]
    alternate = assumptions["alternate_supply_usd_per_kwh"]
    result = {}
    for case in CASES:
        inputs = assumptions[case]
        grid = assumptions[inputs["grid_class"] + "_iqd_per_kwh"]
        fraction = inputs["alternate_kwh_fraction"]
        if not 0 <= fraction <= 1:
            raise ValueError(f"Invalid alternate-supply fraction for {case}")
        blended = (1 - fraction) * grid + fraction * alternate * exchange
        result[case] = {
            "grid_iqd_per_kwh": grid, "alternate_kwh_fraction": fraction,
            "delivered_usd_per_kwh": blended / exchange, "delivered_iqd_per_kwh": blended,
        }
    return result


def site_estimates(assumptions, exchange):
    prices = [row["iqd"] / row["sites"] / exchange / 1e6 for row in assumptions["contracts"]]
    anchors = {"low": min(prices), "base": sum(prices) / len(prices), "high": max(prices)}
    result = {}
    for case, anchor in anchors.items():
        inputs = assumptions[case]
        parts = {"ac_equipment": anchor * (1 + inputs["uplift"]),
                 "site_works": inputs["site_works_usd_m"], "railway_plant": sum(inputs["railway_plant_usd_m"].values())}
        local = sum(cost * inputs["local_share"][part] for part, cost in parts.items())
        result[case] = {"parts_usd_m": parts, "direct_usd_m": sum(parts.values()),
                        "estimated_domestic_usd_m": local}
    return result


def build():
    cfg = read_toml("system.toml")
    ledger = json.loads((CITY / "system-results.json").read_bytes())
    if ledger["candidate_id"] != cfg["candidate_id"]:
        raise ValueError("Published Baghdad candidate differs from system inputs")
    exchange = read_toml("iraq-market.toml")["currency"]["iqd_per_usd"]
    energy = rates()
    sites = site_estimates(read_toml("iraq-power.toml")["equipment"], exchange)
    base_rate = cfg["operation_rates"]["delivered_energy_usd_per_kwh"]
    factor = sum((1 + cfg["discount_rate_real"]) ** -year for year in range(1, cfg["comparison_years"] + 1))
    networks = {}
    for key, row in ledger["networks"].items():
        selected = row["power_cases"]["protected_conductor"]
        if (row["digital_cost_leader"] != "protected_conductor" or
                row["selected_candidate_id"] != selected["physical_candidate_id"]):
            raise ValueError(f"{key} needs a new scope comparison for its selected supply")
        gwh = selected["annual_grid_gwh"]
        old_energy = row["selected_annual_opex_usd_m"]["energy"]
        if not isclose(old_energy, gwh * base_rate):
            raise ValueError(f"{key} published energy allowance and purchase quantity disagree")
        count = cfg["networks"][key]["traction_supply_sites"]
        included = row["selected_capital_scope_usd_m"]["grid_charging_buffers"]
        if not isclose(included, count * cfg["capital_rates_usd_m"]["traction_supply_site"]):
            raise ValueError(f"{key} grid capital includes additional capacity or buffers requiring review")
        service_hours = cfg["vehicle"]["service_days_per_year"] * cfg["vehicle"]["service_hours_per_day"]
        request_mw = gwh * 1000 / service_hours * cfg["power_assumptions"]["grid_peak_over_service_mean"]
        overhead = row["power_cases"]["overhead"]
        cases = {}
        for case in CASES:
            price = energy[case]["delivered_usd_per_kwh"]
            advantage = (overhead["whole_life_30y_present_usd_m"] - selected["whole_life_30y_present_usd_m"]
                         + (overhead["annual_grid_gwh"] - gwh) * (price - base_rate) * factor)
            cases[case] = {"annual_energy_usd_m": gwh * price,
                           "annual_energy_change_usd_m": gwh * price - old_energy,
                           "overhead_minus_conductor_30y_usd_m": advantage,
                           "direct_supply_sites_usd_m": sites[case]["direct_usd_m"] * count,
                           "estimated_domestic_sites_usd_m": sites[case]["estimated_domestic_usd_m"] * count}
        networks[key] = {"candidate_id": selected["physical_candidate_id"],
                         "evaluation_id": row["selected_evaluation_id"],
                         "overhead_candidate_id": overhead["physical_candidate_id"],
                         "annual_grid_gwh": gwh, "annual_train_km": row["selected_service_allowance"]["annual_train_km"],
                         "planning_grid_request_mw": request_mw, "supply_sites": count, "existing_grid_scope_usd_m": included, "cases": cases}
    inputs = {name: sha256((CITY / name).read_bytes()).hexdigest() for name in
              ("system.toml", "system-results.json", "iraq-power.toml", "iraq_power.py")}
    inputs["exchange_iqd_per_usd"] = exchange
    evaluation = sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    return {"evaluation_id": evaluation, "inputs": inputs, "energy_rates": energy,
            "supply_site_estimates": sites, "networks": networks}


def tables(record):
    lines = [
        "| Network | Electricity case | IQD/kWh | Energy $m/year | Change from ledger $m/year | "
        "30-year overhead premium after repricing energy, $m |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for key, network in record["networks"].items():
        for case, row in network["cases"].items():
            price = record["energy_rates"][case]["delivered_iqd_per_kwh"]
            lines.append(f"| {key.title()} | {case.title()} | {price:.1f} | {row['annual_energy_usd_m']:,.1f} | "
                         f"{row['annual_energy_change_usd_m']:+,.1f} | {row['overhead_minus_conductor_30y_usd_m']:,.1f} |")
    lines += ["", "| Network | Site count | Grid request MW | Present direct allowance $m | "
              "Direct sites low / base / high $m | Domestic value low / base / high $m |",
              "|---|---:|---:|---:|---:|---:|"]
    for key, network in record["networks"].items():
        totals = " / ".join(f"{r['direct_supply_sites_usd_m']:,.1f}" for r in network["cases"].values())
        domestic = " / ".join(f"{r['estimated_domestic_sites_usd_m']:,.1f}" for r in network["cases"].values())
        lines.append(f"| {key.title()} | {network['supply_sites']} | {network['planning_grid_request_mw']:,.1f} | "
                     f"{network['existing_grid_scope_usd_m']:,.1f} | {totals} | {domestic} |")
    return "\n".join(lines)


def guide(record, original):
    start, end = "<!-- calculated tables -->", "<!-- end calculated tables -->"
    before, remaining = original.split(start)
    _, after = remaining.split(end)
    return before + start + "\n\n" + tables(record) + "\n\n" + end + after


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group()
    options.add_argument("--write", action="store_true", help="Update the cost tables in the operator guide")
    options.add_argument("--check", action="store_true", help="Check the operator guide against the current inputs")
    args = parser.parse_args()
    record = build()
    if args.write or args.check:
        path = CITY / "IRAQ-POWER.md"
        original = path.read_text()
        updated = guide(record, original)
        if updated != original:
            if args.check:
                raise SystemExit("Regenerate the Iraq power cost tables with --write")
            with disk_reservation(ROOT, CITY, "Baghdad electricity and supply site pricing", 65536) as lease:
                check_disk_reservation(lease)
                path.write_text(updated)
    else:
        print(json.dumps(record, indent=2))
