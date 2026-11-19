"""Prepare a Baghdad quotation return or compare a matched return with first-network capital."""
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import tomllib

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[1]
ROOT = CITY.parents[1]


def verified_record(path, base, register="source_sha256"):
    record = json.loads(path.read_text())
    for source, digest in record[register].items():
        if sha256((base / source).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Rebuild {path.name} after change to {source}")
    return record


def estimate():
    cfg = tomllib.loads((CITY / "system.toml").read_text())
    system = verified_record(CITY / "system-results.json", ROOT)
    parent = json.loads((HERE / "schedule.json").read_text())
    vehicle = verified_record(HERE / "vehicle/result.json", ROOT)
    civil = verified_record(HERE / "civil/section-results.json", CITY)
    network = system["networks"]["first"]
    case = network["power_cases"]["protected_conductor"]
    family = network["civil_cases"]["10m-separate"]
    if (parent["network"] != "first" or network["digital_cost_leader"] != "protected_conductor"
            or network["selected_digital_civil_family"] != "10m-separate"
            or network["selected_candidate_id"] != vehicle["parent_train_id"]
            or parent["parent_selected_candidate_id"] != network["selected_candidate_id"]
            or parent["parent_evaluation_id"] != network["selected_evaluation_id"]
            or vehicle["parent_interface_study_id"] != parent["study_physical_id"]
            or civil["parent_physical_id"] != parent["study_physical_id"]
            or civil["parent_evaluation_id"] != parent["study_evaluation_id"]):
        raise ValueError("Quotation articles and capital must share the first-network parent")
    identity = {
        "network": "first", "currency": cfg["currency"], "price_year": cfg["price_year"],
        "candidate": network["selected_candidate_id"], "cost_evaluation": network["selected_evaluation_id"],
        "frame_revision": vehicle["braced_revision_id"], "civil_revision": civil["physical_id"],
    }
    fleet = network["selected_service_allowance"]["fleet_trainsets"]
    cars = cfg["vehicle"]["cars_per_train"]
    frame_kg = vehicle["braced_body_and_two_bogie_cut_stock_kg_per_car"]
    construction = network["selected_civil_delivery"]
    quantities = {
        "complete_trainsets": fleet, "cars": fleet * cars, "bogie_frames": fleet * cars * 2,
        "trial_cut_stock_kg_per_train": round(cars * frame_kg, 3),
        "complete_installed_train_tare_kg": None,
        "cost_model_loaded_train_t": case["train_crowd_mass_t"],
        "beams": family["beam_count"], "support_positions": family["pier_foundation_count"],
        "concrete_m3_per_trial_running_beam": civil["track"]["gross_concrete_m3"],
        "equivalent_stock_t_per_trial_running_beam": civil["track"]["equivalent_stock_t"],
        "cost_model_hook_surrogate_t": family["hook_surrogate_t_per_beam"],
        "platform_panels_per_uninterrupted_trial_island": civil["platform"]["panel_count_template"],
        "concrete_m3_per_trial_platform_panel": civil["platform"]["panel_volume_m3"],
        "budgeted_stations": network["stations_planning_allowance"],
        "casting_yards": construction["factory_yards_needed_at_declared_rate"],
        "erection_fronts": construction["erection_fronts_needed_at_declared_rate"],
        "additional_yard_and_front_cost_usd": construction["additional_yard_and_front_cost_usd"],
    }
    units = {"vehicles": fleet, "stations_access": quantities["budgeted_stations"], "elevated_civil": 1}
    return identity, quantities, units, network["selected_capital_scope_usd_m"], cfg["capital_rates_usd_m"]


def return_form(identity, units):
    return {"basis": dict(identity), "lots": {key: {
        "matched_units": 0, "cash_total_usd_m": None, "scope_review_reference": None
    } for key in units}}


def compare(form, identity, units, baseline, rates):
    if set(form) != {"basis", "lots"} or form["basis"] != identity or set(form["lots"]) != set(units):
        raise ValueError("Return must match the current quotation form, price year and design revisions")
    scopes = dict(baseline)
    changes = {}
    for scope, available in units.items():
        lot = form["lots"][scope]
        if set(lot) != {"matched_units", "cash_total_usd_m", "scope_review_reference"}:
            raise ValueError(f"Unrecognised fields for {scope}")
        count, cash, evidence = lot["matched_units"], lot["cash_total_usd_m"], lot["scope_review_reference"]
        if type(count) is not int or not 0 <= count <= available:
            raise ValueError(f"Invalid matched unit count in {scope}")
        if count == 0 and cash is None and evidence is None:
            continue
        if (not count or type(cash) not in (float, int) or not isfinite(cash) or cash <= 0
                or not isinstance(evidence, str) or not evidence.strip()):
            raise ValueError(f"{scope} needs matched units, a positive total cash price and scope review")
        displaced = baseline[scope] * count / available
        scopes[scope] += cash - displaced
        changes[scope] = {"matched_units": count, "displaced_allowance_usd_m": displaced,
                          "replacement_cash_usd_m": cash, "scope_review_reference": evidence}
    direct = sum(value for key, value in scopes.items()
                 if key not in {"design_assurance", "testing_commissioning", "project_allowance"})
    scopes["design_assurance"] = direct * rates["design_fraction"]
    scopes["testing_commissioning"] = direct * rates["testing_fraction"]
    scopes["project_allowance"] = (direct + scopes["design_assurance"]
                                   + scopes["testing_commissioning"]) * rates["project_allowance_fraction"]
    original = sum(baseline.values())
    return {"basis": identity, "matched_returns": changes, "scope_usd_m": scopes,
            "baseline_capital_usd_m": original, "comparison_capital_usd_m": sum(scopes.values()),
            "change_usd_m": sum(scopes.values()) - original}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    options = ap.add_mutually_exclusive_group()
    options.add_argument("--form", action="store_true", help="print an empty commercial return")
    options.add_argument("--compare", type=Path, help="read a completed JSON return")
    args = ap.parse_args()
    identity, quantities, units, scopes, rates = estimate()
    if args.form:
        result = return_form(identity, units)
    elif args.compare:
        try:
            result = compare(json.loads(args.compare.read_text()), identity, units, scopes, rates)
        except (KeyError, TypeError, ValueError, OSError) as exc:
            ap.error(str(exc))
    else:
        result = {"basis": identity, "quotation_quantities": quantities, "scope_usd_m": scopes,
                  "installed_capital_usd_m": sum(scopes.values())}
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
