"""Estimate domestic value within Iraqi-awarded packages for each Baghdad network."""
import argparse
from hashlib import sha256
import json
from math import isclose
from pathlib import Path
import sys

CITY = Path(__file__).resolve().parent
ROOT = CITY.parents[1]
sys.path.insert(0, str(ROOT))

from cities.Baghdad import iraq_power
from engineering.performance import check_disk_reservation, disk_reservation

# Fraction of an Iraqi-awarded package retained after imports and transfers.
# Each tuple gives the buyer's low/base/high planning assumptions.
RETENTION = {
    "elevated_civil": ("Elevated civil works", (.60, .75, .85)),
    "stations_access": ("Stations and access", (.50, .65, .80)),
    "track_walkways": ("Track and walkways", (.30, .45, .60)),
    "signalling_comms": ("Signalling and communications", (.15, .30, .45)),
    "brake_protection_recovery": ("Brake protection and recovery", (.15, .30, .45)),
    "line_traction_supply": ("Line traction supply", (.25, .40, .55)),
    "vehicles": ("Complete trains", (.20, .35, .50)),
    "depots_control": ("Depots and control centres", (.40, .55, .70)),
    "tooling_recovery": ("Tooling and recovery", (.30, .45, .60)),
    "design_assurance": ("Design and assurance", (.50, .65, .80)),
    "testing_commissioning": ("Testing and commissioning", (.45, .60, .75)),
}

# Only utility diversions and reinstatement produce new goods/services.
# The remaining provisional share covers land and compensation transfers.
UTILITY_WORK_SHARE = (.25, .45, .65)
UTILITY_WORK_RETENTION = (.55, .75, .90)


def work_types(grid_sites):
    work = {key: (label, dict(zip(iraq_power.CASES, values)))
            for key, (label, values) in RETENTION.items()}
    work["land_utilities_disruption"] = ("Land, utilities and disruption", {
        case: share * local for case, share, local in
        zip(iraq_power.CASES, UTILITY_WORK_SHARE, UTILITY_WORK_RETENTION)})
    work["grid_charging_buffers"] = ("Grid supply sites", {
        case: site["estimated_domestic_usd_m"] / site["direct_usd_m"]
        for case, site in grid_sites.items()})
    return work


def estimate(network, awards, work):
    scope = network["selected_capital_scope_usd_m"]
    excluded = scope["project_allowance"]
    if set(scope) - {"project_allowance"} != set(awards) or set(work) != set(awards):
        raise ValueError("Iraqi award targets and retained-value assumptions must cover all priced scopes")
    case = network["power_cases"][network["digital_cost_leader"]]
    if case["physical_candidate_id"] != network["selected_candidate_id"]:
        raise ValueError("Selected candidate and estimated capital differ")
    if not isclose(sum(scope.values()), case["installed_capital_usd_m"]):
        raise ValueError("Costed packages do not reconcile to selected installed capital")
    packages = {}
    for key, (label, shares) in work.items():
        if not (0 <= awards[key] <= 1 and 0 <= shares["low"] <= shares["base"] <= shares["high"] <= 1):
            raise ValueError(f"Invalid Iraqi award or retention share for {key}")
        local_award = scope[key] * awards[key]
        packages[key] = {"label": label, "price_usd_m": scope[key], "award_fraction": awards[key],
                         "iraqi_award_usd_m": local_award, "retained_fraction_of_award": shares,
                         "retained_usd_m": {k: local_award * f for k, f in shares.items()}}
    opportunity = sum(p["iraqi_award_usd_m"] for p in packages.values())
    published = network["selected_local_delivery"]
    if published:
        for key, package in packages.items():
            if not isclose(published["scope_local_contract_usd_m"][key], package["iraqi_award_usd_m"]):
                raise ValueError(f"{key} differs from the published Iraqi contract opportunity")
    totals = {case: sum(p["retained_usd_m"][case] for p in packages.values()) for case in iraq_power.CASES}
    return {"candidate_id": network["selected_candidate_id"], "evaluation_id": network["selected_evaluation_id"],
            "award_basis": "network targets" if published else "transferred metropolitan scope targets",
            "installed_capital_usd_m": sum(scope.values()), "unassigned_allowance_usd_m": excluded,
            "comparable_price_usd_m": sum(scope.values()) - excluded, "iraqi_award_usd_m": opportunity,
            "retained_usd_m": totals, "packages": packages}


def build():
    cfg = iraq_power.read_toml("system.toml")
    baseline = json.loads((CITY / "system-results.json").read_bytes())
    if baseline["candidate_id"] != cfg["candidate_id"]:
        raise ValueError("Selected city ledger and award assumptions differ")
    pricing = iraq_power.build()
    work = work_types(pricing["supply_site_estimates"])
    networks = {}
    for key, network in baseline["networks"].items():
        awards = cfg["networks"][key].get("local_contract_fraction",
                                          cfg["networks"]["metropolitan"]["local_contract_fraction"])
        networks[key] = estimate(network, awards, work)
    inputs = {"power_evaluation": pricing["evaluation_id"],
              "localisation_source_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}
    return {"evaluation_id": sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
            "inputs": inputs, "networks": networks}


def guide(result, original):
    lines = ["| Network | Installed price $bn | Unassigned contingency $bn | Priced scope $bn | "
             "Iraqi award $bn (% of priced scope) | Value retained in Iraq low / base / high $bn | "
             "Retained % of priced scope |", "|---|---:|---:|---:|---:|---:|---:|"]
    networks = result["networks"]
    for key, n in networks.items():
        price = n["comparable_price_usd_m"]
        values = n["retained_usd_m"].values()
        domestic = " / ".join(f"{x / 1000:.2f}" for x in values)
        shares = " / ".join(f"{100 * x / price:.1f}%" for x in values)
        award = n["iraqi_award_usd_m"]
        lines.append(f"| {key.title()} | {n['installed_capital_usd_m']/1000:.3f} | "
                     f"{n['unassigned_allowance_usd_m']/1000:.3f} | {price/1000:.3f} | "
                     f"{award/1000:.3f} ({100 * award / price:.1f}%) | {domestic} | {shares} |")
    lines += ["", "| Scope | Target Iraqi award | Retained % of Iraqi award, low / base / high | "
              "First network award / base retained $m | Metropolitan award / base retained $m |",
              "|---|---:|---:|---:|---:|"]
    for key, p in networks["first"]["packages"].items():
        metro = networks["metropolitan"]["packages"][key]
        percentages = " / ".join(f"{100 * x:.1f}%" for x in p["retained_fraction_of_award"].values())
        target = f"{100 * p['award_fraction']:.0f}%"
        if p["award_fraction"] != metro["award_fraction"]:
            target += f" / {100 * metro['award_fraction']:.0f}%"
        lines.append(f"| {p['label']} | {target} | {percentages} | "
                     f"{p['iraqi_award_usd_m']:,.1f} / {p['retained_usd_m']['base']:,.1f} | "
                     f"{metro['iraqi_award_usd_m']:,.1f} / {metro['retained_usd_m']['base']:,.1f} |")
    start, end = "<!-- Iraqi award estimates -->", "<!-- end Iraqi award estimates -->"
    before, remaining = original.split(start)
    _, after = remaining.split(end)
    return before + start + "\n\n" + "\n".join(lines) + "\n\n" + end + after


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--write", action="store_true")
    args = parser.parse_args()
    record = build()
    if args.write or args.check:
        path = CITY / "BUYER-COMPARISON.md"
        contents = path.read_text()
        updated = guide(record, contents)
        if contents != updated:
            if args.check:
                raise SystemExit("Regenerate buyer localisation estimates with --write")
            with disk_reservation(ROOT, CITY, "Baghdad buyer local value estimates", 65536) as lease:
                check_disk_reservation(lease)
                path.write_text(updated)
    else:
        print(json.dumps(record, indent=2))
