"""Independently replay two corrected Airport working days through SUMO and pandapower."""

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

from cities.Baghdad.engineering.mechanical.civil import family_comparison
from cities.Baghdad.engineering.simulation import (
    airport_alignment, airport_demand, audit_production, corridor, motion_adapters, motion_evidence, motion_power,
    passengers, production, vehicle_audit,
)

ROOT = airport_alignment.ROOT
SCHEMA = "osr-baghdad-airport-audit-verification/2"
RECEIPT = Path(__file__).with_name("audit-verification.json")
CASE_TIMINGS = {
    "adverse_15min": (15, 330, None),
    "refined_30min": (30, 1308, 210),
}


def ordinary_inputs(label="adverse_15min"):
    headway, phase, positioning_slack = CASE_TIMINGS[label]
    alignment = airport_alignment.evaluate()
    demand = airport_demand.evaluate(alignment, headway_min=headway)
    vehicle = vehicle_audit.evaluate(cars=6, material="steel", alignment=alignment, grade_pct=0)
    mass = vehicle["mass_cases"]["central"]
    passenger = passengers.evaluate({
        "cars": 6, "headway_min": demand["headway_min"], "ambient_c": 40,
        "busiest_departure_load": math.ceil(demand["busiest_departure_load"]),
        "platform_queue": math.ceil(demand["platform_queue"]),
    })
    inputs = {
        "alignment": alignment, "demand_record": demand, "chainages_km": alignment["chainages_km"],
        "candidate_id": vehicle["candidate_id"], "headway_min": demand["headway_min"], "dwell_s": demand["dwell_s"],
        "cars": 6, "material": "steel", "topology": "paired6", "condition": "normal", "grade_pct": 0.0,
        "phase_s": phase,
        "loaded_train_kg": mass["loaded_train_kg"], "tare_train_kg": mass["tare_train_kg"],
        "auxiliary_kw": passenger["auxiliary_kw"],
    }
    if positioning_slack is not None:
        inputs["positioning_slack_s"] = positioning_slack
    return inputs, vehicle, passenger


def verify_inputs(inputs):
    references = motion_power.reference()
    demand = inputs["demand_record"]
    mutations = {
        "alignment_required": {"alignment": None},
        "bound_demand_required": {"demand_record": None},
        "ordered_chainages": {"chainages_km": [*inputs["chainages_km"][:-1], 12.0]},
        "demand_stop_order": {"demand_record": {**demand, "stop_ids": demand["stop_ids"][::-1]}},
        "demand_alignment": {"demand_record": {**demand, "alignment_id": "another-alignment"}},
        "headway": {"headway_min": 20, "phase_s": 0},
        "dwell": {"dwell_s": 36},
        "demand_factor": {"demand_factor": 1.1},
        "unsupported_headway": {"headway_min": 25},
        "unsupported_grade": {"grade_pct": 3},
        "unsupported_positioning_slack": {"positioning_slack_s": -1},
    }
    rejected = {}
    for key, override in mutations.items():
        try:
            motion_power.normalize({**inputs, **override}, references)
        except ValueError as error:
            rejected[key] = str(error)
        else:
            raise ValueError(f"Corrected motion accepted invalid input {key}")
    return rejected


def handoff(inputs, result, vehicle, passenger):
    demand = inputs["demand_record"]
    alignment = inputs["alignment"]
    case = result["scenario"]
    line_km = sum(b - a for a, b in zip(alignment["chainages_km"], alignment["chainages_km"][1:]))
    annual_km = result["metrics"]["distance_km"] * motion_power.reference()[0]["vehicle"]["service_days_per_year"]
    offered = demand["annual_all_journeys"] / airport_demand.SERVICE_DAY_COUNT
    bindings = {
        "physical_alignment": result["physical"]["alignment_id"] == alignment["alignment_id"],
        "physical_vehicle": result["physical"]["upstream_candidate_id"] == vehicle["candidate_id"],
        "service_demand": case["demand_evaluation_id"] == demand["evaluation_id"],
        "auxiliary_kw": case["aux_w"] == passenger["auxiliary_kw"] * 1000,
        "peak_full_mass": case["loaded_train_kg"] == vehicle["mass_cases"]["central"]["loaded_train_kg"],
        "feeder_chainages_m": list(result["physical"]["feeder"]["sites"]) == [km * 1000 for km in alignment["chainages_km"]],
        "route_length": math.isclose(case["chainages_m"][-1] / 1000, line_km, abs_tol=1e-9),
        "daily_od": math.isclose(result["metrics"]["offered_passengers"], offered, abs_tol=1e-5),
        "annual_distance": math.isclose(result["annual_train_km"], annual_km, abs_tol=1e-5),
        "price_scope_held": motion_power.unit_cost_basis(result)["status"] == "held",
        "economic_ranking_held": result["economic_ranking_eligible"] is False,
    }
    if not all(bindings.values()):
        raise ValueError(f"Corrected motion handoff failed {sorted(key for key, passed in bindings.items() if not passed)}")
    return bindings


def economics(inputs, result, vehicle):
    alignment, demand = inputs["alignment"], inputs["demand_record"]
    civil = family_comparison.evaluate_high_load(route_km=alignment["route_km"], installed_vehicle=vehicle)
    leader = civil["quotation_leaders"]["base"]
    girder = next(row for row in civil["rows"] if row["physical_id"] == leader["physical_id"])
    compact_day = motion_power.compact(result)
    compact_day["cost_scope"] = motion_power.unit_cost_basis(result)
    sealed_day = audit_production.seal_motion(compact_day)
    delivery = audit_production.evaluate(alignment, vehicle, sealed_day, girder, demand=demand,
                                         civil_evaluation_id=civil["evaluation_id"])
    tampered = {
        "demand_evaluation": audit_production.seal_motion({
            **compact_day, "scenario": {**compact_day["scenario"], "demand_evaluation_id": "other"},
        }),
        "vehicle_candidate": audit_production.seal_motion({
            **compact_day, "physical": {**compact_day["physical"], "upstream_candidate_id": "other"},
        }),
        "changed_energy_metric": {
            **sealed_day, "metrics": {**sealed_day["metrics"], "source_kwh": sealed_day["metrics"]["source_kwh"] + 1},
        },
        "changed_record_id": {**sealed_day, audit_production.MOTION_RECORD_ID: "0" * 64},
    }
    rejected = {}
    for key, moving_day in tampered.items():
        try:
            audit_production.evaluate(alignment, vehicle, moving_day, girder, demand=demand,
                                      civil_evaluation_id=civil["evaluation_id"])
        except ValueError as error:
            if key in ("changed_energy_metric", "changed_record_id") and "record identity does not match" not in str(error):
                raise ValueError(f"Corrected economics reported the wrong integrity failure for {key}") from error
            rejected[key] = str(error)
        else:
            raise ValueError(f"Corrected economics accepted invalid input {key}")
    operations = delivery["operation_basis"]
    days = operations["service_days"]
    case = motion_power.normalize(inputs)
    _, trips, _, _, positioning, terminal = motion_power.service(case)
    events = result["events"]
    expected_booked = {
        "passenger": len(trips) * alignment["route_km"] * days,
        "positioning": len(positioning) * alignment["route_km"] * days,
        "yard": sum(move["distance_km"] for move in terminal["yard_moves"]) * days,
    }
    expected_nonrevenue = {
        "positioning": {"booked": len(positioning), "completed": sum(e["kind"] == "positioning" for e in events)},
        "yard": {"booked": len(terminal["yard_moves"]), "completed": sum(e["kind"] == "yard" for e in events)},
    }
    expected_paid = (result["metrics"]["boarded_passengers"] * days
                     * demand["annual_paid_journeys"] / demand["annual_all_journeys"])
    if (delivery["child_ids"]["demand_evaluation_id"] != demand["evaluation_id"]
            or delivery["child_ids"]["motion_evaluation_id"] != result["evaluation_id"]
            or delivery["child_ids"]["motion_record_id"] != sealed_day[audit_production.MOTION_RECORD_ID]
            or not math.isclose(operations["annual_paid_journeys_proxy"], expected_paid)
            or not math.isclose(operations["annual_modelled_dc_source_kwh"], result["metrics"]["source_kwh"] * days)
            or not math.isclose(operations["operated_annual_train_km"], result["metrics"]["distance_km"] * days)
            or not math.isclose(operations["booked_annual_train_km"], sum(expected_booked.values()))
            or any(not math.isclose(operations["booked_annual_train_km_by_working"][kind], km, abs_tol=.001)
                   for kind, km in expected_booked.items())
            or operations["working_day_nonrevenue_trips"] != expected_nonrevenue
            or not math.isclose(delivery["quantities"]["track_km"], 2 * alignment["route_km"])
            or delivery["quantities"]["sets"] != result["metrics"]["fleet_sets_required"]
            or delivery["complete_installed_price_usd"] is not None
            or delivery["complete_owner_present_value_usd"] is not None):
        raise ValueError("Corrected production and owner cash failed their independent scope reconciliation")
    return {"civil_evaluation_id": civil["evaluation_id"], "delivery_evaluation_id": delivery["evaluation_id"],
            "provenance": delivery["child_ids"], "operation_basis": operations, "bound_quantities": delivery["quantities"],
            "feeder_scope": delivery["feeder_scope"], "rejected_inputs": rejected}


def source_digests():
    paths = [Path(__file__), *(Path(module.__file__) for module in (
        airport_alignment, airport_demand, audit_production, corridor, family_comparison, motion_adapters,
        motion_evidence, motion_power, passengers, production, vehicle_audit))]
    inputs, vehicle, passenger = ordinary_inputs()
    paths += [
        ROOT / key for sources in (inputs["demand_record"]["source_sha256"], vehicle["source_sha256"])
        for key in sources if (ROOT / key).is_file()
    ]
    paths += [corridor.CITY / key for key in passenger["source_sha256"]]
    paths += [corridor.CITY / key for key in ("iraq-capital.toml", "airport-works.toml", "iraq-market.toml")]
    paths += [family_comparison.HERE / "concept.toml", production.PROTOTYPE / "shop-rates.toml"]
    production_sources = production.sources()[-1]
    paths += [production.PROTOTYPE / key for key in production_sources if ":" not in key]
    return {**motion_evidence.source_digests(), **{
        str(path.resolve().relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in paths
    }}


def replay_case(label):
    inputs, vehicle, passenger = ordinary_inputs(label)
    rejected = verify_inputs(inputs)
    result = motion_power.evaluate(inputs)
    bindings = handoff(inputs, result, vehicle, passenger)
    check = motion_evidence.crosscheck(inputs, result)
    delivery = economics(inputs, result, vehicle)
    sumo = {key: value for key, value in check["sumo"].items() if key not in ("trace", "serialized_type_readback")}
    fields = (
        "booked_passenger_trips", "completed_passenger_trips", "offered_passengers", "boarded_passengers",
        "unserved_passengers", "demand_balance_residual_passengers", "maximum_arrival_delay_s",
        "nominal_timetable_conflicts", "minimum_collector_v", "peak_site_current_ka", "dc_balance_residual_kwh",
        "source_kwh", "distance_km", "booked_positioning_trips", "completed_positioning_trips",
        "booked_yard_trips", "completed_yard_trips",
    )
    record = {
        "case_label": label,
        "alignment_id": inputs["alignment"]["alignment_id"], "alignment_record_id": inputs["alignment"]["record_id"],
        "demand_evaluation_id": inputs["demand_record"]["evaluation_id"], "vehicle_candidate_id": vehicle["candidate_id"],
        "vehicle_evaluation_id": vehicle["evaluation_id"], "passenger_evaluation_id": passenger["evaluation_id"],
        "motion_candidate_id": result["candidate_id"], "motion_evaluation_id": result["evaluation_id"],
        "scenario": result["scenario"], "metrics": {key: result["metrics"][key] for key in fields},
        "motion_gates": result["gates"], "source_price_basis": motion_power.unit_cost_basis(result),
        "rejected_inputs": rejected, "handoff": bindings, "economics": delivery, "sumo": sumo, "ac": check["ac"],
        "scope": ("Both native adapters execute on the bound numerical working day using the same track lengths and DC "
                  "snapshot. Shared throat occupancy, variable train loads and DC remain specific to the coupled motion model. "
                  "The AC utility supply is illustrative. Tool execution is distinct from an engineering screen."),
        "physical_acceptance": "open",
    }
    return {**record, "case_record_id": airport_alignment.identity(record)}


def replay():
    sources = source_digests()
    cases = {label: replay_case(label) for label in CASE_TIMINGS}
    if sources != source_digests():
        raise ValueError("Inputs changed during the corrected Airport verification run")
    record = {"schema": SCHEMA, "source_sha256": sources, "cases": cases}
    return {**record, "receipt_id": airport_alignment.identity(record)}


def verify_receipt(path):
    record = json.loads(Path(path).read_bytes())
    receipt_id = record.pop("receipt_id")
    if (record["schema"] != SCHEMA or receipt_id != airport_alignment.identity(record)
            or record["cases"].keys() != CASE_TIMINGS.keys()
            or any(case["case_label"] != label or case["case_record_id"] != airport_alignment.identity(
                {key: value for key, value in case.items() if key != "case_record_id"})
                for label, case in record["cases"].items())
            or record["source_sha256"] != source_digests()):
        raise ValueError("Corrected Airport verification receipt changed or is stale")
    return {**record, "receipt_id": receipt_id}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--receipt", type=Path, default=RECEIPT)
    args = parser.parse_args()
    if args.replay:
        from engineering.performance import check_disk_reservation, disk_reservation

        with disk_reservation(ROOT, args.receipt.resolve().parent, "Corrected Airport verification receipt", 2 * 2**20) as lease:
            record = replay()
            check_disk_reservation(lease)
            pending = args.receipt.with_suffix(".pending")
            pending.write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n")
            pending.replace(args.receipt)
    record = verify_receipt(args.receipt)
    print(json.dumps({"receipt_id": record["receipt_id"], "cases": {
        label: {tool: case[tool]["status"] for tool in ("sumo", "ac")}
        for label, case in record["cases"].items()
    }}, indent=2))


if __name__ == "__main__":
    main()
