"""Iraqi market estimate of both Baghdad alternatives on the published quantity basis."""
import argparse
from hashlib import sha256
import json
from math import isclose
from pathlib import Path
import sys

CITY = Path(__file__).resolve().parent
ROOT = CITY.parents[1]
sys.path.insert(0, str(ROOT))
from cities.Baghdad import iraq_power, localisation
from engineering.performance import check_disk_reservation, disk_reservation

CASES = iraq_power.CASES
CIVIL_STUDY = "engineering/mechanical/civil/section-results.json"


def unit_rates(cfg, study, evidence, assumptions, site_prices, fx, index):
    civil = assumptions["civil"]
    market = evidence["materials"]
    price_iqd_m3 = (civil["cement_t_per_m3"] * market["resistant_cement_iqd_t"]
                    + civil["rebar_t_per_m3"][index] * market["reinforcing_steel_iqd_t"]
                    + civil["sand_m3_per_m3"] * market["sand_iqd_m3"]
                    + civil["gravel_m3_per_m3"] * market["crushed_gravel_iqd_m3"])
    beam_m3 = study["track"]["gross_concrete_m3"]
    pier = study["track"]["pier_gravity_screen"]
    pier_m3 = sum(pier[k] for k in ("column_volume_m3", "cap_volume_m3", "footing_volume_m3"))
    rail = evidence["rail"]
    station = assumptions["stations"]
    train = assumptions["trains"]
    routes = assumptions["route"]
    facilities = assumptions["facilities"]
    road = evidence["corridor"]
    return {
        "reinforced_material_usd_m3": price_iqd_m3 / fx,
        "beam_usd_each": beam_m3 * price_iqd_m3 / fx + civil["beam_fabrication_and_delivery_usd_each"][index],
        "pier_foundation_usd_each": pier_m3 * price_iqd_m3 / fx + civil["support_works_usd_each"][index],
        "placement_usd_each": civil["lift_usd_each"][index],
        "other_civil_usd_m_route_km": civil["other_civil_usd_m_per_route_km"][index],
        "station_usd_m_each": sum(station[k][index] for k in ("civil_and_finishes",
                                   "electromechanical_and_platform_equipment", "public_access_and_egress")),
        "trainset_usd_m_each": (cfg["vehicle"]["cars_per_train"] * train["contract_eur_m"] / train["contract_cars"]
                                * train["award_usd_per_eur"] * train["delivered_price_factor"][index]),
        "track_walkways_usd_m_track_km": (rail["renewal_estimate_usd"] / 1e6 / rail["renewal_km"]
                                          * routes["track_walkway_factor_on_iraq_renewal"][index]),
        "land_utilities_usd_m_route_km": (road["comparator_iqd"] / fx / 1e6 / road["comparator_km"]
                                          * routes["land_utilities_share_of_baghdad_road_per_km"][index]),
        "grid_site_usd_m_each": site_prices[CASES[index]]["direct_usd_m"],
        "line_supply_equipment_factor": routes["line_traction_supply_factor_on_published_equipment"][index],
        "signalling_usd_m_route_km": routes["signalling_usd_m_per_route_km"][index],
        "brake_usd_m_route_km": routes["brake_recovery_usd_m_per_route_km"][index],
        **{key: values[index] for key, values in facilities.items()},
    }


def estimate(cfg, key, network, rates, fx):
    quantities = cfg["networks"][key]
    protected = network["power_cases"]["protected_conductor"]
    if (network["selected_digital_civil_family"] != "10m-separate" or
        network["digital_cost_leader"] != "protected_conductor" or
        network["selected_candidate_id"] != protected["physical_candidate_id"]):
        raise ValueError("Market comparison requires the selected independent spans and protected conductor")
    civil = network["civil_cases"]["10m-separate"]
    if (civil["beam_count"], civil["pier_foundation_count"]) != (protected["civil_beams"], protected["civil_piers"]):
        raise ValueError("Civil quantities differ from the selected train and supply option")
    km = network["elevated_route_km"]
    if not isclose(km, quantities["route_km"]):
        raise ValueError("An underground or at-grade alignment requires matching rates")
    scope = {
        "elevated_civil": (civil["beam_count"] * (rates["beam_usd_each"] + rates["placement_usd_each"])
                           + civil["pier_foundation_count"] * rates["pier_foundation_usd_each"]) / 1e6
                          + km * rates["other_civil_usd_m_route_km"],
        "stations_access": quantities["stations"] * rates["station_usd_m_each"],
        "track_walkways": km * cfg["track_count"] * rates["track_walkways_usd_m_track_km"],
        "signalling_comms": km * rates["signalling_usd_m_route_km"],
        "brake_protection_recovery": km * rates["brake_usd_m_route_km"],
        "line_traction_supply": network["selected_capital_scope_usd_m"]["line_traction_supply"] * rates["line_supply_equipment_factor"],
        "grid_charging_buffers": quantities["traction_supply_sites"] * rates["grid_site_usd_m_each"],
        "vehicles": quantities["fleet_trainsets"] * rates["trainset_usd_m_each"],
        "depots_control": quantities["depots"] * rates["depot_usd_m_each"] + quantities["control_centres"] * rates["control_centre_usd_m_each"],
        "land_utilities_disruption": km * rates["land_utilities_usd_m_route_km"],
        "tooling_recovery": rates["tooling_fixed_usd_m"] + km * rates["tooling_usd_m_per_route_km"],
    }
    direct = sum(scope.values())
    plan = cfg["capital_rates_usd_m"]
    scope["design_assurance"] = direct * plan["design_fraction"]
    scope["testing_commissioning"] = direct * plan["testing_fraction"]
    scope["project_allowance"] = sum(scope.values()) * plan["project_allowance_fraction"]
    if scope.keys() != network["selected_capital_scope_usd_m"].keys():
        raise ValueError("Capital estimate requires a rate for every published package")
    installed = sum(scope.values())
    cash = [{"year": quantities["construction_start_year"] + i, "installed_usd_m": weight * installed}
            for i, weight in enumerate(quantities["construction_cash_weights"])]
    if not isclose(sum(r["installed_usd_m"] for r in cash), installed):
        raise ValueError("Construction draws must sum to installed capital")
    return {"installed_capital_usd_m": installed, "installed_capital_iqd_trillion": installed * fx / 1e6,
            "direct_capital_usd_m": direct, "scope_usd_m": scope, "construction_years": cash,
            "change_from_reference_usd_m": installed - protected["installed_capital_usd_m"]}


def build():
    cfg = iraq_power.read_toml("system.toml")
    published = json.loads((CITY / "system-results.json").read_bytes())
    if published["candidate_id"] != cfg["candidate_id"]:
        raise ValueError("Published and input network designs differ")
    study = json.loads((CITY / CIVIL_STUDY).read_bytes())
    if study["source_sha256"]["system.toml"] != sha256((CITY / "system.toml").read_bytes()).hexdigest():
        raise ValueError("Representative beam and pier quotation study requires review for this system")
    assumptions = iraq_power.read_toml("iraq-capital.toml")
    evidence = iraq_power.read_toml("airport-works.toml")
    fx = iraq_power.read_toml("iraq-market.toml")["currency"]["iqd_per_usd"]
    power = iraq_power.build()
    sites = power["supply_site_estimates"]
    local_work = localisation.work_types(sites)
    rates = {case: unit_rates(cfg, study, evidence, assumptions, sites, fx, index)
             for index, case in enumerate(CASES)}
    results = {}
    for key, row in published["networks"].items():
        cases = {case: estimate(cfg, key, row, rate, fx) for case, rate in rates.items()}
        base = cases["base"]["scope_usd_m"]
        target = cfg["networks"][key].get("local_contract_fraction",
                                          cfg["networks"]["metropolitan"]["local_contract_fraction"])
        if set(base) - {"project_allowance"} != set(target) or set(target) != set(local_work):
            raise ValueError("Domestic value comparison requires all matched scope targets")
        awards = {k: base[k] * share for k, share in target.items()}
        domestic = {k: amount * local_work[k][1]["base"] for k, amount in awards.items()}
        results[key] = {"candidate_id": row["selected_candidate_id"], "evaluation_id": row["selected_evaluation_id"],
                        "reference_installed_usd_m": row["power_cases"]["protected_conductor"]["installed_capital_usd_m"],
                        "central_iraqi_award_usd_m": sum(awards.values()), "central_retained_usd_m": sum(domestic.values()),
                        "central_iraqi_award_by_scope_usd_m": awards, "central_retained_by_scope_usd_m": domestic,
                        "cases": cases}
    inputs = {name: sha256((CITY / name).read_bytes()).hexdigest() for name in
              ("iraq-capital.toml", "airport-works.toml", CIVIL_STUDY, "iraq_capital.py", "localisation.py")}
    inputs["parent_power_evaluation"] = power["evaluation_id"]
    return {"evaluation_id": sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
            "inputs": inputs, "iqd_per_usd": fx, "unit_rates": rates, "networks": results}


def guide(result, original):
    lines = ["| Independent network | Common bid control $bn | Iraq installed $bn, low / base / high | "
             "IQD trillion, low / base / high | Base Iraqi award / domestic value within award $bn |",
             "|---|---:|---:|---:|---:|"]
    for key, n in result["networks"].items():
        usd = " / ".join(f"{row['installed_capital_usd_m']/1000:.3f}" for row in n["cases"].values())
        iqd = " / ".join(f"{row['installed_capital_iqd_trillion']:.2f}" for row in n["cases"].values())
        lines.append(f"| {key.title()} | {n['reference_installed_usd_m']/1000:.3f} | {usd} | {iqd} | "
                     f"{n['central_iraqi_award_usd_m']/1000:.3f} / {n['central_retained_usd_m']/1000:.3f} |")
    lines += ["", "| Matched package | First $m, low / base / high | Metropolitan $m, low / base / high |",
              "|---|---:|---:|"]
    labels = {k: v[0] for k, v in localisation.RETENTION.items()}
    labels.update(grid_charging_buffers="Grid supply sites", land_utilities_disruption="Land, utilities and disruption",
                  project_allowance="Project contingency")
    networks = result["networks"]
    for name in networks["first"]["cases"]["base"]["scope_usd_m"]:
        amounts = [" / ".join(f"{case['scope_usd_m'][name]:,.1f}" for case in n["cases"].values())
                   for n in networks.values()]
        lines.append(f"| {labels[name]} | " + " | ".join(amounts) + " |")
    start, end = "<!-- Iraq capital tables -->", "<!-- end Iraq capital tables -->"
    before, rest = original.split(start)
    _, after = rest.split(end)
    return before + start + "\n\n" + "\n".join(lines) + "\n\n" + end + after


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--write", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write or args.check:
        path = CITY / "IRAQ-CAPITAL.md"
        original = path.read_text()
        updated = guide(result, original)
        if updated != original:
            if args.check:
                raise SystemExit("Regenerate capital tables with --write")
            with disk_reservation(ROOT, CITY, "Baghdad installed capital market estimate", 65536) as lease:
                check_disk_reservation(lease)
                path.write_text(updated)
    else:
        print(json.dumps(result, indent=2))
